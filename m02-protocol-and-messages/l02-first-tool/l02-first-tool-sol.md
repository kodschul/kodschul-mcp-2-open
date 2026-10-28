# Lab 2.2 – Lösung: Erstes eigenes Tool implementieren

## Aufgabe 1: Starter kopieren und prüfen

```bash
cp starters/m02-l02-first-tool.py playground/server.py
python shared/script_client.py --server playground/server.py
```

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: (keine)
```

## Aufgabe 2: Tool implementieren

```python
@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
def get_ticket(ticket_id: str) -> dict:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    return backend.get_ticket(ticket_id)
```

Der Typhinweis `str` erzeugt das Pflichtfeld `ticket_id`, der Docstring die Beschreibung, `read_only_hint=True` markiert die reine Abfrage.

## Aufgabe 3: Fehler als ToolError

```python
@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))
def get_ticket(ticket_id: str) -> dict:
    """Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
```

`ToolError` lässt die Meldung das Modell erreichen. Eine normale Exception zeigte nur `Error executing tool get_ticket`.

## Aufgabe 4: Aufruf mit VAN-102

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

`status` = `open`, `priority` = `high`, `version` = `3`.

## Aufgabe 5: Aufruf mit VAN-999

```bash
python shared/script_client.py --server playground/server.py --call get_ticket '{"ticket_id": "VAN-999"}'
```

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: get_ticket
is_error=True
Error executing tool get_ticket: Ticket VAN-999 nicht gefunden
```

Der Skript-Client beendet sich bei `is_error=True` mit Exit-Code 1. Die Meldung stammt aus dem `ToolError`, ergänzt um das Präfix `Error executing tool get_ticket: `. Zusätzlich erscheint im Terminal die Log-Zeile des Servers auf stderr: `Tool 'get_ticket' failed: 'Error executing tool get_ticket: Ticket VAN-999 nicht gefunden'`. Sie gehört nicht zur Antwort an den Client.

## Aufgabe 6: tools/call als Rohnachricht

```python
send(proc, {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
            "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}, "_meta": META}})
```

Antwortzeile, umbrochen und gekürzt:

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [{"type": "text", "text": "{\n  \"id\": \"VAN-102\",\n  \"title\": \"Login-Seite lädt nach Release 2.14 sehr langsam\",\n  \"status\": \"open\", … \"version\": 3, …}"}],
    "isError": false,
    "resultType": "complete",
    "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "vantra-ops", "version": ""}}
  }
}
```

Der Ticket-Text steht in `result.content[0].text` (JSON als Zeichenkette), `isError` ist `false`. Die Antworten der Requests 1 bis 5 aus Lab 2.1 zeigen jetzt `get_ticket` in `tools`. Vergleich: `examples/m02-protocol-and-messages/l02-first-tool/raw_requests.py`.

## Aufgabe 7: Inspector

```bash
npx @modelcontextprotocol/inspector python playground/server.py
```

Nach **Connect** und **List Tools** steht im Tab **Tools** `get_ticket` mit der Beschreibung aus dem Docstring und dem Pflichtfeld `ticket_id` (Typ `string`). Für `VAN-105` liefert **Run Tool** `"assignee": null`: das Ticket ist niemandem zugewiesen. Dasselbe in der Konsole:

```bash
npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/call --tool-name get_ticket --tool-arg ticket_id=VAN-105
```

Die Ausgabe hat die Form `{"content": [{"type": "text", "text": "…"}], "isError": false}`.

## Aufgabe 8: Vergleich

Der Server stimmt mit `examples/m02-protocol-and-messages/l02-first-tool/server.py` überein, bis auf die optionale Resource. Zulässige Abweichungen: Wortlaut des Docstrings und der `instructions`.

## Erweiterung: Resource

```python
@mcp.resource("tickets://{ticket_id}", mime_type="application/json")
def ticket_resource(ticket_id: str) -> dict:
    """Ticket als Resource (nur lesen, von der Anwendung adressierbar)."""
    try:
        return backend.get_ticket(ticket_id)
    except NotFound as exc:
        raise ResourceNotFoundError(str(exc)) from exc
```

Im Inspector unter „Resources“ erscheint die Vorlage `tickets://{ticket_id}`; `tickets://VAN-104` liefert das Ticket „Dashboard zeigt falsche Zeitzone“ als JSON (`application/json`). Ein unbekanntes Ticket führt zu einem JSON-RPC-Fehler `-32602` mit der Meldung `Ticket VAN-999 nicht gefunden`.
