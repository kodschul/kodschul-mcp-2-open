# Glossar

Alphabetisch. Modul/Lab nennt die Stelle, an der der Begriff eingeführt oder angewendet wird.

| Begriff | Bedeutung | Modul/Lab |
| --- | --- | --- |
| `_meta` | Feld in `params` und `result`; trägt Protokollversion, Fähigkeiten und `serverInfo` | 2.1 |
| Ablauf eines Tool-Aufrufs | Nummerierte Schrittfolge Entdeckung → Function Calling → Ausführung über MCP → Ergebnis zurück ans LLM | 1.1 |
| Agent | Anwendung, in der ein LLM in einer Schleife Tools vorschlägt und die Anwendung sie ausführt, bis eine Textantwort steht | 1.1, 4.1 |
| Agent-Client | Programm, das MCP-Tools entdeckt, in ein LLM-Gespräch einspeist und Tool-Wünsche des Modells ausführt (`shared/agent_client.py`) | 4.1 |
| Alarmregel | Status, Schwelle, Zeitfenster, Schwere | 8.1 |
| Allow-List | Server-seitige Liste erlaubter Tools je Rolle; alles Übrige wird abgelehnt | 7.1 |
| Annotation (`readOnlyHint`) | Zusatzhinweis eines Tools an Clients, z. B. „ändert nichts“ (`ToolAnnotations(read_only_hint=True)`) | 2.2 |
| Authentifizierung | Feststellen, wer aufruft (z. B. über ein Token) | 7.1 |
| Autorisierung | Entscheiden, was ein Aufrufer darf | 7.1 |
| Befund | Abweichung mit Fundstelle, Risiko, Schwere und Empfehlung | 7.3 |
| Bestätigungspflicht | Schreibende Tools laufen nur mit `confirmed=true`, sonst `confirmation_required` (Human-in-the-loop) | 7.1 |
| Build-Kontext | Ordner, den `docker build` übergibt; `COPY` liest nur daraus | 5.2 |
| Capabilities (Fähigkeiten) | Liste, welche Bereiche eine Seite unterstützt, z. B. `tools`, `resources`, `prompts`; Teil von `server/discover` und `_meta` | 1.2, 2.1 |
| Checkpoint (Projekt) | Wiederaufsetzpunkt in `project/checkpoints/` (`ende-tag1-prototyp` zum Wiedereinstieg in Tag 2, `ende-m07-abgesichert` als Basis für Lab 8.1 und 8.2) | 4.1, 7.1, 8.1, 8.2 |
| Client | Verbindung des Hosts zu genau einem Server; im Code `mcp.Client` aus dem SDK | 1.1 |
| ConfigMap | Kubernetes-Ressource für unkritische Konfiguration; Secrets gehören nicht hinein | 6.2 |
| Confused Deputy | Dienst mit vielen Rechten handelt im Auftrag eines Aufrufers, der das selbst nicht dürfte | 8.3 |
| Container-Healthcheck | Docker-`HEALTHCHECK` auf `/health`; markiert den Container als `unhealthy`, startet ihn aber nicht neu | 5.2, 6.1 |
| Decorator (Dekorator) | Python-Funktion, die eine andere umhüllt oder anmeldet (`@name`), z. B. `@mcp.tool()` | 2.2, 8.1 |
| deny by default | Alles, was die Policy nicht ausdrücklich erlaubt, wird abgelehnt (unbekannte Rolle oder Tool: `policy_denied`) | 7.1 |
| Deployment (Kubernetes) | Ressource für Replikas, Rollout und Rollback | 6.2 |
| DNS-Rebinding | Fremde Webseite spricht über einen DNS-Trick einen lokalen Dienst an | 8.2 |
| Docstring / Typhinweis | Text unter `def` (wird Tool-Beschreibung) bzw. Typangabe wie `ticket_id: str` (wird Eingabeschema) | 2.2 |
| Edge | Platzierungsmuster: Server oder Gateway am Rand, für externe Clients, Streamable HTTP mit TLS | 5.1 |
| Erweiterung | Optionaler Teil einer Übung; nie Voraussetzung für spätere Labs | alle Projekt-Labs |
| `expected_version` | Argument des Schreib-Tools: die zuvor gelesene Version des Tickets; Grundlage der Versionsprüfung | 3.3 |
| Extension | Optionale Erweiterung außerhalb des Protokollkerns | 8.3 |
| Function Calling | Fähigkeit eines LLM, statt Text einen Funktionsaufruf als JSON (Name plus Argumente) auszugeben; das Format legt der Modellanbieter fest, MCP standardisiert die Anbindung dahinter | 1.1 |
| Gateway | Vorgeschalteter Dienst, der Anfragen von außen annimmt, prüft (Anmeldung, TLS, Rate-Limit) und weiterreicht | 5.1 |
| Handshake (`initialize`) | Begrüßungsnachricht älterer MCP-Revisionen vor dem ersten Aufruf; seit Spezifikation 2026-07-28 entfallen | 1.2, 2.1 |
| Health-Pfad `/health` | HTTP-Pfad neben `/mcp`, ohne Authentifizierung und ohne Daten; liefert `{"status":"ok"}` | 5.2 |
| Heuristik | Faustregel, die bekannte Muster erkennt, ohne Garantie | 7.2 |
| `HIDDEN_ARGS` | Argumente, die der Host vor dem Modell verbirgt (`confirmed`) | 7.1 |
| Host | Anwendung, die die Verbindungen zu den Servern hält und entscheidet, welcher Aufruf passiert (im Agenten schlägt das LLM vor, im Inspector oder Skript-Client entscheidet die Person) | 1.1 |
| Hülle (Envelope) | `params._meta` jedes Requests mit Protokollversion, Client-Fähigkeiten und `clientInfo`; fehlt sie: Fehler `-32602` | 2.1 |
| Idempotent | Wiederholung ändert nichts mehr | 3.3 |
| `inputSchema` (Eingabeschema) | Beschreibung der Tool-Parameter im Format JSON Schema (Namen, Typen, Pflichtfelder); das SDK prüft Argumente automatisch dagegen | 2.2 |
| Inspector (MCP Inspector) | Standard-Testclient: listet Tools, ruft sie auf, zeigt JSON-RPC-Nachrichten (`npx @modelcontextprotocol/inspector`) | 1.2 |
| JSON-RPC 2.0 | Nachrichtenformat von MCP: Request, Response, Notification | 2.1 |
| JSONL | Eine JSON-Zeile je Eintrag; Format des Tool-Call-Protokolls (`logs/tool_calls.jsonl`) | 8.1 |
| Kindprozess | Programm, das ein anderes Programm startet und dessen stdin/stdout steuert; bei stdio startet der Client den Server so | 1.1, 1.2 |
| Kontextfenster | Nachrichtenliste eines Modellaufrufs; wird bei jedem Aufruf aus dem Verlauf neu gefüllt und ist begrenzt | 3.1 |
| Kontextschema | Tabelle der Felder des Session-State mit Quelle, Lebensdauer und Sichtbarkeit (`SESSION_SCHEMA`); „sichtbar“ heißt: die Resource `context://session` zeigt den Wert, nicht automatisch das LLM | 3.2 |
| kubeconform | Prüft ein Manifest ohne Cluster gegen Schemas | 6.2 |
| Label/Selector | Etikett an Pods und die Regel, die sie auswählt | 6.2 |
| Layer-Cache | Docker überspringt unveränderte Dockerfile-Schritte | 5.2 |
| Least Privilege | Jede Rolle erhält nur die Rechte, die der Auftrag braucht | 7.1 |
| Liveness-/Readiness-/Startup-Probe | Kubernetes-Prüfungen auf `/health`: Neustart bei Hänger, Verkehr nur an bereite Pods, Zeit zum Starten | 5.2, 6.2 |
| LLM | Großes Sprachmodell (z. B. `qwen3:8b`), das aus Text Text erzeugt; führt selbst nichts aus | 1.1 |
| Lost Update | Änderung geht verloren, weil ein zweiter Schreiber auf veraltetem Stand speichert | 3.3 |
| Manifest | YAML-Datei mit Kubernetes-Ressourcen | 6.2 |
| MCP (Model Context Protocol) | Offener Standard, über den Anwendungen Tools und Daten aus separaten Server-Programmen nutzen | 1.1 |
| Memory (persistent) | Speicher über Sessions hinweg; im Kursprojekt nicht umgesetzt | 3.1 |
| Mock-API | Gemockte Ticket-/Deployment-API des Projekts (Port 8001, `shared/mock_api/`) | 3.3 |
| Multi Round-Trip Request | Revision 2026-07-28: Rückfragen laufen über Folge-Requests statt über server-initiierte Anfragen | 8.3 |
| Nachrichtenrolle | `system`, `user`, `assistant` oder `tool` im Verlauf | 4.1 |
| Notification | JSON-RPC-Nachricht ohne `id`; erhält keine Antwort | 2.1 |
| OAuth | Standard, mit dem ein Client bei einer Anmeldestelle ein Token holt; in MCP für HTTP vorgesehen | 7.1 |
| Ollama | Lokaler HTTP-Dienst für Sprachmodelle (Port 11434) | 4.1 |
| OpenAI-kompatible API | Verbreitetes Chat-Format mit `messages` und `tools` | 4.1 |
| Operator / Viewer | Rollen des Projekts: `viewer` nur lesen (Standard), `operator` schreiben mit Bestätigung (`VANTRA_ROLE`) | 7.1 |
| Orchestrator | Plattform, die Container startet, überwacht und neu startet (Compose, Kubernetes) | 5.2 |
| Pod | Kleinste Kubernetes-Einheit: ein oder mehrere Container mit gemeinsamer Adresse; ein Deployment hält mehrere Replikas davon | 6.2 |
| Policy-Dokument | Zugriffsrichtlinie: Geltungsbereich, Grundsätze, Rollen und Tools, Bestätigungspflicht, Erkennung | 7.1 |
| Primitives | Grundbausteine eines Servers: Tools (vom Modell gewählt), Resources (von der Anwendung geladen), Prompts (von Nutzer:innen gewählt) | 1.1, 2.2 |
| Prompt Injection | Anweisung im Tool-Ergebnis, die das Modell als Auftrag liest | 7.2 |
| Protokollfehler | JSON-RPC-`error` mit Code, z. B. `-32602`, `-32601`; unterscheidet sich vom Tool-Fehler | 2.3 |
| Rechteausweitung | Versuch, mehr Rechte zu erhalten als vorgesehen | 7.2 |
| Registry | Ablage für Images (z. B. ghcr.io) | 6.2 |
| Replay-LLM | Ersatz für das Modell: spielt feste Tool-Calls ab (`--replay`); der Lauf heißt Skript-Agent | 4.1 |
| Request / Response | JSON-RPC-Anfrage mit `id` und `method` bzw. Antwort mit derselben `id` und `result` oder `error` | 2.1 |
| Resource | Lesbare Daten per URI, z. B. `tickets://{ticket_id}` | 2.2 |
| Resource Server | Rolle eines MCP-Servers in der Autorisierung; stellt Protected Resource Metadata (RFC 9728) bereit | 7.1 |
| Rollout/Rollback | Neue Version ausrollen / zur vorigen zurückkehren | 6.2 |
| Sandbox | Begrenzung der Ausführung: Eingabe prüfen, Ausgabe begrenzen, Nicht-Root, nur `/data` beschreibbar | 7.1 |
| Schweregrad | Review-Einstufung: blockierend, wichtig, nice to have | 7.3 |
| Scope Minimization | Token enthält nur die nötigen Rechte | 8.3 |
| SDK | Software Development Kit; im Kurs das Python-Paket `mcp` (2.3.0) mit `MCPServer` und `Client` | 1.1, 1.2 |
| Secret | Geheimer Wert (Token, Schlüssel); nie im Image, im Repo oder im Prompt, sondern zur Laufzeit übergeben | 5.2, 6.2 |
| Server (MCP) | Eigenständiges Programm, das Tools, Resources und Prompts anbietet und ausführt (`MCPServer`) | 1.1 |
| `server/discover` | Optionale Methode: Fähigkeiten, `supportedVersions`, `instructions` | 1.2 |
| Service Discovery | Finden eines Dienstes über seinen Namen statt über eine feste IP: `localhost`, Compose-Dienstname oder Kubernetes-Service | 5.1 |
| Session | Verbindung Client–Server; bei stdio genau ein Serverprozess | 3.1 |
| Session-State | Zustand je Serverprozess (`SessionContext` in `context.py`); beim Neustart verloren | 3.1 |
| Showcase A | Live-Trace der JSON-RPC-Nachrichten über den Logging-Proxy (`shared/trace_proxy.py`) | 2.1 |
| Showcase C | Prompt-Injection-Duell per Replay: ohne Policy gelingt der Aufruf, mit Policy blockt der Server | 7.2 |
| Showcase D | Mini-Dashboard der Tool-Calls (Port 8080) | 8.1 |
| Sidecar | Platzierungsmuster: Server neben dem Agenten, stdio oder localhost | 5.1 |
| Simulierter Agent | `second_client.py`: liest, wartet und schreibt ohne LLM | 3.3 |
| Skript-Agent | Agent-Lauf mit Replay-LLM; wählt selbst keine Tools und wird in Testprotokollen so gekennzeichnet | 4.2 |
| Skript-Client | `shared/script_client.py`: Host und Client ohne LLM; listet Tools, ruft per `--call` eins auf | 1.2 |
| stdio | Transport: Client startet den Server als Kindprozess, eine JSON-Nachricht je Zeile; stdout gehört dem Protokoll | 1.1, 1.2 |
| Streamable HTTP | Transport für entfernte Server, Endpunkt `/mcp`; ersetzt HTTP+SSE | 1.2, 6.1 |
| Strukturierter Fehler (`error_result`) | `isError`-Ergebnis mit JSON-Feldern statt nur Text | 3.3 |
| Strukturiertes Log | Log-Zeile als JSON-Objekt mit festen Feldern | 8.1 |
| System-Prompt | Feste Anweisung am Anfang jedes Verlaufs | 3.1, 4.1 |
| Token (Modell) | Wortstück, in dem ein Modell Text misst; begrenzt die Größe des Kontextfensters | 3.1 |
| Token (Zugang) | Zeichenkette, mit der sich ein Client ausweist | 7.1 |
| Token Passthrough | Anti-Pattern: Tokens weiterreichen, die nicht für den Server ausgestellt sind | 7.1 |
| Tool | Aktion, vom Modell gewählt; Schema aus Typhinweisen, Beschreibung aus dem Docstring | 2.2 |
| Tool Poisoning / Tool-Spoofing | Manipulierte Tool-Definition eines fremden Servers, die das Modell mit versteckten Anweisungen steuert: Namenskollision, Anweisungen in der Beschreibung, zusätzlicher Parameter | 7.2 |
| Tool-Call-Protokoll | JSONL-Datei mit `ts`, `tool`, `role`, `status`, `error_code`, `duration_ms`, `args` | 8.1 |
| Tool-Fehler | Ergebnis mit `isError: true`; die Meldung erreicht das Modell | 2.3 |
| Tool-Schleife (`MAX_STEPS`) | Modell fragen → Tool ausführen → Ergebnis zurück, höchstens 6 Schritte | 4.1 |
| `ToolError` | SDK-Ausnahme für erwartete Fehler; Meldung erreicht das Modell als Tool-Fehler | 2.2, 2.3 |
| Transport | Leitung zwischen Client und Server: stdio oder Streamable HTTP | 1.1 |
| Vektorspeicher | Datenbank, die Texte nach Ähnlichkeit findet; im Kurs nicht genutzt | 3.1 |
| `version_conflict` | Fehlerergebnis mit `expected_version` und `current_version`; Behebung: neu lesen und wiederholen | 3.3 |
| Versionsprüfung | Schreiben nur mit aktueller Version; sonst `version_conflict` | 3.3 |
| Verteidigungslinie | Eine von vier Schutzebenen: Modell/Prompt, Client, Server, Policy/Betrieb | 7.2 |
| Vertrauensgrenze (Trust Boundary) | Stelle, an der Daten zwischen Bereichen wechseln und geprüft werden müssen, z. B. zwischen Client und Server | 1.3, 5.1 |
| Vieraugenprinzip | Eine zweite Person prüft vor der Freigabe | 7.3 |
| Volume | Docker-Speicher, der Container-Neustarts überdauert; im Projekt nach `/data` | 6.1, 8.2 |
| Workflow/Job/Step/Runner/Action | Bausteine einer Pipeline: Ablauf, Arbeitspaket, Einzelschritt, ausführende Maschine, wiederverwendbarer Baustein | 6.2 |
| YAML-Anker/Alias (`&`/`*`) | Block einmal benennen, mehrfach einsetzen | 6.1 |
| Zeitfenster | Rückwärts vom aktuellen Zeitpunkt gezählter Zeitraum einer Alarmregel | 8.1 |
| Zustandsloses Modell | Das LLM merkt sich zwischen Aufrufen nichts; der Client schickt den Verlauf jedes Mal mit | 3.1 |
