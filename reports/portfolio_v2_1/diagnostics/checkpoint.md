# Portfolio v2.1 Checkpoint

**Date:** 2026-06-16  
**Branch:** `portfolio_v2`  
**Starting HEAD:** `0236b1e`

## Git Status Summary

The checkpoint started from a dirty worktree containing the completed v2 and
v2.1 portfolio work. `Instructions.md` is an untracked local prompt file and is
intentionally excluded from commits.

`git status --short -- Data` returned no entries, confirming raw data remained
untouched before checkpointing.

## Commands Run

| Command | Result |
|---|---|
| `git status --short` | Completed; v2/v2.1 dirty worktree identified |
| `git status --short -- Data` | Pass: no entries |
| `git diff --stat` | Completed |
| `git diff --name-only` | Completed |
| `uv run pytest` | Pass: 26 passed |
| `uv run mypy src/cqresearch` | Pass: no issues in 24 source files |
| `uv run ruff check scripts/run_portfolio_v2_1_pipeline.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/ablation.py src/cqresearch/features/volatility.py src/cqresearch/analysis/native_factors.py src/cqresearch/analysis/portfolio_v2_1.py tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_volatility.py tests/unit/test_portfolio_v2_1_pipeline.py` | Pass |
| `uv run python scripts/run_portfolio_v2_1_pipeline.py` | Pass: regenerated v2.1 packet |

## Notes

- The v2.1 pipeline emitted two known pandas runtime warnings from existing
  log-return construction on nonpositive values. The packet still generated
  completely.
- No paid data, live data, or raw `Data/` edits were introduced.
- ETF-flow, stablecoin, and native-factor interpretation remains reduced-form.

## Commits Created

To be filled after checkpoint commits are created.
