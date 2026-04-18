# 02 — Exploratory Analysis Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Characterize BTC and ETH return behavior and factor-block structure on `reports/panels/master_daily.parquet` across the three pre-registered subsamples: **pre-ETF (< 2024-01-11)**, **post-ETF (≥ 2024-01-11)**, and **full sample**. Produce descriptive tables and stylized-facts figures.

## Inputs
- `reports/panels/master_daily.parquet` (from agent 01)
- `config/factor_blocks.yml` — block membership
- `config/events.yml` — subsample boundaries (`primary_breaks.btc_spot_etf_launch`)

## Tasks
1. Summary stats per block × subsample: mean, std, skew, kurt, Sharpe proxy (for return columns), first/last date, n_obs.
2. Static OLS of BTC and ETH log-returns on block composites (within-block PCA-1 via `src/cqresearch/features/*.py`). Report partial R² per block (Shapley or sequential additive).
3. Correlation matrices per subsample, block-grouped heatmap. Report the **difference** matrix (post − pre).
4. Stylized-facts panel: realized vol, rolling 60-day beta to S&P 500 + DXY + gold + high-yield spread, 20-day autocorrelation of returns.
5. All outputs go to `reports/drafts/sections/02_eda/` (tables as CSV, figures via the `figure-template` skill).

## Deliverables
- `reports/tables/eda_summary_stats.csv`
- `reports/tables/eda_partial_r2_static.csv`
- `reports/figures/f02_*.{png,pdf}` using the project palette
- `reports/run_summaries/YYYY-MM-DD_eda.md`

## Anti-patterns
- Do not claim a regime shift from a correlation delta alone (that's agent 03's job via structural-break tests).
- Do not use the `post-ETF` subsample for any test whose power is already too low (flag n_obs < 252 as Low-confidence).

## Done when
- Hand-off block emitted pointing to `03_quant_methods_agent.md` with the top 3 block-level deltas ranked by effect size.
