"""Infrastruktur: Mock-API, Streamable HTTP, Trace-Proxy, Docker-/Kubernetes-/Pipeline-Dateien, Starter und Konsistenz."""

import filecmp
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest
import yaml
from mcp import Client

from conftest import EX, PROJECT, SRV_CONTAINER, SRV_SECURE, connect

CHECK = PROJECT / "checkpoints"
SECRET_PATTERN = re.compile(r"(sk-[A-Za-z0-9-]{8,}|password\s*=|api[_-]?key\s*=\s*[A-Za-z0-9_-]{12,})", re.IGNORECASE)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


# --- Mock-API -------------------------------------------------------------------------------

def test_mock_api_endpoints(mock_api):
    assert _http("GET", mock_api + "/health") == (200, {"status": "ok"})
    status, tickets = _http("GET", mock_api + "/tickets")
    assert status == 200 and {t["id"] for t in tickets} >= {"VAN-101", "VAN-102", "VAN-106"}
    assert all("version" in t for t in tickets)
    assert _http("GET", mock_api + "/tickets/VAN-102")[1]["version"] == 3
    assert _http("GET", mock_api + "/tickets/VAN-999")[0] == 404
    status, dep = _http("GET", mock_api + "/tickets/VAN-102/deployment")
    assert status == 200 and dep["id"] == "dep-2041" and dep["log"]
    assert _http("GET", mock_api + "/tickets/VAN-105/deployment")[0] == 404


def test_mock_api_version_conflict_and_validation(mock_api):
    url = mock_api + "/tickets/VAN-102"
    assert _http("PATCH", url, {"status": "resolved", "expected_version": 1}) == (409, {"error": "version_conflict", "expected_version": 1, "current_version": 3})
    assert _http("PATCH", url, {"status": "kaputt"})[0] == 422
    status, ticket = _http("PATCH", url, {"status": "in_progress", "expected_version": 3})
    assert status == 200 and ticket["version"] == 4
    assert _http("POST", mock_api + "/reset", {})[0] == 200
    assert _http("GET", url)[1]["version"] == 3


def test_in_process_and_http_backend_behave_the_same(mock_api, monkeypatch):
    from shared.mock_api.client import HttpBackend
    from shared.mock_api.store import Store, VersionConflict

    for backend in (Store(), HttpBackend(mock_api)):
        assert backend.get_ticket("VAN-102")["version"] == 3
        with pytest.raises(VersionConflict) as exc:
            backend.update_ticket("VAN-102", "resolved", 2)
        assert (exc.value.expected, exc.value.current) == (2, 3)
        assert backend.update_ticket("VAN-102", "resolved", 3)["version"] == 4
        assert backend.latest_deployment("VAN-102")["id"] == "dep-2041"
        _http("POST", mock_api + "/reset", {})


# --- Streamable HTTP ------------------------------------------------------------------------

