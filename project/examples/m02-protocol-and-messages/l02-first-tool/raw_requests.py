"""Rohe JSON-RPC-Requests gegen den Server mit get_ticket (Lab 2.2, Aufgabe 6; genutzt in Lab 2.3).

Stand von Lab 2.1 plus tools/call: einmal korrekt, einmal mit falschem Parameternamen.
Aufruf (im Projektordner):

  python examples/m02-protocol-and-messages/l02-first-tool/raw_requests.py [Server-Pfad]

Tool-Fehler (falscher Parameter) kommen als "result" mit "isError": true,
Protokollfehler (unbekannte Methode, fehlende Hülle) als "error"-Objekt.
"""

import json
import subprocess
import sys
from pathlib import Path

SERVER = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "server.py")
META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "raw-script", "version": "0.1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}


def send(proc: subprocess.Popen, message: dict) -> None:
    print(">>", json.dumps(message, ensure_ascii=False))
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    if "id" in message:  # nur Requests bekommen eine Antwort
        print("<<", proc.stdout.readline().strip(), "\n")


def main() -> None:
    proc = subprocess.Popen([sys.executable, SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        print("1) server/discover (optional)")
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": META}})
        print("2) tools/list")
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {"_meta": META}})
        print("3) Fehlerfall: unbekannte Methode")
        send(proc, {"jsonrpc": "2.0", "id": 3, "method": "nope/list", "params": {"_meta": META}})
        print("4) Fehlerfall: Request ohne _meta-Hülle")
        send(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
        print("5) Notification (ohne id, keine Antwort), danach tools/list")
        send(proc, {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99, "_meta": META}})
        send(proc, {"jsonrpc": "2.0", "id": 5, "method": "tools/list", "params": {"_meta": META}})
        print("6) tools/call get_ticket (Lab 2.2)")
        send(proc, {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                    "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}, "_meta": META}})
        print("7) Fehlerfall: falscher Parameter, id statt ticket_id (Lab 2.3)")
        send(proc, {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                    "params": {"name": "get_ticket", "arguments": {"id": "VAN-102"}, "_meta": META}})
    finally:
        proc.kill()


if __name__ == "__main__":
    main()


# ECHTE AUSGABE der Zeilen 6 und 7 (SDK mcp 2.3.0, Server aus diesem Ordner):
#
# << {"jsonrpc":"2.0","id":6,"result":{"content":[{"text":"{\n  \"id\": \"VAN-102\",\n  \"title\": \"Login-Seite lädt nach
#     Release 2.14 sehr langsam\",\n  \"status\": \"open\",\n  ... \"version\": 3, ...}","type":"text"}],"isError":false,
#     "resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
#
# << {"jsonrpc":"2.0","id":7,"result":{"content":[{"text":"Error executing tool get_ticket: 1 validation error for
#     get_ticketArguments\nticket_id\n  Field required [type=missing, input_value={'id': 'VAN-102'}, input_type=dict]\n
#     For further information visit https://errors.pydantic.dev/2.14/v/missing","type":"text"}],"isError":true,...}}
