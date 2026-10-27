"""Skript-Client ohne LLM: Server verbinden, Tools auflisten, optional ein Tool aufrufen.

Beispiele (im Projektordner):
  python shared/script_client.py --server playground/server.py
  python shared/script_client.py --server playground/server.py --call get_ticket '{"ticket_id": "VAN-102"}'
  python shared/script_client.py --url http://localhost:8000/mcp --call get_deployment_log '{"ticket_id": "VAN-102"}'
"""

import argparse
import asyncio
import json
import os
import sys

from mcp import Client
from mcp.client.stdio import StdioServerParameters
from mcp.shared.exceptions import MCPError


async def run(args) -> int:
    env = {**os.environ, **({"VANTRA_ROLE": args.role} if args.role else {})}
    client = Client(args.url) if args.url else Client(StdioServerParameters(command=sys.executable, args=[args.server], env=env))
    async with client:
        info = client.server_info
        print(f"Server: {info.name if info else '?'} · Protokoll {client.protocol_version}")
        tools = (await client.list_tools()).tools
        print("Tools:", ", ".join(t.name for t in tools) or "(keine)")
        if args.call:
            name, raw = args.call
            try:
                result = await client.call_tool(name, json.loads(raw))
            except MCPError as exc:
                print(f"Protokollfehler {exc.error.code}: {exc.error.message}")
                return 1
            print(f"is_error={result.is_error}")
            for block in result.content:
                print(getattr(block, "text", block))
            if result.structured_content:
                print("structured_content:", json.dumps(result.structured_content, ensure_ascii=False))
            return 1 if result.is_error else 0
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--server", default=os.getenv("MCP_SERVER_SCRIPT", "playground/server.py"))
    parser.add_argument("--url", default=os.getenv("MCP_SERVER_URL"))
    parser.add_argument("--role", help="VANTRA_ROLE für den stdio-Server")
    parser.add_argument("--call", nargs=2, metavar=("TOOL", "JSON_ARGS"))
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    sys.exit(main())
