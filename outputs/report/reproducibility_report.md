# Reproducibility Report

## Maintained commands

```powershell
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run python scripts/run_all.py
uv run pytest
uv run python scripts/check_public_surface.py
```

## Data contract

The local reproducible build reads provider exports from `data_local/raw/` and writes generated feature stores to `data_local/processed/`. Both locations are ignored by Git. Public-safe semantic tables remain under `outputs/tables/`, and source inventories are written to `data_local/metadata/`.

## Determinism

Public CI validates code, committed derived outputs, and public-surface guardrails without requiring licensed local provider exports. On a machine with `data_local/raw/`, the canonical build is run before semantic-output tests so tests can exercise freshly regenerated artifacts. Determinism checks compare generated semantic outputs while excluding timestamp metadata.
