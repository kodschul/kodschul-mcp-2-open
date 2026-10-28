# Lab 8.2 – Übung: Abschlussprojekt – sicherer MCP-Agent im Mini-Workflow

**Dauer:** ca. 40 Minuten
**Ändert die Vantra-Projektbasis?** Nein — der Stand aus Lab 8.1 wird containerisiert ausgeführt und dokumentiert; der Gesamtstand liegt als Vergleich unter `examples/`.
**Arbeitsdatei:** `playground/capstone.md`
**Starter:** `starters/m08-l02-capstone.md`
**Beispiel (zum Vergleichen):** `examples/m08-observability-and-capstone/l02-capstone/` (kompletter Stand, `run_demo.py`)
**Weitere Dateien:** `examples/m06-containerization-cicd/l01-docker/docker-compose.yml` (Server, Mock-API, Dashboard), `shared/agent_client.py`, `shared/dashboard/server.py`

## Vorbereitung

- Virtuelle Umgebung ist aktiv, Befehle laufen im Projektordner `output/project`; Docker läuft.
- `playground/` enthält Server, Policy und Logging (Lab 7.1 und 8.1). Bei Lücken: `cp examples/m08-observability-and-capstone/l01-monitoring/{server.py,context.py,auth.py,policy.md,logging_config.py} playground/`.
- Zwei Terminals im Projektordner `output/project` öffnen. In **beiden** Terminals die Compose-Datei festlegen:

```bash
export COMPOSE=examples/m06-containerization-cicd/l01-docker/docker-compose.yml
```

  Sie baut den Stand aus `playground/` und startet Server, Mock-API und Dashboard. Mit einer eigenen `playground/docker-compose.yml` samt Dienst `dashboard` (Erweiterung Lab 6.1) gilt stattdessen `export COMPOSE=playground/docker-compose.yml`. Dockerfile und Compose-Datei aus `checkpoints/` nicht nach `playground/` kopieren: ihre relativen Pfade gelten nur an ihrem Ort.
- Starter kopieren: `cp starters/m08-l02-capstone.md playground/capstone.md`; die Checkliste „Voraussetzung“ darin abhaken.
- Stack mit Rolle `viewer` im Hintergrund starten (Terminal 1, `-d` gibt das Terminal sofort wieder frei):

```bash
docker compose -f "$COMPOSE" up -d --build
docker compose -f "$COMPOSE" ps
```

Erwartete Ausgabe von `ps` nach etwa 20 Sekunden: `mcp-server`, `mock-api` und `dashboard` mit Status `Up … (healthy)` bzw. `Up`.

Server-Logs live verfolgen (Terminal 1, beenden mit Ctrl+C, der Stack läuft weiter):

```bash
docker compose -f "$COMPOSE" logs -f mcp-server
```

**Zeitplan:** Vorbereitung ca. 8 Minuten, Aufgabe 1–2 ca. 15 Minuten, Aufgabe 3 ca. 10 Minuten, Aufgabe 4 ca. 7 Minuten.

## Aufgaben

1. **Workflow mit Rolle `viewer`:** Führe den Workflow in Terminal 2 aus und trage je Schritt Tool-Call und Ergebnis in die Tabelle in `playground/capstone.md` ein.

```bash
python shared/agent_client.py --url http://localhost:8000/mcp --replay workflow --confirm yes
```

2. **Rolle `operator`:** Wechsle die Rolle des Servers. `up -d` erzeugt nur den Container `mcp-server` neu, weil sich nur seine Umgebung ändert; ein neuer Build ist nicht nötig:

```bash
VANTRA_ROLE=operator docker compose -f "$COMPOSE" up -d
docker compose -f "$COMPOSE" exec mcp-server printenv VANTRA_ROLE    # erwartet: operator
curl -X POST http://localhost:8001/reset
```

   Führe den Workflow in Terminal 2 mit `--confirm yes` und danach mit `--confirm none` aus. Trage die Policy-Entscheidung für Schritt 3 je Rolle und Bestätigung in die Tabelle ein.
3. **Auswertung:** Beantworte in `playground/capstone.md`: Welcher Schritt hätte ohne die Maßnahmen aus Modul 7 versagen können? Setze danach die Rolle zurück auf `viewer`:

