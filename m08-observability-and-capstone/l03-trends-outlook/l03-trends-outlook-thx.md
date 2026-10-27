# Lab 8.3: Trends und Ausblick

**Stand: 27.10.2026.** Dieses Lab beschreibt Entwicklungen, die sich ändern. Jede Aussage nennt ihre Quelle; Abrufdatum aller Quellen: 27.10.2026.

**Leitfragen:**

<details>
<summary>Welcher Trend verändert die heutige Architekturentscheidung am ehesten?</summary>

Das hängt von der Organisation ab. Im Projekt berührt die Roadmap-Priorität „Agent Identity“ die schwächste Stelle: Die Rolle gilt je Server-Prozess, nicht je Client. Setzen sich die dort genannten Vorhaben durch, ist an dieser Stelle die erste Architekturentscheidung fällig.

</details>

<details>
<summary>Wo bleibt bewusst Unsicherheit?</summary>

Bei allem, was die Roadmap als Denkrichtung beschreibt: Die Roadmap nennt „current thinking rather than firm commitments“. Offen sind auch Reifegrad und Zeitpunkt von Extensions, Arbeitsgruppen, die sich erst bilden, und das Verhalten künftiger SDK-Versionen.

</details>

- Die Spezifikation 2026-07-28 ist die aktuelle Revision; ältere Tutorials (SDK 1.x, `initialize`-Handshake) passen nicht mehr.
- Trends sind Hypothesen über Richtung und Tempo, keine Zusagen. Für Entscheidungen zählen Spezifikationstext und SDK-Dokumentation.

> **Vor Kursbeginn prüfen:** (1) Seite „Versioning“: Welche Revision ist „Current“? (2) Seite „Roadmap“: Datum „Last updated“ (hier 2026-08-22) und die fünf Prioritäten. (3) Python-SDK-Version auf PyPI (hier 2.3.0). Abweichungen in der Tabelle unten nachziehen.

## Trends im MCP-Umfeld

| # | Trend | Beobachtung (Quelle) | Berührt im Projekt |
| --- | --- | --- | --- |
| 1 | zustandslos statt Handshake | Revision 2026-07-28 entfernt den `initialize`-Handshake und protokollweite Sessions; jede Anfrage trägt Version und Fähigkeiten in `_meta`; `server/discover` ist Pflicht [Q1] | Der SDK-Client im Projekt sendet `server/discover` als erste Nachricht; Antworten tragen `serverInfo` in `_meta`; Kontext je Serverprozess |
| 2 | Rückfragen per Multi Round-Trip | Server-initiierte Anfragen (`roots/list`, `sampling/createMessage`, `elicitation/create`) werden durch Multi Round-Trip Requests ersetzt [Q1] | Bestätigung im Projekt über `confirmed`, nicht über das Protokoll |
| 3 | lang laufende Arbeit: Tasks | Tasks wandern als offizielle Extension aus dem Kern [Q1]; die Roadmap strebt eine spätere Aufnahme in den Kern an [Q2] | nicht genutzt |
| 4 | HTTP-nativer Transport, Caching | Roadmap: Streamable HTTP als einheitliche Bindung (auch über stdio), Erweiterung des Caching [Q2]; `ttlMs` und `cacheScope` sind in Revision 2026-07-28 Pflicht bei Listen-Ergebnissen [Q1] | Antworten tragen `ttlMs: 0` und `cacheScope: "private"` |
| 5 | Agent-Identität und Enterprise-Security | Roadmap-Priorität 3: DPoP, Workload Identity Federation, Identity Assertion JWT Authorization Grant, Token Exchange (RFC 8693) [Q2]; Autorisierung ist optional und OAuth-2.1-basiert, Dynamic Client Registration gilt als deprecated [Q3] | Rolle je Prozess; keine Authentifizierung je Client |
| 6 | Observability | Revision 2026-07-28 dokumentiert OpenTelemetry-Trace-Kontext in `_meta` (`traceparent`, `tracestate`, `baggage`) [Q1] | eigenes JSONL-Protokoll (Lab 8.1) |
| 7 | Sicherheitsleitfäden | Dokumentation zu Confused Deputy, Token Passthrough, Scope Minimization [Q4] und zu lokalen Servern (Isolation, Tool-Definitionen als nicht vertrauenswürdige Eingabe) [Q5] | Policy, Sandbox-Prinzipien, Angriffsproben (Modul 7) |
| 8 | SDK-Reife und Deprecation-Regeln | Python-SDK ist als Tier 1 geführt [Q6]; veraltete Features bleiben mindestens zwölf Monate (in Ausnahmefällen mindestens 90 Tage) erhalten, bevor sie entfernt werden dürfen [Q7] | `mcp==2.3.0` fest gepinnt |

Roadmap-Prioritäten (Stand der Seite: 2026-08-22) im Überblick: 1 Agentic Messaging Primitives, 2 HTTP-native Transport Unification and Hardening, 3 Agent Identity and Enterprise-Ready Security, 4 Improved Primitives (u. a. Form von Tool-Ergebnissen, schrittweises Entdecken), 5 Improved SDK Developer Experience [Q2].

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

Die Übung ordnet die acht Trends nach Relevanz und formuliert je eine Folgefrage.
