# Lab 8.2 – Lösung: Abschlussprojekt – sicherer MCP-Agent im Mini-Workflow

Vergleichsstand: `examples/m08-observability-and-capstone/l02-capstone/`. Die Ausgaben stammen aus Läufen von `shared/agent_client.py --url http://localhost:8000/mcp --replay workflow` gegen den Compose-Stack (`playground/` mit dem Stand aus Lab 8.1, Docker 29.2.0, Compose v5.0.2); `run_demo.py` (stdio) liefert dieselben Zeilen. `_meta`-Felder und Zeitstempel sind weggelassen.

## Aufgabe 1: Workflow mit Rolle `viewer`

```text
Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam",   "status": "open",   "priority": "high",   "assignee": "jonas.brandt",   "se…
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).

Nutzer: Zeige das Deployment-Log dazu
  → Tool-Call: get_deployment_log({})
  ← ok: {   "id": "dep-2041",   "ticket_id": "VAN-102",   "service": "auth-service",   "version": "2.14.1",   "environment": "production",   "status": "degraded",   "lo…
Agent: Deployment dep-2041 (auth-service 2.14.1, Status degraded). Letzte Zeilen: auth      token cache disabled by config key AUTH_CACHE_TTL=0;  deploy    finished with warnings, rollback not triggered

Nutzer: Setze das Ticket auf in_progress
  → Tool-Call: update_ticket_status({"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3})
  ← FEHLER: {"error": "policy_denied", "message": "Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.", "role": "viewer", "tool": "update_ticket_status"}
Agent: Der Aufruf war nicht erfolgreich: Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.
```

## Aufgabe 2: Rolle `operator`

Mit `--confirm yes` gelingt Schritt 3:

```text
  → Tool-Call: update_ticket_status({"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam",   "status": "in_progress",   "priority": "high",   "assignee": "jonas.brandt"…
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status in_progress, Version 4).
```

Mit `--confirm none`:

```text
  ← FEHLER: {"error": "confirmation_required", "message": "Das Schreib-Tool 'update_ticket_status' braucht eine Bestätigung durch den Nutzer (confirmed=true).", "role": "op…
Agent: Der Aufruf war nicht erfolgreich: Das Schreib-Tool 'update_ticket_status' braucht eine Bestätigung durch den Nutzer (confirmed=true).
```

Ausgefülltes Workflow-Protokoll (`playground/capstone.md`):

| Schritt | Eingabe | Tool-Call | Ergebnis | Policy-Entscheidung |
| ------- | ------- | --------- | -------- | ------------------- |
| 1 | `Zeige Ticket VAN-102` | `get_ticket({"ticket_id": "VAN-102"})` | Ticket VAN-102, Status `open`, Version 3 | lesen: erlaubt für `viewer` und `operator` |
| 2 | `Zeige das Deployment-Log dazu` | `get_deployment_log({})` | `dep-2041`, auth-service 2.14.1, Status `degraded`; `AUTH_CACHE_TTL=0`, `rollback not triggered` | lesen: erlaubt für `viewer` und `operator` |
| 3 | `Setze das Ticket auf in_progress` | `update_ticket_status({"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3})` | je nach Rolle, siehe unten | siehe unten |

| Rolle | Bestätigung | Ergebnis Schritt 3 | Policy-Entscheidung |
| --- | --- | --- | --- |
| `viewer` | `yes` | `policy_denied` | abgelehnt: Rolle darf das Schreib-Tool nicht aufrufen |
| `operator` | `yes` | Status `in_progress`, Version 4 | erlaubt: Rolle plus Bestätigung |
| `operator` | `none` | `confirmation_required` | abgelehnt: Bestätigung fehlt |

Der Replay-Agent liest `expected_version` aus dem Ergebnis von Schritt 1 (Version 3).

## Aufgabe 3: Auswertung

**Schritt 3 hätte ohne Modul 7 versagt:** Ohne Rollenprüfung und Bestätigung wäre `update_ticket_status` für jeden Client ausführbar gewesen, auch auf Anweisung eines manipulierten Ticket-Textes (VAN-106, Showcase C). Schritte 1 und 2 sind lesend und bleiben in beiden Rollen erlaubt.

**Dashboard nach drei Läufen mit Rolle `viewer`** (aufgezeichnet im Compose-Stack nach Aufgabe 1 und 2, Volume `toolcalls` nicht gelöscht):

