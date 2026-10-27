"""Zweiter Client für die Multi-Agent-Übung (Lab 3.3): zwei Agenten, ein Ticket.

Liest ein Ticket, wartet (--hold Sekunden, simuliert Überlegen des Agenten) und ändert danach den
Status mit der zuvor gelesenen Version. Gemeinsamer Zustand entsteht nur über die Mock-API:
  Terminal 1:  python shared/mock_api/app.py
  Terminal 2:  MOCK_API_URL=http://localhost:8001 python shared/second_client.py --name agent-a --hold 10 --status resolved
  Terminal 3:  MOCK_API_URL=http://localhost:8001 python shared/second_client.py --name agent-b --status in_progress
Agent B ändert das Ticket während Agent A wartet; danach meldet der Server mit Versionsprüfung
einen Konflikt (version_conflict), ohne Versionsprüfung überschreibt Agent A still.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp import Client
from mcp.client.stdio import StdioServerParameters


def _text(result) -> str:
    return "\n".join(c.text for c in result.content if getattr(c, "type", "") == "text")


async def run(args) -> int:
    env = {**os.environ, "VANTRA_ROLE": args.role}
    client = Client(args.url) if args.url else Client(StdioServerParameters(command=sys.executable, args=[args.server], env=env))
    async with client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
        read = await client.call_tool("get_ticket", {"ticket_id": args.ticket})
        if read.is_error:
            print(f"[{args.name}] Lesen fehlgeschlagen: {_text(read)}")
            return 1
        ticket = json.loads(_text(read))
        print(f"[{args.name}] gelesen: {ticket['id']} Status={ticket['status']} Version={ticket['version']}")
        if args.hold:
            print(f"[{args.name}] überlegt {args.hold} s ...")
            time.sleep(args.hold)
        call_args = {"ticket_id": args.ticket, "status": args.status}
        if "expected_version" in tools["update_ticket_status"].input_schema["properties"]:
            call_args["expected_version"] = ticket["version"]
        if "confirmed" in tools["update_ticket_status"].input_schema["properties"]:
            call_args["confirmed"] = True
        result = await client.call_tool("update_ticket_status", call_args)
        label = "FEHLER" if result.is_error else "ok"
        print(f"[{args.name}] update_ticket_status({call_args}) -> {label}: {_text(result).replace(chr(10), ' ')}")
        return 2 if result.is_error else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", default="agent-b")
    parser.add_argument("--server", default=os.getenv("MCP_SERVER_SCRIPT", "playground/server.py"))
    parser.add_argument("--url", default=os.getenv("MCP_SERVER_URL"))
    parser.add_argument("--ticket", default="VAN-102")
    parser.add_argument("--status", default="in_progress")
    parser.add_argument("--hold", type=float, default=0.0, help="Sekunden zwischen Lesen und Schreiben")
    parser.add_argument("--role", default="operator", help="VANTRA_ROLE für den stdio-Server (nur relevant ab Lab 7.1)")
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    sys.exit(main())
