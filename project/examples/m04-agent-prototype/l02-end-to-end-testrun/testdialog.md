# End-to-End-Testlauf (Beispiel zu Lab 4.2)

Server: `examples/m04-agent-prototype/l01-agent-client-connection/server.py` · Client: `shared/agent_client.py`

## Befehl

```bash
# mit echtem LLM laut .env (Ollama oder Cloud)
python shared/agent_client.py --server examples/m04-agent-prototype/l01-agent-client-connection/server.py
# ohne Modell, reproduzierbar (Replay-LLM, im Protokoll als Skript-Agent kennzeichnen)
python shared/agent_client.py --server examples/m04-agent-prototype/l01-agent-client-connection/server.py --replay
```

## Testdialog

| Schritt | Eingabe | Erwarteter Tool-Call | Erwartetes Ergebnis |
| ------- | ------- | -------------------- | ------------------- |
| 1 | `Zeige Ticket VAN-102` | `get_ticket({"ticket_id": "VAN-102"})` | Ticket „Login-Seite lädt nach Release 2.14 sehr langsam“, Status open, Version 3 |
| 2 | `Zeige das Deployment-Log dazu` | `get_deployment_log` (ohne oder mit `ticket_id` VAN-102) | Deployment dep-2041, auth-service 2.14.1, Status degraded |

Schritt 2 funktioniert ohne Nennung der Ticket-ID, weil das Kontextschema aus Lab 3.2 das zuletzt abgefragte Ticket kennt.

## Beobachtungen (Replay-Lauf, Protokoll siehe `testlauf.log`)

| Beobachtung | Bewertung |
| ----------- | --------- |
| Beide Tool-Calls wurden in der erwarteten Reihenfolge ausgeführt | wie erwartet |
| Der Server hat jeden Aufruf ohne Rollenprüfung angenommen, auch `update_ticket_status` stünde offen | Lücke: Absicherung (Tag 2, m07) |
| Es gibt kein Protokoll der Aufrufe auf Serverseite | Lücke: Monitoring (m08) |
| Server läuft nur als lokaler stdio-Prozess | Lücke: Betrieb im Container (m05, m06) |

## Echtes LLM: worauf achten

- Wählt das Modell das passende Tool, und mit welchen Argumenten?
- Wie reagiert es, wenn die Ticket-ID fehlt oder falsch ist?
- Überlappen sich Tool-Beschreibungen so, dass das Modell das falsche Tool nimmt?
