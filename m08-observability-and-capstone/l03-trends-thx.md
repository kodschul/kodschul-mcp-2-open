# Lab 8.3: Trends und Ausblick

**Stand: 27.10.2026.** Dieses Lab beschreibt Entwicklungen, die sich ändern. Jede Aussage nennt ihre Quelle; Abrufdatum aller Quellen: 27.10.2026.

**Leitfragen:**

<details>
<summary>Welche Schwachstelle des Kursprojekts sollte ein künftiger Standard als Erstes lösen?</summary>

Die Identität: Die Rolle gilt je Server-Prozess, nicht je Client. Genau dort setzt die Roadmap-Priorität „Agent Identity“ an. Setzen sich die Vorhaben durch, ist an dieser Stelle die erste Architekturentscheidung fällig.

</details>

<details>
<summary>Wie verlässlich sind Aussagen über künftige Versionen eines Standards?</summary>

Wenig verlässlich bei allem, was nur in der Roadmap steht: Sie beschreibt nach eigener Aussage „current thinking rather than firm commitments“ (Denkrichtung, keine Zusage). Verlässlich ist nur der Text einer veröffentlichten Revision. Offen sind auch Reifegrad und Zeitpunkt von Extensions, Arbeitsgruppen, die sich erst bilden, und das Verhalten künftiger SDK-Versionen.

</details>

- Die Spezifikation 2026-07-28 ist die aktuelle Revision; ältere Tutorials (SDK 1.x, `initialize`-Handshake) passen nicht mehr.
- Trends sind Hypothesen über Richtung und Tempo, keine Zusagen. Für Entscheidungen zählen Spezifikationstext und SDK-Dokumentation.

Stand der Quellen: Revision 2026-07-28 ist laut Seite „Versioning“ die aktuelle Revision, die Roadmap trägt „Last updated“ 2026-08-22, das Python-SDK steht auf PyPI bei 2.3.0.

## Trends im MCP-Umfeld

| # | Trend | In einem Satz | Beobachtung (Quelle) | Berührt im Projekt |
| --- | --- | --- | --- | --- |
| 1 | zustandslos statt Handshake | Server und Client müssen sich nicht mehr erst begrüßen; jede Anfrage bringt alles Nötige selbst mit. | Revision 2026-07-28 entfernt den `initialize`-Handshake und protokollweite Sessions; jede Anfrage trägt Version und Fähigkeiten in `_meta`; `server/discover` ist Pflicht [Q1] | Der SDK-Client im Projekt sendet `server/discover` als erste Nachricht; Antworten tragen `serverInfo` in `_meta`; Kontext je Serverprozess |
| 2 | Rückfragen per Multi Round-Trip | Will der Server zwischendurch etwas vom Client wissen, läuft das künftig als Folge einzelner Anfragen statt als eigene Gegenrichtung. | Server-initiierte Anfragen (`roots/list`, `sampling/createMessage`, `elicitation/create`) werden durch Multi Round-Trip Requests ersetzt [Q1] | Bestätigung im Projekt über `confirmed`, nicht über das Protokoll |
| 3 | lang laufende Arbeit: Tasks | Lange Arbeiten (z. B. ein Deployment) laufen als „Auftrag“, dessen Stand sich später abfragen lässt. | Tasks wandern als offizielle Extension aus dem Kern [Q1]; die Roadmap strebt eine spätere Aufnahme in den Kern an [Q2] | nicht genutzt |
| 4 | HTTP-nativer Transport, Caching | HTTP wird zum gemeinsamen Transport; Antworten sagen, wie lange sie zwischengespeichert werden dürfen. | Roadmap: Streamable HTTP als einheitliche Bindung (auch über stdio), Erweiterung des Caching [Q2]; `ttlMs` und `cacheScope` sind in Revision 2026-07-28 Pflicht bei Listen-Ergebnissen [Q1] | Antworten tragen `ttlMs: 0` und `cacheScope: "private"` |
| 5 | Agent-Identität und Enterprise-Security | Jeder Agent soll sich künftig selbst ausweisen können, statt eine gemeinsame Rolle zu teilen. | Roadmap-Priorität 3: DPoP, Workload Identity Federation, Identity Assertion JWT Authorization Grant, Token Exchange (RFC 8693) [Q2]; Autorisierung ist optional und OAuth-2.1-basiert, Dynamic Client Registration gilt als deprecated [Q3] | Rolle je Prozess; keine Authentifizierung je Client |
| 6 | Observability | Ein Aufruf kann über mehrere Dienste hinweg verfolgt werden, weil eine gemeinsame Kennung mitreist. | Revision 2026-07-28 dokumentiert OpenTelemetry-Trace-Kontext in `_meta` (`traceparent`, `tracestate`, `baggage`) [Q1] | eigenes JSONL-Protokoll (Lab 8.1) |
| 7 | Sicherheitsleitfäden | Offizielle Leitfäden beschreiben typische Angriffe und Gegenmaßnahmen für MCP-Server und -Clients. | Dokumentation zu Confused Deputy, Token Passthrough, Scope Minimization [Q4] und zu lokalen Servern (Isolation, Tool-Definitionen als nicht vertrauenswürdige Eingabe) [Q5] | Policy, Sandbox-Prinzipien, Angriffsproben (Modul 7) |
| 8 | SDK-Reife und Deprecation-Regeln | Das Python-SDK gilt als ausgereift; veraltete Funktionen verschwinden nicht über Nacht. | Python-SDK ist als Tier 1 geführt [Q6]; veraltete Features bleiben mindestens zwölf Monate (in Ausnahmefällen mindestens 90 Tage) erhalten, bevor sie entfernt werden dürfen [Q7] | `mcp==2.3.0` fest gepinnt |

