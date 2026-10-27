# Lab 2.3 – Übung: Fehlerfälle provozieren und verstehen

**Dauer:** ca. 20 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Nein – analysiert den Server aus Lab 2.2; die Erweiterung ändert nur den Playground
**Arbeitsdatei:** `playground/server.py` (Server aus Lab 2.2) und `playground/fehlerprotokoll.md`
**Starter:** keiner (nutzt das Ergebnis von Lab 2.2)
**Vergleichsbeispiel:** `examples/m02-protocol-and-messages/l02-first-tool/error_cases.py`

## Vorbereitung

- Terminal im Ordner `output/project/`, venv aktiv.
- `playground/server.py` enthält `get_ticket` aus Lab 2.2 und läuft (`Tools: get_ticket`).

## Aufgaben

1. Rufe das Tool mit einem falschen Parameternamen auf: `python shared/script_client.py --server playground/server.py --call get_ticket '{"id": "VAN-102"}'`. Notiere `is_error` und die erste Zeile der Meldung.
2. Rufe das Tool mit einem Zahlenwert auf (`'{"ticket_id": 102}'`) und mit einem unbekannten Ticket (`'{"ticket_id": "VAN-999"}'`). Notiere beide Meldungen.
3. Rufe ein nicht vorhandenes Tool auf: `--call get_tickets '{"ticket_id": "VAN-102"}'`. Notiere die Meldung.
4. Führe `python examples/m02-protocol-and-messages/l02-first-tool/error_cases.py` aus und ordne die fünf Fälle dem Skript-Client-Ergebnis aus Aufgabe 1 bis 3 zu.
5. Sende per `playground/raw_requests.py` (Lab 2.1) einen Request mit unbekannter Methode `nope/list` und `id` 4. Notiere Code und Meldung.
6. Lege `playground/fehlerprotokoll.md` an: je Fehlerfall eine Zeile mit Aufruf, Fehlerebene (Protokollfehler oder Tool-Fehler), Ursache, Retry sinnvoll (ja/nein, an welcher Stelle).
7. Notiere zwei Angaben, die in der Fehlerantwort für Debugging fehlen.

## Checkpoint

- Der Aufruf mit `id` liefert `is_error=True` und `Field required` für `ticket_id`.
- `VAN-999` liefert `Ticket VAN-999 nicht gefunden`, das unbekannte Tool `Unknown tool: get_tickets`.
- `error_cases.py` gibt fünf Fälle aus, der fünfte mit `MCPError code=-32602`.
- Der Request mit `nope/list` liefert ein `error`-Objekt mit Code `-32601`.

## Abschlusskriterien

- `playground/fehlerprotokoll.md` enthält mindestens vier Fälle mit Ursache und Ebene.
- Zu jedem Fall steht, ob und wo ein Retry ansetzt.
- Zwei fehlende Debug-Angaben sind benannt.

## Erweiterung (optional)

Verbessere die Fehlermeldung in `get_ticket`: Lehne Werte, die nicht dem Muster `VAN-<Zahl>` entsprechen, mit einem `ToolError` ab, der das erwartete Format und eine Beispiel-ID nennt. Rufe das Tool danach mit `abc` auf.

## Fallback

- Ohne Zeit zum eigenen Auslösen: `error_cases.py` ausführen und das Fehlerprotokoll aus der Ausgabe füllen (Plenumsvariante).
- Ohne `raw_requests.py` entfällt Aufgabe 5; die Antwort ist in `l03-error-patterns-thx.md` abgedruckt.
