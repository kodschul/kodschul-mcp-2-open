# Lab 1.3 – Übung: Architektur-Mapping am eigenen Server

**Dauer:** ca. 12 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Nein – Handout ohne Code; nutzt den laufenden Server aus Lab 1.2

## Vorbereitung

- `playground/server.py` aus Lab 1.2 ist vorhanden und startet.
- Skript-Client und (falls verfügbar) Inspector aus Lab 1.2 laufen.
- Arbeitsdatei: `playground/architektur.md` oder Papier. Die Datei gehört zum Playground und wird nicht versioniert.

## Aufgaben

1. Führe `python shared/script_client.py --server playground/server.py` aus. Notiere, welche Angaben der Ausgabe vom Server stammen (Name, Tools) und welches Programm die Ausgabe erzeugt.
2. Liste alle beteiligten Komponenten auf: Terminal, Skript, Client-Objekt, Server-Prozess, Verbindung, Datenquelle.
3. Ordne jede Komponente einer Rolle zu: Host, Client, Server, Transport oder Datenquelle.
4. Zeichne ein Diagramm (Mermaid, Text oder Papier) mit Pfeilen für die Richtung der Requests. Beschrifte die Pfeile mit dem Transport.
5. Markiere im Diagramm die Komponente, die entscheidet, welches Tool aufgerufen wird. Notiere, wer das beim Skript-Client, beim Inspector und beim Agenten (Modul 4) ist.
6. Zeichne die Vertrauensgrenze zwischen Client und Server als gestrichelte Linie ein und notiere je eine Prüfung auf beiden Seiten.

## Checkpoint

- Das Diagramm enthält Host, Client, Server, Transport (stdio) und die Datenquelle.
- Jeder Pfeil trägt eine Richtung und eine Beschriftung.
- Die Tool-Entscheidung ist für drei Werkzeuge benannt.
- Die Vertrauensgrenze ist eingezeichnet und mit zwei Prüfungen beschriftet.

## Abschlusskriterien

- Beschriftetes Diagramm des eigenen Setups liegt vor.
- Die Antwort auf „Wer wählt das Tool?“ unterscheidet Skript, Inspector und Agent.

## Erweiterung (optional)

Ergänze den Fall „Server als Container mit Streamable HTTP“ (Modul 6) als zweites Diagramm: Welche Elemente ändern sich, welche bleiben?

## Fallback

Ohne laufenden Server genügt Aufgabe 2 bis 6 auf Basis des Textes aus Lab 1.2 und der Tabelle „Rollen in den Werkzeugen des Kurses“ in `l03-architecture-mapping-thx.md`.
