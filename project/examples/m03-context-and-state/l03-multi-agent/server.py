"""Vantra Ops Agent – Konflikterkennung über das Versionsfeld (Lab 3.3)."""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, next(str(p) for p in Path(__file__).resolve().parents if (p / "shared").is_dir()))

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import CallToolResult, TextContent, ToolAnnotations

from context import SESSION_SCHEMA, session
from shared.mock_api.client import get_backend
from shared.mock_api.store import InvalidStatus, NotFound, VersionConflict

mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent: Tickets abfragen, Deployment-Logs lesen, Ticket-Status ändern.",
)
backend = get_backend()
READ_ONLY = ToolAnnotations(read_only_hint=True)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False)


def error_result(code: str, message: str, **details) -> CallToolResult:
    """Strukturierter Tool-Fehler: Code, Meldung und Details als JSON (is_error=True).

    Anders als ToolError (nur Text) trägt das Ergebnis maschinenlesbare Felder wie current_version.
    """
    payload = {"error": code, "message": message, **details}
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))],
        structured_content=payload,
        is_error=True,
    )


@mcp.tool(annotations=READ_ONLY)
def get_ticket(ticket_id: str) -> dict:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    session.tool_calls += 1
    try:
        ticket = backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    session.remember_ticket(ticket)
    return ticket


@mcp.tool(annotations=READ_ONLY)
def get_deployment_log(ticket_id: str | None = None, tail: int = 20) -> dict:
    """Log des letzten Deployments zu einem Ticket lesen. Ohne ticket_id gilt das zuletzt abgefragte Ticket."""
    session.tool_calls += 1
    resolved = session.resolve_ticket_id(ticket_id)
    if resolved is None:
        raise ToolError("Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.")
    try:
        deployment = backend.latest_deployment(resolved)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    session.remember_deployment(deployment)
    return {**{k: deployment[k] for k in ("id", "ticket_id", "service", "version", "environment", "status")}, "log": deployment["log"][-tail:]}


@mcp.tool(annotations=WRITE)
def update_ticket_status(ticket_id: str, status: str, expected_version: int) -> Any:
    """Ticket-Status ändern (open, in_progress, resolved, closed). expected_version ist die zuvor gelesene Version des Tickets."""
    session.tool_calls += 1
    try:
        ticket = backend.update_ticket(ticket_id, status, expected_version)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    except InvalidStatus as exc:
        return error_result("invalid_status", str(exc), ticket_id=ticket_id)
    except VersionConflict as exc:
        return error_result(
            "version_conflict",
            f"Ticket {ticket_id} wurde zwischenzeitlich geändert. Neu lesen mit get_ticket und erneut versuchen.",
            ticket_id=ticket_id,
            expected_version=exc.expected,
            current_version=exc.current,
        )
    session.remember_ticket(ticket)
    return ticket


@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> dict:
    """Ticket als Resource (nur lesen, von der Anwendung adressierbar)."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ResourceNotFoundError(str(exc)) from exc


@mcp.resource("context://session", mime_type="application/json")
def session_context() -> dict:
    """Ansicht des Session-Kontexts für Menschen und Hosts (der Agent-Client lädt sie nicht ins LLM)."""
    return {"schema": SESSION_SCHEMA, "aktuell": session.to_view()}


if __name__ == "__main__":
    mcp.run()
