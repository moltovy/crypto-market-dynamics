# TradFi Exposure Model Card

Purpose: measure contemporaneous BTC/ETH co-movement with equities, volatility, dollar, rates, and gold.

Calendar: daily models use common TradFi business-date closes; weekly models use Friday-to-Friday returns.

Estimator: same-support HAC OLS with drop-block delta R-squared, conventional partial R-squared in a separate table, FDR, VIF, and ridge diagnostics.

Principal finding: BTC equity block pre-BTC-ETF delta R2=0.0249 (n=797) vs BTC-ETF-era delta R2=0.0884 (n=436); ETH equity block pre-BTC-ETF delta R2=0.0193 (n=797) vs BTC-ETF-era delta R2=0.1076 (n=436); period comparison, not ETF effect.

Prohibited claims: ETF effect; forecast; causal macro driver.
