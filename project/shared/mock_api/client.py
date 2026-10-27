"""Zugriff der MCP-Server auf die Mock-API: HTTP (MOCK_API_URL gesetzt) oder in-process.

Beide Backends haben dieselbe Schnittstelle und werfen dieselben Ausnahmen
(NotFound, InvalidStatus, VersionConflict aus store.py).
"""

import json
import os
import urllib.error
import urllib.request

from shared.mock_api.store import InvalidStatus, NotFound, Store, VersionConflict

_local_store: Store | None = None


class HttpBackend:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self.base_url + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read() or b"{}")
            if exc.code == 404:
                raise NotFound(payload.get("message", "nicht gefunden")) from exc
            if exc.code == 422:
                raise InvalidStatus(payload.get("message", "ungültig")) from exc
            if exc.code == 409:
                ticket_id = path.split("/")[2]
                raise VersionConflict(ticket_id, payload["expected_version"], payload["current_version"]) from exc
            raise

    def get_ticket(self, ticket_id: str) -> dict:
        return self._request("GET", f"/tickets/{ticket_id}")

    def update_ticket(self, ticket_id: str, status: str, expected_version: int | None = None) -> dict:
        return self._request("PATCH", f"/tickets/{ticket_id}", {"status": status, "expected_version": expected_version})

    def latest_deployment(self, ticket_id: str) -> dict:
        return self._request("GET", f"/tickets/{ticket_id}/deployment")


def get_backend():
    """Liefert HttpBackend, wenn MOCK_API_URL gesetzt ist, sonst den prozesslokalen Store."""
    global _local_store
    url = os.getenv("MOCK_API_URL")
    if url:
        return HttpBackend(url)
    if _local_store is None:
        _local_store = Store()
    return _local_store
