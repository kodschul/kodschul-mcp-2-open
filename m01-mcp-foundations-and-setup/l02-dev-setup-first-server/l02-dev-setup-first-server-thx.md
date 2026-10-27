# Lab 1.2: Dev-Setup und erster eigener MCP-Server

**Leitfragen:**

<details>
<summary>Wie ermittelt der Client, welche Tools und Fähigkeiten der Server anbietet?</summary>

Der Client fragt nach: `tools/list` liefert die Tools mit Beschreibung und Schema, das optionale `server/discover` liefert Fähigkeiten (`capabilities`) und unterstützte Protokollversionen. Ein `initialize`-Handshake ist seit Spezifikation 2026-07-28 nicht nötig.

</details>

<details>
<summary>Welche Transportart nutzt der Starter-Server, und warum?</summary>

stdio: `mcp.run()` startet ohne Argumente den Standardtransport. Der Client startet den Server als Kindprozess, es gibt keinen Netzwerkport und keine eigene Authentifizierung; das ist für lokale Entwicklung am einfachsten.

</details>

- Ein MCP-Server in Python besteht aus einem `MCPServer`-Objekt und einem Aufruf von `mcp.run()`.
- Ein Server ohne Tools ist gültig: er läuft, meldet seine Fähigkeiten und liefert eine leere Tool-Liste.

## Ablauf im Projekt

| Schritt | Befehl (im Ordner `output/project/`, venv aktiv) |
| --- | --- |
| Pakete prüfen | `pip list` zeigt `mcp 2.3.0` (Installation: `00-setup-and-installation.md`) |
| Starter in den Playground kopieren | `cp starters/m01-l02-first-server.py playground/server.py` |
| Lücken schließen | `TODO(Aufgabe n)` in `playground/server.py` |
| Server mit Skript-Client prüfen | `python shared/script_client.py --server playground/server.py` |
| Server mit MCP Inspector prüfen | `npx @modelcontextprotocol/inspector python playground/server.py` |

Der Playground ist der einzige Arbeitsbereich. Das fertige Vergleichsbeispiel liegt unter `examples/m01-mcp-foundations-and-setup/l02-dev-setup-first-server/server.py`.

## Der minimale Server

```python
"""Vantra Ops Agent – leerer MCP-Server (Lab 1.2)."""

from mcp.server import MCPServer          # SDK 2.x: MCPServer, nicht FastMCP (SDK 1.x)

mcp = MCPServer(
    "vantra-ops",                         # Servername, der Clients angezeigt wird
    instructions="MCP-Server des Vantra Ops Agent. Noch ohne Tools: Aufbau folgt in den nächsten Labs.",
)

if __name__ == "__main__":
    mcp.run()  # stdio: der Client startet diesen Prozess und spricht über stdin/stdout
```

| Teil | Bedeutung |
| --- | --- |
| `MCPServer("vantra-ops", instructions=…)` | Name und Kurzbeschreibung; beides erscheint in `server/discover` |
| `mcp.run()` | startet den Standardtransport stdio und blockiert, bis der Client die Verbindung schließt |
| `if __name__ == "__main__":` | Der Client startet die Datei als Programm (`python server.py`) |

Der Starter `starters/m01-l02-first-server.py` ist unvollständig: `MCPServer()` hat keinen Namen und `mcp.run()` fehlt. Er bricht ab mit:

```text
TODO(Aufgabe 2): Server starten, hier fehlt der Aufruf von mcp.run()
```

## Transportwahl: stdio oder Streamable HTTP

| | stdio | Streamable HTTP |
| --- | --- | --- |
| Start | Client startet den Server als Kindprozess | Server läuft eigenständig und lauscht auf einer URL |
| Verbindung | stdin/stdout, eine JSON-Nachricht pro Zeile | HTTP-Endpunkt (z. B. `http://localhost:8000/mcp`) |
| Aufruf im Server | `mcp.run()` | `mcp.run(transport="streamable-http", host=…, port=…)` |
| Typischer Einsatz | lokale Entwicklung, Tag 1 | entfernter Betrieb, Container ab Modul 6 |

Bei stdio gehört stdout dem Protokoll. Ausgaben mit `print()` im Server würden die Nachrichten stören; Logs gehören auf stderr.

## Der Server von außen: server/discover und tools/list

Der Skript-Client verbindet den Server und fragt ab:

```bash
python shared/script_client.py --server playground/server.py
```

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: (keine)
```

Dahinter stehen JSON-RPC-Nachrichten. Es gibt keinen `initialize`-Handshake: der Client sendet direkt Requests, jeder mit der Protokollversion in `params._meta`. Antwort auf `server/discover` (Server aus Lab 2.2, bei dem `instructions` den Text „Tickets abfragen“ trägt):

```json
{"jsonrpc":"2.0","id":1,"result":{"cacheScope":"private","capabilities":{"prompts":{"listChanged":true},"resources":{"listChanged":true,"subscribe":true},"tools":{"listChanged":true}},"instructions":"MCP-Server des Vantra Ops Agent: Tickets abfragen.","resultType":"complete","supportedVersions":["2026-07-28"],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

Die Nachrichten im Detail folgen in Lab 2.1.

## MCP Inspector

Der Inspector ist der Standard-Testclient des Kurses. Er startet den Server als Kindprozess und zeigt Tools, Resources und Nachrichten.

| Befehl | Wirkung |
| --- | --- |
| `npx @modelcontextprotocol/inspector python playground/server.py` | Weboberfläche, Server über stdio |
| `npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/list` | Ausgabe in der Konsole, ohne Browser |

Ausgabe von `--method tools/list` für den leeren Server:

```json
{
  "tools": []
}
```

## Typische Fehler

| Symptom | Ursache | Lösung |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'mcp'` | venv nicht aktiv | `source .venv/bin/activate` |
| `ImportError … FastMCP` | Code aus einem SDK-1.x-Tutorial | `from mcp.server import MCPServer` |
| Server startet und zeigt nichts | normal: stdio-Server wartet auf einen Client | `Ctrl+C`, danach Skript-Client oder Inspector |
| `TODO(Aufgabe 2): Server starten …` | Starter noch nicht vervollständigt | `mcp.run()` ergänzen |
| Inspector findet den Server nicht | Pfad relativ zum falschen Ordner | Befehl im Ordner `output/project/` ausführen |

## Fazit

- `MCPServer(name, instructions=…)` plus `mcp.run()` genügt für einen lauffähigen Server.
- Der Server nutzt stdio; der Client startet ihn als Kindprozess.
- Skript-Client und Inspector erkennen Name, Protokollversion und Tools über `server/discover` und `tools/list`.

Die Übung vervollständigt den Starter und verbindet den Server mit Skript-Client und Inspector.
