# Technical Report

## Data Contract

The project uses a frozen 2020-01-01 to 2026-04-11 daily panel with 2,293 rows
and 63 columns. Inputs combine curated crypto, macro, ETF-flow, stablecoin,
DeFi, sentiment, and on-chain sources. Raw files under `Data/` are not modified
by the canonical export pipeline.

## Feature Engineering

Price-like series are transformed into log returns. Rates, spreads, sentiment,
and native levels use first differences. ETF-flow intensity is daily USD ETF
flow divided by prior-day USD market capitalization. Realized volatility uses a
30-day annualized rolling standard deviation of crypto returns.

## Models And Diagnostics

- HAC OLS for reduced-form factor exposure.
- Full-vs-reduced block partial R2 for block attribution.
- ETF and stablecoin lead-lag regressions with explicit lag convention.
- Rolling cross-asset correlations and pre/post event deltas.
- Stablecoin supply, DeFi TVL, and realized-volatility diagnostics.
- BTC-native factor registry and ablations with MVRV separated.
- Chow tests and single-break sup-F scans for structural-break diagnostics.
- VAR/FEVD connectedness and event-study CAR summaries.
- Advanced diagnostics: PCA blocks, exact block Shapley R2, exploratory CUSUM,
  FEVD-order sensitivity, rolling connectedness, and BTC robustness grid.

## Interpretation

All outputs are reduced-form diagnostics. The project uses language such as
association, exposure, market plumbing, contribution, sensitivity, and regime
diagnostics. It does not claim ETF flows caused BTC or ETH returns.
