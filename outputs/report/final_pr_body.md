## Summary

- Replace the old portfolio/v2 public surface with the canonical Crypto Market Dynamics offline build.
- Add semantic feature stores, tables, reports, model cards, docs, data governance, and exactly nine public figures.
- Reframe MVRV, ETF flows, leverage/liquidations, stablecoin/DeFi liquidity, PIT market structure, and selected major assets according to the final evidence standards.

## Verification

- `uv sync --all-extras`
- `uv run ruff check src/cqresearch scripts tests`
- `uv run mypy src/cqresearch`
- `uv run pytest`
- `uv run python scripts/run_all.py`
- `uv run python scripts/check_public_surface.py`

## Guardrails

- No instruction-bundle files are included.
- Raw data changes are limited to generated `Data/MASTER_DATA.*` inventory files.
- Public README embeds exactly nine canonical figures.
- ETF-flow, liquidation, data-licensing, and current-top50 cohort claims remain caveated.
