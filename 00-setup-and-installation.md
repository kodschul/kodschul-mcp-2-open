# Setup und Installation: Schulungs-PC prüfen

Der Kurs läuft auf dem bereitgestellten Schulungs-PC. Schritt 0 bis 4 sind vor Kursbeginn erledigt (Vorbereitung durch die IT des Schulungsorts); am ersten Morgen wird nur die Checkliste am Ende abgearbeitet (ca. 5 Minuten). Ohne Vorbereitung dauern alle Schritte etwa 15 bis 20 Minuten.

- **Terminal:** Alle Befehle sind Bash-Befehle. Unter Windows läuft Bash als **Git Bash** (Teil von Git for Windows, Startmenü „Git Bash“); PowerShell und `cmd` werden im Kurs nicht verwendet.
- **Ordner:** Ab Schritt 2 laufen alle Befehle im Projektordner `output/project/`.

## Voraussetzungen im Überblick

| Baustein | Soll | Prüfbefehl | Gebraucht ab |
| --- | --- | --- | --- |
| Python | ≥ 3.11 (verifiziert mit 3.13) | `python --version` | Lab 1.2 |
| Node.js mit `npx` | aktuelle LTS-Version | `node --version` und `npx --version` | Lab 1.2 (MCP Inspector) |
| Ollama mit Modell `qwen3:8b` | Modell lokal vorhanden | `ollama list` | Modul 4 |
| Docker Desktop | Daemon läuft | `docker version` | Modul 6 |
| `kubeconform` | Binary im `PATH` | `kubeconform -v` | Lab 6.2 (Manifest validieren) |
| Git Bash (nur Windows) | Teil von Git for Windows | `bash --version` in Git Bash | alle Labs |
| Code-Editor | VS Code empfohlen | – | alle Labs |
| Internet | `pip`, `npx`, `docker pull` erreichbar | siehe Abschnitt „Netzwerk“ | Installation |

Ein LLM-API-Key ist nicht nötig. Ollama ersetzt nur den Cloud-Zugang und ist selbst kein Kursthema. Ein Kubernetes-Cluster ist optional (Modul 6).

## Schritt 0: Projekt holen

Die Kursunterlagen bestehen aus dem Ordner `output/` mit den Handouts und dem Projekt `output/project/`. Er liegt auf dem Schulungs-PC bereit (z. B. im Benutzerordner) oder wird als ZIP-Archiv verteilt und dort entpackt.

```bash
cd <Pfad zum Ordner output>           # z. B. cd ~/mcp-kurs/output
ls project                            # zeigt u. a. examples  playground  requirements.txt  shared  starters
```

Pfade mit Leerzeichen in Anführungszeichen setzen (`cd ~/"Meine Kurse/output"`). In Git Bash heißt `C:\Users\name` `/c/Users/name`.

## Schritt 1: Versionen prüfen

```bash
python --version        # Python 3.11 oder höher
node --version
npx --version
docker version          # Client und Server müssen antworten
ollama list             # qwen3:8b steht in der Liste
```

Unter Windows heißt der Python-Befehl in Git Bash je nach Installation `py` oder `python`. Die Beispiele verwenden `python`; nach Aktivieren der venv (Schritt 2) gilt immer `python`.

## Schritt 2: Projekt-Umgebung anlegen

```bash
cd project                           # aus dem Ordner output/ heraus
python -m venv .venv
source .venv/bin/activate            # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

| Befehl | Wirkung |
| --- | --- |
| `python -m venv .venv` | isolierte Python-Umgebung im Projektordner |
| `source .venv/bin/activate` | Umgebung aktivieren (gilt nur für das aktuelle Terminal; Git Bash: `source .venv/Scripts/activate`) |
| `pip install -r requirements.txt` | installiert `mcp==2.3.0`, `openai==3.40.0`, `pytest`, `pytest-asyncio`, `PyYAML` in festen Versionen |
| `cp .env.example .env` | Konfiguration des LLM-Backends (Standard: Ollama, `qwen3:8b`) |

Die Umgebung muss in jedem neuen Terminal erneut aktiviert werden. Das Terminal-Präfix `(.venv)` zeigt den aktiven Zustand.

## Schritt 3: Installation testen

```bash
python -c "import mcp; from mcp.server import MCPServer; from mcp import Client; print('mcp ok')"
pytest -q
```

`pytest -q` startet 90 Tests ohne LLM und endet mit `90 passed`. Der Lauf dauert je nach Rechner ein bis drei Minuten. Für einen schnellen Funktionstest genügt:

```bash
python shared/script_client.py --server examples/m01-mcp-foundations-and-setup/l02-dev-setup/server.py
```

Erwartete Ausgabe:

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: (keine)
```

## Schritt 4: MCP Inspector prüfen

```bash
npx @modelcontextprotocol/inspector --cli python examples/m01-mcp-foundations-and-setup/l02-dev-setup/server.py --method tools/list
```

Erwartete Ausgabe bei einem Server ohne Tools:

```json
{
  "tools": []
}
```

Die Weboberfläche startet ohne `--cli` (`npx @modelcontextprotocol/inspector python playground/server.py`) und öffnet den Browser. Beim ersten Aufruf lädt `npx` das Paket nach; dafür muss das Netzwerk `npx` erlauben.

## Schritt 5: Modell prüfen (ab Modul 4)

```bash
ollama list                                  # qwen3:8b vorhanden (ca. 5,2 GB)
ollama run qwen3:8b "Antworte mit einem Wort: Hallo"
```

