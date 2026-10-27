# Lab 7.1: Zugriffskontrolle und Sandbox-Prinzipien

**Leitfragen:**

<details>
<summary>Welche Tools dürfen nie ohne Bestätigung ausgeführt werden?</summary>

Alle Tools, die Zustand verändern oder nach außen wirken. Im Projekt ist das `update_ticket_status`; die lesenden Tools `get_ticket` und `get_deployment_log` laufen ohne Bestätigung.

</details>

<details>
<summary>Wie wird ein kompromittierter Client erkannt?</summary>

Über das Protokoll aller Aufrufe, auch der abgelehnten, und Alarmregeln darauf: etwa mehrere `policy_denied` in kurzer Zeit oder Schreibaufrufe direkt nach dem Lesen eines Tickets. Die Umsetzung folgt in Lab 8.1.

</details>

- Der Server entscheidet über jeden Aufruf; Hinweise im Prompt oder Filter im Client sind nur zusätzliche Schichten.
- Eine Zugriffsrichtlinie (`policy.md`) legt fest, wer was darf. `auth.py` setzt sie im Server durch.

## Drei Fragen der Zugriffskontrolle

| Frage | Begriff | Im Vantra-Projekt |
| --- | --- | --- |
| Wer ruft auf? | Authentifizierung | Rolle des Server-Prozesses (`VANTRA_ROLE`), keine Client-Identität |
| Was darf die Rolle? | Autorisierung | Allow-List je Rolle in `auth.py` |
| Was kann der Prozess technisch? | Sandbox | Eingabevalidierung, Obergrenzen, Nicht-Root-Container |

Eine Richtlinie hat sechs Abschnitte (Vorlage: `shared/policy-template.md`): Geltungsbereich, Grundsätze, Rollen und Tools, Bestätigungspflicht, Erkennung und Reaktion, Offene Punkte.

## Least Privilege und deny by default

Jede Rolle bekommt nur die Tools, die ihre Aufgabe braucht. Alles, was nicht ausdrücklich erlaubt ist, wird abgelehnt.

| Tool | Art | viewer | operator | Bedingung |
| --- | --- | --- | --- | --- |
| `get_ticket` | lesen | erlaubt | erlaubt | `ticket_id` im Format `VAN-<Zahl>` |
| `get_deployment_log` | lesen | erlaubt | erlaubt | höchstens 100 Zeilen pro Aufruf |
| `update_ticket_status` | schreiben | verboten | erlaubt, nur mit Bestätigung | `expected_version` zwingend, Status aus fester Liste |

Standardrolle ohne Angabe: `viewer`. Unbekannte Rollen und unbekannte Tools werden abgelehnt.

## Durchsetzung im Server: `auth.py`

Die Rolle kommt aus der Umgebung des Server-Prozesses, nie aus Tool-Argumenten oder Modell-Ausgaben.

```python
ROLE_TOOLS = {
    "viewer": frozenset({"get_ticket", "get_deployment_log"}),
    "operator": frozenset({"get_ticket", "get_deployment_log", "update_ticket_status"}),
}
WRITE_TOOLS = frozenset({"update_ticket_status"})

def authorize(tool: str, confirmed: bool = False, role: str | None = None) -> str:
    role = role or current_role()                       # aus VANTRA_ROLE, Standard viewer
    if tool not in ROLE_TOOLS.get(role, frozenset()):   # unbekannte Rolle: leere Menge
        raise PolicyDenied("policy_denied", f"Rolle '{role}' darf das Tool '{tool}' nicht aufrufen.", role=role, tool=tool)
    if tool in WRITE_TOOLS and not confirmed:
        raise PolicyDenied("confirmation_required", f"Das Schreib-Tool '{tool}' braucht eine Bestätigung durch den Nutzer (confirmed=true).", role=role, tool=tool)
    return role
```

Jedes Tool ruft `authorize(...)` als Erstes auf und übersetzt `PolicyDenied` in einen strukturierten Tool-Fehler (`is_error=True`). Die vollständige Datei: `examples/m07-security-hardening/l01-access-control-sandboxing/auth.py`.

| Fehlercode | Bedeutung | Echte Antwort (Auszug) |
| --- | --- | --- |
| `policy_denied` | Rolle darf das Tool nicht aufrufen | `Rolle 'viewer' darf das Tool 'update_ticket_status' nicht aufrufen.` |
| `confirmation_required` | Schreib-Tool ohne Bestätigung | `Das Schreib-Tool 'update_ticket_status' braucht eine Bestätigung durch den Nutzer (confirmed=true).` |
| `version_conflict` | Ticket zwischenzeitlich geändert (Lab 3.3) | `Ticket VAN-102 wurde zwischenzeitlich geändert. …` |

## Bestätigung (Human-in-the-loop)

