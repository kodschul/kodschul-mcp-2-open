# Lab 1.1 – Lösung: Vergleichstabelle MCP gegen direkte API-Integration

## Aufgabe 1: Anbindungen zählen

- Direkte Integration: 3 Anwendungen × 2 Schnittstellen = 6 Adapter.
- MCP: 3 Clients (einer je Anwendung) + 2 Server (Ticket, Deployment) = 5 Bausteine. Eine vierte Anwendung kostet direkt 2 weitere Adapter, mit MCP nur einen Client.

Die Zahl allein ist bei kleinen Zahlen kein Argument. Entscheidend ist, dass Tool-Beschreibung und Ausführung nur einmal im Server liegen.

## Aufgabe 2: Tabelle ausgefüllt

| Kriterium | Direkte Integration | MCP |
| --- | --- | --- |
| Anzahl Anbindungen | 6 (3 × 2) | 5 (3 Clients + 2 Server) |
| Beschreibung der Tools | je Anwendung eigenes Schema und eigener Prompt-Text | einmal im Server, Clients lesen sie per `tools/list` |
| Neues Tool `get_deployment_log` kommt hinzu | in allen drei Anwendungen nachbauen | im Deployment-Server ergänzen, alle Clients finden es |
| Wechsel des Modellanbieters | Tool-Format der Anwendung anpassen | Server bleibt unverändert, nur Host und Modell wechseln |
| Wiederverwendung in einer vierten Anwendung | 2 neue Adapter | 1 neuer Client |
| Einführungsaufwand | gering: eine Funktion pro API | höher: Server, Prozess und Protokoll einmalig aufbauen |

## Aufgabe 3: Zeile mit Vorteil der direkten Integration

Einführungsaufwand: Bei einer einzigen Anwendung und einer einzigen API ist eine direkte Funktion schneller gebaut als ein Server. MCP lohnt sich ab mehreren Anwendungen, mehreren Schnittstellen oder wenn Modell und Anwendung austauschbar bleiben sollen.

## Aufgabe 4: Rollenzuordnung

„Das Modell entscheidet, welches Tool aufgerufen wird“ gehört zum **Host**. Der Host übergibt dem Modell die Tool-Beschreibungen und führt den vorgeschlagenen Aufruf über den Client aus. Der Client sendet nur Requests, der Server führt aus und trifft keine Tool-Auswahl.

## Erweiterung: Sicherheitsgrenze

| Kriterium | Direkte Integration | MCP |
| --- | --- | --- |
| Sicherheitsgrenze | Rechteprüfung liegt im Code der Anwendung, jede Anwendung prüft selbst | Server ist eigener Prozess mit eigener Grenze, Rechte lassen sich an einer Stelle prüfen (Modul 7) |
