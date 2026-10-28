# Zugriffsrichtlinie Vantra Ops Agent

Stand: Beispiel zu Lab 7.1 · Geltungsbereich: MCP-Server `vantra-ops` mit den Tools `get_ticket`, `get_deployment_log`, `update_ticket_status` · Durchsetzung: `auth.py` im Server

## Grundsätze

1. **Least Privilege:** Jede Rolle erhält nur die Tools, die für ihre Aufgabe nötig sind.
2. **Deny by default:** Unbekannte Rollen und nicht gelistete Tools werden abgelehnt.
3. **Durchsetzung im Server:** Der Server prüft jeden Aufruf. Hinweise im Prompt oder Filter im Client gelten nur als zusätzliche Schicht.
4. **Rolle kommt nicht vom Modell:** Die Rolle wird beim Start des Server-Prozesses festgelegt (`VANTRA_ROLE`). Kein Tool-Argument kann sie ändern.
5. **Schreiben nur mit Bestätigung:** Schreibende Tools laufen erst nach ausdrücklicher Zustimmung des Nutzers.

## Rollen und Tools

| Tool | Art | viewer | operator | Bedingung |
| ---- | --- | ------ | -------- | --------- |
| `get_ticket` | lesen | erlaubt | erlaubt | `ticket_id` im Format `VAN-<Zahl>` |
| `get_deployment_log` | lesen | erlaubt | erlaubt | höchstens 100 Zeilen pro Aufruf |
| `update_ticket_status` | schreiben | verboten | erlaubt, nur mit Bestätigung | `expected_version` zwingend (Konflikterkennung), Status aus der festen Liste |

Standardrolle ohne Angabe: `viewer`.

## Bestätigung (Human-in-the-loop)

- Der Agent-Client zeigt vor jedem schreibenden Tool Tool, Ticket und neuen Status und fragt den Nutzer.
- Erst nach „ja“ setzt der **Client** `confirmed=true`. Das Argument wird dem Modell nicht angeboten und aus Modell-Ausgaben entfernt.
- Der Server lehnt schreibende Aufrufe ohne `confirmed=true` mit dem Fehlercode `confirmation_required` ab.

## Fehlercodes

| Code | Bedeutung |
| ---- | --------- |
| `policy_denied` | Rolle darf das Tool nicht aufrufen |
| `confirmation_required` | Schreib-Tool ohne Bestätigung aufgerufen |
| `version_conflict` | Ticket wurde zwischenzeitlich geändert (Lab 3.3) |

## Erkennung eines kompromittierten Clients

- Jeder Aufruf wird protokolliert (Lab 8.1), auch abgelehnte.
- Auffällig sind: mehrere `policy_denied` in kurzer Zeit, Schreib-Tools außerhalb üblicher Zeiten, Aufrufe direkt nach dem Lesen eines Tickets mit Text, der Anweisungen enthält.

## Offene Punkte (bewusst nicht Teil dieses Beispiels)

- Echte Authentifizierung der Clients (Token, OAuth) beim HTTP-Transport; im Beispiel gilt die Rolle des Server-Prozesses für alle Verbindungen.
- Ratenbegrenzung pro Client.
- Freigabe durch eine zweite Person bei kritischen Services.
