# Lab 5.2 – Lösung: Dockerfile für den MCP-Server vervollständigen

Vergleichsdatei: `examples/m05-cloud-integration/l02-container-prep/Dockerfile` (nutzt zusätzlich `ARG APP_DIR` und `PIP_NO_CACHE_DIR`).

## Aufgabe 1: Konfiguration per Umgebung

```dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    TOOL_CALL_LOG=/data/tool_calls.jsonl
```

`MCP_HOST=0.0.0.0` ist nötig, damit der Port außerhalb des Containers erreichbar ist. Rolle, Mock-API-URL und alle Secrets fehlen bewusst: sie kommen zur Laufzeit.

## Aufgabe 2: Nicht-Root-Nutzer

Anlegen nach der Installation der Abhängigkeiten, Wechsel nach den `COPY`-Zeilen:

```dockerfile
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir /data \
    && chown app:app /data

COPY playground/ /app/
COPY shared/ /app/shared/

USER app
```

`USER` steht nach den `COPY`-Zeilen, damit `COPY` noch als Root schreibt und die Dateien nicht dem Prozess gehören. Der Prozess darf nur `/data` beschreiben.

## Aufgabe 3: Healthcheck

```dockerfile
HEALTHCHECK --interval=15s --timeout=4s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]
```

Schlägt der HTTP-Aufruf fehl (Fehlercode, Timeout), endet Python mit Fehler und Docker zählt einen Fehlversuch; nach drei Fehlversuchen gilt der Container als `unhealthy`. `--start-period` gibt dem Server Zeit zum Starten.

## Aufgabe 4: Bauen und prüfen

```bash
docker build -f playground/Dockerfile -t vantra-ops-mcp:local .
docker image inspect --format '{{.Config.User}}' vantra-ops-mcp:local
docker image inspect --format '{{json .Config.Env}}' vantra-ops-mcp:local
docker image inspect --format '{{json .Config.Healthcheck}}' vantra-ops-mcp:local
```

Erwartete Ausgabe (nicht auf einem Docker-Daemon aufgezeichnet, aus der Dockerfile abgeleitet):

```text
app
["PATH=...","PYTHONUNBUFFERED=1","PYTHONDONTWRITEBYTECODE=1","MCP_TRANSPORT=streamable-http","MCP_HOST=0.0.0.0","MCP_PORT=8000","TOOL_CALL_LOG=/data/tool_calls.jsonl",...]
{"Test":["CMD","python","-c","import urllib.request; ..."],"Interval":15000000000,"Timeout":4000000000,"StartPeriod":10000000000,"Retries":3}
```

Die Basis-Image-Variablen (`PATH`, `PYTHON_VERSION` u. a.) stehen zusätzlich in der Liste. Die Zeiten erscheinen in Nanosekunden.

## Vollständiges Dockerfile

```dockerfile
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    TOOL_CALL_LOG=/data/tool_calls.jsonl

WORKDIR /app

COPY requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir /data \
    && chown app:app /data

COPY playground/ /app/
COPY shared/ /app/shared/

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=4s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["python", "server.py"]
```

## Erweiterung

1. Healthcheck mit `MCP_PORT`: `CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('MCP_PORT', '8000') + '/health', timeout=3)"]`
2. `docker history --no-trunc vantra-ops-mcp:local` zeigt die `ENV`-Zeilen und Build-Befehle, aber keine Zeile mit `KEY`, `TOKEN` oder `SECRET`; die Prüfung ist bestanden, wenn der Filter nichts findet.
3. Layer-Cache: `COPY requirements-server.txt` und `RUN pip install` bleiben bei Codeänderungen im Cache; `COPY playground/` und alles danach werden neu gebaut.

## Prüfung ohne Docker (Fallback)

| Prüfpunkt | Erfüllt, wenn |
| --- | --- |
| Basis-Image | `FROM python:3.13-slim` mit festem Versions-Tag, kein `latest` |
| Konfiguration | `ENV` enthält `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, `TOOL_CALL_LOG` |
| Secrets | kein Schlüssel, Token oder Passwort in `ENV`, `ARG`, `COPY` oder `RUN` |
| Layer-Cache | `COPY requirements-server.txt` und `RUN pip install` stehen vor `COPY playground/` |
| Nicht-Root | `useradd` mit uid 10001 und `USER app` nach den `COPY`-Zeilen |
| Schreibrechte | `/data` gehört `app`, sonst ist nichts beschreibbar vorgesehen |
| Healthcheck | `HEALTHCHECK` fragt `/health` auf dem Server-Port ab |
| Startbefehl | `CMD ["python", "server.py"]` in Exec-Form |

Lokale Probe, tatsächliche Ausgabe (Server mit `MCP_TRANSPORT=streamable-http`, `MCP_HOST=127.0.0.1`, Port 8000):

```text
$ curl -si http://127.0.0.1:8000/health
HTTP/1.1 200 OK
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```
