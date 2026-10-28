# Lab 8.1 – Übung: Strukturiertes Logging und Alarm

**Dauer:** ca. 20 Minuten
**Ändert die Vantra-Projektbasis?** Ja — `logging_config.py` und `@logged` im Server; der Stand entspricht `examples/m08-observability-and-capstone/l01-monitoring/` und ist die Basis für Lab 8.2.
**Arbeitsdateien:** `playground/logging_config.py`, `playground/server.py`
**Starter:** `starters/m08-l01-logging.py`
**Beispiel (zum Vergleichen):** `examples/m08-observability-and-capstone/l01-monitoring/` (`logging_config.py`, `server.py`)
**Zusätzliche Werkzeuge:** `shared/agent_client.py`, `shared/dashboard/server.py`

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`.
- `playground/` enthält den Stand von Lab 7.1 (`server.py`, `context.py`, `auth.py`, `policy.md`). Fehlen Dateien: aus `checkpoints/ende-m07-abgesichert/` nach `playground/` kopieren.
- Starter kopieren: `cp starters/m08-l01-logging.py playground/logging_config.py`.
- Altes Protokoll entfernen, falls vorhanden: `rm -f logs/tool_calls.jsonl`.

## Aufgaben

`JsonFormatter` (JSON-Zeilen auf stderr), `log_tool_call` (eine JSON-Zeile je Aufruf in `TOOL_CALL_LOG`) und das Gerüst von `logged` mit `try`/`except`/`finally` sind im Starter vorgegeben. Ablauf des Decorators: Abschnitt „So arbeitet `@logged`“ in der Theorie.

**Zeitplan:** Aufgabe 1–4 ca. 10 Minuten, Aufgabe 5–8 ca. 10 Minuten.

1. **Tool-Call-Protokoll:**
   - 1a: Ergänze `_classify`: Bei `result.is_error` den Code aus `result.structured_content["error"]` lesen und auf `denied`, `conflict` oder `error` abbilden; sonst `ok`.
   - 1b: Ersetze im `finally`-Block das `pass`: Baue den Eintrag mit `ts`, `tool`, `role`, `status`, `error_code`, `duration_ms` und `args`, rufe `log_tool_call(entry)` auf und schreibe die Log-Zeile auf den Logger `vantra`. `confirmed` gehört nicht in `args`.
2. **Beispielalarm:** Fülle `ALERT_RULES` mit mindestens einer Regel: Status, Schwelle, Zeitfenster in Sekunden, Schwere.
3. **Einbinden:** Importiere `logged` und `setup_logging` in `playground/server.py` und rufe `log = setup_logging()` auf.
4. **Dekorieren:** Setze `@logged("<toolname>")` unter `@mcp.tool(...)` bei allen drei Tools.
5. **Aufrufe erzeugen:** Starte den Workflow dreimal mit Rolle `viewer`. Der Schreibaufruf wird jedes Mal abgelehnt.

```bash
for i in 1 2 3; do
  TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/agent_client.py --server playground/server.py --replay workflow --role viewer --confirm yes
