# Feature Strength Methodology Audit

## 1. BTC Attribution Audit

### What the existing statistics mean

| Statistic | Definition | Value (BTC full sample) | Source |
|-----------|-----------|------------------------|--------|
| Full model R² | 1 − RSS_full / TSS with all blocks | 0.921 | T03 row 2 |
| Reduced R² (without MVRV) | 1 − RSS_reduced / TSS after removing MVRV block | 0.146 | T03 row 7 |
| Block partial R² (MVRV) | (RSS_reduced − RSS_full) / TSS | 0.775 | T03 row 7 |
| MVRV-only standalone R² | OLS of btc_ret ~ btc_mvrv_d1 only | 0.912 | T07 row N2 |
| Native-ex-MVRV standalone R² | OLS of btc_ret ~ basis + netflow + miner | 0.004 | T07 row N1 |

### Why the old F02 chart was wrong

The previous `render_f02()` in `make_hero_figures.py` (lines 86–107) created a
horizontal bar chart with these entries:

- "Full model" → full_r2 = 0.921 (a model R²)
- "Without MVRV" → reduced_r2 = 0.146 (a model R²)
- "Native ex-MVRV" → partial_r2 ≈ 0.0002 (a block contribution ΔR²)
- "MVRV only" → partial_r2 ≈ 0.775 (a block contribution ΔR²)
- "Macro + TradFi + Liquidity" → sum of partial_r2 ≈ 0.003 (a summed ΔR²)

These are **three different statistics** displayed on one axis:

1. Standalone/full model R² (full model, without MVRV)
2. Block partial R² = ΔR² from removing a block (MVRV, native-ex-MVRV)
3. Sum of block partial R² values (Macro + TradFi + Liquidity)

The label "MVRV only = 0.775" was misleading. It is **not** the MVRV-only model
R² (which is 0.912). It is the drop in full-model R² when MVRV is removed:
0.921 − 0.146 = 0.775.

### Correct presentation

Two separate panels:

**Panel A — Standalone model R² (same-support):** Full-with-MVRV, Full-ex-MVRV,
MVRV-only, Native-ex-MVRV-only, Macro+TradFi+Liquidity. All on same rows.

**Panel B — Block ΔR² (incremental contribution):** BTC MVRV, TradFi,
Liquidity, Macro, Native-ex-MVRV. These show how much R² drops when each block
is removed from the full model.

---

## 2. Native ex-MVRV Audit

**Variables:** `cme_btc_basis_close_d1`, `btc_exchange_netflow_d1`,
`btc_miner_to_exchange_flow_d1`.

**Standalone R²:** 0.004 (T07 row N1, n=1942).

**Is this a bug?** No. The native correlation table (T07) confirms:

| Feature | Correlation with btc_ret |
|---------|------------------------|
| cme_btc_basis_close_d1 | 0.048 |
| btc_exchange_netflow_d1 | −0.012 |
| btc_miner_to_exchange_flow_d1 | −0.029 |
| btc_mvrv_d1 | 0.955 |

CME basis, exchange netflow, and miner-to-exchange flow have near-zero
contemporaneous correlation with daily BTC returns. This is a genuine result:
these flow variables do not explain daily BTC returns in the current linear
same-day specification.

**Note on sample sizes:** Native-ex-MVRV uses n=1,942 while MVRV-only uses
n=2,292. This means R² comparisons are partly sample-composition. The
same-support ablation tables (T19) will resolve this.

---

## 3. Data Inventory Audit

**Problem:** `T01_source_inventory.csv` is a raw copy of `MASTER_DATA.csv`
(128KB, the entire data atlas file). The figure script groups this by `source`
column to compute file counts and date ranges, but the mapping can produce
incorrect aggregations if the source column is not clean.

**Known issue:** The data atlas reports CryptoQuant=345 files, Artemis=48,
TradingView=44, DefiLlama=28, FRED=21, Farside=3, AlternativeMe=1. If the
figure shows different counts, the source column mapping is stale.

**Fix:** Replace the Gantt timeline figure with a clean source summary table
or compact inventory chart. Remove ETF event lines from the data inventory
figure.

---

## 4. Modeling Interpretation Audit

| Result | Classification |
|--------|---------------|
| Full-model R² | Contemporaneous exposure diagnostic |
| Block partial R² | Contemporaneous attribution diagnostic |
| ETF lead-lag coefficients | Lead-lag association diagnostic |
| Rolling correlations | Descriptive co-movement |
| Stablecoin/TVL features | Descriptive context (liquidity proxy) |
| Native factor ablation | Contemporaneous exposure diagnostic |
| Chow test | Structural-break diagnostic |
| Sup-F sweep | Structural-break diagnostic |
| VAR/FEVD connectedness | Reduced-form spillover diagnostic |
| Robustness grid | Sensitivity diagnostic |

**None of these are causal identification.** All should be labeled as
reduced-form diagnostics, association, or exposure. ETF-flow results must
explicitly note that daily timing prevents causal interpretation.
