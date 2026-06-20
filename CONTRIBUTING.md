# Contributing

Run the maintained verification suite before proposing changes:

```powershell
uv sync --all-extras
uv run python scripts/run_all.py
uv run python scripts/check_public_surface.py
uv run pytest
uv run mypy src/cqresearch
uv run ruff check src/cqresearch scripts tests
```

Do not commit secrets, raw cache payloads, or newly licensed raw data without explicit redistribution permission.
