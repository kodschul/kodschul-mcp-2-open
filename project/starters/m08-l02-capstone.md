# Abschlussprojekt – Starter (Lab 8.2)

Kopieren nach `playground/capstone.md` und ausfüllen. Ziel: containerisierten, abgesicherten Vantra Ops Agent im Mini-Workflow vorführen.

## Voraussetzung (Checkliste)

- [ ] Server-Stand mit Policy (Lab 7.1) und Logging (Lab 8.1) liegt im `playground/`. Bei Lücken: `cp examples/m08-observability-and-capstone/l01-monitoring/{server.py,context.py,auth.py,policy.md,logging_config.py} playground/`
- [ ] Compose-Datei in **beiden** Terminals gesetzt: `export COMPOSE=examples/m06-containerization-cicd/l01-docker/docker-compose.yml` (Server, Mock-API, Dashboard; baut `playground/`). Eigene Datei mit Dienst `dashboard` (Erweiterung Lab 6.1): `export COMPOSE=playground/docker-compose.yml`

## Start

```bash
docker compose -f "$COMPOSE" up -d --build              # Rolle viewer (Standard), im Hintergrund
VANTRA_ROLE=operator docker compose -f "$COMPOSE" up -d  # Rollenwechsel: Schreibrechte
docker compose -f "$COMPOSE" up -d                       # zurück zu viewer
docker compose -f "$COMPOSE" logs -f mcp-server          # Server-Logs (Ctrl+C beendet nur die Anzeige)
curl -X POST http://localhost:8001/reset                 # Mock-Daten zurücksetzen
```

Agent (zweites Terminal):

```bash
python shared/agent_client.py --url http://localhost:8000/mcp --replay workflow --confirm yes
```

Dashboard: http://localhost:8080 · Mock-API: http://localhost:8001/tickets

## Workflow-Protokoll

| Schritt | Eingabe | Tool-Call | Ergebnis | Policy-Entscheidung |
| ------- | ------- | --------- | -------- | ------------------- |
| 1 | `Zeige Ticket VAN-102` | TODO(Aufgabe 1): eintragen | | |
| 2 | `Zeige das Deployment-Log dazu` | TODO(Aufgabe 1): eintragen | | |
| 3 | `Setze das Ticket auf in_progress` | TODO(Aufgabe 1): eintragen | | TODO(Aufgabe 2): Rolle viewer und Rolle operator vergleichen |

## Auswertung

TODO(Aufgabe 3): Welcher Schritt hätte ohne die Maßnahmen aus m07 versagen können? Was zeigt das Dashboard dazu?

TODO(Aufgabe 4): Was fehlt noch bis zum Produktivbetrieb? Mindestens drei Punkte.
