"""Gemockte Ticket- und Deployment-API (nur Standardbibliothek), Port 8001.

Start:  python shared/mock_api/app.py
Routen: GET /health · GET /tickets · GET /tickets/<id> · PATCH /tickets/<id>
        GET /tickets/<id>/deployment · POST /reset
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.mock_api.store import InvalidStatus, NotFound, Store, VersionConflict  # noqa: E402

STORE = Store()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict | list) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _route(self, method: str) -> None:
        parts = [p for p in self.path.split("?")[0].split("/") if p]
        try:
            if method == "GET" and parts == ["health"]:
                return self._send(200, {"status": "ok"})
            if method == "GET" and parts == ["tickets"]:
                return self._send(200, STORE.list_tickets())
            if method == "GET" and len(parts) == 2 and parts[0] == "tickets":
                return self._send(200, STORE.get_ticket(parts[1]))
            if method == "GET" and len(parts) == 3 and parts[0] == "tickets" and parts[2] == "deployment":
                return self._send(200, STORE.latest_deployment(parts[1]))
            if method == "PATCH" and len(parts) == 2 and parts[0] == "tickets":
                length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(length) or b"{}")
                return self._send(200, STORE.update_ticket(parts[1], payload.get("status", ""), payload.get("expected_version")))
            if method == "POST" and parts == ["reset"]:
                STORE.reset()
                return self._send(200, {"status": "reset"})
            self._send(404, {"error": "not_found", "message": f"Route {method} {self.path} unbekannt"})
        except NotFound as exc:
            self._send(404, {"error": "not_found", "message": str(exc)})
        except InvalidStatus as exc:
            self._send(422, {"error": "invalid_status", "message": str(exc)})
        except VersionConflict as exc:
            self._send(409, {"error": "version_conflict", "expected_version": exc.expected, "current_version": exc.current})

    def do_GET(self) -> None:
        self._route("GET")

    def do_PATCH(self) -> None:
        self._route("PATCH")

    def do_POST(self) -> None:
        self._route("POST")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[mock-api] {self.address_string()} {fmt % args}", file=sys.stderr, flush=True)


def make_server(host: str = "127.0.0.1", port: int = 8001) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    host = os.getenv("MOCK_API_HOST", "127.0.0.1")
    port = int(os.getenv("MOCK_API_PORT", "8001"))
    print(f"[mock-api] läuft auf http://{host}:{port}", file=sys.stderr, flush=True)
    make_server(host, port).serve_forever()
