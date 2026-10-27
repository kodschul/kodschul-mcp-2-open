# Lab 7.1 – Lösung: Zugriffsrichtlinie schreiben und im Server durchsetzen

Vollständige Dateien: `examples/m07-security-hardening/l01-access-control-sandboxing/` (`policy.md`, `auth.py`, `server.py`).

## Teil A: Policy

### A1: Geltungsbereich und Grundsätze

```markdown
## Geltungsbereich

- Server: `vantra-ops`
- Tools: `get_ticket`, `get_deployment_log`, `update_ticket_status`
- Durchsetzung: im Server (`auth.py`), weil nur der Server jeden Aufruf sieht und sich nicht vom Modell
  oder Client umgehen lässt. Prompt-Hinweise und Client-Filter sind zusätzliche Schichten.

## Grundsätze

1. **Least Privilege:** Jede Rolle erhält nur die Tools, die für ihre Aufgabe nötig sind.
2. **Deny by default:** Unbekannte Rollen und nicht gelistete Tools werden abgelehnt.
3. **Rolle kommt nicht vom Modell:** Die Rolle wird beim Start des Server-Prozesses festgelegt (`VANTRA_ROLE`).
   Kein Tool-Argument kann sie ändern.
```

### A2: Rollen und Tools

| Tool | Art | viewer | operator | Bedingung |
| ---- | --- | ------ | -------- | --------- |
| `get_ticket` | lesen | erlaubt | erlaubt | `ticket_id` im Format `VAN-<Zahl>` |
| `get_deployment_log` | lesen | erlaubt | erlaubt | höchstens 100 Zeilen pro Aufruf |
| `update_ticket_status` | schreiben | verboten | erlaubt, nur mit Bestätigung | `expected_version` zwingend, Status aus fester Liste |

Standardrolle ohne Angabe: `viewer`. Grund: Fehlt die Konfiguration, soll der Server nur lesen.

### A3: Bestätigungspflicht

- Betroffen: `update_ticket_status` (jedes schreibende Tool).
- Bestätigt der Nutzer, über den Agent-Client: Er zeigt Tool, Ticket und neuen Status und fragt. Erst nach „ja“ setzt der Client `confirmed=true`; das Argument wird dem Modell nicht angeboten.
- Ohne Bestätigung lehnt der Server mit `confirmation_required` ab.

### A4: Erkennung eines kompromittierten Clients

- Jeder Aufruf wird protokolliert (Lab 8.1), auch abgelehnte.
- Auffällig: mehrere `policy_denied` in kurzer Zeit, Schreib-Tools außerhalb üblicher Zeiten, Aufrufe direkt nach dem Lesen eines Tickets mit Text, der Anweisungen enthält.

## Teil B: Durchsetzung

### B1–B3: `auth.py`

```python
ROLE_TOOLS: dict[str, frozenset[str]] = {
    "viewer": frozenset({"get_ticket", "get_deployment_log"}),
    "operator": frozenset({"get_ticket", "get_deployment_log", "update_ticket_status"}),   # B1
}

def authorize(tool: str, confirmed: bool = False, role: str | None = None) -> str:
    """Prüft einen Tool-Aufruf; gibt die Rolle zurück oder wirft PolicyDenied."""
    role = role or current_role()
    if tool not in ROLE_TOOLS.get(role, frozenset()):                                      # B2
        raise PolicyDenied("policy_denied", f"Rolle '{role}' darf das Tool '{tool}' nicht aufrufen.", role=role, tool=tool)
    if tool in WRITE_TOOLS and not confirmed:                                              # B3
        raise PolicyDenied(
            "confirmation_required",
            f"Das Schreib-Tool '{tool}' braucht eine Bestätigung durch den Nutzer (confirmed=true).",
            role=role,
            tool=tool,
        )
    return role
```

Der Zugriff `ROLE_TOOLS.get(role, frozenset())` lehnt unbekannte Rollen ab (deny by default), ohne eine eigene Prüfung.

### B4–B6: `server.py`

