# Lab 1.2 – Lösung: Dev-Setup und erster eigener MCP-Server

## Aufgabe 1: Starter kopieren und starten

```bash
cp starters/m01-l02-first-server.py playground/server.py
python playground/server.py
```

```text
TODO(Aufgabe 2): Server starten, hier fehlt der Aufruf von mcp.run()
```

Der Starter bricht bewusst ab, weil `mcp.run()` fehlt.

## Aufgabe 2: Name und Beschreibung

```python
mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent. Noch ohne Tools: Aufbau folgt in den nächsten Labs.",
)
```

Der Text von `instructions` darf abweichen. Der Name `vantra-ops` bleibt, weil spätere Labs und Tests ihn erwarten.

## Aufgabe 3: Server starten

```python
if __name__ == "__main__":
    mcp.run()  # stdio: der Client startet diesen Prozess und spricht über stdin/stdout
```

`mcp.run()` ohne Argumente nutzt stdio, den Standardtransport.

## Aufgabe 4: Direkter Start

`python playground/server.py` zeigt keine Ausgabe und wartet auf Eingaben auf stdin. Das ist korrekt: der Server spricht erst, wenn ein Client eine Nachricht sendet. `Ctrl+C` beendet den Prozess.

## Aufgabe 5: Skript-Client

```bash
python shared/script_client.py --server playground/server.py
```

```text
Server: vantra-ops · Protokoll 2026-07-28
Tools: (keine)
```

## Aufgabe 6: MCP Inspector

```bash
npx @modelcontextprotocol/inspector python playground/server.py
```

Die Weboberfläche zeigt Servername `vantra-ops` und einen leeren Tools-Bereich. Die Konsolenvariante:

```bash
npx @modelcontextprotocol/inspector --cli python playground/server.py --method tools/list
```

```json
{
  "tools": []
}
```

## Aufgabe 7: Vergleich mit dem Beispiel

Der Server im Beispiel `examples/m01-mcp-foundations-and-setup/l02-dev-setup-first-server/server.py` ist bis auf Kommentare und den `instructions`-Text identisch:

```python
from mcp.server import MCPServer

mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent. Noch ohne Tools: Aufbau folgt in den nächsten Labs.",
)

if __name__ == "__main__":
    mcp.run()
```

## Erweiterung

Mit dem Namen `vantra-demo` zeigt der Skript-Client `Server: vantra-demo · Protokoll 2026-07-28`. Der Name kommt aus `MCPServer(...)` und wird bei jeder Abfrage mitgeliefert.

Bei stdio läuft das Protokoll über stdout: eine zusätzliche Textzeile würde nicht als JSON-RPC-Nachricht lesbar sein und die Verbindung stören. Ausgaben und Logs gehören auf stderr.
