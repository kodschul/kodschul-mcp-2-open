"""Rohe JSON-RPC-Requests gegen den eigenen stdio-Server (Lab 2.1).

Startet den Server als Kindprozess, schreibt je eine JSON-Zeile auf stdin und liest je eine
Zeile Antwort von stdout. Aufruf (im Projektordner):

  python examples/m02-protocol-and-messages/l01-jsonrpc/raw_requests.py [Server-Pfad]

Standard-Server ist der leere Server aus Lab 1.2 (noch ohne Tools). Den Aufruf eines Tools
per tools/call zeigt examples/m02-protocol-and-messages/l02-first-tool/raw_requests.py (Lab 2.2).

Spezifikation 2026-07-28 mit SDK 2.3.0 (hier geprüft, siehe ECHTE AUSGABE unten):
- Kein initialize-Handshake nötig. Jeder Request trägt Version und Fähigkeiten selbst in params._meta.
- Ohne diese _meta-Hülle antwortet der Server mit Fehler -32602.
- Unbekannte Methoden beantwortet der Server mit -32601.
- Eine Notification hat kein Feld "id" und bekommt keine Antwort.
"""

import json
import subprocess
import sys
from pathlib import Path

SERVER = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[2] / "m01-mcp-foundations-and-setup/l02-dev-setup/server.py")
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
    finally:
        proc.kill()


if __name__ == "__main__":
    main()


# ECHTE AUSGABE der Antwortzeilen (SDK mcp 2.3.0, leerer Server aus Lab 1.2):
#
# << {"jsonrpc":"2.0","id":1,"result":{"cacheScope":"private","capabilities":{"prompts":{"listChanged":true},
#     "resources":{"listChanged":true,"subscribe":true},"tools":{"listChanged":true}},"instructions":"MCP-Server des
#     Vantra Ops Agent. Noch ohne Tools: Aufbau folgt in den nächsten Labs.","resultType":"complete",
#     "supportedVersions":["2026-07-28"],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
# << {"jsonrpc":"2.0","id":2,"result":{"cacheScope":"private","resultType":"complete","tools":[],"ttlMs":0,"_meta":{...}}}
# << {"jsonrpc":"2.0","id":3,"error":{"code":-32601,"message":"Method not found","data":"nope/list"}}
# << {"jsonrpc":"2.0","id":4,"error":{"code":-32602,"message":"params._meta must be an object carrying the required
#     'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys"}}
# (Notification: keine Antwortzeile)
# << {"jsonrpc":"2.0","id":5,"result":{"cacheScope":"private","resultType":"complete","tools":[],"ttlMs":0,"_meta":{...}}}
