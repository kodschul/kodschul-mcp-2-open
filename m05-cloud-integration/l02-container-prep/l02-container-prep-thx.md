# Lab 5.2: Vorbereitung auf Containerisierung

**Leitfragen:**

<details>
<summary>Welche Konfiguration darf nicht im Image landen?</summary>

Alles Geheime und alles Umgebungsabhängige: Schlüssel, Tokens, Passwörter (`LLM_API_KEY`, `MOCK_API_TOKEN`), `.env`-Dateien, Zugangsdaten. Ein Image ist teilbar und ändert sich nicht; Secrets kommen zur Laufzeit aus der Umgebung oder einem Secret-Speicher.

</details>

<details>
<summary>Woran prüft Kubernetes später die Gesundheit des Containers?</summary>

An Probes: HTTP-GET auf `/health` (Startup, Readiness, Liveness). Ein `HEALTHCHECK` aus dem Dockerfile wertet Kubernetes nicht aus.

</details>

- Ein containerfähiger MCP-Server liest seine Konfiguration aus der Umgebung, bietet einen Health-Pfad und läuft ohne Root-Rechte.
- Im Container ersetzt Streamable HTTP den stdio-Transport; derselbe Servercode läuft in beiden Modi.

## Anforderungen an einen containerfähigen Server

| Anforderung | Grund | Umsetzung im Projekt |
| --- | --- | --- |
| Konfiguration per Umgebung | ein Image für alle Umgebungen | `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT`, `MOCK_API_URL`, `VANTRA_ROLE`, `TOOL_CALL_LOG` |
| Netzwerk-Transport | stdio braucht einen Elternprozess, der Container hat keinen | Streamable HTTP auf Port 8000, Endpunkt `/mcp` |
| Health-Pfad | Orchestrator erkennt Start, Bereitschaft, Hänger | `GET /health` → `{"status":"ok"}` |
| Keine Secrets im Image | Image ist teilbar und unveränderlich | Secrets zur Laufzeit (`-e`, Compose, Kubernetes-Secret) |
| Nicht-Root | begrenzt Schaden bei Ausbruch | Nutzer `app`, uid 10001 |
| Ein beschreibbares Verzeichnis | read-only Dateisystem möglich | `/data` für das Tool-Call-Protokoll |
| Logs auf stdout/stderr | Plattform sammelt sie ein | Server loggt auf stderr, JSON-RPC läuft über HTTP |

## Server: Transport und Health per Umgebung

Beispiel: `examples/m05-cloud-integration/l02-container-prep/server.py` (Unterschied zum Prototyp: drei Stellen).

```python
from starlette.requests import Request
from starlette.responses import JSONResponse

# 1) Health-Pfad neben /mcp: keine Authentifizierung, keine Daten
@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})

# 2) Transport und Bindung nur über Umgebungsvariablen
if __name__ == "__main__":
    if os.getenv("MCP_TRANSPORT", "stdio") == "streamable-http":
        mcp.run(transport="streamable-http", host=os.getenv("MCP_HOST", "0.0.0.0"), port=int(os.getenv("MCP_PORT", "8000")))
    else:
        mcp.run()      # lokal weiter stdio
```

- Standard bleibt stdio; der Container setzt `MCP_TRANSPORT=streamable-http`.
- Im Container bindet der Server an `0.0.0.0`, sonst ist der Port von außen nicht erreichbar. Dann ist der DNS-Rebinding-Schutz des SDK aus (bekannte Lücke im Kursprojekt: `transport_security` ist nicht gesetzt).

Lokale Probe ohne Docker (Bindung an `127.0.0.1`), im Projektordner:

```bash
MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 python playground/server.py
curl -i http://127.0.0.1:8000/health
```

Tatsächliche Ausgabe von `curl` (Auszug):

```text
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

{"status":"ok"}
```

## Dockerfile mit Anmerkungen

`examples/m05-cloud-integration/l02-container-prep/Dockerfile`:

