# Kurs-Projekt: Vantra Ops Agent (MCP)

Ein Python-Projekt mit dem MCP-Server und Agent-Client des Kurses, den fertigen Ständen je Lab (`examples/`), den Starter-Dateien der Übungen (`starters/`), einem Playground als Arbeitsbereich und gemeinsamen Hilfsmitteln (`shared/`). Handouts und Aufgaben liegen eine Ebene höher: [`../README.md`](../README.md).

## Start

Voraussetzung: Python ≥ 3.11 (verifiziert mit 3.13), für den MCP Inspector Node.js mit `npx`, für Modul 6 Docker. Alle Befehle sind Bash-Befehle (Windows: Git Bash) und laufen im Projektordner (`output/project`). Einrichtung Schritt für Schritt: [`../00-setup-and-installation.md`](../00-setup-and-installation.md).

```bash
python -m venv .venv
source .venv/bin/activate            # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env                 # LLM-Backend und Ports, siehe Abschnitt .env
pytest -q                            # alle Tests, kein LLM nötig
```

Erster Server (Lab 1.2):

```bash
cp starters/m01-l02-first-server.py playground/server.py    # Lücken laut TODO schließen
python shared/script_client.py --server playground/server.py
npx @modelcontextprotocol/inspector python playground/server.py
```

## Stack

| Bereich | Paket (Version laut `requirements.txt`) |
| --- | --- |
| MCP-SDK | `mcp==2.3.0` (Spezifikation 2026-07-28; Importe `from mcp.server import MCPServer`, `from mcp import Client`) |
| LLM-Client | `openai==3.40.0` (nur als Client für jede OpenAI-kompatible Schnittstelle, auch Ollama) |
| Tests | `pytest==9.1.1`, `pytest-asyncio==1.4.1`, `PyYAML==6.0.3` |
| Server im Container | nur `mcp==2.3.0` (`requirements-server.txt`) |

Das SDK 2.x unterscheidet sich von Tutorials zu 1.x: kein `FastMCP`-Import, kein `initialize`-Handshake, Streamable HTTP statt HTTP+SSE. Als Vorlage dienen nur die Beispiele dieses Projekts.

## Befehle

| Befehl | Wirkung |
| --- | --- |
| `python playground/server.py` | Server über stdio starten (wartet auf einen Client auf stdin) |
| `python shared/script_client.py --server playground/server.py [--call TOOL '{"arg": 1}']` | Skript-Client ohne LLM: Tools auflisten, Tool aufrufen |
| `npx @modelcontextprotocol/inspector python playground/server.py` | MCP Inspector (Standard-Testclient) |
| `python shared/agent_client.py --server playground/server.py` | Agent mit echtem LLM laut `.env` (interaktiv) |
| `python shared/agent_client.py --server playground/server.py --replay` | Agent mit Replay-LLM (Skript-Agent, kein Modell) |
| `python shared/mock_api/app.py` | Mock-API auf Port 8001 |
| `python shared/trace_proxy.py -- python playground/server.py` | Logging-Proxy (Showcase A), siehe unten |
| `pytest -q` | alle Tests |

Optionen des Agent-Clients: `--url http://localhost:8000/mcp` (Streamable HTTP statt stdio), `--replay [dialog\|injection\|workflow]`, `--prompt "..."` (mehrfach), `--confirm ask\|yes\|no\|none` (Bestätigung schreibender Tools), `--role viewer\|operator` (Rolle des lokalen Servers, ab Lab 7.1), `--trace [DATEI]` (JSON-RPC-Trace über den Logging-Proxy).

## MCP Inspector

```bash
npx @modelcontextprotocol/inspector python playground/server.py
```

Der Inspector startet den Server als Kindprozess (Transport stdio), öffnet eine Weboberfläche und zeigt Tools, Resources und die JSON-RPC-Nachrichten. Ohne Browser geht dasselbe auf der Kommandozeile (verifiziert mit Inspector 2.12.0):

