# Lab 8.1 – Lösung: Strukturiertes Logging und Alarm

Vollständige Dateien: `examples/m08-observability-and-capstone/l01-monitoring/` (`logging_config.py`, `server.py`).

## Vorgegeben im Starter: JSON-Formatter und `log_tool_call`

```python
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))   # zusätzliche Felder aus extra={"fields": ...}
        return json.dumps(entry, ensure_ascii=False)
```

`setup_logging` hängt den Formatter an einen `StreamHandler(sys.stderr)`. stdout bleibt dem Protokoll vorbehalten.

```python
def log_tool_call(record: dict) -> None:
    path = tool_call_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

## Aufgabe 1: Tool-Call-Protokoll im Decorator (1a `_classify`, 1b `finally`-Block)

```python
def _classify(result) -> tuple[str, str | None]:
    if isinstance(result, CallToolResult) and result.is_error:
        code = (result.structured_content or {}).get("error", "error")
        if code in DENIED_CODES:
            return "denied", code
        if code == "version_conflict":
            return "conflict", code
        return "error", code
    return "ok", None


def logged(tool_name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            started = time.perf_counter()
            status, code = "ok", None
            try:
                result = fn(*args, **kwargs)
                status, code = _classify(result)
                return result
            except Exception as exc:
                status, code = "error", type(exc).__name__
                raise
            finally:                                   # auch bei Ausnahmen wird protokolliert
                entry = {
                    "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                    "tool": tool_name,
                    "role": os.getenv("VANTRA_ROLE", "viewer"),
                    "status": status,
                    "error_code": code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "args": {k: v for k, v in kwargs.items() if k != "confirmed"},
                }
                log_tool_call(entry)
                level = logging.INFO if status == "ok" else logging.WARNING
                logging.getLogger("vantra").log(level, f"tool_call {tool_name} {status}", extra={"fields": entry})
        return wrapper
    return decorator
```

Gründe: `finally` stellt sicher, dass auch Fehler und Ablehnungen im Protokoll landen. Abgelehnte Aufrufe sind die wichtigsten Einträge für die Erkennung. `confirmed` bleibt aus `args`, weil es eine Steuergröße der Bestätigung ist und kein Nutzdatum.

## Aufgabe 2: Beispielalarm

```python
ALERT_RULES = [
    {"name": "viele-abgelehnte-aufrufe", "status": "denied", "schwelle": 3, "fenster_s": 60, "schwere": "hoch"},
    {"name": "viele-fehler", "status": "error", "schwelle": 5, "fenster_s": 300, "schwere": "mittel"},
]
```

Begründung: Drei Ablehnungen in 60 Sekunden sind für den normalen Betrieb unwahrscheinlich (ein Client kennt seine Rolle), aber nach einer Injection oder bei einem fehlkonfigurierten Client schnell erreicht.

## Aufgabe 3 und 4: `server.py`

```python
from logging_config import logged, setup_logging

log = setup_logging()

@mcp.tool(annotations=READ_ONLY)
@logged("get_ticket")
def get_ticket(ticket_id: TicketId) -> Any: ...

@mcp.tool(annotations=READ_ONLY)
@logged("get_deployment_log")
def get_deployment_log(ticket_id: TicketId | None = None, tail: int = 20) -> Any: ...

@mcp.tool(annotations=WRITE)
@logged("update_ticket_status")
def update_ticket_status(ticket_id: TicketId, status: str, expected_version: int, confirmed: bool = False) -> Any: ...
```

`@logged` steht unter `@mcp.tool(...)`, damit das SDK die dekorierte Funktion registriert; `functools.wraps` erhält Signatur und Docstring für das Tool-Schema.

## Aufgabe 5: Aufrufe erzeugen

Auszug von `logs/tool_calls.jsonl` nach einem Lauf mit Rolle `viewer` (`ts` und `duration_ms` variieren):

```json
{"ts": "2026-10-27T16:56:53.847+00:00", "tool": "get_ticket", "role": "viewer", "status": "ok", "error_code": null, "duration_ms": 0.05, "args": {"ticket_id": "VAN-102"}}
{"ts": "2026-10-27T16:56:53.851+00:00", "tool": "get_deployment_log", "role": "viewer", "status": "ok", "error_code": null, "duration_ms": 0.05, "args": {"ticket_id": null, "tail": 20}}
{"ts": "2026-10-27T16:56:53.852+00:00", "tool": "update_ticket_status", "role": "viewer", "status": "denied", "error_code": "policy_denied", "duration_ms": 0.05, "args": {"ticket_id": "VAN-102", "status": "in_progress", "expected_version": 3}}
```

Drei Läufe ergeben neun Zeilen, davon drei `denied`.

## Aufgabe 6: Dashboard

`http://localhost:8080/api/calls` liefert für neun Aufrufe mit drei Ablehnungen in den letzten 60 Sekunden:

```json
{"summary": {"total": 9, "by_status": {"ok": 6, "denied": 3}, "alert": true, "recent_denied": 3, ...}, "calls": [...]}
```

Die Seite zeigt Summen, die Zeitleiste mit rot markierten `denied`-Zeilen und das Banner „ALARM: 3 abgelehnte Aufrufe in den letzten 60 Sekunden“. Nach 60 Sekunden ohne neue Ablehnung (Beispiel: `{'total': 12, 'by_status': {'ok': 9, 'denied': 3}, 'alert': False, 'recent_denied': 0, …}`) verschwindet das Banner; die Zeilen bleiben.

## Aufgabe 7: Datenschutz

`grep -c -E "Login-Seite|description|confirmed" logs/tool_calls.jsonl` gibt `0` aus. Das Protokoll enthält IDs, Status und Zahlen, keine Ticket-Texte.

## Aufgabe 8: Regel auswerten

```bash
TOOL_CALL_LOG=logs/tool_calls.jsonl python playground/logging_config.py
```

Ausgabe direkt nach drei abgelehnten Aufrufen (mit den Regeln aus Aufgabe 2):

```text
{'regel': 'viele-abgelehnte-aufrufe', 'schwere': 'hoch', 'anzahl': 3, 'fenster_s': 60}
```

Nach Ablauf des Fensters: `{'regel': 'keine Alarme'}`. Die Regel `viele-fehler` löst nicht aus, weil keiner der Aufrufe den Status `error` hat.

## Erweiterung

Zweite Regel (Beispiel):

```python
{"name": "viele-konflikte", "status": "conflict", "schwelle": 2, "fenster_s": 300, "schwere": "mittel"},
```

Aufgabe 8 zeigt danach weiterhin nur `viele-abgelehnte-aufrufe`: der Workflow erzeugt Ablehnungen, keine Versionskonflikte. Auslösen lässt sich die Regel mit dem Zwei-Agenten-Szenario aus Lab 3.3 gegen den dekorierten Server.

Entscheidung (Beispiel, Eintrag in `policy.md`): Bei Alarm „viele-abgelehnte-aufrufe“ benachrichtigt der Betrieb die Verantwortlichen des Services. Sofortmaßnahme: Rolle des betroffenen Servers auf `viewer` setzen und den Client sperren. Aufbewahrung: Protokoll 90 Tage, Zugriff nur für Betrieb und Security (Beispielwert, vom Unternehmen festzulegen).
