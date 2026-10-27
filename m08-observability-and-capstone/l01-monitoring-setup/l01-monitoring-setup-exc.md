# Lab 8.1 – Übung: Strukturiertes Logging und Alarm

**Dauer:** ca. 25 Minuten
**Ändert die Vantra-Projektbasis?** Ja — `logging_config.py` und `@logged` im Server; der Stand entspricht `examples/m08-observability-and-capstone/l01-monitoring-setup/` und ist die Basis für Lab 8.2.
**Arbeitsdateien:** `playground/logging_config.py`, `playground/server.py`
**Starter:** `starters/m08-l01-logging.py`
**Beispiel (zum Vergleichen):** `examples/m08-observability-and-capstone/l01-monitoring-setup/` (`logging_config.py`, `server.py`)
**Zusätzliche Werkzeuge:** `shared/agent_client.py`, `shared/dashboard/server.py`

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`.
- `playground/` enthält den Stand von Lab 7.1 (`server.py`, `context.py`, `auth.py`, `policy.md`). Fehlen Dateien: aus `checkpoints/ende-m07-abgesichert/` nach `playground/` kopieren.
- Starter kopieren: `cp starters/m08-l01-logging.py playground/logging_config.py`.
- Altes Protokoll entfernen, falls vorhanden: `rm -f logs/tool_calls.jsonl`.

## Aufgaben

1. **JSON-Formatter:** Implementiere `JsonFormatter.format` in `playground/logging_config.py`. Der Eintrag enthält `ts` (UTC, ISO 8601), `level`, `logger`, `message` und die Felder aus `record.fields`; Rückgabe ist ein JSON-String.
2. **Tool-Call-Protokoll:** Implementiere `log_tool_call` (Eintrag als eine JSON-Zeile an die Datei anhängen, Ordner bei Bedarf anlegen). Ergänze in `logged` die Statusbestimmung (`ok`, `denied`, `conflict`, `error`) und rufe `log_tool_call` mit `ts`, `tool`, `role`, `status`, `error_code`, `duration_ms` und `args` auf. `confirmed` gehört nicht in `args`.
3. **Beispielalarm:** Fülle `ALERT_RULES` mit mindestens einer Regel: Status, Schwelle, Zeitfenster in Sekunden, Schwere.
4. **Einbinden:** Importiere `logged` und `setup_logging` in `playground/server.py` und rufe `log = setup_logging()` auf.
5. **Dekorieren:** Setze `@logged("<toolname>")` unter `@mcp.tool(...)` bei allen drei Tools.
6. **Aufrufe erzeugen:** Starte den Workflow dreimal mit Rolle `viewer`. Der Schreibaufruf wird jedes Mal abgelehnt.

```bash
for i in 1 2 3; do
  TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/agent_client.py --server playground/server.py --replay workflow --role viewer --confirm yes
done
cat logs/tool_calls.jsonl
```

7. **Dashboard ansehen:** Starte das Dashboard in einem zweiten Terminal und öffne http://localhost:8080. Prüfe Zeitleiste, Summen und Alarmbanner. Das Banner gilt für die letzten 60 Sekunden; bei Bedarf Aufgabe 6 wiederholen.

```bash
TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py
```

8. **Datenschutz prüfen:** Suche im Protokoll nach Ticket-Texten und `confirmed`: `grep -c -E "Login-Seite|description|confirmed" logs/tool_calls.jsonl`.

## Checkpoint

- `logs/tool_calls.jsonl` hat neun Zeilen: je Lauf `get_ticket`, `get_deployment_log` und `update_ticket_status`.
- Die drei `update_ticket_status`-Zeilen haben `status: "denied"` und `error_code: "policy_denied"`.
- Auf stderr erscheinen JSON-Zeilen mit `message` der Form `tool_call <tool> <status>`.
- Das Dashboard zeigt neun Aufrufe, davon drei `denied`, und das Alarmbanner.
- Der `grep`-Zähler aus Aufgabe 8 ist `0`.

## Abschlusskriterien

- Alle drei Tools schreiben je Aufruf genau einen Eintrag, auch bei Ablehnung.
- Das Protokoll enthält weder Ticket-Texte noch Log-Inhalte noch Secrets.
- `ALERT_RULES` enthält eine begründete Regel.

## Erweiterung (optional)

Mache `ALERT_RULES` ausführbar: Ergänze `read_records(path)` (JSONL lesen), `evaluate_alerts(records, now=None, rules=None)` (Einträge je Regel im Zeitfenster zählen, ausgelöste Regeln als Liste von Dictionaries mit `regel`, `schwere`, `anzahl`, `fenster_s` liefern) und einen `__main__`-Block, der die Ausgabe druckt. Prüfe mit Aufgabe 6 und `python playground/logging_config.py`.

Ohne Programmierung (Entscheidung): Lege fest, wer bei einem Alarm der Regel „viele-abgelehnte-aufrufe“ benachrichtigt wird, welche Sofortmaßnahme gilt und wie lange das Protokoll aufbewahrt wird. Trage die Entscheidung in `playground/policy.md` unter „Erkennung und Reaktion“ ein.

## Fallback

Ohne Dashboard-Port (8080 belegt) genügen `cat logs/tool_calls.jsonl` und `python examples/m08-observability-and-capstone/l01-monitoring-setup/logging_config.py`; der Befehl wertet dasselbe Protokoll mit den Regeln des Beispiels aus. Der Alarm des Dashboards entfällt dann.
