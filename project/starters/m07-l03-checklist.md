# Review-Befunde – Starter (Lab 7.3)

Kopieren nach `playground/review.md`. Geprüft wird das Dockerfile und die Policy des Nachbarn oder die Trainer-Konfiguration (`examples/m07-security-hardening/l03-security-review/flawed/`).

Prüfer:in: `<Name>` · Geprüftes Objekt: `<Pfad>`

## Checkliste

TODO(Aufgabe 1): Jede Zeile mit ✔ (erfüllt), ✘ (nicht erfüllt) oder ? (nicht prüfbar) bewerten und bei ✘ die Fundstelle notieren.

| # | Prüffrage | Ergebnis | Fundstelle |
| - | --------- | -------- | ---------- |
| A1 | Basis-Image mit fester Version? | | |
| A2 | Läuft der Prozess als Nicht-Root-Nutzer? | | |
| A3 | Keine Secrets im Image oder in `ENV`? | | |
| A4 | Nur benötigte Dateien kopiert (`.dockerignore`)? | | |
| A5 | Abhängigkeiten gepinnt? | | |
| A6 | `HEALTHCHECK` vorhanden? | | |
| A7 | Nur benötigte Ports und Pakete? | | |
| B1 | Rollen nach Least Privilege? | | |
| B2 | Deny by default? | | |
| B3 | Rolle aus vertrauenswürdiger Quelle? | | |
| B4 | Schreib-Tools nur mit Bestätigung? | | |
| B5 | Durchsetzung im Server? | | |
| B6 | Jeder Aufruf protokolliert? | | |
| B7 | Eigene Identität je Client? | | |

## Befunde

TODO(Aufgabe 2): Jeden ✘ als Befund festhalten und die Schwere vergeben (blockierend, wichtig, nice to have).

| # | Gegenstand | Fundstelle | Befund | Schwere | Empfehlung |
| - | ---------- | ---------- | ------ | ------- | ---------- |
| 1 | | | | | |

## Leitfragen

TODO(Aufgabe 3): Welcher Befund blockiert den Produktionseinsatz, welcher ist nice to have? Je eine Begründung.
