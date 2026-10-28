# Überblick: Model Context Protocol (MCP) in Agentic AI

## Die Entwicklung von KI-Agenten

- Ein LLM (großes Sprachmodell wie GPT oder `qwen3`) erzeugt nur Text; es liest keine Tickets und ändert keine Daten
- **Function Calling**: Das LLM antwortet statt mit Text mit einem Funktionsaufruf, z. B. `get_ticket(ticket_id="VAN-102")`
  - Die Anwendung führt die Funktion aus und gibt das Ergebnis an das LLM zurück
  - Eine so angebotene Funktion heißt **Tool**
  - **Agent**: Anwendung, in der ein LLM in einer Schleife Tools vorschlägt und die Anwendung sie ausführt, bis eine Textantwort steht
- Agenten lesen damit Tickets, prüfen Deployments, ändern Status
- Problem: Jede Anwendung beschreibt und bindet ihre Tools selbst an, in ihrem eigenen Format
- Neue Fragen für den Betrieb: Kontext, mehrere Agenten gleichzeitig, Rechte, Angriffe über manipulierte Daten, Monitoring

## Was ist MCP?

- MCP (Model Context Protocol): offener Standard, über den KI-Anwendungen Tools und Daten anbinden
- Ein Tool wird einmal als **MCP-Server** gebaut und ist dann von jeder MCP-fähigen Anwendung nutzbar
- Drei Rollen:
  - **Host**: Anwendung, die die Verbindungen zu den Servern hält und entscheidet, welcher Aufruf passiert (im Agenten schlägt das LLM vor, im Inspector oder Skript-Client entscheidet die Person)
  - **Client**: die Verbindung des Hosts zu genau einem Server; fertig im SDK (Python-Paket `mcp`) enthalten
  - **Server**: Programm, das Tools anbietet, z. B. „Ticket lesen“
- Function Calling bleibt: Das LLM wählt weiterhin per Function Calling ein Tool, MCP regelt, woher die Tools kommen und wie sie ausgeführt werden

## Warum MCP?

| | Ohne MCP | Mit MCP |
| --- | --- | --- |
| Anbindung | M Anwendungen × N Systeme = M·N eigene Adapter | statt M·N eigener Adapter: N Server plus ein generischer MCP-Client (SDK) je Anwendung |
| Neues Tool | in jeder Anwendung nachziehen | einmal im Server ergänzen, Anwendungen finden es selbst |
| Anbieter | an das Format eines Modellanbieters gebunden | offener Standard, Anwendung und Modell austauschbar |
| Betrieb | Tool-Code steckt in der Anwendung | Server läuft als eigener Dienst mit eigenen Rechten |

Details und Ablauf eines Tool-Aufrufs als Diagramm: [Lab 1.1](../m01-mcp-foundations-and-setup/l01-architecture-thx.md).

## Kursziel und Ergebnis

- Ergebnis: „Vantra Ops Agent“
  - MCP-Server in Python mit zwei Tools
  - angebunden an einen Agent-Client
  - containerisiert und orchestriert
  - mit Zugriffsrichtlinie abgesichert
  - über ein Tool-Call-Protokoll überwacht
- Tag 1: lauffähiger Agentenprototyp (Module 1–4)
- Tag 2: Container, Security, Monitoring im Mini-Workflow (Module 5–8)

## Inhalte

- MCP-Architektur: Host, Client, Server
- Protokoll: JSON-RPC (einheitliches JSON-Format für Anfragen und Antworten), Tools, Resources
- Zwei eigene Tools mit Kontextverwaltung
- Versionsprüfung bei konkurrierenden Agenten
- Agent-Client anbinden, Prototyp end-to-end testen
- Server containerisieren und orchestrieren (Docker, Compose, Kubernetes)
- Absicherung: Rollen, Bestätigung, Eingabeprüfung, Prompt Injection
- Monitoring: Tool-Calls protokollieren, Alarmregeln, Lücken bis zum Produktivbetrieb

## Zielgruppe

- IT-Architekt:innen
- KI-Entwickler:innen mit Fokus Agentic AI
- DevOps und Cloud Engineers
- Systemintegrator:innen
- IT-Sicherheitsverantwortliche
- Niveau: fortgeschritten
- Herstellerneutral, kein Fokus auf einen einzelnen Stack

## Voraussetzungen

| Bereich | Anforderung |
| --- | --- |
| Kenntnisse | Python lesen und anpassen, Terminal, Docker-Grundlagen (Image, Container), HTTP/JSON |
| Gerät | Python ≥ 3.11, Node.js (`npx`), Docker Desktop, Ollama mit `qwen3:8b`, Code-Editor |
| Zugänge | kein LLM-API-Key nötig; Internet für `pip`, `npx`, `docker pull` |
| Optional | lokaler Kubernetes-Cluster (Modul 6); ohne Cluster wird das Manifest nur validiert |

Prüfung der Umgebung und Fallbacks: [`../00-setup-and-installation.md`](../00-setup-and-installation.md).

## Szenario und Projekt

- Fiktive Firma **Vantra Systems**
- Interne Tools (Ticket-API, Deployment-API, Metriken) über MCP-Server für KI-Agenten zugänglich
- Projekt „Vantra Ops Agent“ mit gemockter Ticket-/Deployment-API

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

- Jedes Lab: Theorie (`-thx.md`, im Modulordner) → Übung (`-exc.md`) → Lösung (`-sol.md`, beide im Lab-Unterordner)
- Projekt-Labs:
  - Starter in den Playground kopieren
  - Lücken schließen: `TODO(Aufgabe n)` gehört zu Aufgabe n der Übung, `TODO(Erweiterung)` ist optional
  - mit dem Beispiel in `examples/` vergleichen
- Jede Projekt-Übung:
  - **Basisaufgabe**: Pflicht, mit Checkpoint
  - **Erweiterung**: optional, nie Voraussetzung für spätere Labs
  - Modul 5 und 7: Erweiterungen ohne Programmieranteil (Review, Entscheidung) für Sicherheits- und Architekturrollen
- Tests lokal:
  - stdio zuerst
  - MCP Inspector oder Skript-Client als Testclient
  - Ollama als lokales LLM; ohne funktionierendes Modell Replay-LLM (Skript-Agent)
- Ein Spickzettel je Modul (`*-cheatsheet.md`) mit Befehlen und Syntax

## Stack (Stand: 27.10.2026)

| Baustein | Version |
| --- | --- |
| MCP-Python-SDK | `mcp==2.3.0`, fest in `requirements.txt` |
| MCP-Spezifikation | 2026-07-28 |
| Modell lokal | `qwen3:8b` (Fallback `qwen3:4b`) über Ollama |