```bash
npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/list
npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/call --tool-name get_ticket --tool-arg ticket_id=VAN-102
```

Gegen einen laufenden HTTP-Server (Modul 6): Transport „Streamable HTTP“ und URL `http://localhost:8000/mcp` wählen.

## Ordnerstruktur

```text
project/
├── README.md, requirements.txt, requirements-server.txt, .env.example, pytest.ini
├── shared/
│   ├── mock_api/             tickets.json, deployments.json, store.py, client.py, app.py (Port 8001)
│   ├── agent_client.py       vorbereiteter Agent-Client (stdio oder URL, OpenAI-kompatibel, --replay)
│   ├── replay_llm.py         Replay-LLM: Skripte dialog, injection, workflow
│   ├── script_client.py      Skript-Client ohne LLM
│   ├── trace_proxy.py        Logging-Proxy für den Live-Trace (Showcase A)
│   ├── second_client.py      zweiter Client für die Multi-Agent-Übung (Lab 3.3)
│   ├── dashboard/            Mini-Dashboard der Tool-Calls (Port 8080, Showcase D)
│   ├── policy-template.md    Vorlage Zugriffsrichtlinie (Lab 7.1)
│   └── attack-samples/       manipulierte Tool-Ergebnisse (Lab 7.2)
├── examples/<mNN-…>/<lNN-…>/ fertiger Stand je Lab, jeder Stand ist ohne Vorläufer lauffähig
├── starters/                 unvollständige Startdateien (mNN-lNN-<name>), Lücken als TODO(Aufgabe n)
├── playground/               einziger Arbeitsbereich (Inhalt wird nicht versioniert)
├── checkpoints/              ende-tag1-prototyp/, ende-m07-abgesichert/
└── tests/                    pytest-Suite (Skript-Client, kein LLM)
```

| Ordner | Regel |
| --- | --- |
| `examples/` | Jeder Stand enthält alle Dateien, die er braucht (z. B. `context.py` neben `server.py`), und baut auf dem vorigen auf |
| `starters/` | Starter nach `playground/` kopieren (Zielname steht im Kopf der Datei); Lücken sind mit `TODO(Aufgabe n)` markiert; `n` ist die Aufgabennummer im `-exc.md`, optionale Teile tragen `TODO(Erweiterung)`. Starter laufen bis zur Lücke oder brechen mit einer klaren Meldung ab |
| `playground/` | Arbeitsbereich von Trainer und Teilnehmenden; `server.py` und Hilfsdateien liegen hier |
| `shared/` | gemeinsame Hilfsmittel; die Server importieren `shared/mock_api` (Pfad wird beim Start automatisch ergänzt) |

## Lab → Beispiel → Starter

Pfade relativ zu `output/project/`. `–` bedeutet: kein Projektcode (nur Handout).

