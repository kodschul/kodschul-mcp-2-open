# Agent-Cheatsheet

Schnellreferenz für Modul 4 (Agent-Client, Testlauf, Debrief). Alle Befehle im Projektordner `output/project/` mit aktiver virtueller Umgebung.

## Agent-Client mit MCP-Python-SDK 2.3.0

| Syntax | Wirkung |
| --- | --- |
| `from mcp import Client` | Client des SDKs |
| `from mcp.client.stdio import StdioServerParameters` | Parameter für einen stdio-Server als Kindprozess |
| `StdioServerParameters(command=sys.executable, args=[SERVER])` | startet `server.py` mit dem Python der aktiven venv |
| `async with Client(params) as client:` | Verbindung öffnen und sicher schließen |
| `Client("http://host:8000/mcp")` | Streamable HTTP statt stdio |
| `(await client.list_tools()).tools` | entdeckte Tools (`name`, `description`, `input_schema`) |
| `await client.call_tool(name, arguments)` | Tool aufrufen |
| `result.is_error` | `True` bei Tool-Fehler |
| `result.content` | Liste von Inhalten; Text: `c.text` bei `c.type == "text"` |
| `result.structured_content` | strukturierter Inhalt, z. B. bei `version_conflict` |
| `client.protocol_version`, `client.server_info.name` | `2026-07-28`, `vantra-ops` |

## Tool-Schleife

| Schritt | Code |
| --- | --- |
| Tool in LLM-Format | `{"type": "function", "function": {"name": tool.name, "description": tool.description or "", "parameters": tool.input_schema}}` |
| Modell fragen | `reply = llm.chat(messages, llm_tools)` → `{"content": …, "tool_calls": […]}` |
| Ende der Schleife | `reply["tool_calls"]` ist leer: `reply["content"]` ist die Antwort |
| Assistenten-Nachricht mit Tool-Wunsch | `{"role": "assistant", "content": …, "tool_calls": [{"id": …, "type": "function", "function": {"name": …, "arguments": json.dumps(args)}}]}` |
| Ergebnis zurück | `{"role": "tool", "tool_call_id": call["id"], "content": text}` |
| Fehler kennzeichnen | Präfix `"FEHLER: "` bei `result.is_error` |

## LLM-Backend (`.env`)

| Variable | Standard | Wirkung |
| --- | --- | --- |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | OpenAI-kompatibler Endpunkt (Ollama lokal) |
| `LLM_MODEL` | `qwen3:8b` | Modellname (Fallback `qwen3:4b`) |
| `LLM_API_KEY` | `ollama` | Schlüssel; wird nicht an den Server-Prozess weitergegeben |
| `MCP_SERVER_SCRIPT` | `playground/server.py` | Standard-Server des Agent-Clients |
| `MCP_SERVER_URL` | leer | Standard-URL für HTTP |

## Befehle

| Befehl | Wirkung |
| --- | --- |
| `python playground/agent.py` | eigener Agent, echtes LLM laut `.env` (leere Eingabe beendet) |
| `python playground/agent.py --replay` | eigener Agent mit Replay-LLM (Skript-Agent) |
| `python shared/agent_client.py --server playground/server.py` | vorbereiteter Agent-Client, echtes LLM |
| `python shared/agent_client.py --server playground/server.py --replay` | Replay-Skript `dialog` (Skript-Agent) |
| `python shared/agent_client.py --server playground/server.py --replay workflow --confirm none` | Replay-Skript `workflow` (Ticket, Log, Statusänderung) |
| `python shared/agent_client.py --server playground/server.py --replay --prompt "Zeige Ticket VAN-999"` | einzelne Eingabe (`--prompt` mehrfach möglich) |
| `python shared/script_client.py --server playground/server.py` | Tools auflisten, ohne LLM |

## Replay-Skripte (`shared/replay_llm.py`)

| Skript | Eingaben | Zweck |
| --- | --- | --- |
| `dialog` | `Zeige Ticket VAN-102`, `Zeige das Deployment-Log dazu` | kanonischer Testdialog (Modul 4) |
| `workflow` | Ticket, Deployment-Log, `Setze das Ticket auf in_progress` | Ticket → Log → Statusänderung |
| `injection` | `Zeige Ticket VAN-106` | Angriffsablauf, später im Kurs |

## Testprotokoll (`playground/testlauf.md`)

| Abschnitt | Inhalt |
| --- | --- |
| Befehl und verwendeter Agent | echtes LLM mit Modellname oder Skript-Agent (Replay) |
| Testdialog | Eingabe, erwarteter und tatsächlicher Tool-Call, Ergebnis ok? |
| Beobachtungen | Tool-Auswahl, Argumente, Antwortqualität, Dauer; Bewertung: wie erwartet / Auffälligkeit / Lücke |
| Lücken für Tag 2 | je Lücke eine Zeile mit Beleg |

## Ausgabe lesen

| Zeile | Bedeutung |
| --- | --- |
| `Entdeckte Tools: …` | Ergebnis von `tools/list` |
| `→ Tool-Call: name(args)` | Wunsch des Modells |
| `← ok: …` / `← FEHLER: …` | Ergebnis des Tools |
| `Agent: …` | Antwort an den Nutzer |
| `LLM: replay` | Skript-Agent: Tool-Calls vorgegeben |

## Typische Fehler

| Symptom | Ursache |
| --- | --- |
| `NotImplementedError: TODO(Aufgabe n)` | Lücke im Starter nicht ausgefüllt |
| Verbindungsfehler zum LLM | Ollama läuft nicht oder `LLM_BASE_URL` falsch: `--replay` nutzen |
| Modell ruft kein oder falsches Tool | Beschreibung unklar oder Modell zu klein; Docstring abgrenzend formulieren |
| `Keine ticket_id angegeben und kein Ticket im Kontext` | neuer Prozess: erst `get_ticket`, dann Log in einer Sitzung |
| `playground/server.py` nicht gefunden | Stand aus Lab 3.3 fehlt: aus `examples/m03-context-and-state/l03-multi-agent-sync/` kopieren |
