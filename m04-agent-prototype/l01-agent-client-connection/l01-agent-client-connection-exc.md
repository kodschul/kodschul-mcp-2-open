# Lab 4.1 – Übung: LLM-Agent-Client anbinden

**Dauer:** ca. 30 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja — `playground/agent.py` ist der Agent-Client des Prototyps; Lab 4.2 testet ihn, Tag 2 nutzt `shared/agent_client.py` mit demselben Prinzip.
**Arbeitsdatei:** `playground/agent.py` (Server: `playground/server.py`)
**Starter:** `starters/m04-l01-agent-client.py`
**Beispiel zum Vergleich:** `examples/m04-agent-prototype/l01-agent-client-connection/` (`agent.py`, `server.py`, `context.py`)

## Vorbereitung

- Terminal im Projektordner `output/project/`, virtuelle Umgebung aktiv.
- `playground/server.py` und `playground/context.py` enthalten den Stand aus Lab 3.3 (drei Tools). Fehlen sie, kopiere beide Dateien aus `examples/m03-context-and-state/l03-multi-agent-sync/`.
- Kopiere den Starter: `cp starters/m04-l01-agent-client.py playground/agent.py`.
- LLM: Ollama ist vorinstalliert. Falls `.env` fehlt: `cp .env.example .env`. Die Standardwerte zeigen auf Ollama mit `qwen3:8b`.

## Aufgaben

1. Lege in `playground/agent.py` die Serverparameter an (`TODO(Aufgabe 1)`): `StdioServerParameters` mit `command=sys.executable` und `args=[SERVER]`.
2. Implementiere `to_openai_tool` (`TODO(Aufgabe 2)`): Wandle `tool.name`, `tool.description` und `tool.input_schema` in das Funktionsformat `{"type": "function", "function": {...}}` um.
3. Führe den Tool-Call aus (`TODO(Aufgabe 3)`): Rufe `client.call_tool(call["name"], call["arguments"])` auf, lege den Text aller `TextContent`-Elemente aus `result.content` in `text` ab und gib mit `print` eine Zeile `← ok` bzw. `← FEHLER` aus, abhängig von `result.is_error`.
4. Starte den Agenten mit dem Replay-LLM: `python playground/agent.py --replay`. Prüfe, dass beide Tool-Calls des Dialogs laufen.
5. Starte den Agenten mit dem echten LLM: `python playground/agent.py`. Gib nacheinander `Zeige Ticket VAN-102` und `Zeige das Deployment-Log dazu` ein, danach eine leere Zeile zum Beenden. Notiere, welche Tool-Calls das Modell wählt.

## Checkpoint

- Die Ausgabe beginnt mit `Entdeckte Tools: get_ticket, get_deployment_log, update_ticket_status`.
- Beim Replay-Lauf erscheinen `→ Tool-Call: get_ticket({"ticket_id": "VAN-102"})` und `→ Tool-Call: get_deployment_log({})`, beide mit `← ok`.
- Die Antwort zum Deployment nennt `dep-2041` und den Status `degraded`.
- Mit echtem LLM ruft das Modell für die Ticketfrage `get_ticket` und für die Log-Frage `get_deployment_log` auf (Abweichungen werden notiert, nicht korrigiert).

## Abschlusskriterien

- `playground/agent.py` startet ohne `NotImplementedError` und ohne Ausnahme.
- Beide Tools werden über natürliche Sprache aufgerufen (mit echtem LLM oder als Skript-Agent mit Replay, im Protokoll gekennzeichnet).
- Die Tool-Liste wird beim Start vom Server entdeckt, nicht im Client fest eingetragen.

## Erweiterung (optional)

Stelle mit echtem LLM zwei Fragen, die das Modell zwischen den Tools schwanken lassen könnten (z. B. `Was ist mit dem Login los?`). Notiere die gewählten Tool-Calls. Formuliere danach in `playground/server.py` die Beschreibung (Docstring) von `get_deployment_log` abgrenzend um („Nur Deployment-Logs, nicht Ticketdaten“) und vergleiche. Replay ändert sich dadurch nicht: Das Skript wählt feste Tool-Calls.

## Fallback

- Ollama langsam, Modell fehlt oder Tool-Auswahl falsch: Aufgabe 5 entfällt, der Replay-Lauf aus Aufgabe 4 genügt. Er ist ein Skript-Agent; die Tool-Auswahl ist vorgegeben und nicht vom Modell getroffen.
- Stattdessen kann das fertige `shared/agent_client.py` laufen: `python shared/agent_client.py --server playground/server.py --replay`.
- Bleibt Aufgabe 1 bis 3 hängen: Vergleiche mit `examples/m04-agent-prototype/l01-agent-client-connection/agent.py`.
