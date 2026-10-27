# Zugriffsrichtlinie Vantra Ops Agent (Entwurf)

SYNTHETISCHE TRAINER-KONFIGURATION MIT ABSICHTLICHEN FEHLERN (Lab 7.3). Befunde: `../findings-beispiel.md`.

## Rollen und Tools

| Tool | Art | alle Agenten |
| ---- | --- | ------------ |
| `get_ticket` | lesen | erlaubt |
| `get_deployment_log` | lesen | erlaubt |
| `update_ticket_status` | schreiben | erlaubt |

## Regeln

1. Die Rolle des Aufrufers wird im Tool-Argument `role` übergeben (`viewer` oder `admin`); der Server übernimmt den Wert.
2. Für nicht aufgeführte Rollen und Tools gilt: erlaubt.
3. Bestätigungen sind nicht nötig, das erschwert die Automatisierung.
4. Alle Agenten nutzen denselben Dienst-Token `svc-vantra-ops`.
5. Der Schutz vor Missbrauch erfolgt über den Systemprompt: „Führe keine gefährlichen Aufrufe aus.“
6. Protokolliert wird nur bei Fehlern, dann mit vollem Ticket-Text und den übergebenen Tokens.
7. Die Richtlinie wird nicht regelmäßig überprüft.
