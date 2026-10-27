# Lab 4.1: LLM-Agent-Client anbinden

**Leitfragen:**

<details>
<summary>Woran erkennt der Agent, welches Tool zu einer Nutzeranfrage passt?</summary>

Das Modell wählt anhand von Tool-Name, Beschreibung (Docstring) und Eingabeschema, die der Client aus `tools/list` übernimmt. Eine Regel im Client gibt es nicht; die Auswahl trifft das Modell.

</details>

<details>
<summary>Was passiert, wenn zwei Tools fachlich überlappen?</summary>

Das Modell kann das falsche oder wechselnd das eine oder andere Tool wählen. Abhilfe: ein Tool je Zweck, klare Namen und Beschreibungen, die Abgrenzung („nicht für …“) und Argumente benennen.

</details>

- Ein Agent-Client verbindet drei Teile: MCP-Server (Tools), LLM (Auswahl) und eine Schleife, die Tool-Calls ausführt.
- Der Server kennt das Modell nicht; das Modell kennt den Server nur über die weitergereichten Tool-Beschreibungen.

## Ablauf eines Agenten-Gesprächs

```text
Nutzer ──► Client ──► LLM
             │          │ liefert Text ODER Tool-Calls
             │◄─────────┘
             │  tools/call (MCP, stdio)
             ▼
        MCP-Server ──► Ergebnis ──► Client ──► LLM ──► Antwort an Nutzer
```

| Schritt | MCP / LLM | Code in `agent.py` |
| --- | --- | --- |
| 1. Server starten, verbinden | stdio-Kindprozess | `Client(StdioServerParameters(...))` |
| 2. Tools entdecken | `tools/list` | `(await client.list_tools()).tools` |
| 3. Tools umwandeln | MCP-Schema → LLM-Funktionsformat | `to_openai_tool(tool)` |
| 4. Nachrichten senden | Nutzertext + Tool-Liste an das LLM | `llm.chat(messages, llm_tools)` |
| 5. Tool-Calls ausführen | `tools/call` je Wunsch des Modells | `client.call_tool(name, arguments)` |
| 6. Ergebnis zurückgeben | Rolle `tool` in der Nachrichtenliste | `messages.append({"role": "tool", ...})` |
| 7. Wiederholen bis Text kommt | Schleife | `while True` ohne `tool_calls` beenden |

## Tools in das LLM-Format übersetzen

Ein MCP-Tool hat `name`, `description` und `input_schema`. OpenAI-kompatible Backends erwarten dasselbe als Funktion:

```python
def to_openai_tool(tool) -> dict:
    return {
        "type": "function",
        "function": {"name": tool.name, "description": tool.description or "", "parameters": tool.input_schema},
    }
```

Das Eingabeschema ist bereits ein JSON-Schema und kann unverändert als `parameters` dienen. Die Beschreibung stammt aus dem Docstring des Tools (Lab 2.2, 3.2).

## Die Tool-Schleife

Vollständiger Agent: `examples/m04-agent-prototype/l01-agent-client-connection/agent.py`. Kern:

```python
params = StdioServerParameters(command=sys.executable, args=[SERVER])   # Server als Kindprozess
async with Client(params) as client:
    tools = (await client.list_tools()).tools                           # Entdeckung
    llm_tools = [to_openai_tool(t) for t in tools]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    ...
    messages.append({"role": "user", "content": prompt})
    while True:                                                         # Tool-Schleife
        reply = llm.chat(messages, llm_tools)
        if not reply["tool_calls"]:                                     # Text = fertig
            print(f"Agent: {reply['content']}")
            break
        for call in reply["tool_calls"]:
            result = await client.call_tool(call["name"], call["arguments"])
            text = "\n".join(c.text for c in result.content if c.type == "text")
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": ("FEHLER: " if result.is_error else "") + text})
```

- `result.is_error` markiert Tool-Fehler; sie gehen als Text an das Modell zurück, damit es reagieren kann.
- Die Nachrichtenliste `messages` ist das Kontextfenster: Die Liste wächst mit jedem Tool-Ergebnis.
- Der Kontext aus Lab 3.2 liegt im Server; deshalb braucht „Zeige das Deployment-Log dazu“ keine ID im Argument.

## LLM-Backend

| Aspekt | Festlegung im Projekt |
| --- | --- |
| Schnittstelle | OpenAI-kompatibel (`chat.completions` mit `tools`) |
| Standard lokal | Ollama, `LLM_BASE_URL=http://localhost:11434/v1`, `LLM_MODEL=qwen3:8b`, `LLM_API_KEY=ollama` |
| Wechsel auf Cloud-Anbieter | nur über `.env` (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`) |
| Schlüssel | gehört dem Client und wird nicht an den Server-Prozess weitergegeben |
| Ohne Modell | `--replay`: Replay-LLM (`shared/replay_llm.py`) spielt feste Tool-Calls ab |

Ein Lauf mit Replay ist ein Skript-Agent: Die Tool-Auswahl ist vorgegeben, nicht vom Modell getroffen. Er prüft Verdrahtung und Server, nicht die Tool-Auswahl eines Modells. Kleine Modelle wählen Tools weniger zuverlässig; Ergebnisse mit echtem LLM können schwanken.

## Fazit

- Der Agent-Client entdeckt Tools mit `tools/list`, reicht sie als Funktionen an das LLM und führt dessen `tools/call`-Wünsche aus.
- Name, Beschreibung und Schema der Tools steuern die Auswahl; überlappende Tools verschlechtern sie.
- Ohne Modell prüft `--replay` die Verdrahtung als Skript-Agent.

Die Übung ergänzt die drei Lücken des Starters und lässt den Agenten beide Tools über Sprache aufrufen.
