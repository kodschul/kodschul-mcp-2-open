"""Gemeinsame Hilfen der Tests: stdio-Verbindung zu den Beispiel-Servern, Mock-API im Hintergrund."""

import json
import os
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from mcp import Client
from mcp.client.stdio import StdioServerParameters

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

EX = PROJECT / "examples"
SRV_EMPTY = EX / "m01-mcp-foundations-and-setup/l02-dev-setup-first-server/server.py"
SRV_TOOL = EX / "m02-protocol-and-messages/l02-first-tool/server.py"
SRV_CONTEXT = EX / "m03-context-and-state/l02-context-schema-implementation/server.py"
SRV_CONFLICT = EX / "m03-context-and-state/l03-multi-agent-sync/server.py"
SRV_AGENT = EX / "m04-agent-prototype/l01-agent-client-connection/server.py"
SRV_CONTAINER = EX / "m05-cloud-integration/l02-container-prep/server.py"
SRV_SECURE = EX / "m07-security-hardening/l01-access-control-sandboxing/server.py"
SRV_LOGGING = EX / "m08-observability-and-capstone/l01-monitoring-setup/server.py"
SRV_CAPSTONE = EX / "m08-observability-and-capstone/l02-capstone-integration/server.py"


@asynccontextmanager
async def connect(server: Path, **env: str):
    """Startet den Server als stdio-Kindprozess und verbindet einen Client."""
    full_env = {**os.environ, **env}
    params = StdioServerParameters(command=sys.executable, args=[str(server)], env=full_env)
    async with Client(params) as client:
        yield client


def text_of(result) -> str:
    return "\n".join(c.text for c in result.content if getattr(c, "type", "") == "text")


def json_of(result):
    return json.loads(text_of(result))


@pytest.fixture
def mock_api():
    """Mock-API im Hintergrund-Thread auf freiem Port; liefert die Basis-URL."""
    from shared.mock_api import app as mock_app

    mock_app.STORE.reset()
    server = mock_app.make_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()
    mock_app.STORE.reset()
