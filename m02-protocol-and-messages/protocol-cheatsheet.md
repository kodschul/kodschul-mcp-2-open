# Protokoll und Nachrichten: Cheatsheet

## Nachrichtenarten (JSON-RPC 2.0)

| Art | Felder | Antwort |
| --- | --- | --- |
| Request | `jsonrpc`, `id`, `method`, `params` | Response mit gleicher `id` |
| Response (Erfolg) | `jsonrpc`, `id`, `result` | – |
| Response (Fehler) | `jsonrpc`, `id`, `error {code, message}` | – |
| Notification | `jsonrpc`, `method`, `params`, kein `id` | keine |

stdio: eine JSON-Nachricht pro Zeile; stdout gehört dem Protokoll, Logs auf stderr.

## Hülle pro Request (Spezifikation 2026-07-28)

| Schlüssel in `params._meta` | Wert |
| --- | --- |
| `io.modelcontextprotocol/protocolVersion` | `"2026-07-28"` (Pflicht) |
| `io.modelcontextprotocol/clientCapabilities` | `{}` (Pflicht) |
| `io.modelcontextprotocol/clientInfo` | `{"name": "…", "version": "…"}` (vom SDK gesendet) |

Kein `initialize`. Antworten tragen `"resultType":"complete"` und `_meta["io.modelcontextprotocol/serverInfo"]`.

## Methoden

| Methode | Zweck |
| --- | --- |
| `server/discover` | optional: Fähigkeiten, `supportedVersions`, `instructions` |
| `tools/list` | Tools mit `description` und `inputSchema` |
| `tools/call` | Tool mit `name` und `arguments` aufrufen |
| `resources/templates/list` | URI-Vorlagen der Resources |
| `resources/read` | Resource per URI lesen |

## Server-Code

| Code | Wirkung |
| --- | --- |
| `@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))` | Tool registrieren, nur lesend |
| `def get_ticket(ticket_id: str) -> dict:` | Typhinweis → `inputSchema`, Pflichtfeld |
| Docstring | wird `description` |
| `raise ToolError("…")` | erwarteter Fehler, Meldung erreicht das Modell |
| `@mcp.resource("tickets://{ticket_id}", mime_type="application/json")` | Resource mit URI-Vorlage |
| `raise ResourceNotFoundError("…")` | Resource-Fehler → `-32602` |
| `from mcp.server.mcpserver.exceptions import ToolError, ResourceNotFoundError` | Import der Fehlerklassen |

## Testbefehle

| Befehl | Wirkung |
| --- | --- |
| `python shared/script_client.py --server playground/server.py --call get_ticket '{"ticket_id": "VAN-102"}'` | Tool per Skript-Client aufrufen |
| `python playground/raw_requests.py` | rohe JSON-RPC-Zeilen senden |
| `python examples/m02-protocol-and-messages/l02-first-tool/error_cases.py` | fünf Fehlerfälle |
| `npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/call --tool-name get_ticket --tool-arg ticket_id=VAN-102` | Aufruf per Inspector-CLI |
| `python shared/agent_client.py --server playground/server.py --replay --trace trace.log` | Trace der Nachrichten in Datei |

## Fehlerarten

| Ebene | Erkennung | Beispiel | Retry |
| --- | --- | --- | --- |
| Tool-Fehler | `result.isError: true` | `Error executing tool get_ticket: Ticket VAN-999 nicht gefunden` | bei Eingabefehlern mit korrigierten Argumenten |
| Protokollfehler | `error.code` | `-32602` ungültige Parameter, `-32601` Methode unbekannt, `-32600` ungültiger Request | Client korrigieren |

| Aufruf | Ergebnis |
| --- | --- |
| `{"id": "VAN-102"}` statt `ticket_id` | `isError: true`, `Field required` |
| `{"ticket_id": 102}` | `isError: true`, validation error |
| unbekanntes Tool | `isError: true`, `Unknown tool: get_tickets` |
| Request ohne `_meta` | `error` `-32602` |
| unbekannte Methode | `error` `-32601`, `data` = Methodenname |
| unbekannte Resource | `error` `-32602`, Meldung der Resource |
| normale Exception im Tool | Modell sieht nur `Error executing tool <name>` |