| Lab | Beispiel (`examples/…`) | Starter (`starters/…`) | Ergebnis |
| --- | ----------------------- | ---------------------- | -------- |
| 1.1 | – | – | Vergleichstabelle (Handout) |
| 1.2 | `m01-mcp-foundations-and-setup/l02-dev-setup/server.py` | `m01-l02-first-server.py` | leerer MCP-Server läuft, Client verbunden |
| 1.3 | – | – | Architekturdiagramm des eigenen Setups (Handout) |
| 2.1 | `m02-protocol-and-messages/l01-jsonrpc/` (`raw_requests.py`) | `m02-l01-raw-requests.py` | protokollierter Request/Response am eigenen, leeren Server |
| 2.2 | `m02-protocol-and-messages/l02-first-tool/server.py` | `m02-l02-first-tool.py` | Tool „Ticket abfragen“ |
| 2.3 | – (nutzt Beispiel 2.2) | – | dokumentierter Fehlerfall |
| 3.1 | – | – | Entscheidungstabelle State/Memory |
| 3.2 | `m03-context-and-state/l02-context-schema/` (`server.py`, `context.py`) | `m03-l02-context.py` | Kontextschema + Tool „Deployment-Log“ |
| 3.3 | `m03-context-and-state/l03-multi-agent/server.py` | `m03-l03-conflict.py` | Server erkennt Konflikt zweier Clients |
| 4.1 | `m04-agent-prototype/l01-agent-client/` | `m04-l01-agent-client.py` | Agent ruft beide Tools per Sprache auf |
| 4.2 | `m04-agent-prototype/l02-testrun/` (Testdialog, Log) | `m04-l02-testrun.md` | dokumentierter Testlauf |
| 4.3 | – | – | Risikoliste |
| 5.1 | – | – | Platzierungsentscheidung |
| 5.2 | `m05-cloud-integration/l02-container-prep/Dockerfile` | `m05-l02-Dockerfile` | baufähiges Dockerfile |
| 6.1 | `m06-containerization-cicd/l01-docker/` (`docker-compose.yml`) | `m06-l01-compose.yml` | Server im Container, Agent verbunden |
| 6.2 | `m06-containerization-cicd/l02-kubernetes-cicd/` (`k8s.yaml`, `pipeline.yml`) | `m06-l02-k8s.yaml` | validiertes Manifest + Pipeline-Skizze |
| 7.1 | `m07-security-hardening/l01-access-control/` (`policy.md`, `auth.py`) | `m07-l01-policy.md` | Zugriffsrichtlinie, durchgesetzt im Server |
| 7.2 | – (nutzt `shared/attack-samples/`, Showcase C) | – | Tabelle Angriff · Gegenmaßnahme · Verteidigungslinie |
| 7.3 | `m07-security-hardening/l03-security-review/` (Checkliste, Beispielbefunde) | `m07-l03-checklist.md` | Review-Befunde |
| 8.1 | `m08-observability-and-capstone/l01-monitoring/` (`logging_config.py`) | `m08-l01-logging.py` | strukturierte Logs + Beispielalarm |
| 8.2 | `m08-observability-and-capstone/l02-capstone/` (kompletter Stand) | `m08-l02-capstone.md` | End-to-End-Demo des gesicherten Agenten |
| 8.3 | – | – | priorisierte Trendliste (Handout) |

Zusätzliche Dateien gegenüber der Tabelle (jeweils im selben Ordner bzw. in `starters/`): in 2.1 `raw_requests.py` (gegen den leeren Server aus 1.2); in 2.2 `raw_requests.py` (Stand 2.1 plus `tools/call`, Lab 2.2 Aufgabe 6 und Lab 2.3 Aufgabe 5) und `error_cases.py` (Fehlerfälle für Lab 2.3); in 4.1 `agent.py`, `server.py`, `context.py`; in 4.2 `testdialog.md`, `testlauf.log`; in 5.2 zusätzlich `server.py` und `context.py` (Container-Variante mit Umgebungskonfiguration und `/health`); in 7.1 `server.py`, `context.py`; in 7.3 `flawed/Dockerfile`, `flawed/policy.md` (Trainer-Konfiguration mit Fehlern); in 8.1 `server.py` und Kopien der Vorgänger; in 8.2 alle Dateien des Gesamtstands plus `run_demo.py`. Zusätzliche Starter: `m06-l02-pipeline.yml` (Job-Gerüste vorgegeben, Lücken als `TODO(Aufgabe B1)` bis `TODO(Aufgabe B5)`; Policy-Tests in der Pipeline nur als Hinweis „ab Lab 7.1“), `m07-l01-auth.py`.

**Reihenfolge der Projektstände:** 1.2 → 2.2 → 3.2 → 3.3 → 4.1 (Prototyp, Checkpoint Ende Tag 1) → 5.2 → 6.1 → 6.2 → 7.1 (Checkpoint Ende m07) → 8.1 → 8.2.

## Befehle je Stufe

Alle Beispiel-Server laufen über stdio; Pfad des Servers ersetzen durch `playground/server.py` für den eigenen Stand.

