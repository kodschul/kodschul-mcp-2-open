# SYNTHETISCHE TRAINER-KONFIGURATION MIT ABSICHTLICHEN FEHLERN (Lab 7.3), nicht verwenden.
# Befunde stehen in ../findings-beispiel.md. Der Schlüssel unten ist ein erfundener Platzhalter.
FROM python:latest

ENV LLM_API_KEY=sk-demo-0000-not-a-real-key
ENV VANTRA_ROLE=operator

RUN apt-get update && apt-get install -y curl openssh-server

WORKDIR /app
COPY . .
RUN pip install mcp httpx openai

RUN chmod -R 777 /app

EXPOSE 8000 22

CMD ["python", "server.py"]
