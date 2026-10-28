# Lab 3.2 – Übung: Kontextschema entwerfen und einbauen

**Dauer:** ca. 40 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja — `playground/context.py` und das zweite Tool in `playground/server.py` sind Grundlage für Lab 3.3 und Modul 4.
**Arbeitsdatei:** `playground/context.py` und `playground/server.py`
**Starter:** `starters/m03-l02-context.py`
**Beispiel zum Vergleich:** `examples/m03-context-and-state/l02-context-schema/` (`context.py`, `server.py`)

## Vorbereitung

- Terminal im Projektordner `output/project/`, virtuelle Umgebung aktiv.
- `playground/server.py` enthält den Stand aus Lab 2.2 (Tool `get_ticket`). Fehlt die Datei, kopiere `examples/m02-protocol-and-messages/l02-first-tool/server.py` nach `playground/server.py`.
- Kopiere den Starter: `cp starters/m03-l02-context.py playground/context.py`.

## Aufgaben

1. Vervollständige in `playground/context.py` das Schema (`TODO(Aufgabe 1)`): Ergänze das Datenfeld `last_deployment` in `SessionContext` und eine zweite Zeile in `SESSION_SCHEMA` mit Feld, Quelle, Lebensdauer und Sichtbarkeit. Ergänze danach zwei Zeilen für die Felder, die nur der Server nutzt (`ticket_versions`, `tool_calls`).
2. Implementiere `remember_deployment` (`TODO(Aufgabe 2)`): Nur `id`, `service`, `version`, `status` landen in `last_deployment`.
3. Implementiere `resolve_ticket_id` und `to_view` (`TODO(Aufgabe 3)`): Eine explizite ID gewinnt, sonst gilt die ID des zuletzt abgefragten Tickets; `to_view` gibt nur `last_ticket` und `last_deployment` zurück. Starte danach `python playground/context.py`.
4. Binde den Kontext in `playground/server.py` ein. `server.py` enthält keine TODO-Marker; die Schritte stehen im Kopfkommentar von `playground/context.py` unter `TODO(Aufgabe 4)`. Ergänze `from context import SESSION_SCHEMA, session` bei den Imports, lege das Ergebnis von `backend.get_ticket` in einer Variablen `ticket` ab, rufe danach `session.remember_ticket(ticket)` auf und gib `ticket` zurück. Zähle jeden Tool-Aufruf mit `session.tool_calls += 1`.
5. Ergänze in `playground/server.py` das zweite Tool `get_deployment_log(ticket_id: str | None = None, tail: int = 20)` (Kopfkommentar `TODO(Aufgabe 5)` in `context.py`): ID über `session.resolve_ticket_id` auflösen, Deployment über `backend.latest_deployment` laden, mit `session.remember_deployment` merken, Metadaten plus die letzten `tail` Zeilen von `log` zurückgeben. Ist weder eine ID angegeben noch ein Ticket im Kontext, melde einen `ToolError`; fange außerdem `NotFound` (Ticket ohne Deployment) als `ToolError` ab.
6. Prüfe einzelne Aufrufe mit dem Skript-Client (Befehle im Checkpoint).
7. Prüfe das Zusammenspiel in einer Session mit dem Inspector: Starte `npx @modelcontextprotocol/inspector python playground/server.py`, klicke „Connect“, rufe im Tab „Tools“ zuerst `get_ticket` mit `VAN-102` auf, danach `get_deployment_log` mit leerem Feld `ticket_id`.

## Checkpoint

- `python playground/context.py` gibt aus:

  ```text
  Kontext nach Ticket: {'id': 'VAN-102', 'title': 'Beispiel', 'status': 'open', 'version': 3}
  Aufgelöste Ticket-ID: VAN-102
  ```

- `python shared/script_client.py --server playground/server.py` listet `Tools: get_ticket, get_deployment_log`.
- `python shared/script_client.py --server playground/server.py --call get_deployment_log '{"ticket_id": "VAN-102", "tail": 2}'` zeigt `dep-2041` mit genau zwei Log-Zeilen.
- `python shared/script_client.py --server playground/server.py --call get_deployment_log '{}'` endet mit `is_error=True` und der Meldung zum fehlenden Ticket im Kontext (neuer Prozess, leerer State).
- Im Inspector liefert `get_deployment_log` ohne `ticket_id` nach `get_ticket` das Deployment `dep-2041` mit `"ticket_id": "VAN-102"`.

## Abschlusskriterien

- `playground/context.py` enthält `SESSION_SCHEMA` mit vier Zeilen und die vollständige Klasse `SessionContext`.
- Kein Tool schreibt in das Feld eines anderen Tools.
- `playground/server.py` stellt zwei Tools bereit und verweist beide auf denselben `session`.

## Erweiterung (optional)

Ergänze in `playground/server.py` die Resource `context://session` (`TODO(Erweiterung)`), die `SESSION_SCHEMA` und `session.to_view()` zurückgibt. Verbinde den Inspector neu, rufe `get_ticket` und `get_deployment_log` auf und lies danach im Tab „Resources“ `context://session`.

## Fallback

- Fehlt der Stand aus Lab 2.2, dient `examples/m02-protocol-and-messages/l02-first-tool/server.py` als Ausgangspunkt.
- Startet der Inspector nicht (z. B. `npx` blockiert): Der Befehl `python shared/agent_client.py --server playground/server.py --replay` ruft beide Tools in einem Prozess nacheinander auf. Das Werkzeug wird in Lab 4.1 erklärt; hier dient es nur als fertiges Prüfskript mit festen Aufrufen.
- Bleibt die Aufgabe hängen, ersetze `playground/context.py` und `playground/server.py` durch die Dateien aus dem Beispielordner und arbeite mit Lab 3.3 weiter.
