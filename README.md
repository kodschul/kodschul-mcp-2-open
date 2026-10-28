<div align="center">

<img src="assets/kodschul-logo.png" alt="Kodschul" width="220" />

# Model Context Protocol (MCP) in Agentic AI

**2-Tage-Workshop** · Programmierung · Deutsch · Präsenz (onsite)

</div>

---

Teilnehmerunterlagen des Kurses **„Model Context Protocol (MCP) in Agentic AI"**. Teilnehmende bauen über zwei Tage den **Vantra Ops Agent**: einen eigenen MCP-Server mit Kontextverwaltung, angebundenem Agent-Client, Containerisierung und Absicherung.

Jedes Lab besteht aus drei Dateien: Theorie (`-thx.md`), Übung (`-exc.md`) und Lösung (`-sol.md`); jedes Modul hat einen Spickzettel. Alle Pfade in dieser Datei sind relativ zu diesem Ordner. Alle Befehle sind Bash-Befehle (Windows: Git Bash).

## Auf einen Blick

| | |
| --- | --- |
| **Dauer** | 2 Tage, 09:00–16:30 |
| **Format** | Präsenz (onsite), kleine Gruppe (2–3 Teilnehmende) |
| **Zielgruppe** | IT-Architekt:innen, KI-Entwickler:innen (Agentic AI), DevOps, Cloud Engineers, Systemintegrator:innen, IT-Sicherheitsverantwortliche |
| **Niveau** | fortgeschritten |
| **Sprache** | Deutsch |
| **Projekt** | Vantra Ops Agent (Python, MCP-SDK `mcp` 2.3.0) |

Details zu Zielen, Voraussetzungen und Tagesablauf: [`m00-overview/overview.md`](m00-overview/overview.md).

## Einstieg

| Datei | Inhalt |
| --- | --- |
| [`00-setup-and-installation.md`](00-setup-and-installation.md) | Projekt holen, Schulungs-PC prüfen: Git Bash, Python, Node, Docker, Ollama, venv, Fallbacks |
| [`m00-overview/overview.md`](m00-overview/overview.md) | Ziel, Zielgruppe, Szenario, Tagesablauf, Arbeitsmethode |
| [`m00-overview/topics.md`](m00-overview/topics.md) | Module und Kernthemen |
| [`m00-overview/glossary.md`](m00-overview/glossary.md) | Begriffe mit Fundstelle |
| [`m00-overview/best-practices.md`](m00-overview/best-practices.md) | Regeln aus allen Modulen |
| [`m00-overview/faq.md`](m00-overview/faq.md) | Häufige Fragen und Probleme |
| [`project/README.md`](project/README.md) | Projekt „Vantra Ops Agent“: Start, Befehle, Tabelle Lab → Beispiel → Starter |

## Tag 1

| Modul | Ordner | Spickzettel | Labs |
| --- | --- | --- | --- |
| 1 MCP-Grundlagen und erster eigener Server | [`m01-mcp-foundations-and-setup/`](m01-mcp-foundations-and-setup/) | [`mcp-basics-cheatsheet.md`](m01-mcp-foundations-and-setup/mcp-basics-cheatsheet.md) | `l01-architecture`, `l02-dev-setup`, `l03-setup-mapping` |
| 2 Protokoll und erstes eigenes Tool | [`m02-protocol-and-messages/`](m02-protocol-and-messages/) | [`protocol-cheatsheet.md`](m02-protocol-and-messages/protocol-cheatsheet.md) | `l01-jsonrpc`, `l02-first-tool`, `l03-errors` |
| 3 Kontextmanagement und zweites Tool | [`m03-context-and-state/`](m03-context-and-state/) | [`context-cheatsheet.md`](m03-context-and-state/context-cheatsheet.md) | `l01-state-memory`, `l02-context-schema`, `l03-multi-agent` |
| 4 Agent-Client anbinden und testen | [`m04-agent-prototype/`](m04-agent-prototype/) | [`agent-cheatsheet.md`](m04-agent-prototype/agent-cheatsheet.md) | `l01-agent-client`, `l02-testrun`, `l03-debrief` |

## Tag 2

| Modul | Ordner | Spickzettel | Labs |
| --- | --- | --- | --- |
| 5 Cloud- und Microservice-Integration | [`m05-cloud-integration/`](m05-cloud-integration/) | [`integration-cheatsheet.md`](m05-cloud-integration/integration-cheatsheet.md) | `l01-integration`, `l02-container-prep` |
| 6 Containerisierung und Orchestrierung | [`m06-containerization-cicd/`](m06-containerization-cicd/) | [`container-cheatsheet.md`](m06-containerization-cicd/container-cheatsheet.md) | `l01-docker`, `l02-kubernetes-cicd` |
| 7 Security und Absicherung | [`m07-security-hardening/`](m07-security-hardening/) | [`security-cheatsheet.md`](m07-security-hardening/security-cheatsheet.md) | `l01-access-control`, `l02-injection`, `l03-security-review` |
| 8 Monitoring, Abschlussintegration und Ausblick | [`m08-observability-and-capstone/`](m08-observability-and-capstone/) | [`observability-cheatsheet.md`](m08-observability-and-capstone/observability-cheatsheet.md) | `l01-monitoring`, `l02-capstone`, `l03-trends` |

Labfolder-Schema: Theorie liegt flach im Modulordner (`m<NN>-<modul>/l<NN>-<lab>-thx.md`), Übung und Lösung liegen im Lab-Unterordner (`m<NN>-<modul>/l<NN>-<lab>/l<NN>-<lab>-exc.md`, `-sol.md`). Beispiel: [`l02-first-tool-thx.md`](m02-protocol-and-messages/l02-first-tool-thx.md).

## Projektdateien

Alle Projektdateien liegen in [`project/`](project/), gegliedert in `examples/` (fertiger Stand je Lab), `starters/` (Startdatei je Übung), `playground/` (Arbeitsbereich), `shared/` (Mock-API, Clients, Dashboard, Policy-Vorlage, Angriffsproben) und `checkpoints/` (Wiederaufsetzpunkte). Die Zuordnung je Lab steht in [`project/README.md`](project/README.md#lab--beispiel--starter).

---

<div align="center">

<sub>© Nextise GmbH · <a href="https://www.kodschul.com">kodschul.com</a> · Kompetenz aufbauen – von der sicheren KI-Anwendung bis zur modernen IT-Basis</sub>

</div>
