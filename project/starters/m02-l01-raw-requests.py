"""Starter Lab 2.1: rohe JSON-RPC-Requests gegen den eigenen stdio-Server.

Kopieren nach playground/raw_requests.py. Aufruf im Projektordner: python playground/raw_requests.py
Der Server (playground/server.py) kommt aus Lab 1.2 bzw. 2.2.
"""

import json
import subprocess
import sys

SERVER = "playground/server.py"
# Seit Spezifikation 2026-07-28 trägt jeder Request diese Angaben selbst; ein initialize-Handshake ist nicht nötig.
META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "raw-script", "version": "0.1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}


def send(proc: subprocess.Popen, message: dict) -> None:
    print(">>", json.dumps(message, ensure_ascii=False))
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    if "id" in message:
        print("<<", proc.stdout.readline().strip(), "\n")


def main() -> None:
    proc = subprocess.Popen([sys.executable, SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        # Beispiel: Fähigkeiten des Servers erfragen
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": META}})

        # TODO(Aufgabe 1): tools/list senden (id 2, params mit _meta) und die Antwort ansehen
        # TODO(Aufgabe 2): tools/call für get_ticket mit ticket_id VAN-102 senden (ab Lab 2.2)
        # TODO(Aufgabe 3): denselben Aufruf ohne _meta senden und die Fehlerantwort erklären
        # TODO(Aufgabe 4): eine Notification senden (ohne "id") und beobachten, dass keine Antwort kommt
    finally:
        proc.kill()


if __name__ == "__main__":
    main()
