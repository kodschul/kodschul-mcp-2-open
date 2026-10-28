"""Labs 1.2, 2.1, 2.2, 2.3: leerer Server, rohe JSON-RPC-Requests, erstes Tool, Fehlerfälle."""

import json
import subprocess
import sys

import pytest
from mcp.shared.exceptions import MCPError

from conftest import EX, SRV_EMPTY, SRV_TOOL, connect, json_of, text_of

META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "pytest", "version": "1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}


async def test_empty_server_is_reachable_and_has_no_tools():
    async with connect(SRV_EMPTY) as client:
        assert client.protocol_version == "2026-07-28"
        assert client.server_info.name == "vantra-ops"
        assert (await client.list_tools()).tools == []


async def test_first_tool_is_listed_with_schema():
    async with connect(SRV_TOOL) as client:
        tools = (await client.list_tools()).tools
        assert [t.name for t in tools] == ["get_ticket"]
        schema = tools[0].input_schema
        assert schema["required"] == ["ticket_id"]
        assert schema["properties"]["ticket_id"]["type"] == "string"
        assert tools[0].annotations.read_only_hint is True


async def test_get_ticket_returns_ticket_with_version():
    async with connect(SRV_TOOL) as client:
        result = await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
        assert not result.is_error
        ticket = json_of(result)
        assert ticket["id"] == "VAN-102"
        assert ticket["version"] == 3
        assert ticket["status"] == "open"


async def test_resource_template_and_read():
    async with connect(SRV_TOOL) as client:
        templates = (await client.list_resource_templates()).resource_templates
        assert [t.uri_template for t in templates] == ["tickets://{ticket_id}"]
        content = (await client.read_resource("tickets://VAN-103")).contents[0]
        assert json.loads(content.text)["id"] == "VAN-103"


@pytest.mark.parametrize(
    "tool,args,fragment",
    [
        ("get_ticket", {"id": "VAN-102"}, "Field required"),  # falscher Parametername
        ("get_ticket", {"ticket_id": 102}, "valid string"),  # falscher Typ
        ("get_ticket", {"ticket_id": "VAN-999"}, "Ticket VAN-999 nicht gefunden"),
        ("get_tickets", {"ticket_id": "VAN-102"}, "Unknown tool: get_tickets"),
    ],
)
async def test_tool_errors_are_results_with_is_error(tool, args, fragment):
    async with connect(SRV_TOOL) as client:
        result = await client.call_tool(tool, args)
        assert result.is_error is True
        assert fragment in text_of(result)


async def test_unknown_resource_is_protocol_error():
    async with connect(SRV_TOOL) as client:
        with pytest.raises(MCPError) as exc:
            await client.read_resource("tickets://VAN-999")
        assert exc.value.error.code == -32602


def _session(messages, server=SRV_TOOL):
    proc = subprocess.Popen([sys.executable, str(server)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    replies = []
    try:
        for message in messages:
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()
            if "id" in message:
                replies.append(json.loads(proc.stdout.readline()))
    finally:
        proc.kill()
    return replies


def test_raw_jsonrpc_without_handshake():
    """Spezifikation 2026-07-28: kein initialize, jeder Request trägt die _meta-Hülle."""
    replies = _session([
        {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": META}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {"_meta": META}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}, "_meta": META}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_ticket", "arguments": {"id": "VAN-102"}, "_meta": META}},
        {"jsonrpc": "2.0", "id": 5, "method": "unbekannt/list", "params": {"_meta": META}},
        {"jsonrpc": "2.0", "id": 6, "method": "tools/list"},
    ])
    assert replies[0]["result"]["supportedVersions"] == ["2026-07-28"]
    assert [t["name"] for t in replies[1]["result"]["tools"]] == ["get_ticket"]
    assert replies[2]["id"] == 3 and replies[2]["result"]["isError"] is False
    assert replies[3]["result"]["isError"] is True and "Field required" in replies[3]["result"]["content"][0]["text"]
    assert replies[4]["error"]["code"] == -32601
    assert replies[5]["error"]["code"] == -32602 and "_meta" in replies[5]["error"]["message"]


def test_raw_jsonrpc_against_empty_server_lab_2_1():
    """Lab 2.1 arbeitet am eigenen, leeren Server aus Lab 1.2."""
    replies = _session([
        {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": META}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {"_meta": META}},
        {"jsonrpc": "2.0", "id": 3, "method": "nope/list", "params": {"_meta": META}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/list"},
        {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99, "_meta": META}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/list", "params": {"_meta": META}},
    ], server=SRV_EMPTY)
    assert [r["id"] for r in replies] == [1, 2, 3, 4, 5]
    assert replies[0]["result"]["_meta"]["io.modelcontextprotocol/serverInfo"]["name"] == "vantra-ops"
    assert replies[1]["result"]["tools"] == [] and replies[4]["result"]["tools"] == []
    assert replies[2]["error"]["code"] == -32601 and replies[2]["error"]["data"] == "nope/list"
    assert replies[3]["error"]["code"] == -32602


def test_raw_notification_gets_no_reply_and_ids_correlate():
    replies = _session([
        {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99, "_meta": META}},
        {"jsonrpc": "2.0", "id": 41, "method": "tools/list", "params": {"_meta": META}},
    ])
    assert len(replies) == 1 and replies[0]["id"] == 41


def test_legacy_initialize_handshake_still_works():
    replies = _session([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "pytest", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ])
    assert replies[0]["result"]["protocolVersion"] == "2025-06-18"
    assert replies[1]["result"]["tools"][0]["name"] == "get_ticket"


def _run_example(rel):
    done = subprocess.run([sys.executable, str(EX / rel)], capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    return done.stdout


def test_example_scripts_run():
    raw_21 = _run_example("m02-protocol-and-messages/l01-jsonrpc/raw_requests.py")
    assert '"tools":[]' in raw_21 and '"code":-32601' in raw_21 and '"code":-32602' in raw_21 and "tools/call" not in raw_21
    raw_22 = _run_example("m02-protocol-and-messages/l02-first-tool/raw_requests.py")
    assert '"id":6,"result"' in raw_22 and '"isError":false' in raw_22 and "Field required" in raw_22
    errors = _run_example("m02-protocol-and-messages/l02-first-tool/error_cases.py")
    assert "is_error=True" in errors and "MCPError code=-32602" in errors


def test_starter_m02_raw_requests_targets_own_server():
    text = (EX.parent / "starters/m02-l01-raw-requests.py").read_text(encoding="utf-8")
    assert 'SERVER = "playground/server.py"' in text and "tools/call" not in text
