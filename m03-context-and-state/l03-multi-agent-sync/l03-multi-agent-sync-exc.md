# Lab 3.3 – Übung: Zwei Agenten, ein Kontext

**Dauer:** ca. 20 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja — `playground/server.py` erhält `update_ticket_status` mit Versionsprüfung; Modul 4 und Tag 2 bauen darauf auf.
**Arbeitsdatei:** `playground/server.py` (mit `playground/context.py` aus Lab 3.2)
**Starter:** `starters/m03-l03-conflict.py`
**Beispiel zum Vergleich:** `examples/m03-context-and-state/l03-multi-agent-sync/server.py`

## Vorbereitung

- Lab 3.2 ist abgeschlossen: `playground/context.py` liegt vor. Fehlt der Stand, kopiere `examples/m03-context-and-state/l03-multi-agent-sync/context.py` nach `playground/context.py`.
- Kopiere den Starter: `cp starters/m03-l03-conflict.py playground/server.py`.
- Terminal 1 (Mock-API als gemeinsamer Zustand): `python shared/mock_api/app.py`.
- Konflikt auslösen, damit der Ist-Zustand sichtbar ist. Terminal 2 und Terminal 3 jeweils im Projektordner mit aktiver venv; Terminal 3 innerhalb der 10 Sekunden nach Terminal 2 starten:

  ```bash
  # Terminal 2
  MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-a --hold 10 --status resolved
  # Terminal 3
  MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-b --status in_progress
  ```

- Notiere, welchen Status `VAN-102` am Ende hat (`curl localhost:8001/tickets/VAN-102`) und ob Agent A eine Meldung bekam.
- Setze die Daten zurück: `curl -X POST localhost:8001/reset`.

## Aufgaben

1. Ergänze in `playground/server.py` den Parameter `expected_version: int` bei `update_ticket_status` (`TODO(Aufgabe 1)`) und erweitere den Docstring um seine Bedeutung.
2. Übergib `expected_version` als dritten Parameter an `backend.update_ticket` (`TODO(Aufgabe 2)`).
3. Fange `VersionConflict` ab (`TODO(Aufgabe 3)`) und gib `error_result("version_conflict", ...)` mit `ticket_id`, `expected_version` und `current_version` zurück. Die Meldung soll dem Agenten sagen, was zu tun ist.
4. Wiederhole den Ablauf aus der Vorbereitung (erst `reset`, dann Terminal 2 und 3) und vergleiche das Ergebnis mit dem Ist-Zustand.

## Checkpoint

- Agent B meldet `-> ok` und das Ticket hat Version 4.
- Agent A meldet `-> FEHLER:` mit `"error": "version_conflict"`, `"expected_version": 3` und `"current_version": 4`.
- `curl localhost:8001/tickets/VAN-102` zeigt weiter `in_progress` (Version 4): Die Änderung von Agent B ist nicht überschrieben.

## Abschlusskriterien

- `update_ticket_status` verlangt `expected_version` und meldet Konflikte als strukturierten Fehler (`is_error=True`).
- Der Ablauf mit zwei Clients ist mit dem Beispielserver und dem eigenen Server identisch.

## Erweiterung (optional)

Zusammenführungsstrategie (`TODO(Aufgabe 4)`): Entspricht bei einem Konflikt der gewünschte Status bereits dem aktuellen Status, gib das aktuelle Ticket zurück statt eines Fehlers. Prüfe beide Fälle: beide Agenten setzen `in_progress` (kein Fehler) und A setzt `resolved` nach B's `in_progress` (Konflikt).

## Fallback

- Ohne zweites Terminal: zwei Läufe nacheinander im selben Terminal, den ersten mit `&` im Hintergrund.
- Ist die Mock-API nicht startbar (Port 8001 belegt), setze `MOCK_API_PORT` auf einen freien Port und passe `MOCK_API_URL` an.
- Fehlt die Zeit, entfällt die Übung zugunsten einer Plenumsdiskussion der drei Strategien aus der Theorie; der Beispielserver in `examples/m03-context-and-state/l03-multi-agent-sync/server.py` zeigt das Ergebnis.
