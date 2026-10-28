# Lab 7.3 – Übung: Security-Review mit Checkliste

**Dauer:** ca. 25 Minuten
**Ändert die Vantra-Projektbasis?** Nein — Ergebnis ist ein Review-Dokument; Code, Dockerfile und Policy des Projekts bleiben unverändert.
**Arbeitsdatei:** `playground/review.md`
**Starter:** `starters/m07-l03-checklist.md`
**Prüfgegenstand (allein oder als Paar):** `examples/m07-security-hardening/l03-security-review/flawed/Dockerfile` und `flawed/policy.md` (Trainer-Konfiguration). Im Paar alternativ `playground/Dockerfile` und `playground/policy.md` der Nachbarin oder des Nachbarn.
**Prüfgrundlage:** `examples/m07-security-hardening/l03-security-review/checklist.md`
**Beispielbefunde:** `examples/m07-security-hardening/l03-security-review/findings-beispiel.md` erst ab Aufgabe 4 öffnen.

## Vorbereitung

- Starter kopieren: `cp starters/m07-l03-checklist.md playground/review.md`.
- Im Kopf der Datei Prüfer:in und geprüftes Objekt (Pfad) eintragen.
- `checklist.md` zum Nachlesen öffnen. Der Starter enthält alle 21 Prüfpunkte (A1–A8, B1–B8, C1–C5).
- Im Paar mit eigenem Stand: Platz tauschen oder die Dateien am Bildschirm der Nachbarin oder des Nachbarn lesen; eine Datei-Übertragung ist nicht nötig.

**Zeitplan:** Aufgabe 1 ca. 10 Minuten, Aufgabe 2 ca. 8 Minuten, Aufgabe 3 und 4 je ca. 3–4 Minuten.

## Aufgaben

1. **Checkliste bewerten:** Lies Dockerfile und Policy vollständig. Bewerte jede Zeile der Gruppen A und B mit ✔, ✘ oder ? und notiere bei ✘ die Fundstelle. Bewerte die Gruppe C, soweit sie sich aus den beiden Dateien ableiten lässt; alles andere erhält ?.
2. **Befunde festhalten:** Formuliere jeden ✘ als Befund (Gegenstand, Fundstelle, Befund, Schwere, Empfehlung). Schwere: blockierend, wichtig oder nice to have.
3. **Leitfragen beantworten:** Nenne die Befunde, die einen Produktionseinsatz blockieren, und einen, der „nice to have“ ist. Begründe je in einem Satz. Halte die Entscheidung fest: Freigabe ja oder nein.
4. **Vergleichen:** Öffne `findings-beispiel.md`. Ergänze übersehene Befunde. Begründe Abweichungen bei der Schwere in einem Satz.

## Checkpoint

- Jede Zeile der Gruppen A und B hat ein Ergebnis (✔, ✘ oder ?).
- Jeder ✘ erscheint als Befund mit Fundstelle, Schwere und Empfehlung.
- Mindestens ein blockierender Befund ist benannt und begründet.
- Die Freigabeentscheidung steht in `playground/review.md`.

## Abschlusskriterien

- `playground/review.md` enthält Checkliste, Befundtabelle, Antworten zu den Leitfragen und die Freigabeentscheidung.
- Jeder Befund hat eine konkrete Empfehlung, keine allgemeine Mahnung.
- Abweichungen vom Vergleich sind begründet.

## Erweiterung (optional)

- **Eigener Stand:** Prüfe `playground/Dockerfile` und `playground/policy.md` aus den eigenen Labs mit derselben Checkliste. Dokumentiere Befunde und, falls vorhanden, was offen bleibt.
- **Ohne Programmierung (Entscheidung):** Verfasse eine Freigabeempfehlung für ein Architekturgremium in höchstens zehn Zeilen: Bedingungen für die Freigabe, Reihenfolge der Behebung, Restrisiko, Zuständige für die Nachprüfung.

## Fallback

Fehlt ein Nachbar, bleibt die Trainer-Konfiguration in `flawed/` der Prüfgegenstand; alle Aufgaben sind damit allein lösbar.
