# Research Spec - Legacy Draft

> **Legacy warning:** this v0.1 research spec is retained for provenance only.
> The current portfolio release contract is
> [`portfolio_spec.md`](./portfolio_spec.md) plus
> [`methods_spec_v2.md`](./methods_spec_v2.md). Do not use this file as the
> active public framing for portfolio v2.

**Status:** LEGACY DRAFT - v0.1 (2026-04-18)

## 1. Historical Research Question

How did the factor exposures of BTC and ETH returns, decomposed into macro,
institutional, liquidity, and native blocks, evolve around the 2024 US spot-ETF
launches?

## 2. Historical Scope

- **In scope at the time:** BTC and ETH daily log returns, factor blocks, and
  pre-registered events in `config/events.yml`.
- **Out of scope:** altcoins beyond BTC/ETH/WBTC, intraday dynamics, and
  forecasting.

## 3. Historical Null Hypotheses

- H01: block-level diagnostics are constant across pre- and post-ETF subsamples.
- H02: no structural break at 2024-01-11 in the BTC return process.
- H03: no structural break at 2024-07-23 in the ETH return process.
- H04: Diebold-Yilmaz total-connectedness index is stationary over the sample.

## 4. Current Portfolio Interpretation

Portfolio v2 uses Chow plus single-break sup-F diagnostics. Full Bai-Perron
multi-break estimation is not implemented. Rolling attribution is drop-one
marginal R^2, not Shapley/Owen attribution. ETF-flow results are reduced-form
associations and should not be described as causal effects.

## 5. Superseded Deliverables

The earlier paper-style deliverables are superseded by the portfolio packet in
`reports/portfolio_v2/`: executive summary, technical report, data atlas, model
cards, curated figures/tables, and resume bullets.
