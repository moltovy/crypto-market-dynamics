# Static Payload Schema Notes

The optional-data tests currently keep sample payloads inline. Expected payload
shapes are:

| Source | Payload Shape | Normalized Key Columns |
|---|---|---|
| DefiLlama chains | list of chain dictionaries | `source`, `chain`, `tvl_usd`, `token_symbol` |
| DefiLlama protocol TVL | dictionary with `slug` and `tvl` list | `source`, `protocol`, `date`, `tvl_usd` |
| CoinGecko market chart | dictionary with `prices`, `market_caps`, `total_volumes` arrays | `source`, `coin_id`, `date`, `price_usd`, `market_cap_usd`, `volume_usd` |
| Binance klines | list of 12-field kline arrays | `source`, `symbol`, `interval`, `open_time`, `close_time`, OHLCV fields |
| FRED observations | dictionary with `observations` list | `source`, `series_id`, `date`, `value` |
