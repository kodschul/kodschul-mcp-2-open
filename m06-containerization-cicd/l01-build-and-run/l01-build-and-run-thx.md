# Lab 6.1: Container bauen und starten

**Leitfragen:**

<details>
<summary>Welche Portfreigabe ist für den HTTP-Transport (Streamable HTTP) nötig?</summary>

Der Container-Port 8000 wird auf einen Host-Port veröffentlicht (`-p 8000:8000`, in Compose `ports`). Der Server muss dazu an `0.0.0.0` binden; der Client erreicht ihn unter `http://localhost:8000/mcp`. Ein zweiter Port ist nicht nötig.

</details>

<details>
<summary>Wie wird ein Absturz des Containers erkannt?</summary>

Beendete Prozesse zeigen `docker ps -a` und der Exit-Code (`docker inspect`); Hänger zeigt der Healthcheck als `unhealthy`. Ursachen stehen in `docker logs`; eine Restart-Policy startet beendete Container neu.

</details>

- Ein MCP-Server im Container ist ein HTTP-Dienst: Port veröffentlichen, Server an `0.0.0.0` binden, Client auf `/mcp` zeigen.
- Docker Compose beschreibt mehrere Dienste (Server, Mock-API, Dashboard) in einer Datei und startet sie mit einem Befehl.

## Docker in fünf Befehlen

| Befehl | Wirkung |
| --- | --- |
| `docker build -f <Dockerfile> -t <name>:<tag> .` | Image bauen, `.` ist der Build-Kontext |
| `docker run -d -p 8000:8000 --name vantra-mcp vantra-ops-mcp:local` | Container starten, Host-Port 8000 → Container-Port 8000 |
| `docker ps` / `docker ps -a` | laufende / alle Container samt Status |
| `docker logs vantra-mcp` | stdout und stderr des Containers |
| `docker stop vantra-mcp` und `docker rm vantra-mcp` | stoppen und entfernen |

## Besonderheiten bei MCP-Servern: stdio oder Port

| | stdio | Streamable HTTP |
| --- | --- | --- |
| Wer startet den Server? | der Client als Kindprozess | Container/Orchestrator unabhängig vom Client |
| Verbindung | stdin/stdout des Prozesses | HTTP auf Port 8000, Endpunkt `/mcp` |
| Im Container | nur mit `docker run -i` und Client als Elternprozess, umständlich | Standard: Port veröffentlichen |
| Mehrere Clients | ein Client je Prozess | mehrere Verbindungen zum selben Prozess |
| Logs | stderr (stdout gehört dem Protokoll) | stdout und stderr frei |

- Im Container gilt `MCP_TRANSPORT=streamable-http`; den Rest regelt `server.py` (Lab 5.2).
- `localhost` im Container ist der Container selbst, nicht der Host. Dienste im Compose-Netz erreichen sich über den Dienstnamen (`http://mock-api:8001`).
- Der Kontext (`context://session`) gilt bei HTTP je Serverprozess, nicht je Client.

## Compose-Datei: Server, Mock-API, Dashboard

`examples/m06-containerization-cicd/l01-build-and-run/docker-compose.yml` (gekürzt auf das Wesentliche):

```yaml
name: vantra-ops

x-build: &build                         # gemeinsamer Build für alle Dienste
  context: ../../..                     # Projektordner
  dockerfile: examples/m05-cloud-integration/l02-container-prep/Dockerfile
  args:
    APP_DIR: ${APP_DIR:-playground}     # welcher Server-Stand

services:
  mcp-server:
    build: *build
    image: vantra-ops-mcp:local
    environment:
      MCP_TRANSPORT: streamable-http
      MCP_PORT: "8000"
      MOCK_API_URL: http://mock-api:8001   # Dienstname als Hostname
      TOOL_CALL_LOG: /data/tool_calls.jsonl
      VANTRA_ROLE: ${VANTRA_ROLE:-viewer}
    ports:
      - "${MCP_PORT:-8000}:8000"          # Host:Container
    volumes:
      - toolcalls:/data
    depends_on:
      mock-api:
        condition: service_healthy        # erst starten, wenn die Mock-API antwortet
    restart: unless-stopped

  mock-api:
    build: *build
    image: vantra-ops-mcp:local
    command: ["python", "shared/mock_api/app.py"]
    environment:
      MOCK_API_HOST: 0.0.0.0
      MOCK_API_PORT: "8001"
    ports:
      - "${MOCK_API_PORT:-8001}:8001"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=3)"]
      interval: 10s
      timeout: 4s
      retries: 3
      start_period: 5s

  dashboard:                              # liest dasselbe Volume nur lesend
    build: *build
    image: vantra-ops-mcp:local
    command: ["python", "shared/dashboard/server.py"]
    environment:
      DASHBOARD_HOST: 0.0.0.0
      DASHBOARD_PORT: "8080"
      TOOL_CALL_LOG: /data/tool_calls.jsonl
    ports:
      - "${DASHBOARD_PORT:-8080}:8080"
    volumes:
      - toolcalls:/data:ro

volumes:
  toolcalls:
```

