# Context-Cheatsheet

Schnellreferenz für Modul 3 (State vs. Memory, Kontextschema, Konflikte bei mehreren Agenten). Alle Befehle im Projektordner `output/project/` mit aktiver virtueller Umgebung.

## Speicherorte

| Ort | Lebensdauer | Beispiel im Projekt |
| --- | --- | --- |
| Kontextfenster | ein Modellaufruf (Nachrichtenliste des Clients) | `messages` im Agent-Client |
| Session-State | Serverprozess | `session` in `context.py` |
| Memory (persistent) | über Sessions | im Kursprojekt nicht umgesetzt |
| Geheimnisse, Tokens | nie im Prompt oder Memory | Umgebungsvariablen des Prozesses |

## Kontextschema (`context.py`)

| Syntax | Wirkung |
| --- | --- |
| `SESSION_SCHEMA = [{"feld": …, "quelle": …, "lebensdauer": …, "an_llm": …}]` | Schema als Daten: Feld, Quelle, Lebensdauer, Sichtbarkeit |
| `@dataclass class SessionContext` | Felder des Session-State |
| `last_ticket: dict \| None = None` | ein Feld je Tool-Ergebnis |
| `ticket_versions: dict[str, int] = field(default_factory=dict)` | veränderliches Feld mit Standardwert |
| `session.remember_ticket(ticket)` | legt Ausschnitt `id, title, status, version` ab |
| `session.remember_deployment(deployment)` | legt Ausschnitt `id, service, version, status` ab |
| `session.resolve_ticket_id(explicit)` | explizite ID gewinnt, sonst `last_ticket["id"]`, sonst `None` |
| `session.to_llm_view()` | nur die für das Modell sichtbaren Felder |
| `session.tool_calls += 1` | Zähler, nur im Server sichtbar |
| `session = SessionContext()` | eine Instanz je Serverprozess |

## Tools und Resources am Kontext

| Syntax | Wirkung |
| --- | --- |
| `@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))` | Lese-Tool kennzeichnen |
| `def get_deployment_log(ticket_id: str \| None = None, tail: int = 20)` | optionales Argument; Docstring wird zur Tool-Beschreibung |
| `raise ToolError("…")` | erwarteter Fehler; Text erreicht das Modell, Ergebnis `isError: true` |
| `from mcp.server.mcpserver.exceptions import ToolError` | Importpfad (nicht aus `mcp.server.mcpserver`) |
| `deployment["log"][-tail:]` | nur die letzten `tail` Zeilen zurückgeben |
| `@mcp.resource("context://session", mime_type="application/json")` | Kontext als lesbare Resource |
| `await client.read_resource("context://session")` | Resource im Client lesen (`.contents[0].text`) |

## Konflikterkennung

| Syntax | Wirkung |
| --- | --- |
| `update_ticket_status(ticket_id, status, expected_version)` | Schreib-Tool mit zuvor gelesener Version |
| `backend.update_ticket(ticket_id, status, expected_version)` | prüft die Version, erhöht sie bei Erfolg um 1 |
| `except VersionConflict as exc` | `exc.expected`, `exc.current` |
| `error_result("version_conflict", msg, ticket_id=…, expected_version=…, current_version=…)` | strukturierter Fehler mit `is_error=True` |
| Rückgabetyp `Any` | nötig, wenn ein Tool `dict` oder `CallToolResult` liefert |

Fehlerergebnis:

```json
{"error": "version_conflict", "message": "Ticket VAN-102 wurde zwischenzeitlich geändert. Neu lesen mit get_ticket und erneut versuchen.", "ticket_id": "VAN-102", "expected_version": 3, "current_version": 4}
```

## Synchronisationsstrategien

| Strategie | Prinzip | Eignung Ops |
| --- | --- | --- |
| Versionsprüfung | Schreiben nur mit aktueller Version | Standard |
| Sperre | Objekt vorab sperren, Timeout nötig | kurze, kritische Schreibvorgänge |
| Zusammenführen | nur bei gleichem Ziel oder getrennten Feldern | Erweiterung, vorsichtig |

## Befehle

| Befehl | Wirkung |
| --- | --- |
| `python playground/context.py` | Kurztest des Kontexts (Starter-Selbsttest) |
| `python shared/script_client.py --server playground/server.py` | Server und Tools auflisten |
| `python shared/script_client.py --server playground/server.py --call get_deployment_log '{"ticket_id": "VAN-102", "tail": 2}'` | ein Tool aufrufen (jeder Aufruf = neuer Serverprozess, leerer State) |
| `python shared/agent_client.py --server playground/server.py --replay` | Dialog in einem Prozess (Skript-Agent), Kontext bleibt erhalten |
| `python shared/mock_api/app.py` | Mock-API als gemeinsamer Zustand (Port 8001) |
| `MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-a --hold 10 --status resolved` | Agent A: lesen, warten, schreiben |
| `MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-b --status in_progress` | Agent B: lesen, sofort schreiben |
| `curl -s localhost:8001/tickets/VAN-102` | aktuellen Ticketstand der Mock-API lesen |
| `curl -X POST localhost:8001/reset` | Daten zurücksetzen |

## Typische Fehler

| Symptom | Ursache |
| --- | --- |
| `Keine ticket_id angegeben und kein Ticket im Kontext` | neuer Prozess oder `get_ticket` nie aufgerufen |
| beide Agenten melden `ok`, Änderung von B fehlt | Server ohne `expected_version` (Starter-Stand) |
| kein Konflikt trotz zwei Clients | `MOCK_API_URL` fehlt: zwei Prozesse mit getrennten Daten |
| Konflikt schon beim ersten Lauf | Daten nicht zurückgesetzt (Version > 3) |
| `InvalidSignature` beim Start | Rückgabetyp `dict \| CallToolResult` statt `Any` |
