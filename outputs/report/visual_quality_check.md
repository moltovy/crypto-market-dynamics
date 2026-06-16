# Visual Quality Check

Generated at: 2026-06-16T18:04:08.633635+00:00

## Final Figures

| Figure | PNG | SVG | Dimensions | Size KB | Dark theme |
|---|---:|---:|---:|---:|---:|
| F00_project_summary_card.png | True | True | 1600x900 | 108.5 | True |
| F01_data_coverage.png | True | True | 1600x900 | 106.0 | True |
| F02_btc_block_attribution.png | True | True | 1600x900 | 126.2 | True |
| F03_btc_etf_lead_lag.png | True | True | 1600x900 | 75.2 | True |
| F04_btc_rolling_correlations.png | True | True | 1600x900 | 215.5 | True |
| F05_stablecoin_supply_tvl.png | True | True | 1600x900 | 182.1 | True |
| F06_btc_native_dashboard.png | True | True | 1600x900 | 129.0 | True |
| F07_connectedness.png | True | True | 1600x900 | 134.5 | True |
| F08_robustness_grid.png | True | True | 1600x900 | 77.1 | True |
| F09_key_results_cards.png | True | True | 1600x900 | 128.6 | True |
| T00_key_results_table.png | True | True | 1600x900 | 130.4 | True |

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
