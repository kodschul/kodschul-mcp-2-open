# Lab 2.1 – Übung: JSON-RPC live am eigenen Server

**Dauer:** ca. 25 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Nein – `playground/raw_requests.py` ist ein Hilfsskript, `server.py` bleibt unverändert
**Arbeitsdatei:** `playground/raw_requests.py`
**Starter:** `starters/m02-l01-raw-requests.py`
**Vergleichsbeispiel:** `examples/m02-protocol-and-messages/l01-jsonrpc-live/raw_requests.py`

## Vorbereitung

- Terminal im Ordner `output/project/`, venv aktiv.
- Der Server aus Lab 1.2 liegt unter `playground/server.py`. Für Aufgabe 2 wird ein Server mit `get_ticket` gebraucht: bis Lab 2.2 fertig ist, dient `examples/m02-protocol-and-messages/l02-first-tool/server.py`.

## Aufgaben

1. Kopiere den Starter: `cp starters/m02-l01-raw-requests.py playground/raw_requests.py`. Setze `SERVER` auf den Server aus der Vorbereitung und führe das Skript aus: `python playground/raw_requests.py`. Lies die Antwort auf `server/discover`.
2. Sende `tools/list` mit `id` 2 und `params._meta` (`TODO(Aufgabe 1)`). Notiere Toolnamen und Pflichtparameter aus der Antwort.
3. Sende `tools/call` für `get_ticket` mit `ticket_id` `VAN-102` und `id` 3 (`TODO(Aufgabe 2)`). Notiere `status`, `priority` und `isError`.
4. Sende denselben Aufruf mit `id` 4 ohne `_meta` (`TODO(Aufgabe 3)`). Notiere Fehlercode und Meldung und erkläre, warum es ein `error` und kein `result` ist.
5. Sende eine Notification (`notifications/cancelled` mit `requestId` 99, ohne `id`) und danach ein `tools/list` mit `id` 5 (`TODO(Aufgabe 4)`). Notiere, ob die Notification eine Zeile `<<` erzeugt und welche `id` die nächste Antwort trägt.
6. Erstelle ein Protokoll `playground/protokoll.md` mit je einer Zeile pro Nachricht: Richtung, Art (Request, Response, Notification), `id`, `method`.

## Checkpoint

- `server/discover` und `tools/list` liefern `"resultType":"complete"`.
- Die `tools/call`-Antwort enthält den Text mit `"status": "open"` und `"isError":false`.
- Der Request ohne `_meta` liefert ein Objekt mit `"error"` und dem Code `-32602`.
- Nach der Notification erscheint keine Antwortzeile.

## Abschlusskriterien

- `playground/raw_requests.py` läuft und gibt alle Nachrichten mit `>>` und `<<` aus.
- `playground/protokoll.md` listet jede Nachricht mit Art und `id`.
- Zu jeder Antwort ist der zugehörige Request über die `id` benannt.

## Erweiterung (optional)

Starte den Replay-Agenten mit Trace und vergleiche die Reihenfolge mit dem eigenen Protokoll: `python shared/agent_client.py --server playground/server.py --replay --trace trace.log`. Der zweite Dialogschritt schlägt mit einem Tool-Fehler fehl, solange `get_deployment_log` noch nicht existiert; das ist erwartet. Lösche `trace.log` danach.

## Fallback

- Ohne laufendes Skript: Inspector verwenden (`npx @modelcontextprotocol/inspector python playground/server.py`) und die Nachrichten im Verlaufsbereich lesen.
- Ohne Node: das Vergleichsbeispiel ausführen und die ECHTE AUSGABE am Dateiende lesen.