def _start_http_server(script, port, **env):
    full = {**os.environ, "MCP_TRANSPORT": "streamable-http", "MCP_HOST": "127.0.0.1", "MCP_PORT": str(port), **env}
    proc = subprocess.Popen([sys.executable, str(script)], env=full, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
            return proc
        except OSError:
            time.sleep(0.25)
    proc.kill()
    raise RuntimeError("HTTP-Server startet nicht")


async def test_streamable_http_container_server_with_mock_api(mock_api):
    port = _free_port()
    proc = _start_http_server(SRV_CONTAINER, port, MOCK_API_URL=mock_api)
    try:
        async with Client(f"http://127.0.0.1:{port}/mcp") as client:
            assert client.protocol_version == "2026-07-28"
            assert {t.name for t in (await client.list_tools()).tools} == {"get_ticket", "get_deployment_log", "update_ticket_status"}
            result = await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
            assert json.loads(result.content[0].text)["id"] == "VAN-102"
            conflict = await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved", "expected_version": 1})
            assert conflict.structured_content["current_version"] == 3
    finally:
        proc.kill()


async def test_streamable_http_enforces_role_from_server_environment():
    port = _free_port()
    proc = _start_http_server(SRV_SECURE, port, VANTRA_ROLE="viewer")
    try:
        async with Client(f"http://127.0.0.1:{port}/mcp") as client:
            result = await client.call_tool("update_ticket_status", {"ticket_id": "VAN-101", "status": "closed", "expected_version": 1, "confirmed": True})
            assert result.structured_content["error"] == "policy_denied"
    finally:
        proc.kill()


# --- Trace-Proxy ----------------------------------------------------------------------------

async def test_trace_proxy_logs_both_directions(tmp_path):
    from mcp.client.stdio import StdioServerParameters

    trace = tmp_path / "trace.log"
    params = StdioServerParameters(command=sys.executable, args=[str(PROJECT / "shared/trace_proxy.py"), "--log", str(trace), "--", sys.executable, str(SRV_CONTAINER)])
    async with Client(params) as client:
        await client.call_tool("get_ticket", {"ticket_id": "VAN-102"})
    lines = trace.read_text(encoding="utf-8").splitlines()
    assert any("CLIENT -> SERVER" in l and '"method":"tools/call"' in l for l in lines)
    assert any("SERVER -> CLIENT" in l and '"isError":false' in l for l in lines)


def test_agent_client_trace_option(tmp_path):
    trace = tmp_path / "t.log"
    done = _run_py(PROJECT / "shared/agent_client.py", "--server", str(SRV_CONTAINER), "--replay", "--prompt", "Zeige Ticket VAN-102", "--trace", str(trace))
    assert done.returncode == 0, done.stderr
    assert "Tool-Call: get_ticket" in done.stdout and '"method":"tools/call"' in trace.read_text(encoding="utf-8")


# --- Docker, Compose, Kubernetes, Pipeline --------------------------------------------------

DOCKERFILE = EX / "m05-cloud-integration/l02-container-prep/Dockerfile"


def test_dockerfile_hardening():
    text = DOCKERFILE.read_text(encoding="utf-8")
    assert re.search(r"^FROM python:3\.\d+-slim$", text, re.M) and ":latest" not in text
    assert re.search(r"^USER app$", text, re.M) and "useradd" in text
    assert "HEALTHCHECK" in text and "/health" in text
    assert "COPY . ." not in text and "pip install -r requirements-server.txt" in text
    assert not SECRET_PATTERN.search(text), "Secret im Dockerfile"
    assert text.index("USER app") > text.index("COPY shared/")


def test_server_requirements_are_pinned():
    for name in ("requirements-server.txt", "requirements.txt"):
        for line in (PROJECT / name).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith(("#", "-r")):
                assert "==" in line, f"{name}: {line} nicht gepinnt"
    assert "mcp==2.3.0" in (PROJECT / "requirements-server.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("compose", [
    EX / "m06-containerization-cicd/l01-docker/docker-compose.yml",
    EX / "m08-observability-and-capstone/l02-capstone/docker-compose.yml",
    CHECK / "ende-m07-abgesichert/docker-compose.yml",
])
def test_compose_structure(compose):
    doc = yaml.safe_load(compose.read_text(encoding="utf-8"))
    assert set(doc["services"]) == {"mcp-server", "mock-api", "dashboard"}
    server = doc["services"]["mcp-server"]
    assert server["environment"]["MCP_TRANSPORT"] == "streamable-http"
    assert server["environment"]["MOCK_API_URL"] == "http://mock-api:8001"
    assert server["depends_on"]["mock-api"]["condition"] == "service_healthy"
    assert "8000" in server["ports"][0] and "8001" in doc["services"]["mock-api"]["ports"][0] and "8080" in doc["services"]["dashboard"]["ports"][0]
    assert doc["services"]["dashboard"]["volumes"][0].endswith(":/data:ro")
    context = (compose.parent / doc["x-build"]["context"]).resolve()
    assert context == PROJECT
    assert (context / doc["x-build"]["dockerfile"]).is_file()
    assert not SECRET_PATTERN.search(compose.read_text(encoding="utf-8"))


