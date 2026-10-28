"""Starter Lab 3.2: Kontextschema. Kopieren nach playground/context.py und vervollständigen.

Anleitung für playground/server.py (Stand Lab 2.2); dort stehen keine TODO-Marker, die Schritte stehen hier:
  - TODO(Aufgabe 4): oben "from context import SESSION_SCHEMA, session" importieren;
      in get_ticket: session.tool_calls += 1, Ergebnis in ticket ablegen, session.remember_ticket(ticket), return ticket
  - TODO(Aufgabe 5): zweites Tool get_deployment_log(ticket_id: str | None = None, tail: int = 20) ergänzen:
      resolved = session.resolve_ticket_id(ticket_id); bei None: raise ToolError("Keine ticket_id angegeben ...")
      deployment = backend.latest_deployment(resolved)   (wirft NotFound, wenn es kein Deployment gibt -> ToolError)
      session.remember_deployment(deployment); Rückgabe: Metadaten plus deployment["log"][-tail:]
  - TODO(Erweiterung): Resource context://session mit SESSION_SCHEMA und session.to_view() ergänzen

Session-State lebt nur so lange wie der Server-Prozess. Persistentes Memory gehört nicht in dieses Modul.
Das LLM sieht diesen Kontext nicht direkt, sondern nur Tool-Ergebnisse; "sichtbar" beschreibt die Resource-Ansicht.
"""

from dataclasses import dataclass, field

# TODO(Aufgabe 1): Schema vervollständigen: Feld · Quelle · Lebensdauer · sichtbar in der Resource context://session
SESSION_SCHEMA = [
    {"feld": "last_ticket", "quelle": "Tool get_ticket", "lebensdauer": "bis zum nächsten get_ticket", "sichtbar": "id, title, status, version"},
]


@dataclass
class SessionContext:
    last_ticket: dict | None = None
    # TODO(Aufgabe 1): Feld last_deployment ergänzen (eigenes Feld, damit das zweite Tool das erste nicht überschreibt)
    ticket_versions: dict[str, int] = field(default_factory=dict)  # zuletzt gelesene Version je Ticket (Nachvollziehbarkeit)
    tool_calls: int = 0

    def remember_ticket(self, ticket: dict) -> None:
        self.last_ticket = {k: ticket[k] for k in ("id", "title", "status", "version")}
        self.ticket_versions[ticket["id"]] = ticket["version"]

    def remember_deployment(self, deployment: dict) -> None:
        raise NotImplementedError("TODO(Aufgabe 2): Ausschnitt id, service, version, status in last_deployment ablegen")

    def resolve_ticket_id(self, explicit: str | None) -> str | None:
        raise NotImplementedError("TODO(Aufgabe 3): explizite ID bevorzugen, sonst die ID des zuletzt abgefragten Tickets")

    def to_view(self) -> dict:
        raise NotImplementedError("TODO(Aufgabe 3): nur last_ticket und last_deployment zurückgeben (Ansicht für die Resource)")


session = SessionContext()

if __name__ == "__main__":
    session.remember_ticket({"id": "VAN-102", "title": "Beispiel", "status": "open", "version": 3})
    print("Kontext nach Ticket:", session.last_ticket)
    print("Aufgelöste Ticket-ID:", session.resolve_ticket_id(None))
