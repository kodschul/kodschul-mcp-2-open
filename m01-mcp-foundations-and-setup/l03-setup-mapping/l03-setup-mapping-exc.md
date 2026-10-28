# Lab 1.3 – Übung: Architektur-Mapping am eigenen Server

**Dauer:** ca. 12 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Nein – Handout ohne Code; nutzt den laufenden Server aus Lab 1.2

## Vorbereitung

- `playground/server.py` aus Lab 1.2 ist vorhanden und startet.
- Skript-Client und (falls verfügbar) Inspector aus Lab 1.2 laufen.
- Arbeitsdatei: Papier (empfohlen) oder `playground/architektur.md`. Die Datei gehört zum Playground und wird nicht versioniert.
- Vorlage zum Beschriften (abzeichnen oder in die Datei kopieren und die `?` ersetzen):

```text
[ ? ] --> [ ? : script_client.py ] --> [ ? : mcp.Client ] ==( ? )==> [ ? : playground/server.py ] - - -> [ ? ]
          |<------------ Prozess 1 ------------>|                    |<--------- Prozess 2 --------->|
```

## Aufgaben

1. Führe `python shared/script_client.py --server playground/server.py` aus. Notiere, welche Angaben der Ausgabe vom Server stammen (Name, Tools) und welches Programm die Ausgabe erzeugt.
2. Liste alle beteiligten Komponenten auf: Terminal, Skript, Client-Objekt, Server-Prozess, Verbindung, Datenquelle (die Mock-API nutzt der Server erst ab Lab 2.2; im Diagramm gestrichelt eintragen).
3. Ordne jede Komponente einer Rolle zu: Host, Client, Server, Transport oder Datenquelle.
4. Beschrifte die Vorlage aus der Vorbereitung (oder zeichne das Diagramm frei) mit Pfeilen für die Richtung der Requests. Beschrifte die Pfeile mit dem Transport.
5. Markiere im Diagramm die Komponente, die entscheidet, welches Tool aufgerufen wird. Notiere, wer das beim Skript-Client, beim Inspector und beim Agenten (Modul 4) ist.
6. Zeichne die Vertrauensgrenze zwischen Client und Server als gestrichelte Linie ein und notiere je eine Prüfung auf beiden Seiten.

## Checkpoint

- Das Diagramm enthält Host, Client, Server, Transport (stdio) und die Datenquelle (gestrichelt, ab Lab 2.2).
- Jeder Pfeil trägt eine Richtung und eine Beschriftung.
- Die Tool-Entscheidung ist für drei Werkzeuge benannt.
- Die Vertrauensgrenze ist eingezeichnet und mit zwei Prüfungen beschriftet.

## Abschlusskriterien

- Beschriftetes Diagramm des eigenen Setups liegt vor.
- Die Antwort auf „Wer wählt das Tool?“ unterscheidet Skript, Inspector und Agent.

## Erweiterung (optional)

Ergänze den Fall „Server als Container mit Streamable HTTP“ (Modul 6) als zweites Diagramm: Welche Elemente ändern sich, welche bleiben?

## Fallback

Ohne laufenden Server genügt Aufgabe 2 bis 6 auf Basis des Textes aus Lab 1.2 und der Tabelle „Rollen in den Werkzeugen des Kurses“ in [`../l03-setup-mapping-thx.md`](../l03-setup-mapping-thx.md).