def test_k8s_manifest_structure():
    docs = [d for d in yaml.safe_load_all((EX / "m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml").read_text(encoding="utf-8")) if d]
    res = {(d["kind"], d["metadata"]["name"]): d for d in docs}
    assert set(res) == {
        ("ConfigMap", "vantra-ops-config"),
        ("Deployment", "vantra-ops-mcp"), ("Service", "vantra-ops-mcp"),
        ("Deployment", "vantra-mock-api"), ("Service", "vantra-mock-api"),
    }
    cm = res[("ConfigMap", "vantra-ops-config")]
    dep = res[("Deployment", "vantra-ops-mcp")]
    svc = res[("Service", "vantra-ops-mcp")]
    pod = dep["spec"]["template"]["spec"]
    container = pod["containers"][0]
    assert pod["securityContext"]["runAsNonRoot"] is True
    assert container["securityContext"]["readOnlyRootFilesystem"] is True and container["securityContext"]["allowPrivilegeEscalation"] is False
    for probe in ("readinessProbe", "livenessProbe", "startupProbe"):
        assert container[probe]["httpGet"]["path"] == "/health"
    assert container["envFrom"][0]["configMapRef"]["name"] == cm["metadata"]["name"]
    assert container["env"][0]["valueFrom"]["secretKeyRef"]["name"] == "vantra-ops-secrets"
    assert ":latest" not in container["image"] and {"requests", "limits"} <= set(container["resources"])
    assert svc["spec"]["selector"] == dep["spec"]["selector"]["matchLabels"]
    # MOCK_API_URL muss auf einen Service im selben Manifest zeigen
    mock_dep = res[("Deployment", "vantra-mock-api")]
    mock_svc = res[("Service", "vantra-mock-api")]
    assert cm["data"]["MOCK_API_URL"] == f"http://{mock_svc['metadata']['name']}:{mock_svc['spec']['ports'][0]['port']}"
    assert mock_svc["spec"]["selector"] == mock_dep["spec"]["selector"]["matchLabels"]
    assert mock_dep["spec"]["template"]["spec"]["containers"][0]["command"] == ["python", "shared/mock_api/app.py"]
    assert "kind: Secret" not in (EX / "m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml").read_text(encoding="utf-8")


def test_pipeline_has_required_stages():
    doc = yaml.safe_load((EX / "m06-containerization-cicd/l02-kubernetes-cicd/pipeline.yml").read_text(encoding="utf-8"))
    jobs = doc["jobs"]
    assert list(jobs) == ["build", "test", "scan", "deploy", "rollback"]
    assert {"build", "scan"} <= set(jobs["deploy"]["needs"]) and jobs["rollback"]["if"] == "failure()"
    assert "rollout undo" in json.dumps(jobs["rollback"])


# --- Trainer-Konfiguration mit Fehlern (7.3) ------------------------------------------------

def test_flawed_dockerfile_contains_planted_findings():
    text = (EX / "m07-security-hardening/l03-security-review/flawed/Dockerfile").read_text(encoding="utf-8")
    findings = [
        ":latest" in text,
        "USER" not in text,
        "LLM_API_KEY=" in text,
        "COPY . ." in text,
        "pip install mcp httpx openai" in text,
        "HEALTHCHECK" not in text,
        "chmod -R 777" in text,
        "EXPOSE 8000 22" in text,
        "VANTRA_ROLE=operator" in text,
    ]
    assert sum(findings) >= 6 and all(findings)


