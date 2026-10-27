# Lab 3.2 – Übung: Kontextschema entwerfen und einbauen

**Dauer:** ca. 50 Minuten (Einzel/Paar)
**Ändert die Vantra-Projektbasis?** Ja — `playground/context.py` und das zweite Tool in `playground/server.py` sind Grundlage für Lab 3.3 und Modul 4.
**Arbeitsdatei:** `playground/context.py` und `playground/server.py`
**Starter:** `starters/m03-l02-context.py`
**Beispiel zum Vergleich:** `examples/m03-context-and-state/l02-context-schema-implementation/` (`context.py`, `server.py`)

## Vorbereitung

- Terminal im Projektordner `output/project/`, virtuelle Umgebung aktiv.
- `playground/server.py` enthält den Stand aus Lab 2.2 (Tool `get_ticket`). Fehlt die Datei, kopiere `examples/m02-protocol-and-messages/l02-first-tool/server.py` nach `playground/server.py`.
- Kopiere den Starter: `cp starters/m03-l02-context.py playground/context.py`.

## Aufgaben

1. Vervollständige in `playground/context.py` das Schema (`TODO(Aufgabe 1)`): Ergänze das Datenfeld `last_deployment` in `SessionContext` und eine zweite Zeile in `SESSION_SCHEMA` mit Feld, Quelle, Lebensdauer und Sichtbarkeit. Ergänze danach zwei Zeilen für die Felder, die nur der Server nutzt (`ticket_versions`, `tool_calls`).
2. Implementiere `remember_deployment` (`TODO(Aufgabe 2)`): Nur `id`, `service`, `version`, `status` landen in `last_deployment`.
3. Implementiere `resolve_ticket_id` und `to_llm_view` (`TODO(Aufgabe 3)`): Eine explizite ID gewinnt, sonst gilt die ID des zuletzt abgefragten Tickets; `to_llm_view` gibt nur `last_ticket` und `last_deployment` zurück. Starte danach `python playground/context.py`.
4. Binde den Kontext in `playground/server.py` ein (`TODO(Aufgabe 4)`): Importiere `session` aus `context` und rufe in `get_ticket` nach erfolgreicher Abfrage `session.remember_ticket(ticket)` auf. Zähle jeden Tool-Aufruf mit `session.tool_calls += 1`.
5. Ergänze das zweite Tool `get_deployment_log(ticket_id: str | None = None, tail: int = 20)` (`TODO(Aufgabe 5)`): ID über `session.resolve_ticket_id` auflösen, Deployment über `backend.latest_deployment` laden, mit `session.remember_deployment` merken, Metadaten plus die letzten `tail` Zeilen von `log` zurückgeben. Ist weder eine ID angegeben noch ein Ticket im Kontext, melde einen `ToolError`.
6. Prüfe das Zusammenspiel mit dem Skript-Client und dem Agent-Client (Befehle im Checkpoint).

## Checkpoint

- `python playground/context.py` gibt aus:

  ```text
  Kontext nach Ticket: {'id': 'VAN-102', 'title': 'Beispiel', 'status': 'open', 'version': 3}
  Aufgelöste Ticket-ID: VAN-102
  ```

- `python shared/script_client.py --server playground/server.py` listet `Tools: get_ticket, get_deployment_log`.
- `python shared/script_client.py --server playground/server.py --call get_deployment_log '{"ticket_id": "VAN-102", "tail": 2}'` zeigt `dep-2041` mit genau zwei Log-Zeilen.
- `python shared/script_client.py --server playground/server.py --call get_deployment_log '{}'` endet mit `is_error=True` und der Meldung zum fehlenden Ticket im Kontext.
- `python shared/agent_client.py --server playground/server.py --replay` ruft `get_ticket` und danach `get_deployment_log({})` auf; das Deployment gehört zu `VAN-102`.

## Abschlusskriterien

- `playground/context.py` enthält `SESSION_SCHEMA` mit vier Zeilen und die vollständige Klasse `SessionContext`.
- Kein Tool schreibt in das Feld eines anderen Tools.
- `playground/server.py` stellt zwei Tools bereit und verweist beide auf denselben `session`.

## Erweiterung (optional)

Ergänze in `playground/server.py` die Resource `context://session` (`TODO(Aufgabe 6)`), die `SESSION_SCHEMA` und `session.to_llm_view()` zurückgibt. Rufe danach `get_ticket` und `get_deployment_log` auf und lies die Resource mit einem kurzen Skript auf Basis von `Client.read_resource("context://session")`.

## Fallback

- Fehlt der Stand aus Lab 2.2, dient `examples/m02-protocol-and-messages/l02-first-tool/server.py` als Ausgangspunkt.
- Ohne Ollama oder bei langsamem Modell: `--replay` nutzen. Ein Lauf mit Replay-LLM ist ein Skript-Agent: Die Tool-Aufrufe sind vorgegeben, nicht vom Modell gewählt.
- Bleibt die Aufgabe hängen, ersetze `playground/context.py` und `playground/server.py` durch die Dateien aus dem Beispielordner und arbeite mit Lab 3.3 weiter.
