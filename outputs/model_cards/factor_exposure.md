# Model Card - Static OLS

## Purpose

Estimate BTC/ETH reduced-form exposure to factor stacks.

## Inputs

Frozen feature panel derived from `reports/panels/master_daily.parquet`.

## Sample

Full, pre-ETF, and post-ETF samples from the baseline bundle.

## Method

HAC/Newey-West OLS using stationary transformed variables.

## Output files

`baseline_static_ols_pre_post_etf.csv`.

## Interpretation

Factor exposure diagnostics, not causal estimates.

## Risks / limitations

Omitted variables, multicollinearity, and sample-support differences.

## Upgrade path

Add sensitivity tables for alternative controls and common-support samples.
