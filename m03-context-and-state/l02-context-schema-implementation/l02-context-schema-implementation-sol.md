# Lab 3.2 – Lösung: Kontextschema entwerfen und einbauen

Vollständiger Stand: `examples/m03-context-and-state/l02-context-schema-implementation/` (`context.py`, `server.py`).

## Aufgabe 1: Schema vervollständigen

```python
SESSION_SCHEMA = [
    {"feld": "last_ticket", "quelle": "Tool get_ticket", "lebensdauer": "bis zum nächsten get_ticket", "an_llm": "id, title, status, version"},
    {"feld": "last_deployment", "quelle": "Tool get_deployment_log", "lebensdauer": "bis zum nächsten get_deployment_log", "an_llm": "id, service, version, status"},
    {"feld": "ticket_versions", "quelle": "get_ticket, update_ticket_status", "lebensdauer": "Session", "an_llm": "nein (nur Server)"},
    {"feld": "tool_calls", "quelle": "jeder Tool-Aufruf", "lebensdauer": "Session", "an_llm": "nein (nur Server)"},
]


@dataclass
class SessionContext:
    last_ticket: dict | None = None
    last_deployment: dict | None = None     # eigenes Feld: das zweite Tool überschreibt last_ticket nie
    ticket_versions: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0
```

Ein eigenes Feld pro Tool ist die Antwort auf die Überschreibungsfrage; ein gemeinsames Feld `last_result` würde bei jedem Tool-Wechsel das vorherige Ergebnis verlieren.

## Aufgabe 2: `remember_deployment`

```python
def remember_deployment(self, deployment: dict) -> None:
    self.last_deployment = {k: deployment[k] for k in ("id", "service", "version", "status")}
```

Das Log bleibt draußen: Es ist groß und jederzeit neu abrufbar.

## Aufgabe 3: `resolve_ticket_id` und `to_llm_view`

```python
def resolve_ticket_id(self, explicit: str | None) -> str | None:
    """Explizite ID gewinnt; sonst das zuletzt abgefragte Ticket ("das Deployment dazu")."""
    if explicit:
        return explicit
    return self.last_ticket["id"] if self.last_ticket else None

def to_llm_view(self) -> dict:
    return {"last_ticket": self.last_ticket, "last_deployment": self.last_deployment}
```

`python playground/context.py` gibt aus:

```text
Kontext nach Ticket: {'id': 'VAN-102', 'title': 'Beispiel', 'status': 'open', 'version': 3}
Aufgelöste Ticket-ID: VAN-102
```

## Aufgabe 4: Kontext in `get_ticket`

```python
from context import SESSION_SCHEMA, session

@mcp.tool(annotations=READ_ONLY)
def get_ticket(ticket_id: str) -> dict:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    session.tool_calls += 1
    try:
        ticket = backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    session.remember_ticket(ticket)          # Ausschnitt in last_ticket, Version in ticket_versions
    return ticket
```

## Aufgabe 5: Tool `get_deployment_log`

```python
@mcp.tool(annotations=READ_ONLY)
def get_deployment_log(ticket_id: str | None = None, tail: int = 20) -> dict:
    """Log des letzten Deployments zu einem Ticket lesen. Ohne ticket_id gilt das zuletzt abgefragte Ticket."""
    session.tool_calls += 1
    resolved = session.resolve_ticket_id(ticket_id)
    if resolved is None:
        raise ToolError("Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.")
    try:
        deployment = backend.latest_deployment(resolved)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    session.remember_deployment(deployment)
    return {**{k: deployment[k] for k in ("id", "ticket_id", "service", "version", "environment", "status")}, "log": deployment["log"][-tail:]}
```

Die Beschreibung im Docstring nennt das Kontextverhalten („Ohne ticket_id …“), damit das Modell das Argument weglassen darf.

## Aufgabe 6: Prüfen

`--call get_deployment_log '{"ticket_id": "VAN-102", "tail": 2}'`:

```text
is_error=False
{
  "id": "dep-2041",
  "ticket_id": "VAN-102",
  "service": "auth-service",
  "version": "2.14.1",
  "environment": "production",
  "status": "degraded",
  "log": [
    "2026-10-26T22:17:03Z ERROR auth      token cache disabled by config key AUTH_CACHE_TTL=0",
    "2026-10-26T22:17:10Z INFO  deploy    finished with warnings, rollback not triggered"
  ]
}
```

`--call get_deployment_log '{}'` in einem neuen Prozess: `is_error=True`, `Error executing tool get_deployment_log: Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.`

Agent-Lauf mit `--replay` (Skript-Agent, ein Prozess, daher bleibt der Kontext erhalten):

```text
Verbunden mit vantra-ops, Protokoll 2026-07-28
Tools: get_ticket, get_deployment_log  ·  LLM: replay

Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: {   "id": "VAN-102",   "title": "Login-Seite lädt nach Release 2.14 sehr langsam",   "status": "open",   "priority": "high",   "assignee": "jonas.brandt",   "se…
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).

Nutzer: Zeige das Deployment-Log dazu
  → Tool-Call: get_deployment_log({})
  ← ok: {   "id": "dep-2041",   "ticket_id": "VAN-102",   "service": "auth-service",   "version": "2.14.1",   "environment": "production",   "status": "degraded",   "lo…
Agent: Deployment dep-2041 (auth-service 2.14.1, Status degraded). Letzte Zeilen: auth      token cache disabled by config key AUTH_CACHE_TTL=0;  deploy    finished with warnings, rollback not triggered
```

Der zweite Aufruf trägt keine ID: Die ID kommt aus `last_ticket`.

## Erweiterung: Resource `context://session`

```python
@mcp.resource("context://session", mime_type="application/json")
def session_context() -> dict:
    """Sichtbarer Ausschnitt des Session-Kontexts und das Schema dahinter."""
    return {"schema": SESSION_SCHEMA, "aktuell": session.to_llm_view()}
```

Lesen nach `get_ticket` und `get_deployment_log` in einer Session (Ausschnitt `aktuell`):

```json
{
  "last_ticket": {"id": "VAN-102", "title": "Login-Seite lädt nach Release 2.14 sehr langsam", "status": "open", "version": 3},
  "last_deployment": {"id": "dep-2041", "service": "auth-service", "version": "2.14.1", "status": "degraded"}
}
```

`ticket_versions` und `tool_calls` fehlen in der Resource, wie das Schema es festlegt.