Roadmap-Prioritäten (Stand der Seite: 2026-08-22) im Überblick: 1 Agentic Messaging Primitives, 2 HTTP-native Transport Unification and Hardening, 3 Agent Identity and Enterprise-Ready Security, 4 Improved Primitives (u. a. Form von Tool-Ergebnissen, schrittweises Entdecken), 5 Improved SDK Developer Experience [Q2].

## Fachbegriffe

Die Beobachtungen nennen Begriffe aus Spezifikation und Roadmap. Für die Bewertung genügt die Spalte „In einem Satz“; die Tabelle dient zum Nachschlagen.

| Begriff | Bedeutung in einem Satz |
| --- | --- |
| Spezifikation, Revision | Verbindlicher Text des Protokolls; jede Revision trägt ein Datum, hier 2026-07-28. |
| Roadmap | Absichtserklärung der Projektverantwortlichen, keine Zusage. |
| Extension | Optionale Erweiterung außerhalb des Protokollkerns, die nicht jede Implementierung unterstützen muss. |
| `initialize`-Handshake | Begrüßungsnachricht älterer Revisionen, bevor andere Anfragen erlaubt waren. |
| Multi Round-Trip Request | Anfrage, die über mehrere Hin-und-Rück-Schritte zwischen Client und Server läuft. |
| `roots/list`, `sampling/createMessage`, `elicitation/create` | Bisherige Anfragen vom Server an den Client: Arbeitsordner erfragen, das Modell des Clients nutzen, den Nutzer etwas fragen. |
| Tasks | Protokollmuster für lang laufende Arbeiten mit späterem Abruf des Ergebnisses. |
| Caching, `ttlMs`, `cacheScope` | Zwischenspeichern von Antworten; `ttlMs` ist die Gültigkeitsdauer, `cacheScope` sagt, wer die Antwort speichern darf. |
| ETag | Kennung einer Antwortversion, mit der ein Client nachfragt, ob sich etwas geändert hat. |
| OAuth 2.1 | Verbreiteter Standard, mit dem ein Client bei einer Anmeldestelle ein Token holt (Lab 7.1). |
| Dynamic Client Registration | Verfahren, bei dem sich ein Client selbst bei der Anmeldestelle registriert; laut Spezifikation veraltet (deprecated). |
| DPoP | Bindet ein Token an einen Schlüssel des Clients, damit ein gestohlenes Token allein nicht genügt. |
| Workload Identity Federation | Ein Dienst weist sich mit der Identität seiner Plattform (z. B. Kubernetes) aus statt mit einem gespeicherten Geheimnis. |
| Identity Assertion JWT Authorization Grant | Verfahren, bei dem eine bestehende Firmenanmeldung in ein Token für einen anderen Dienst umgetauscht wird. |
| Token Exchange (RFC 8693) | Standard zum Tauschen eines Tokens gegen ein anderes mit passenderen Rechten. |
| Confused Deputy | Ein Dienst mit vielen Rechten wird von einem Aufrufer mit wenigen Rechten dazu gebracht, in dessen Auftrag etwas zu tun, das der Aufrufer selbst nicht dürfte (Beispiel: Ein MCP-Server mit Admin-Token schließt ein Ticket, weil ein beliebiger Client darum bittet). |
| Token Passthrough | Ein Server akzeptiert ein Token, das nicht für ihn ausgestellt ist, und reicht es weiter (Lab 7.1). |
| Scope Minimization | Ein Token enthält nur die Rechte, die für die Aufgabe nötig sind: Least Privilege für Tokens. |
| OpenTelemetry, `traceparent` | Offener Standard für Traces; `traceparent` ist die Kennung, die mit jedem Aufruf weitergereicht wird. |
| Tier 1 (SDK) | Höchste Reifestufe eines SDK in der Einstufung des MCP-Projekts. |
| Deprecation | Ankündigung, dass eine Funktion veraltet ist und später entfernt wird. |

