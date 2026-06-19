# Altseason Rotation Lab

The daily constituent layer adds exploratory breadth, dispersion, rolling beta, rotation, and event-response diagnostics from the available DefiLlama current-top50 ex-stablecoin OHLCV sample.

Current top50 ex-stablecoin constituent sample from DefiLlama daily OHLCV. Use for exploratory breadth/rotation diagnostics only; it is not a point-in-time top100 universe.

Definitions:

- `broad_altseason`: at least 70% of clean-risk ex-BTC/ETH constituents beat BTC over 90 days.
- `btc_led`: BTC beats ETH and the median clean-risk sample over 90 days.
- `eth_led`: ETH beats BTC and the median clean-risk sample over 90 days.
- `large_cap_rotation_vs_btc`: top10 ex-BTC/ETH 90-day return minus BTC 90-day return.

- Latest 90-day breadth: 54.5% of clean-risk sample assets beat BTC; regime `mixed_rotation`.
- Daily constituent span: 2023-01-01 to 2026-06-16; index rows: 7,572.
- Event-response rows: 160.

Guardrail: this is a current top50 sample, not a point-in-time top100/top200 constituent panel. Treat it as an exploratory rotation lab until a full point-in-time daily OHLCV/mcap file is supplied.
