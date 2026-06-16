# Executive Summary

Crypto Market Factor Lab is a reproducible Python analytics system for BTC/ETH
factor regimes, ETF-flow market plumbing, stablecoin liquidity, cross-asset
connectedness, and crypto-native market structure.

The canonical public artifact packet lives under `outputs/`. It uses a frozen
daily panel from 2020-01-01 through 2026-04-11 with 2,293 rows and 63 columns.
The frozen-data design keeps the project reproducible and avoids paid or live
data dependencies for public review.

## Headline Results

- BTC model fit is heavily influenced by native valuation and flow-state
  variables, especially MVRV-style valuation state. MVRV is separated from
  non-MVRV native variables because it can mechanically co-move with returns.
- ETF-flow intensity has strong same-day association with BTC and ETH returns,
  but daily data cannot identify causal flow impact. The evidence is framed as
  market-plumbing and lead-lag diagnostics.
- Rolling correlations show time-varying integration between BTC, ETH, TradFi,
  rates, and volatility variables.
- Stablecoin supply and DeFi TVL are useful liquidity context, not identified
  liquidity shocks.
- Structural-break diagnostics are Chow tests and single-break sup-F sweeps,
  not full multiple-break Bai-Perron estimation.
- Advanced diagnostics include PCA compression, exact block Shapley R2,
  exploratory CUSUM, FEVD-order sensitivity, rolling connectedness, and a BTC
  robustness grid.
