# Model Card - Static Factor Exposure OLS

## Purpose

Estimate reduced-form BTC/ETH return exposure to macro, institutional,
liquidity, sentiment, and native factor blocks.

## Inputs

`reports/panels/master_daily.parquet` transformed by
`src/cqresearch/features/panel.py`.

## Method

OLS with HAC/Newey-West standard errors over full, pre-ETF, and post-ETF
samples.

## Outputs

`static_ols_pre_post_etf.csv` and `block_r2_pre_post.csv`.

## Interpretation

Exposure and association diagnostics, not causal estimates.

## Risks

Multicollinearity, mixed calendars, omitted variables, and observational
confounding.

## Upgrade Path

Add block-level Shapley/Owen attribution only after a tested implementation is
available, and keep the current HAC OLS outputs as the reproducible baseline.
