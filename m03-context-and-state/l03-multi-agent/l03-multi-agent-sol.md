# Lab 3.3 – Lösung: Zwei Agenten, ein Kontext

Vollständiger Stand: `examples/m03-context-and-state/l03-multi-agent/server.py`.

## Vorbereitung: Ist-Zustand (Starter, stilles Überschreiben, optional)

Dieselbe Ausgabe steht in der Theorie. Ausgabe von Terminal 3 (Agent B, gekürzt) und Terminal 2 (Agent A, gekürzt):

```text
[agent-b] gelesen: VAN-102 Status=open Version=3
[agent-b] update_ticket_status({'ticket_id': 'VAN-102', 'status': 'in_progress'}) -> ok: {   "id": "VAN-102", ...
[agent-a] gelesen: VAN-102 Status=open Version=3
[agent-a] überlegt 10.0 s ...
[agent-a] update_ticket_status({'ticket_id': 'VAN-102', 'status': 'resolved'}) -> ok: {   "id": "VAN-102", ... "status": "resolved", ...
```

Am Ende steht `VAN-102` auf `resolved`, Version 5. Agent A erhält `ok`; die Änderung von Agent B ist ohne Meldung überschrieben. Der Starter-Server hat kein Argument `expected_version`, daher sendet `second_client.py` keine Version mit.

## Aufgabe 1: Parameter `expected_version`

```python
@mcp.tool(annotations=WRITE)
def update_ticket_status(ticket_id: str, status: str, expected_version: int) -> Any:
    """Ticket-Status ändern (open, in_progress, resolved, closed). expected_version ist die zuvor gelesene Version des Tickets."""
```

Der Docstring ist die Tool-Beschreibung für das Modell: Er sagt, woher die Version stammt.

## Aufgabe 2: Version an das Backend geben

```python
ticket = backend.update_ticket(ticket_id, status, expected_version)
```

## Aufgabe 3: Konflikt abfangen

```python
except VersionConflict as exc:
    return error_result(
        "version_conflict",
        f"Ticket {ticket_id} wurde zwischenzeitlich geändert. Neu lesen mit get_ticket und erneut versuchen.",
        ticket_id=ticket_id,
        expected_version=exc.expected,
        current_version=exc.current,
    )
```

Der Fehler ist ein Tool-Ergebnis mit `is_error=True` (nicht `ToolError`), damit er strukturiert und maschinenlesbar bleibt: `structured_content` und Text sind identisch. Der Block steht direkt nach `except InvalidStatus` und vor `session.remember_ticket(ticket)`.

## Aufgabe 4: Konflikt auslösen

Terminal 2, Agent A (liest Version 3, wartet):

```text
[agent-a] gelesen: VAN-102 Status=open Version=3
[agent-a] überlegt 10.0 s ...
[agent-a] update_ticket_status({'ticket_id': 'VAN-102', 'status': 'resolved', 'expected_version': 3}) -> FEHLER: {"error": "version_conflict", "message": "Ticket VAN-102 wurde zwischenzeitlich geändert. Neu lesen mit get_ticket und erneut versuchen.", "ticket_id": "VAN-102", "expected_version": 3, "current_version": 4}
```

Terminal 3, Agent B:

```text
[agent-b] gelesen: VAN-102 Status=open Version=3
[agent-b] update_ticket_status({'ticket_id': 'VAN-102', 'status': 'in_progress', 'expected_version': 3}) -> ok: {   "id": "VAN-102", ... "version": 4, ...
```

## Aufgabe 5: Endstand vergleichen

`curl localhost:8001/tickets/VAN-102` zeigt `"status": "in_progress"` und `"version": 4`.

Der Unterschied zum Ist-Zustand: Der Starter meldete `ok` und überschrieb; der fertige Server meldet den Konflikt, das Ticket bleibt `in_progress` (Version 4). Ein Agent kann nun neu lesen und bewusst entscheiden.

## Erweiterung: Zusammenführungsstrategie

Im `except VersionConflict`-Zweig vor dem Fehler: aktuelles Ticket laden und bei gleichem Zielstatus als Erfolg behandeln.

```python
except VersionConflict as exc:
    current = backend.get_ticket(ticket_id)
    if current["status"] == status:          # Ziel ist schon erreicht (idempotent)
        session.remember_ticket(current)
        return current
    return error_result("version_conflict", ...)   # wie in Aufgabe 3
```

Geprüfte Ergebnisse (beide Agenten, Agent A hält 6 Sekunden):

| Fall | Agent B | Agent A |
| --- | --- | --- |
| beide setzen `in_progress` | `ok` | `ok` (Ticket unverändert, Version 4) |
| B setzt `in_progress`, A setzt `resolved` | `ok` | `FEHLER` mit `version_conflict` (`expected_version` 3, `current_version` 4) |

Diese Variante ist eine Erweiterung und nicht im Beispielordner enthalten; der Beispielserver meldet jeden Konflikt. Für Ops mit niedriger Fehlertoleranz bleibt der harte Konflikt bei abweichendem Ziel die sichere Wahl.

Hinweis: Nach jedem Lauf `curl -X POST localhost:8001/reset` ausführen, sonst startet der nächste Lauf mit Version 4 oder höher.
