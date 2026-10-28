# MCP-Grundlagen: Cheatsheet

## Rollen und Primitives

| Begriff | Bedeutung |
| --- | --- |
| Host | hält die Verbindungen zu den Servern und entscheidet, welcher Aufruf passiert (Agent: LLM schlägt vor; Inspector/Skript-Client: Person) |
| Agent | Anwendung, in der ein LLM in einer Schleife Tools vorschlägt und die Anwendung sie ausführt, bis eine Textantwort steht |
| Client | Verbindung zu genau einem Server (`mcp.Client`) |
| Server | bietet Tools, Resources, Prompts (`MCPServer`) |
| Tool | Aktion, vom Modell gewählt |
| Resource | lesbare Daten per URI, von der Anwendung gewählt |
| Prompt | Vorlage, von Nutzer:innen gewählt |

## Setup

| Befehl | Wirkung |
| --- | --- |
| `python -m venv .venv` | venv anlegen (im Ordner `output/project/`) |
| `source .venv/bin/activate` | venv aktivieren (Windows, Git Bash: `source .venv/Scripts/activate`) |
| `pip install -r requirements.txt` | Pakete in festen Versionen installieren |
| `pytest -q` | alle Tests, kein LLM nötig |

## Erster Server

| Code | Wirkung |
| --- | --- |
| `from mcp.server import MCPServer` | Import in SDK 2.x (nicht `FastMCP`) |
| `mcp = MCPServer("vantra-ops", instructions="…")` | Server mit Name und Beschreibung |
| `mcp.run()` | startet stdio, blockiert bis zum Verbindungsende |
| `cp starters/m01-l02-first-server.py playground/server.py` | Starter in den Arbeitsbereich |

## Testen

| Befehl | Wirkung |
| --- | --- |
| `python shared/script_client.py --server playground/server.py` | Skript-Client: Name, Protokollversion, Tools |
| `npx @modelcontextprotocol/inspector python playground/server.py` | Inspector mit Weboberfläche: Adresse mit Token öffnen → **Connect** → Tab **Tools** → **List Tools** |
| `npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/list` | Tool-Liste in der Konsole |
| `python playground/server.py` | direkter Start: keine Ausgabe, wartet auf Client (`Ctrl+C`) |

## Transporte

| Transport | Start | Aufruf |
| --- | --- | --- |
| stdio | Client startet Server als Kindprozess | `mcp.run()` |
| Streamable HTTP | Server lauscht, Endpunkt `/mcp` | `mcp.run(transport="streamable-http", host=…, port=…)` |

## Ablauf eines Tool-Aufrufs (Lab 1.1)

| Schritte | Was passiert |
| --- | --- |
| 1–3 | Host fragt über den Client `tools/list`, Server liefert die Tools |
| 4–6 | Host gibt Frage und Tool-Liste ans LLM, LLM schlägt einen Tool-Call vor |
| 7–12 | Client sendet `tools/call`, Server führt aus und fragt die API |
| 13–15 | Ergebnis geht ans LLM: Textantwort oder nächster Tool-Call |

## Entdeckung (Spezifikation 2026-07-28)

| Nachricht | Zweck |
| --- | --- |
| `server/discover` | optional: Fähigkeiten, unterstützte Versionen, `instructions` |
| `tools/list` | Tools mit Beschreibung und Eingabeschema |
| kein `initialize` | Handshake entfällt; Versionsangabe steht in `params._meta` jedes Requests |

## Häufige Fehler

| Symptom | Lösung |
| --- | --- |
| `No module named 'mcp'` | venv aktivieren |
| `cannot import name 'FastMCP'` | `MCPServer` aus `mcp.server` verwenden |
| Server „hängt“ nach dem Start | normal bei stdio; Client verwenden |
| `print()` im stdio-Server | stört das Protokoll; stderr nutzen |
