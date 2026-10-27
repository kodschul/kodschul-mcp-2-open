# Checkpoint: Ende m07 (abgesichert)

Stand nach Lab 7.1: containerfähiger Server (`MCP_TRANSPORT`, `/health`), Rollenprüfung und Bestätigungspflicht (`auth.py`, `policy.md`), Dockerfile, `docker-compose.yml`, `k8s.yaml`, `pipeline.yml`. Noch ohne strukturiertes Logging (kommt in Lab 8.1).

Wiedereinstieg in Modul 8:

```bash
cp checkpoints/ende-m07-abgesichert/{server.py,context.py,auth.py,policy.md} playground/
VANTRA_ROLE=operator python shared/agent_client.py --server playground/server.py --replay workflow --confirm yes
```

Container (aus dem Projektordner):

```bash
docker compose -f checkpoints/ende-m07-abgesichert/docker-compose.yml up --build
```
