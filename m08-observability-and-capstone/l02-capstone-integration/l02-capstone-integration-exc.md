# Lab 8.2 – Übung: Abschlussprojekt – sicherer MCP-Agent im Mini-Workflow

**Dauer:** ca. 45 Minuten
**Ändert die Vantra-Projektbasis?** Nein — der Stand aus Lab 8.1 wird containerisiert ausgeführt und dokumentiert; der Gesamtstand liegt als Vergleich unter `examples/`.
**Arbeitsdatei:** `playground/capstone.md`
**Starter:** `starters/m08-l02-capstone.md`
**Beispiel (zum Vergleichen):** `examples/m08-observability-and-capstone/l02-capstone-integration/` (kompletter Stand, `run_demo.py`)
**Weitere Dateien:** `playground/docker-compose.yml`, `playground/Dockerfile` (Lab 5.2 und 6.1), `shared/agent_client.py`, `shared/dashboard/server.py`

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`; Docker läuft.
- `playground/` enthält Server, Policy und Logging (Lab 7.1 und 8.1) sowie Dockerfile und `docker-compose.yml`. Bei Lücken: `checkpoints/ende-m07-abgesichert/` nach `playground/` kopieren und `logging_config.py` samt `@logged`-Server aus `examples/m08-observability-and-capstone/l01-monitoring-setup/` übernehmen.
- Starter kopieren: `cp starters/m08-l02-capstone.md playground/capstone.md`; die Checkliste „Voraussetzung“ darin abhaken.
- Stack mit Rolle `viewer` starten (Terminal 1):

```bash
docker compose -f playground/docker-compose.yml up --build
```

## Aufgaben

1. **Workflow mit Rolle `viewer`:** Führe den Workflow in Terminal 2 aus und trage je Schritt Tool-Call und Ergebnis in die Tabelle in `playground/capstone.md` ein.

```bash
python shared/agent_client.py --url http://localhost:8000/mcp --replay workflow --confirm yes
```

2. **Rolle `operator`:** Stoppe den Stack (`docker compose -f playground/docker-compose.yml down`), starte ihn mit `VANTRA_ROLE=operator docker compose -f playground/docker-compose.yml up --build` neu und setze die Daten zurück (`curl -X POST http://localhost:8001/reset`). Führe den Workflow mit `--confirm yes` und danach mit `--confirm none` aus. Trage die Policy-Entscheidung für Schritt 3 je Rolle und Bestätigung in die Tabelle ein.
3. **Auswertung:** Beantworte in `playground/capstone.md`: Welcher Schritt hätte ohne die Maßnahmen aus Modul 7 versagen können? Führe den Workflow mit Rolle `viewer` dreimal kurz hintereinander aus, öffne http://localhost:8080 und notiere, was das Dashboard zeigt (Summen, Status, Banner).
4. **Lücken:** Nenne mindestens drei Punkte, die bis zum Produktivbetrieb fehlen. Notiere je Punkt, wo im Projekt der Stand dokumentiert ist (z. B. `policy.md`, Abschnitt „Offene Punkte“).

## Checkpoint

- `docker compose ps` zeigt `mcp-server`, `mock-api` und `dashboard` als laufend.
- Schritt 1 und 2 liefern in beiden Rollen Daten zu VAN-102.
- Mit Rolle `viewer` endet Schritt 3 mit `policy_denied`; mit Rolle `operator` ohne Bestätigung mit `confirmation_required`; mit Rolle `operator` und `--confirm yes` ändert sich der Status.
- Das Dashboard zeigt die Aufrufe beider Rollen mit Status `ok` und `denied`.

## Abschlusskriterien

- `playground/capstone.md` enthält das vollständige Workflow-Protokoll, die Policy-Entscheidungen je Rolle, die Auswertung und mindestens drei Lücken.
- Jede Aussage im Protokoll stammt aus einem tatsächlich ausgeführten Lauf.
- Alle drei Container laufen nach dem Neustart wieder.

## Erweiterung (optional)

- **Showcase C gegen den Container:** Stack mit Rolle `viewer` laufen lassen und `python shared/agent_client.py --url http://localhost:8000/mcp --replay injection --confirm none` ausführen. Notiere den Fehlercode und den Eintrag im Dashboard.
- **Ohne Programmierung (Entscheidung):** Erstelle ein Risikoregister für den Produktivbetrieb mit den Lücken aus Aufgabe 4: Risiko, Wahrscheinlichkeit, Auswirkung, Maßnahme, Verantwortliche. Entscheide, welche Lücken vor einem Pilotbetrieb mit realen Tickets geschlossen sein müssen.

## Fallback

Ohne funktionierendes Docker entfällt der Container. Der Workflow läuft dann mit dem Aufruf `python examples/m08-observability-and-capstone/l02-capstone-integration/run_demo.py` (drei Läufe: `viewer`, `operator` mit Bestätigung, `operator` ohne Bestätigung). Das Dashboard startet mit `python shared/dashboard/server.py` im Projektordner und liest `logs/tool_calls.jsonl`. Einschränkung: Der Container-Betrieb (Healthcheck, Compose, Ports) wird dabei nicht gezeigt; Aufgabe 1–4 bleiben bearbeitbar.
