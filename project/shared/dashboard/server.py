"""Mini-Dashboard der Tool-Calls (Showcase D, Lab 6.1/8.1): nur Standardbibliothek, Port 8080.

Liest die JSONL-Datei aus TOOL_CALL_LOG (eine JSON-Zeile je Tool-Call, geschrieben von
logging_config.py) und zeigt Kennzahlen, Alarm und die Zeitleiste im Browser.
Start:  TOOL_CALL_LOG=logs/tool_calls.jsonl python shared/dashboard/server.py
Routen: GET / (HTML) · GET /api/calls (JSON) · GET /health
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HTML = Path(__file__).with_name("index.html").read_bytes()
ALERT_DENIED_THRESHOLD, ALERT_WINDOW_S = 3, 60  # entspricht ALERT_RULES in logging_config.py


def read_calls(path: Path, limit: int = 200) -> list[dict]:
    if not path.exists():
        return []
    calls = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            calls.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return calls


def summarize(calls: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    recent_denied = 0
    for c in calls:
        try:
            age = (now - datetime.fromisoformat(c["ts"])).total_seconds()
        except (KeyError, ValueError):
            continue
        if c.get("status") == "denied" and age <= ALERT_WINDOW_S:
            recent_denied += 1
    by_status: dict[str, int] = {}
    for c in calls:
        by_status[c.get("status", "?")] = by_status.get(c.get("status", "?"), 0) + 1
    return {
        "total": len(calls),
        "by_status": by_status,
        "alert": recent_denied >= ALERT_DENIED_THRESHOLD,
        "recent_denied": recent_denied,
        "generated_at": time.strftime("%H:%M:%S"),
    }


class Handler(BaseHTTPRequestHandler):
    log_path = Path(os.getenv("TOOL_CALL_LOG", "logs/tool_calls.jsonl"))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/":
            self._send(200, HTML, "text/html; charset=utf-8")
        elif path == "/api/calls":
            calls = read_calls(self.log_path)
            payload = {"summary": summarize(calls), "calls": calls}
            self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
        elif path == "/health":
            self._send(200, b'{"status": "ok"}', "application/json")
        else:
            self._send(404, b'{"error": "not_found"}', "application/json")

    def log_message(self, fmt: str, *args) -> None:
        pass


def make_server(host: str = "127.0.0.1", port: int = 8080) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    host = os.getenv("DASHBOARD_HOST", "127.0.0.1")
    port = int(os.getenv("DASHBOARD_PORT", "8080"))
    print(f"[dashboard] http://{host}:{port} liest {Handler.log_path}", file=sys.stderr, flush=True)
    make_server(host, port).serve_forever()
