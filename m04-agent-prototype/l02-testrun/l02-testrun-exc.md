# Lab 4.2 – Übung: End-to-End-Testlauf

**Dauer:** ca. 25 Minuten (Einzel/Paar, kurze Vorstellung im Plenum)
**Ändert die Vantra-Projektbasis?** Ja — das Testprotokoll `playground/testlauf.md` dokumentiert den Prototyp und ist Grundlage für Lab 4.3 und die Planung von Tag 2.
**Arbeitsdatei:** `playground/testlauf.md`
**Starter:** `starters/m04-l02-testrun.md`
**Beispiel zum Vergleich:** `examples/m04-agent-prototype/l02-testrun/` (`testdialog.md`, `testlauf.log`)

## Vorbereitung

- Terminal im Projektordner `output/project/`, virtuelle Umgebung aktiv.
- `playground/server.py` mit `playground/context.py` enthält den Stand aus Lab 4.1. Fehlen sie, kopiere die Dateien aus `examples/m04-agent-prototype/l01-agent-client/`.
- Kopiere den Starter: `cp starters/m04-l02-testrun.md playground/testlauf.md`.

## Aufgaben

1. Fülle den Testdialog (`TODO(Aufgabe 1)`): Trage vor dem Lauf je Schritt den erwarteten Tool-Call ein. Starte danach den Agenten und trage Tool-Call und Ergebnis ein:

   ```bash
   python shared/agent_client.py --server playground/server.py            # echtes LLM laut .env
   python shared/agent_client.py --server playground/server.py --replay   # Skript-Agent (Replay-LLM)
   ```

   Gib bei echtem LLM `Zeige Ticket VAN-102` und `Zeige das Deployment-Log dazu` ein, beende mit einer leeren Zeile. Kennzeichne unter „Verwendeter Agent“, welcher Lauf es war.
2. Notiere mindestens drei Beobachtungen mit Bewertung (`TODO(Aufgabe 2)`): Tool-Auswahl, Argumente, Antwortqualität, Dauer in Sekunden je Antwort.
3. Führe drei Zusatzläufe aus und ergänze die Ergebnisse als Beobachtungen: eine unbekannte Ticket-ID, die Log-Frage ohne vorheriges Ticket (neuer Prozess), ein Schreibwunsch. `--prompt` gibt eine feste Eingabe vor; `--replay workflow` spielt Ticket, Log und `Setze das Ticket auf in_progress` ab:

   ```bash
   python shared/agent_client.py --server playground/server.py --replay --prompt "Zeige Ticket VAN-999"
   python shared/agent_client.py --server playground/server.py --replay --prompt "Zeige das Deployment-Log dazu"
   python shared/agent_client.py --server playground/server.py --replay workflow
   ```

4. Halte die Lücken für Tag 2 fest (`TODO(Aufgabe 4)`): Wo verhält sich der Prototyp nicht produktionsreif? Je Lücke eine Zeile; nenne bei jeder, was passiert ist.
5. Stelle zwei Beobachtungen und die wichtigste Lücke kurz im Plenum vor.

## Checkpoint

- `playground/testlauf.md` enthält einen ausgefüllten Testdialog mit zwei Schritten, mindestens drei Beobachtungen und mindestens drei Lücken.
- Das Protokoll nennt, ob echtes LLM (mit Modellname) oder Skript-Agent lief.
- Die Zusatzläufe sind mit der tatsächlichen Ausgabe (`← FEHLER` bzw. `← ok`) dokumentiert.

## Abschlusskriterien

- Das Protokoll ist ohne Rückfrage nachvollziehbar: Befehl, erwartetes und tatsächliches Ergebnis, Bewertung.
- Jede Lücke ist mit einer beobachteten Tatsache belegt, nicht nur behauptet.

## Erweiterung (optional)

Führe den Dialog zweimal mit dem echten LLM aus und vergleiche beide Läufe: gleiche Tool-Calls, gleiche Argumente, gleiche Antwort? Notiere Abweichungen und vermutete Ursache.

## Fallback

- Ollama langsam oder nicht verfügbar: nur den Replay-Befehl ausführen und im Protokoll „Skript-Agent (Replay)“ eintragen. Beobachtungen zur Tool-Auswahl entfallen dann; Kontext, Fehlertexte und Schreibzugriff bleiben prüfbar.
- Fehlt der Stand aus Lab 4.1, nutze `examples/m04-agent-prototype/l01-agent-client/server.py` als `--server`.
