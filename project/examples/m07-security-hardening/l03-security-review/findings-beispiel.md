# Beispielbefunde zur Trainer-Konfiguration (Lab 7.3)

Lösung des Trainers zu `flawed/Dockerfile` und `flawed/policy.md`. Teilnehmende müssen nicht alle Befunde finden; die Einstufung ist Diskussionsgrundlage.

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

Beantwortung der Leitfragen: Blockierend sind die Befunde 1, 2, 3, 10, 11, 12 und 14, weil sie unmittelbar Zugriff oder Rechteausweitung ermöglichen. „Nice to have“ sind die Befunde 9 und 16.
