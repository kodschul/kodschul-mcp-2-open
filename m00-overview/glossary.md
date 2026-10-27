# Glossar

Alphabetisch. Modul/Lab nennt die Stelle, an der der Begriff eingeführt oder angewendet wird.

| Begriff | Bedeutung | Modul/Lab |
| --- | --- | --- |
| Agent-Client | Programm, das MCP-Tools entdeckt, in ein LLM-Gespräch einspeist und Tool-Wünsche des Modells ausführt (`shared/agent_client.py`) | 4.1 |
| Allow-List | Server-seitige Liste erlaubter Tools je Rolle; alles Übrige wird abgelehnt | 7.1 |
| Bestätigungspflicht | Schreibende Tools laufen nur mit `confirmed=true`, sonst `confirmation_required` (Human-in-the-loop) | 7.1 |
| Checkpoint (Projekt) | Wiederaufsetzpunkt in `project/checkpoints/` (`ende-tag1-prototyp` zum Wiedereinstieg in Tag 2, `ende-m07-abgesichert` als Basis für Lab 8.1 und 8.2) | 4.1, 7.1, 8.1, 8.2 |
| ConfigMap | Kubernetes-Ressource für unkritische Konfiguration; Secrets gehören nicht hinein | 6.2 |
| Container-Healthcheck | Docker-`HEALTHCHECK` auf `/health`; markiert den Container als `unhealthy`, startet ihn aber nicht neu | 5.2, 6.1 |
| deny by default | Alles, was die Policy nicht ausdrücklich erlaubt, wird abgelehnt (unbekannte Rolle oder Tool: `policy_denied`) | 7.1 |
| Deployment (Kubernetes) | Ressource für Replikas, Rollout und Rollback | 6.2 |
| Edge | Platzierungsmuster: Server oder Gateway am Rand, für externe Clients, Streamable HTTP mit TLS | 5.1 |
| Erweiterung | Optionaler Teil einer Übung; nie Voraussetzung für spätere Labs | alle Projekt-Labs |
| `expected_version` | Argument des Schreib-Tools: die zuvor gelesene Version des Tickets; Grundlage der Versionsprüfung | 3.3 |
| Function Calling | Tool-Aufruf-Fähigkeit eines Modells mit herstellerspezifischem Format; MCP standardisiert die Anbindung dahinter | 1.1 |
| Health-Pfad `/health` | HTTP-Pfad neben `/mcp`, ohne Authentifizierung und ohne Daten; liefert `{"status":"ok"}` | 5.2 |
| Host | Anwendung mit LLM, die einen oder mehrere MCP-Clients hält | 1.1 |
| Inspector (MCP Inspector) | Standard-Testclient: listet Tools, ruft sie auf, zeigt JSON-RPC-Nachrichten (`npx @modelcontextprotocol/inspector`) | 1.2 |
| JSON-RPC 2.0 | Nachrichtenformat von MCP: Request, Response, Notification | 2.1 |
| JSONL | Eine JSON-Zeile je Eintrag; Format des Tool-Call-Protokolls (`logs/tool_calls.jsonl`) | 8.1 |
| Kontextfenster | Nachrichtenliste eines Modellaufrufs; begrenzt und nach dem Aufruf verloren | 3.1 |
| Kontextschema | Tabelle der Kontextfelder mit Quelle, Lebensdauer und Sichtbarkeit für das LLM (`SESSION_SCHEMA`) | 3.2 |
| Least Privilege | Jede Rolle erhält nur die Rechte, die der Auftrag braucht | 7.1 |
| Liveness-/Readiness-/Startup-Probe | Kubernetes-Prüfungen auf `/health`: Neustart bei Hänger, Verkehr nur an bereite Pods, Zeit zum Starten | 5.2, 6.2 |
| Memory (persistent) | Speicher über Sessions hinweg; im Kursprojekt nicht umgesetzt | 3.1 |
| `_meta` | Feld in `params` und `result`; trägt Protokollversion, Fähigkeiten und `serverInfo` | 2.1 |
| Mock-API | Gemockte Ticket-/Deployment-API des Projekts (Port 8001, `shared/mock_api/`) | 3.3 |
| Multi Round-Trip Request | Revision 2026-07-28: Rückfragen laufen über Folge-Requests statt über server-initiierte Anfragen | 8.3 |
| Notification | JSON-RPC-Nachricht ohne `id`; erhält keine Antwort | 2.1 |
| Operator / Viewer | Rollen des Projekts: `viewer` nur lesen (Standard), `operator` schreiben mit Bestätigung (`VANTRA_ROLE`) | 7.1 |
| Policy-Dokument | Zugriffsrichtlinie: Geltungsbereich, Grundsätze, Rollen und Tools, Bestätigungspflicht, Erkennung | 7.1 |
| Primitives | Tools (vom Modell gewählt), Resources (von der Anwendung gewählt), Prompts (von Nutzer:innen gewählt) | 1.1, 2.2 |
| Prompt Injection | Anweisung im Tool-Ergebnis, die das Modell als Auftrag liest | 7.2 |
| Protokollfehler | JSON-RPC-`error` mit Code, z. B. `-32602`, `-32601`; unterscheidet sich vom Tool-Fehler | 2.3 |
| Replay-LLM | Ersatz für das Modell: spielt feste Tool-Calls ab (`--replay`); der Lauf heißt Skript-Agent | 4.1 |
| Resource | Lesbare Daten per URI, z. B. `tickets://{ticket_id}` | 2.2 |
| Resource Server | Rolle eines MCP-Servers in der Autorisierung; stellt Protected Resource Metadata (RFC 9728) bereit | 7.1 |
| Sandbox | Begrenzung der Ausführung: Eingabe prüfen, Ausgabe begrenzen, Nicht-Root, nur `/data` beschreibbar | 7.1 |
| Schweregrad | Review-Einstufung: blockierend, wichtig, nice to have | 7.3 |
| Secret | Geheimer Wert (Token, Schlüssel); nie im Image, im Repo oder im Prompt, sondern zur Laufzeit übergeben | 5.2, 6.2 |
| `server/discover` | Optionale Methode: Fähigkeiten, `supportedVersions`, `instructions` | 1.2 |
| Service Discovery | Auffinden des Servers per Adresse: `localhost`, Compose-Dienstname oder Kubernetes-Service | 5.1 |
| Session-State | Zustand je Serverprozess (`SessionContext` in `context.py`); beim Neustart verloren | 3.1 |
| Showcase A | Live-Trace der JSON-RPC-Nachrichten über den Logging-Proxy (`shared/trace_proxy.py`) | 2.1 |
| Showcase C | Prompt-Injection-Duell per Replay: ohne Policy gelingt der Aufruf, mit Policy blockt der Server | 7.2 |
| Showcase D | Mini-Dashboard der Tool-Calls (Port 8080) | 8.1 |
| Sidecar | Platzierungsmuster: Server neben dem Agenten, stdio oder localhost | 5.1 |
| Skript-Agent | Agent-Lauf mit Replay-LLM; wählt selbst keine Tools und wird in Testprotokollen so gekennzeichnet | 4.2 |
| stdio | Transport: Client startet den Server als Kindprozess, eine JSON-Nachricht je Zeile; stdout gehört dem Protokoll | 1.1, 1.2 |
| Streamable HTTP | Transport für entfernte Server, Endpunkt `/mcp`; ersetzt HTTP+SSE | 1.2, 6.1 |
| Token Passthrough | Anti-Pattern: Tokens weiterreichen, die nicht für den Server ausgestellt sind | 7.1 |
| Tool | Aktion, vom Modell gewählt; Schema aus Typhinweisen, Beschreibung aus dem Docstring | 2.2 |
| Tool-Call-Protokoll | JSONL-Datei mit `ts`, `tool`, `role`, `status`, `error_code`, `duration_ms`, `args` | 8.1 |
| Tool-Fehler | Ergebnis mit `isError: true`; die Meldung erreicht das Modell | 2.3 |
| Tool-Spoofing | Manipulierte Tool-Definition: Namenskollision, Anweisungen in der Beschreibung, zusätzlicher Parameter | 7.2 |
| Trust Boundary (Vertrauensgrenze) | Stelle, an der Eingaben nicht mehr als vertrauenswürdig gelten, z. B. zwischen Client und Server | 1.3, 5.1 |
| Versionsprüfung | Schreiben nur mit aktueller Version; sonst `version_conflict` | 3.3 |
| `version_conflict` | Fehlerergebnis mit `expected_version` und `current_version`; Behebung: neu lesen und wiederholen | 3.3 |
| Verteidigungslinie | Eine von vier Schutzebenen: Modell/Prompt, Client, Server, Policy/Betrieb | 7.2 |
| Volume | Persistenter Speicher des Containers, im Projekt nach `/data` | 6.1 |
