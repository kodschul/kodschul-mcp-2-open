"""Vantra Ops Agent – abgesicherter Server mit Monitoring (Lab 8.1): strukturierte Logs und Tool-Call-Protokoll."""

import json
import os
import sys
from pathlib import Path
from typing import Annotated, Any

sys.path.insert(0, next(str(p) for p in Path(__file__).resolve().parents if (p / "shared").is_dir()))

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import PolicyDenied, authorize
from context import SESSION_SCHEMA, session
from logging_config import logged, setup_logging
from shared.mock_api.client import get_backend
from shared.mock_api.store import InvalidStatus, NotFound, VersionConflict

log = setup_logging()
mcp = MCPServer(
    "vantra-ops",
    instructions=(
        "MCP-Server des Vantra Ops Agent: Tickets abfragen, Deployment-Logs lesen, Ticket-Status ändern. "
        "Schreibende Aufrufe sind rollenabhängig und brauchen eine Bestätigung des Nutzers."
    ),
)
backend = get_backend()
READ_ONLY = ToolAnnotations(read_only_hint=True)
WRITE = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False)
TicketId = Annotated[str, Field(pattern=r"^VAN-\d{1,6}$", description="Ticket-ID im Format VAN-<Zahl>, z. B. VAN-102")]
MAX_LOG_LINES = 100


def error_result(code: str, message: str, **details) -> CallToolResult:
    """Strukturierter Tool-Fehler: Code, Meldung und Details als JSON (is_error=True)."""
    payload = {"error": code, "message": message, **details}
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))],
        structured_content=payload,
        is_error=True,
    )


@mcp.tool(annotations=READ_ONLY)
@logged("get_ticket")
def get_ticket(ticket_id: TicketId) -> Any:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    session.tool_calls += 1
    try:
        authorize("get_ticket")
        ticket = backend.get_ticket(ticket_id)
    except PolicyDenied as exc:
        return error_result(exc.code, exc.message, **exc.details)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    session.remember_ticket(ticket)
    return ticket


@mcp.tool(annotations=READ_ONLY)
@logged("get_deployment_log")
def get_deployment_log(ticket_id: TicketId | None = None, tail: int = 20) -> Any:
    """Log des letzten Deployments zu einem Ticket lesen. Ohne ticket_id gilt das zuletzt abgefragte Ticket."""
    session.tool_calls += 1
    try:
        authorize("get_deployment_log")
        resolved = session.resolve_ticket_id(ticket_id)
        if resolved is None:
            raise ToolError("Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.")
        deployment = backend.latest_deployment(resolved)
    except PolicyDenied as exc:
        return error_result(exc.code, exc.message, **exc.details)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    session.remember_deployment(deployment)
    lines = deployment["log"][-max(1, min(tail, MAX_LOG_LINES)):]
    return {**{k: deployment[k] for k in ("id", "ticket_id", "service", "version", "environment", "status")}, "log": lines}


@mcp.tool(annotations=WRITE)
@logged("update_ticket_status")
def update_ticket_status(ticket_id: TicketId, status: str, expected_version: int, confirmed: bool = False) -> Any:
    """Ticket-Status ändern (open, in_progress, resolved, closed). Schreibend: braucht Rolle operator und confirmed=true nach Zustimmung des Nutzers. expected_version ist die zuvor gelesene Version."""
    session.tool_calls += 1
    try:
        authorize("update_ticket_status", confirmed=confirmed)
        ticket = backend.update_ticket(ticket_id, status, expected_version)
    except PolicyDenied as exc:
        return error_result(exc.code, exc.message, **exc.details)
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


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    """Health-Check für Docker und Kubernetes (ohne Authentifizierung, ohne Daten)."""
    return JSONResponse({"status": "ok"})


@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> dict:
    """Ticket als Resource (nur lesen, von der Anwendung adressierbar)."""
    try:
        authorize("get_ticket")
        return backend.get_ticket(ticket_id)
    except PolicyDenied as exc:
        raise ResourceNotFoundError(exc.message) from exc
    except NotFound as exc:
        raise ResourceNotFoundError(str(exc)) from exc


@mcp.resource("context://session", mime_type="application/json")
def session_context() -> dict:
    """Ansicht des Session-Kontexts für Menschen und Hosts (der Agent-Client lädt sie nicht ins LLM)."""
    return {"schema": SESSION_SCHEMA, "aktuell": session.to_view()}


if __name__ == "__main__":
    log.info("server_start", extra={"fields": {"transport": os.getenv("MCP_TRANSPORT", "stdio")}})
    if os.getenv("MCP_TRANSPORT", "stdio") == "streamable-http":
        mcp.run(transport="streamable-http", host=os.getenv("MCP_HOST", "0.0.0.0"), port=int(os.getenv("MCP_PORT", "8000")))
    else:
        mcp.run()
