# Model Card - ETF Flow Lead-Lag

## Purpose

Test whether ETF-flow intensity associations are contemporaneous or lagged.

## Inputs

BTC/ETH ETF intensity, returns, realized volatility, and controls.

## Sample

Post-launch windows for each asset.

## Method

HAC OLS grid by lag. Lag convention: lag < 0 means x is shifted earlier and leads the target; lag -1 uses x[t-1] to explain y[t].

## Output files

`etf_lead_lag_btc.csv`, `etf_lead_lag_eth.csv`, quintile/top-day tables.

## Interpretation

Market-plumbing association only; same-day evidence is not causality.

## Risks / limitations

Simultaneity, omitted news, and daily aggregation.

## Upgrade path

Use intraday data or external instruments for stronger timing evidence.
