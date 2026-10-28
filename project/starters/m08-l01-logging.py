"""Starter Lab 8.1: Logging. Kopieren nach playground/logging_config.py und vervollständigen.

Danach in playground/server.py (Stand Lab 7.1):
  - TODO(Aufgabe 3): "from logging_config import logged, setup_logging" importieren, log = setup_logging() aufrufen
  - TODO(Aufgabe 4): jede Tool-Funktion mit @logged("<toolname>") dekorieren (unter @mcp.tool(...))
  - Dashboard ansehen:  TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py  -> http://localhost:8080
  - Alarmregeln auswerten (Aufgabe 8):  TOOL_CALL_LOG=logs/tool_calls.jsonl python playground/logging_config.py

Datenschutz: protokolliert werden Tool, Rolle, Status, Dauer, Argumente. Nie Ticket-Texte, Log-Inhalte oder Secrets.
Auf stdout schreibt bei stdio nur das Protokoll; Logs gehen nach stderr oder in eine Datei.
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

# TODO(Aufgabe 2): Beispielalarm definieren: Status, Schwelle, Zeitfenster in Sekunden, Schwere
ALERT_RULES: list[dict] = []


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Vorgegeben: eine JSON-Zeile je Log-Eintrag, Zusatzfelder aus extra={"fields": ...}
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
    # Vorgegeben: Eintrag als eine JSON-Zeile anhängen, Ordner bei Bedarf anlegen
    path = tool_call_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _classify(result) -> tuple[str, str | None]:
    """Ordnet ein Tool-Ergebnis einem Status zu: ok, denied, conflict oder error."""
    # error_result(...) aus server.py liefert CallToolResult(is_error=True, structured_content={"error": "<code>", ...})
    # TODO(Aufgabe 1a): bei is_error den Code aus structured_content["error"] lesen;
    #   Code in DENIED_CODES -> ("denied", code), "version_conflict" -> ("conflict", code), sonst ("error", code)
    return "ok", None


def logged(tool_name: str):
    """Decorator für Tool-Funktionen: misst die Dauer und schreibt einen Eintrag je Aufruf."""

    def decorator(fn):
        @functools.wraps(fn)  # behält Name, Signatur und Docstring: daraus baut das SDK das Tool-Schema
        def wrapper(*args, **kwargs):
            started = time.perf_counter()  # für duration_ms
            status, code = "ok", None
            try:
                result = fn(*args, **kwargs)  # die eigentliche Tool-Funktion
                status, code = _classify(result)
                return result
            except Exception as exc:  # Ausnahme (z. B. ToolError): als error zählen und weiterreichen
                status, code = "error", type(exc).__name__
                raise
            finally:  # läuft immer, auch nach return oder raise
                # TODO(Aufgabe 1b): Eintrag bauen und schreiben:
                #   {"ts": <UTC ISO 8601 mit Millisekunden>, "tool": tool_name, "role": VANTRA_ROLE (Standard viewer),
                #    "status": status, "error_code": code, "duration_ms": <gerundet auf 2 Stellen>,
                #    "args": kwargs ohne "confirmed"}
                #   -> log_tool_call(entry) und eine Zeile auf den Logger "vantra":
                #      logging.getLogger("vantra").log(<INFO bei ok, sonst WARNING>, f"tool_call {tool_name} {status}", extra={"fields": entry})
                pass

        return wrapper

    return decorator


# Vorgegeben (keine Aufgabe): wertet ALERT_RULES gegen das Tool-Call-Protokoll aus.
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
