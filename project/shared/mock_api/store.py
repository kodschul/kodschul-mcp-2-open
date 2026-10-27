"""Datenhaltung der gemockten Ticket- und Deployment-API (im Speicher).

Wird vom HTTP-Dienst (app.py) und direkt im Server-Prozess (in-process) genutzt.
"""

import copy
import json
import threading
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
VALID_STATUS = ("open", "in_progress", "resolved", "closed")


class NotFound(Exception):
    pass


class VersionConflict(Exception):
    def __init__(self, ticket_id: str, expected: int, current: int):
        super().__init__(f"{ticket_id}: erwartet Version {expected}, aktuell {current}")
        self.ticket_id, self.expected, self.current = ticket_id, expected, current


class InvalidStatus(Exception):
    pass


class Store:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with open(DATA_DIR / "tickets.json", encoding="utf-8") as f:
            self._tickets = {t["id"]: t for t in json.load(f)}
        with open(DATA_DIR / "deployments.json", encoding="utf-8") as f:
            self._deployments = json.load(f)

    def list_tickets(self) -> list[dict]:
        return [copy.deepcopy(t) for t in self._tickets.values()]

    def get_ticket(self, ticket_id: str) -> dict:
        if ticket_id not in self._tickets:
            raise NotFound(f"Ticket {ticket_id} nicht gefunden")
        return copy.deepcopy(self._tickets[ticket_id])

    def update_ticket(self, ticket_id: str, status: str, expected_version: int | None = None) -> dict:
        if status not in VALID_STATUS:
            raise InvalidStatus(f"Status {status!r} ungültig, erlaubt: {', '.join(VALID_STATUS)}")
        with self._lock:
            ticket = self._tickets.get(ticket_id)
            if ticket is None:
                raise NotFound(f"Ticket {ticket_id} nicht gefunden")
            if expected_version is not None and ticket["version"] != expected_version:
                raise VersionConflict(ticket_id, expected_version, ticket["version"])
            ticket["status"] = status
            ticket["version"] += 1
            return copy.deepcopy(ticket)

    def latest_deployment(self, ticket_id: str) -> dict:
        found = [d for d in self._deployments if d["ticket_id"] == ticket_id]
        if not found:
            raise NotFound(f"Kein Deployment zu Ticket {ticket_id} gefunden")
        return copy.deepcopy(max(found, key=lambda d: d["started_at"]))

    def get_deployment(self, deployment_id: str) -> dict:
        for d in self._deployments:
            if d["id"] == deployment_id:
                return copy.deepcopy(d)
        raise NotFound(f"Deployment {deployment_id} nicht gefunden")
