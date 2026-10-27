# Lab 1.1 – Übung: Vergleichstabelle MCP gegen direkte API-Integration

**Dauer:** ca. 15 Minuten (Einzelarbeit, danach Abgleich im Plenum)
**Ändert die Vantra-Projektbasis?** Nein – reines Handout, kein Projektcode (Lab 1.2 baut den ersten Server)

## Ausgangslage

Vantra Systems betreibt zwei interne Schnittstellen: die Ticket-API (`GET /tickets/<id>`) und die Deployment-API. Drei KI-Anwendungen sollen beide nutzen:

| Anwendung | Beschreibung |
| --- | --- |
| A | Chat-Assistent für den Support |
| B | Assistent in der Entwicklungsumgebung des DevOps-Teams |
| C | Agentenprototyp „Vantra Ops Agent“ |

Zwei Varianten stehen zur Wahl: Jede Anwendung bindet jede API selbst an (direkte Integration), oder die APIs stehen hinter je einem MCP-Server.

Arbeitsdatei: ein leeres Textdokument oder Papier. Projektdateien werden nicht gebraucht.

## Aufgaben

1. Zähle für die direkte Integration, wie viele Anbindungen entstehen (Anwendungen × Schnittstellen). Zähle danach die Bausteine bei MCP (Clients + Server).
2. Übernimm die Tabelle unten und fülle für jede Zeile beide Spalten mit einem kurzen Satz.
3. Markiere in der Tabelle eine Zeile, in der die direkte Integration die bessere Wahl bleibt (Einführungsaufwand beachten).
4. Ordne den Satz „Das Modell entscheidet, welches Tool aufgerufen wird“ einer der Rollen Host, Client oder Server zu.

| Kriterium | Direkte Integration | MCP |
| --- | --- | --- |
| Anzahl Anbindungen | | |
| Beschreibung der Tools | | |
| Neues Tool `get_deployment_log` kommt hinzu | | |
| Wechsel des Modellanbieters | | |
| Wiederverwendung in einer vierten Anwendung | | |
| Einführungsaufwand | | |

## Checkpoint

- Beide Anbindungszahlen stehen auf dem Papier.
- Jede der sechs Tabellenzeilen hat zwei ausgefüllte Zellen.
- Eine Zeile ist als Vorteil der direkten Integration markiert.
- Die Rollenzuordnung aus Aufgabe 4 ist mit einer Begründung notiert.

## Abschlusskriterien

- Vollständig ausgefüllte Vergleichstabelle liegt vor.
- Die Rolle des Codes aus Lab 1.2 (Server) ist benannt.

## Erweiterung (optional)

Ergänze eine Zeile „Sicherheitsgrenze“ und notiere, wo bei direkter Integration und bei MCP die Rechte der API geprüft werden können.

## Fallback

Ohne Papier und Editor genügt die mündliche Zuordnung der Zeilen; die Lösung enthält die vollständige Tabelle zum Abgleich.
