# Lab 3.2: Kontextschema entwerfen und einbauen

**Leitfragen:**

<details>
<summary>Wie wird verhindert, dass das zweite Tool den Kontext des ersten überschreibt?</summary>

Jedes Tool schreibt nur in sein eigenes Feld: `get_ticket` in `last_ticket`, `get_deployment_log` in `last_deployment`. Gemeinsam genutzt wird nur lesend, über `resolve_ticket_id`.

</details>

<details>
<summary>Welcher Teil des Kontexts wird dem LLM tatsächlich übergeben?</summary>

Das Schema legt es pro Feld fest (Spalte `an_llm`): nur `last_ticket` und `last_deployment` in Kurzform. `ticket_versions` und `tool_calls` bleiben im Server.

</details>

- Ein Kontextschema besteht aus vier Angaben je Feld: Name, Quelle, Lebensdauer, Sichtbarkeit für das LLM.
- Schlank heißt: nur Felder, die ein Tool oder das Modell später braucht, und nur Ausschnitte statt Rohdaten.

## Kriterien für ein schlankes Schema

| Kriterium | Frage | Beispiel Vantra |
| --- | --- | --- |
| Quelle | Welches Tool schreibt das Feld? Genau eines. | `last_ticket` ← `get_ticket` |
| Lebensdauer | Wann wird der Wert ersetzt oder verworfen? | bis zum nächsten `get_ticket` |
| Sichtbarkeit | Darf das Modell den Wert sehen? | `ticket_versions`: nein |
| Größe | Reicht ein Ausschnitt? | Deployment ohne `log` |
| Vollständigkeit | Kann jedes Tool seine Eingaben aus Argument oder Kontext auflösen? | `get_deployment_log` ohne `ticket_id` |

## Schema im Projekt

Das Schema steht als Daten (`SESSION_SCHEMA`) und als Klasse in `context.py`. Vollständiger Stand: `examples/m03-context-and-state/l02-context-schema-implementation/context.py`.

| Feld | Quelle | Lebensdauer | an LLM |
| --- | --- | --- | --- |
| `last_ticket` | Tool `get_ticket` | bis zum nächsten `get_ticket` | `id, title, status, version` |
| `last_deployment` | Tool `get_deployment_log` | bis zum nächsten `get_deployment_log` | `id, service, version, status` |
| `ticket_versions` | `get_ticket`, `update_ticket_status` | Session | nein (nur Server) |
| `tool_calls` | jeder Tool-Aufruf | Session | nein (nur Server) |

```python
@dataclass
class SessionContext:
    last_ticket: dict | None = None
    last_deployment: dict | None = None            # eigenes Feld je Tool
    ticket_versions: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0

    def remember_ticket(self, ticket: dict) -> None:
        # nur der Ausschnitt, nicht das ganze Ticket
        self.last_ticket = {k: ticket[k] for k in ("id", "title", "status", "version")}
        self.ticket_versions[ticket["id"]] = ticket["version"]

    def remember_deployment(self, deployment: dict) -> None:
        self.last_deployment = {k: deployment[k] for k in ("id", "service", "version", "status")}

    def resolve_ticket_id(self, explicit: str | None) -> str | None:
        if explicit:                                # explizite ID gewinnt
            return explicit
        return self.last_ticket["id"] if self.last_ticket else None

    def to_llm_view(self) -> dict:
        return {"last_ticket": self.last_ticket, "last_deployment": self.last_deployment}


session = SessionContext()                          # eine Instanz je Serverprozess
```

## Zweites Tool am Kontext

`get_deployment_log` löst die Ticket-ID aus Argument oder Kontext auf und legt danach seinen Ausschnitt in `last_deployment` ab (`server.py` im Beispielordner):

```python
@mcp.tool(annotations=READ_ONLY)
def get_deployment_log(ticket_id: str | None = None, tail: int = 20) -> dict:
    """Log des letzten Deployments zu einem Ticket lesen. Ohne ticket_id gilt das zuletzt abgefragte Ticket."""
    session.tool_calls += 1
    resolved = session.resolve_ticket_id(ticket_id)
    if resolved is None:
        raise ToolError("Keine ticket_id angegeben und kein Ticket im Kontext: zuerst get_ticket aufrufen.")
    deployment = backend.latest_deployment(resolved)      # Mock-API
    session.remember_deployment(deployment)               # nur last_deployment wird geschrieben
    return {**{k: deployment[k] for k in ("id", "ticket_id", "service", "version", "environment", "status")},
            "log": deployment["log"][-tail:]}             # letzte `tail` Zeilen
```

- Der Docstring ist die Tool-Beschreibung, die das Modell zur Auswahl sieht; `ticket_id: str | None` macht das Argument optional.
- `ToolError` liefert dem Modell eine lesbare Meldung (`isError: true`) statt „Error executing tool …“ ohne Text.
- Das Log wird auf `tail` Zeilen gekürzt; das schont das Kontextfenster.

## Kontext als Resource

Die Resource `context://session` zeigt Schema und sichtbaren Ausschnitt; sie ist die Prüfstelle, was das Modell sehen darf:

```python
@mcp.resource("context://session", mime_type="application/json")
def session_context() -> dict:
    return {"schema": SESSION_SCHEMA, "aktuell": session.to_llm_view()}
```

## Grenzen

- Der Kontext gilt je Serverprozess, nicht je Nutzer: Bei mehreren Clients auf demselben Prozess (HTTP in Tag 2) teilen sie ihn.
- Der Zustand geht beim Neustart verloren; Memory ist nicht umgesetzt (Lab 3.1).

## Fazit

- Schema = Feld, Quelle, Lebensdauer, Sichtbarkeit; ein Tool schreibt genau ein Feld.
- `resolve_ticket_id` verbindet die Tools lesend, ohne dass sie sich überschreiben.
- Die Resource `context://session` zeigt, was vom Kontext sichtbar ist.

Die Übung baut `context.py` aus dem Starter, ergänzt `get_deployment_log` und prüft das Zusammenspiel.
