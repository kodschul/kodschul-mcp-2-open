# Security-Cheatsheet (Modul 7)

Pfade relativ zu `output/project/`. Alle Befehle im Projektordner mit aktiver virtueller Umgebung.

## Rollen und Tools (Stand Lab 7.1)

| Tool | Art | viewer | operator |
| --- | --- | --- | --- |
| `get_ticket` | lesen | erlaubt | erlaubt |
| `get_deployment_log` | lesen | erlaubt | erlaubt |
| `update_ticket_status` | schreiben | verboten | erlaubt, nur mit `confirmed=true` |

Standardrolle: `viewer`. Unbekannte Rolle oder unbekanntes Tool: `policy_denied`.

## Fehlercodes

| Code | Ursache | Behebung |
| --- | --- | --- |
| `policy_denied` | Rolle darf das Tool nicht aufrufen | Rolle des Servers prüfen (`VANTRA_ROLE`), Policy anpassen |
| `confirmation_required` | Schreib-Tool ohne `confirmed=true` | Nutzer fragen, Client setzt `confirmed` |
| `version_conflict` | Ticket zwischenzeitlich geändert | neu lesen (`get_ticket`), mit neuer `expected_version` wiederholen |
| `invalid_status` | Status nicht in `open, in_progress, resolved, closed` | gültigen Status wählen |
| Validierungsfehler `String should match pattern '^VAN-\d{1,6}$'` | ungültige `ticket_id` | Format `VAN-<Zahl>` |

## Befehle

| Befehl | Wirkung |
| --- | --- |
| `VANTRA_ROLE=operator python playground/server.py` | Server mit Rolle `operator` starten |
| `python shared/script_client.py --server playground/server.py --role operator --call update_ticket_status '{"ticket_id": "VAN-101", "status": "closed", "expected_version": 1}'` | Schreibaufruf mit Rolle `operator` ohne Bestätigung |
| dasselbe mit `"confirmed": true` im JSON | Schreibaufruf mit Bestätigung |
| `python shared/agent_client.py --server <Server> --replay injection --confirm none` | Showcase C: Injection-Ablauf ohne Bestätigung |
| `--role viewer` / `--role operator` | Rolle des lokalen Servers wählen (ab Lab 7.1) |
| `--confirm ask` / `yes` / `no` / `none` | Bestätigung im Agent-Client: Nutzer fragen / automatisch ja / automatisch nein (Client meldet `user_declined`, kein Serveraufruf) / `confirmed` nie senden (der Server entscheidet) |

`confirmed` sieht das Modell nie: `shared/agent_client.py` entfernt es aus dem Tool-Schema (`HIDDEN_ARGS`) und aus jedem Tool-Call des Modells; erst nach Zustimmung setzt der Host `confirmed=true`.

Server für Showcase C: ohne Policy `examples/m03-context-and-state/l03-multi-agent/server.py`, mit Policy `examples/m07-security-hardening/l01-access-control/server.py`.

## Aufbau einer Zugriffsrichtlinie

| Abschnitt | Inhalt |
| --- | --- |
| Geltungsbereich | Server, Tools, Ort der Durchsetzung |
| Grundsätze | Least Privilege, deny by default, Rolle nicht vom Modell |
| Rollen und Tools | Tabelle Tool · Art · Rolle · Bedingung |
| Bestätigungspflicht | betroffene Tools, Kanal, Fehlercode |
| Erkennung und Reaktion | Protokoll, Auffälligkeiten, Reaktion |
| Offene Punkte | bewusst nicht Geregeltes |

Vorlage: `shared/policy-template.md`. Beispiel: `examples/m07-security-hardening/l01-access-control/policy.md`.

## Angriffe und Verteidigungslinien

| Angriff | Merkmal | Linie | Maßnahme |
| --- | --- | --- | --- |
| Prompt Injection im Tool-Ergebnis | Anweisung im Datenfeld, Adressierung an KI, Schreibaufruf, Verschweigen | Server | Rolle, Allow-List, Bestätigungspflicht |
| Tool-Spoofing | Namenskollision, Anweisungen in der Beschreibung, zusätzlicher Parameter | Client / Policy | geprüfte Server, Tool-Liste lesen, Änderungen melden lassen |
| Rechteausweitung | Aufforderung zu Massenänderung oder Rollenwechsel | Server / Policy | Rolle nur aus Prozessumgebung, Bestätigung je Aufruf |
| alle | Versuch bleibt unbemerkt | Betrieb | Protokoll, Alarm (Lab 8.1) |

Linien: 1 Modell/Prompt (probabilistisch) · 2 Client (Bestätigung, Tool-Prüfung) · 3 Server (Allow-List, Validierung) · 4 Policy/Betrieb (Standardrolle, Protokoll, Alarm).

## Sandbox-Härtung

| Maßnahme | Umsetzung |
| --- | --- |
| Eingabe prüfen | `Annotated[str, Field(pattern=r"^VAN-\d{1,6}$")]` |
| Ausgabe begrenzen | `deployment["log"][-max(1, min(tail, 100)):]` |
| Nicht-Root | `RUN useradd --system --uid 10001 --no-create-home app` und `USER app` |
| nur `/data` beschreibbar | `mkdir /data && chown app:app /data`; Kubernetes `readOnlyRootFilesystem: true` |
| Konfiguration zur Laufzeit | `ENV`-Variablen ohne Werte für Secrets; Kubernetes `secretKeyRef` |

## Review-Schweregrade

| Schwere | Kriterium | Folge |
| --- | --- | --- |
| blockierend | unmittelbar Zugriff, Rechteausweitung, Secret-Offenlegung | keine Freigabe |
| wichtig | erhöhtes Risiko | beheben oder bewusst akzeptieren |
| nice to have | Verbesserung ohne akutes Risiko | Backlog |

Checkliste: `examples/m07-security-hardening/l03-security-review/checklist.md` (A Dockerfile, B Policy, C Server). Ergebnis je Punkt: ✔ · ✘ · ?.

## MCP-Autorisierung (Stand: 27.10.2026)

| Aussage | Quelle |
| --- | --- |
| optional, auf Transportebene; HTTP: OAuth-2.1-basiert (SHOULD), stdio: Zugangsdaten aus der Umgebung | Spezifikation 2026-07-28, Authorization |
| MCP-Server = Resource Server, muss Protected Resource Metadata (RFC 9728) bereitstellen | ebenda |
| Token Passthrough ist ein Anti-Pattern: Tokens nur akzeptieren, die für den Server ausgestellt sind | Security Best Practices |
| Tool-Definitionen sind nicht vertrauenswürdige Eingabe | Local Server Security |

URLs und Abrufdatum: Theorie Lab 7.1 und Lab 7.2 (abgerufen am 27.10.2026). Im Projekt nicht umgesetzt: OAuth, Token je Client, Ratenbegrenzung.
