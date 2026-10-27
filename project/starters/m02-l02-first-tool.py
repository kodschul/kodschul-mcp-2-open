"""Starter Lab 2.2: Server mit leerem Tool-Platz. Kopieren nach playground/server.py und vervollständigen.

Stand: Ergebnis von Lab 1.2 plus Anbindung an die Mock-API (shared/mock_api).
"""

import sys
from pathlib import Path

sys.path.insert(0, next(str(p) for p in Path(__file__).resolve().parents if (p / "shared").is_dir()))

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from shared.mock_api.client import get_backend
from shared.mock_api.store import NotFound

mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent: Tickets abfragen.",
)
backend = get_backend()  # liefert Ticket-Daten: backend.get_ticket("VAN-102"), wirft NotFound bei unbekannter ID


# TODO(Aufgabe 1): Funktion get_ticket(ticket_id: str) -> dict implementieren
#   - mit @mcp.tool(annotations=ToolAnnotations(read_only_hint=True)) registrieren
#   - Docstring als Tool-Beschreibung schreiben (das LLM liest ihn später)
#   - backend.get_ticket(ticket_id) aufrufen und das Ticket zurückgeben
# TODO(Aufgabe 2): NotFound abfangen und als ToolError("...") melden
# TODO(Aufgabe 3, Erweiterung): Resource "tickets://{ticket_id}" mit @mcp.resource(...) ergänzen


if __name__ == "__main__":
    mcp.run()
