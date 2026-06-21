# Contributing

Run the maintained verification suite before proposing changes:

```powershell
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run ruff format --check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run pytest -q
uv run python scripts/check_public_surface.py
```

Run `uv run python scripts/run_all.py` only when legally obtained local provider inputs are present under `data_local/raw/`. Do not commit secrets, raw cache payloads, provider exports, or generated local panels.
