# Visual Quality Check

Generated at: 2026-06-16T19:04:26.041744+00:00

## Final Figures

| Figure | PNG | SVG | Dimensions | Size KB | Dark theme |
|---|---:|---:|---:|---:|---:|
| F00_project_summary_card.png | True | True | 1600x900 | 21.6 | False |
| F01_data_coverage.png | True | True | 1600x900 | 68.2 | False |
| F02_btc_block_attribution.png | True | True | 1600x900 | 96.7 | False |
| F03_btc_etf_lead_lag.png | True | True | 1600x900 | 39.1 | False |
| F04_btc_rolling_correlations.png | True | True | 1600x900 | 190.6 | False |
| F05_stablecoin_supply_tvl.png | True | True | 1600x900 | 153.0 | False |
| F06_btc_native_dashboard.png | True | True | 1600x900 | 91.6 | False |
| F07_connectedness.png | True | True | 1600x900 | 100.1 | False |
| F08_robustness_grid.png | True | True | 1600x900 | 42.5 | False |
| F09_key_results_cards.png | True | True | 1600x900 | 72.6 | False |
| T00_key_results_table.png | True | True | 1600x900 | 77.5 | False |

## README Link Rules

- README image paths point to `outputs/figures/`.
- README does not point to archived portfolio release folders.
- F00-F09 are generated as both PNG and SVG.

## Dashboard

`outputs/dashboard/index.html` is a standalone static HTML dashboard built from
generated PNGs. Plotly/Kaleido is not required for the public static release.

## Known Visual Limitations

- F06 uses public ablation and correlation tables rather than a hidden raw
  native z-score time series, so it is a dashboard-style native summary instead
  of a dense line-z-score plot.
- F04 links to both rolling-correlation and pre/post delta outputs because the
  visual story uses rolling correlations while the public table also includes
  event deltas.
- All visuals remain reduced-form research artifacts and avoid causal claims.
