# Lab 2.1: JSON-RPC live am eigenen Server

**Leitfragen:**

<details>
<summary>Woran erkennt man eine Notification im Gegensatz zu einem Request?</summary>

Eine Notification hat kein Feld `id` und bekommt keine Antwort. Ein Request trägt eine `id` und erwartet genau eine Antwort mit derselben `id`.

</details>

<details>
<summary>Welches Feld bräuchte man, um die Antwort einem Request zuzuordnen?</summary>

Das Feld `id`: die Antwort übernimmt den Wert des Requests. Bei mehreren offenen Requests ist es die einzige Zuordnung.

</details>

- MCP-Nachrichten sind JSON-RPC 2.0: Request, Response und Notification.
- Bei stdio steht je Nachricht eine JSON-Zeile auf stdin (Client → Server) bzw. stdout (Server → Client).

## Die drei Nachrichtenarten

| Art | Pflichtfelder | Antwort |
| --- | --- | --- |
| Request | `jsonrpc: "2.0"`, `id`, `method`, optional `params` | genau eine Response mit gleicher `id` |
| Response (Erfolg) | `jsonrpc`, `id`, `result` | – |
| Response (Fehler) | `jsonrpc`, `id`, `error` mit `code` und `message` | – |
| Notification | `jsonrpc`, `method`, optional `params`, **kein** `id` | keine |

## Seit Spezifikation 2026-07-28: kein Handshake

Ein `initialize`-Handshake ist nicht nötig. Der Client sendet direkt `tools/list` oder `tools/call`. Jeder Request trägt in `params._meta` die Angaben, die früher der Handshake geliefert hat:

| Schlüssel in `params._meta` | Inhalt | Pflicht |
| --- | --- | --- |
| `io.modelcontextprotocol/protocolVersion` | `"2026-07-28"` | ja |
| `io.modelcontextprotocol/clientCapabilities` | Objekt, darf `{}` sein | ja |
| `io.modelcontextprotocol/clientInfo` | `{"name": …, "version": …}` | vom SDK mitgesendet |

Antworten tragen `"resultType":"complete"` und den Servernamen in `_meta["io.modelcontextprotocol/serverInfo"]`. `server/discover` ist optional und liefert Fähigkeiten und unterstützte Versionen.

> **Merksatz:** Request und Antwort gehören über die `id` zusammen; eine Nachricht ohne `id` ist eine Notification und bleibt unbeantwortet.

## Request und Response: tools/list

Request (eine Zeile, hier umbrochen):

```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list",
 "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                      "io.modelcontextprotocol/clientInfo": {"name": "raw-script", "version": "0.1"},
                      "io.modelcontextprotocol/clientCapabilities": {}}}}
```

Antwort des Servers aus Lab 2.2:

```json
{"jsonrpc":"2.0","id":2,"result":{"cacheScope":"private","resultType":"complete","tools":[{"annotations":{"readOnlyHint":true},"description":"Ticket anhand seiner ID (z. B. VAN-102) abfragen: Titel, Status, Priorität, Version.","inputSchema":{"type":"object","properties":{"ticket_id":{"title":"Ticket Id","type":"string"}},"required":["ticket_id"],"title":"get_ticketArguments"},"name":"get_ticket"}],"ttlMs":0,"_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

| Feld | Bedeutung |
| --- | --- |
| `id: 2` | gleiche `id` wie im Request |
| `result.tools[]` | Tools mit `name`, `description`, `inputSchema` und `annotations` |
| `inputSchema.required` | Pflichtparameter: hier `ticket_id` |

## Request mit Ergebnis: tools/call

```json
{"jsonrpc": "2.0", "id": 3, "method": "tools/call",
 "params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}, "_meta": {…}}}
```

```json
{"jsonrpc":"2.0","id":3,"result":{"content":[{"text":"{\n  \"id\": \"VAN-102\",\n  \"title\": \"Login-Seite lädt nach Release 2.14 sehr langsam\",\n  \"status\": \"open\",\n  \"priority\": \"high\",\n  \"assignee\": \"jonas.brandt\",\n  \"service\": \"auth-service\",\n  \"description\": \"Seit dem Rollout von auth-service 2.14.1 dauert der Login 8 bis 12 Sekunden. Vor dem Release lag er unter 1 Sekunde.\",\n  \"version\": 3,\n  \"updated_at\": \"2026-10-27T07:45:00Z\"\n}","type":"text"}],"isError":false,"resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

`result.content` enthält das Ergebnis als Textblock, `isError: false` kennzeichnet den Erfolg.

## Fehler: fehlende Hülle

Fehlt `params._meta`, antwortet der Server mit einem JSON-RPC-Fehlerobjekt:

```json
{"jsonrpc":"2.0","id":5,"error":{"code":-32602,"message":"params._meta must be an object carrying the required 'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys"}}
```

Die erste Nachricht einer Verbindung legt die Protokollgeneration fest. Beginnt sie ohne Hülle, schaltet der Server in den alten Handshake-Modus und lehnt danach Requests mit Hülle ab (`-32600`). Eine Notification wie `notifications/cancelled` hat kein `id` und erzeugt keine Zeile auf stdout.

## Rohe Requests im Projekt

`starters/m02-l01-raw-requests.py` startet den Server als Kindprozess und schickt eigene Zeilen:

```python
proc = subprocess.Popen([sys.executable, SERVER], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
proc.stdin.write(json.dumps(message) + "\n")      # eine Nachricht = eine Zeile
proc.stdin.flush()
if "id" in message:                               # nur Requests bekommen eine Antwort
    print("<<", proc.stdout.readline().strip())
```

Das vollständige Vergleichsbeispiel liegt unter `examples/m02-protocol-and-messages/l01-jsonrpc-live/raw_requests.py`. `printf … | python server.py` taugt nicht: das Dateiende beendet den Server vor den Antworten.

## Live-Trace

`shared/agent_client.py --replay --trace trace.log` leitet die Verbindung über `shared/trace_proxy.py` und schreibt jede Zeile mit Richtung:

```text
[17:58:41] CLIENT -> SERVER {"jsonrpc":"2.0","id":1,"method":"server/discover","params":{...}}
[17:58:41] SERVER -> CLIENT {"jsonrpc":"2.0","id":1,"result":{...}}
```

Der SDK-Client sendet immer `server/discover` (id 1), dann `tools/list` (id 2), danach die Aufrufe.

## Fazit

- Request mit `id` → Response mit derselben `id`; Notification ohne `id` → keine Antwort.
- Jeder Request trägt die Protokollversion in `params._meta`; kein `initialize`.
- Auf stdout stehen nur JSON-Zeilen, Logs gehen auf stderr.

Die Übung schickt diese Nachrichten selbst an den Server und liest die Rohantworten.
