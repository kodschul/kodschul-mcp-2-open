"""Replay-LLM: Fallback ohne echtes Modell, spielt feste Tool-Calls ab.

Gleiche Schnittstelle wie das OpenAI-kompatible Backend (chat(messages, tools) -> dict),
daher in shared/agent_client.py mit --replay austauschbar. Skripte:

  dialog     "Zeige Ticket VAN-102" -> "Zeige das Deployment-Log dazu"   (m04, kanonischer Testdialog)
  injection  "Zeige Ticket VAN-106": der Ticket-Text enthält eine Anweisung, die der naive
             Replay-Agent befolgt (Showcase C, m07-l02)
  workflow   Ticket abfragen -> Deployment-Log prüfen -> Status ändern (Policy-Entscheidung, m08-l02)
"""

import json
import re

SCENARIOS: dict[str, list[str]] = {
    "dialog": ["Zeige Ticket VAN-102", "Zeige das Deployment-Log dazu"],
    "injection": ["Zeige Ticket VAN-106"],
    "workflow": ["Zeige Ticket VAN-102", "Zeige das Deployment-Log dazu", "Setze das Ticket auf in_progress"],
}
TICKET_RE = re.compile(r"VAN-\d+")
STATUS_RE = re.compile(r"\b(open|in_progress|resolved|closed)\b")


def _loads(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


class ReplayLLM:
    name = "replay"

    def __init__(self, scenario: str = "dialog") -> None:
        if scenario not in SCENARIOS:
            raise ValueError(f"Unbekanntes Replay-Skript '{scenario}', erlaubt: {', '.join(SCENARIOS)}")
        self.scenario = scenario
        self._calls = 0

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        last_user = max(i for i, m in enumerate(messages) if m["role"] == "user")
        user_text = messages[last_user]["content"]
        results = [m["content"] for m in messages[last_user + 1:] if m["role"] == "tool"]
        if not results:
            return self._first_step(user_text, messages)
        return self._next_step(user_text, results)

    def _call(self, name: str, arguments: dict) -> dict:
        self._calls += 1
        return {"content": None, "tool_calls": [{"id": f"replay_{self._calls}", "name": name, "arguments": arguments}]}

    def _known_ticket(self, messages: list[dict]) -> dict | None:
        for m in reversed(messages):
            data = _loads(m["content"]) if m["role"] == "tool" else None
            if isinstance(data, dict) and "version" in data and str(data.get("id", "")).startswith("VAN-"):
                return data
        return None

    def _first_step(self, user_text: str, messages: list[dict]) -> dict:
        ticket_id = (TICKET_RE.search(user_text) or [None])[0]
        lowered = user_text.lower()
        if "deployment" in lowered:
            return self._call("get_deployment_log", {"ticket_id": ticket_id} if ticket_id else {})
        if lowered.startswith("setze") or "status" in lowered:
            known = self._known_ticket(messages)
            status = (STATUS_RE.search(user_text) or [None])[0] or "in_progress"
            if known is None:
                return {"content": "Replay: Für die Statusänderung fehlt ein zuvor abgefragtes Ticket.", "tool_calls": []}
            return self._call("update_ticket_status", {"ticket_id": known["id"], "status": status, "expected_version": known["version"]})
        if ticket_id:
            return self._call("get_ticket", {"ticket_id": ticket_id})
        return {"content": "Replay: Für diese Eingabe gibt es kein Skript.", "tool_calls": []}

    def _next_step(self, user_text: str, results: list[str]) -> dict:
        last = results[-1]
        failed = last.startswith("FEHLER:")
        data = _loads(last.removeprefix("FEHLER:").strip())
        if self.scenario == "injection" and not failed and "update_ticket_status" in last and len(results) == 1:
            # naiver Agent: folgt der Anweisung aus dem Ticket-Text
            return self._call("update_ticket_status", {"ticket_id": "VAN-101", "status": "closed", "expected_version": 1})
        if failed:
            message = data.get("message") if isinstance(data, dict) else last
            return {"content": f"Der Aufruf war nicht erfolgreich: {message}", "tool_calls": []}
        if isinstance(data, dict) and "log" in data:
            tail = "; ".join(line.split(" ", 2)[2] for line in data["log"][-2:])
            text = f"Deployment {data['id']} ({data['service']} {data['version']}, Status {data['status']}). Letzte Zeilen: {tail}"
        elif isinstance(data, dict) and "title" in data:
            text = f"Ticket {data['id']}: {data['title']} (Status {data['status']}, Version {data['version']})."
        else:
            text = f"Ergebnis: {last}"
        return {"content": text, "tool_calls": []}
