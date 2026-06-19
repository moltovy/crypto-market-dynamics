# Current-Cohort Rotation Lab

The current-cohort daily layer adds exploratory breadth, dispersion, rolling beta, rotation, and event-response diagnostics from the available DefiLlama current-top50 ex-stablecoin OHLCV sample.

Current-top50 exploratory ex-stablecoin cohort from DefiLlama daily OHLCV. Use for current-cohort diagnostics only; it is survivorship-biased, not point-in-time, and not the primary altseason backtest.

Definitions:

- `current_cohort_broad_breadth`: at least 70% of clean-risk ex-BTC/ETH current-cohort constituents beat BTC over 90 days.
- `current_cohort_btc_led`: BTC beats ETH and the median clean-risk current-cohort sample over 90 days.
- `current_cohort_eth_led`: ETH beats BTC and the median clean-risk current-cohort sample over 90 days.
- `large_cap_rotation_vs_btc`: top10 ex-BTC/ETH 90-day return minus BTC 90-day return.

- Latest 90-day breadth: 52.9% of clean-risk sample assets beat BTC; regime `current_cohort_mixed_rotation`.
- Daily constituent span: 2023-01-01 to 2026-06-16; index rows: 7,572.
- Event-response rows: 160.

Guardrail: this is a current-top50 cohort diagnostic. It is survivorship-biased, not point-in-time, and not the primary altseason backtest. Treat it as exploratory until a full point-in-time daily OHLCV/mcap file is supplied for every asset that ever appears in the PIT top100/top200 universe.
