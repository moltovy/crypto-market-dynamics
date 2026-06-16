# Model Card - CUSUM Diagnostics

## Purpose

Flag periods where residual paths suggest possible parameter instability.

## Inputs

BTC/ETH returns with compact macro/TradFi/liquidity controls.

## Sample

Full frozen sample with complete-case rows.

## Method

Fit full-sample OLS, cumulate standardized residuals, and compare with a visual 5% boundary.

## Output files

`cusum_summary.csv`, `cusum_paths.csv`, `F74`, `F75`.

## Interpretation

Boundary crossings are prompts for regime discussion and further testing.

## Risks / limitations

This is exploratory standardized residual CUSUM, not full Bai-Perron multi-break estimation.

## Upgrade path

Replace or augment with statsmodels recursive residual tests and selected break-date inference.