## Quellen

| Kürzel | Seite | URL |
| --- | --- | --- |
| Q1 | Spezifikation 2026-07-28, Key Changes | https://modelcontextprotocol.io/specification/2026-07-28/changelog |
| Q2 | Roadmap | https://modelcontextprotocol.io/development/roadmap |
| Q3 | Spezifikation 2026-07-28, Authorization | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization |
| Q4 | Security Best Practices | https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices |
| Q5 | Local Server Security | https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/local-server-security |
| Q6 | SDKs | https://modelcontextprotocol.io/docs/2026-07-28/sdk |
| Q7 | Versioning | https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning |

Alle sieben Seiten wurden am 27.10.2026 abgerufen. Die Versionsnummer des Python-SDK (2.3.0) stammt von PyPI, abgerufen am 27.10.2026.

## Trends bewerten

Ein Trend wird nach Relevanz für die eigene Organisation sortiert, mit einer Folgefrage, die sich prüfen lässt.

| Kriterium | Frage |
| --- | --- |
| Betroffenheit | Berührt der Trend eine bestehende oder geplante Architekturentscheidung? |
| Zeithorizont | Ist er in der aktuellen Revision enthalten (Q1) oder nur Roadmap (Q2)? |
| Aufwand | Was kostet die Umstellung, wenn er eintritt? |
| Unsicherheit | Welche Aussage fehlt noch, um zu entscheiden? |

Beispiel einer Folgefrage zu Trend 5: „Welche Identität (Nutzer, Workload, beides) muss der MCP-Server für die Aufrufe der Ops-Agenten kennen?“

## Fazit

- Revision 2026-07-28 ist die verbindliche Grundlage; Roadmap-Punkte sind Richtung, keine Zusage.
- Identität je Agent, Tasks, HTTP-Transport und Observability sind die Themen mit dem engsten Bezug zum Projekt.
- Jede Trend-Aussage braucht Quelle und Datum und wird vor jedem Kurs erneut geprüft.

Die Übung wählt die drei relevantesten Trends aus und formuliert je eine Folgefrage.
