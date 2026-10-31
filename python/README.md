# openhead (Python)

Client library, simulator, CLI and MCP server for the OpenHead protocol. See the repository [README](../README.md).

```bash
cd python
uv sync            # creates python/.venv with dev tools
uv run pytest
```

`src/openhead/protocol/models.py` and `registry.py` are generated from `protocol/schema` by `tools/protocol.py`; do not edit them by hand.
