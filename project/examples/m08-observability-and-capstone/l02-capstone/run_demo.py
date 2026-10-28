"""Mini-Workflow des Abschlussprojekts (Lab 8.2): Ticket abfragen -> Deployment-Log prüfen -> Policy-Entscheidung.

Führt den Ablauf mit dem Replay-LLM dreimal aus und vergleicht Rollen und Bestätigung:
  viewer                  -> der schreibende Schritt wird vom Server abgelehnt (policy_denied)
  operator, --confirm yes -> der schreibende Schritt gelingt nach Bestätigung
  operator, --confirm none -> der Server lehnt ohne Bestätigung ab (confirmation_required)

Aufruf (im Projektordner):  python examples/m08-observability-and-capstone/l02-capstone/run_demo.py
Mit Container:              ... run_demo.py --url http://localhost:8000/mcp   (Rolle bestimmt der Container, VANTRA_ROLE)
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = next(p for p in HERE.parents if (p / "shared").is_dir())


def run(title: str, extra: list[str]) -> None:
    print(f"\n=== {title} ===", flush=True)
    cmd = [sys.executable, str(PROJECT / "shared/agent_client.py"), "--replay", "workflow", *extra]
    subprocess.run(cmd, cwd=PROJECT, check=False)


if __name__ == "__main__":
    if "--url" in sys.argv:
        url = sys.argv[sys.argv.index("--url") + 1]
        run("Workflow gegen den Container", ["--url", url, "--confirm", "yes"])
    else:
        server = str(HERE / "server.py")
        run("Rolle viewer (nur lesen)", ["--server", server, "--role", "viewer", "--confirm", "yes"])
        run("Rolle operator mit Bestätigung", ["--server", server, "--role", "operator", "--confirm", "yes"])
        run("Rolle operator ohne Bestätigung (--confirm none)", ["--server", server, "--role", "operator", "--confirm", "none"])
