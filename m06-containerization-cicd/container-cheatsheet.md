# Cheatsheet: Containerisierung, Orchestrierung und CI/CD (Modul 6)

## Docker

| Befehl | Wirkung |
| --- | --- |
| `docker build -f playground/Dockerfile -t vantra-ops-mcp:local .` | Image bauen (Kontext: Projektordner) |
| `docker run -d -p 8000:8000 --name vantra-mcp vantra-ops-mcp:local` | Container starten, Port veröffentlichen |
| `docker run --rm -e MCP_PORT=abc vantra-ops-mcp:local` | Start mit überschriebener Umgebungsvariable |
| `docker ps` / `docker ps -a` | laufende / alle Container |
| `docker logs vantra-mcp` | Ausgabe des Containers |
| `docker inspect --format '{{.State.Health.Status}}' <container>` | `starting`, `healthy`, `unhealthy` |
| `docker inspect --format '{{.State.ExitCode}}' <container>` | Exit-Code (0 normal, 1 Fehler, 137 SIGKILL) |
| `docker rm -f vantra-mcp` | Container entfernen |

## Docker Compose

| Befehl | Wirkung |
| --- | --- |
| `docker compose -f playground/docker-compose.yml config --services` | Datei prüfen, Dienste auflisten |
| `docker compose -f playground/docker-compose.yml up --build -d` | bauen und im Hintergrund starten |
| `docker compose -f playground/docker-compose.yml ps` | Dienste, Status, Ports |
| `docker compose -f playground/docker-compose.yml logs mcp-server` | Logs eines Dienstes |
| `docker compose -f playground/docker-compose.yml run --rm -e MCP_PORT=abc mcp-server` | Einmal-Start mit geänderter Umgebung |
| `docker compose -f playground/docker-compose.yml down -v` | stoppen, entfernen, Volumes löschen |
| `APP_DIR=<ordner> docker compose -f <datei> up --build` | anderen Server-Stand bauen (Beispieldatei) |

| Compose-Schlüssel | Bedeutung |
| --- | --- |
| `build.context` / `build.dockerfile` | Kontext-Ordner / Dockerfile relativ zum Kontext |
| `ports: "8000:8000"` | Host-Port:Container-Port; `"127.0.0.1:8000:8000"` nur lokal |
| `environment` | Umgebungsvariablen des Dienstes |
| `depends_on: <dienst>: condition: service_healthy` | Start nach bestandenem Healthcheck |
| `healthcheck.test` | Prüfbefehl (`["CMD", ...]`), dazu `interval`, `timeout`, `retries`, `start_period` |
| `restart: unless-stopped` | Neustart nach Prozessende |
| `volumes: toolcalls:/data` (`:ro` lesend) | benanntes Volume |

## Agent und Client gegen den Container

| Befehl | Wirkung |
| --- | --- |
| `curl -i http://localhost:8000/health` | Health-Pfad, erwartet `200` und `{"status":"ok"}` |
| `python shared/agent_client.py --url http://localhost:8000/mcp --replay` | Agent mit Replay-LLM gegen die URL |
| `python shared/script_client.py --url http://localhost:8000/mcp --call get_ticket '{"ticket_id": "VAN-102"}'` | Tool ohne LLM aufrufen |

| Symptom | Behebung |
| --- | --- |
| `Connection refused` | `ports` ergänzen, `MCP_HOST=0.0.0.0` |
| `port is already allocated` | anderer Host-Port, URL anpassen |
| Server erreicht Mock-API nicht | `MOCK_API_URL=http://mock-api:8001` (Dienstname) |
| Dienst `unhealthy` obwohl er läuft | Healthcheck prüft den falschen Port (Image prüft 8000) |

## Kubernetes-Ressourcen

| Ressource | Zweck | Wichtige Felder |
| --- | --- | --- |
| ConfigMap | unkritische Konfiguration | `data` (Werte sind Texte, Zahlen in Anführungszeichen) |
| Secret | geheime Werte | nie Werte im Repo; Referenz per `secretKeyRef` |
| Deployment | Replikas, Rollout, Rollback | `replicas`, `strategy`, `template`, `image` mit festem Tag |
| Service (`ClusterIP`) | stabile Adresse im Cluster | `selector`, `port`, `targetPort` |
| `startupProbe` | Zeit zum Starten | `periodSeconds`, `failureThreshold` |
| `readinessProbe` | Verkehr nur an bereite Pods | HTTP-GET `/health` |
| `livenessProbe` | Neustart bei Hänger | HTTP-GET `/health` |
| `securityContext` | Rechte | `runAsNonRoot`, `runAsUser`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true` |
| `resources` | Platzierung und Obergrenze | `requests`, `limits` |

## kubectl und Validierung

| Befehl | Wirkung |
| --- | --- |
| `kubeconform -strict -summary playground/k8s.yaml` | Schema-Prüfung ohne Cluster |
| `kubectl apply --dry-run=client --validate=false -f playground/k8s.yaml` | Trockenlauf (je nach Version Cluster nötig) |
| `kubectl apply -f playground/k8s.yaml` | anwenden (Cluster nötig) |
| `kubectl rollout status deployment/vantra-ops-mcp` | auf Rollout warten |
| `kubectl rollout history deployment/vantra-ops-mcp` | Revisionen |
| `kubectl rollout undo deployment/vantra-ops-mcp` | Rollback |
| `kubectl set image deployment/vantra-ops-mcp mcp-server=<image>:<tag>` | neues Image ausrollen |
| `kubectl port-forward service/vantra-ops-mcp 8000:8000` | Service lokal erreichbar machen |
| `kubectl create secret generic vantra-ops-secrets --from-literal=MOCK_API_TOKEN=<wert>` | Secret anlegen |
| `kubectl delete -f playground/k8s.yaml` | Ressourcen entfernen |

## Pipeline-Stufen

| Stufe | Inhalt | Kennzeichen in der Datei |
| --- | --- | --- |
| build | Image mit Commit-SHA taggen | `${GITHUB_SHA::12}` |
| test | `pytest -q` | `actions/setup-python` |
| scan | `pip-audit`, Trivy, Policy-Test | `needs: [build, test]` |
| deploy | Freigabe, `kubectl set image`, `rollout status` | `environment: production`, `needs: [build, scan]` |
| rollback | `kubectl rollout undo` | `if: failure()` |