(Gekürzt: das Dashboard hat in der Projektdatei zusätzlich einen Healthcheck.)

| Schlüssel | Bedeutung |
| --- | --- |
| `build.context` | Ordner, aus dem `COPY` liest (hier der Projektordner) |
| `ports: "8000:8000"` | veröffentlicht; `"127.0.0.1:8000:8000"` beschränkt auf den eigenen Rechner |
| `depends_on ... service_healthy` | Startreihenfolge nach Healthcheck, nicht nur nach Containerstart |
| `restart: unless-stopped` | Docker startet beendete Container neu, außer sie wurden gestoppt |
| `volumes: toolcalls:/data` | benanntes Volume überlebt Neustarts; Dashboard bindet es `:ro` ein |

## Starten und testen

Aus dem Projektordner (`output/project`):

```bash
APP_DIR=examples/m05-cloud-integration/l02-container-prep \
  docker compose -f examples/m06-containerization-cicd/l01-build-and-run/docker-compose.yml up --build -d
docker compose -f examples/m06-containerization-cicd/l01-build-and-run/docker-compose.yml ps
curl -i http://localhost:8000/health
python shared/agent_client.py --url http://localhost:8000/mcp --replay
```

Der Agent-Client verbindet sich mit der URL. Ausgabe des Replay-Dialogs gegen den Server im HTTP-Modus (aufgezeichnet mit einem lokalen Serverprozess, nicht im Container; derselbe Servercode):

```text
Verbunden mit vantra-ops, Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log, update_ticket_status  ·  LLM: replay

Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam", ...
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).
```

`docker compose ps` listet die Dienste mit Status (`running`, bei Healthcheck zusätzlich `(healthy)`); Ports stehen in der Spalte `PORTS`.

## Absturz und Fehler erkennen

| Signal | Befehl | Bedeutung |
| --- | --- | --- |
| Status | `docker compose ps -a` | `Exited (1)` = Prozess beendet; `Up … (unhealthy)` = Prozess läuft, `/health` antwortet nicht |
| Exit-Code | `docker inspect --format '{{.State.ExitCode}}' <container>` | 0 normal, 1 Fehler, 137 SIGKILL (z. B. Speicherlimit) |
| Health | `docker inspect --format '{{.State.Health.Status}}' <container>` | `starting`, `healthy`, `unhealthy` |
| Ursache | `docker compose logs mcp-server` | Traceback bzw. Startmeldung |

- Der Healthcheck des Images prüft den MCP-Port (8000); Dienste mit anderem Port (Mock-API, Dashboard) brauchen einen eigenen `healthcheck` in der Compose-Datei.
- Docker startet `unhealthy` Container nicht von selbst neu; das übernimmt erst die Liveness-Probe in Kubernetes (Lab 6.2).
- Das Dashboard bleibt bis zum Aufbau des Tool-Call-Protokolls leer („Noch keine Tool-Calls“); der Server dieses Stands schreibt es noch nicht.

## Typische Fehler

| Symptom | Ursache | Behebung |
| --- | --- | --- |
| `Connection refused` auf `localhost:8000` | `ports` fehlt oder Server bindet an `127.0.0.1` | `ports` ergänzen, `MCP_HOST=0.0.0.0` |
| `port is already allocated` | Host-Port belegt | anderen Host-Port: `MCP_PORT=8010 docker compose ...` und `--url http://localhost:8010/mcp` |
| Server kann Mock-API nicht erreichen | `MOCK_API_URL` zeigt auf `localhost` | Dienstname verwenden: `http://mock-api:8001` |
| Änderung am Code wirkt nicht | Image nicht neu gebaut | `up --build` |

## Fazit

- Der Container braucht einen veröffentlichten Port; der Client nutzt `http://localhost:8000/mcp`.
- Compose koppelt Dienste über Namen, Healthchecks und Startreihenfolge.
- Abstürze zeigen Status und Exit-Code, Hänger der Healthcheck.

In der Übung wird die Starter-Compose-Datei ergänzt, der Server gestartet und der Agent gegen den Container getestet.
