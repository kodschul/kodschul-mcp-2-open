# Lab 2.1 – Übung: JSON-RPC live am eigenen Server

**Dauer:** ca. 20 Minuten (Einzel oder Paar)
**Ändert die Vantra-Projektbasis?** Nein – `playground/raw_requests.py` ist ein Hilfsskript (wird in Lab 2.2 erweitert), `server.py` bleibt unverändert
**Arbeitsdatei:** `playground/raw_requests.py`
**Starter:** `starters/m02-l01-raw-requests.py`
**Vergleichsbeispiel:** `examples/m02-protocol-and-messages/l01-jsonrpc/raw_requests.py`

## Vorbereitung

- Bash-Terminal (Windows: Git Bash) im Ordner `output/project/`, venv aktiv.
- Der eigene Server aus Lab 1.2 liegt unter `playground/server.py` und zeigt im Skript-Client `Tools: (keine)`.
- Jede Nachricht wird mit der vorhandenen Funktion `send(proc, {...})` geschickt; Vorlage ist der `server/discover`-Aufruf im Starter.

## Aufgaben

1. Kopiere den Starter: `cp starters/m02-l01-raw-requests.py playground/raw_requests.py`. Führe ihn aus: `python playground/raw_requests.py`. Lies die Antwortzeile `<<` auf `server/discover` und notiere Servername, `instructions` und `supportedVersions`.
2. Ergänze bei `TODO(Aufgabe 2)` einen Request `tools/list` mit `id` 2 und `"params": {"_meta": META}`. Führe das Skript erneut aus und notiere, was unter `tools` steht.
3. Ergänze bei `TODO(Aufgabe 3)` einen Request mit der unbekannten Methode `nope/list`, `id` 3 und `_meta`. Notiere Fehlercode und Meldung.
4. Ergänze bei `TODO(Aufgabe 4)` einen Request `tools/list` mit `id` 4 **ohne** `params`. Notiere Fehlercode und Meldung und begründe, warum die Antwort `error` statt `result` enthält.
5. Ergänze bei `TODO(Aufgabe 5)` eine Notification `notifications/cancelled` mit `"params": {"requestId": 99, "_meta": META}` und **ohne** `id`, danach einen Request `tools/list` mit `id` 5. Notiere, ob die Notification eine Zeile `<<` erzeugt und welche `id` die nächste Antwort trägt.
6. Lege `playground/protokoll.md` an: je Nachricht eine Zeile mit Richtung, Art (Request, Response, Notification), `id` und `method`.

## Checkpoint

- `server/discover` liefert `"name":"vantra-ops"` und `"supportedVersions":["2026-07-28"]`.
- `tools/list` liefert `"tools":[]`.
- `nope/list` liefert ein `error` mit Code `-32601`, der Request ohne Hülle ein `error` mit Code `-32602`.
- Nach der Notification erscheint keine Antwortzeile; die nächste Antwort trägt `"id":5`.

## Abschlusskriterien

- `playground/raw_requests.py` läuft und gibt alle Nachrichten mit `>>` und `<<` aus.
- `playground/protokoll.md` listet jede Nachricht mit Art und `id`.
- Zu jeder Antwort ist der zugehörige Request über die `id` benannt.

## Erweiterung (optional)

Starte den Inspector mit dem Logging-Proxy (Abschnitt „Vertiefung: Live-Trace“ in [`../l01-jsonrpc-thx.md`](../l01-jsonrpc-thx.md)): **Command** `python`, **Arguments** `shared/trace_proxy.py -- python playground/server.py`. Klicke **Connect** und **List Tools** und vergleiche die Reihenfolge der Nachrichten im Terminal mit dem eigenen Protokoll.

## Fallback

- Skript hängt: `Ctrl+C`, `stderr=subprocess.DEVNULL` vorübergehend durch `stderr=None` ersetzen und die Fehlermeldung des Servers lesen.
- Starter nicht lauffähig: `python examples/m02-protocol-and-messages/l01-jsonrpc/raw_requests.py playground/server.py` ausführen und das Protokoll aus dieser Ausgabe erstellen; die erwarteten Antworten stehen als ECHTE AUSGABE am Dateiende.
- Ohne eigenen Server aus Lab 1.2: `cp examples/m01-mcp-foundations-and-setup/l02-dev-setup/server.py playground/server.py`.
