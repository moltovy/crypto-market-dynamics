# Market-Structure Fetch Diagnostics

Endpoint rows audited: 25

Optional key-gated endpoints available now: 0/1

Skipped outputs:
- Binance liquidity top100 skipped because no spot kline cache exists.
- CMC Fear & Greed skipped because CMC_API_KEY/cache is unavailable; AlternativeMe baseline used.
- Historical market-cap top100 skipped because no point-in-time source is available.

No API keys are written to public outputs. Raw payloads, when fetched, remain in `data_cache/`.
