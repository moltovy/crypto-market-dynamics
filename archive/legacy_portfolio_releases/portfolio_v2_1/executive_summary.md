# Crypto Market Factor Lab - Portfolio v2.1 Executive Summary

## What The Project Is

Crypto Market Factor Lab is a reproducible BTC/ETH factor analytics system built
on a frozen multi-source daily panel. It is a portfolio-grade quant research and
data-engineering project, not a publication-first academic paper.

## Data And Reproducibility

The frozen master panel spans 2020-01-01 through 2026-04-11
with 2,293 daily rows and 63 columns.
Portfolio v2.1 uses the existing panel and the baseline source bundles
`reports\tables\2026-06-16` and
`reports\figures\2026-06-16`. No raw `Data/` files are
modified and no paid or live data source is required.

## What v2.1 Adds Over v2

- True full-vs-reduced block partial R^2 tables and 180-day rolling block
  partial R^2 outputs.
- BTC/ETH nested ablation waterfalls that separate macro, TradFi, liquidity,
  sentiment, ETF intensity, and native variables.
- ETF-flow lead-lag and quintile diagnostics with an explicit lag convention.
- Rolling cross-asset correlation and pre/post ETF delta dashboards.
- Stablecoin liquidity proxy and realized-volatility diagnostics.
- BTC-native factor registry with MVRV separated from non-MVRV native flows.

## Headline Analytics

- BTC post-BTC-ETF block partial R^2 is led by **BTC MVRV**
  (0.687). MVRV-like variables are treated separately from macro and
  ETF-flow interpretation.
- ETH post-ETH-ETF block partial R^2 is led by **TradFi**
  (0.034), so ETH remains a comparison asset rather than forced BTC
  symmetry.
- BTC same-day ETF-flow intensity lead-lag row: beta=56.87,
  HAC t=10.22, R^2=0.271.
- ETH same-day ETF-flow intensity lead-lag row: beta=25.22,
  HAC t=4.68, R^2=0.248.

## Interpretation Boundaries

All results are reduced-form diagnostics. ETF-flow evidence is association and
market plumbing, not proof that flows caused BTC or ETH returns. Structural-break
references remain Chow plus single-break sup-F diagnostics, not full
Bai-Perron. Rolling and block attribution are not Shapley/Owen allocations.

## Job-Market Value

The v2.1 packet demonstrates frozen-data engineering, econometric hygiene,
factor modeling, crypto market-structure reasoning, visual communication,
model-card discipline, and one-command reproducible portfolio packaging.
