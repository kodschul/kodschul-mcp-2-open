"""Logging-Proxy zwischen MCP-Client und stdio-Server (Showcase A).

Der Client startet den Proxy statt des Servers; der Proxy startet den echten
Server als Kindprozess und leitet stdin/stdout unverändert weiter. Jede
JSON-RPC-Zeile erscheint zusätzlich auf stderr (und optional in einer Datei).

Aufruf:  python shared/trace_proxy.py [--log trace.log] -- python playground/server.py
"""

import argparse
import subprocess
import sys
import threading
import time

RESET, BLUE, GREEN = "\033[0m", "\033[34m", "\033[32m"


def _pump(src, dst, label: str, color: str, log_file) -> None:
    for line in iter(src.readline, b""):
        dst.write(line)
        dst.flush()
        text = line.decode("utf-8", errors="replace").rstrip()
        stamp = time.strftime("%H:%M:%S")
        use_color = color if sys.stderr.isatty() else ""
        end = RESET if use_color else ""
        print(f"{use_color}[{stamp}] {label} {text}{end}", file=sys.stderr, flush=True)
        if log_file:
            log_file.write(f"[{stamp}] {label} {text}\n")
            log_file.flush()
    if dst is not sys.stdout.buffer:
        dst.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", help="Trace zusätzlich in diese Datei schreiben")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- <Server-Befehl>")
    args = parser.parse_args()
    command = [c for i, c in enumerate(args.command) if not (i == 0 and c == "--")]
    if not command:
        parser.error("Server-Befehl fehlt, z. B.: -- python playground/server.py")

    log_file = open(args.log, "a", encoding="utf-8") if args.log else None
    server = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    threads = [
        threading.Thread(target=_pump, args=(sys.stdin.buffer, server.stdin, "CLIENT -> SERVER", BLUE, log_file), daemon=True),
        threading.Thread(target=_pump, args=(server.stdout, sys.stdout.buffer, "SERVER -> CLIENT", GREEN, log_file), daemon=True),
    ]
    for t in threads:
        t.start()
    code = server.wait()
    threads[1].join(timeout=1)
    return code


if __name__ == "__main__":
    sys.exit(main())
