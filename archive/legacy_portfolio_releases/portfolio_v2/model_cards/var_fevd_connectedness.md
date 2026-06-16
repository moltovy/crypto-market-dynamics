# Model Card - VAR/FEVD Connectedness

## Purpose

Summarize dynamic connectedness between BTC, ETH, equities, volatility, and
liquidity proxies.

## Inputs

Stationary feature columns selected by `scripts/02_run_analyses.py`.

## Method

statsmodels VAR with BIC lag selection and 10-day FEVD.

## Outputs

`fevd_10d_compact.csv`, `fevd_10d.csv`, and FEVD heatmaps.

## Interpretation

Connectedness diagnostics under the declared variable ordering.

## Risks

Ordering sensitivity, non-structural shocks, and unstable small systems.

## Upgrade Path

Add generalized FEVD or ordering-sensitivity tables before making stronger
connectedness claims.
