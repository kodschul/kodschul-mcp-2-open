# Lab 4.2: End-to-End-Testlauf

**Leitfragen:**

<details>
<summary>Wo verhält sich der Agent heute noch nicht produktionsreif?</summary>

Das Schreib-Tool `update_ticket_status` ist ohne Rollenprüfung und Bestätigung aufrufbar, der Server schreibt kein Protokoll der Aufrufe, und er läuft nur als lokaler Prozess.

</details>

<details>
<summary>Welche Lücke adressiert Tag 2?</summary>

Alle drei: Container und Orchestrierung (Betrieb), Zugriffskontrolle und Policy (Absicherung), Logging und Alarme (Monitoring).

</details>

- Ein End-to-End-Test läuft vom Nutzertext über das Modell und MCP bis zum Tool und zurück.
- Das Protokoll hält fest, was erwartet war, was passierte und welche Lücke daraus folgt.

## Aufbau eines Testprotokolls

Vorlage: `starters/m04-l02-testrun.md`. Fertiges Beispiel: `examples/m04-agent-prototype/l02-end-to-end-testrun/testdialog.md` mit dem Lauf in `testlauf.log`.

| Abschnitt | Inhalt |
| --- | --- |
| Befehl | genauer Aufruf; echtes LLM mit Modellname oder Skript-Agent (Replay) |
| Testdialog | je Schritt: Eingabe, erwarteter Tool-Call, tatsächlicher Tool-Call, Ergebnis ok? |
| Beobachtungen | Tool-Auswahl, Argumente, Antwortqualität, Dauer; je Zeile eine Bewertung |
| Lücken | was für den produktiven Einsatz fehlt, je Lücke eine Zeile |

## Worauf der Lauf zu lesen ist

| Ausgabezeile | Bedeutung |
| --- | --- |
| `Verbunden mit vantra-ops, Protokoll 2026-07-28` | Verbindung steht, Protokollversion ausgehandelt |
| `Tools: …  ·  LLM: …` | entdeckte Tools und verwendetes Backend (`replay` = Skript-Agent) |
| `→ Tool-Call: name(args)` | Wahl des Modells, mit Argumenten |
| `← ok: …` / `← FEHLER: …` | Ergebnis des Tools; bei Fehler erhält das Modell den Text |
| `Agent: …` | Antwort an den Nutzer |

Bewertung einer Beobachtung: wie erwartet, Auffälligkeit (funktioniert, aber unerwartet) oder Lücke (für den Betrieb zu beheben).

## Kennzeichnung der Läufe

| Lauf | Aussage | Kennzeichnung im Protokoll |
| --- | --- | --- |
| echtes LLM | prüft Tool-Auswahl des Modells; Ergebnis kann schwanken | Modellname, z. B. `qwen3:8b` |
| Replay (`--replay`) | prüft Server, Kontext und Verdrahtung; Tool-Calls sind vorgegeben | „Skript-Agent (Replay)“ |

## Fazit

- Ein Testprotokoll hat vier Teile: Befehl, Testdialog, Beobachtungen, Lücken.
- Replay-Läufe sind reproduzierbar, sagen aber nichts über die Auswahl eines Modells.

Die Übung führt den Dialog „Ticket abfragen, dann Deployment-Log prüfen“ durch und dokumentiert ihn im Protokoll.
