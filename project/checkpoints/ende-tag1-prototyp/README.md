# Checkpoint: Ende Tag 1 (Prototyp)

Stand nach Lab 4.1: Server mit den Tools `get_ticket`, `get_deployment_log`, `update_ticket_status` (Versionsprüfung), Kontextschema (`context.py`) und angebundenem Agent-Client (`agent.py`). Entspricht `examples/m04-agent-prototype/l01-agent-client-connection/`.

Wiedereinstieg in Tag 2:

```bash
cp checkpoints/ende-tag1-prototyp/server.py checkpoints/ende-tag1-prototyp/context.py playground/
python shared/agent_client.py --server playground/server.py --replay
```

Der Stand läuft nur über stdio und ist nicht containerisiert oder abgesichert; das folgt in m05 bis m07.
