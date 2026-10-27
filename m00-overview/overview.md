# Überblick: Model Context Protocol (MCP) in Agentic AI

Zwei Tage, onsite, kleine Gruppe (2–3 Teilnehmende). Ein Python-Projekt wächst über beide Tage zum „Vantra Ops Agent“: Tag 1 entsteht ein lauffähiger MCP-Agentenprototyp, Tag 2 wird er containerisiert, abgesichert und mit Monitoring in einem Mini-Workflow demonstriert.

## Ziel

- Architektur und Protokoll von MCP (Host, Client, Server, JSON-RPC, Tools, Resources) am eigenen Server nachvollziehen.
- Zwei eigene Tools mit Kontextverwaltung und Versionsprüfung bei konkurrierenden Agenten bauen.
- Einen Agent-Client anbinden und den Prototyp end-to-end testen.
- Den Server für Containerbetrieb vorbereiten, containerisieren, orchestrieren und mit einer Zugriffsrichtlinie absichern.
- Tool-Calls protokollieren, Alarmregeln definieren und offene Lücken bis zum Produktivbetrieb benennen.

## Zielgruppe

IT-Architekt:innen, KI-Entwickler:innen mit Fokus Agentic AI, DevOps, Cloud Engineers, Systemintegrator:innen und IT-Sicherheitsverantwortliche. Niveau: fortgeschritten. Kein Fokus auf einen einzelnen Hersteller-Stack.

## Voraussetzungen

| Bereich | Anforderung |
| --- | --- |
| Kenntnisse | Python lesen und anpassen, Terminal, Grundlagen von Docker (Image, Container) und HTTP/JSON |
| Gerät | Schulungs-PC mit Python ≥ 3.11, Node.js (`npx`), Docker Desktop, Ollama mit `qwen3:8b`, Code-Editor |
| Zugänge | kein LLM-API-Key nötig; Internet für `pip`, `npx`, `docker pull` |
| Optional | lokaler Kubernetes-Cluster (Modul 6); ohne Cluster wird das Manifest nur validiert |

Prüfung der Umgebung und Fallbacks: [`../00-setup-and-installation.md`](../00-setup-and-installation.md).

## Szenario und Projekt

Die fiktive Firma **Vantra Systems** macht interne Tools (Ticket-API, Deployment-API, Metriken) über MCP-Server für KI-Agenten zugänglich. Das Projekt „Vantra Ops Agent“ nutzt eine gemockte Ticket-/Deployment-API.

| Ordner in `project/` | Rolle |
| --- | --- |
| `examples/` | fertiger, lauffähiger Stand je Lab (Vergleich und Wiederaufsetzpunkt) |
| `starters/` | bewusst unvollständige Startdatei je Lab, wird in den Playground kopiert |
| `playground/` | einziger Arbeitsbereich |
| `shared/` | Mock-API, Skript-Client, Agent-Client, Replay-LLM, Dashboard, Policy-Vorlage, Angriffsproben |
| `checkpoints/` | Wiederaufsetzpunkte `ende-tag1-prototyp` und `ende-m07-abgesichert` |

Details und Tabelle Lab → Beispiel → Starter: [`../project/README.md`](../project/README.md).

## Tagesablauf

Zeitraster beider Tage: 09:00–10:30 · Pause bis 10:45 · 10:45–12:15 · Mittagspause bis 13:15 · 13:15–14:45 · Pause bis 15:00 · 15:00–16:30.

### Tag 1: Grundlagen, Protokoll und erster Agentenprototyp

| Zeit | Inhalt |
| --- | --- |
| 09:00–09:15 | Auftakt: Leitmotiv, Projektüberblick „Vantra Ops Agent“ |
| 09:15–10:30 | Modul 1: MCP-Grundlagen und erster eigener Server (Lab 1.1 25 min, Lab 1.2 35 min, Lab 1.3 15 min) |
| 10:30–10:45 | Pause |
| 10:45–12:15 | Modul 2: Protokoll und erstes eigenes Tool (Lab 2.1 30 min, Lab 2.2 40 min, Lab 2.3 20 min) |
| 12:15–13:15 | Mittagspause |
| 13:15–14:45 | Modul 3: Kontextmanagement und zweites Tool (Lab 3.1 20 min, Lab 3.2 50 min, Lab 3.3 20 min) |
| 14:45–15:00 | Pause |
| 15:00–16:15 | Modul 4: Agent-Client anbinden und testen (Lab 4.1 30 min, Lab 4.2 30 min, Lab 4.3 15 min) |
| 16:15–16:30 | Tagesabschluss: Recap der vier Module, Überleitung zu Tag 2 |

### Tag 2: Integration, Security und Betrieb

| Zeit | Inhalt |
| --- | --- |
| 09:00–09:10 | Tagesauftakt: Recap Tag 1 |
| 09:10–10:30 | Modul 5: Cloud- und Microservice-Integration (Lab 5.1 35 min, Lab 5.2 45 min) |
| 10:30–10:45 | Pause |
| 10:45–12:15 | Modul 6: Containerisierung und Orchestrierung (Lab 6.1 40 min, Lab 6.2 50 min) |
| 12:15–13:15 | Mittagspause |
| 13:15–14:45 | Modul 7: Security und Absicherung (Lab 7.1 35 min, Lab 7.2 25 min, Lab 7.3 30 min) |
| 14:45–15:00 | Pause |
| 15:00–16:20 | Modul 8: Monitoring, Abschlussintegration und Ausblick (Lab 8.1 25 min, Lab 8.2 45 min, Lab 8.3 10 min) |
| 16:20–16:30 | Tagesabschluss: Recap beider Tage, offene Punkte, Feedback |

## Arbeitsmethode

- Jedes Lab folgt demselben Ablauf: Theorie (`-thx.md`), Übung (`-exc.md`), Lösung (`-sol.md`).
- Projekt-Labs: Starter in den Playground kopieren, Lücken (`TODO(Aufgabe n)`) schließen, mit dem Beispiel in `examples/` vergleichen.
- Jede Projekt-Übung hat eine **Basisaufgabe** (Pflicht, Checkpoint) und eine **Erweiterung** (optional, nie Voraussetzung für spätere Labs). Für Sicherheits- und Architekturrollen enthalten Modul 5 und 7 Erweiterungen ohne Programmieranteil (Review, Entscheidung).
- Tests laufen lokal: stdio zuerst, MCP Inspector oder Skript-Client als Testclient, Ollama als lokales LLM. Ohne funktionierendes Modell läuft der Agent mit dem Replay-LLM (Skript-Agent).
- Ein Spickzettel je Modul (`*-cheatsheet.md`) fasst Befehle und Syntax zusammen.

## Stack (Stand: 27.10.2026)

| Baustein | Version |
| --- | --- |
| MCP-Python-SDK | `mcp==2.3.0`, fest in `requirements.txt` |
| MCP-Spezifikation | 2026-07-28 |
| Modell lokal | `qwen3:8b` (Fallback `qwen3:4b`) über Ollama |