def test_flawed_policy_findings_and_findings_file_cover_them():
    base = EX / "m07-security-hardening/l03-security-review"
    policy = (base / "flawed/policy.md").read_text(encoding="utf-8")
    assert "Tool-Argument `role`" in policy and "gilt: erlaubt" in policy and "keine Bestätigung" not in policy
    findings = (base / "findings-beispiel.md").read_text(encoding="utf-8")
    rows = [l for l in findings.splitlines() if re.match(r"\| \d+ \|", l)]
    assert len(rows) >= 12
    assert sum("blockierend" in r for r in rows) >= 5 and sum("nice to have" in r for r in rows) >= 2
    assert (base / "checklist.md").read_text(encoding="utf-8").count("| A") >= 8


# --- Starter: laufen bis zur Lücke oder scheitern klar ---------------------------------------

def _run_py(path, *args, **env):
    return subprocess.run([sys.executable, str(path), *args], capture_output=True, text=True, timeout=60, cwd=PROJECT, env={**os.environ, **env})


def test_starter_m01_stops_with_todo_message():
    done = _run_py(PROJECT / "starters/m01-l02-first-server.py")
    assert done.returncode != 0 and "TODO(Aufgabe 3)" in done.stderr


async def test_starter_m02_first_tool_has_no_tool_yet():
    async with connect(PROJECT / "starters/m02-l02-first-tool.py") as client:
        assert (await client.list_tools()).tools == []


async def test_starter_m03_conflict_overwrites_silently():
    async with connect(PROJECT / "starters/m03-l03-conflict.py", PYTHONPATH=str(EX / "m03-context-and-state/l03-multi-agent")) as client:
        tool = next(t for t in (await client.list_tools()).tools if t.name == "update_ticket_status")
        assert "expected_version" not in tool.input_schema["properties"]
        result = await client.call_tool("update_ticket_status", {"ticket_id": "VAN-102", "status": "resolved"})
        assert not result.is_error  # Lücke: kein Konflikt trotz geänderter Version


def test_starter_m03_context_fails_at_first_gap():
    done = _run_py(PROJECT / "starters/m03-l02-context.py")
    assert done.returncode != 0 and "TODO(Aufgabe 3)" in done.stderr


def test_starter_m04_agent_fails_at_first_gap():
    target = EX / "m04-agent-prototype/l01-agent-client"
    done = subprocess.run([sys.executable, "-c", f"import runpy,sys; sys.argv=['x','--replay']; runpy.run_path(r'{PROJECT / 'starters/m04-l01-agent-client.py'}', run_name='__main__')"],
                          capture_output=True, text=True, timeout=60, cwd=target)
    assert done.returncode != 0 and ("TODO(Aufgabe" in done.stderr or "NoneType" in done.stderr or "Client" in done.stderr)


def test_starters_exist_per_agenda_table():
    names = [
        "m01-l02-first-server.py", "m02-l01-raw-requests.py", "m02-l02-first-tool.py", "m03-l02-context.py", "m03-l03-conflict.py",
        "m04-l01-agent-client.py", "m04-l02-testrun.md", "m05-l02-Dockerfile", "m06-l01-compose.yml", "m06-l02-k8s.yaml",
        "m07-l01-policy.md", "m07-l03-checklist.md", "m08-l01-logging.py", "m08-l02-capstone.md",
    ]
    for name in names:
        text = (PROJECT / "starters" / name).read_text(encoding="utf-8")
        assert "TODO(Aufgabe" in text, name


def test_starter_yaml_files_parse():
    yaml.safe_load((PROJECT / "starters/m06-l01-compose.yml").read_text(encoding="utf-8"))
    list(yaml.safe_load_all((PROJECT / "starters/m06-l02-k8s.yaml").read_text(encoding="utf-8")))
    yaml.safe_load((PROJECT / "starters/m06-l02-pipeline.yml").read_text(encoding="utf-8"))


# --- Konsistenz der kumulativen Stände -------------------------------------------------------

