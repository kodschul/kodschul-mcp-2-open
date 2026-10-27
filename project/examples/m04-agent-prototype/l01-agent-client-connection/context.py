"""Kontextschema des Vantra Ops Agent (Lab 3.2).

Session-State: lebt nur so lange wie der Server-Prozess (= eine stdio-Session).
Persistentes Memory (Präferenzen, Historie über Sessions) liegt bewusst NICHT hier.
"""

from dataclasses import dataclass, field

# Schema: Feld · Quelle · Lebensdauer · Sichtbarkeit für das LLM
SESSION_SCHEMA = [
    {"feld": "last_ticket", "quelle": "Tool get_ticket", "lebensdauer": "bis zum nächsten get_ticket", "an_llm": "id, title, status, version"},
    {"feld": "last_deployment", "quelle": "Tool get_deployment_log", "lebensdauer": "bis zum nächsten get_deployment_log", "an_llm": "id, service, version, status"},
    {"feld": "ticket_versions", "quelle": "get_ticket, update_ticket_status", "lebensdauer": "Session", "an_llm": "nein (nur Server)"},
    {"feld": "tool_calls", "quelle": "jeder Tool-Aufruf", "lebensdauer": "Session", "an_llm": "nein (nur Server)"},
]


@dataclass
class SessionContext:
    last_ticket: dict | None = None
    last_deployment: dict | None = None
    ticket_versions: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0

    # Jedes Tool schreibt nur in sein eigenes Feld: get_deployment_log überschreibt last_ticket nie.
    def remember_ticket(self, ticket: dict) -> None:
        self.last_ticket = {k: ticket[k] for k in ("id", "title", "status", "version")}
        self.ticket_versions[ticket["id"]] = ticket["version"]

    def remember_deployment(self, deployment: dict) -> None:
        self.last_deployment = {k: deployment[k] for k in ("id", "service", "version", "status")}

    def resolve_ticket_id(self, explicit: str | None) -> str | None:
        """Explizite ID gewinnt; sonst das zuletzt abgefragte Ticket ("das Deployment dazu")."""
        if explicit:
            return explicit
        return self.last_ticket["id"] if self.last_ticket else None

    def to_llm_view(self) -> dict:
        """Nur dieser Ausschnitt wird dem LLM angezeigt (Resource context://session)."""
        return {"last_ticket": self.last_ticket, "last_deployment": self.last_deployment}


session = SessionContext()
