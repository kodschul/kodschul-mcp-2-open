# Lab 1.2 – Übung: Dev-Setup und erster eigener MCP-Server

**Dauer:** ca. 25 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Ja – `playground/server.py` ist der Startpunkt für Lab 2.2
**Arbeitsdatei:** `playground/server.py`
**Starter:** `starters/m01-l02-first-server.py`
**Vergleichsbeispiel:** `examples/m01-mcp-foundations-and-setup/l02-dev-setup-first-server/server.py`

## Vorbereitung

- Terminal im Ordner `output/project/`, venv aktiv (`(.venv)` im Prompt), Pakete installiert (`00-setup-and-installation.md`).
- `python -c "import mcp"` läuft ohne Fehler.

## Aufgaben

1. Kopiere den Starter nach `playground/server.py`: `cp starters/m01-l02-first-server.py playground/server.py`. Starte ihn einmal mit `python playground/server.py` und notiere die Meldung.
2. Setze den Servernamen `vantra-ops` und eine kurze `instructions`-Beschreibung (`TODO(Aufgabe 1)`).
3. Ersetze die `raise SystemExit(...)`-Zeile durch den Start des Servers über stdio (`TODO(Aufgabe 2)`).
4. Starte `python playground/server.py`. Beobachte, dass keine Ausgabe erscheint, und beende mit `Ctrl+C`.
5. Verbinde den Server mit dem Skript-Client: `python shared/script_client.py --server playground/server.py`. Notiere Servername, Protokollversion und Tools.
6. Verbinde denselben Server mit dem MCP Inspector (`npx @modelcontextprotocol/inspector python playground/server.py`), liste die Tools auf und notiere das Ergebnis. Ohne Browser: `--cli` mit `--method tools/list`.
7. Vergleiche `playground/server.py` mit dem Vergleichsbeispiel und notiere Unterschiede.

## Checkpoint

- Der Starter meldet vor der Änderung `TODO(Aufgabe 2): Server starten …`.
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
