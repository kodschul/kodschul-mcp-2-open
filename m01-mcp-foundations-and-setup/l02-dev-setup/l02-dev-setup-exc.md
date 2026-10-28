# Lab 1.2 – Übung: Dev-Setup und erster eigener MCP-Server

**Dauer:** ca. 25 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Ja – `playground/server.py` ist der Startpunkt für Lab 2.2
**Arbeitsdatei:** `playground/server.py`
**Starter:** `starters/m01-l02-first-server.py`
**Vergleichsbeispiel:** `examples/m01-mcp-foundations-and-setup/l02-dev-setup/server.py`

## Vorbereitung

- Bash-Terminal (Windows: Git Bash) im Ordner `output/project/`, venv aktiv (`(.venv)` im Prompt), Pakete installiert ([`../../00-setup-and-installation.md`](../../00-setup-and-installation.md), Schritt 0–3).
- `python -c "import mcp"` läuft ohne Fehler.

## Aufgaben

1. Kopiere den Starter nach `playground/server.py`: `cp starters/m01-l02-first-server.py playground/server.py`. Starte ihn einmal mit `python playground/server.py` und notiere die Meldung.
2. Setze den Servernamen `vantra-ops` und eine kurze `instructions`-Beschreibung (`TODO(Aufgabe 2)`).
3. Ersetze die `raise SystemExit(...)`-Zeile durch den Start des Servers über stdio (`TODO(Aufgabe 3)`).
4. Starte `python playground/server.py`. Beobachte, dass keine Ausgabe erscheint, und beende mit `Ctrl+C`.
5. Verbinde den Server mit dem Skript-Client: `python shared/script_client.py --server playground/server.py`. Notiere Servername, Protokollversion und Tools.
6. Verbinde denselben Server mit dem MCP Inspector: Starte `npx @modelcontextprotocol/inspector python playground/server.py`, öffne die angezeigte Adresse mit Token, prüfe **Transport Type** `STDIO`, **Command** `python`, **Arguments** `playground/server.py`, klicke **Connect**, öffne den Tab **Tools** und klicke **List Tools**. Notiere das Ergebnis und beende mit `Ctrl+C`. Ohne Browser: `npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/list`.
7. Vergleiche `playground/server.py` mit dem Vergleichsbeispiel und notiere Unterschiede.

## Checkpoint

- Der Starter meldet vor der Änderung `TODO(Aufgabe 3): Server starten …`.
- Der Skript-Client zeigt `Server: vantra-ops · Protokoll 2026-07-28` und `Tools: (keine)`.
- Der Inspector bzw. `--cli` zeigt eine leere Tool-Liste.
- `python playground/server.py` läuft ohne Fehlermeldung und wartet.

## Abschlusskriterien

- `playground/server.py` enthält den Servernamen `vantra-ops` und `mcp.run()`.
- Ein Client (Skript-Client oder Inspector) hat den Server erreicht, ohne dass `server.py` geändert werden musste.
- Der Transport des Servers ist benannt (stdio).

## Erweiterung (optional)

Ändere den Servernamen in `vantra-demo`, starte den Skript-Client erneut und beobachte die Zeile `Server:`. Setze den Namen danach zurück. Erkläre, warum `print("...")` im Server bei stdio den Client stören würde.

## Fallback

- Ohne Node/`npx` entfällt Aufgabe 6; der Skript-Client prüft dieselbe Verbindung.
- Ohne Installationsrechte die vorbereitete venv aktivieren.
- Bei einem nicht lauffähigen Starter: das Vergleichsbeispiel nach `playground/server.py` kopieren und ab Aufgabe 4 weiterarbeiten.
