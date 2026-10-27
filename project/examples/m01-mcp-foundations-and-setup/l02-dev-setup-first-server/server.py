"""Vantra Ops Agent – leerer MCP-Server (Lab 1.2)."""

from mcp.server import MCPServer

mcp = MCPServer(
    "vantra-ops",
    instructions="MCP-Server des Vantra Ops Agent. Noch ohne Tools: Aufbau folgt in den nächsten Labs.",
)

if __name__ == "__main__":
    mcp.run()  # stdio: der Client startet diesen Prozess und spricht über stdin/stdout
