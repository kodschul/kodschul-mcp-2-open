"""Fehlerfälle gegen den Server aus Lab 2.2 provozieren (Lab 2.3).

Aufruf (im Projektordner):  python examples/m02-protocol-and-messages/l02-first-tool/error_cases.py

Zwei Fehlerarten im Protokoll:
- Tool-Fehler: normales Ergebnis mit isError=true; die Fehlermeldung steht in content und ist für das Modell lesbar.
- Protokollfehler: JSON-RPC-Fehlerobjekt (code, message); das Client-SDK wirft MCPError.
"""

import asyncio
import sys
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters
from mcp.shared.exceptions import MCPError

SERVER = str(Path(__file__).resolve().parent / "server.py")


def show(label: str, result) -> None:
    text = result.content[0].text.splitlines()[0]
    print(f"{label}\n  is_error={result.is_error}  text={text!r}\n")


async def main() -> None:
    async with Client(StdioServerParameters(command=sys.executable, args=[SERVER])) as client:
        show("1) falscher Parameter (id statt ticket_id)", await client.call_tool("get_ticket", {"id": "VAN-102"}))
        show("2) falscher Typ (Zahl statt Text)", await client.call_tool("get_ticket", {"ticket_id": 102}))
        show("3) unbekanntes Ticket", await client.call_tool("get_ticket", {"ticket_id": "VAN-999"}))
        show("4) unbekanntes Tool", await client.call_tool("get_tickets", {"ticket_id": "VAN-102"}))
        try:
            await client.read_resource("tickets://VAN-999")
        except MCPError as exc:
            print(f"5) unbekannte Resource\n  MCPError code={exc.error.code} message={exc.error.message!r}\n")


if __name__ == "__main__":
    asyncio.run(main())
