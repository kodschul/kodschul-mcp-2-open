# Lab 6.1 – Lösung: Container bauen, starten und mit dem Agenten testen

Vergleichsdatei: `examples/m06-containerization-cicd/l01-build-and-run/docker-compose.yml` (nutzt zusätzlich einen Anker für den Build, `APP_DIR` und Host-Port-Variablen).

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

Erwartete Ausgabe (`config --services`, abgeleitet aus der Datei; Reihenfolge kann abweichen):

```text
mock-api
mcp-server
```

Erwartete Ausgabe `ps` (Format je nach Compose-Version, nicht im Container aufgezeichnet):

```text
NAME                       SERVICE      STATUS                    PORTS
vantra-ops-mcp-server-1    mcp-server   Up 20 seconds             0.0.0.0:8000->8000/tcp
vantra-ops-mock-api-1      mock-api     Up 30 seconds (healthy)   0.0.0.0:8001->8001/tcp
```

Ausgaben von `curl` und Agent, aufgezeichnet gegen den Server im HTTP-Modus (lokaler Prozess, nicht im Container):

```text
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

{"status":"ok"}
```

```text
Verbunden mit vantra-ops, Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log, update_ticket_status  ·  LLM: replay

Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam", ...
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).
```

Skript-Client (aufgezeichnet gegen Mock-API plus Server im HTTP-Modus):

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

Der Server liest den Port mit `int(os.getenv("MCP_PORT"))` und scheitert beim Start. Ausgabe der letzten Zeilen (aufgezeichnet mit demselben Servercode und `MCP_TRANSPORT=streamable-http`, lokal):

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

Exit-Code `1` (Python-Traceback). Der reguläre Container bleibt davon unberührt: `healthy`. Erkennung: Exit-Code und Traceback bei einem beendeten Prozess, `unhealthy` bei einem Prozess, der läuft, aber `/health` nicht beantwortet.

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
      TOOL_CALL_LOG: /data/tool_calls.jsonl
      VANTRA_ROLE: ${VANTRA_ROLE:-viewer}
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

`http://localhost:8080` zeigt „Noch keine Tool-Calls“: der Server dieses Stands schreibt kein Tool-Call-Protokoll nach `/data/tool_calls.jsonl`. Das Volume ist aus Sicht des Dashboards `:ro`, es liest nur.

## Ohne Docker (Fallback)

Drei Terminals im Projektordner, gleiche Topologie wie im Container:

```bash
python shared/mock_api/app.py
MOCK_API_URL=http://127.0.0.1:8001 MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 python playground/server.py
python shared/agent_client.py --url http://127.0.0.1:8000/mcp --replay
```

Die Ausgabe entspricht der Agent-Ausgabe oben. Nicht belegt sind Image-Build, Compose-Netz und Healthcheck-Reihenfolge.
