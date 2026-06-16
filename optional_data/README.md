# Optional Free-Data Extension Layer

This folder documents optional data-source scaffolding for future work. The core
portfolio releases (`portfolio_v2`, `portfolio_v2_1`, and `portfolio_v2_2`) do
not depend on live pulls from these sources.

## Included Scaffolding

- DefiLlama public endpoint URL builders and normalizers
- CoinGecko market-chart URL builder and normalizer
- Binance public kline URL builder and normalizer
- FRED observations URL builder and normalizer

## Policy

- No raw `Data/` files are modified by this layer.
- Tests use static sample payloads only.
- Free/live sources are optional audit or extension inputs, not prerequisites for
  reproducing the portfolio packets.
