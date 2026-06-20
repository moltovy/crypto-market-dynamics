# Final Release Audit

## Verdict

Pass, pending reviewer approval and merge.

## Scope completed

- Maintained canonical build path: `scripts/run_all.py`.
- Semantic table and report surface under `outputs/`.
- Public figure surface limited to nine canonical figures under `outputs/figures/public/`.
- MVRV same-day features removed from primary BTC/ETH exposure models.
- ETF flows framed as market-plumbing associations, not causal return drivers.
- Monthly PIT market-structure data used for composition, concentration, and turnover only.
- Current-top50 daily cohort marked exploratory and survivorship-biased.
- Selected-major assets use canonical IDs and explicit coverage caveats.

## Required local gates

- `uv sync --all-extras`
- `uv run ruff check src/cqresearch scripts tests`
- `uv run mypy src/cqresearch`
- `uv run pytest`
- `uv run python scripts/run_all.py`
- `uv run python scripts/check_public_surface.py`

## Known non-goals

- No live or paid data dependency is required for the canonical build.
- No price forecasting, trading strategy, or causal ETF-flow identification is claimed.
- Historical daily point-in-time altseason performance remains deferred until constituent-level daily OHLCV and market-cap history exists.
