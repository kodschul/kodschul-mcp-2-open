"""Starter Lab 8.1: Logging. Kopieren nach playground/logging_config.py und vervollständigen.

Danach in playground/server.py (Stand Lab 7.1):
  - TODO(Aufgabe 4): "from logging_config import logged, setup_logging" importieren, log = setup_logging() aufrufen
  - TODO(Aufgabe 5): jede Tool-Funktion mit @logged("<toolname>") dekorieren (unter @mcp.tool(...))
  - Dashboard ansehen:  TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py  -> http://localhost:8080

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

# TODO(Aufgabe 3): Beispielalarm definieren: Status, Schwelle, Zeitfenster in Sekunden, Schwere
ALERT_RULES: list[dict] = []


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # TODO(Aufgabe 1): Eintrag als JSON zurückgeben: ts (UTC, ISO), level, logger, message plus record.fields
        raise NotImplementedError("TODO(Aufgabe 1): JsonFormatter.format implementieren")


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
    # TODO(Aufgabe 2): Eintrag als eine JSON-Zeile an die Datei tool_call_log_path() anhängen (Ordner ggf. anlegen)
    raise NotImplementedError("TODO(Aufgabe 2): log_tool_call implementieren")


def logged(tool_name: str):
    """Decorator für Tool-Funktionen: misst die Dauer und schreibt einen Eintrag je Aufruf."""

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            started = time.perf_counter()  # für duration_ms
            result = fn(*args, **kwargs)
            # TODO(Aufgabe 2): Status bestimmen (ok, denied, conflict, error: siehe CallToolResult.is_error und
            #   structured_content["error"]) und log_tool_call({ts, tool, role, status, error_code, duration_ms, args}) aufrufen
            return result

        return wrapper

    return decorator
