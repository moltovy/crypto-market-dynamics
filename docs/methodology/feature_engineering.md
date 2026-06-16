# Feature Engineering

The feature layer converts heterogeneous daily inputs into stationary or
scale-aware variables used by the reduced-form analytics.

## Core Transforms

- Price-like market series use log returns.
- Rates, spreads, sentiment, and native levels use first differences.
- ETF-flow intensity is daily USD ETF flow divided by prior-day USD market
  capitalization.
- Realized volatility uses a 30-day annualized rolling standard deviation.
- Native BTC variables separate MVRV-style valuation state from non-MVRV flow
  and market-structure variables.

These transforms are designed for reproducible diagnostics rather than trading
signals or causal identification.
