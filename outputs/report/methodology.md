# Transformations And Timing

- Prices use log returns.
- Rates and index levels use first differences where appropriate.
- Daily TradFi models use common business-date closes: BTC/ETH returns are recomputed between consecutive common TradFi business dates, then aligned with QQQ, SPY, IWM, DXY, gold, VIX, real-yield, and nominal-yield moves on those same business dates.
- Weekly TradFi models use Friday-to-Friday BTC/ETH and TradFi returns/changes.
- Crypto-native weekly liquidity/state analysis uses Sunday-ended crypto weeks.
- ETF trading-day panels compute BTC/ETH returns from the prior ETF trading date to the current ETF trading date.
- ETF flows are scaled by prior-period market capitalization and modeled separately at lag 0 and lag 1 in ETF-era augmented specifications.
- Liquidations are expressed as liquidation USD divided by prior-period open interest in percent and prior-period market cap in basis points.
- MVRV same-day changes are diagnostic only; lagged MVRV levels, percentiles, z-scores, and regimes are used for state conditioning.
- Stablecoin and DeFi state features are primary at weekly frequency; weekly returns sum daily log returns, weekly changes sum daily level changes, flows sum over the week and scale by prior week-end denominators, and state variables use prior week-end state.
- Raw USD DeFi TVL growth is labeled `valuation_sensitive_defi_tvl_growth` unless price-adjusted. OI growth is audited and OI/market-cap growth is preferred when OI is treated as USD/notional-valued.
- Monthly PIT market-universe data is joined only for composition, concentration, and turnover analysis.
- Same-support model comparisons use identical non-missing row sets.


## Estimation

Full, reduced-block, and feature-drop models are fit on one explicitly constructed complete-case frame per asset, frequency, regime, and model family. The tables report `n_full`, `n_reduced`, `same_support`, sample dates, feature lists, and row-index hashes. The build fails if nested-model R-squared monotonicity or conventional partial-R-squared bounds are violated.

## Evidence Language

Contemporaneous TradFi coefficients are exposure/co-movement estimates. Crypto-native lagged variables are lagged-state associations. ETF flow intensity is a market-plumbing association. Raw USD TVL is a valuation-sensitive DeFi balance-sheet proxy, and OI growth is interpreted through OI/market-cap scaling when treated as USD/notional-valued.
