# Methods Spec — Econometric Protocol

> Skeleton. Owned by the Quant Methods Lead. Fill in during Sprint 2 (rolling OLS + structural breaks) and Sprint 3 (VAR/FEVD + event study).

**Status:** DRAFT — v0.1 (2026-04-18)
**Canonical plan:** [`project_research_plan.md`](../../project_research_plan.md) §11.3 – §11.5

---

## 1. Notation
- Let $r_t^{(i)}$ denote the daily log-return of asset $i \in \{BTC, ETH\}$ at date $t$.
- Let $X_t^{(b)}$ denote the within-block PCA-1 composite of block $b \in \{\text{macro, institutional, liquidity, btc\_native, eth\_native}\}$.
- Let $\tau^{*}$ denote a pre-registered event date from `config/events.yml`.

## 2. Static OLS per subsample
$$r_t^{(i)} = \alpha + \sum_{b} \beta^{(b)} X_t^{(b)} + \varepsilon_t.$$
- Estimator: OLS with HAC (Newey-West) standard errors, lag selected by Andrews automatic rule.
- Report: coefficient, HAC t-stat, total R², **partial R² per block** (sequential + Shapley).

## 3. Rolling OLS
- Windows: $w \in \{60, 120, 252\}$ trading days. Report all three.
- Step: 1 day.
- Output: block × date matrix of partial R².

## 4. Chow test at pre-registered $\tau^{*}$
- Restricted: full-sample OLS.
- Unrestricted: pre-$\tau^{*}$ and post-$\tau^{*}$ OLS pooled.
- Report: F-stat, p-value, coefficient deltas per block.

## 5. Bai-Perron multiple-break search
- Window: $\tau^{*} \pm 60$ trading days.
- Max breaks: 2.
- Trimming: 15%.
- Report: supF, UDmax, WDmax, break locations and 95% CIs.

## 6. CUSUM / CUSUM-of-squares
- Recursive residuals on OLS from §2.
- Plot 5% bands.

## 7. Placebo protocol
- Re-run §4-§6 on each date in `config/events.yml.placebos`. Any real-date significance that also appears at a placebo date is downgraded.

## 8. Compact VAR
- Variables: `[btc_ret, eth_ret, spx_ret, dxy_ret, hy_spread_Δ, stablecoin_mcap_Δ, etf_net_flows_Δ]`.
- Lag: AIC-selected, cap 5.
- Stability: check eigenvalues inside unit circle.
- Identification: Cholesky ordering (declared in `docs/decisions/<date>_cholesky_ordering.md` — pending).

## 9. FEVD (Diebold-Yilmaz)
- Horizon: 10 days.
- Rolling: 126-day window for total-connectedness index.
- Output: pairwise directional spillover table + rolling index plot.

## 10. Event study
- Estimation window: [−252, −21] trading days from $\tau^{*}$.
- Event window: [−5, +5], [−20, +20], [−60, +60] trading days.
- Abnormal return: $\hat\varepsilon_t$ from a market-model benchmark (S&P 500 or global crypto market cap — declared per asset).
- Test stats: CAR, Patell, BMP.

## 11. Robustness checklist (automatic)
- Window-size sensitivity.
- HAC lag sensitivity (0 vs optimal).
- Outlier leverage (Cook's D > 4/n flagged).
- Winsorization at 1% / 5% (reported, not default).
- Placebo battery.

## 12. Reporting contract
Every model output writes `reports/tables/<model>_<tag>_<YYYY-MM-DD>.csv` + a run summary with the 11-point checklist ticked.