```dockerfile
# feste Basis, kleine Variante
FROM python:3.13-slim

# Build-Argument: welcher Server-Stand wird eingepackt
ARG APP_DIR=playground

# Konfiguration: nur unkritische Werte, keine Secrets
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    TOOL_CALL_LOG=/data/tool_calls.jsonl

WORKDIR /app

# zuerst nur die Abhängigkeiten: nutzt den Layer-Cache
COPY requirements-server.txt .
RUN pip install -r requirements-server.txt

# Nicht-Root-Nutzer; /data ist das einzige beschreibbare Verzeichnis
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir /data \
    && chown app:app /data

# Server-Stand und gemeinsame Hilfsmodule (Mock-API-Client u. a.)
COPY ${APP_DIR}/ /app/
COPY shared/ /app/shared/

# ab hier kein Root mehr; EXPOSE dokumentiert nur, öffnet keinen Port
USER app
EXPOSE 8000

# Docker-Healthcheck mit Python, kein curl im Image nötig
HEALTHCHECK --interval=15s --timeout=4s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('MCP_PORT', '8000') + '/health', timeout=3)"]

CMD ["python", "server.py"]
```

Bauen aus dem Projektordner (Build-Kontext ist immer `output/project`):

```bash
docker build -f playground/Dockerfile -t vantra-ops-mcp:local .
```

| Baustein | Wirkung |
| --- | --- |
| `COPY requirements-server.txt` vor `COPY playground/` | Abhängigkeiten werden nur neu installiert, wenn sich `requirements-server.txt` ändert |
| `USER app` | Prozess läuft mit uid 10001; Schreiben außerhalb von `/data` scheitert |
| `HEALTHCHECK` mit Python | kein `curl` im schlanken Image nötig |
| `.dockerignore` | hält `.env`, `.venv/`, `logs/`, `tests/`, `.git/` aus dem Build-Kontext |

## Konfiguration und Secrets: wohin womit

| Wert | Beispiel | Ort |
| --- | --- | --- |
| Unkritisch, fest | `MCP_PORT=8000`, `MCP_TRANSPORT` | `ENV` im Dockerfile |
| Unkritisch, je Umgebung | `MOCK_API_URL`, `VANTRA_ROLE`, `LOG_LEVEL` | Compose `environment`, Kubernetes ConfigMap |
| Geheim | `MOCK_API_TOKEN`, `LLM_API_KEY` | Laufzeit: `-e`, Compose-Secret, Kubernetes Secret; nie `ENV`/`COPY` im Dockerfile |
| Daten, die bleiben | `tool_calls.jsonl` | Volume nach `/data` |

- `ENV`-Werte stehen im Image und in `docker history`/`docker inspect`: sichtbar für jeden mit Zugriff auf das Image.
- Die `.env`-Datei des Projekts steht in `.dockerignore` und gelangt nicht in den Build.

## Health-Checks

| Ebene | Mechanismus | Reaktion bei Ausfall |
| --- | --- | --- |
| Docker | `HEALTHCHECK` im Dockerfile | Status `unhealthy` in `docker ps`; kein automatischer Neustart |
| Docker Compose | `healthcheck` je Dienst, `depends_on: condition: service_healthy` | Startreihenfolge; Neustart nur über `restart` bei Prozessende |
| Kubernetes | `startupProbe`, `readinessProbe`, `livenessProbe` auf `GET /health` | Readiness: Pod bekommt keinen Verkehr; Liveness: Container wird neu gestartet |

- `/health` prüft hier nur, dass der Prozess antwortet. Eine tiefere Prüfung (Mock-API erreichbar) macht Readiness aussagekräftiger, kostet aber Ausfälle bei Abhängigkeitsproblemen.

## Typische Fehler

| Fehler | Symptom | Behebung |
| --- | --- | --- |
| Bindung an `127.0.0.1` im Container | Port freigegeben, Verbindung wird abgewiesen | `MCP_HOST=0.0.0.0` |
| `COPY . .` vor `pip install` | jede Codeänderung installiert alles neu | Abhängigkeiten zuerst kopieren |
| Läuft als Root | `docker image inspect` zeigt leeren `User` | `useradd` plus `USER` |
| Secret in `ENV` | Wert in `docker inspect` lesbar | Laufzeit-Übergabe |
| `latest` als Tag | Rollback nicht eindeutig | fester Tag |

## Fazit

- Konfiguration per Umgebung, Health-Pfad und Nicht-Root machen den Server containerfähig.
- Geheimnisse gehören zur Laufzeit in die Umgebung, nie ins Image.
- Docker-`HEALTHCHECK` und Kubernetes-Probes sind getrennte Mechanismen für denselben Pfad.

In der Übung wird das Starter-Dockerfile um Konfiguration, Nicht-Root-Nutzer und Healthcheck ergänzt und gebaut.
