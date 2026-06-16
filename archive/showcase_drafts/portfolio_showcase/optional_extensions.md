# Optional Extensions

The optional extension layer is intentionally separate from the frozen
portfolio releases. It is useful for discussing where the project can go next
without weakening reproducibility.

## Candidate Extensions

| Extension | Value | Recommendation |
|---|---|---|
| Binance intraday microstructure | Adds realized volatility, volume, and liquidity checks at a higher frequency than the daily panel. | Best future quant-dev extension. |
| DefiLlama TVL/stablecoin refresh | Audits DeFi/stablecoin liquidity coverage against current public endpoints. | Best low-maintenance data refresh candidate. |
| CoinGecko asset benchmarks | Adds free market-cap/volume benchmarks for broader asset coverage. | Optional benchmark extension. |
| FRED macro refresh | Refreshes macro factors already represented in the frozen panel. | Useful only with explicit versioning. |
| SEC/public ETF filings | Documents ETF approval/listing event dates from primary sources. | Useful for event-study audit notes. |

## Guardrails

- Optional sources do not replace the frozen core dataset.
- No paid data is required.
- Tests use static payloads and do not make network calls.
- Any future live fetch should write to a separate versioned cache, not curated
  raw `Data/` files.
