# Observability-Cheatsheet (Modul 8)

Pfade relativ zu `output/project/`. Alle Befehle im Projektordner mit aktiver virtueller Umgebung.

## Tool-Call-Protokoll

| Feld | Inhalt |
| --- | --- |
| `ts` | UTC, ISO 8601 mit Millisekunden |
| `tool` | Name des Tools |
| `role` | `VANTRA_ROLE` des Servers (Standard `viewer`) |
| `status` | `ok`, `denied`, `conflict`, `error` |
| `error_code` | `policy_denied`, `confirmation_required`, `version_conflict`, Ausnahmeklasse oder `null` |
| `duration_ms` | Dauer in Millisekunden |
| `args` | Argumente ohne `confirmed` |

| Fehlercode | `status` |
| --- | --- |
| `policy_denied`, `confirmation_required` | `denied` |
| `version_conflict` | `conflict` |
| alle anderen Fehler und Ausnahmen | `error` |

Nicht protokollieren: Ticket-Texte, Log-Inhalte, Secrets, Tokens, `confirmed`. stdout gehört bei stdio dem Protokoll; Logs gehen nach stderr oder in eine Datei.

## Code

| Baustein | Zweck |
| --- | --- |
| `setup_logging()` | Logger `vantra` mit `JsonFormatter` auf stderr (`LOG_LEVEL`, Standard `INFO`) |
| `@logged("<tool>")` | unter `@mcp.tool(...)`: misst Dauer, schreibt JSONL-Zeile und Log-Zeile, auch bei Fehlern |
| `log_tool_call(record)` | hängt eine JSON-Zeile an `TOOL_CALL_LOG` an |
| `ALERT_RULES` | Liste von `{name, status, schwelle, fenster_s, schwere}` |
| `evaluate_alerts(records)` | liefert ausgelöste Regeln (Beispielstand `examples/m08-…/l01-monitoring-setup/logging_config.py`) |

Standardregeln: `viele-abgelehnte-aufrufe` (`denied`, 3 in 60 s, hoch) und `viele-fehler` (`error`, 5 in 300 s, mittel).

## Befehle

| Befehl | Wirkung |
| --- | --- |
| `TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/agent_client.py --server playground/server.py --replay workflow --role viewer --confirm yes` | Workflow ausführen und Protokoll schreiben |
| `cat logs/tool_calls.jsonl` | Protokoll ansehen |
| `python examples/m08-observability-and-capstone/l01-monitoring-setup/logging_config.py` | Alarmregeln gegen das Protokoll prüfen (Ausgabe `{'regel': 'keine Alarme'}` ohne Treffer) |
| `TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py` | Dashboard auf http://localhost:8080 |
| `curl localhost:8080/api/calls` | JSON mit `summary` und `calls` |
| `grep -c -E "description\|confirmed" logs/tool_calls.jsonl` | Datenschutzprüfung (Ausgabe `0`) |

## Dashboard

| Route | Inhalt |
| --- | --- |
| `/` | Zeitleiste, Summen je Status, Alarmbanner |
| `/api/calls` | `summary` (`total`, `by_status`, `alert`, `recent_denied`, `generated_at`) und `calls` (letzte 200) |
| `/health` | `{"status": "ok"}` |

Banner: mindestens 3 `denied` in den letzten 60 Sekunden (im Dashboard fest eingetragen).

## Abschlussprojekt

| Befehl | Wirkung |
| --- | --- |
| `python examples/m08-observability-and-capstone/l02-capstone-integration/run_demo.py` | Workflow ohne Container: `viewer`, `operator` mit Bestätigung, `operator` ohne Bestätigung |
| `docker compose -f playground/docker-compose.yml up --build` | Stack mit Rolle `viewer` |
| `VANTRA_ROLE=operator docker compose -f playground/docker-compose.yml up --build` | Stack mit Rolle `operator` |
| `python shared/agent_client.py --url http://localhost:8000/mcp --replay workflow --confirm yes` | Workflow gegen den Container |
| `docker compose -f playground/docker-compose.yml down` | Stack stoppen |
| `curl -X POST http://localhost:8001/reset` | Mock-Daten zurücksetzen |

| Schritt | Rolle `viewer` | Rolle `operator`, `--confirm yes` | Rolle `operator`, `--confirm none` |
| --- | --- | --- | --- |
| 1 `get_ticket` VAN-102 | ok | ok | ok |
| 2 `get_deployment_log` | ok | ok | ok |
| 3 `update_ticket_status` auf `in_progress` | `policy_denied` | ok, Version 4 | `confirmation_required` |

| Port | Dienst |
| --- | --- |
| 8000 | MCP-Server (`/mcp`, `/health`) |
| 8001 | Mock-API (`/tickets`, `/health`, `POST /reset`) |
| 8080 | Dashboard |

## Umgebungsvariablen

| Variable | Wirkung |
| --- | --- |
| `VANTRA_ROLE` | Rolle des Servers (`viewer`, `operator`) |
| `TOOL_CALL_LOG` | Pfad der JSONL-Datei (Standard `logs/tool_calls.jsonl`, im Container `/data/tool_calls.jsonl`) |
| `LOG_LEVEL` | Stufe der Log-Zeilen (Standard `INFO`) |
| `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT` | Transport und Bindung des Servers |
| `MOCK_API_URL` | Mock-API statt prozesslokaler Daten |

## Lücken bis zum Produktivbetrieb

Authentifizierung je Client · Bestätigung unabhängig vom Client · Ratenbegrenzung · DNS-Rebinding-Schutz bei Host `0.0.0.0` · Log-Aufbewahrung und -Zugriff · Kontext je Client · ausgeführter Infrastrukturtest · Test mit echtem Modell.

## Quellen für Trends (Stand: 27.10.2026, abgerufen am 27.10.2026)

| Thema | URL |
| --- | --- |
| Änderungen der Revision 2026-07-28 | https://modelcontextprotocol.io/specification/2026-07-28/changelog |
| Roadmap | https://modelcontextprotocol.io/development/roadmap |
| Autorisierung | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization |
| Versionierung | https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning |
| SDKs | https://modelcontextprotocol.io/docs/2026-07-28/sdk |
