"""Labs 3.2 und 3.3: Kontextschema, zweites Tool, Konflikterkennung über das Versionsfeld."""

import json
import subprocess
import sys

import pytest

from conftest import PROJECT, SRV_AGENT, SRV_CONFLICT, SRV_CONTEXT, connect, json_of, text_of


async def test_two_tools_and_context_resource():
    async with connect(SRV_CONTEXT) as client:
        assert [t.name for t in (await client.list_tools()).tools] == ["get_ticket", "get_deployment_log"]
        uris = [r.uri_template for r in (await client.list_resource_templates()).resource_templates]
        assert "tickets://{ticket_id}" in uris
        context = json.loads((await client.read_resource("context://session")).contents[0].text)
        assert {f["feld"] for f in context["schema"]} >= {"last_ticket", "last_deployment"}
        assert context["aktuell"] == {"last_ticket": None, "last_deployment": None}


async def test_deployment_log_needs_ticket_in_context():
    async with connect(SRV_CONTEXT) as client:
        result = await client.call_tool("get_deployment_log", {})
        assert result.is_error and "zuerst get_ticket" in text_of(result)


async def test_deployment_log_uses_ticket_from_context_and_keeps_it():
    async with connect(SRV_CONTEXT) as client:
        await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
        log = json_of(await client.call_tool("get_deployment_log", {}))
        assert log["id"] == "dep-2041" and log["status"] == "degraded"
        assert "AUTH_CACHE_TTL=0" in "\n".join(log["log"])
        context = json.loads((await client.read_resource("context://session")).contents[0].text)["aktuell"]
        assert context["last_ticket"]["id"] == "VAN-102"  # zweites Tool überschreibt den Ticket-Kontext nicht
        assert context["last_deployment"]["id"] == "dep-2041"


async def test_deployment_log_explicit_id_and_tail():
    async with connect(SRV_CONTEXT) as client:
        log = json_of(await client.call_tool("get_deployment_log", {"ticket_id": "VAN-103", "tail": 1}))
        assert log["service"] == "report-service" and len(log["log"]) == 1
        missing = await client.call_tool("get_deployment_log", {"ticket_id": "VAN-105"})
        assert missing.is_error and "Kein Deployment" in text_of(missing)


@pytest.mark.parametrize("server", [SRV_CONFLICT, SRV_AGENT])
async def test_update_and_version_increment(server):
    async with connect(server) as client:
        ticket = json_of(await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3}))
        assert ticket["status"] == "in_progress" and ticket["version"] == 4


async def test_stale_version_is_reported_as_structured_conflict():
    async with connect(SRV_CONFLICT) as client:
        result = await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": 2})
        assert result.is_error is True
        assert result.structured_content["error"] == "version_conflict"
        assert result.structured_content["expected_version"] == 2
        assert result.structured_content["current_version"] == 3
        assert json.loads(text_of(result)) == result.structured_content


async def test_invalid_status_is_structured_error():
    async with connect(SRV_CONFLICT) as client:
        result = await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "kaputt", "expected_version": 3})
        assert result.is_error and result.structured_content["error"] == "invalid_status"


async def test_two_agents_conflict_over_shared_mock_api(mock_api):
    """Zwei Server-Prozesse (zwei Agenten) teilen den Zustand über die Mock-API."""
    env = {"MOCK_API_URL": mock_api}
    async with connect(SRV_CONFLICT, **env) as agent_a, connect(SRV_CONFLICT, **env) as agent_b:
        a_ticket = json_of(await agent_a.call_tool("get_ticket", {"ticket_id": "VAN-102"}))
        b_ticket = json_of(await agent_b.call_tool("get_ticket", {"ticket_id": "VAN-102"}))
        ok = await agent_b.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "in_progress", "expected_version": b_ticket["version"]})
        assert not ok.is_error
        conflict = await agent_a.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": a_ticket["version"]})
        assert conflict.is_error and conflict.structured_content["error"] == "version_conflict"
        assert conflict.structured_content["current_version"] == b_ticket["version"] + 1
        # Neu lesen und erneut versuchen gelingt
        fresh = json_of(await agent_a.call_tool("get_ticket", {"ticket_id": "VAN-102"}))
        retry = await agent_a.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": fresh["version"]})
        assert not retry.is_error and json_of(retry)["status"] == "resolved"


def test_second_client_script_reports_conflict(mock_api):
    env = {"MOCK_API_URL": mock_api, "PATH": "/usr/bin:/bin"}
    base = [sys.executable, str(PROJECT / "shared/second_client.py"), "--server", str(SRV_CONFLICT)]
    slow = subprocess.Popen(base + ["--name", "agent-a", "--hold", "10", "--status", "resolved"], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    fast = subprocess.run(base + ["--name", "agent-b", "--status", "in_progress"], env=env, capture_output=True, text=True, timeout=90)
    out_a, _ = slow.communicate(timeout=90)
    assert fast.returncode == 0, fast.stdout
    assert slow.returncode == 2 and "version_conflict" in out_a