| Stufe | Befehl |
| --- | --- |
| 1.2 | `python shared/script_client.py --server examples/m01-mcp-foundations-and-setup/l02-dev-setup/server.py` (Tools: keine) |
| 2.1 | `python examples/m02-protocol-and-messages/l01-jsonrpc/raw_requests.py` (rohe JSON-RPC-Zeilen gegen den leeren Server aus 1.2) |
| 2.2 (roh) | `python examples/m02-protocol-and-messages/l02-first-tool/raw_requests.py` (wie 2.1 plus `tools/call` gegen Server 2.2) |
| 2.2 | `python shared/script_client.py --server examples/m02-protocol-and-messages/l02-first-tool/server.py --call get_ticket '{"ticket_id": "VAN-102"}'` |
| 2.3 | `python examples/m02-protocol-and-messages/l02-first-tool/error_cases.py` |
| 3.2 | `python shared/script_client.py --server examples/m03-context-and-state/l02-context-schema/server.py --call get_deployment_log '{"ticket_id": "VAN-102"}'` |
| 3.3 | siehe „Multi-Agent-Konflikt“ unten |
| 4.1 | `python examples/m04-agent-prototype/l01-agent-client/agent.py --replay` oder `python shared/agent_client.py --server examples/m04-agent-prototype/l01-agent-client/server.py [--replay]` |
| 4.2 | `python shared/agent_client.py --server examples/m04-agent-prototype/l01-agent-client/server.py --replay` (Beispiellog: `testlauf.log`) |
| 5.2 | `docker build -f examples/m05-cloud-integration/l02-container-prep/Dockerfile --build-arg APP_DIR=examples/m05-cloud-integration/l02-container-prep -t vantra-ops-mcp:local .` |
| 6.1 | `APP_DIR=examples/m05-cloud-integration/l02-container-prep docker compose -f examples/m06-containerization-cicd/l01-docker/docker-compose.yml up --build`, dann `python shared/agent_client.py --url http://localhost:8000/mcp --replay` |
| 6.2 | `kubeconform -strict -summary examples/m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml` bzw. `kubectl apply --dry-run=client -f …` (braucht je nach Version einen erreichbaren Cluster) |
| 7.1 | `python shared/script_client.py --server examples/m07-security-hardening/l01-access-control/server.py --role operator --call update_ticket_status '{"ticket_id": "VAN-101", "status": "closed", "expected_version": 1}'` |
| 7.2 | Showcase C, siehe unten |
| 7.3 | `examples/m07-security-hardening/l03-security-review/flawed/` gegen `checklist.md` prüfen |
| 8.1 | `TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/agent_client.py --server examples/m08-observability-and-capstone/l01-monitoring/server.py --replay`, dann `python examples/m08-observability-and-capstone/l01-monitoring/logging_config.py` (Alarmprüfung) und `TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py` |
| 8.2 | `python examples/m08-observability-and-capstone/l02-capstone/run_demo.py` oder Container: `VANTRA_ROLE=operator docker compose -f examples/m08-observability-and-capstone/l02-capstone/docker-compose.yml up --build` |

`APP_DIR` wählt in Dockerfile und Compose den Server-Stand (Standard: `playground`, im 8.2-Beispiel der Ordner des Beispiels). Der Build-Kontext ist immer der Projektordner.

## Multi-Agent-Konflikt (Lab 3.3)

Zwei Agenten brauchen gemeinsamen Zustand. Der kommt von der Mock-API (zwei stdio-Server-Prozesse haben sonst getrennte Daten):

```bash
python shared/mock_api/app.py                                   # Terminal 1
MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-a --hold 10 --status resolved   # Terminal 2
MOCK_API_URL=http://localhost:8001 python shared/second_client.py --server playground/server.py --name agent-b --status in_progress          # Terminal 3, innerhalb der 10 s
```

Mit Versionsprüfung (Beispiel 3.3) endet Agent A mit `version_conflict` (erwartet 3, aktuell 4). Im Starter überschreibt Agent A still.

