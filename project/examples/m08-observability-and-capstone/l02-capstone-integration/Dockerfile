FROM python:3.13-slim

# Build-Kontext ist der Projektordner (output/project); APP_DIR wählt den Server-Stand
ARG APP_DIR=examples/m08-observability-and-capstone/l02-capstone-integration

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    TOOL_CALL_LOG=/data/tool_calls.jsonl

WORKDIR /app

COPY requirements-server.txt .
RUN pip install -r requirements-server.txt

# Nicht-Root-Nutzer; /data ist das einzige beschreibbare Verzeichnis
RUN useradd --system --uid 10001 --no-create-home app \
    && mkdir /data \
    && chown app:app /data

COPY ${APP_DIR}/ /app/
COPY shared/ /app/shared/

USER app
EXPOSE 8000

# Konfiguration (Rolle, Mock-API-URL, Ports) kommt zur Laufzeit per Umgebung; keine Secrets im Image
HEALTHCHECK --interval=15s --timeout=4s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('MCP_PORT', '8000') + '/health', timeout=3)"]

CMD ["python", "server.py"]
