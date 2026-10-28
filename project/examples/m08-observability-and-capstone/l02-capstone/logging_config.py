"""Strukturiertes Logging und Tool-Call-Protokoll (Lab 8.1).

- Log-Zeilen als JSON auf stderr (stdout gehört bei stdio dem JSON-RPC-Protokoll).
- Jeder Tool-Aufruf landet als eine Zeile in einer JSONL-Datei (TOOL_CALL_LOG), die das Dashboard liest.
- Datenschutz: protokolliert werden Tool, Rolle, Status, Dauer und Argumente. Nie Ticket-Texte,
  Log-Inhalte oder Secrets.
"""

import functools
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from mcp.types import CallToolResult

DENIED_CODES = {"policy_denied", "confirmation_required"}

# Beispielalarm: drei abgelehnte Aufrufe innerhalb von 60 Sekunden deuten auf einen missbrauchten oder fehlerhaften Client.
ALERT_RULES = [
    {"name": "viele-abgelehnte-aufrufe", "status": "denied", "schwelle": 3, "fenster_s": 60, "schwere": "hoch"},
    {"name": "viele-fehler", "status": "error", "schwelle": 5, "fenster_s": 300, "schwere": "mittel"},
]


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))
        return json.dumps(entry, ensure_ascii=False)


def setup_logging(level: str | None = None) -> logging.Logger:
    logger = logging.getLogger("vantra")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel((level or os.getenv("LOG_LEVEL", "INFO")).upper())
    return logger


def tool_call_log_path() -> Path:
    return Path(os.getenv("TOOL_CALL_LOG", "logs/tool_calls.jsonl"))


def log_tool_call(record: dict) -> None:
    path = tool_call_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


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
    """Decorator für Tool-Funktionen: misst die Dauer und schreibt Log-Zeile und JSONL-Eintrag."""

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
            finally:
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


def evaluate_alerts(records: list[dict], now: datetime | None = None, rules: list[dict] | None = None) -> list[dict]:
    """Prüft die Regeln gegen Tool-Call-Einträge und liefert die ausgelösten Alarme."""
    now = now or datetime.now(timezone.utc)
    fired = []
    for rule in rules or ALERT_RULES:
        count = sum(
            1
            for r in records
            if r.get("status") == rule["status"]
            and (now - datetime.fromisoformat(r["ts"])).total_seconds() <= rule["fenster_s"]
        )
        if count >= rule["schwelle"]:
            fired.append({"regel": rule["name"], "schwere": rule["schwere"], "anzahl": count, "fenster_s": rule["fenster_s"]})
    return fired


def read_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


if __name__ == "__main__":
    for alert in evaluate_alerts(read_records(tool_call_log_path())) or [{"regel": "keine Alarme"}]:
        print(alert)
