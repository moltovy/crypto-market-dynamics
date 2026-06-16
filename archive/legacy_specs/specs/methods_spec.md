# Methods Spec - Legacy Draft

> **Legacy warning:** this v0.1 methods spec is retained for provenance only.
> The active portfolio v2 method contract is
> [`methods_spec_v2.md`](./methods_spec_v2.md).

**Status:** LEGACY DRAFT - superseded for portfolio release by
[`methods_spec_v2.md`](./methods_spec_v2.md)

## 1. Historical Notation

- Let `r_t` denote daily log returns for BTC or ETH.
- Let `X_t` denote factor-block features used in reduced-form diagnostics.
- Let `tau` denote pre-registered event dates from `config/events.yml`.

## 2. Static OLS

The implemented pipeline estimates OLS with HAC/Newey-West standard errors over
full, pre-ETF, and post-ETF samples. Results are exposure and association
diagnostics, not causal estimates.

## 3. Rolling OLS

The implemented rolling model uses 180-day windows and reports drop-one
marginal R^2 surfaces. This is not Shapley/Owen attribution.

## 4. Structural-Break Diagnostics

The current code implements Chow tests at ETF dates and a single-break sup-F
sweep with trimming. It does not implement a full Bai-Perron multi-break
estimator.

## 5. VAR/FEVD and Event Studies

The implemented pipeline uses statsmodels VAR/FEVD connectedness diagnostics and
market-model event studies. These outputs should be described as reduced-form
diagnostics and event-window associations.
