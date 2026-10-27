# FAQ

Antworten stützen sich auf die Handouts und das Projekt. Setup-Details: [`../00-setup-and-installation.md`](../00-setup-and-installation.md).

## Umgebung

**Ist ein LLM-API-Key nötig?**
Nein. Der Agent-Client spricht jedes OpenAI-kompatible Backend; Standard ist Ollama lokal (`LLM_BASE_URL=http://localhost:11434/v1`, `LLM_API_KEY=ollama`). Ollama ersetzt nur den Cloud-Zugang und ist kein Kursthema.

**Ollama antwortet zu langsam oder das Modell fehlt. Was dann?**
Den Agent mit Replay-LLM starten: `python shared/agent_client.py --server playground/server.py --replay`. Der Lauf ist ein Skript-Agent: Er spielt feste Tool-Calls ab und wählt selbst keine Tools. Testprotokolle kennzeichnen das (Lab 4.2). Alternativ in `.env` `LLM_MODEL=qwen3:4b` setzen (ca. 2,5 GB, Tool-Auswahl weniger zuverlässig).

**Docker läuft auf dem Schulungs-PC nicht. Bleibt Modul 6 aus?**
Nein. Modul 6 läuft dann als Demo statt Hands-on (kein eigenes Bauen und Starten). Die Module 1 bis 4 brauchen weder Docker noch Ollama.

**Es gibt keinen Kubernetes-Cluster.**
Das Manifest wird nur validiert, nicht angewendet: `kubeconform -strict -summary playground/k8s.yaml` (Lab 6.2). Ein Cluster ist optional.

**`npx` oder der MCP Inspector funktioniert nicht.**
`python shared/script_client.py --server playground/server.py` ruft dieselben Tools auf, ohne Weboberfläche.

**Pakete lassen sich nicht installieren (Rechte, Proxy).**
Eine vorbereitete venv mit allen Paketen verwenden und aktivieren. Pakete werden nur im Projekt (venv) installiert, Administratorrechte sind dafür nicht nötig.

## MCP-Grundlagen

**Wann stdio, wann Streamable HTTP?**

| Transport | Einsatz im Kurs | Merkmal |
| --- | --- | --- |
| stdio | Module 1–4 und lokale Tests | Client startet den Server als Kindprozess; kein Port, kein Netzwerk |
| Streamable HTTP | Container in Modul 6, entfernte Server | Server lauscht, Endpunkt `/mcp`; `MCP_TRANSPORT=streamable-http` |

**Der Server „hängt“ nach dem Start.**
Normales Verhalten: Ein stdio-Server wartet auf einen Client an stdin. Mit `Ctrl+C` beenden und Skript-Client oder Inspector verwenden.

**Warum scheitern Tutorials aus dem Netz (`FastMCP`, `initialize`, HTTP+SSE)?**
Der Kurs nutzt SDK 2.x (`mcp==2.3.0`) und die Spezifikation 2026-07-28 (Stand: 27.10.2026). Dort gibt es `from mcp.server import MCPServer` statt `FastMCP`, keinen `initialize`-Handshake (Version und Fähigkeiten stehen in `params._meta` jedes Requests) und Streamable HTTP statt HTTP+SSE. Als Vorlage dienen die Beispiele in `project/examples/`.

**Wie erfährt der Client, welche Tools es gibt?**
Über `tools/list` (Namen, Beschreibung, Eingabeschema); `server/discover` liefert zusätzlich Fähigkeiten, `supportedVersions` und `instructions`.

**Warum zeigt ein Tool-Fehler nur „Error executing tool …“?**
Eine normale Exception zeigt dem Modell nur diese Meldung. `raise ToolError("…")` bringt eine eigene Meldung zum Modell (Lab 2.3).

## Kontext und Agent

**Warum meldet das Deployment-Log „Keine ticket_id angegeben und kein Ticket im Kontext“?**
Jeder Aufruf des Skript-Clients startet einen neuen Serverprozess mit leerem State. Ticket und Log in einer Sitzung abfragen, z. B. mit `agent_client.py --replay` (Lab 3.2).

**Zwei Clients melden beide `ok`, einen Konflikt gibt es nicht.**
Entweder fehlt `MOCK_API_URL` (zwei Prozesse mit getrennten Daten) oder der Server prüft `expected_version` noch nicht (Starter-Stand). Zurücksetzen: `curl -X POST localhost:8001/reset` (Lab 3.3).

**Das Modell ruft kein oder das falsche Tool auf.**
Beschreibungen sind unklar oder überlappen, oder das Modell ist zu klein. Docstring abgrenzend formulieren; zum Gegenprüfen `--replay` nutzen (Lab 4.1).

## Container und Security

**Der Container läuft, aber `Connection refused`.**
`ports` fehlt oder `MCP_HOST` steht auf `127.0.0.1`. Im Container `MCP_HOST=0.0.0.0` setzen und `-p 8000:8000` bzw. `ports: "8000:8000"` angeben (Lab 5.2, 6.1).

**Wohin gehören Secrets?**
Zur Laufzeit übergeben (`docker run -e`, Compose-Secret, Kubernetes `secretKeyRef`), nie per `ENV` im Image oder im Repo. `docker inspect` und `docker history` zeigen `ENV`-Werte (Lab 5.2).

**`update_ticket_status` liefert `policy_denied`.**
Die Standardrolle ist `viewer` und darf nur lesen. Mit `VANTRA_ROLE=operator` starten (oder `--role operator` beim Skript- und Agent-Client). Ohne `confirmed=true` folgt danach `confirmation_required` (Lab 7.1).

**Was fehlt bis zum Produktivbetrieb?**
Authentifizierung je Client, Bestätigung unabhängig vom Client, Ratenbegrenzung, DNS-Rebinding-Schutz bei Host `0.0.0.0`, Log-Aufbewahrung und -Zugriff, Kontext je Client, ein ausgeführter Infrastrukturtest und ein Test mit echtem Modell (Lab 8.2).

**Wo ist das persistente Memory?**
Im Kursprojekt nicht umgesetzt. Umgesetzt sind Kontextfenster und Session-State je Serverprozess (Lab 3.1).
