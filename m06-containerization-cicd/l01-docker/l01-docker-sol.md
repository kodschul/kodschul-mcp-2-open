# Lab 6.1 – Lösung: Container bauen, starten und mit dem Agenten testen

Vergleichsdatei: `examples/m06-containerization-cicd/l01-docker/docker-compose.yml` (nutzt zusätzlich einen YAML-Anker für den Build, `APP_DIR` und Host-Port-Variablen; Theorie: Abschnitt „Anker und Variablen“).

## Aufgabe 1: Port veröffentlichen

```yaml
    ports:
      - "8000:8000"
```

Syntax `Host:Container`. Mit `"127.0.0.1:8000:8000"` bleibt der Port auf den eigenen Rechner beschränkt.

## Aufgabe 2: Mock-API ergänzen

Umgebung des Servers:

```yaml
      MOCK_API_URL: http://mock-api:8001
```

Neuer Dienst auf Höhe von `mcp-server`:

```yaml
  mock-api:
    build:
      context: ..
      dockerfile: playground/Dockerfile
    image: vantra-ops-mcp:local
    command: ["python", "shared/mock_api/app.py"]
    environment:
      MOCK_API_HOST: 0.0.0.0
      MOCK_API_PORT: "8001"
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=3)"]
      interval: 10s
      timeout: 4s
      retries: 3
      start_period: 5s
```

`mock-api` nutzt dasselbe Image (`shared/` liegt darin) und überschreibt nur den Startbefehl. Der Server erreicht sie über den Dienstnamen; `localhost` wäre der Server-Container selbst.

## Aufgabe 3: Startreihenfolge

```yaml
    depends_on:
      mock-api:
        condition: service_healthy
```

Ohne `condition` wartet Compose nur auf den Containerstart, nicht auf die Antwort der Mock-API.

## Aufgabe 4: Starten und testen

```bash
docker compose -f playground/docker-compose.yml config --services
docker compose -f playground/docker-compose.yml up --build -d
docker compose -f playground/docker-compose.yml ps
curl -i http://localhost:8000/health
python shared/agent_client.py --url http://localhost:8000/mcp --replay
python shared/script_client.py --url http://localhost:8000/mcp --call get_ticket '{"ticket_id": "VAN-102"}'
```

Ausgabe `config --services`:

```text
mock-api
mcp-server
```

Ausgabe `ps` (Docker 29.2.0, Compose v5.0.2, Spalten `IMAGE`, `COMMAND` und `CREATED` gekürzt):

```text
NAME                      SERVICE      STATUS                    PORTS
vantra-ops-mcp-server-1   mcp-server   Up 26 seconds (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
vantra-ops-mock-api-1     mock-api     Up 2 minutes (healthy)    0.0.0.0:8001->8001/tcp, [::]:8001->8001/tcp
```

Direkt nach `up -d` steht der Server einige Sekunden auf `(health: starting)`; `curl` antwortet erst danach.

Ausgaben von `curl` und Agent gegen den Container:

```text
HTTP/1.1 200 OK
date: Wed, 28 Oct 2026 14:18:22 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```

```text
Verbunden mit vantra-ops, Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log, update_ticket_status  ·  LLM: replay

Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam",   "status": "open",   "priority": "high",   "assignee": "jonas.brandt",   "se…
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).

Nutzer: Zeige das Deployment-Log dazu
  → Tool-Call: get_deployment_log({})
  ← ok: {   "id": "dep-2041",   "ticket_id": "VAN-102",   "service": "auth-service",   "version": "2.14.1",   "environment": "production",   "status": "degraded",   "lo…
Agent: Deployment dep-2041 (auth-service 2.14.1, Status degraded). Letzte Zeilen: auth      token cache disabled by config key AUTH_CACHE_TTL=0;  deploy    finished with warnings, rollback not triggered
```

