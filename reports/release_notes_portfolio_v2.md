# Crypto Market Factor Lab Portfolio v2.2

## Overview

This release candidate turns the research repository into a reproducible
GitHub-ready crypto factor analytics lab. It preserves the frozen data backbone
while adding polished v2.1 and v2.2 release packets, model cards, manifests,
figures, verification diagnostics, optional-data scaffolding, and CI/release
engineering.

## Main Release: Portfolio v2.1

Portfolio v2.1 is the primary public release. It includes block partial R2,
BTC/ETH nested ablations, ETF-flow lead-lag diagnostics, rolling cross-asset
correlations, stablecoin liquidity proxy diagnostics, BTC-native factor
analysis, model cards, reports, tables, and figures under
`reports/portfolio_v2_1/`.

## Advanced Extension: Portfolio v2.2

Portfolio v2.2 is an advanced diagnostics extension, not a replacement for
v2.1. It adds PCA block factors, exact block Shapley R2, exploratory CUSUM,
FEVD-order sensitivity, rolling VAR/FEVD connectedness, and a BTC robustness
grid under `reports/portfolio_v2_2/`.

## Data Policy

- Core reproduction uses the frozen committed panel and existing curated data.
- No raw files under `Data/` are modified by portfolio pipelines.
- No paid data or live API calls are required for v2.1 or v2.2.
- Optional free-data scaffolding remains separate from the core release.

## Reproducibility

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_portfolio_v2_1_pipeline.py
uv run python scripts/run_portfolio_v2_2_pipeline.py
```

## Major Analytics

- Block partial R2 and nested ablations for BTC/ETH factor families.
- ETF-flow lead-lag and flow-quintile diagnostics with explicit lag convention.
- Rolling BTC/ETH cross-asset correlation dashboards and event markers.
- Stablecoin supply, TVL, and realized-volatility proxy diagnostics.
- BTC-native valuation and flow-state registry, correlations, and ablations.
- PCA, exact Shapley R2, CUSUM, FEVD sensitivity, rolling connectedness, and
  robustness-grid diagnostics in v2.2.

## Guardrails

- ETF-flow outputs are not causal claims.
- Stablecoin outputs are liquidity proxies, not proven funding shocks.
- Structural breaks are Chow and single-break sup-F diagnostics, not full
  Bai-Perron.
- v2.1 attribution is not Shapley/Owen.
- v2.2 exact block Shapley R2 is predictive attribution over chosen blocks.

## Known Limitations

- Daily data cannot identify intraday mechanism ordering.
- Frozen data gives reproducibility but is not a live market monitor.
- Broad Ruff still reports legacy findings outside the maintained portfolio
  surface; focused CI linting targets the maintained release paths.
- v2.1/v2.2 pipelines emit known pandas and statsmodels warnings while
  completing successfully.

## Verification

- `uv run pytest` -> PASS, 43 passed
- `uv run mypy src/cqresearch` -> PASS
- focused Ruff on maintained portfolio/optional-data paths -> PASS
- `uv run python scripts/run_portfolio_v2_1_pipeline.py` -> PASS
- `uv run python scripts/run_portfolio_v2_2_pipeline.py` -> PASS
- `uv run pytest tests/unit/test_optional_data_sources.py` -> PASS, 6 passed
- `git status --short -- Data` -> PASS, no output

## Suggested Tag

Suggested tag after merge:

```powershell
git tag -a portfolio-v2.2 -m "Crypto Market Factor Lab portfolio v2.2"
git push origin portfolio-v2.2
```

Do not push the tag before the branch is reviewed and merged.