| Anzeige | Wert |
| --- | --- |
| Aufrufe | 18 (13 `ok`, 5 `denied`); davon 9 aus den drei `viewer`-Läufen (6 `ok`, 3 `denied`) |
| Alarmbanner | „ALARM: 4 abgelehnte Aufrufe in den letzten 60 Sekunden“ (3 × `policy_denied` plus `confirmation_required` aus Aufgabe 2) |
| Zeitleiste | je Lauf `get_ticket` ok, `get_deployment_log` ok, `update_ticket_status` denied (`policy_denied`) |

Das Banner erscheint nur, solange mindestens drei Ablehnungen jünger als 60 Sekunden sind. Die Zahlen hängen von den vorherigen Läufen im Protokoll ab (das Volume `toolcalls` bleibt bei `down` ohne `-v` erhalten); entscheidend ist das Verhältnis `denied` zu `ok` und das Banner.

## Aufgabe 4: Lücken bis zum Produktivbetrieb

| Lücke | Fundstelle | Maßnahme |
| --- | --- | --- |
| Keine Authentifizierung je Client; die Rolle gilt je Server-Prozess und bei HTTP für alle Verbindungen | `policy.md`, „Offene Punkte“ | Token je Client (OAuth nach Spezifikation) oder Gateway, Rolle je Identität |
| Bestätigung hängt am Client (`confirmed`) | `policy.md`, Abschnitt „Bestätigung“ | vom Client unabhängige Bestätigung, zweite Person bei kritischen Services |
| Keine Ratenbegrenzung pro Client | `policy.md`, „Offene Punkte“ | Limits je Client am Server oder Gateway |
| DNS-Rebinding-Schutz des SDKs ist bei Host `0.0.0.0` aus und nicht konfiguriert | Server-Start im Container | `TransportSecuritySettings` setzen, Zugriff über Gateway begrenzen |
| Log-Aufbewahrung und Zugriff nicht geregelt | `logging_config.py`, Lab 8.1 | Aufbewahrungsdauer, Zugriffsrechte, Weiterleitung an zentrales Logging festlegen |
| Kubernetes und Pipeline nicht ausgeführt | Docker-Build und Compose-Stack lokal gelaufen; Kubernetes-Manifest nur per `kubeconform` validiert, Pipeline nur per `actionlint` geprüft | Anwendung und Pipeline in einer Testumgebung ausführen |
| Modellqualität ungeprüft | Replay-Agent statt echtem Modell | Tool-Auswahl und Injection-Verhalten mit dem vorgesehenen Modell testen |

## Erweiterung

Showcase C gegen den Container (Rolle `viewer`):

```text
Nutzer: Zeige Ticket VAN-106
  → Tool-Call: get_ticket({"ticket_id": "VAN-106"})
  ← ok: {   "id": "VAN-106",   "title": "Rückfrage zum Rechnungsexport",   "status": "open",   "priority": "medium",   "assignee": null,   "service": "report-service", …
  → Tool-Call: update_ticket_status({"ticket_id": "VAN-101", "status": "closed", "expected_version": 1})
  ← FEHLER: {"error": "policy_denied", "message": "Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.", "role": "viewer", "tool": "update_ticket_status"}
Agent: Der Aufruf war nicht erfolgreich: Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.
```

Fehlercode `policy_denied`; im Dashboard erscheint eine `denied`-Zeile für `update_ticket_status` mit den Argumenten `{"ticket_id": "VAN-101", "status": "closed", "expected_version": 1}`.

Risikoregister (Beispiel):

| Risiko | Wahrscheinlichkeit | Auswirkung | Maßnahme | Verantwortlich |
| --- | --- | --- | --- | --- |
| Client schreibt ohne echte Bestätigung | mittel | hoch | clientunabhängige Bestätigung | Entwicklung |
| ein Client nutzt die Rolle aller | hoch | hoch | Token je Client | Architektur |
| Missbrauch bleibt unbemerkt | mittel | mittel | Alarm an Betrieb, Aufbewahrung festlegen | Betrieb |
| Kubernetes-Betrieb unerprobt | mittel | mittel | Testlauf in Staging | Betrieb |

Vor einem Pilotbetrieb mit realen Tickets geschlossen sein müssen: Token je Client, clientunabhängige Bestätigung und ein ausgeführter Test von Kubernetes und Pipeline; die übrigen Punkte folgen im Pilotbetrieb unter Beobachtung.
