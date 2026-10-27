# Lab 3.3: Zwei Agenten, ein Kontext

**Leitfragen:**

<details>
<summary>Wie wird ein Konflikt erkannt?</summary>

Der Schreibende sendet die zuvor gelesene Version mit (`expected_version`). Weicht sie von der aktuellen Version des Tickets ab, hat jemand dazwischen geschrieben, und der Server meldet `version_conflict`.

</details>

<details>
<summary>Welche Strategie passt zu einem Ops-Szenario mit niedriger Fehlertoleranz?</summary>

Versionsprüfung mit hartem Konfliktfehler und erneutem Lesen: Nichts wird still überschrieben. Zusammenführen nur bei eindeutig vereinbaren Änderungen, Sperren nur für kurze, kritische Schreibvorgänge.

</details>

- Zwei Agenten auf demselben Ticket erzeugen das Lost-Update-Problem: Der spätere Schreibvorgang überschreibt den früheren, ohne ihn zu kennen.
- Ein Versionsfeld macht den Konflikt sichtbar, bevor Daten verloren gehen.

## Das Problem: stilles Überschreiben

```text
Zeit ─►   Agent A                       Agent B                      Ticket VAN-102
  t1      liest: open, Version 3        liest: open, Version 3       open, v3
  t2      überlegt ...                  setzt in_progress            in_progress, v4
  t3      setzt resolved (ohne Prüfung)                              resolved, v5   ← B's Änderung ist weg
```

Mit Versionsprüfung scheitert t3: A erwartet Version 3, aktuell ist 4.

## Synchronisationsstrategien

| Strategie | Prinzip | Vorteil | Nachteil | Passt zu |
| --- | --- | --- | --- | --- |
| Versionsprüfung (optimistisch) | Schreiben nur, wenn `expected_version` der aktuellen Version entspricht | einfach, keine Wartezeit, Konflikt wird gemeldet | Aufrufer muss neu lesen und wiederholen | Ops-Tickets, seltene Konflikte |
| Sperre (pessimistisch) | Wer schreiben will, sperrt das Objekt vorab | verhindert Konflikte im Voraus | Wartezeiten, verwaiste Sperren (Timeout nötig) | kurze, kritische Schreibvorgänge |
| Zusammenführen | Änderungen werden verrechnet, z. B. verschiedene Felder oder gleicher Zielstatus | weniger Abbrüche | fachliche Regeln nötig, Fehlerquelle bei Widersprüchen | idempotente oder feldgetrennte Änderungen |

Bei niedriger Fehlertoleranz gilt: lieber ein sichtbarer Konflikt als eine falsch zusammengeführte Änderung.

## Versionsprüfung im Projekt

Die Daten kommen aus der Mock-API (`shared/mock_api/store.py`). Jede erfolgreiche Änderung erhöht `version` um 1; `update_ticket` prüft die erwartete Version unter einer Sperre:

```python
# shared/mock_api/store.py (Ausschnitt)
if expected_version is not None and ticket["version"] != expected_version:
    raise VersionConflict(ticket_id, expected_version, ticket["version"])
ticket["status"] = status
ticket["version"] += 1
```

Das Schreib-Tool des Servers reicht die Version durch und übersetzt die Ausnahme in einen strukturierten Fehler (`examples/m03-context-and-state/l03-multi-agent-sync/server.py`):

```python
@mcp.tool(annotations=WRITE)
def update_ticket_status(ticket_id: str, status: str, expected_version: int) -> Any:
    """Ticket-Status ändern (open, in_progress, resolved, closed). expected_version ist die zuvor gelesene Version des Tickets."""
    session.tool_calls += 1
    try:
        ticket = backend.update_ticket(ticket_id, status, expected_version)
    except NotFound as exc:
        raise ToolError(str(exc)) from exc
    except InvalidStatus as exc:
        return error_result("invalid_status", str(exc), ticket_id=ticket_id)
    except VersionConflict as exc:
        return error_result(
            "version_conflict",
            f"Ticket {ticket_id} wurde zwischenzeitlich geändert. Neu lesen mit get_ticket und erneut versuchen.",
            ticket_id=ticket_id, expected_version=exc.expected, current_version=exc.current,
        )
    session.remember_ticket(ticket)
    return ticket
```

- `expected_version` ist Pflichtargument: Das Modell muss die gelesene Version mitsenden.
- Der Rückgabetyp ist `Any`, weil das Tool entweder ein Ticket oder ein `CallToolResult` liefert; `dict | CallToolResult` lehnt das SDK ab.
- Der Fehler ist ein Ergebnis mit `isError: true`, kein JSON-RPC-Fehler. Die Meldung sagt dem Agenten, was zu tun ist.

Fehlerergebnis bei `expected_version` 3 und aktueller Version 4:

```json
{"error": "version_conflict", "message": "Ticket VAN-102 wurde zwischenzeitlich geändert. Neu lesen mit get_ticket und erneut versuchen.", "ticket_id": "VAN-102", "expected_version": 3, "current_version": 4}
```

## Zwei Agenten lokal

Zwei stdio-Server sind zwei Prozesse mit getrennten Daten. Gemeinsamer Zustand entsteht erst über die Mock-API als HTTP-Dienst (Port 8001), die beide Serverprozesse per `MOCK_API_URL` nutzen.

| Baustein | Aufgabe |
| --- | --- |
| `python shared/mock_api/app.py` | startet die Mock-API (gemeinsamer Zustand) |
| `shared/second_client.py` | liest ein Ticket, wartet `--hold` Sekunden, schreibt mit der gelesenen Version |
| `MOCK_API_URL=http://localhost:8001` | schaltet den Server von prozesslokalen Daten auf die HTTP-Mock-API |
| `curl -X POST localhost:8001/reset` | setzt Tickets auf den Ausgangszustand zurück |

## Zusammenführen als Erweiterung

Ein Konflikt ist unkritisch, wenn der gewünschte Status schon gilt (idempotent). Dann kann der Server das aktuelle Ticket zurückgeben statt einen Fehler zu melden. Bei abweichendem Status bleibt es beim Konflikt.

## Fazit

- Ohne Versionsprüfung überschreibt der spätere Schreibvorgang still.
- `expected_version` plus `version_conflict` macht den Konflikt sichtbar und nennt den Weg zur Lösung.
- Für Ops gilt: Konflikt melden, neu lesen, bewusst wiederholen; Zusammenführen nur bei Gleichheit des Ziels.

Die Übung löst den Konflikt mit zwei Clients aus und ergänzt die Versionsprüfung im Server.
