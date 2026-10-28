# Lab 6.1 – Übung: Container bauen, starten und mit dem Agenten testen

**Dauer:** ca. 30 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja – Ergebnis ist ein containerisierter MCP-Server, den der Agent über HTTP erreicht; Lab 6.2 beschreibt dasselbe Image für Kubernetes.
**Arbeitsdatei:** `playground/docker-compose.yml`
**Starter:** `starters/m06-l01-compose.yml`
**Vergleich:** `examples/m06-containerization-cicd/l01-docker/docker-compose.yml`

## Vorbereitung

- Terminal im Projektordner `output/project`, Docker läuft, venv ist aktiv.
- Aus Lab 5.2 liegen `playground/Dockerfile`, `playground/server.py` und `playground/context.py` vor. Fehlt eine Datei, kopiere sie aus `examples/m05-cloud-integration/l02-container-prep/`; das Dockerfile des Starters aus Lab 5.2 muss vervollständigt sein.
- Starter kopieren: `cp starters/m06-l01-compose.yml playground/docker-compose.yml`
- Die Lücken im Starter tragen die Markierung `TODO(Aufgabe n)`.
- Alle Befehle laufen im Projektordner `output/project`; `-f playground/docker-compose.yml` nennt die Datei, `context: ..` darin zeigt zurück auf den Projektordner.

## Aufgaben

1. **Port veröffentlichen:** Ersetze `TODO(Aufgabe 1)` so, dass Container-Port 8000 unter Host-Port 8000 erreichbar ist (Schlüssel `ports`, Theorie: Abschnitt „Compose-Datei, Grundform“). Achte auf die Einrückung: `ports` steht auf derselben Ebene wie `environment`.
2. **Mock-API ergänzen:** Ersetze beide `TODO(Aufgabe 2)`: Setze `MOCK_API_URL` des Servers auf die Adresse der Mock-API im Compose-Netz, und lege den Dienst `mock-api` an (gleiches Image und Build, Startbefehl `python shared/mock_api/app.py`, `MOCK_API_HOST=0.0.0.0`, `MOCK_API_PORT=8001`, Port 8001 veröffentlicht, Healthcheck auf `http://127.0.0.1:8001/health`).
3. **Startreihenfolge:** Ersetze `TODO(Aufgabe 3)` so, dass `mcp-server` erst startet, wenn `mock-api` gesund ist.
4. **Starten und testen:**
   1. Prüfe die Datei: `docker compose -f playground/docker-compose.yml config --services`. Erwartet: zwei Zeilen `mock-api` und `mcp-server`; bei einem YAML-Fehler nennt Compose die Zeile.
   2. Starte: `docker compose -f playground/docker-compose.yml up --build -d`
   3. Zeige den Status: `docker compose -f playground/docker-compose.yml ps`. Erwartet: beide Dienste `Up … (healthy)`; steht dort `(health: starting)`, einige Sekunden warten und wiederholen.
   4. Rufe den Health-Pfad auf: `curl -i http://localhost:8000/health`. Erwartet: `HTTP/1.1 200 OK` und `{"status":"ok"}`.
   5. Starte den Agenten gegen den Container: `python shared/agent_client.py --url http://localhost:8000/mcp --replay`. Erwartet: erste Zeile `Verbunden mit vantra-ops, Protokoll 2026-07-28`.
   6. Rufe ein Tool ohne LLM auf: `python shared/script_client.py --url http://localhost:8000/mcp --call get_ticket '{"ticket_id": "VAN-102"}'`
5. **Absturz provozieren:**
   1. Starte den Server mit ungültigem Port: `docker compose -f playground/docker-compose.yml run --rm -e MCP_PORT=abc mcp-server`
   2. Notiere die letzte Zeile der Ausgabe und lies den Exit-Code mit `echo $?` (`$?` enthält den Exit-Code des letzten Befehls; Bash bzw. Git Bash).
   3. Zeige danach den Health-Status des regulären Containers: `docker inspect --format '{{.State.Health.Status}}' vantra-ops-mcp-server-1` (der Name kann je nach Compose-Version `vantra-ops_mcp-server_1` lauten; `docker compose ps` zeigt ihn).
6. **Aufräumen:** Beende alle Dienste und entferne das Volume: `docker compose -f playground/docker-compose.yml down -v`

## Checkpoint

- `config --services` listet `mcp-server` und `mock-api`.
- `docker compose ps` zeigt beide Dienste mit Status `Up … (healthy)`; der Server steht in den ersten Sekunden auf `(health: starting)`.
- `curl` antwortet mit `200 OK` und `{"status":"ok"}`.
- Der Agent meldet `Verbunden mit vantra-ops, Protokoll 2026-07-28` und beantwortet „Zeige Ticket VAN-102“ mit Status `open`, Version 3.
- Der Skript-Client gibt `is_error=False` und das Ticket VAN-102 aus.
- Der Absturzversuch endet mit einem `ValueError` und Exit-Code `1`.
- Nach `down -v` listet `docker compose ps` keinen Dienst mehr.

## Abschlusskriterien

- `playground/docker-compose.yml` enthält keine `TODO`-Markierung (außer der optionalen Erweiterung).
- Der Agent erreicht den Server im Container über `http://localhost:8000/mcp`.
- Ursache und Erkennungsweg des provozierten Absturzes sind benannt (Exit-Code, Traceback).

## Erweiterung

Dashboard ergänzen (`TODO(Erweiterung)` im Starter):

1. Lege den Dienst `dashboard` an: Startbefehl `python shared/dashboard/server.py`, `DASHBOARD_HOST=0.0.0.0`, Port 8080, `TOOL_CALL_LOG=/data/tool_calls.jsonl`, Volume `toolcalls` schreibgeschützt auf `/data`, eigener Healthcheck auf `http://127.0.0.1:8080/health` (der Healthcheck des Images prüft Port 8000 und passt nicht zum Dashboard).
2. Starte neu, öffne `http://localhost:8080` und notiere, was das Dashboard anzeigt und warum.

## Fallback

- **Ohne laufenden Docker-Daemon:** Aufgaben 1–3 bleiben (reine Dateiarbeit); Aufgaben 4–6 werden durch die Variante ohne Container ersetzt (drei Terminals, gleiche Topologie, siehe Lösung, Abschnitt „Ohne Docker“). Das Ergebnis belegt Server, Mock-API und Agent, nicht das Image.
- **Nur `docker`, kein `docker compose`:** Aufgabe 4.1 bis 4.3 entfallen; stattdessen `docker run -d -p 8000:8000 --name vantra-mcp vantra-ops-mcp:local` (Mock-API-Daten dann prozesslokal), danach Schritte 4.4 bis 4.6 und `docker rm -f vantra-mcp`.
