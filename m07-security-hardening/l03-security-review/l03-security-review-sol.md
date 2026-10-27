# Lab 7.3 – Lösung: Security-Review mit Checkliste

Geprüft: `examples/m07-security-hardening/l03-security-review/flawed/Dockerfile` und `flawed/policy.md`. Die vollständige Befundliste steht in `findings-beispiel.md` (16 Befunde, 7 blockierend). Die Einstufung ist Diskussionsgrundlage, nicht jeder Befund muss gefunden werden.

## Aufgabe 1: Checkliste bewertet

| # | Prüffrage | Ergebnis | Fundstelle |
| --- | --- | --- | --- |
| A1 | Basis-Image mit fester Version? | ✘ | `FROM python:latest` |
| A2 | Nicht-Root-Nutzer? | ✘ | kein `USER` |
| A3 | Keine Secrets im Image oder in `ENV`? | ✘ | `ENV LLM_API_KEY=sk-demo-…` |
| A4 | Nur benötigte Dateien kopiert? | ✘ | `COPY . .` |
| A5 | Abhängigkeiten gepinnt? | ✘ | `RUN pip install mcp httpx openai` |
| A6 | `HEALTHCHECK`? | ✘ | fehlt |
| A7 | Nur benötigte Ports und Pakete? | ✘ | `EXPOSE 8000 22`, `openssh-server`, `curl` |
| A8 | Restriktive Dateirechte? | ✘ | `chmod -R 777 /app` |
| B1 | Rollen nach Least Privilege? | ✘ | Tabelle „alle Agenten“; `ENV VANTRA_ROLE=operator` im Image |
| B2 | Deny by default? | ✘ | Regel 2: „erlaubt“ |
| B3 | Rolle aus vertrauenswürdiger Quelle? | ✘ | Regel 1: Rolle im Tool-Argument |
| B4 | Schreib-Tools nur mit Bestätigung? | ✘ | Regel 3, Tabelle |
| B5 | Durchsetzung im Server? | ✘ | Regel 5: nur Systemprompt |
| B6 | Jeder Aufruf protokolliert? | ✘ | Regel 6: nur bei Fehlern |
| B7 | Eigene Identität je Client? | ✘ | Regel 4: gemeinsamer Token `svc-vantra-ops` |
| B8 | Erkennung und Reaktion beschrieben? | ✘ | fehlt; Regel 7 verneint regelmäßige Überprüfung |
| C1 | Eingaben validiert? | ? | Server-Code nicht Teil der Dateien |
| C2 | Ergebnisse als Daten behandelt? | ? | Server-Code nicht Teil der Dateien |
| C3 | Konfiguration über Umgebung/Secret-Store? | ✘ | Schlüssel steht in `ENV` im Image |
| C4 | Keine Secrets/Ticket-Inhalte im Protokoll? | ✘ | Regel 6: voller Ticket-Text und Tokens |
| C5 | Rollback-Weg? | ? | in den Dateien nicht erkennbar |

## Aufgabe 2: Befunde

| # | Gegenstand | Fundstelle | Befund | Schwere | Empfehlung |
| - | ---------- | ---------- | ------ | ------- | ---------- |
| 1 | Dockerfile | `ENV LLM_API_KEY=...` | Secret im Image, jede Person mit Image-Zugriff kann es lesen | blockierend | Wert zur Laufzeit per Secret/Umgebung übergeben, Schlüssel rotieren |
| 2 | Dockerfile | kein `USER` | Prozess läuft als root | blockierend | Nicht-Root-Nutzer anlegen und mit `USER` setzen |
| 3 | Dockerfile | `COPY . .` | kopiert alles, auch `.env`, Tests, Git-Daten | blockierend | gezielt kopieren, `.dockerignore` ergänzen |
| 4 | Dockerfile | `EXPOSE 8000 22`, `openssh-server`, `curl` | unnötige Angriffsfläche | wichtig | nur Port 8000, keine zusätzlichen Dienste |
| 5 | Dockerfile | `FROM python:latest` | nicht reproduzierbar, unerwartete Updates | wichtig | feste Version, z. B. `python:3.13-slim` |
| 6 | Dockerfile | `pip install mcp httpx openai` | Abhängigkeiten nicht gepinnt | wichtig | Versionen in `requirements.txt` festlegen |
| 7 | Dockerfile | `chmod -R 777 /app` | jeder Prozess im Container darf Code ändern | wichtig | Rechte entziehen, nur `/data` beschreibbar |
| 8 | Dockerfile | `ENV VANTRA_ROLE=operator` | Schreibrechte als Standard im Image | wichtig | Standardrolle `viewer`, Rolle per Deployment setzen |
| 9 | Dockerfile | kein `HEALTHCHECK` | Ausfall wird nicht erkannt | nice to have | Health-Endpunkt und `HEALTHCHECK` ergänzen |
| 10 | Policy | Regel 1 | Rolle kommt vom Aufrufer (Argument) und kann gefälscht werden | blockierend | Rolle aus Server-Konfiguration oder Authentifizierung ableiten |
| 11 | Policy | Regel 2 | Standard „erlaubt“ statt deny by default | blockierend | Unbekanntes ablehnen |
| 12 | Policy | Tabelle und Regel 3 | Schreib-Tool für alle Agenten ohne Bestätigung | blockierend | Schreiben nur für `operator` und mit Bestätigung |
| 13 | Policy | Regel 4 | ein gemeinsamer Token für alle Agenten, keine Zuordnung von Aufrufen | wichtig | eigene Identität je Client |
| 14 | Policy | Regel 5 | Schutz nur über Systemprompt, nicht im Server durchgesetzt | blockierend | Durchsetzung im Server, Prompt nur als zusätzliche Schicht |
| 15 | Policy | Regel 6 | Protokoll nur bei Fehlern, enthält Ticket-Texte und Tokens | wichtig | jeden Aufruf protokollieren, ohne Inhalte und Secrets |
| 16 | Policy | Regel 7 | keine regelmäßige Überprüfung | nice to have | Review-Intervall und Verantwortliche festlegen |

