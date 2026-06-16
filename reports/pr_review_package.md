# Portfolio v2 PR Review Package

## What Changed

- Added the v2.1 main analytics release with executive, technical, analytics,
  data-atlas, manifest, verification, model-card, table, and figure artifacts.
- Added the v2.2 advanced diagnostics extension with PCA blocks, exact block
  Shapley R2, exploratory CUSUM, FEVD order sensitivity, rolling connectedness,
  and BTC robustness-grid diagnostics.
- Added a GitHub-facing showcase layer with a project walkthrough, figure
  gallery, limitations, and role-oriented technical summaries.
- Added optional free-data scaffolding for DefiLlama, CoinGecko, Binance public
  klines, and FRED without making live data part of core reproduction.
- Added CI/release engineering: focused Ruff, mypy, pytest, portfolio smoke
  workflow, Makefile targets, PR template, release checklist, artifact index,
  public-readiness audit, and PR summary.

## How To Review

Suggested order:

1. `README.md`
2. `reports/artifact_index.md`
3. `reports/portfolio_showcase/README_SHOWCASE.md`
4. `reports/portfolio_showcase/figure_gallery.md`
5. `reports/portfolio_v2_1/executive_summary.md`
6. `reports/portfolio_v2_1/technical_report.md`
7. `reports/portfolio_v2_1/analytics_summary.md`
8. `reports/portfolio_v2_1/model_cards/`
9. `reports/portfolio_v2_2/advanced_methods_summary.md`
10. `reports/final_public_readiness_audit.md`

## How To Reproduce

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_portfolio_v2_1_pipeline.py
uv run python scripts/run_portfolio_v2_2_pipeline.py
```

Focused lint surface:

```powershell
uv run ruff check scripts/run_portfolio_pipeline.py scripts/run_portfolio_v2_1_pipeline.py scripts/run_portfolio_v2_2_pipeline.py scripts/optional_data src/cqresearch/analysis/native_factors.py src/cqresearch/analysis/portfolio_v2_1.py src/cqresearch/analysis/portfolio_v2_2.py src/cqresearch/features/volatility.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/ablation.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/pca_blocks.py src/cqresearch/modeling/shapley_r2.py src/cqresearch/modeling/cusum.py src/cqresearch/modeling/fevd_sensitivity.py src/cqresearch/modeling/rolling_connectedness.py src/cqresearch/modeling/robustness_grid.py src/cqresearch/optional_data tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_volatility.py tests/unit/test_pca_blocks.py tests/unit/test_shapley_r2.py tests/unit/test_cusum.py tests/unit/test_fevd_sensitivity.py tests/unit/test_rolling_connectedness.py tests/unit/test_robustness_grid.py tests/unit/test_portfolio_v2_1_pipeline.py tests/unit/test_portfolio_v2_2_pipeline.py tests/unit/test_optional_data_sources.py
```

## Guardrails

- `Data/` remains untouched.
- Core v2.1/v2.2 reproduction uses frozen committed artifacts and does not
  require paid or live data.
- ETF-flow outputs are reduced-form association, lead-lag, exposure, and
  market-plumbing diagnostics, not causal identification.
- Structural-break diagnostics are Chow plus single-break sup-F, not full
  Bai-Perron.
- v2.1 attribution is drop-one/partial R2, not Shapley/Owen.
- v2.2 exact block Shapley R2 is separately implemented, tested, and labeled as
  predictive attribution.
- Optional data remains a separate extension layer.

## Known Caveats

- Broad Ruff over `src/cqresearch scripts tests` still reports legacy findings
  outside the maintained portfolio surface; focused Ruff passes.
- v2.1/v2.2 pipeline runs emit known pandas warnings from frozen transforms
  with non-positive inputs.
- v2.2 VAR/FEVD windows emit statsmodels frequency warnings while still
  generating the expected outputs.
- Daily data limits intraday sequencing and liquidity-mechanism claims.
- Frozen data is reproducible but intentionally not live-refreshed.
- All interpretations remain reduced-form unless explicitly labeled otherwise.
