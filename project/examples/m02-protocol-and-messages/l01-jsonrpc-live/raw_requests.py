"""Rohe JSON-RPC-Requests gegen den eigenen stdio-Server (Lab 2.1).

Startet den Server als Kindprozess, schreibt je eine JSON-Zeile auf stdin und liest je eine
Zeile Antwort von stdout. Aufruf (im Projektordner):

  python examples/m02-protocol-and-messages/l01-jsonrpc-live/raw_requests.py [Server-Pfad]

Spezifikation 2026-07-28 mit SDK 2.3.0 (hier geprüft, siehe ECHTE AUSGABE unten):
- Kein initialize-Handshake nötig. Jeder Request trägt selbst die Angaben, die früher der
  Handshake lieferte, in params._meta: protocolVersion, clientInfo, clientCapabilities.
- Ohne diese _meta-Hülle antwortet der Server mit Fehler -32602 bzw. -32600. Der erste Request
  einer Verbindung legt fest, welche Protokollgeneration gilt: Wer ohne Hülle beginnt, landet im
  alten Handshake-Modus und kann die neue Form auf dieser Verbindung nicht mehr nutzen.
- server/discover ist optional und liefert Fähigkeiten und unterstützte Versionen.
- Eine Notification hat kein Feld "id" und bekommt keine Antwort.
- Fehler: Protokollfehler kommen als "error"-Objekt (code, message), Tool-Fehler als "result"
  mit "isError": true.
"""

import json
import subprocess
import sys
from pathlib import Path

SERVER = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[2] / "m02-protocol-and-messages/l02-first-tool/server.py")
META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "raw-script", "version": "0.1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}


def request(rid: int, method: str, params: dict | None = None) -> dict:
    return {"jsonrpc": "2.0", "id": rid, "method": method, "params": {**(params or {}), "_meta": META}}


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
        send(proc, request(1, "server/discover"))
        print("2) tools/list")
        send(proc, request(2, "tools/list"))
        print("3) tools/call get_ticket")
        send(proc, request(3, "tools/call", {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}}))
        print("4) Fehlerfall: falscher Parameter (id statt ticket_id)")
        send(proc, request(4, "tools/call", {"name": "get_ticket", "arguments": {"id": "VAN-102"}}))
        print("5) Fehlerfall: Request ohne _meta-Hülle")
        send(proc, {"jsonrpc": "2.0", "id": 5, "method": "tools/list"})
    finally:
        proc.kill()


if __name__ == "__main__":
    main()


# ECHTE AUSGABE (SDK mcp 2.3.0, Server aus examples/m02-.../l02-first-tool, _meta zur Lesbarkeit gekürzt):
#
# >> {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_ticket",
#     "arguments": {"ticket_id": "VAN-102"}, "_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28", ...}}}
# << {"jsonrpc":"2.0","id":3,"result":{"content":[{"text":"{\n  \"id\": \"VAN-102\",\n  \"title\": \"Login-Seite lädt nach
#     Release 2.14 sehr langsam\",\n  \"status\": \"open\",\n  ... \"version\": 3, ...}","type":"text"}],"isError":false,
#     "resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
#
# Fehlerfall falscher Parameter (id statt ticket_id): Antwort mit "result" und "isError": true
# << {"jsonrpc":"2.0","id":4,"result":{"content":[{"text":"Error executing tool get_ticket: 1 validation error for
#     get_ticketArguments\nticket_id\n  Field required [type=missing, input_value={'id': 'VAN-102'}, input_type=dict]\n
#     For further information visit https://errors.pydantic.dev/2.14/v/missing","type":"text"}],"isError":true,...}}
#
# Fehlerfall ohne _meta-Hülle: echtes JSON-RPC-Fehlerobjekt
# << {"jsonrpc":"2.0","id":5,"error":{"code":-32602,"message":"params._meta must be an object carrying the required
#     'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys"}}