## Aufgabe 3: Leitfragen und Entscheidung

**Blockierend** sind die Befunde 1, 2, 3, 10, 11, 12 und 14. Jeder ermöglicht unmittelbar Zugriff oder Rechteausweitung:

| Befund | Begründung |
| --- | --- |
| 1 | Der Schlüssel ist für jede Person mit Image-Zugriff lesbar |
| 2 | Ein Ausbruch im Prozess hat Root-Rechte |
| 3 | `.env`, Git-Daten und Tests gelangen ins Image |
| 10 | Der Aufrufer wählt die Rolle selbst, die Rollenprüfung ist wirkungslos |
| 11 | Jedes neue Tool und jede neue Rolle ist sofort offen |
| 12 | Eine einzige manipulierte Anweisung ändert Tickets ohne Rückfrage |
| 14 | Ein Systemprompt ist kein technischer Schutz; das Modell kann ihn ignorieren |

**Nice to have** sind die Befunde 9 (`HEALTHCHECK`) und 16 (Review-Intervall): Beide verbessern Betrieb und Pflege, öffnen aber keinen Zugriff.

**Freigabe: nein.** Sieben blockierende Befunde. Reihenfolge der Behebung: 1 (Schlüssel rotieren), 10–12 und 14 (Policy neu fassen, Durchsetzung im Server), dann 2–3, danach die „wichtig“-Befunde.

## Aufgabe 4: Vergleich

Mögliche Abweichungen, die sich begründen lassen:

| Befund | Alternative Einstufung | Begründung |
| --- | --- | --- |
| 8 (`VANTRA_ROLE=operator` im Image) | blockierend | zusammen mit Befund 12 hat jeder Client Schreibrechte ohne Bestätigung |
| 13 (gemeinsamer Token) | blockierend | bei einem kompromittierten Client ist keine Zuordnung und kein gezielter Entzug möglich |
| 4 (Port 22, `openssh-server`) | blockierend | erreichbarer Fernzugang im Container |
| 15 (Tokens im Protokoll) | blockierend | Tokens im Klartext im Log sind ein Secret-Leck |

Die Einstufung hängt vom Einsatzumfeld ab. Entscheidend ist die Begründung, die Empfehlung bleibt gleich.

## Erweiterung

Eigener Stand: Das Dockerfile aus Lab 5.2 (`examples/m05-cloud-integration/l02-container-prep/Dockerfile`) erfüllt A1–A8: Image `python:3.13-slim`, Nicht-Root-Nutzer `app`, keine Secrets in `ENV`, gezieltes `COPY`, gepinnte Abhängigkeiten über `requirements-server.txt`, `HEALTHCHECK`, nur Port 8000. Offene Punkte stehen in `policy.md` (Authentifizierung je Client, Ratenbegrenzung, Freigabe durch eine zweite Person).

Freigabeempfehlung (Beispiel):

```text
Empfehlung: keine Freigabe der Konfiguration in der vorliegenden Form.
Bedingungen: (1) Schlüssel rotiert und zur Laufzeit übergeben, (2) Container als Nicht-Root,
(3) Policy: Rolle aus Server-Konfiguration, deny by default, Schreiben nur mit Bestätigung, im Server durchgesetzt.
Reihenfolge: Befunde 1, 10, 11, 12, 14, danach 2, 3, danach die wichtigen Befunde.
Restrisiko: Bestätigung hängt am Client; gemeinsame Identität je Server-Prozess, bis ein Token je Client eingeführt ist.
Nachprüfung: zweite Person prüft mit derselben Checkliste nach Behebung.
```
