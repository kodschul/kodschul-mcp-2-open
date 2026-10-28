# Cheatsheet: Cloud-Integration und Container-Vorbereitung (Modul 5)

## Platzierung des MCP-Servers

| Muster | Aufbau | Transport | Wann |
| --- | --- | --- | --- |
| Sidecar | Server neben genau einem Agenten (Beiwagen) | stdio / localhost | strenge Isolation je Agent |
| Zentraler Service | ein Server mit festem Namen für viele Agenten | Streamable HTTP | mehrere interne Agenten, ein Betriebspunkt |
| Edge | Gateway am Netzwerkrand prüft und reicht weiter | Streamable HTTP, TLS | externe Clients |

## Adressen

| Umgebung | URL |
| --- | --- |
| lokal / Portfreigabe | `http://localhost:8000/mcp` |
| Docker Compose (Lab 6.1) | `http://mcp-server:8000/mcp` |
| Kubernetes, gleicher Namespace (Lab 6.2) | `http://vantra-ops-mcp:8000/mcp` |
| Kubernetes, anderer Namespace (Lab 6.2) | `http://vantra-ops-mcp.<namespace>.svc.cluster.local:8000/mcp` |

## Versionen

| Ebene | Wert / Befehl |
| --- | --- |
| Image | fester Tag, z. B. `vantra-ops-mcp:1.0.0` |
| Revisionen | `kubectl rollout history deployment/vantra-ops-mcp` (Lab 6.2) |
| Protokoll | `2026-07-28` (`server/discover` → `supportedVersions`) |

## Server-Konfiguration (Umgebungsvariablen)

| Variable | Wirkung | Standard |
| --- | --- | --- |
| `MCP_TRANSPORT` | `stdio` oder `streamable-http` | `stdio` |
| `MCP_HOST` | Bindung des HTTP-Servers | `0.0.0.0` |
| `MCP_PORT` | Port des HTTP-Servers | `8000` |
| `MOCK_API_URL` | HTTP-Mock-API statt prozesslokaler Daten | leer |
| `TOOL_CALL_LOG` | Pfad des Tool-Call-Protokolls (vorbereitet, wirkt ab Lab 8.1) | `logs/tool_calls.jsonl` |
| `VANTRA_ROLE` | Rolle des Servers (vorbereitet, wirkt ab Lab 7.1) | `viewer` |
| `MCP_SERVER_URL` | Server-Adresse des Agent-Clients | leer |

## Dockerfile-Bausteine

| Zeile | Wirkung |
| --- | --- |
| `FROM python:3.13-slim` | feste, kleine Basis |
| `ARG APP_DIR=playground` | Server-Stand per `--build-arg` wählbar |
| `ENV KEY=wert` | Konfiguration im Image (nie Secrets) |
| `COPY requirements-server.txt .` + `RUN pip install ...` | Abhängigkeiten als eigener, gecachter Layer |
| `RUN useradd --system --uid 10001 --no-create-home app` | Nicht-Root-Nutzer |
| `USER app` | Prozess ohne Root |
| `EXPOSE 8000` | dokumentiert den Port, öffnet ihn nicht |
| `HEALTHCHECK ... CMD [...]` | Docker prüft `/health` |
| `CMD ["python", "server.py"]` | Startbefehl in Exec-Form |

## Build und Prüfung

| Befehl | Wirkung |
| --- | --- |
| `docker build -f playground/Dockerfile -t vantra-ops-mcp:local .` | Image bauen (Kontext: Projektordner) |
| `docker image inspect --format '{{.Config.User}}' vantra-ops-mcp:local` | Nutzer des Images |
| `docker image inspect --format '{{json .Config.Env}}' vantra-ops-mcp:local` | Umgebung im Image |
| `docker image inspect --format '{{json .Config.Healthcheck}}' vantra-ops-mcp:local` | Healthcheck im Image |
| `docker history --no-trunc vantra-ops-mcp:local` | Layer und Befehle (Secrets-Suche) |
| `docker run -d -p 8000:8000 -e MOCK_API_TOKEN vantra-ops-mcp:local` | Secret beim Start aus der Shell übergeben |
| `MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 python playground/server.py` | lokale Probe ohne Docker |
| `curl -i http://127.0.0.1:8000/health` | Health-Pfad, erwartet `200` und `{"status":"ok"}` |

## Wohin mit welchem Wert

| Wert | Ort |
| --- | --- |
| Port, Transport | `ENV` im Dockerfile |
| URL, Log-Stufe, später Rolle je Umgebung | `docker run -e`, Compose `environment` (Lab 6.1), Kubernetes ConfigMap (Lab 6.2) |
| Tokens, Schlüssel | beim Start: `docker run -e NAME`, Kubernetes Secret (Lab 6.2) |
| Daten, die bleiben | Volume nach `/data` |

## Health-Mechanismen

| Ebene | Mechanismus | Folge bei Ausfall |
| --- | --- | --- |
| Docker | `HEALTHCHECK` | Status `unhealthy`, kein Neustart |
| Compose (Lab 6.1) | `healthcheck`, `depends_on: condition: service_healthy` | Startreihenfolge |
| Kubernetes (Lab 6.2) | `startupProbe`, `readinessProbe`, `livenessProbe` auf `/health` | kein Verkehr bzw. Neustart |

## Typische Fehler

| Fehler | Behebung |
| --- | --- |
| Verbindung abgewiesen trotz `-p` | `MCP_HOST=0.0.0.0` im Container |
| Jede Codeänderung installiert alles neu | `requirements-server.txt` vor dem Code kopieren |
| Prozess läuft als Root | `useradd` plus `USER` |
| Secret in `docker inspect` sichtbar | Laufzeit-Übergabe statt `ENV` |
| Tag `latest` | fester Tag |
