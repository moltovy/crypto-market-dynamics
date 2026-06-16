# Crypto Market Factor Lab Showcase

## What This Project Is

Crypto Market Factor Lab is a reproducible Python research system for BTC/ETH
factor regimes, ETF-flow market plumbing, stablecoin liquidity, cross-asset
connectedness, and BTC-native market structure.

## Why It Matters

The project shows how to turn a messy multi-source crypto data problem into a
reviewable analytics product: frozen panel, transparent feature engineering,
model cards, figures, manifests, and reduced-form interpretation.

## Data Scale

- Frozen panel: 2020-01-01 through 2026-04-11
- Daily rows: 2,293
- Panel columns: 63
- Source inventory: CryptoQuant, Artemis, TradingView, DefiLlama, FRED,
  Farside ETF Data, and AlternativeMe

## Core Modules

| Module | What it demonstrates |
|---|---|
| Portfolio v2 | Stable baseline packet |
| Portfolio v2.1 | Enhanced analytics release |
| Data atlas | Curation, coverage, reproducibility |
| Model cards | Honest method disclosure |
| ETF lead-lag | Market-plumbing diagnostics |
| BTC-native lab | Native valuation/flow-state separation |

## Hero Visuals

- [BTC block partial R2](../portfolio_v2_1/figures/F10_btc_block_partial_r2_heatmap.png)
- [BTC ETF lead-lag](../portfolio_v2_1/figures/F22_btc_etf_lead_lag_heatmap.png)
- [BTC rolling correlations](../portfolio_v2_1/figures/F30_btc_rolling_correlations_180d.png)
- [Stablecoin supply and TVL](../portfolio_v2_1/figures/F40_stablecoin_supply_and_tvl.png)
- [BTC native z-score dashboard](../portfolio_v2_1/figures/F50_btc_native_zscore_dashboard.png)

## Key Reduced-Form Findings

- BTC fit is heavily influenced by MVRV-like valuation-state variables.
- ETH is better treated as a comparison asset than forced into BTC symmetry.
- ETF-flow intensity has strong contemporaneous association, but this is not
  causal identification.
- Stablecoin supply and TVL are useful liquidity context, not proven funding
  shocks.

## Reproducibility

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_portfolio_v2_1_pipeline.py
```

## Reviewer Discussion Points

- How the frozen panel prevents reproducibility drift.
- Why ETF-flow intensity is scaled by prior-day market cap.
- Why full-vs-reduced block partial R2 is useful but not Shapley/Owen.
- Why MVRV is separated from non-MVRV native factors.
- What intraday ETF/price data would add.

## Links To Artifacts

- [Executive summary](../portfolio_v2_1/executive_summary.md)
- [Technical report](../portfolio_v2_1/technical_report.md)
- [Analytics summary](../portfolio_v2_1/analytics_summary.md)
- [Data atlas](../portfolio_v2_1/data_atlas.md)
- [Figure gallery](figure_gallery.md)
