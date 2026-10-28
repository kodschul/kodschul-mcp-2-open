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

`MCP_HOST=0.0.0.0` ist nötig, damit der Port außerhalb des Containers erreichbar ist. Mock-API-URL, die Rolle (ab Lab 7.1) und alle Secrets fehlen bewusst: sie kommen beim Start des Containers hinzu. `TOOL_CALL_LOG` ist vorbereitet; der Server schreibt das Protokoll ab Lab 8.1.

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

Ausgabe der drei `inspect`-Befehle (Docker 29.2.0; Python-Version und Prüfsumme wechseln mit dem Basis-Image):

```text
app
["PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","LANG=C.UTF-8","GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305","PYTHON_VERSION=3.13.18","PYTHON_SHA256=abb0102e6d4ae027509bcb82327d9dd85515b44a3ba8ad538cfc5e9847029f68","PYTHONUNBUFFERED=1","PYTHONDONTWRITEBYTECODE=1","MCP_TRANSPORT=streamable-http","MCP_HOST=0.0.0.0","MCP_PORT=8000","TOOL_CALL_LOG=/data/tool_calls.jsonl"]
{"Test":["CMD","python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"],"Interval":15000000000,"Timeout":4000000000,"StartPeriod":10000000000,"Retries":3}
```

`PATH`, `LANG`, `GPG_KEY`, `PYTHON_VERSION` und `PYTHON_SHA256` stammen aus dem Basis-Image. `GPG_KEY` ist der öffentliche Fingerabdruck des Signaturschlüssels der Python-Releases, kein Geheimnis. Die Zeiten erscheinen in Nanosekunden.

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
2. `docker history --no-trunc vantra-ops-mcp:local | grep -iE 'KEY|TOKEN|SECRET'` findet genau zwei Zeilen, beide aus dem Basis-Image: `ENV GPG_KEY=7169605F…` und die `RUN`-Zeile, die Python mit `gpg --recv-keys "$GPG_KEY"` prüft (öffentlicher Schlüssel, kein Geheimnis). Die eigenen Zeilen ab `WORKDIR /app` liefern keinen Treffer; damit ist die Prüfung bestanden.
3. Layer-Cache: Nach einer Änderung an `playground/server.py` meldet der Build `CACHED` für `WORKDIR`, `COPY requirements-server.txt`, `RUN pip install` und `RUN useradd`; `COPY playground/` und alles danach werden neu gebaut.

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
