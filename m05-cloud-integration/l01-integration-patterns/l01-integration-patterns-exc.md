# Lab 5.1 – Übung: Platzierung des Vantra-MCP-Servers entscheiden

**Dauer:** ca. 20 Minuten (Plenum und Einzel/Paar-Ausarbeitung)
**Ändert die Vantra-Projektbasis?** Nein – Entscheidungsübung ohne Code; das Ergebnis begründet das Container-Setup in Lab 5.2 und 6.2.
**Arbeitsdatei:** `playground/m05-l01-entscheidung.md` (neue Datei)
**Starter:** keiner (Projekt: nein)
**Vergleich:** Musterlösung in `l01-integration-patterns-sol.md`

## Ausgangslage

Vantra betreibt einen Kubernetes-Cluster. Folgende Anforderungen liegen vor:

- Der Ops Agent (intern) und ein Support-Agent (anderes Team, intern) sollen dieselben zwei Tools nutzen: Tickets lesen, Deployment-Logs lesen. Das Schreib-Tool `update_ticket_status` ist für beide eingeplant.
- Ein Partner-Dienstleister möchte später lesend auf Tickets zugreifen (extern, über das Internet).
- Die Ticket- und Deployment-API ist intern und darf nicht von außen erreichbar sein.
- Das Betriebsteam will eine Stelle, an der es Version, Logs und Rechte pflegt.

Pflichtzeilen der Tabelle sind „Ein Betriebspunkt für Version und Rechte“ und „Zwei interne Agenten teilen Server“; sie folgen aus diesen Anforderungen.

## Vorbereitung

- Theorie von Lab 5.1 (Trade-off-Tabelle) liegt offen.
- Datei `playground/m05-l01-entscheidung.md` anlegen und die Tabelle aus Aufgabe 1 hineinkopieren.

## Aufgaben

1. Kopiere diese Tabelle in die Arbeitsdatei und bewerte jede Zelle mit `+` (günstig), `o` (neutral) oder `–` (ungünstig) für das Vantra-Szenario:

   | Kriterium | Sidecar | Zentraler Service | Edge |
   | --- | --- | --- | --- |
   | Latenz für interne Agenten | | | |
   | Angriffsfläche | | | |
   | Ein Betriebspunkt für Version und Rechte | | | |
   | Zwei interne Agenten teilen Server | | | |
   | Externer Partner-Zugriff möglich | | | |
   | Kontext und Rolle je Agent getrennt | | | |

2. Zähle die `+` und `–` je Spalte und notiere die Summen unter der Tabelle.
3. Entscheide, wo der Server für die **internen** Agenten sitzt. Schreibe unter die Tabelle: `Entscheidung: …` (ein Satz) und `Begründung: …` (höchstens drei Sätze, mit Bezug auf mindestens zwei Zeilen der Tabelle).
4. Lege fest, wie der Agent den Server findet: trage in die Arbeitsdatei die Adresse ein, die der Ops Agent in Kubernetes nutzt (Schema: `http://<name>:<port>/mcp`), und die Konfigurationsvariable, über die sie gesetzt wird.
5. Lege die Versionierung fest: wie sieht der Image-Tag für Release 1.0.0 aus, und welches Kommando zeigt die Revisionen eines Deployments?
6. Nenne unter `Risiko:` genau eine Schwäche der Entscheidung und eine Gegenmaßnahme.

## Checkpoint

- Alle 18 Zellen der Tabelle sind bewertet, die Summen stehen darunter.
- Entscheidung, Begründung, Adresse, Variable, Image-Tag, Kommando und Risiko stehen in `playground/m05-l01-entscheidung.md`.
- Die Begründung nennt Zeilen der Tabelle, keine Allgemeinplätze.

## Abschlusskriterien

- Die Entscheidung ist mit der Tabelle widerspruchsfrei (die gewählte Spalte hat kein `–` in einer Pflichtzeile).
- Die Adresse folgt dem Kubernetes-Namensschema aus der Theorie.

## Erweiterung

Ohne Programmieranteil, für Architektur- und Sicherheitsrollen:

1. Zeichne ein Diagramm (Text oder Mermaid) der Vantra-Architektur mit Agent, MCP-Server, Mock-API, Dashboard und externem Partner. Markiere jede Vertrauensgrenze.
2. Notiere je Grenze eine Zeile: wer verbindet, womit authentifiziert er sich (offen: in Modul 7 festzulegen), was wird protokolliert.
3. Entscheide, ob der Partner-Zugriff über dasselbe Deployment laufen darf oder über eine getrennte Edge-Instanz mit eigener Rolle, und begründe in zwei Sätzen.

## Fallback

Keine technische Abhängigkeit. Ohne Gruppendiskussion bearbeitet jede Person die Aufgaben allein; die Musterlösung dient dann als Vergleich.
