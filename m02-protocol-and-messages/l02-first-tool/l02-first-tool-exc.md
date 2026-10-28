# Lab 2.2 – Übung: Erstes eigenes Tool implementieren

**Dauer:** ca. 30 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Ja – `playground/server.py` mit `get_ticket` ist die Basis für Lab 2.3 und Lab 3.2
**Arbeitsdatei:** `playground/server.py`
**Starter:** `starters/m02-l02-first-tool.py`
**Vergleichsbeispiel:** `examples/m02-protocol-and-messages/l02-first-tool/server.py`

## Vorbereitung

- Bash-Terminal (Windows: Git Bash) im Ordner `output/project/`, venv aktiv.
- `playground/raw_requests.py` aus Lab 2.1 ist vorhanden (sonst: `cp examples/m02-protocol-and-messages/l01-jsonrpc/raw_requests.py playground/raw_requests.py`).
- Der Server aus Lab 1.2 läuft mit dem Skript-Client (`Tools: (keine)`).
- Die Ticketdaten stehen in `shared/mock_api/tickets.json` (IDs `VAN-101` bis `VAN-106`); der Starter bindet sie über `backend` an.

## Aufgaben

1. Kopiere den Starter nach `playground/server.py` (`cp starters/m02-l02-first-tool.py playground/server.py`) und prüfe mit `python shared/script_client.py --server playground/server.py`, dass der Server läuft und `Tools: (keine)` zeigt.
2. Implementiere die Funktion `get_ticket(ticket_id: str) -> dict` (`TODO(Aufgabe 2)`): registriere sie mit `@mcp.tool(annotations=ToolAnnotations(read_only_hint=True))`, schreibe einen Docstring, der Zweck und eine Beispiel-ID nennt, und gib `backend.get_ticket(ticket_id)` zurück.
3. Fange `NotFound` ab und melde es als `ToolError` (`TODO(Aufgabe 3)`).
4. Rufe das Tool für `VAN-102` auf: `python shared/script_client.py --server playground/server.py --call get_ticket '{"ticket_id": "VAN-102"}'`. Notiere `status`, `priority` und `version`.
5. Rufe das Tool mit `VAN-999` auf und notiere die Fehlermeldung.
6. Ergänze in `playground/raw_requests.py` am Ende des `try`-Blocks einen Request `tools/call` mit `id` 6: `"params": {"name": "get_ticket", "arguments": {"ticket_id": "VAN-102"}, "_meta": META}`. Führe `python playground/raw_requests.py` aus (Variable `SERVER` zeigt weiter auf `playground/server.py`). Notiere, in welchem Feld der Ticket-Text steht und welchen Wert `isError` hat.
7. Starte den Inspector mit `npx @modelcontextprotocol/inspector python playground/server.py`, klicke **Connect**, öffne den Tab **Tools**, klicke **List Tools** und wähle `get_ticket`. Lies Beschreibung und Pflichtparameter, trage `VAN-105` in das Feld `ticket_id` ein, klicke **Run Tool** und notiere den Wert von `assignee`.
8. Vergleiche `playground/server.py` mit dem Vergleichsbeispiel.

## Checkpoint

- Der Skript-Client zeigt `Tools: get_ticket`.
- Der Aufruf mit `VAN-102` liefert `is_error=False` und ein Ticket mit `"version": 3`.
- Der Aufruf mit `VAN-999` liefert `is_error=True` mit der Meldung `Ticket VAN-999 nicht gefunden`.
- Die Rohantwort auf `id` 6 enthält `"isError":false` und den Ticket-Text in `result.content[0].text`.
- Der Inspector zeigt die Beschreibung aus dem Docstring und `ticket_id` als Pflichtfeld.

## Abschlusskriterien

- `playground/server.py` enthält ein registriertes Tool `get_ticket` mit Typhinweis, Docstring und `ToolError`.
- Erfolg und Fehlerfall sind über einen Client nachgewiesen.
- Der Server startet weiterhin mit `mcp.run()` über stdio.

## Erweiterung (optional)

Ergänze die Resource `tickets://{ticket_id}` (`TODO(Erweiterung)`) mit `@mcp.resource("tickets://{ticket_id}", mime_type="application/json")`. Unbekannte Tickets melden `ResourceNotFoundError`. Prüfe sie im Inspector unter „Resources“ mit `tickets://VAN-104`.

## Fallback

- Ohne Inspector: Skript-Client für alle Aufrufe verwenden (`--call get_ticket '{"ticket_id": "VAN-105"}'`); Beschreibung und Pflichtparameter stehen in der Rohantwort auf `tools/list` (Aufgabe 6).
- Ohne lauffähiges `raw_requests.py`: `python examples/m02-protocol-and-messages/l02-first-tool/raw_requests.py playground/server.py` ausführen.
- Bei einem nicht lauffähigen Server: Vergleichsbeispiel nach `playground/server.py` kopieren und ab Aufgabe 4 fortfahren.
