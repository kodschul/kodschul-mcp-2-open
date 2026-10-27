# Lab 4.1 – Lösung: LLM-Agent-Client anbinden

Vollständiger Stand: `examples/m04-agent-prototype/l01-agent-client-connection/agent.py`.

## Aufgabe 1: Serverparameter

```python
params = StdioServerParameters(command=sys.executable, args=[SERVER])
async with Client(params) as client:
```

`sys.executable` startet den Server mit demselben Python wie der Client (aktive venv); `SERVER` zeigt auf `server.py` neben `agent.py`.

## Aufgabe 2: `to_openai_tool`

```python
def to_openai_tool(tool) -> dict:
    """MCP-Tool-Beschreibung (name, description, inputSchema) im Format des LLM-Backends."""
    return {
        "type": "function",
        "function": {"name": tool.name, "description": tool.description or "", "parameters": tool.input_schema},
    }
```

`input_schema` ist bereits ein JSON-Schema; `description or ""` vermeidet `None` bei Tools ohne Docstring.

## Aufgabe 3: Tool-Call ausführen

```python
for call in reply["tool_calls"]:
    print(f"  → Tool-Call: {call['name']}({json.dumps(call['arguments'], ensure_ascii=False)})")
    result = await client.call_tool(call["name"], call["arguments"])
    text = "\n".join(c.text for c in result.content if c.type == "text")
    print(f"  ← {'FEHLER' if result.is_error else 'ok'}: {text[:100]!r}")
    messages.append({"role": "tool", "tool_call_id": call["id"],
                     "content": ("FEHLER: " if result.is_error else "") + text})
```

Das Ergebnis geht mit `tool_call_id` zurück an das Modell; das Präfix `FEHLER:` macht Tool-Fehler im Text erkennbar.

## Aufgabe 4: Replay-Lauf

`python playground/agent.py --replay` (Skript-Agent, Replay-LLM):

```text
Entdeckte Tools: get_ticket, get_deployment_log, update_ticket_status

Nutzer: Zeige Ticket VAN-102
  → Tool-Call: get_ticket({"ticket_id": "VAN-102"})
  ← ok: '{\n  "id": "VAN-102",\n  "title": "Login-Seite lädt nach Release 2.14 sehr langsam",\n  "status": "open'
Agent: Ticket VAN-102: Login-Seite lädt nach Release 2.14 sehr langsam (Status open, Version 3).

Nutzer: Zeige das Deployment-Log dazu
  → Tool-Call: get_deployment_log({})
  ← ok: '{\n  "id": "dep-2041",\n  "ticket_id": "VAN-102",\n  "service": "auth-service",\n  "version": "2.14.1",\n'
Agent: Deployment dep-2041 (auth-service 2.14.1, Status degraded). Letzte Zeilen: auth      token cache disabled by config key AUTH_CACHE_TTL=0;  deploy    finished with warnings, rollback not triggered
```

Der zweite Tool-Call trägt keine ID (`{}`): Der Server löst sie aus dem Kontext aus Lab 3.2 auf.

## Aufgabe 5: Echtes LLM

Die Ausgabe hängt vom Modell ab und ist hier nicht festgelegt. Erwartet wird derselbe Ablauf wie im Replay-Lauf: `get_ticket` mit `ticket_id` `VAN-102`, danach `get_deployment_log` mit oder ohne `ticket_id`. Beides ist richtig, weil der Kontext die ID ergänzt. Abweichungen (falsches Tool, erfundene ID, mehrere Aufrufe) gehören in die Notizen von Lab 4.2.

## Erweiterung: überlappende Tools

Zwei Beobachtungen sind festzuhalten, ohne sie vorwegzunehmen: welches Tool das Modell bei der vagen Frage wählt und ob die Wahl über mehrere Läufe gleich bleibt. Ein abgrenzender Docstring („Nur Deployment-Logs, nicht Ticketdaten“) kann die Verwechslung verringern; ein festes Ergebnis lässt sich ohne Modelllauf nicht angeben und hängt von Modell und Größe ab. Vorgehen: Frage, gewähltes Tool und Argumente je Lauf in die Notizen eintragen.
