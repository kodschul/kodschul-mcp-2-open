"""Minimaler Agent-Client (Lab 4.1): MCP-Tools entdecken, an ein LLM geben, Tool-Calls ausführen.

Aufruf (im Projektordner):
  python examples/m04-agent-prototype/l01-agent-client/agent.py            # echtes LLM laut .env
  python examples/m04-agent-prototype/l01-agent-client/agent.py --replay   # Replay-LLM
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
    """MCP-Tool-Beschreibung (name, description, inputSchema) im Format des LLM-Backends."""
    return {
        "type": "function",
        "function": {"name": tool.name, "description": tool.description or "", "parameters": tool.input_schema},
    }


async def main() -> None:
    load_env()
    replay = "dialog" if "--replay" in sys.argv else None
    prompts = SCENARIOS["dialog"] if replay else None
    llm = make_llm(replay)

    params = StdioServerParameters(command=sys.executable, args=[SERVER])
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

            while True:  # Tool-Schleife: solange das LLM Tools aufrufen will
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
                    result = await client.call_tool(call["name"], call["arguments"])
                    text = "\n".join(c.text for c in result.content if c.type == "text")
                    print(f"  ← {'FEHLER' if result.is_error else 'ok'}: {text[:100]!r}")
                    messages.append({"role": "tool", "tool_call_id": call["id"], "content": ("FEHLER: " if result.is_error else "") + text})
            if prompts and not queue:
                break


if __name__ == "__main__":
    asyncio.run(main())
