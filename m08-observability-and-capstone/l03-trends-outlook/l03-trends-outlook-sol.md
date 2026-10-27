# Lab 8.3 – Lösung: Trends nach Relevanz sortieren

Die Rangfolge ist vom Einsatzumfeld abhängig. Das Beispiel gilt für Vantra Systems: interne Tools über MCP-Server für KI-Agenten, Betrieb in Containern, mehrere Agenten als Clients.

## Aufgaben 1–3: priorisierte Trendliste (Beispiel)

| Rang | Trend | Relevanz | Begründung | Folgefrage | Quelle |
| --- | --- | --- | --- | --- | --- |
| 1 | 5 Agent-Identität und Enterprise-Security | hoch | Betroffenheit: Die Rolle gilt heute je Server-Prozess, nicht je Client (Lab 7.1); die größte Lücke vor dem Produktivbetrieb | Welche Identität (Nutzer, Workload, beides) muss der Server für Aufrufe der Ops-Agenten kennen? | Q2, Q3 |
| 2 | 1 zustandslos statt Handshake | hoch | Zeithorizont: aktuelle Revision; ältere Tutorials (SDK 1.x, `initialize`-Handshake) passen nicht mehr | Welche Clients im Haus sprechen noch die Handshake-Revisionen und müssen unterstützt werden? | Q1 |
| 3 | 7 Sicherheitsleitfäden | hoch | Betroffenheit: Tool-Definitionen als nicht vertrauenswürdige Eingabe, Token Passthrough; deckt sich mit Probe 2 aus Lab 7.2, die das Projekt nicht abdeckt | Wie prüft und fixiert der Client Tool-Definitionen fremder Server? | Q4, Q5 |
| 4 | 4 HTTP-nativer Transport, Caching | mittel | Aufwand: `ttlMs` und `cacheScope` sind schon in den Antworten, der Rest ist Roadmap | Welche Listen-Antworten dürfen Zwischenstationen cachen (`cacheScope`)? | Q1, Q2 |
| 5 | 6 Observability | mittel | Das eigene JSONL-Protokoll genügt für den Prototyp; ein Trace-Kontext lohnt bei mehreren Diensten | Unterstützen die eingesetzten SDKs und Clients `traceparent` in `_meta`? | Q1 |
| 6 | 3 Tasks (Extension) | mittel | Betrifft lang laufende Arbeiten wie Deployments; im Projekt nicht benötigt | Gibt es Tool-Aufrufe, die länger als ein Request-Zyklus dauern? | Q1, Q2 |
| 7 | 8 SDK-Reife, Deprecation-Regeln | gering | `mcp==2.3.0` ist gepinnt; Regeln geben Planungssicherheit | Wie oft wird die SDK-Version geprüft und wer entscheidet über Updates? | Q6, Q7 |
| 8 | 2 Rückfragen per Multi Round-Trip | gering | Die Bestätigung läuft heute über `confirmed`; eine Umstellung auf das Protokoll ist ein späterer Schritt | Kann die Bestätigung durch eine protokollseitige Rückfrage unabhängig vom Client erzwungen werden? | Q1 |

Kennzeichnung (Nummern der Trends aus der Theorie): Aktueller Stand sind 1, 2, 6, 7, 8, die Extension aus 3 und `ttlMs`/`cacheScope` aus 4 (Q1, Q4–Q7). Roadmap-Richtung, keine Zusage, sind die Vorhaben aus 5 (DPoP, Workload-Identität), die Aufnahme von Tasks in den Kern (3) sowie ETag-Caching und HTTP über stdio (4) (Q2).

## Aufgabe 4: Was noch fehlt

| Trend | Fehlende Information |
| --- | --- |
| Agent-Identität | Wann Spezifikationstexte zu DPoP und Workload-Identität vorliegen: Die Arbeitsgruppe bildet sich laut Roadmap erst; ein Zeitpunkt ist nicht genannt |
| zustandslos | Wie die eingesetzten Clients im Haus mit der neuen Revision umgehen: Das ist pro Client zu testen |
| Sicherheitsleitfäden | Ob der vorgesehene Client Tool-Definitionen festhält und bei Änderung fragt: Das Protokoll schreibt es nicht vor (Q5) |

## Erweiterung

Beispiel für Trend 6 (Observability): Abgerufen am 27.10.2026 von https://modelcontextprotocol.io/specification/2026-07-28/changelog, Abschnitt Minor changes: „Document OpenTelemetry trace context propagation conventions for `_meta` keys (`traceparent`, `tracestate`, `baggage`)“. Seitenstand: Revision 2026-07-28 (Current laut Seite „Versioning“). Die Tabelle stimmt: Die Revision beschreibt die Konventionen; welche SDKs sie umsetzen, belegt die Quelle nicht, und die Folgefrage bleibt offen.
