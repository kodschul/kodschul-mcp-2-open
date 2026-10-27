# Abschlussprojekt – Starter (Lab 8.2)

Kopieren nach `playground/capstone.md` und ausfüllen. Ziel: containerisierten, abgesicherten Vantra Ops Agent im Mini-Workflow vorführen.

## Voraussetzung (Checkliste)

- [ ] Server-Stand mit Policy (Lab 7.1) und Logging (Lab 8.1) liegt im `playground/`. Bei Lücken: `checkpoints/ende-m07-abgesichert/` plus `logging_config.py` aus `examples/m08-observability-and-capstone/l01-monitoring-setup/`
- [ ] Dockerfile und `docker-compose.yml` aus Lab 5.2 und 6.1 liegen im `playground/`

## Start

```bash
docker compose -f playground/docker-compose.yml up --build            # Rolle viewer (Standard)
VANTRA_ROLE=operator docker compose -f playground/docker-compose.yml up --build   # Schreibrechte
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
