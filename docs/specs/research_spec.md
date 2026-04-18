# Research Spec — CryptoQuant BTC/ETH Factor-Block Evolution

> Skeleton. Owned by the Research Lead. Every section to be filled in during Sprint 1.

**Status:** DRAFT — v0.1 (2026-04-18)
**Canonical plan:** [`project_research_plan.md`](../../project_research_plan.md)

---

## 1. Research question (one sentence, pre-registered)
*How did the factor exposures of BTC and ETH returns — decomposed into macro, institutional, liquidity, and native blocks — evolve around the 2024 US spot-ETF launches?*

## 2. Scope
- **In scope.** BTC and ETH daily log-returns; four factor blocks per asset; pre-registered events in `config/events.yml`.
- **Out of scope.** Altcoins beyond BTC/ETH/WBTC; intraday dynamics; forecasting.

## 3. Null hypotheses (pre-registered)
- H01: block-level partial R² is constant across pre- and post-ETF subsamples.
- H02: no structural break at 2024-01-11 in the BTC return generating process.
- H03: no structural break at 2024-07-23 in the ETH return generating process.
- H04: Diebold-Yilmaz total-connectedness index is stationary over the sample.

## 4. Success criteria
- Each H0 is evaluated by at least two independent tests (e.g. Chow + Bai-Perron).
- Every finding is robust to 60/120/252 day rolling window choice.
- Placebo dates produce no false positives at the 1% level (or the false-positive rate is documented).

## 5. Deliverables
- Peer-reviewable empirical note (`reports/drafts/paper_v1.0.*`).
- Reproducible panel (`reports/panels/master_daily.parquet`).
- Public figure set (`reports/figures/`) and table set (`reports/tables/`).
- Replication packet (`reports/drafts/submission/<date>/replication.md`).

## 6. Non-goals
Listed in `.cursor/rules/global-constitution.mdc`.

## 7. Open questions
- To be populated by agent 01 (data cleaning) after DQ runs.