```bash
docker compose -f "$COMPOSE" up -d
docker compose -f "$COMPOSE" exec mcp-server printenv VANTRA_ROLE    # erwartet: viewer
```

   Führe den Workflow in Terminal 2 dreimal kurz hintereinander aus, öffne http://localhost:8080 und notiere, was das Dashboard zeigt (Summen, Status, Banner).
4. **Lücken:** Nenne mindestens drei Punkte, die bis zum Produktivbetrieb fehlen. Notiere je Punkt, wo im Projekt der Stand dokumentiert ist (z. B. `policy.md`, Abschnitt „Offene Punkte“).

## Checkpoint

- `docker compose -f "$COMPOSE" ps` zeigt `mcp-server`, `mock-api` und `dashboard` als laufend.
- Schritt 1 und 2 liefern in beiden Rollen Daten zu VAN-102.
- Mit Rolle `viewer` endet Schritt 3 mit `policy_denied`; mit Rolle `operator` ohne Bestätigung mit `confirmation_required`; mit Rolle `operator` und `--confirm yes` ändert sich der Status.
- Das Dashboard zeigt die Aufrufe beider Rollen mit Status `ok` und `denied`.

## Wenn es hakt

| Symptom | Ursache | Lösung |
| --- | --- | --- |
| `open : no such file or directory` oder `-f ""` | `COMPOSE` ist in diesem Terminal nicht gesetzt | `export COMPOSE=…` aus der Vorbereitung im Terminal wiederholen |
| Dienst `unhealthy` | Healthcheck-Timeout (4 s) auf ausgelastetem Rechner oder Startfehler | `docker compose -f "$COMPOSE" logs mcp-server` lesen, danach erneut `up -d` |
| Rolle wechselt nicht | `VANTRA_ROLE` ist in der Shell dauerhaft exportiert | `unset VANTRA_ROLE`, dann `up -d` mit bzw. ohne Präfix |
| `port is already allocated` | ein Server aus einem früheren Lab läuft noch | anderen Stack mit `docker compose -f <Datei> down` stoppen oder `MCP_PORT=8010` voranstellen und `--url http://localhost:8010/mcp` verwenden |
| Schritt 3 scheitert mit `version_conflict` | Daten aus einem früheren Lauf geändert | `curl -X POST http://localhost:8001/reset` |
| Änderungen in `playground/` fehlen im Container | Image ohne neuen Build | `docker compose -f "$COMPOSE" up -d --build` |

## Abschlusskriterien

- `playground/capstone.md` enthält das vollständige Workflow-Protokoll, die Policy-Entscheidungen je Rolle, die Auswertung und mindestens drei Lücken.
- Jede Aussage im Protokoll stammt aus einem tatsächlich ausgeführten Lauf.
- Alle drei Container laufen nach dem Neustart wieder.

## Erweiterung (optional)

- **Showcase C gegen den Container:** Stack mit Rolle `viewer` laufen lassen und `python shared/agent_client.py --url http://localhost:8000/mcp --replay injection --confirm none` ausführen. Notiere den Fehlercode und den Eintrag im Dashboard.
- **Ohne Programmierung (Entscheidung):** Erstelle ein Risikoregister für den Produktivbetrieb mit den Lücken aus Aufgabe 4: Risiko, Wahrscheinlichkeit, Auswirkung, Maßnahme, Verantwortliche. Entscheide, welche Lücken vor einem Pilotbetrieb mit realen Tickets geschlossen sein müssen.

## Fallback

Ohne funktionierendes Docker entfällt der Container. Der Workflow läuft dann mit dem Aufruf `python examples/m08-observability-and-capstone/l02-capstone/run_demo.py` (drei Läufe: `viewer`, `operator` mit Bestätigung, `operator` ohne Bestätigung). Das Dashboard startet mit `python shared/dashboard/server.py` im Projektordner und liest `logs/tool_calls.jsonl`. Die drei Läufe mit Rolle `viewer` für Aufgabe 3: dreimal `python shared/agent_client.py --server examples/m08-observability-and-capstone/l02-capstone/server.py --replay workflow --role viewer --confirm yes`. Einschränkung: Der Container-Betrieb (Healthcheck, Compose, Ports) wird dabei nicht gezeigt; Aufgabe 1–4 bleiben bearbeitbar.
