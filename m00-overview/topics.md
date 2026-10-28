# Themenübersicht

Pfade der Module: [`../README.md`](../README.md).

| Modul | Titel | Tag | Kernthemen |
| --- | --- | --- | --- |
| 1 | MCP-Grundlagen und erster eigener Server | 1 | Lab 1.1 Function Calling, Agent, Ablauf eines Tool-Aufrufs, M × N-Problem, Host/Client/Server · Lab 1.2 venv, minimaler `MCPServer`, stdio vs. Streamable HTTP, `server/discover`, MCP Inspector · Lab 1.3 Rollen im eigenen Setup, Vertrauensgrenzen |
| 2 | Protokoll und erstes eigenes Tool | 1 | Lab 2.1 JSON-RPC (Request, Response, Notification) am eigenen Server, Hülle `_meta` ohne Handshake, Fehlercodes `-32601`/`-32602`, Live-Trace · Lab 2.2 Tools, Resources, Prompts, `get_ticket` mit Schema, automatische Argumentprüfung, `tools/call` als Rohnachricht · Lab 2.3 Tool-Fehler vs. Protokollfehler, `ToolError`, Retry |
| 3 | Kontextmanagement und zweites Tool | 1 | Lab 3.1 Kontextfenster, Session-State, Memory · Lab 3.2 Kontextschema, `get_deployment_log`, Kontext als Resource · Lab 3.3 stilles Überschreiben, `expected_version`, Sperre, Zusammenführen |
| 4 | Agent-Client anbinden und testen | 1 | Lab 4.1 Tools entdecken, Tool-Schleife, OpenAI-kompatibles Backend, Replay-LLM · Lab 4.2 Testprotokoll, Skript-Agent kennzeichnen · Lab 4.3 Risiken und Lücken, Bewertungsraster |
| 5 | Cloud- und Microservice-Integration | 2 | Lab 5.1 Sidecar, zentraler Service, Edge, Service Discovery, Versionierung · Lab 5.2 Umgebungsvariablen, `/health`, Dockerfile, Secrets |
| 6 | Containerisierung und Orchestrierung | 2 | Lab 6.1 `docker build`/`run`, Compose, Healthcheck, Absturzerkennung · Lab 6.2 ConfigMap, Secret, Deployment, Service, Probes, `kubeconform`, CI/CD-Stufen, Rollback |
| 7 | Security und Absicherung | 2 | Lab 7.1 Rollen, Least Privilege, deny by default, Bestätigung, Sandbox, Authentifizierung in MCP · Lab 7.2 Prompt Injection, Tool-Spoofing, vier Verteidigungslinien, Showcase C · Lab 7.3 Checkliste, Schweregrade, Befund-Format |
| 8 | Monitoring, Abschlussintegration und Ausblick | 2 | Lab 8.1 Tool-Call-Protokoll (JSONL), Alarmregeln, Datenschutz im Log, Dashboard · Lab 8.2 Mini-Workflow Ticket → Log → Policy-Entscheidung, Lücken bis Produktivbetrieb · Lab 8.3 Trends mit Quellen (Stand: 27.10.2026) |

## Dateien je Modul

| Datei | Inhalt |
| --- | --- |
| `lNN-…-thx.md` | Theorie mit Leitfragen und Fazit, liegt im Modulordner |
| `lNN-…/lNN-…-exc.md` | Übung mit Checkpoint und Abschlusskriterien, liegt im Lab-Unterordner |
| `lNN-…/lNN-…-sol.md` | Lösung mit erwarteter Ausgabe, liegt im Lab-Unterordner |
| `*-cheatsheet.md` | Befehle und Syntax des Moduls |
