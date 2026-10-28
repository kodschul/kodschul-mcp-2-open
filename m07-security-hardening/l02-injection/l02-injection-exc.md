# Lab 7.2 – Übung: Manipulierte Tool-Ergebnisse analysieren

**Dauer:** ca. 15 Minuten
**Ändert die Vantra-Projektbasis?** Nein — reine Analyse; der Code bleibt unverändert, das Ergebnis ist eine Tabelle.
**Arbeitsdatei:** `playground/verteidigung.md` (neu anlegen)
**Material:** `shared/attack-samples/` (`01-…json`, `02-…json`, `03-…json`, `README.md`)

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`.
- Die Server aus Lab 3.3 (`examples/m03-context-and-state/l03-multi-agent/server.py`) und Lab 7.1 (`examples/m07-security-hardening/l01-access-control/server.py`) liegen vor.
- Datei `playground/verteidigung.md` anlegen mit der Überschrift `# Angriffsanalyse` und einem Abschnitt je Probe.

## Aufgaben

1. Öffne `shared/attack-samples/01-prompt-injection-ticket.json`. Notiere im Abschnitt „Probe 1“ mindestens drei Auffälligkeiten im Feld `manipuliertes_ergebnis`.
2. Führe Showcase C ohne Policy aus (Server aus Lab 3.3). Notiere die beiden Tool-Calls und was mit VAN-101 geschieht.

```bash
python shared/agent_client.py --server examples/m03-context-and-state/l03-multi-agent/server.py --replay injection --confirm none
```

3. Führe denselben Ablauf mit dem Server aus Lab 7.1 und `--confirm none` aus: erst mit Rolle `viewer` (Standard), dann mit `--role operator`. Notiere je Lauf die Antwort des Servers.
4. Analysiere `02-gefaelschte-tool-beschreibung.json` und `03-ueberprivilegierte-anweisung.json`: Wo steckt die Manipulation, was ist auffällig, was soll der Angriff erreichen?
5. Lege die Tabelle an und fülle sie für alle drei Proben. Die Spalte „Verteidigungslinie“ nimmt eine der Linien Modell/Prompt, Client, Server, Policy/Betrieb.

| Angriff | Gegenmaßnahme | Verteidigungslinie | Wirkt im Projekt? (ja/nein, wo) |
| --- | --- | --- | --- |
| Probe 1 | | | |
| Probe 2 | | | |
| Probe 3 | | | |

6. Nenne zu jeder Probe eine zweite Linie, die greift, wenn die erste versagt.

## Checkpoint

- Aufgabe 2 zeigt `← ok` für das Schreib-Tool; VAN-101 steht danach auf `closed`.
- Aufgabe 3 zeigt `← FEHLER` mit Code `policy_denied` (Rolle `viewer`) bzw. `confirmation_required` (Rolle `operator`).
- Die Tabelle hat drei vollständige Zeilen.

## Abschlusskriterien

- Jede Probe hat mindestens eine Gegenmaßnahme mit zugeordneter Verteidigungslinie.
- Für jede Probe ist begründet, ob das Projekt sie abdeckt.
- Mindestens eine zweite Linie je Probe ist benannt.

## Erweiterung (optional)

Ohne Programmierung: Formuliere eine eigene Probe 4, bei der die Manipulation in einem anderen Feld steckt (z. B. `title` oder `assignee`). Beschreibe Erkennungsmerkmale, Ziel und die wirksame Linie. Skizziere danach eine Erkennungsheuristik für Tool-Ergebnisse in fünf Zeilen Pseudocode und nenne zwei Fälle, die sie nicht erkennt.

## Fallback

Läuft der Replay-Agent nicht, genügen die Aufgaben 1, 4, 5 und 6. Die Beobachtungen für Aufgabe 2 und 3 stehen in der Lösung.
