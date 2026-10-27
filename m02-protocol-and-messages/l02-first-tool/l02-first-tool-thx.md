# Lab 2.2: Erstes eigenes Tool implementieren

**Leitfragen:**

<details>
<summary>Welche Angaben im Tool-Schema prüft der Client vor dem Aufruf?</summary>

Das `inputSchema` nennt Parameternamen, Typen und Pflichtfelder (`required`); daran baut der Host gültige Aufrufe. Im Kurs-Setup meldet der Server Abweichungen beim Aufruf als Tool-Fehler (`isError: true`, Lab 2.3).

</details>

<details>
<summary>Warum ist ein Resource kein Tool?</summary>

Eine Resource ist lesbare Information unter einer URI (`tickets://VAN-102`), die die Anwendung auswählt und lädt. Ein Tool ist eine Aktion, die das Modell auswählt und aufruft.

</details>

- Ein Tool ist eine Python-Funktion mit Typhinweisen und Docstring, registriert mit `@mcp.tool()`.
- Schema und Beschreibung entstehen aus der Funktion; das Modell sieht beides in `tools/list`.

## Die drei Primitives

| Primitive | Wer wählt aus | Wirkung | Wann nutzen | Beispiel Vantra |
| --- | --- | --- | --- | --- |
| Tool | Modell | kann rechnen, abfragen, ändern | Aktion oder Abfrage mit Parametern | `get_ticket(ticket_id)` |
| Resource | Anwendung | nur lesen, adressiert per URI | Daten, die der Host anzeigt oder mitgibt | `tickets://VAN-102` |
| Prompt | Nutzer:in | liefert eine Nachrichtenvorlage | wiederkehrende Arbeitsabläufe | „Ticket zusammenfassen“ |

Faustregel: Soll das Modell selbst entscheiden und Parameter wählen, ist es ein Tool. Sind es feste Daten unter einer Adresse, ist es eine Resource.

## Das Tool im Server

Datei `playground/server.py` (Beispiel: `examples/m02-protocol-and-messages/l02-first-tool/server.py`):

```python
import sys
from pathlib import Path

sys.path.insert(0, next(str(p) for p in Path(__file__).resolve().parents if (p / "shared").is_dir()))

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import ToolAnnotations

from shared.mock_api.client import get_backend
from shared.mock_api.store import NotFound

mcp = MCPServer("vantra-ops", instructions="MCP-Server des Vantra Ops Agent: Tickets abfragen.")
backend = get_backend()                       # Ticket-Daten aus shared/mock_api


@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))   # Tool registrieren, nur lesend
def get_ticket(ticket_id: str) -> dict:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc    # erwarteter Fehler: Text erreicht das Modell


if __name__ == "__main__":
    mcp.run()
```

| Teil | Wirkung |
| --- | --- |
| `@mcp.tool(...)` | registriert die Funktion; Name = Funktionsname (`get_ticket`) |
| `ticket_id: str` | erzeugt `inputSchema`: Eigenschaft `ticket_id` vom Typ `string`, Pflichtfeld |
| Docstring | wird zur `description`; das LLM liest ihn bei der Tool-Auswahl |
| `ToolAnnotations(read_only_hint=True)` | Hinweis an Clients: ändert nichts |
| Rückgabe `dict` | erscheint als JSON-Text in `content[0].text` |
| `ToolError` | erwarteter Fehler: Meldung geht an das Modell, Ergebnis mit `isError: true` |

Die Funktion `get_ticket` mit ihrem Schema erscheint in `tools/list`:

```json
{"name":"get_ticket","description":"Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version.","inputSchema":{"type":"object","properties":{"ticket_id":{"title":"Ticket Id","type":"string"}},"required":["ticket_id"],"title":"get_ticketArguments"},"annotations":{"readOnlyHint":true}}
```

## Tool aufrufen

```bash
python shared/script_client.py --server playground/server.py --call get_ticket '{"ticket_id": "VAN-102"}'
```

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: get_ticket
is_error=False
{
  "id": "VAN-102",
  "title": "Login-Seite lädt nach Release 2.14 sehr langsam",
  "status": "open",
  "priority": "high",
  "assignee": "jonas.brandt",
  "service": "auth-service",
  "description": "Seit dem Rollout von auth-service 2.14.1 dauert der Login 8 bis 12 Sekunden. Vor dem Release lag er unter 1 Sekunde.",
  "version": 3,
  "updated_at": "2026-10-27T07:45:00Z"
}
```

Im Inspector: `npx @modelcontextprotocol/inspector python playground/server.py`, Tab „Tools“, `get_ticket`, Feld `ticket_id` füllen.

## Fehler im Tool

Unbekanntes Ticket:

```bash
python shared/script_client.py --server playground/server.py --call get_ticket '{"ticket_id": "VAN-999"}'
```

```text
is_error=True
Error executing tool get_ticket: Ticket VAN-999 nicht gefunden
```

Eine normale Exception im Tool-Code würde dem Modell nur `Error executing tool get_ticket` zeigen; die Meldung bliebe verborgen und der Traceback landet auf stderr. Darum `ToolError` für erwartete Fehler.

## Resource als Gegenstück (Erweiterung)

```python
@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> dict:
    """Ticket als Resource (nur lesen, von der Anwendung adressierbar)."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ResourceNotFoundError(str(exc)) from exc
```

| Merkmal | Tool `get_ticket` | Resource `tickets://{ticket_id}` |
| --- | --- | --- |
| Auswahl | Modell, per `tools/call` | Anwendung, per `resources/read` |
| Eintrag in | `tools/list` | `resources/templates/list` (URI-Vorlage) |
| Fehler | `isError: true` im Ergebnis | JSON-RPC-Fehler `-32602` |

## Typische Fehler

| Symptom | Ursache | Lösung |
| --- | --- | --- |
| `Tools: (keine)` | `@mcp.tool()` vergessen oder falsche Datei gestartet | Dekorator prüfen, `--server`-Pfad prüfen |
| LLM wählt das Tool nicht | Docstring fehlt oder ist vage | Docstring mit Zweck und Beispiel-ID schreiben |
| Meldung des Modells nur `Error executing tool …` | normale Exception statt `ToolError` | `ToolError` verwenden |
| `ModuleNotFoundError: shared` | Starter außerhalb von `output/project/` kopiert | Datei im Playground belassen |

## Fazit

- `@mcp.tool()` macht aus Funktion, Typhinweisen und Docstring ein Tool mit Schema.
- Tool = Aktion mit Modellentscheidung, Resource = Daten unter einer URI.
- Erwartete Fehler werden mit `ToolError` gemeldet.

Die Übung ergänzt `get_ticket` im Playground-Server und ruft das Tool über Skript-Client und Inspector auf.