@pytest.mark.parametrize("a,b", [
    (EX / "m03-context-and-state/l02-context-schema/context.py", EX / "m03-context-and-state/l03-multi-agent/context.py"),
    (EX / "m03-context-and-state/l03-multi-agent/server.py", EX / "m04-agent-prototype/l01-agent-client/server.py"),
    (EX / "m04-agent-prototype/l01-agent-client/server.py", CHECK / "ende-tag1-prototyp/server.py"),
    (EX / "m04-agent-prototype/l01-agent-client/agent.py", CHECK / "ende-tag1-prototyp/agent.py"),
    (EX / "m07-security-hardening/l01-access-control/server.py", CHECK / "ende-m07-abgesichert/server.py"),
    (EX / "m07-security-hardening/l01-access-control/auth.py", CHECK / "ende-m07-abgesichert/auth.py"),
    (EX / "m08-observability-and-capstone/l01-monitoring/server.py", EX / "m08-observability-and-capstone/l02-capstone/server.py"),
    (EX / "m08-observability-and-capstone/l01-monitoring/logging_config.py", EX / "m08-observability-and-capstone/l02-capstone/logging_config.py"),
    (EX / "m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml", EX / "m08-observability-and-capstone/l02-capstone/k8s.yaml"),
])
def test_cumulative_states_are_identical(a, b):
    assert filecmp.cmp(a, b, shallow=False), f"{a.name} weicht von {b} ab"


def test_agenda_example_files_exist():
    expected = [
        "m01-mcp-foundations-and-setup/l02-dev-setup/server.py",
        "m02-protocol-and-messages/l01-jsonrpc/raw_requests.py",
        "m02-protocol-and-messages/l02-first-tool/raw_requests.py",
        "m02-protocol-and-messages/l02-first-tool/server.py",
        "m03-context-and-state/l02-context-schema/server.py",
        "m03-context-and-state/l02-context-schema/context.py",
        "m03-context-and-state/l03-multi-agent/server.py",
        "m04-agent-prototype/l01-agent-client/agent.py",
        "m04-agent-prototype/l02-testrun/testdialog.md",
        "m04-agent-prototype/l02-testrun/testlauf.log",
        "m05-cloud-integration/l02-container-prep/Dockerfile",
        "m06-containerization-cicd/l01-docker/docker-compose.yml",
        "m06-containerization-cicd/l02-kubernetes-cicd/k8s.yaml",
        "m06-containerization-cicd/l02-kubernetes-cicd/pipeline.yml",
        "m07-security-hardening/l01-access-control/policy.md",
        "m07-security-hardening/l01-access-control/auth.py",
        "m07-security-hardening/l03-security-review/checklist.md",
        "m07-security-hardening/l03-security-review/findings-beispiel.md",
        "m08-observability-and-capstone/l01-monitoring/logging_config.py",
        "m08-observability-and-capstone/l02-capstone/server.py",
    ]
    missing = [p for p in expected if not (EX / p).is_file()]
    assert not missing, missing


def test_no_secrets_in_repo_files():
    for path in PROJECT.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".yml", ".yaml", ".md", ".json", ".txt", ".example"} and "flawed" not in path.parts and "tests" not in path.parts and ".venv" not in path.parts:
            assert not SECRET_PATTERN.search(path.read_text(encoding="utf-8")), path


def test_script_client_lists_tools_and_calls_tool():
    server = EX / "m03-context-and-state/l03-multi-agent/server.py"
    done = _run_py(PROJECT / "shared/script_client.py", "--server", str(server), "--call", "get_ticket", '{"ticket_id": "VAN-102"}')
    assert done.returncode == 0 and "Tools: get_ticket, get_deployment_log, update_ticket_status" in done.stdout
    failed = _run_py(PROJECT / "shared/script_client.py", "--server", str(server), "--call", "update_ticket_status", '{"ticket_id":"VAN-102","status":"open","expected_version":1}')
    assert failed.returncode == 1 and "version_conflict" in failed.stdout
