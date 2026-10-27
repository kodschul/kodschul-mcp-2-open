"""Starter Lab 7.1: Zugriffskontrolle im Server. Kopieren nach playground/auth.py und vervollständigen.

Die Regeln kommen aus der Policy (playground/policy.md). Danach in playground/server.py:
  - TODO(Aufgabe 4): "from auth import PolicyDenied, authorize" importieren
  - TODO(Aufgabe 5): jedes Tool beginnt im try-Block mit authorize("<toolname>") (Schreib-Tool mit confirmed=confirmed),
    PolicyDenied wird mit error_result(exc.code, exc.message, **exc.details) beantwortet
  - TODO(Aufgabe 6): update_ticket_status bekommt den Parameter confirmed: bool = False
"""

import os

# TODO(Aufgabe 1): Allow-List je Rolle (viewer: nur lesen, operator: lesen und schreiben)
ROLE_TOOLS: dict[str, frozenset[str]] = {
    "viewer": frozenset({"get_ticket", "get_deployment_log"}),
}
WRITE_TOOLS = frozenset({"update_ticket_status"})
DEFAULT_ROLE = "viewer"


class PolicyDenied(Exception):
    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details


def current_role() -> str:
    # Rolle nur aus der Prozessumgebung, nie aus Tool-Argumenten oder Modell-Ausgaben
    return os.getenv("VANTRA_ROLE", DEFAULT_ROLE)


def authorize(tool: str, confirmed: bool = False, role: str | None = None) -> str:
    """Prüft einen Tool-Aufruf; gibt die Rolle zurück oder wirft PolicyDenied."""
    role = role or current_role()
    # TODO(Aufgabe 2): Tool nicht in der Allow-List der Rolle -> PolicyDenied("policy_denied", ..., role=role, tool=tool)
    # TODO(Aufgabe 3): Schreib-Tool ohne confirmed -> PolicyDenied("confirmation_required", ..., role=role, tool=tool)
    raise NotImplementedError("TODO(Aufgabe 2/3): Prüfungen in authorize() ergänzen")