- Der Agent-Client zeigt vor jedem Schreibaufruf Tool, Ticket und neuen Status und fragt den Nutzer.
- Erst nach „ja“ setzt der Client `confirmed=true`. Das Argument wird dem Modell nicht angeboten.
- Grenze: Der Server prüft nur, ob `confirmed=true` ankommt, nicht wer es gesetzt hat. Ein Client, der das Argument selbst setzt, umgeht die Abfrage. Eine Bestätigung, die vom Server unabhängig vom Client erzwungen wird, ist im Projekt nicht umgesetzt (offener Punkt in `policy.md`).

## Sandbox-Prinzipien für Tool-Ausführung

Ein MCP-Server ist ein gewöhnlicher Prozess mit den Rechten seines Nutzers. Das Protokoll bietet keine Sandbox; sie entsteht durch den Betrieb (Quelle: MCP-Dokumentation „Local Server Security“, https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/local-server-security, abgerufen am 27.10.2026).

| Prinzip | Umsetzung im Projekt | Fundstelle |
| --- | --- | --- |
| Eingaben validieren | `ticket_id` muss `^VAN-\d{1,6}$` entsprechen, sonst Validierungsfehler | `server.py` (`TicketId`) |
| Ausgaben begrenzen | höchstens 100 Log-Zeilen je Aufruf | `server.py` (`MAX_LOG_LINES`) |
| Keine Root-Rechte | Nicht-Root-Nutzer `app` (uid 10001) im Container | `Dockerfile` |
| Wenig beschreibbarer Speicher | nur `/data` beschreibbar, `readOnlyRootFilesystem: true` | `Dockerfile`, `k8s.yaml` |
| Keine Secrets im Image | Konfiguration per Umgebung zur Laufzeit, Secret nur als Referenz | `Dockerfile`, `k8s.yaml` |
| Rolle nicht änderbar | `VANTRA_ROLE` nur beim Prozessstart, kein Tool kann sie setzen | `auth.py` |

Echte Antwort auf eine manipulierte ID (`../etc/passwd`): `String should match pattern '^VAN-\d{1,6}$'`, `is_error=True`.

## Authentifizierung in MCP (Stand: 27.10.2026)

Quelle: MCP-Spezifikation 2026-07-28, Abschnitt Authorization (https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization), abgerufen am 27.10.2026.

| Aussage der Spezifikation | Bedeutung |
| --- | --- |
| Autorisierung ist optional und gilt auf Transportebene | Ein Server kann ohne sie betrieben werden |
| HTTP-basierte Transporte sollen der Spezifikation folgen (SHOULD) | Grundlage ist OAuth 2.1; der MCP-Server ist Resource Server, der MCP-Client OAuth-Client |
| MCP-Server müssen OAuth 2.0 Protected Resource Metadata (RFC 9728) bereitstellen | So findet der Client den Authorization Server |
| stdio-Transport soll der Spezifikation nicht folgen (SHOULD NOT) | Zugangsdaten kommen aus der Umgebung |
| Server sollen benötigte Scopes im `WWW-Authenticate`-Header nennen | Least Privilege auch beim Token |

Im Projekt ist weder OAuth noch ein Token umgesetzt. Die Rolle gilt je Server-Prozess, bei HTTP für alle Verbindungen. Tool-Autorisierung (welche Rolle darf welches Tool) bleibt auch mit OAuth Aufgabe des Servers. Die Spezifikation warnt vor Token Passthrough: Ein Server darf keine Tokens akzeptieren, die nicht für ihn ausgestellt wurden.

> **Vor Kursbeginn prüfen:** Die Spezifikation ändert sich zwischen Revisionen. Seite „Authorization“ der aktuellen Revision öffnen und die Punkte der Tabelle gegen den Stand abgleichen.

## Typische Fehler

| Fehler | Folge |
| --- | --- |
| Prüfung nur im Systemprompt | Das Modell kann sie ignorieren; kein technischer Schutz |
| Rolle als Tool-Argument | Jeder Aufrufer wählt die Rolle selbst |
| Standard „erlaubt“ für Unbekanntes | Neue Tools sind sofort offen |
| Ein gemeinsamer Zugang für alle Clients | Aufrufe lassen sich keinem Client zuordnen |
| Schreib-Tool ohne Bestätigung | Eine einzige manipulierte Anweisung ändert Daten |

## Fazit

- Least Privilege, deny by default und Durchsetzung im Server sind die Kernregeln der Policy.
- Schreibende Tools laufen nur mit Rolle `operator` und Bestätigung.
- Sandbox heißt Begrenzung durch Betrieb: Validierung, Obergrenzen, Nicht-Root, Konfiguration zur Laufzeit.
- Authentifizierung nach OAuth ist in der Spezifikation für HTTP vorgesehen und im Projekt nicht umgesetzt.

Die Übung schreibt die Policy für die drei Vantra-Tools und setzt sie in `auth.py` im Server durch.
