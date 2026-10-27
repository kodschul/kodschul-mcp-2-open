"""Zugriffskontrolle des Vantra Ops Agent (Lab 7.1): Rollen, Tool-Allow-List, Bestätigungspflicht.

Die Regeln stehen in policy.md; dieses Modul setzt sie im Server durch (nicht im Client).
Die Rolle kommt aus der Umgebung des Server-Prozesses (VANTRA_ROLE), nie aus Tool-Argumenten
oder Modell-Ausgaben. Unbekannte Rollen und unbekannte Tools werden abgelehnt (deny by default).
"""

import os

ROLE_TOOLS: dict[str, frozenset[str]] = {
    "viewer": frozenset({"get_ticket", "get_deployment_log"}),
    "operator": frozenset({"get_ticket", "get_deployment_log", "update_ticket_status"}),
}
WRITE_TOOLS = frozenset({"update_ticket_status"})
DEFAULT_ROLE = "viewer"


class PolicyDenied(Exception):
    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details


def current_role() -> str:
    return os.getenv("VANTRA_ROLE", DEFAULT_ROLE)


def authorize(tool: str, confirmed: bool = False, role: str | None = None) -> str:
    """Prüft einen Tool-Aufruf; gibt die Rolle zurück oder wirft PolicyDenied."""
    role = role or current_role()
    if tool not in ROLE_TOOLS.get(role, frozenset()):
        raise PolicyDenied("policy_denied", f"Rolle '{role}' darf das Tool '{tool}' nicht aufrufen.", role=role, tool=tool)
    if tool in WRITE_TOOLS and not confirmed:
        raise PolicyDenied(
            "confirmation_required",
            f"Das Schreib-Tool '{tool}' braucht eine Bestätigung durch den Nutzer (confirmed=true).",
            role=role,
            tool=tool,
        )
    return role
