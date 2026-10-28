"""Lab 7.1: Zugriffskontrolle im Server (Rollen, Bestätigung, Eingabevalidierung) und Angriffsproben."""

import json

import pytest

from conftest import EX, PROJECT, SRV_SECURE, connect, json_of, text_of

SECURE_DIR = EX / "m07-security-hardening/l01-access-control"
WRITE = {"ticket_id": "VAN-101", "status": "closed", "expected_version": 1}


def _auth():
    import importlib.util

    spec = importlib.util.spec_from_file_location("auth_under_test", SECURE_DIR / "auth.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_auth_unit_rules():
    auth = _auth()
    assert auth.authorize("get_ticket", role="viewer") == "viewer"
    with pytest.raises(auth.PolicyDenied) as exc:
        auth.authorize("update_ticket_status", confirmed=True, role="viewer")
    assert exc.value.code == "policy_denied"
    with pytest.raises(auth.PolicyDenied) as exc:
        auth.authorize("update_ticket_status", role="operator")
    assert exc.value.code == "confirmation_required"
    assert auth.authorize("update_ticket_status", confirmed=True, role="operator") == "operator"
    with pytest.raises(auth.PolicyDenied):  # unbekannte Rolle: deny by default
        auth.authorize("get_ticket", role="admin")
    with pytest.raises(auth.PolicyDenied):  # unbekanntes Tool
        auth.authorize("delete_everything", role="operator", confirmed=True)


async def test_default_role_is_viewer_and_write_is_denied():
    async with connect(SRV_SECURE) as client:
        assert json_of(await client.call_tool("get_ticket", {"ticket_id": "VAN-101"}))["status"] == "open"
        denied = await client.call_tool("update_ticket_status", {**WRITE, "confirmed": True})
        assert denied.is_error and denied.structured_content["error"] == "policy_denied"
        assert denied.structured_content["role"] == "viewer"
        # abgelehnter Aufruf ändert nichts
        assert json_of(await client.call_tool("get_ticket", {"ticket_id": "VAN-101"}))["version"] == 1


async def test_operator_needs_confirmation():
    async with connect(SRV_SECURE, VANTRA_ROLE="operator") as client:
        unconfirmed = await client.call_tool("update_ticket_status", WRITE)
        assert unconfirmed.structured_content["error"] == "confirmation_required"
        confirmed = await client.call_tool("update_ticket_status", {**WRITE, "confirmed": True})
        assert not confirmed.is_error and json_of(confirmed)["status"] == "closed"


async def test_role_cannot_be_chosen_by_tool_argument():
    async with connect(SRV_SECURE) as client:
        schema = next(t for t in (await client.list_tools()).tools if t.name == "update_ticket_status").input_schema
        assert "role" not in schema["properties"]
        result = await client.call_tool("update_ticket_status", {**WRITE, "confirmed": True, "role": "operator"})
        assert result.is_error  # unbekanntes Argument wird abgewiesen oder Rolle bleibt viewer


async def test_unknown_role_is_denied_everywhere():
    async with connect(SRV_SECURE, VANTRA_ROLE="root") as client:
        result = await client.call_tool("get_ticket", {"ticket_id": "VAN-101"})
        assert result.is_error and result.structured_content["error"] == "policy_denied"


@pytest.mark.parametrize("bad_id", ["../etc/passwd", "VAN-1; DROP", "van-102", "VAN-"])
async def test_ticket_id_format_is_validated(bad_id):
    async with connect(SRV_SECURE) as client:
        result = await client.call_tool("get_ticket", {"ticket_id": bad_id})
        assert result.is_error and "pattern" in text_of(result)


async def test_log_tail_is_capped():
    async with connect(SRV_SECURE) as client:
        log = json_of(await client.call_tool("get_deployment_log", {"ticket_id": "VAN-102", "tail": 100000}))
        assert len(log["log"]) <= 100


async def test_read_tools_and_conflict_still_work_under_policy():
    async with connect(SRV_SECURE, VANTRA_ROLE="operator") as client:
        stale = await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": 1, "confirmed": True})
        assert stale.structured_content["error"] == "version_conflict"


def test_policy_document_matches_enforced_rules():
    text = (SECURE_DIR / "policy.md").read_text(encoding="utf-8")
    auth = _auth()
    for tool in ("get_ticket", "get_deployment_log", "update_ticket_status"):
        assert f"`{tool}`" in text
    for role in auth.ROLE_TOOLS:
        assert role in text
    for code in ("policy_denied", "confirmation_required", "version_conflict"):
        assert code in text


def test_attack_samples_are_well_formed_and_injection_ticket_exists():
    samples = sorted((PROJECT / "shared/attack-samples").glob("*.json"))
    assert len(samples) >= 3
    for path in samples:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["manipuliertes_ergebnis"]
        assert "auffaelligkeiten" not in data, f"{path.name}: Auffälligkeiten gehören in die Lösung, nicht in die Probe"
    solution = (PROJECT.parent / "m07-security-hardening/l02-injection/l02-injection-sol.md").read_text(encoding="utf-8")
    assert "Auffälligkeiten je Probe" in solution
    tickets = json.loads((PROJECT / "shared/mock_api/tickets.json").read_text(encoding="utf-8"))
    injected = next(t for t in tickets if t["id"] == "VAN-106")
    assert "update_ticket_status" in injected["description"]
