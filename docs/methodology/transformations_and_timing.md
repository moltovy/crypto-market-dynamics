# Transformations And Timing

- Prices use log returns.
- Rates and index levels use first differences where appropriate.
- ETF flows are scaled by prior-period market capitalization and modeled separately at lag 0 and lag 1 in ETF-era augmented specifications.
- Liquidations are expressed as liquidation USD divided by prior-period open interest in percent and prior-period market cap in basis points.
- MVRV same-day changes are diagnostic only; lagged MVRV levels, percentiles, z-scores, and regimes are used for state conditioning.
- Stablecoin and DeFi liquidity features are primary at weekly frequency; weekly returns sum daily log returns, weekly changes sum daily level changes, flows sum over the week and scale by prior week-end denominators, and state variables use prior week-end state.
- Monthly PIT market-universe data is joined only for composition, concentration, and turnover analysis.
- Same-support model comparisons use identical non-missing row sets.
