# Model Card - BTC Robustness Grid

## Purpose

Test whether BTC factor fit is sensitive to common modeling choices.

## Inputs

BTC returns and macro, TradFi, liquidity, sentiment, and BTC-native regressors.

## Sample

Trailing 90, 180, and 365 day windows with crypto-seven-day and weekday calendars.

## Method

Run static HAC OLS across window, HAC lag, winsorization, MVRV, and calendar choices.

## Output files

`robustness_grid.csv`, `F78`.

## Interpretation

Stable R2 across cells supports model robustness; unstable cells clarify limitations.

## Risks / limitations

Grid search is diagnostic and in-sample; it is not model selection by itself.

## Upgrade path

Add out-of-sample forecasts, purged cross-validation, and coefficient stability summaries.
