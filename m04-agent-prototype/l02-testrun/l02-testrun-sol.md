# Lab 4.2 – Lösung: End-to-End-Testlauf

Fertiges Beispiel: `examples/m04-agent-prototype/l02-testrun/testdialog.md` und `testlauf.log`. Die Ergebnisse unten stammen aus Replay-Läufen (Skript-Agent); Läufe mit echtem LLM können abweichen.

## Aufgabe 1: Testdialog

Verwendeter Agent: Skript-Agent (Replay).

| Schritt | Eingabe | Erwarteter Tool-Call | Tatsächlicher Tool-Call | Ergebnis ok? |
| ------- | ------- | -------------------- | ----------------------- | ------------ |
| 1 | `Zeige Ticket VAN-102` | `get_ticket({"ticket_id": "VAN-102"})` | `get_ticket({"ticket_id": "VAN-102"})` | ja: Ticket „Login-Seite lädt nach Release 2.14 sehr langsam“, Status open, Version 3 |
| 2 | `Zeige das Deployment-Log dazu` | `get_deployment_log` (ohne oder mit `ticket_id` `VAN-102`) | `get_deployment_log({})` | ja: `dep-2041`, auth-service 2.14.1, Status degraded |

Lauf (`testlauf.log`):

```text
Verbunden mit vantra-ops, Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log, update_ticket_status  ·  LLM: replay

Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam",   "status": "open",   "priority": "high",   "assignee": "jonas.brandt",   "se…
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).

Nutzer: Zeige das Deployment-Log dazu
  → Tool-Call: get_deployment_log({})
  ← ok: {   "id": "dep-2041",   "ticket_id": "VAN-102",   "service": "auth-service",   "version": "2.14.1",   "environment": "production",   "status": "degraded",   "lo…
Agent: Deployment dep-2041 (auth-service 2.14.1, Status degraded). Letzte Zeilen: auth      token cache disabled by config key AUTH_CACHE_TTL=0;  deploy    finished with warnings, rollback not triggered
```

Schritt 2 funktioniert ohne ID, weil das Kontextschema aus Lab 3.2 das zuletzt abgefragte Ticket kennt.

## Aufgabe 2: Beobachtungen

| Beobachtung | Bewertung |
| ----------- | --------- |
| Beide Tool-Calls liefen in der erwarteten Reihenfolge | wie erwartet |
| Schritt 2 trägt keine `ticket_id` und liefert trotzdem das Deployment zu `VAN-102` | wie erwartet (Kontext) |
| Antwort des Skript-Agenten nennt Deployment, Status und nur die letzten zwei Log-Zeilen, nicht die Warnung `connection pool exhausted: 50/50 in use` | Auffälligkeit: Die Antwort verkürzt das Log; das vollständige Ergebnis steht im Tool-Aufruf |

Bei echtem LLM zusätzlich: gewählte Tools und Argumente, Dauer je Antwort in Sekunden (über 60 Sekunden: Auffälligkeit „zu langsam für den Dialog“), Abweichungen zwischen Läufen. Replay antwortet ohne messbare Wartezeit.

## Aufgabe 3: Zusatzläufe

Unbekannte Ticket-ID:

```text
Nutzer: Zeige Ticket VAN-999
  → Tool-Call: get_ticket({"ticket_id": "VAN-999"})
  ← FEHLER: Error executing tool get_ticket: Ticket VAN-999 nicht gefunden
Agent: Der Aufruf war nicht erfolgreich: FEHLER: Error executing tool get_ticket: Ticket VAN-999 nicht gefunden
```

Log-Frage im neuen Prozess:

```text
Nutzer: Zeige das Deployment-Log dazu
  → Tool-Call: get_deployment_log({})
  ← FEHLER: Error executing tool get_deployment_log: Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.
Agent: Der Aufruf war nicht erfolgreich: FEHLER: Error executing tool get_deployment_log: Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.
```

Schreibwunsch (`--replay workflow`, dritter Schritt):

```text
Nutzer: Setze das Ticket auf in_progress
  → Tool-Call: update_ticket_status({"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam",   "status": "in_progress",   "priority": "high",   "assignee": "jonas.brandt"…
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status in_progress, Version 4).
```

Zusätzliche Beobachtungen:

| Beobachtung | Bewertung |
| ----------- | --------- |
| Unbekannte ID: sauberer Fehlertext, der Agent meldet ihn weiter | wie erwartet |
| Log-Frage ohne Vorgänger-Ticket: klare Anweisung „zuerst get_ticket aufrufen“; Kontext ist pro Prozess | wie erwartet (Grenze: kein Memory) |
| Schreibwunsch wird ohne Rolle, Bestätigung oder Rückfrage ausgeführt (Version 3 → 4) | Lücke: Absicherung |

## Aufgabe 4: Lücken für Tag 2

| Lücke | Beleg | Adressiert in |
| ----- | ----- | ------------- |
| Kein Zugriffsschutz: jeder Aufruf wird angenommen, auch Schreiben | `update_ticket_status` lief ohne Prüfung (Aufgabe 3) | Absicherung (Modul 7) |
| Kein Protokoll der Aufrufe auf Serverseite | Ausgaben nur im Client-Terminal | Monitoring (Modul 8) |
| Nur lokaler stdio-Prozess, kein Betrieb als Dienst | Server startet als Kindprozess des Clients | Container und Betrieb (Module 5 und 6) |
| Kontext geht beim Neustart verloren | Log-Frage im neuen Prozess scheitert | Memory/Persistenz, bewusst offen |

## Aufgabe 5: Plenum

Die Vorstellung nutzt die Tabellen aus Aufgabe 2 bis 4: zwei Beobachtungen (z. B. Kontext funktioniert, Schreibzugriff ungeschützt) und die Lücke mit dem größten Schaden.

## Erweiterung

Vergleich zweier Läufe mit echtem LLM: Tool-Calls, Argumente und Antworttext werden nebeneinander eingetragen. Das Ergebnis hängt vom Modell ab und wird mit der eigenen Beobachtung festgehalten, nicht vorausgesetzt.