Antwortet das Modell, ist das LLM-Backend einsatzbereit. Die Standardwerte stehen in `.env`:

| Variable | Standardwert |
| --- | --- |
| `LLM_BASE_URL` | `http://localhost:11434/v1` |
| `LLM_MODEL` | `qwen3:8b` |
| `LLM_API_KEY` | `ollama` |

## Netzwerk und Rechte

| Dienst | Gebraucht für | Prüfung |
| --- | --- | --- |
| PyPI | `pip install -r requirements.txt` | Installation läuft ohne Zeitüberschreitung |
| npm-Registry | `npx @modelcontextprotocol/inspector` | Inspector startet |
| Docker-Registry | `docker pull` in Modul 6 | `docker pull python:3.13-slim` |
| GitHub (raw.githubusercontent.com) | Kubernetes-Schemas für `kubeconform` in Lab 6.2 | `kubeconform -summary examples/m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml` meldet `Valid` |

Hinter einem Proxy setzt die Kunden-IT die Proxy-Variablen für `pip`, `npm` und Docker. Pakete werden nur im Projekt installiert (venv), Administratorrechte sind dafür nicht nötig.

## Fallbacks

| Problem | Fallback | Einschränkung |
| --- | --- | --- |
| Keine Installationsrechte oder `pip` blockiert | vorbereitete venv mit allen Paketen verwenden und aktivieren | keine Live-Installation, Paketstand ist fest |
| Node/`npx` fehlt oder `npx` blockiert | `python shared/script_client.py` statt MCP Inspector | keine Weboberfläche, gleiche Tool-Aufrufe |
| Ollama fehlt, Modell zu langsam oder nicht geladen | Replay-LLM: `--replay` am Agent-Client | Skript-Agent: spielt feste Tool-Calls ab, wählt selbst keine Tools |
| Modell `qwen3:8b` zu groß | `LLM_MODEL=qwen3:4b` in `.env` (ca. 2,5 GB) | Tool-Auswahl weniger zuverlässig |
| Docker läuft nicht | Modul 6 als Demo statt Hands-on | kein eigenes Bauen und Starten |
| Kein Kubernetes-Cluster | Manifest nur validieren (`kubeconform`) | kein Anwenden |
| `kubeconform` fehlt oder Schemas nicht ladbar | Ressourcenliste mit PyYAML (Lab 6.2, Aufgabe 7.1) | prüft Syntax und Vollständigkeit, nicht die Feldnamen |

Module 1 und 2 brauchen weder Docker noch Ollama.

## Häufige Probleme

| Symptom | Ursache | Lösung |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'mcp'` | venv nicht aktiv oder Pakete nicht installiert | `source .venv/bin/activate` (Git Bash: `source .venv/Scripts/activate`), danach `pip install -r requirements.txt` |
| `bash: .venv/bin/activate: No such file or directory` | Windows: venv liegt unter `Scripts` | `source .venv/Scripts/activate` |
| `cp: command not found` oder `'cp' is not recognized` | Befehl in PowerShell oder `cmd` statt Git Bash | Git Bash öffnen |
| `json.decoder.JSONDecodeError` bei `--call` | JSON-Argument nicht in Bash-Quoting | Git Bash verwenden, Argument wie gezeigt in `'…'` |
| `ImportError: cannot import name 'FastMCP'` | Code aus einem SDK-1.x-Tutorial | `from mcp.server import MCPServer` verwenden (SDK 2.3.0) |
| `python: command not found` | Befehl heißt `python3` bzw. `py` | passenden Befehl nutzen, venv danach aktivieren (dann gilt `python`) |
| `pip install` bricht mit Zeitüberschreitung ab | Proxy oder Firewall | Proxy-Einstellung der Kunden-IT, sonst vorbereitete venv |
| `npx` lädt endlos | Registry nicht erreichbar | Netzwerk prüfen, sonst Skript-Client verwenden |
| `Cannot connect to the Docker daemon` | Docker Desktop nicht gestartet | Docker Desktop starten, `docker version` wiederholen |
| `ollama list` zeigt kein `qwen3:8b` | Modell nicht geladen | Kunden-IT informieren; bis dahin Replay-LLM |
| Server startet und „hängt“ | normales Verhalten: stdio-Server wartet auf einen Client | mit `Ctrl+C` beenden, Client oder Inspector verwenden |
| `Address already in use` | Port 8000, 8001 oder 8080 belegt | belegenden Prozess beenden |
| Inspector-Befehl findet `python` nicht | venv nicht aktiv | venv aktivieren, dann Inspector starten |

## Checkliste

- `ls project` im Ordner `output/` zeigt `examples`, `starters`, `playground`, `shared`.
- Windows: Terminal ist Git Bash (`echo $BASH_VERSION` gibt eine Version aus).
- `python --version` zeigt 3.11 oder höher.
- venv ist aktiv (`(.venv)` im Prompt), `pip install -r requirements.txt` endet ohne Fehler.
- `python shared/script_client.py --server examples/m01-mcp-foundations-and-setup/l02-dev-setup/server.py` zeigt `Server: vantra-ops · Protokoll 2026-07-28`.
- `npx @modelcontextprotocol/inspector --cli …` liefert `{ "tools": [] }`.
- `ollama list` nennt `qwen3:8b` (ab Modul 4 relevant).
- `docker version` antwortet (ab Modul 6 relevant).
- `kubeconform -v` zeigt eine Version (Lab 6.2).
