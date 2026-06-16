# Portfolio v2.2 Data Atlas

This v2.2 atlas inherits the frozen v2.1 panel and adds advanced diagnostic table coverage. Raw `Data/` files are not modified.

- Date range: `2020-01-01` through `2026-04-11`
- Rows: `2293`
- Columns: `63`
- Source inventory rows: `490`

## Source Inventory

| source           |   files |    rows |
|:-----------------|--------:|--------:|
| CryptoQuant      |     345 | 1181712 |
| Artemis          |      48 |   75302 |
| Tradingview      |      44 |   92157 |
| DefiLlama        |      28 |  306856 |
| FRED             |      21 |  166529 |
| Farside ETF Data |       3 |    1032 |
| AlternativeMe    |       1 |    2994 |

## Advanced Table Coverage

| table                          |   rows |   columns |
|:-------------------------------|-------:|----------:|
| pca_block_loadings             |     32 |         4 |
| pca_explained_variance         |     10 |         4 |
| pca_factor_panel_summary       |     10 |         9 |
| pca_static_ols                 |     22 |        10 |
| shapley_r2_btc                 |      6 |         8 |
| rolling_shapley_r2_btc_180d    |    354 |        11 |
| shapley_r2_eth                 |      5 |         8 |
| rolling_shapley_r2_eth_180d    |    230 |        11 |
| cusum_summary                  |      2 |         7 |
| cusum_paths                    |   4582 |         3 |
| fevd_order_sensitivity         |     64 |         8 |
| fevd_order_sensitivity_summary |     16 |         6 |
| rolling_connectedness          |     68 |         8 |
| robustness_grid                |    108 |         9 |

## Data Policy

Portfolio v2.2 uses only the frozen committed panel and derived feature transforms. No raw `Data/` file is modified and no live or paid source is required for regeneration.
