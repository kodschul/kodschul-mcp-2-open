# Lab 3.1 – Übung: State vs. Memory

**Dauer:** ca. 15 Minuten (Plenum, Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Nein — reine Entscheidungsübung; der Kontext wird in Lab 3.2 umgesetzt.
**Arbeitsdatei:** `playground/m03-l01-entscheidung.md`
**Starter:** keiner
**Beispiel zum Vergleich:** `examples/m03-context-and-state/l02-context-schema-implementation/server.py` (Neustart-Effekt)

## Vorbereitung

- Terminal im Projektordner `output/project/`, virtuelle Umgebung aktiv (`source .venv/bin/activate`).
- Leere Datei `playground/m03-l01-entscheidung.md` anlegen.

## Aufgaben

1. Lege in `playground/m03-l01-entscheidung.md` diese Tabelle an:

   ```markdown
   | Datentyp | Ort (Kontextfenster / Session-State / Memory) | Lebensdauer | Risiko | Begründung (1 Zeile) |
   | --- | --- | --- | --- | --- |
   | laufende Konversation | | | | |
   | Nutzerpräferenz | | | | |
   | einmaliges Tool-Ergebnis | | | | |
   ```

2. Fülle die drei Zeilen aus. Wende die drei Fragen aus der Theorie an (Lebensdauer, Sichtbarkeit für das Modell, Sensibilität).
3. Weise vier weitere Daten einem Ort zu und ergänze sie als Zeilen: API-Token des Mock-Servers, zuletzt abgefragte Ticket-ID, Rolle des Nutzers (`viewer`/`operator`), Text einer Ticket-Beschreibung.
4. Belege den Neustart-Effekt. Rufe nacheinander in zwei getrennten Prozessen auf:

   ```bash
   python shared/script_client.py --server examples/m03-context-and-state/l02-context-schema-implementation/server.py --call get_ticket '{"ticket_id": "VAN-102"}'
   python shared/script_client.py --server examples/m03-context-and-state/l02-context-schema-implementation/server.py --call get_deployment_log '{}'
   ```

   Notiere die Fehlermeldung des zweiten Aufrufs und ergänze unter der Tabelle einen Satz, warum sie auftritt.
5. Stelle die Tabelle kurz im Plenum vor und überarbeite Zeilen, bei denen die Gruppe anders entscheidet.

## Checkpoint

- Jede Zeile der Tabelle nennt genau einen Ort und eine Lebensdauer.
- Der zweite Befehl aus Aufgabe 4 endet mit `is_error=True` und der Meldung `Keine ticket_id angegeben und kein Ticket im Kontext`.
- Mindestens eine Zeile ist als „nie ins Memory“ markiert und begründet.

## Abschlusskriterien

- Tabelle mit sieben Zeilen in `playground/m03-l01-entscheidung.md`.
- Der Satz zum Neustart-Effekt nennt den Grund: Jeder `--call` startet einen neuen Serverprozess mit leerem State.

## Erweiterung (optional)

Ergänze drei Datenarten, die im Ops-Alltag anfallen (z. B. Eskalationsregeln, Bereitschaftsplan, Ergebnis einer Fehleranalyse), und lege fest, welche ein Memory bräuchte und wer es löschen darf.

## Fallback

Läuft der Server nicht, entfällt Aufgabe 4; die Meldung steht in der Theorie von Lab 3.1 und wird in Lab 3.2 selbst erzeugt.
