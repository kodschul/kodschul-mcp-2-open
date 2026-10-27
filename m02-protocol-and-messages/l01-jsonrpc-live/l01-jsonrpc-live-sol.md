# Lab 2.1 – Lösung: JSON-RPC live am eigenen Server

## Aufgabe 1: Starter, Server und server/discover

```python
SERVER = "examples/m02-protocol-and-messages/l02-first-tool/server.py"
```

Die Ausgabe beginnt mit dem mitgeschickten `server/discover`-Request (`>>`) und der Antwort (`<<`):

```json
{"jsonrpc":"2.0","id":1,"result":{"cacheScope":"private","capabilities":{"prompts":{"listChanged":true},"resources":{"listChanged":true,"subscribe":true},"tools":{"listChanged":true}},"instructions":"MCP-Server des Vantra Ops Agent: Tickets abfragen.","resultType":"complete","supportedVersions":["2026-07-28"],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

## Aufgabe 2: tools/list

```python
send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {"_meta": META}})
```

Antwort:

```json
{"jsonrpc":"2.0","id":2,"result":{"cacheScope":"private","resultType":"complete","tools":[{"annotations":{"readOnlyHint":true},"description":"Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version.","inputSchema":{"type":"object","properties":{"ticket_id":{"title":"Ticket Id","type":"string"}},"required":["ticket_id"],"title":"get_ticketArguments"},"name":"get_ticket"}],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

## Aufgabe 3: tools/call

```python
send(proc, {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}, "_meta": META}})
```

```json
{"jsonrpc":"2.0","id":3,"result":{"content":[{"text":"{\n  \"id\": \"VAN-102\",\n  \"title\": \"Login-Seite lädt nach Release 2.14 sehr langsam\",\n  \"status\": \"open\",\n  \"priority\": \"high\",\n  \"assignee\": \"jonas.brandt\",\n  \"service\": \"auth-service\",\n  \"description\": \"Seit dem Rollout von auth-service 2.14.1 dauert der Login 8 bis 12 Sekunden. Vor dem Release lag er unter 1 Sekunde.\",\n  \"version\": 3,\n  \"updated_at\": \"2026-10-27T07:45:00Z\"\n}","type":"text"}],"isError":false,"resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

`status` ist `open`, `priority` ist `high`, `isError` ist `false`.

## Aufgabe 4: Request ohne _meta

```python
send(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}}})
```

```json
{"jsonrpc":"2.0","id":4,"error":{"code":-32602,"message":"params._meta must be an object carrying the required 'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys"}}
```

Es ist ein `error`, weil der Request als Nachricht ungültig ist (Protokollfehler, Code `-32602` = ungültige Parameter). Der Tool-Code wurde nicht erreicht; ein Fehler im Tool käme dagegen als `result` mit `isError: true` (Lab 2.3).

## Aufgabe 5: Notification

```python
send(proc, {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99, "_meta": META}})
send(proc, {"jsonrpc": "2.0", "id": 5, "method": "tools/list", "params": {"_meta": META}})
```

Auf die Notification folgt keine `<<`-Zeile: die Zeile `>>` mit `notifications/cancelled` steht direkt vor dem nächsten `>>` mit `id` 5. Die erste Antwort danach trägt `"id":5`. Das Fehlen von `id` unterscheidet die Notification vom Request.

## Aufgabe 6: Protokoll

`playground/protokoll.md`:

| Nr. | Richtung | Art | id | method |
| --- | --- | --- | --- | --- |
| 1 | Client → Server | Request | 1 | `server/discover` |
| 2 | Server → Client | Response | 1 | – |
| 3 | Client → Server | Request | 2 | `tools/list` |
| 4 | Server → Client | Response | 2 | – |
| 5 | Client → Server | Request | 3 | `tools/call` |
| 6 | Server → Client | Response | 3 | – |
| 7 | Client → Server | Request | 4 | `tools/call` (ohne `_meta`) |
| 8 | Server → Client | Response (`error` -32602) | 4 | – |
| 9 | Client → Server | Notification | – | `notifications/cancelled` |
| 10 | Client → Server | Request | 5 | `tools/list` |
| 11 | Server → Client | Response | 5 | – |

Die Antwortzeilen tragen kein `method`; sie gehören über die `id` zum Request.

## Erweiterung: Trace-Vergleich

```bash
python shared/agent_client.py --server playground/server.py --replay --trace trace.log
```

`trace.log` zeigt dieselbe Reihenfolge wie das Protokoll: `server/discover` (id 1), `tools/list` (id 2), `tools/call` `get_ticket` (id 3), danach `tools/call` `get_deployment_log` (id 4). Der letzte Aufruf endet mit `Unknown tool: get_deployment_log` und `isError: true`, weil der Server das Tool noch nicht hat. Der SDK-Client trägt außerdem `clientInfo` und die Version in `_meta`.
