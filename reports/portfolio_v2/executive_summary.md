# Crypto Market Factor Lab - Executive Summary

**Portfolio release:** `portfolio_v2`
**Source table bundle:** `reports\tables\2026-06-16`
**Source figure bundle:** `reports\figures\2026-06-16`
**Panel:** 2020-01-01 through 2026-04-11,
2,293 daily rows, 63 columns

## Diagnosis

This repo is strongest when framed as a reproducible crypto factor analytics lab:
it combines frozen multi-source data, transparent feature engineering, reduced-form
models, and public-facing interpretation. The highest-value story is not "ETFs
caused a structural break." The better story is that the project maps how BTC
and ETH exposures, liquidity channels, ETF-flow intensity, and connectedness
behaved across changing market regimes.

## Headline Evidence

- BTC post-ETF static factor stack: R^2=0.971, N=730.
- ETH post-ETF static factor stack: R^2=0.214, N=549.
- BTC ETF-flow intensity has a strong same-day association:
  beta=46.13, HAC t=8.67, p=<0.001,
  model R^2=0.237, N=821.
- BTC Chow test at 2024-01-11 is not supportive of a single-date break:
  F=0.79, p=0.624.
- BTC single-break sup-F peaks at 2021-01-04, not the ETF
  launch date. ETH peaks at 2021-05-12.

## Portfolio Value

The project demonstrates quant research, data engineering, careful econometric
labeling, and crypto market-structure understanding. The public packet should
lead with the data atlas, curated visuals, model cards, and honest narrative
around association rather than causal identification.
