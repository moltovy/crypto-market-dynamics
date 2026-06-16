# Visual Triage

## Current Figures Evaluation

| Figure | Decision | Reason | New Design |
|---|---|---|---|
| F00_project_summary_card | Remove | Text-heavy summary, unnecessary if README describes the project well. | N/A |
| F01_data_coverage | Replace -> F01 | Shows mere file counts instead of actual coverage timeframe. | Gantt-style timeline covering source families. |
| F02_btc_block_attribution | Replace -> F02 | MVRV dominates visually; "static block removal" is confusingly labeled. | Model ablation/sensitivity chart (horizontal bar/waterfall) showing $R^2$ with and without MVRV. |
| F03_btc_etf_lead_lag | Replace -> F03 | Cluttered and uses a heatmap for a 1D result. | Lollipop chart / point-range of HAC t-stats by lag. |
| F04_btc_rolling_correlations | Replace -> F04 | Too many lines in one panel; ETH dominates; messy legend. | 2x2 small multiples (BTC-ETH, BTC-SPY, BTC-VIX, BTC-Gold/DXY). |
| F05_stablecoin_supply_tvl | Replace -> F05 | Scale is broken because DeFi TVL index dominates Stablecoins. | Two indexed/log scale panels separated vertically. |
| F06_btc_native_dashboard | Move to Gallery -> G01 | Highly technical correlation matrix; MVRV vs non-MVRV dominance is better shown in F02. | Mask diagonal in correlation matrix. Rename labels. |
| F07_connectedness | Replace -> F06 (Composite) | Diagonal FEVD values dominate, hiding the spillovers. | Combine rolling connectedness with MVRV robustness. |
| F08_robustness_grid | Move to Gallery -> G02 | Visual grid is boring and repetitive. | Clean with/without MVRV sensitivity chart (combined into F06). Full grid goes to gallery. |
| F09_key_results_cards | Remove | Redundant given README structure. | N/A |
| T00_key_results_table | Remove | Redundant given CSV tables and README summary. | N/A |

## Final README Figures
- F01_data_inventory.png
- F02_btc_model_sensitivity.png
- F03_etf_flow_lead_lag.png
- F04_rolling_correlations.png
- F05_liquidity_context.png
- F06_connectedness_and_robustness.png

## Supporting Gallery Figures
- G01_native_state_detail.png (Correlation matrix)
- G02_full_robustness_grid.png (Original F08)
- G03_fevd_matrix.png (Original F07 matrix)
- G04_data_coverage_detail.png
- G05_stablecoin_volatility_detail.png

## Note on Old "Static Block Removal"
The 77.5% figure in the old `F02` chart was technically correct—it represented the exact $\Delta R^2$ when the `BTC MVRV` variable was ablated from the full model (Full $R^2$ ~0.92, Reduced $R^2$ ~0.15). However, labeling it "static block removal" and graphing it in a way that made other components look completely empty was visually deceiving. It will now be properly framed as **MVRV Sensitivity**.
