# Executive Summary

Crypto Market Dynamics is a descriptive research-code project covering BTC/ETH valuation mechanics, synchronized TradFi exposure, ETF market plumbing, leverage/tail stress, stablecoin/DeFi state, point-in-time market structure, selected-major risk, and event windows from local 2020-2026 data.

The strongest measurement warning remains MVRV: corr(BTC return, d-log MVRV)=0.9966; R2=0.9932; median abs residual / median abs BTC return=1.14e-07. Same-day MVRV therefore stays out of the primary BTC/ETH exposure models and appears only as a mechanics audit and lagged state context.

TradFi exposure is now calendar-synchronized. BTC equity block pre-BTC-ETF delta R2=0.0249 (n=797) vs BTC-ETF-era delta R2=0.0884 (n=436); ETH equity block pre-BTC-ETF delta R2=0.0193 (n=797) vs BTC-ETF-era delta R2=0.1076 (n=436); period comparison, not ETF effect. This is a period comparison of co-movement on common business-date closes, not an ETF-effect estimate.

ETF, leverage, and liquidity results are descriptive and timing-sensitive. BTC lag0 return corr=0.379 (n=820) vs lag1=0.049 (n=819); ETH lag0 return corr=0.226 (n=627) vs lag1=0.086 (n=626). Q1 low tail-day rate=7.06% (n=453); Q3 tail-day rate=4.20% (n=452); Q5 high tail-day rate=7.73% (n=453); read as U-shaped state pattern. BTC same-week raw USD TVL corr=0.679 (n=327); ETH same-week raw USD TVL corr=0.761 (n=327); TVL labeled valuation-sensitive.

The latest PIT structure headline is 2026-06-16 partial snapshot (month=2026-06) top10 share=87.64%, HHI=0.334. Selected-major risk is coverage-aware: 10 assets comparable from 2024-11-30 to 2026-06-16; HYPE max-coverage n=564. Event outputs remain empirical placebo-window tests: BTC,ETH event windows use block size=10; median eligible placebo windows=2007; convention +1 through +10.

Release caveat: `DATA_LICENSE.md` and `provider_data_disposition.csv` document provider-data risk but do not grant redistribution rights. The repository should remain private until uncertain/restricted raw exports are cleared or removed from the public repository and history.
