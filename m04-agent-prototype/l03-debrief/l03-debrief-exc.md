# Lab 4.3 – Übung: Debrief

**Dauer:** ca. 15 Minuten (Plenum)
**Ändert die Vantra-Projektbasis?** Nein — Auswertung des Testlaufs; die Liste ordnet Tag 2.
**Arbeitsdatei:** `playground/debrief.md`
**Starter:** keiner (Eingabe: `playground/testlauf.md` aus Lab 4.2)
**Beispiel zum Vergleich:** `examples/m04-agent-prototype/l02-end-to-end-testrun/testdialog.md` (Beobachtungen)

## Vorbereitung

- `playground/testlauf.md` aus Lab 4.2 liegt vor. Fehlt sie, dient `examples/m04-agent-prototype/l02-end-to-end-testrun/testdialog.md` als Eingabe.
- Leere Datei `playground/debrief.md` anlegen.

## Aufgaben

1. Lege in `playground/debrief.md` diese Tabelle an und übertrage jede Lücke und Auffälligkeit aus dem Testprotokoll als Zeile:

   ```markdown
   | Risiko | Beleg aus dem Testlauf | Schaden | Wahrscheinlichkeit | Baustein | Rang |
   | --- | --- | --- | --- | --- | --- |
   ```

2. Bewerte Schaden und Wahrscheinlichkeit je Zeile mit hoch, mittel oder niedrig. Begründe jede Einstufung „hoch“ in einem Halbsatz.
3. Ordne jeder Zeile den Baustein zu: Absicherung, Betrieb oder Monitoring.
4. Vergib Rang 1 bis 3 an die drei wichtigsten Zeilen. Schaden zählt vor Wahrscheinlichkeit.
5. Beantworte unter der Tabelle in zwei Sätzen: Welches Risiko wäre in einer echten Vantra-Umgebung am kritischsten, und was braucht der Prototyp zuerst?
6. Vergleiche die Rangfolge im Plenum und passe Rang oder Einstufung an, wenn die Gruppe mit Begründung anders entscheidet.

## Checkpoint

- Die Tabelle enthält mindestens vier Zeilen, jede mit Beleg, Bewertung und Baustein.
- Genau drei Zeilen tragen einen Rang.
- Der Zwei-Satz-Abschnitt nennt ein Risiko und einen Baustein mit Begründung.

## Abschlusskriterien

- `playground/debrief.md` enthält die priorisierte Tabelle und den Entscheidungssatz.
- Jedes Risiko stützt sich auf eine Beobachtung aus Lab 4.2.

## Erweiterung (optional)

Wechsle die Perspektive: Ordne die Risiken aus Sicht einer Betriebsrolle und einer Sicherheitsrolle jeweils neu und markiere Zeilen, bei denen sich der Rang unterscheidet. Halte fest, wer die Entscheidung über die Reihenfolge trifft.

## Fallback

Fehlt `playground/testlauf.md`, genügen die Beobachtungen aus `examples/m04-agent-prototype/l02-end-to-end-testrun/testdialog.md`. Ohne Plenum entfällt Aufgabe 6; die Rangfolge bleibt eine begründete Einzelentscheidung.
