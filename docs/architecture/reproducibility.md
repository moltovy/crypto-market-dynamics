# Reproducibility

## Local Verification

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_all.py
```

Focused Ruff is used for the maintained public and portfolio surfaces. Broad
Ruff over every historical script and test still includes legacy findings; this
is documented as cleanup debt rather than part of the public reproduction
contract.

## Data Policy

The canonical export path does not modify `Data/`. Source inventory copies are
read-only exports into `docs/data/catalog/`.