Skript-Client gegen den Container (die Mock-API im Compose-Netz liefert die Daten, `docker compose logs mock-api` zeigt `GET /tickets/VAN-102`):

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log, update_ticket_status
is_error=False
{
  "id": "VAN-102",
  "title": "Login-Seite lädt nach Release 2.14 sehr langsam",
  "status": "open",
  "priority": "high",
  ...
```

## Aufgabe 5: Absturz provozieren

```bash
docker compose -f playground/docker-compose.yml run --rm -e MCP_PORT=abc mcp-server
echo $?
docker inspect --format '{{.State.Health.Status}}' vantra-ops-mcp-server-1
```

Der Server liest den Port mit `int(os.getenv("MCP_PORT"))` und scheitert beim Start. Ausgabe (Compose startet zuerst die Abhängigkeit `mock-api`, dann den Einmal-Container):

```text
 Container vantra-ops-mock-api-1 Running
 Container vantra-ops-mock-api-1 Waiting
 Container vantra-ops-mock-api-1 Healthy
 Container vantra-ops-mcp-server-run-42c7436ad9f9 Creating
 Container vantra-ops-mcp-server-run-42c7436ad9f9 Created
Traceback (most recent call last):
  File "/app/server.py", line 113, in <module>
    mcp.run(transport="streamable-http", host=os.getenv("MCP_HOST", "0.0.0.0"), port=int(os.getenv("MCP_PORT", "8000")))
                                                                                     ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'abc'
```

`echo $?` gibt `1` aus (Python-Traceback). Der reguläre Container bleibt davon unberührt: `docker inspect` meldet `healthy`. Erkennung: Exit-Code und Traceback bei einem beendeten Prozess, `unhealthy` bei einem Prozess, der läuft, aber `/health` nicht beantwortet.

## Aufgabe 6: Aufräumen

```bash
docker compose -f playground/docker-compose.yml down -v
```

`-v` entfernt das Volume `toolcalls`; ohne `-v` bleibt das Tool-Call-Protokoll erhalten.

## Vollständige Compose-Datei (Basis)

```yaml
name: vantra-ops

services:
  mcp-server:
    build:
      context: ..
      dockerfile: playground/Dockerfile
    image: vantra-ops-mcp:local
    environment:
      MCP_TRANSPORT: streamable-http
      MCP_PORT: "8000"
      MOCK_API_URL: http://mock-api:8001
      TOOL_CALL_LOG: /data/tool_calls.jsonl     # vorbereitet, wirkt ab Lab 8.1
      VANTRA_ROLE: ${VANTRA_ROLE:-viewer}       # vorbereitet, wirkt ab Lab 7.1
    ports:
      - "8000:8000"
    depends_on:
      mock-api:
        condition: service_healthy
    volumes:
      - toolcalls:/data

  mock-api:
    build:
      context: ..
      dockerfile: playground/Dockerfile
    image: vantra-ops-mcp:local
    command: ["python", "shared/mock_api/app.py"]
    environment:
      MOCK_API_HOST: 0.0.0.0
      MOCK_API_PORT: "8001"
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health', timeout=3)"]
      interval: 10s
      timeout: 4s
      retries: 3
      start_period: 5s

volumes:
  toolcalls:
```

## Erweiterung: Dashboard

```yaml
  dashboard:
    build:
      context: ..
      dockerfile: playground/Dockerfile
    image: vantra-ops-mcp:local
    command: ["python", "shared/dashboard/server.py"]
    environment:
      DASHBOARD_HOST: 0.0.0.0
      DASHBOARD_PORT: "8080"
      TOOL_CALL_LOG: /data/tool_calls.jsonl
    ports:
      - "8080:8080"
    volumes:
      - toolcalls:/data:ro
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"]
      interval: 10s
      timeout: 4s
      retries: 3
```

`http://localhost:8080` zeigt „Noch keine Tool-Calls im Protokoll. Das Protokoll schreibt der Server ab Lab 8.1 (logging_config.py).“; `GET /api/calls` liefert `"total": 0`. Der Server dieses Stands schreibt kein Tool-Call-Protokoll nach `/data/tool_calls.jsonl`. Das Volume ist aus Sicht des Dashboards `:ro`, es liest nur.

## Ohne Docker (Fallback)

Drei Terminals im Projektordner, gleiche Topologie wie im Container:

```bash
python shared/mock_api/app.py
MOCK_API_URL=http://127.0.0.1:8001 MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 python playground/server.py
python shared/agent_client.py --url http://127.0.0.1:8000/mcp --replay
```

Die Ausgabe entspricht der Agent-Ausgabe oben. Nicht belegt sind Image-Build, Compose-Netz und Healthcheck-Reihenfolge.
