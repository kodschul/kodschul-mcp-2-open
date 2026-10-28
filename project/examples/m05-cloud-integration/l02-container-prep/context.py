"""Kontextschema des Vantra Ops Agent (Lab 3.2).

Session-State: lebt nur so lange wie der Server-Prozess (= eine stdio-Session).
Persistentes Memory (Präferenzen, Historie über Sessions) liegt bewusst NICHT hier.

Was das LLM sieht: nur Tool-Ergebnisse und die Nachrichtenliste des Clients. Dieser Kontext
erreicht das Modell nicht direkt; die Spalte "sichtbar" legt fest, was die Resource
context://session (Ansicht für Menschen und Hosts) davon zeigt.
"""

from dataclasses import dataclass, field

# Schema: Feld · Quelle · Lebensdauer · sichtbar in der Resource context://session
SESSION_SCHEMA = [
    {"feld": "last_ticket", "quelle": "Tool get_ticket", "lebensdauer": "bis zum nächsten get_ticket", "sichtbar": "id, title, status, version"},
    {"feld": "last_deployment", "quelle": "Tool get_deployment_log", "lebensdauer": "bis zum nächsten get_deployment_log", "sichtbar": "id, service, version, status"},
    {"feld": "ticket_versions", "quelle": "get_ticket (ab Lab 3.3 auch update_ticket_status)", "lebensdauer": "Session", "sichtbar": "nein (nur Server)"},
    {"feld": "tool_calls", "quelle": "jeder Tool-Aufruf", "lebensdauer": "Session", "sichtbar": "nein (nur Server)"},
]


@dataclass
class SessionContext:
    last_ticket: dict | None = None
    last_deployment: dict | None = None
    ticket_versions: dict[str, int] = field(default_factory=dict)  # zuletzt gelesene Version je Ticket (Nachvollziehbarkeit)
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

    def to_view(self) -> dict:
        """Sichtbarer Ausschnitt für die Resource context://session (nicht automatisch beim LLM)."""
        return {"last_ticket": self.last_ticket, "last_deployment": self.last_deployment}


session = SessionContext()