done
cat logs/tool_calls.jsonl
```

6. **Dashboard ansehen:** Starte das Dashboard in einem zweiten Terminal und öffne http://localhost:8080. Prüfe Zeitleiste, Summen und Alarmbanner. Das Banner gilt für die letzten 60 Sekunden; bei Bedarf Aufgabe 5 wiederholen.

```bash
TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py
```

7. **Datenschutz prüfen:** Suche im Protokoll nach Ticket-Texten und `confirmed`: `grep -c -E "Login-Seite|description|confirmed" logs/tool_calls.jsonl`.
8. **Regel auswerten:** Werte die eigenen `ALERT_RULES` gegen das Protokoll aus. `evaluate_alerts` und `read_records` sind im Starter vorgegeben.

```bash
TOOL_CALL_LOG=logs/tool_calls.jsonl python playground/logging_config.py
```

## Checkpoint

- `logs/tool_calls.jsonl` hat neun Zeilen: je Lauf `get_ticket`, `get_deployment_log` und `update_ticket_status`.
- Die drei `update_ticket_status`-Zeilen haben `status: "denied"` und `error_code: "policy_denied"`.
- Auf stderr erscheinen JSON-Zeilen mit `message` der Form `tool_call <tool> <status>`.
- Das Dashboard zeigt neun Aufrufe, davon drei `denied`, und das Alarmbanner.
- Der `grep`-Zähler aus Aufgabe 7 ist `0`.
- Aufgabe 8 druckt innerhalb des Zeitfensters die eigene Regel für `denied` als ausgelösten Alarm.

Erwartete Ausgabe von `cat logs/tool_calls.jsonl` je Lauf (Auszug, `ts` und `duration_ms` variieren):

```json
{"ts": "…", "tool": "get_ticket", "role": "viewer", "status": "ok", "error_code": null, "duration_ms": 0.05, "args": {"ticket_id": "VAN-102"}}
{"ts": "…", "tool": "update_ticket_status", "role": "viewer", "status": "denied", "error_code": "policy_denied", "duration_ms": 0.05, "args": {"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3}}
```

## Wenn es hakt

| Symptom | Ursache | Lösung |
| --- | --- | --- |
| `logs/tool_calls.jsonl` fehlt oder bleibt leer | `@logged` steht über `@mcp.tool(...)`; das SDK registriert dann die Funktion ohne Decorator | `@logged("<tool>")` direkt unter `@mcp.tool(...)` setzen |
| Datei bleibt leer, Agent läuft normal | Agent startet einen anderen Server (`--server` fehlt oder `MCP_SERVER_URL` gesetzt) | `--server playground/server.py` angeben, `MCP_SERVER_URL` in `.env` auskommentieren |
| `args` ist immer `{}` | Argumente werden aus `args` statt `kwargs` gelesen | `kwargs` verwenden; das SDK ruft Tools mit Schlüsselwort-Argumenten auf |
| Alle Einträge haben `status: "ok"` | `_classify` liefert noch den Platzhalter | Aufgabe 1a fertigstellen |
| Agent hängt oder meldet einen Protokollfehler | Log-Ausgabe mit `print` auf stdout stört JSON-RPC | nur `logging` (stderr) oder `log_tool_call` (Datei) verwenden |
| Kein Alarmbanner im Dashboard | letzte Ablehnungen älter als 60 Sekunden | Aufgabe 5 wiederholen, Seite neu laden |
| `Address already in use` beim Dashboard | Port 8080 belegt | `DASHBOARD_PORT=8090` voranstellen und http://localhost:8090 öffnen |

## Abschlusskriterien

- Alle drei Tools schreiben je Aufruf genau einen Eintrag, auch bei Ablehnung.
- Das Protokoll enthält weder Ticket-Texte noch Log-Inhalte noch Secrets.
- `ALERT_RULES` enthält eine begründete Regel.

## Erweiterung (optional)

Ergänze in `ALERT_RULES` eine zweite Regel für den Status `conflict` (Versionskonflikte, Lab 3.3) und prüfe mit Aufgabe 8, dass sie bei den drei Workflow-Läufen nicht auslöst.

Ohne Programmierung (Entscheidung): Lege fest, wer bei einem Alarm der Regel „viele-abgelehnte-aufrufe“ benachrichtigt wird, welche Sofortmaßnahme gilt und wie lange das Protokoll aufbewahrt wird. Trage die Entscheidung in `playground/policy.md` unter „Erkennung und Reaktion“ ein.

## Fallback

Ohne Dashboard-Port (8080 belegt) genügen `cat logs/tool_calls.jsonl` und `python examples/m08-observability-and-capstone/l01-monitoring/logging_config.py`; der Befehl wertet dasselbe Protokoll mit den Regeln des Beispiels aus. Der Alarm des Dashboards entfällt dann.
