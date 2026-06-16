# Model Card - Rolling Correlations

## Purpose

Describe BTC/ETH co-movement regimes with TradFi and liquidity proxies.

## Inputs

Stationary return/difference features from the frozen panel.

## Sample

Full available sample using 60/180/365-day rolling windows.

## Method

Rolling pairwise correlations plus pre/post ETF correlation deltas.

## Output files

`rolling_correlations.csv`, `correlation_delta_pre_post_*_etf.csv`.

## Interpretation

Descriptive integration/regime diagnostics.

## Risks / limitations

Correlation is not causation and can move with volatility regimes.

## Upgrade path

Add bootstrap confidence intervals or regime-clustering checks.
