# Portfolio v2.1 Verification

Generated after the Phase 0 checkpoint verification run.

## Command Results

| Command | Result |
|---|---|
| `uv run pytest` | Pass: 26 passed |
| `uv run mypy src/cqresearch` | Pass: no issues in 24 source files |
| `uv run python scripts/run_portfolio_v2_1_pipeline.py` | Pass: generated 27 tables, 25 figures, 7 report/diagnostic files, 9 model cards, and `manifest.json` |
| `uv run ruff check scripts/run_portfolio_v2_1_pipeline.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/ablation.py src/cqresearch/features/volatility.py src/cqresearch/analysis/native_factors.py src/cqresearch/analysis/portfolio_v2_1.py tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_volatility.py tests/unit/test_portfolio_v2_1_pipeline.py` | Pass |
| `git status --short -- Data` | Pass: no entries returned |

## Optional Modules

No optional v2.1 modules failed. See `optional_failures.md`.

## Language And Method Checks

- ETF-flow language is reduced-form association / market plumbing; no active
  v2.1 artifact claims ETF flows caused BTC or ETH returns.
- Structural-break language remains Chow plus single-break sup-F, not full
  Bai-Perron.
- Attribution language distinguishes full-vs-reduced block partial R^2 from
  drop-one marginal R^2 and Shapley/Owen.
- Stablecoin supply/growth is framed as a liquidity proxy, not a proven causal
  driver.

## Caveats

The v2.1 pipeline emits two pandas runtime warnings from existing log-return
feature construction on nonpositive values. The warnings do not stop generation
and the resulting packet is complete.
