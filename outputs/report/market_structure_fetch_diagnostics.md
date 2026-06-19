# Market-Structure Fetch Diagnostics

Endpoint rows audited: 25

Optional key-gated endpoints available now: 0/1

Cached CMC Fear & Greed rows available: 1086

Skipped outputs:
- Binance liquidity top100 skipped because no spot kline cache exists.
- Historical market-cap top100 skipped because no point-in-time source is available.

No API keys are written to public outputs. Raw payloads, when fetched, remain in `data_cache/`.
