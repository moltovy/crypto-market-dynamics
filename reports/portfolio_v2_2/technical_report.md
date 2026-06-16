# Portfolio v2.2 Technical Report

## Scope

This packet extends the v2.1 portfolio release with advanced diagnostics while
leaving v2 and v2.1 outputs intact. It is built from the frozen master panel
(`2020-01-01` to `2026-04-11`) and writes only to
`reports/portfolio_v2_2/`.

## Generated Tables

- PCA: `pca_block_loadings.csv`, `pca_explained_variance.csv`,
  `pca_factor_panel_summary.csv`, `pca_static_ols.csv`
- Shapley: `shapley_r2_btc.csv`, `shapley_r2_eth.csv`,
  `rolling_shapley_r2_btc_180d.csv`, `rolling_shapley_r2_eth_180d.csv`
- Regime/VAR: `cusum_summary.csv`, `fevd_order_sensitivity.csv`,
  `fevd_order_sensitivity_summary.csv`, `rolling_connectedness.csv`
- Robustness: `robustness_grid.csv`

## PCA Output Snapshot

| block      |   component |   explained_variance_ratio |   n_variables |
|:-----------|------------:|---------------------------:|--------------:|
| Macro      |           1 |                   0.374273 |             5 |
| Macro      |           2 |                   0.237778 |             5 |
| TradFi     |           1 |                   0.651888 |             3 |
| TradFi     |           2 |                   0.324323 |             3 |
| Liquidity  |           1 |                   0.587657 |             2 |
| Liquidity  |           2 |                   0.412343 |             2 |
| BTC Native |           1 |                   0.281787 |             4 |
| BTC Native |           2 |                   0.261744 |             4 |
| ETF Flow   |           1 |                   0.752169 |             2 |
| ETF Flow   |           2 |                   0.247831 |             2 |

## CUSUM Summary

|    n |   max_abs_cusum |   bound_5pct | crossed_5pct   | method                                  | asset   | controls                                         |
|-----:|----------------:|-------------:|:---------------|:----------------------------------------|:--------|:-------------------------------------------------|
| 2291 |         1.22721 |         1.36 | False          | exploratory_standardized_residual_cusum | btc     | spy_ret;VIXCLS_d1;DGS10_d1;stables_total_usd_ret |
| 2291 |         1.55039 |         1.36 | True           | exploratory_standardized_residual_cusum | eth     | spy_ret;VIXCLS_d1;DGS10_d1;stables_total_usd_ret |

## Rolling Connectedness Snapshot

| date                |   connectedness_pct |   lag_order |   n | error   |
|:--------------------|--------------------:|------------:|----:|:--------|
| 2020-09-10 00:00:00 |             35.2319 |           1 | 252 |         |
| 2020-10-10 00:00:00 |             34.9997 |           1 | 252 |         |
| 2020-11-09 00:00:00 |             33.6505 |           1 | 252 |         |
| 2020-12-09 00:00:00 |             31.8429 |           1 | 252 |         |
| 2021-01-08 00:00:00 |             29.3269 |           1 | 252 |         |
| 2021-02-07 00:00:00 |             29.886  |           1 | 252 |         |
| 2021-03-09 00:00:00 |             30.3694 |           1 | 252 |         |
| 2021-04-08 00:00:00 |             30.3883 |           1 | 252 |         |

## Interpretation Discipline

- Shapley R2 is a predictive attribution diagnostic over specified blocks; it
  does not prove economic causality.
- FEVD order sensitivity records how much VAR accounting depends on variable
  ordering.
- The CUSUM figures are residual diagnostics and are not labeled Bai-Perron.
- The robustness grid shows whether BTC model fit is stable across reasonable
  settings; unstable cells are evidence to discuss limitations, not to hide.
