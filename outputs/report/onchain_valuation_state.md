# On-Chain Valuation State

MVRV is retained as a measurement-mechanics audit and lagged valuation-state variable. Same-day `d_log_mvrv` is mechanically tied to BTC market capitalization and is excluded from the primary ex-MVRV exposure models.

The identity audit aligns `d_log_mvrv`, `d_log_market_cap`, and `d_log_realized_cap` over the same date interval and reports residual scale diagnostics. Residuals are interpreted with source-convention caveats, not assumed negligible.

The regime table uses lagged MVRV percentiles and reports conditional forward return, realized volatility, drawdown, funding, and leverage summaries. These are descriptive state summaries, not forecasts.
