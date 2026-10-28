# Lab 2.1 – Lösung: JSON-RPC live am eigenen Server

Alle Antworten stammen vom leeren Server aus Lab 1.2 (`mcp` 2.3.0). Die Zeilen `>>` zeigen den gesendeten Request, die Zeilen `<<` die Antwort.

## Aufgabe 1: Starter und server/discover

```bash
cp starters/m02-l01-raw-requests.py playground/raw_requests.py
python playground/raw_requests.py
```

Antwortzeile, umbrochen:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "capabilities": {"prompts": {"listChanged": true}, "resources": {"listChanged": true, "subscribe": true}, "tools": {"listChanged": true}},
    "instructions": "MCP-Server des Vantra Ops Agent. Noch ohne Tools: Aufbau folgt in den nächsten Labs.",
    "supportedVersions": ["2026-07-28"],
    "cacheScope": "private", "resultType": "complete", "ttlMs": 0,
    "_meta": {"io.modelcontextprotocol/serverInfo": {"name": "vantra-ops", "version": ""}}
  }
}
```

Servername `vantra-ops`, `instructions` aus Lab 1.2, `supportedVersions` = `["2026-07-28"]`.

## Aufgabe 2: tools/list

```python
send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {"_meta": META}})
```

```text
<< {"jsonrpc":"2.0","id":2,"result":{"cacheScope":"private","resultType":"complete","tools":[],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

`tools` ist eine leere Liste: Der Server hat noch kein Tool.

## Aufgabe 3: Unbekannte Methode

```python
send(proc, {"jsonrpc": "2.0", "id": 3, "method": "nope/list", "params": {"_meta": META}})
```

```text
<< {"jsonrpc":"2.0","id":3,"error":{"code":-32601,"message":"Method not found","data":"nope/list"}}
```

Code `-32601` = Methode nicht gefunden; `data` nennt die unbekannte Methode.

## Aufgabe 4: Request ohne Hülle

```python
send(proc, {"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
```

```text
<< {"jsonrpc":"2.0","id":4,"error":{"code":-32602,"message":"params._meta must be an object carrying the required 'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys"}}
```

Es ist ein `error`, weil die Nachricht selbst ungültig ist (Code `-32602` = ungültige Parameter): Die Pflichtangaben der Hülle fehlen, der Server bearbeitet den Request gar nicht erst.

## Aufgabe 5: Notification

```python
send(proc, {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99, "_meta": META}})
send(proc, {"jsonrpc": "2.0", "id": 5, "method": "tools/list", "params": {"_meta": META}})
```

```text
>> {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 99, ...}}
>> {"jsonrpc": "2.0", "id": 5, "method": "tools/list", "params": {...}}
<< {"jsonrpc":"2.0","id":5,"result":{"cacheScope":"private","resultType":"complete","tools":[],"ttlMs":0,"_meta":{...}}}
```

Auf die Notification folgt keine `<<`-Zeile. Die erste Antwort danach trägt `"id":5`. Das Fehlen von `id` unterscheidet die Notification vom Request.

## Aufgabe 6: Protokoll

`playground/protokoll.md`:

| Nr. | Richtung | Art | id | method |
| --- | --- | --- | --- | --- |
| 1 | Client → Server | Request | 1 | `server/discover` |
| 2 | Server → Client | Response | 1 | – |
| 3 | Client → Server | Request | 2 | `tools/list` |
| 4 | Server → Client | Response | 2 | – |
| 5 | Client → Server | Request | 3 | `nope/list` |
| 6 | Server → Client | Response (`error` -32601) | 3 | – |
| 7 | Client → Server | Request | 4 | `tools/list` (ohne `_meta`) |
| 8 | Server → Client | Response (`error` -32602) | 4 | – |
| 9 | Client → Server | Notification | – | `notifications/cancelled` |
| 10 | Client → Server | Request | 5 | `tools/list` |
| 11 | Server → Client | Response | 5 | – |

Die Antwortzeilen tragen kein `method`; sie gehören über die `id` zum Request.

## Erweiterung: Trace im Inspector

Nach **Connect** und **List Tools** zeigt das Terminal:

```text
[..:..:..] CLIENT -> SERVER {"jsonrpc":"2.0","id":...,"method":"server/discover",...}
[..:..:..] SERVER -> CLIENT {"jsonrpc":"2.0","id":...,"result":{...}}
[..:..:..] CLIENT -> SERVER {"jsonrpc":"2.0","id":...,"method":"tools/list",...}
[..:..:..] SERVER -> CLIENT {"jsonrpc":"2.0","id":...,"result":{..."tools":[]...}}
```

Gleiche Reihenfolge wie im eigenen Protokoll; die `id`-Werte vergibt der Inspector selbst.
