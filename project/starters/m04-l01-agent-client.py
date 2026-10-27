"""Starter Lab 4.1: Agent-Client mit Lücken. Kopieren nach playground/agent.py und vervollständigen.

Aufruf (im Projektordner):
  python playground/agent.py --replay    # Replay-LLM, kein Modell nötig
  python playground/agent.py             # echtes LLM laut .env (Ollama oder Cloud)
Der Server ist playground/server.py (Stand Lab 3.3).
"""

import asyncio
import json
import sys
from pathlib import Path

PROJECT = next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())
sys.path.insert(0, str(PROJECT))

from mcp import Client
from mcp.client.stdio import StdioServerParameters

from shared.agent_client import SYSTEM_PROMPT, load_env, make_llm
from shared.replay_llm import SCENARIOS

SERVER = str(Path(__file__).resolve().parent / "server.py")


def to_openai_tool(tool) -> dict:
    # TODO(Aufgabe 2): MCP-Tool (tool.name, tool.description, tool.input_schema) in das Funktionsformat des LLM
    #   umwandeln: {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}
    raise NotImplementedError("TODO(Aufgabe 2): to_openai_tool implementieren")


async def main() -> None:
    load_env()
    replay = "dialog" if "--replay" in sys.argv else None
    prompts = SCENARIOS["dialog"] if replay else None
    llm = make_llm(replay)

    # TODO(Aufgabe 1): StdioServerParameters für SERVER anlegen (command=sys.executable, args=[SERVER])
    params = None
    async with Client(params) as client:
        tools = (await client.list_tools()).tools
        llm_tools = [to_openai_tool(t) for t in tools]
        print("Entdeckte Tools:", ", ".join(t.name for t in tools))

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        queue = list(prompts or [])
        while True:
            prompt = queue.pop(0) if prompts else input("\nNutzer (leer = Ende): ").strip()
            if not prompt:
                break
            print(f"\nNutzer: {prompt}")
            messages.append({"role": "user", "content": prompt})

            while True:
                reply = llm.chat(messages, llm_tools)
                if not reply["tool_calls"]:
                    messages.append({"role": "assistant", "content": reply["content"]})
                    print(f"Agent: {reply['content']}")
                    break
                messages.append({
                    "role": "assistant",
                    "content": reply["content"],
                    "tool_calls": [
                        {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}}
                        for c in reply["tool_calls"]
                    ],
                })
                for call in reply["tool_calls"]:
                    print(f"  → Tool-Call: {call['name']}({json.dumps(call['arguments'], ensure_ascii=False)})")
                    # TODO(Aufgabe 3): Tool über den MCP-Client aufrufen: client.call_tool(call["name"], call["arguments"])
                    #   und den Text aus result.content (TextContent) in `text` ablegen; result.is_error beachten
                    result = None
                    text = ""
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": ("FEHLER: " if result and result.is_error else "") + text})
            if prompts and not queue:
                break


if __name__ == "__main__":
    asyncio.run(main())
