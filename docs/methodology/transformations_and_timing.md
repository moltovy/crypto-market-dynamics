# Transformations And Timing

- Prices use log returns.
- Rates and index levels use first differences where appropriate.
- ETF flows are scaled by lagged market capitalization.
- Liquidations use `log1p` and lagged denominators where possible.
- MVRV same-day changes are diagnostic only; lagged MVRV levels, percentiles, z-scores, and regimes are used for state conditioning.
- Stablecoin and DeFi liquidity features are primary at weekly frequency.
- Monthly PIT market-universe data is joined only for composition, concentration, and turnover analysis.
- Same-support model comparisons use identical non-missing row sets.
