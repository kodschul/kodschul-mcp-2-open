"""Lab 4.1/4.2: Agent-Client mit Replay-LLM und mit einem OpenAI-kompatiblen Fake-Backend."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from conftest import SRV_AGENT, SRV_CONFLICT, SRV_SECURE, connect
from shared import agent_client
from shared.replay_llm import SCENARIOS, ReplayLLM


async def run_replay(server, scenario, confirm="none", **env):
    lines: list[str] = []
    async with connect(server, **env) as client:
        records = await agent_client.run_agent(client, ReplayLLM(scenario), SCENARIOS[scenario], confirm, out=lines.append)
    return records, lines


async def test_replay_canonical_dialog():
    records, lines = await run_replay(SRV_AGENT, "dialog")
    assert [r["tool"] for r in records] == ["get_ticket", "get_deployment_log"]
    assert records[0]["arguments"] == {"ticket_id": "VAN-102"}
    assert records[1]["arguments"] == {}  # "dazu" wird über den Kontext aufgelöst
    assert not any(r["is_error"] for r in records)
    joined = "\n".join(lines)
    assert "Tool-Call: get_ticket" in joined and "dep-2041" in joined


async def test_replay_hides_confirmed_from_llm_tools():
    async with connect(SRV_SECURE) as client:
        tools = (await client.list_tools()).tools
        converted = {t.name: agent_client.to_openai_tool(t) for t in tools}
        assert "confirmed" in next(t for t in tools if t.name == "update_ticket_status").input_schema["properties"]
        assert "confirmed" not in converted["update_ticket_status"]["function"]["parameters"]["properties"]


async def test_injection_succeeds_without_policy():
    records, _ = await run_replay(SRV_CONFLICT, "injection")
    assert [r["tool"] for r in records] == ["get_ticket", "update_ticket_status"]
    assert records[1]["is_error"] is False and '"closed"' in records[1]["text"]


async def test_injection_is_blocked_by_policy():
    records, lines = await run_replay(SRV_SECURE, "injection", VANTRA_ROLE="viewer")
    assert records[1]["tool"] == "update_ticket_status" and records[1]["is_error"] is True
    assert "policy_denied" in records[1]["text"]
    assert "nicht erfolgreich" in lines[-1]


async def test_injection_blocked_even_for_operator_without_confirmation():
    records, _ = await run_replay(SRV_SECURE, "injection", VANTRA_ROLE="operator")
    assert "confirmation_required" in records[1]["text"]


async def test_user_declining_never_reaches_server():
    records, _ = await run_replay(SRV_SECURE, "injection", confirm="no", VANTRA_ROLE="operator")
    assert "user_declined" in records[1]["text"]


async def test_workflow_operator_with_confirmation():
    records, _ = await run_replay(SRV_SECURE, "workflow", confirm="yes", VANTRA_ROLE="operator")
    assert [r["tool"] for r in records] == ["get_ticket", "get_deployment_log", "update_ticket_status"]
    assert records[2]["is_error"] is False and '"in_progress"' in records[2]["text"]


class _FakeOpenAI(BaseHTTPRequestHandler):
    requests: list[dict] = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).requests.append({"auth": self.headers.get("Authorization"), "body": body})
        has_tool_result = any(m["role"] == "tool" for m in body["messages"])
        if has_tool_result:
            message = {"role": "assistant", "content": "VAN-102 ist offen (Version 3)."}
            finish = "stop"
        else:
            message = {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "get_ticket", "arguments": json.dumps({"ticket_id": "VAN-102"})}}
            ]}
            finish = "tool_calls"
        payload = {"id": "x", "object": "chat.completion", "created": 0, "model": body["model"],
                   "choices": [{"index": 0, "finish_reason": finish, "message": message}]}
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


async def test_openai_compatible_backend_configured_by_env(monkeypatch):
    _FakeOpenAI.requests = []
    fake = ThreadingHTTPServer(("127.0.0.1", 0), _FakeOpenAI)
    threading.Thread(target=fake.serve_forever, daemon=True).start()
    monkeypatch.setenv("LLM_BASE_URL", f"http://127.0.0.1:{fake.server_address[1]}/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    try:
        lines: list[str] = []
        llm = agent_client.make_llm(None)
        async with connect(SRV_AGENT) as client:
            records = await agent_client.run_agent(client, llm, ["Zeige Ticket VAN-102"], "none", out=lines.append)
    finally:
        fake.shutdown()
        fake.server_close()
    assert [r["tool"] for r in records] == ["get_ticket"]
    assert lines[-1] == "Agent: VAN-102 ist offen (Version 3)."
    first = _FakeOpenAI.requests[0]
    assert first["auth"] == "Bearer test-key" and first["body"]["model"] == "test-model"
    assert {t["function"]["name"] for t in first["body"]["tools"]} == {"get_ticket", "get_deployment_log", "update_ticket_status"}


def test_env_file_does_not_override_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("# Kommentar\nLLM_MODEL=aus-datei\nLLM_BASE_URL=http://x/v1\n", encoding="utf-8")
    monkeypatch.setenv("LLM_MODEL", "aus-umgebung")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    agent_client.load_env(env_file)
    import os

    assert os.environ["LLM_MODEL"] == "aus-umgebung" and os.environ["LLM_BASE_URL"] == "http://x/v1"
    monkeypatch.delenv("LLM_BASE_URL")


def test_unknown_replay_scenario_is_rejected():
    with pytest.raises(ValueError):
        ReplayLLM("gibt-es-nicht")


async def test_example_agent_script_runs_with_replay():
    import subprocess
    import sys

    from conftest import EX

    script = EX / "m04-agent-prototype/l01-agent-client/agent.py"
    done = subprocess.run([sys.executable, str(script), "--replay"], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert "Tool-Call: get_ticket" in done.stdout and "Tool-Call: get_deployment_log" in done.stdout