```python
from auth import PolicyDenied, authorize                                  # B4

@mcp.tool(annotations=READ_ONLY)
def get_ticket(ticket_id: str) -> Any:
    session.tool_calls += 1
    try:
        authorize("get_ticket")                                           # B5: zuerst prüfen
        ticket = backend.get_ticket(ticket_id)
    except PolicyDenied as exc:
        return error_result(exc.code, exc.message, **exc.details)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    ...

@mcp.tool(annotations=WRITE)
def update_ticket_status(ticket_id: str, status: str, expected_version: int, confirmed: bool = False) -> Any:   # B6
    session.tool_calls += 1
    try:
        authorize("update_ticket_status", confirmed=confirmed)            # B5: Schreib-Tool mit confirmed
        ticket = backend.update_ticket(ticket_id, status, expected_version)
    except PolicyDenied as exc:
        return error_result(exc.code, exc.message, **exc.details)
    ...
```

`get_deployment_log` erhält denselben Aufbau mit `authorize("get_deployment_log")` vor dem Auflösen der Ticket-ID. Die Resource `tickets://{ticket_id}` ruft `authorize("get_ticket")` und übersetzt `PolicyDenied` in `ResourceNotFoundError(exc.message)`, damit die Resource nicht an der Tool-Prüfung vorbei Daten liefert.

### B7: Aufrufe prüfen

Rolle `viewer`:

```text
is_error=True
{"error": "policy_denied", "message": "Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.", "role": "viewer", "tool": "update_ticket_status"}
```

Rolle `operator` ohne `confirmed`:

```text
is_error=True
{"error": "confirmation_required", "message": "Das Schreib-Tool 'update_ticket_status' braucht eine Bestätigung durch den Nutzer (confirmed=true).", "role": "operator", "tool": "update_ticket_status"}
```

Rolle `operator` mit `"confirmed": true`:

```text
is_error=False
{ "id": "VAN-101", "title": "Passwort-Reset-Mail kommt nicht an", "status": "closed", ..., "version": 2, ... }
```

| Rolle | `confirmed` | Ergebnis |
| --- | --- | --- |
| `viewer` | – | `policy_denied` |
| `operator` | nein | `confirmation_required` |
| `operator` | ja | Ticket geändert, `version` +1 |

Der Aufruf ändert den Zustand von VAN-101 nur im Prozess des Skript-Clients; ein neuer Start setzt die Daten zurück.

## Erweiterung

### Code: Eingabevalidierung und Obergrenze

```python
from typing import Annotated
from pydantic import Field

TicketId = Annotated[str, Field(pattern=r"^VAN-\d{1,6}$", description="Ticket-ID im Format VAN-<Zahl>, z. B. VAN-102")]
MAX_LOG_LINES = 100

def get_ticket(ticket_id: TicketId) -> Any: ...
def get_deployment_log(ticket_id: TicketId | None = None, tail: int = 20) -> Any:
    ...
    lines = deployment["log"][-max(1, min(tail, MAX_LOG_LINES)):]
```

Ergebnis für `../etc/passwd`: `Error executing tool get_ticket: 1 validation error … String should match pattern '^VAN-\d{1,6}$'`, `is_error=True`. Mit `"tail": 500` kommen höchstens 100 Zeilen zurück (VAN-102 hat sechs).

### A5: Offene Punkte (Beispiel)

- Echte Authentifizierung der Clients (Token, OAuth) beim HTTP-Transport; im Beispiel gilt die Rolle des Server-Prozesses für alle Verbindungen.
- Ratenbegrenzung pro Client.
- Freigabe durch eine zweite Person bei kritischen Services.

### Entscheidung: Client-Identität bei HTTP (Beispiel)

| Option | Aufwand | Aufrufe zuordenbar | Risiko |
| --- | --- | --- | --- |
| Rolle je Server-Prozess (heutiger Stand) | gering | nein, alle Clients teilen die Rolle | hoch bei mehreren Clients |
| Token je Client (OAuth nach Spezifikation, Server als Resource Server) | mittel bis hoch | ja | Token-Verwaltung, Audience-Prüfung nötig |
| Gateway vor dem Server | mittel | ja, am Gateway | zusätzliche Komponente im Betrieb |

Entscheidung (Beispiel): Für den Prototyp bleibt die Rolle je Prozess, ein Server je Rolle. Vor einem Mehr-Client-Betrieb wird ein Token je Client mit Prüfung des Audience-Werts eingeführt. Begründung: Ohne Identität je Client ist der Alarm aus Lab 8.1 nicht einem Client zuordenbar.
