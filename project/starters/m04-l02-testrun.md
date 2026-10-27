# Testlauf – Starter (Lab 4.2)

Kopieren nach `playground/testlauf.md` und ausfüllen. Server: eigener Stand aus Lab 4.1 (`playground/server.py`).

## Befehl

```bash
python shared/agent_client.py --server playground/server.py            # echtes LLM laut .env
python shared/agent_client.py --server playground/server.py --replay   # Skript-Agent (Replay-LLM)
```

Verwendeter Agent (zutreffendes behalten): echtes LLM `<Modellname>` · Skript-Agent (Replay)

## Testdialog

| Schritt | Eingabe | Erwarteter Tool-Call | Tatsächlicher Tool-Call | Ergebnis ok? |
| ------- | ------- | -------------------- | ----------------------- | ------------ |
| 1 | `Zeige Ticket VAN-102` | TODO(Aufgabe 1): erwarteten Tool-Call mit Argumenten eintragen | | |
| 2 | `Zeige das Deployment-Log dazu` | TODO(Aufgabe 1): erwarteten Tool-Call eintragen | | |

## Beobachtungen

TODO(Aufgabe 2): mindestens drei Beobachtungen zum Verhalten notieren (Tool-Auswahl, Argumente, Antwortqualität, Dauer).

| Beobachtung | Bewertung (wie erwartet / Auffälligkeit / Lücke) |
| ----------- | ------------------------------------------------ |
| | |

## Lücken für Tag 2

TODO(Aufgabe 3): Wo verhält sich der Prototyp noch nicht produktionsreif? Je Lücke eine Zeile.
