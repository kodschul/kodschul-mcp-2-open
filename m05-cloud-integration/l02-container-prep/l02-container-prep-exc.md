# Lab 5.2 – Übung: Dockerfile für den MCP-Server vervollständigen

**Dauer:** ca. 35 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja – Ergebnis ist ein baufähiges Dockerfile; Lab 6.1 startet daraus den Container.
**Arbeitsdatei:** `playground/Dockerfile`
**Starter:** `starters/m05-l02-Dockerfile`
**Vergleich:** `examples/m05-cloud-integration/l02-container-prep/Dockerfile`

## Vorbereitung

- Terminal im Projektordner `output/project`, Docker läuft (`docker version` zeigt Client und Server).
- Server und Dockerfile in den Playground kopieren:

  ```bash
  cp starters/m05-l02-Dockerfile playground/Dockerfile
  cp examples/m05-cloud-integration/l02-container-prep/server.py playground/server.py
  cp examples/m05-cloud-integration/l02-container-prep/context.py playground/context.py
  ```

- Der kopierte `server.py` ist der Prototyp aus Lab 4.1 plus Transport-Umschaltung und `/health` (Theorie: Abschnitt „Server“). Ein eigener `server.py` aus dem Playground funktioniert, wenn er diese zwei Änderungen enthält.
- Die Lücken im Starter tragen die Markierung `TODO(Aufgabe n)`.

## Aufgaben

1. **Konfiguration per Umgebung:** Ersetze `TODO(Aufgabe 1)` durch einen `ENV`-Block mit `MCP_TRANSPORT`, `MCP_HOST`, `MCP_PORT` und `TOOL_CALL_LOG` in den Werten aus dem Kommentar. Schreibe keinen Schlüssel und kein Token in die Datei.
2. **Nicht-Root-Nutzer:** Ersetze beide `TODO(Aufgabe 2)`: lege den Nutzer `app` mit uid 10001 an, erzeuge `/data`, übertrage `/data` an `app` und wechsle nach den `COPY`-Zeilen mit `USER` zu diesem Nutzer.
3. **Healthcheck:** Ersetze `TODO(Aufgabe 3)` durch einen `HEALTHCHECK`, der `http://127.0.0.1:8000/health` mit Python abfragt. Wähle Intervall, Timeout, Startfenster und Wiederholungen.
4. **Bauen und prüfen:**
   1. Baue das Image: `docker build -f playground/Dockerfile -t vantra-ops-mcp:local .`
   2. Zeige den Nutzer: `docker image inspect --format '{{.Config.User}}' vantra-ops-mcp:local`
   3. Zeige die Umgebung: `docker image inspect --format '{{json .Config.Env}}' vantra-ops-mcp:local`
   4. Prüfe, dass der Healthcheck eingetragen ist: `docker image inspect --format '{{json .Config.Healthcheck}}' vantra-ops-mcp:local`

## Checkpoint

- `docker build` endet ohne Fehler; `docker images` listet `vantra-ops-mcp` mit Tag `local`.
- Der Nutzer-Befehl gibt `app` aus.
- Die Umgebungsliste enthält `MCP_TRANSPORT=streamable-http` und `MCP_PORT=8000`, aber keinen Schlüssel, kein Token, kein Passwort.
- Der Healthcheck-Befehl liefert ein JSON mit `Test`, `Interval` und `Retries`.

## Abschlusskriterien

- `playground/Dockerfile` enthält keine `TODO`-Markierung mehr.
- Das Image baut, läuft als Nicht-Root und trägt einen Healthcheck.
- Kein Secret steht in der Datei oder im Image.

## Erweiterung

1. Lies die Portnummer im Healthcheck aus `MCP_PORT` statt sie fest zu schreiben.
2. Suche im Image-Verlauf nach Geheimnissen: `docker history --no-trunc vantra-ops-mcp:local` und prüfe die Ausgabe auf `KEY`, `TOKEN`, `SECRET`.
3. Notiere, welche Zeile des Dockerfiles den Layer-Cache bei einer Codeänderung nutzt und welche nicht.

## Fallback

Ohne laufendes Docker entfällt Aufgabe 4; stattdessen:

- **Dockerfile-Prüfung durch Lesen:** `playground/Dockerfile` gegen die Tabelle in der Lösung (Abschnitt „Prüfung ohne Docker“) abhaken.
- **Server-Probe lokal** (Bindung an `127.0.0.1`):

  ```bash
  MCP_TRANSPORT=streamable-http MCP_HOST=127.0.0.1 python playground/server.py
  curl -i http://127.0.0.1:8000/health
  ```

  Erwartet: Status `200 OK` und `{"status":"ok"}`. Der Beweis, dass das Image baut, entfällt; das Dockerfile bleibt ungetestet.
