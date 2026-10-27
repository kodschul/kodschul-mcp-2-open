"""Lab 8.1/8.2: strukturierte Logs, Tool-Call-JSONL, Alarmregel, Dashboard, Abschluss-Workflow."""

import json
import os
import subprocess
import sys
import threading
import urllib.request
from datetime import datetime, timedelta, timezone

from conftest import EX, SRV_CAPSTONE, SRV_LOGGING, connect, json_of

LOGGING_DIR = EX / "m08-observability-and-capstone/l01-monitoring-setup"


def _logging_config():
    import importlib.util

    spec = importlib.util.spec_from_file_location("logging_config_under_test", LOGGING_DIR / "logging_config.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _records(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


async def test_every_tool_call_is_logged_with_status(tmp_path):
    log = tmp_path / "calls.jsonl"
    async with connect(SRV_LOGGING, TOOL_CALL_LOG=str(log), VANTRA_ROLE="operator") as client:
        await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
        await client.call_tool("get_ticket", {"ticket_id": "VAN-999"})
        await client.call_tool("get_deployment_log", {})
        await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": 1, "confirmed": True})
        await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": 3})
        await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": 3, "confirmed": True})
    rows = _records(log)
    assert [(r["tool"], r["status"]) for r in rows] == [
        ("get_ticket", "ok"),
        ("get_ticket", "error"),
        ("get_deployment_log", "ok"),
        ("update_ticket_status", "conflict"),
        ("update_ticket_status", "denied"),
        ("update_ticket_status", "ok"),
    ]
    assert rows[4]["error_code"] == "confirmation_required"
    assert all(r["role"] == "operator" and r["duration_ms"] >= 0 and r["ts"] for r in rows)


async def test_log_contains_no_ticket_content_or_confirmed_flag(tmp_path):
    log = tmp_path / "calls.jsonl"
    async with connect(SRV_LOGGING, TOOL_CALL_LOG=str(log)) as client:
        await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
    raw = log.read_text(encoding="utf-8")
    assert "Login-Seite" not in raw and "jonas.brandt" not in raw and "confirmed" not in raw


async def test_stdout_stays_protocol_clean_and_stderr_is_json(tmp_path):
    """Server-Logs gehen als JSON auf stderr; stdout gehört dem Protokoll."""
    proc = subprocess.Popen(
        [sys.executable, str(SRV_LOGGING)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env={**os.environ, "TOOL_CALL_LOG": str(tmp_path / "x.jsonl")},
    )
    meta = {"io.modelcontextprotocol/protocolVersion": "2026-07-28", "io.modelcontextprotocol/clientCapabilities": {}}
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-101"}, "_meta": meta}}) + "\n")
    proc.stdin.flush()
    reply = json.loads(proc.stdout.readline())
    proc.stdin.close()
    err = proc.stderr.read()
    proc.wait(timeout=10)
    assert reply["id"] == 1
    json_lines = [json.loads(line) for line in err.splitlines() if line.startswith("{")]
    assert any(entry.get("message") == "tool_call get_ticket ok" for entry in json_lines)


def test_alert_rule_fires_on_burst_of_denied_calls():
    cfg = _logging_config()
    now = datetime.now(timezone.utc)

    def rec(status, seconds_ago):
        return {"ts": (now - timedelta(seconds=seconds_ago)).isoformat(), "status": status}

    burst = [rec("denied", 5), rec("denied", 10), rec("denied", 20), rec("ok", 1)]
    fired = cfg.evaluate_alerts(burst, now)
    assert [a["regel"] for a in fired] == ["viele-abgelehnte-aufrufe"] and fired[0]["anzahl"] == 3
    assert cfg.evaluate_alerts([rec("denied", 5), rec("denied", 6)], now) == []
    assert cfg.evaluate_alerts([rec("denied", 120), rec("denied", 130), rec("denied", 140)], now) == []  # außerhalb des Fensters


def test_dashboard_serves_html_and_summary(tmp_path, monkeypatch):
    from shared.dashboard import server as dash

    log = tmp_path / "calls.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text("\n".join(json.dumps({"ts": now, "tool": "update_ticket_status", "role": "viewer", "status": "denied", "error_code": "policy_denied", "duration_ms": 1, "args": {}}) for _ in range(3)) + "\nkaputt\n", encoding="utf-8")
    monkeypatch.setattr(dash.Handler, "log_path", log)
    server = dash.make_server("127.0.0.1", 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        assert b"Tool-Call-Zeitleiste" in urllib.request.urlopen(base + "/").read()
        data = json.loads(urllib.request.urlopen(base + "/api/calls").read())
        assert data["summary"]["total"] == 3 and data["summary"]["alert"] is True
        assert json.loads(urllib.request.urlopen(base + "/health").read()) == {"status": "ok"}
    finally:
        server.shutdown()
        server.server_close()


def test_dashboard_handles_missing_log(tmp_path, monkeypatch):
    from shared.dashboard import server as dash

    assert dash.read_calls(tmp_path / "gibt-es-nicht.jsonl") == []
    assert dash.summarize([])["alert"] is False


async def test_capstone_workflow_viewer_vs_operator(tmp_path):
    log = tmp_path / "calls.jsonl"
    results = {}
    for role, confirm in (("viewer", True), ("operator", True), ("operator", False)):
        async with connect(SRV_CAPSTONE, TOOL_CALL_LOG=str(log), VANTRA_ROLE=role) as client:
            await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
            await client.call_tool("get_deployment_log", {})
            results[(role, confirm)] = await client.call_tool(
                "update_ticket_status", {"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3, **({"confirmed": True} if confirm else {})}
            )
    assert results[("viewer", True)].structured_content["error"] == "policy_denied"
    assert json_of(results[("operator", True)])["status"] == "in_progress"
    assert results[("operator", False)].structured_content["error"] == "confirmation_required"
    statuses = [r["status"] for r in _records(log) if r["tool"] == "update_ticket_status"]
    assert statuses == ["denied", "ok", "denied"]


def test_capstone_demo_script_runs(tmp_path):
    env = {**os.environ, "TOOL_CALL_LOG": str(tmp_path / "demo.jsonl")}
    done = subprocess.run([sys.executable, str(EX / "m08-observability-and-capstone/l02-capstone-integration/run_demo.py")], capture_output=True, text=True, timeout=180, env=env)
    assert done.returncode == 0, done.stderr
    assert "policy_denied" in done.stdout and "confirmation_required" in done.stdout and "Status in_progress" in done.stdout
