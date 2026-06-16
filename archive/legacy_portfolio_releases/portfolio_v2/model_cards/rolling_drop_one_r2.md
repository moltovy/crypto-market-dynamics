# Model Card - Rolling Drop-One Marginal R^2

## Purpose

Track time variation in model fit and approximate factor-block contribution.

## Inputs

Stationary feature panel and 180-day rolling windows.

## Method

Fit rolling OLS, then drop one regressor at a time and measure the increase in
RSS relative to TSS.

## Outputs

`rolling_ols_btc_180d.csv`, `rolling_ols_eth_180d.csv`, and stacked figures.

## Interpretation

Drop-one marginal R^2 is conditional on the full model and correlated
regressors. It is not Shapley/Owen fair attribution.

## Risks

Correlated features can make marginal attribution unstable.

## Upgrade Path

Add Shapley/Owen attribution as an appendix and compare it against the current
drop-one marginal R^2 outputs before promoting any new attribution language.
