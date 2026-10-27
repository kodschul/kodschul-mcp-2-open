# Lab 2.3: Fehlerfälle provozieren und verstehen

**Leitfragen:**

<details>
<summary>An welcher Stelle würde ein Retry sinnvoll ansetzen?</summary>

Beim Host bzw. Modell, nachdem die Fehlermeldung ausgewertet wurde: bei Eingabefehlern mit korrigierten Argumenten, bei vorübergehenden Störungen (Verbindung, Zeitüberschreitung) unverändert. Ein Retry mit denselben fehlerhaften Argumenten bringt nichts.

</details>

<details>
<summary>Welche Information fehlt in der Fehlerantwort, die für Debugging nötig wäre?</summary>

Die Antwort nennt weder die erlaubten Werte noch einen Hinweis, ob ein Retry sinnvoll ist, und sie enthält keine eigene Fehlerkennung. Bei normalen Exceptions fehlt zudem die Ursache, sie steht nur im stderr-Log des Servers.

</details>

- MCP kennt zwei Fehlerebenen: Protokollfehler (JSON-RPC-`error`) und Tool-Fehler (`result` mit `isError: true`).
- Tool-Fehler sind für das Modell lesbar und ermöglichen eine Korrektur im nächsten Versuch.

## Zwei Fehlerebenen

| Ebene | Form | Ursache | Wer sieht es |
| --- | --- | --- | --- |
| Protokollfehler | `"error": {"code": …, "message": …}` | Nachricht ungültig: fehlende `_meta`, unbekannte Methode, unbekannte Resource | Client (SDK wirft `MCPError`) |
| Tool-Fehler | `"result": {"isError": true, "content": [...]}` | Tool nicht gefunden, Argumente ungültig, Fehler im Tool | Modell über den Host |

| Code | Bedeutung | Beispiel |
| --- | --- | --- |
| `-32602` | ungültige Parameter | fehlende `_meta`-Hülle, unbekannte Resource-URI |
| `-32601` | Methode nicht gefunden | `nope/list` |
| `-32600` | ungültiger Request | Verbindung im Handshake-Modus |

## Die Fehlerfälle am Server aus Lab 2.2

Das Skript `examples/m02-protocol-and-messages/l02-first-tool/error_cases.py` löst fünf Fälle aus:

```bash
python examples/m02-protocol-and-messages/l02-first-tool/error_cases.py
```

```text
1) falscher Parameter (id statt ticket_id)
  is_error=True  text='Error executing tool get_ticket: 1 validation error for get_ticketArguments'

2) falscher Typ (Zahl statt Text)
  is_error=True  text='Error executing tool get_ticket: 1 validation error for get_ticketArguments'

3) unbekanntes Ticket
  is_error=True  text='Error executing tool get_ticket: Ticket VAN-999 nicht gefunden'

4) unbekanntes Tool
  is_error=True  text='Unknown tool: get_tickets'

5) unbekannte Resource
  MCPError code=-32602 message='Ticket VAN-999 nicht gefunden'
```

| Fall | Ebene | Ursache | Retry sinnvoll? |
| --- | --- | --- | --- |
| 1 falscher Parameter | Tool-Fehler | Pflichtfeld `ticket_id` fehlt | ja, mit `ticket_id` |
| 2 falscher Typ | Tool-Fehler | Zahl statt Text | ja, mit Text |
| 3 unbekanntes Ticket | Tool-Fehler | ID existiert nicht (`ToolError`) | nein, andere ID wählen |
| 4 unbekanntes Tool | Tool-Fehler | Toolname falsch (`get_tickets`) | ja, mit Namen aus `tools/list` |
| 5 unbekannte Resource | Protokollfehler | URI existiert nicht | nein |

## Die Rohantwort bei falschem Parameter

Aufruf mit `{"id": "VAN-102"}` statt `{"ticket_id": "VAN-102"}`:

```json
{"jsonrpc":"2.0","id":4,"result":{"content":[{"text":"Error executing tool get_ticket: 1 validation error for get_ticketArguments\nticket_id\n  Field required [type=missing, input_value={'id': 'VAN-102'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.14/v/missing","type":"text"}],"isError":true,"resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"vantra-ops","version":""}}}}
```

| Teil | Aussage |
| --- | --- |
| `"result"` statt `"error"` | der Tool-Aufruf wurde zugestellt, das Tool schlug fehl |
| `isError: true` | Fehler-Kennzeichen für den Host |
| `ticket_id … Field required` | Ursache: Pflichtfeld fehlt |
| `input_value={'id': 'VAN-102'}` | zeigt, was angekommen ist |

Fehlt dagegen die `_meta`-Hülle, kommt ein echter Protokollfehler:

```json
{"jsonrpc":"2.0","id":5,"error":{"code":-32602,"message":"params._meta must be an object carrying the required 'io.modelcontextprotocol/protocolVersion' and 'io.modelcontextprotocol/clientCapabilities' envelope keys"}}
```

Eine unbekannte Methode (hier `nope/list`) liefert:

```json
{"jsonrpc":"2.0","id":4,"error":{"code":-32601,"message":"Method not found","data":"nope/list"}}
```

## ToolError und normale Exception

| Im Tool-Code | Meldung beim Modell | Server-Log (stderr) |
| --- | --- | --- |
| `raise ToolError("Ticket VAN-999 nicht gefunden")` | `Error executing tool get_ticket: Ticket VAN-999 nicht gefunden` | eine Logzeile mit der Meldung |
| beliebige andere Exception | nur `Error executing tool get_ticket` | Traceback |

Erwartete Fehler (unbekannte ID, ungültiger Wert) gehören in `ToolError` mit einer Meldung, die dem Modell die Korrektur erlaubt.

## Retry-Muster

| Fehlerart | Maßnahme |
| --- | --- |
| Validierungsfehler (Fall 1, 2) | Argumente korrigieren, erneut aufrufen |
| Tool unbekannt (Fall 4) | `tools/list` lesen, Namen korrigieren |
| Fachlicher Fehler (Fall 3) | nicht wiederholen; Nutzer:in informieren oder andere Eingabe wählen |
| Protokollfehler (fehlende `_meta`) | Client korrigieren, kein Modell-Retry |
| Verbindungsabbruch, Zeitüberschreitung | Wiederholung beim Client oder Host, möglichst nur für lesende Tools |

> **Merksatz:** Tool-Fehler erreichen das Modell als Text und sind korrigierbar; Protokollfehler betreffen den Client und sind Programmierfehler.

## Fazit

- Zwei Ebenen: `error` für ungültige Nachrichten, `result` mit `isError: true` für Tool-Fehler.
- Die Fehlermeldung des Tools ist die Debugging-Information; ihre Qualität bestimmt, ob ein Retry gelingt.
- `ToolError` macht erwartete Fehler für das Modell sichtbar.

Die Übung löst Fehlerfälle selbst aus und dokumentiert Ursache und Retry-Eignung.
