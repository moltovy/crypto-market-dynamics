# Methodology

## Feature Construction

The panel standardizes heterogeneous daily data into returns, differences,
intensity ratios, rolling volatility, and event-aligned variables. ETF-flow
intensity is scaled by prior-day USD market capitalization to make flow
magnitudes comparable through time.

## Factor Exposure

Static models use HAC OLS to estimate reduced-form associations between BTC/ETH
returns and factor families. Results are not structural shocks or causal
effects.

## Attribution

Canonical block attribution is full-vs-reduced block partial R2. It measures the
loss in explanatory power when a block is removed from the full model. Advanced
attribution includes exact block Shapley R2 over the chosen block design.

## Lead-Lag

Lead-lag tables use the convention `lag < 0` means the explanatory series is
shifted earlier and leads the target return. Daily sequencing remains
simultaneity-prone.

## Regimes And Connectedness

Rolling correlations, Chow tests, single-break sup-F scans, VAR/FEVD tables,
and event studies are descriptive regime and connectedness diagnostics.
