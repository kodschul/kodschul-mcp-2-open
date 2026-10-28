"""Starter Lab 2.1: rohe JSON-RPC-Requests gegen den eigenen stdio-Server aus Lab 1.2.

Kopieren nach playground/raw_requests.py. Aufruf im Projektordner: python playground/raw_requests.py
Hängt das Skript, fehlt meist eine Antwort (z. B. "id" bei einer Notification gesetzt): Ctrl+C.
"""

import json
import subprocess
import sys

SERVER = "playground/server.py"  # eigener Server aus Lab 1.2 (noch ohne Tools)

# Angaben, die jeder Request in params._meta mitträgt (die "Hülle", siehe Lab 2.1).
META = {
    "io.modelcontextprotocol/protocolVersion": "2026-07-28",
    "io.modelcontextprotocol/clientInfo": {"name": "raw-script", "version": "0.1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}


def send(proc: subprocess.Popen, message: dict) -> None:
    """Schickt eine Nachricht als eine JSON-Zeile; liest bei Requests (mit "id") genau eine Antwortzeile."""
    print(">>", json.dumps(message, ensure_ascii=False))
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    if "id" in message:
        print("<<", proc.stdout.readline().strip(), "\n")


def main() -> None:
    # stderr=DEVNULL blendet Logs des Servers aus; zur Fehlersuche stderr=None setzen.
    proc = subprocess.Popen([sys.executable, SERVER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        # Aufgabe 1 (vorgegeben): Fähigkeiten des Servers erfragen
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": META}})

        # TODO(Aufgabe 2): tools/list senden (id 2, params mit _meta) und die Antwort ansehen
        # TODO(Aufgabe 3): unbekannte Methode "nope/list" senden (id 3, params mit _meta)
        # TODO(Aufgabe 4): tools/list ohne params/_meta senden (id 4) und die Fehlerantwort ansehen
        # TODO(Aufgabe 5): Notification "notifications/cancelled" ohne "id" senden, danach tools/list mit id 5
    finally:
        proc.kill()


if __name__ == "__main__":
    main()
