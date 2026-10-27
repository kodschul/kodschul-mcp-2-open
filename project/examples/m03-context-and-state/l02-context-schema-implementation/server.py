"""Vantra Ops Agent – zwei Tools und Kontextverwaltung (Lab 3.2)."""

import sys
from pathlib import Path

sys.path.insert(0, next(str(p) for p in Path(__file__).resolve().parents if (p / "shared").is_dir()))

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import ToolAnnotations

from context import SESSION_SCHEMA, session
from shared.mock_api.client import get_backend
from shared.mock_api.store import NotFound

mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent: Tickets abfragen und Deployment-Logs dazu lesen.",
)
backend = get_backend()
READ_ONLY = ToolAnnotations(read_only_hint=True)


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


@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> dict:
    """Ticket als Resource (nur lesen, von der Anwendung adressierbar)."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ResourceNotFoundError(str(exc)) from exc


@mcp.resource("context://session", mime_type="application/json")
def session_context() -> dict:
    """Sichtbarer Ausschnitt des Session-Kontexts und das Schema dahinter."""
    return {"schema": SESSION_SCHEMA, "aktuell": session.to_llm_view()}


if __name__ == "__main__":
    mcp.run()
