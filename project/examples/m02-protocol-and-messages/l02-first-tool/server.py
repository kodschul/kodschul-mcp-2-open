"""Vantra Ops Agent – Server mit erstem Tool (Lab 2.2): Ticket abfragen."""

import sys
from pathlib import Path

# Sucht den Projektordner (den mit shared/), damit "import shared…" funktioniert – nicht ändern.
sys.path.insert(0, next(str(p) for p in Path(__file__).resolve().parents if (p / "shared").is_dir()))

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import ToolAnnotations

from shared.mock_api.client import get_backend
from shared.mock_api.store import NotFound

mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent: Tickets abfragen.",
)
backend = get_backend()


@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
def get_ticket(ticket_id: str) -> dict:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc


@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> dict:
    """Ticket als Resource (nur lesen, von der Anwendung adressierbar)."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ResourceNotFoundError(str(exc)) from exc


if __name__ == "__main__":
    mcp.run()
