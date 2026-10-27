# Handouts: Model Context Protocol (MCP) in Agentic AI

Teilnehmerunterlagen des 2-Tage-Kurses. Pro Lab gibt es Theorie (`-thx.md`), Übung (`-exc.md`) und Lösung (`-sol.md`), pro Modul einen Spickzettel. Alle Pfade relativ zu diesem Ordner.

## Einstieg

| Datei | Inhalt |
| --- | --- |
| [`00-setup-and-installation.md`](00-setup-and-installation.md) | Schulungs-PC prüfen: Python, Node, Docker, Ollama, venv, Fallbacks |
| [`m00-overview/overview.md`](m00-overview/overview.md) | Ziel, Zielgruppe, Szenario, Tagesablauf, Arbeitsmethode |
| [`m00-overview/topics.md`](m00-overview/topics.md) | Module und Kernthemen |
| [`m00-overview/glossary.md`](m00-overview/glossary.md) | Begriffe mit Fundstelle |
| [`m00-overview/best-practices.md`](m00-overview/best-practices.md) | Regeln aus allen Modulen |
| [`m00-overview/faq.md`](m00-overview/faq.md) | Häufige Fragen und Probleme |
| [`project/README.md`](project/README.md) | Projekt „Vantra Ops Agent“: Start, Befehle, Tabelle Lab → Beispiel → Starter |

## Tag 1

| Modul | Ordner | Spickzettel | Labs |
| --- | --- | --- | --- |
| 1 MCP-Grundlagen und erster eigener Server | [`m01-mcp-foundations-and-setup/`](m01-mcp-foundations-and-setup/) | [`mcp-basics-cheatsheet.md`](m01-mcp-foundations-and-setup/mcp-basics-cheatsheet.md) | `l01-motivation-and-architecture`, `l02-dev-setup-first-server`, `l03-architecture-mapping` |
| 2 Protokoll und erstes eigenes Tool | [`m02-protocol-and-messages/`](m02-protocol-and-messages/) | [`protocol-cheatsheet.md`](m02-protocol-and-messages/protocol-cheatsheet.md) | `l01-jsonrpc-live`, `l02-first-tool`, `l03-error-patterns` |
| 3 Kontextmanagement und zweites Tool | [`m03-context-and-state/`](m03-context-and-state/) | [`context-cheatsheet.md`](m03-context-and-state/context-cheatsheet.md) | `l01-state-vs-memory`, `l02-context-schema-implementation`, `l03-multi-agent-sync` |
| 4 Agent-Client anbinden und testen | [`m04-agent-prototype/`](m04-agent-prototype/) | [`agent-cheatsheet.md`](m04-agent-prototype/agent-cheatsheet.md) | `l01-agent-client-connection`, `l02-end-to-end-testrun`, `l03-debrief` |

## Tag 2

| Modul | Ordner | Spickzettel | Labs |
| --- | --- | --- | --- |
| 5 Cloud- und Microservice-Integration | [`m05-cloud-integration/`](m05-cloud-integration/) | [`integration-cheatsheet.md`](m05-cloud-integration/integration-cheatsheet.md) | `l01-integration-patterns`, `l02-container-prep` |
| 6 Containerisierung und Orchestrierung | [`m06-containerization-cicd/`](m06-containerization-cicd/) | [`container-cheatsheet.md`](m06-containerization-cicd/container-cheatsheet.md) | `l01-build-and-run`, `l02-orchestration-cicd` |
| 7 Security und Absicherung | [`m07-security-hardening/`](m07-security-hardening/) | [`security-cheatsheet.md`](m07-security-hardening/security-cheatsheet.md) | `l01-access-control-sandboxing`, `l02-manipulation-defense`, `l03-security-review` |
| 8 Monitoring, Abschlussintegration und Ausblick | [`m08-observability-and-capstone/`](m08-observability-and-capstone/) | [`observability-cheatsheet.md`](m08-observability-and-capstone/observability-cheatsheet.md) | `l01-monitoring-setup`, `l02-capstone-integration`, `l03-trends-outlook` |

Labfolder-Schema: `m<NN>-<modul>/l<NN>-<lab>/l<NN>-<lab>-thx.md` (Theorie), `-exc.md` (Übung), `-sol.md` (Lösung). Beispiel: [`l02-first-tool-thx.md`](m02-protocol-and-messages/l02-first-tool/l02-first-tool-thx.md).

## Projektdateien

Alle Projektdateien liegen in [`project/`](project/), gegliedert in `examples/` (fertiger Stand je Lab), `starters/` (Startdatei je Übung), `playground/` (Arbeitsbereich), `shared/` (Mock-API, Clients, Dashboard, Policy-Vorlage, Angriffsproben) und `checkpoints/` (Wiederaufsetzpunkte). Die Zuordnung je Lab steht in [`project/README.md`](project/README.md#lab--beispiel--starter).
