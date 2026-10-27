# Lab 2.3 – Lösung: Fehlerfälle provozieren und verstehen

## Aufgabe 1: Falscher Parameter

```bash
python shared/script_client.py --server playground/server.py --call get_ticket '{"id": "VAN-102"}'
```

`is_error=True`, Meldung beginnt mit:

```text
Error executing tool get_ticket: 1 validation error for get_ticketArguments
ticket_id
  Field required [type=missing, input_value={'id': 'VAN-102'}, input_type=dict]
```

## Aufgabe 2: Falscher Typ und unbekanntes Ticket

| Aufruf | `is_error` | Meldung (erste Zeile) |
| --- | --- | --- |
| `{"ticket_id": 102}` | True | `Error executing tool get_ticket: 1 validation error for get_ticketArguments` |
| `{"ticket_id": "VAN-999"}` | True | `Error executing tool get_ticket: Ticket VAN-999 nicht gefunden` |

Der Typfehler nennt in der Folgezeile `Input should be a valid string`.

## Aufgabe 3: Unbekanntes Tool

```text
is_error=True
Unknown tool: get_tickets
```

## Aufgabe 4: error_cases.py

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

Fall 1 entspricht Aufgabe 1, Fall 2 und 3 der Aufgabe 2, Fall 4 der Aufgabe 3. Fall 5 ist ein Protokollfehler beim Lesen von `tickets://VAN-999` (Resource aus Lab 2.2, Erweiterung). Das Skript gibt auf stderr zusätzlich Logzeilen des SDK aus (`Tool 'get_ticket' failed: …`); sie gehören nicht zur Antwort.

## Aufgabe 5: Unbekannte Methode

```python
send(proc, {"jsonrpc": "2.0", "id": 4, "method": "nope/list", "params": {"_meta": META}})
```

```json
{"jsonrpc":"2.0","id":4,"error":{"code":-32601,"message":"Method not found","data":"nope/list"}}
```

Protokollfehler (`error`, Code `-32601`), weil die Methode nicht existiert; der Tool-Code läuft nicht.

## Aufgabe 6: Fehlerprotokoll

`playground/fehlerprotokoll.md`:

| Aufruf | Ebene | Ursache | Retry |
| --- | --- | --- | --- |
| `get_ticket {"id": …}` | Tool-Fehler | Pflichtfeld `ticket_id` fehlt | ja, Modell/Host mit korrektem Parameternamen |
| `get_ticket {"ticket_id": 102}` | Tool-Fehler | Typ `integer` statt `string` | ja, Modell/Host mit Text |
| `get_ticket {"ticket_id": "VAN-999"}` | Tool-Fehler | Ticket existiert nicht | nein, andere ID wählen |
| `get_tickets` | Tool-Fehler | Toolname unbekannt | ja, Namen aus `tools/list` nehmen |
| `tickets://VAN-999` lesen | Protokollfehler | Resource existiert nicht | nein |
| `nope/list` | Protokollfehler | Methode unbekannt | nein, Client-Fehler beheben |

## Aufgabe 7: Fehlende Angaben

Mögliche Antworten, jeweils im Antworttext nicht enthalten:

- eine Liste der erlaubten bzw. erwarteten Werte (z. B. Format `VAN-<Zahl>`),
- ein Hinweis, ob ein Retry sinnvoll ist,
- eine eigene Fehlerkennung (nur Freitext; Code und Meldung unterscheiden sich nicht maschinenlesbar),
- die Ursache bei normalen Exceptions (nur im stderr-Log des Servers).

## Erweiterung: Meldung mit Format

```python
import re
...
    if not re.fullmatch(r"VAN-\d{1,6}", ticket_id):
        raise ToolError(f"Ungültige Ticket-ID '{ticket_id}': erwartet Format VAN-<Zahl>, z. B. VAN-102")
```

Der Check steht vor dem `try`-Block in `get_ticket`. Aufruf mit `abc`:

```text
is_error=True
Error executing tool get_ticket: Ungültige Ticket-ID 'abc': erwartet Format VAN-<Zahl>, z. B. VAN-102
```

Die Meldung nennt jetzt das erwartete Format; das Modell kann den nächsten Versuch korrigieren.
