# Figure Gallery

## README Candidates

### F10 BTC Block Partial R2

![BTC block partial R2](../portfolio_v2_1/figures/F10_btc_block_partial_r2_heatmap.png)

- Source table: `block_partial_r2_btc.csv`
- Model card: `block_partial_r2.md`
- Interpretation: BTC fit is heavily influenced by MVRV-like valuation state.
- Limitation: full-vs-reduced block partial R2 is not Shapley/Owen.
- README: yes

### F22 BTC ETF Lead-Lag

![BTC ETF lead-lag](../portfolio_v2_1/figures/F22_btc_etf_lead_lag_heatmap.png)

- Source table: `etf_lead_lag_btc.csv`
- Model card: `etf_flow_lead_lag.md`
- Interpretation: ETF-flow intensity has strong contemporaneous association.
- Limitation: daily timing is simultaneity-prone.
- README: yes

### F30 BTC Rolling Correlations

![BTC rolling correlations](../portfolio_v2_1/figures/F30_btc_rolling_correlations_180d.png)

- Source table: `rolling_correlations.csv`
- Model card: `rolling_correlations.md`
- Interpretation: rolling co-movement regimes shift over time.
- Limitation: correlation is descriptive, not causal.
- README: yes

### F40 Stablecoin Supply And TVL

![Stablecoin supply and TVL](../portfolio_v2_1/figures/F40_stablecoin_supply_and_tvl.png)

- Source table: `stablecoin_liquidity_features.csv`
- Model card: `stablecoin_liquidity.md`
- Interpretation: stablecoins and TVL provide liquidity context.
- Limitation: supply growth is a proxy, not an identified shock.
- README: yes

### F50 BTC Native Z-Score Dashboard

![BTC native dashboard](../portfolio_v2_1/figures/F50_btc_native_zscore_dashboard.png)

- Source table: `native_factor_registry.csv`
- Model card: `btc_native_factor_lab.md`
- Interpretation: native variables can be compared as standardized state.
- Limitation: MVRV can mechanically co-move with BTC price.
- README: yes

## Supporting Figures

| Figure | What it shows | README |
|---|---|---|
| `F11_eth_block_partial_r2_heatmap.png` | ETH block attribution comparison | Optional |
| `F12_btc_ablation_waterfall.png` | BTC nested ablation | Optional |
| `F13_eth_ablation_waterfall.png` | ETH nested ablation | Optional |
| `F20_btc_etf_flow_intensity_timeline.png` | BTC ETF intensity timeline | Optional |
| `F21_eth_etf_flow_intensity_timeline.png` | ETH ETF intensity timeline | Optional |
| `F60_baseline_fevd_compact_heatmap.png` | VAR/FEVD connectedness | Yes |
| `F61_baseline_event_study_cars.png` | Event-study CARs | Optional |
| `F62_baseline_data_coverage.png` | Panel coverage | Yes |
