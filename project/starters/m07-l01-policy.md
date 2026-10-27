# Zugriffsrichtlinie – Starter (Lab 7.1)

Kopieren nach `playground/policy.md` und ausfüllen. Weitere Vorlage: `shared/policy-template.md`. Durchsetzung im Server: `starters/m07-l01-auth.py`.

## Geltungsbereich

- Server: `vantra-ops`
- Tools: `get_ticket`, `get_deployment_log`, `update_ticket_status`
- Durchsetzung: TODO(Aufgabe 1): Wo wird geprüft (Server, Client, Prompt)? Warum dort?

## Grundsätze

TODO(Aufgabe 1): drei Grundsätze formulieren (Least Privilege, Verhalten bei Unbekanntem, Quelle der Rolle).

## Rollen und Tools

TODO(Aufgabe 2): Tabelle ausfüllen. Rollen `viewer` und `operator`; Art je Tool (lesen/schreiben); erlaubt oder verboten; Bedingung.

| Tool | Art | viewer | operator | Bedingung |
| ---- | --- | ------ | -------- | --------- |
| `get_ticket` | | | | |
| `get_deployment_log` | | | | |
| `update_ticket_status` | | | | |

## Bestätigungspflicht

TODO(Aufgabe 3): Welche Tools dürfen nie ohne Bestätigung laufen? Wer bestätigt, über welchen Kanal, und welcher Fehlercode kommt ohne Bestätigung?

## Erkennung eines kompromittierten Clients

TODO(Aufgabe 4): Woran wird ein kompromittierter Client erkannt (Protokollierung, Auffälligkeiten)?

## Offene Punkte

- TODO(Aufgabe 5, Erweiterung): Was ist bewusst noch nicht geregelt?
