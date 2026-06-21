# Econometric Methods

## Static Factor Models

Static BTC/ETH factor exposure models use HAC OLS. The estimates are
reduced-form associations between returns and factor families.

## Lead-Lag Diagnostics

ETF-flow and stablecoin lead-lag tables use the convention `lag < 0` means the
explanatory series is shifted earlier and leads the target return. Daily data is
simultaneity-prone, so the outputs are market-plumbing diagnostics, not causal
flow-impact estimates.

## Regime Diagnostics

Rolling correlations, pre/post event deltas, Chow tests, single-break sup-F
scans, event-window CARs, and VAR/FEVD connectedness tables are descriptive
regime diagnostics.

## Advanced Diagnostics

The advanced layer includes PCA block compression, exact block-attribution
sensitivity checks, exploratory CUSUM, FEVD-order sensitivity, rolling
connectedness, and a BTC robustness grid.
