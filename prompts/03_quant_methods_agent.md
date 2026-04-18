# 03 — Quant Methods Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Run the **headline quantitative analyses** that test whether BTC/ETH factor exposures shifted around the 2024 US spot-ETF launch. Three workstreams, all mandatory: rolling partial R², pre-registered structural breaks, compact VAR/FEVD.

## Inputs
- `reports/panels/master_daily.parquet`
- `config/factor_blocks.yml`, `config/events.yml`

## Workstream A — Rolling OLS with block-level partial R²
- Window sizes: 60, 120, 252 trading days. Report all three (sensitivity).
- Standard errors: HAC (Newey-West) with automatic lag selection.
- Output: a **block × date** partial-R² matrix per asset; plot the stacked time series and the Δ(post − pre) bar.
- Implement in `src/cqresearch/modeling/ols_rolling.py`. Unit test with a synthetic regime-shift fixture.

## Workstream B — Structural-break battery
Invoke the `structural-break-runner` skill for each event in `config/events.yml.primary_breaks`:
- BTC spot-ETF launch (2024-01-11).
- ETH spot-ETF launch (2024-07-23).
- 2024 Bitcoin halving (2024-04-20).

For each, run the full Chow + Bai-Perron + CUSUM + Placebo battery. Tables go to `reports/tables/breaks/`.

## Workstream C — Compact VAR + FEVD (Diebold-Yilmaz)
- Variables: `[btc_ret, eth_ret, spx_ret, dxy_ret, hy_spread_Δ, stablecoin_mcap_Δ, etf_net_flows_Δ]`.
- Lag: pick by AIC, cap at 5. Identification: Cholesky with the ordering declared in `docs/specs/methods_spec.md`.
- Report 10-day-ahead FEVD; rolling 126-day total-connectedness index; pairwise directional spillovers.
- Implement in `src/cqresearch/modeling/var_fevd.py`.

## Guardrails
- Never add an event date that is not already in `config/events.yml` without an ADR.
- Never cherry-pick the window size in the narrative — always show 60/120/252.
- Never interpret Bai-Perron break dates whose 95% CI spans > 30 days as precisely located.

## Done when
- Hand-off block emitted pointing to `04_visualization_agent.md` listing every table/figure written and the top 5 numerical findings with confidence labels.
