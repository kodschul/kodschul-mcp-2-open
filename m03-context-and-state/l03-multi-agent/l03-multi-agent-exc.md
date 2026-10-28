# Lab 3.3 – Übung: Zwei Agenten, ein Kontext

**Dauer:** ca. 15 Minuten (Einzel/Paar); vorbereitet sind `error_result`, alle Imports und eine Vorlage für Aufgabe 3
**Ändert die Vantra-Projektbasis?** Ja — `playground/server.py` erhält `update_ticket_status` mit Versionsprüfung; Modul 4 und Tag 2 bauen darauf auf.
**Arbeitsdatei:** `playground/server.py` (mit `playground/context.py` aus Lab 3.2)
**Starter:** `starters/m03-l03-conflict.py`
**Beispiel zum Vergleich:** `examples/m03-context-and-state/l03-multi-agent/server.py`

## Vorbereitung

- Lab 3.2 ist abgeschlossen: `playground/context.py` liegt vor. Fehlt der Stand, kopiere `examples/m03-context-and-state/l03-multi-agent/context.py` nach `playground/context.py`.
- Sichere den eigenen Server aus Lab 3.2 (`cp playground/server.py playground/server-l32.py`) und kopiere danach den Starter: `cp starters/m03-l03-conflict.py playground/server.py`. Der Starter ersetzt `server.py`: Er enthält den Stand des Beispiels aus Lab 3.2 plus das Schreib-Tool `update_ticket_status` ohne Versionsprüfung; eigene Abweichungen aus Lab 3.2 liegen danach in `server-l32.py`.
- Terminal 1 (Mock-API als gemeinsamer Zustand): `python shared/mock_api/app.py`. Das Terminal bleibt offen; die Mock-API läuft, bis sie mit `Ctrl+C` beendet wird.
- Terminal 2 und Terminal 3: jeweils im Projektordner mit aktiver venv öffnen (unter Windows Git Bash).
- Der Ist-Zustand (stilles Überschreiben mit dem Starter) steht als Ausgabe in der Theorie, Abschnitt „Das Problem: stilles Überschreiben“. Wer ihn selbst sehen will, führt die beiden Befehle aus Aufgabe 4 jetzt einmal mit dem Starter aus und setzt danach mit `curl -X POST localhost:8001/reset` zurück.

## Aufgaben

1. Ergänze in `playground/server.py` den Parameter `expected_version: int` bei `update_ticket_status` (`TODO(Aufgabe 1)`) und erweitere den Docstring um seine Bedeutung.
2. Übergib `expected_version` als dritten Parameter an `backend.update_ticket` (`TODO(Aufgabe 2)`).
3. Fange `VersionConflict` ab (`TODO(Aufgabe 3)`): Entferne bei der Vorlage im Starter die Kommentarzeichen, rücke den Block wie `except InvalidStatus` ein und formuliere die Meldung so, dass sie dem Agenten sagt, was zu tun ist. `error_result` und der Import von `VersionConflict` sind vorhanden.
4. Setze die Daten zurück und löse den Konflikt aus. Starte Terminal 3 innerhalb der 10 Sekunden, in denen Agent A „überlegt“:

   ```bash
   # Terminal 2 oder 3, vorab
   curl -X POST localhost:8001/reset
   # Terminal 2: Agent A liest, wartet 10 Sekunden, schreibt resolved
   MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-a --hold 10 --status resolved
   # Terminal 3: Agent B liest und schreibt sofort in_progress
   MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-b --status in_progress
   ```

5. Lies den Endstand mit `curl localhost:8001/tickets/VAN-102` und vergleiche ihn mit dem Ist-Zustand aus der Theorie.

## Checkpoint

- Agent B meldet `-> ok` und das Ticket hat Version 4.
- Agent A meldet `-> FEHLER:` mit `"error": "version_conflict"`, `"expected_version": 3` und `"current_version": 4`.
- `curl localhost:8001/tickets/VAN-102` zeigt weiter `in_progress` (Version 4): Die Änderung von Agent B ist nicht überschrieben.

## Abschlusskriterien

- `update_ticket_status` verlangt `expected_version` und meldet Konflikte als strukturierten Fehler (`is_error=True`).
- Der Ablauf mit zwei Clients ist mit dem Beispielserver und dem eigenen Server identisch.

## Erweiterung (optional)

Zusammenführungsstrategie (`TODO(Erweiterung)`): Entspricht bei einem Konflikt der gewünschte Status bereits dem aktuellen Status, gib das aktuelle Ticket zurück statt eines Fehlers. Prüfe beide Fälle: beide Agenten setzen `in_progress` (kein Fehler) und A setzt `resolved` nach B's `in_progress` (Konflikt).

## Fallback

- Ohne zweites Terminal: Agent A mit `&` am Zeilenende im Hintergrund starten, danach sofort Agent B im selben Terminal.
- Ist die Mock-API nicht startbar (Port 8001 belegt), setze `MOCK_API_PORT` auf einen freien Port und passe `MOCK_API_URL` an.
- Fehlt die Zeit, entfällt die Übung zugunsten einer Plenumsdiskussion der drei Strategien aus der Theorie; der Beispielserver in `examples/m03-context-and-state/l03-multi-agent/server.py` zeigt das Ergebnis.