## Showcases

| Showcase | Befehle |
| --- | --- |
| A Live-Trace (m02-l01) | Agent mit Proxy: `python shared/agent_client.py --server playground/server.py --replay --trace trace.log`; die JSON-RPC-Zeilen erscheinen auf stderr und in `trace.log` (in einem zweiten Terminal `tail -f trace.log`). Ohne Agent: im Inspector Befehl `python`, Argumente `shared/trace_proxy.py -- python playground/server.py` eintragen |
| C Prompt-Injection-Duell (m07-l02) | ohne Policy: `python shared/agent_client.py --server examples/m03-context-and-state/l03-multi-agent/server.py --replay injection --confirm none`; mit Policy: dasselbe mit `examples/m07-security-hardening/l01-access-control/server.py` (Rolle viewer lehnt ab; mit `--role operator` fehlt die Bestätigung) |
| D Ein-Befehl-Betrieb (m06-l01, m08-l01) | `docker compose -f examples/m08-observability-and-capstone/l02-capstone/docker-compose.yml up --build`, Dashboard unter http://localhost:8080 |

## .env

`.env` entsteht aus `.env.example` und wird nicht versioniert. Der Agent-Client liest sie beim Start; bereits gesetzte Umgebungsvariablen haben Vorrang.

| Variable | Bedeutung | Standard |
| --- | --- | --- |
| `LLM_BASE_URL` | OpenAI-kompatible Basis-URL | `http://localhost:11434/v1` (Ollama) |
| `LLM_MODEL` | Modellname | `qwen3:8b` (Fallback `qwen3:4b`) |
| `LLM_API_KEY` | Schlüssel; Ollama ignoriert den Wert | `ollama` |
| `MCP_PORT`, `MOCK_API_PORT`, `DASHBOARD_PORT` | Host-Ports in Docker Compose | `8000`, `8001`, `8080` |
| `VANTRA_ROLE` | Rolle des Servers ab Lab 7.1 | `viewer` |

Wechsel auf einen Cloud-Anbieter nur über `LLM_BASE_URL`, `LLM_MODEL` und `LLM_API_KEY`; der Code bleibt gleich. Der Schlüssel wird nicht an den Server-Prozess weitergegeben. Ohne Modell oder bei Zeitdruck läuft `--replay`; solche Läufe sind in den Labs als Skript-Agent zu kennzeichnen.

## Ports

| Port | Dienst |
| --- | --- |
| 8000 | MCP-Server über Streamable HTTP (Pfad `/mcp`, Health `/health`) |
| 8001 | Mock-API (Tickets, Deployments) |
| 8080 | Dashboard der Tool-Calls |

## Checkpoints

| Ordner | Stand | Wiedereinstieg |
| --- | --- | --- |
| `checkpoints/ende-tag1-prototyp/` | nach Lab 4.1: zwei Tools plus Schreib-Tool mit Versionsprüfung, Kontext, Agent | siehe `README.md` im Ordner |
| `checkpoints/ende-m07-abgesichert/` | nach Lab 7.1: containerfähig, Rollen und Bestätigung, Dockerfile, Compose, Kubernetes, Pipeline (noch ohne Logging) | siehe `README.md` im Ordner |

## Was geprüft ist und was nicht

- `pytest -q`: 90 Tests über alle Beispiele (stdio, Streamable HTTP, Fehlerfälle, Konflikt, Policy, Logging, Dashboard, Agent mit Replay und mit OpenAI-kompatiblem Fake-Backend, Starter, Konsistenz der Stände).
- Dateien: `docker compose config` gültig, `k8s.yaml` mit kubeconform (strict) gültig, `pipeline.yml` mit actionlint ohne Befund.
- Nicht in dieser Umgebung geprüft: `docker build` und `docker compose up` (kein laufender Docker-Daemon), Anwenden auf einen Kubernetes-Cluster, ein echtes Modell (Ollama oder Cloud), die Inspector-Weboberfläche.
