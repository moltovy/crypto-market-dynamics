# Factor-block evolution in BTC and ETH around the spot-ETF regime shift

**Version 1.0 — 2026-04-19**  
**Sample:** 2020-01-01 through 2026-04-11 (2,293 UTC calendar days)  
**Code:** `cqresearch` v0.1 (reproducible via `uv sync` + `uv.lock`)  
**Data panel:** `reports/panels/master_daily.parquet` (63 columns in the 2026-04-19 build)  
**Tables:** `reports/tables/2026-04-19/`  
**Figures:** `reports/figures/2026-04-19/`

> **Scope.** v1.0 corrects v0.1 **labeling**, **calendar/config alignment**, **ETF intensity scaling**, adds a **pre-registered CryptoQuant-native block**, splits **calendar-day vs weekday** estimation, and promotes a **4-variable VAR/FEVD** primary with an **8-variable** appendix. Every quantitative claim below points to a CSV in `reports/tables/2026-04-19/` unless noted.

---

## 1. Executive summary

**Three headline facts (association and reduced-form only; no causal identification):**

1. **Chow tests do not support a single-date BTC factor break at the spot-ETF approval.** At 2024-01-11, Chow F≈0.79, p≈0.62 (`structural_breaks_summary.csv`). A **single-break sup-F** sweep (not full Bai–Perron) peaks at **2021-01-04** for BTC; permutation placebo p≈0.01 — evidence of a regime shift in the **2021** window, not uniquely at the ETF listing.
2. **Post-2024, ETF-flow intensity is a strong contemporaneous correlate** of BTC returns when scaled by **prior-day market cap** (USD flow ÷ USD mcap). The augmented regression reports R²≈0.24, n=821, with β≈46.1 on `btc_etf_intensity` and large HAC t (`etf_flow_regression.csv`). Interpret as **same-day correlation**; R1 lag structure in robustness shows **overshoot–revert** dynamics, consistent with simultaneity rather than causal “flow drives price.”
3. **The 2024 spot-ETF approval is better framed as compositional change than as a single structural break.** Rolling and block attributions remain useful; **rolling partial R²** figures use **drop-one marginal R²** (not Shapley).

**Volatility.** Lower realized volatility post-ETF **coexists** with the ETF era; it is **not** separately identified from confounding macro and liquidity conditions — avoid “patient flows dampen vol” as a mechanism claim.

---

## 2. Data and method provenance

### 2.1 Sources

v0.1 source table still applies (`reports/run_summaries/01_inspect_core_files.md`), plus **BTC/ETH market capitalization** and **CryptoQuant-native** series listed in `docs/specs/paper_1_native_metrics.yml`.

### 2.2 Calendar and mixed frequency

- Master index is **crypto-7** (every calendar day).  
- **TradFi / equity levels** use forward-fill with limit **`ffill_limit` from `config/calendars.yml`** (implemented in `align_to_master`; **no longer hardcoded** to 4 days).  
- **Flows vs returns:** semantics unchanged from v0.1 — weekend zeros for equities are structural; crypto trades 24/7.

**Headline regressions:** Run **both** `calendar=crypto7` (all days) and `calendar=weekday` (Mon–Fri) — see §4.2.

### 2.3 Feature construction

- **ETF intensity:** `btc_etf_intensity` = (Farside BTC ETF total flow, USD millions × 1e6) ÷ **BTC USD market cap at t−1**; same for ETH.  
- **Native block (BTC):** first differences of exchange net flow, miner→exchange flow, and MVRV — **pre-registered** in `docs/specs/paper_1_native_metrics.yml`.  
- Winsorization: 1st / 99th percentile on estimation sample (per `scripts/02_run_analyses.py`).

### 2.4 Inference

- HAC OLS: **Newey–West, 5 lags** (primary).  
- Structural breaks: **Chow** at ETF date; **sup-F** single unknown break; **placebo** permutations (see §5).  
- VAR/FEVD: statsmodels VAR; **Cholesky ordering = column order** in `var_fevd_meta*.json`.

---

## 3. Factor blocks (v1.0)

| Block | Regressors (BTC) | Notes |
|-------|------------------|-----|
| Macro | `DGS10_d1`, `DGS2_d1`, `VIXCLS_d1`, `DTWEXBGS_d1`, `DFF_d1` | |
| Institutional | `spy_ret`, `qqq_ret`, `gld_ret` | |
| Liquidity | `defi_tvl_usd_ret`, `stables_total_usd_ret` | |
| Sentiment | `fng_value_d1` | |
| BTC-native | `cme_btc_basis_close_d1`, `btc_exchange_netflow_d1`, `btc_miner_to_exchange_flow_d1`, `btc_mvrv_d1` | Basis + pre-registered CQ metrics |

ETF flows enter **separate** augmented specs (`etf_flow_regression.csv`), not the nested block table.

---

## 4. Results

### 4.1 Descriptives

Unchanged logic from v0.1; refreshed numbers in `descriptive_stats.csv` (2026-04-19 folder).

### 4.2 Static OLS — calendar comparison (Table A, `static_ols_pre_post_etf.csv`)

Model R² is repeated on each coefficient row; filter to `regressor == const` for one row per (asset, sample, calendar).

| Asset | Calendar | Sample | Approx. R² | n (const row) |
|-------|----------|--------|------------|---------------|
| BTC | crypto7 | post_etf | **0.971** | 730 |
| BTC | weekday | post_etf | **0.971** | 530 |
| ETH | crypto7 | post_etf | **0.214** | 549 |

**Interpretation.** The BTC specification including **MVRV** and the native block achieves **very high** in-sample R² — **dominated by valuation co-movement** (`btc_mvrv_d1` t-statistics are large). That **does not** validate a “macro ETF” story; it requires **cautious** language on economic meaning. ETH post-ETF R² remains in the **~0.21** range without the same BTC valuation driver. For a **macro-focused** narrative, report an appendix specification **excluding** `btc_mvrv_d1` (future v1.1).

### 4.3 Structural breaks (`structural_breaks_summary.csv`)

| Asset | Chow F @ ETF | Chow p | sup-F | argmax date | placebo p |
|-------|--------------|--------|-------|-------------|-----------|
| BTC | 0.79 | 0.62 | 3.84 | 2021-01-04 | 0.01 |
| ETH | 2.12 | 0.025 | 4.11 | 2021-05-12 | 0.0033 |

**Label:** single-break **sup-F**, not Bai–Perron multi-break.

### 4.4 ETF flow regression (`etf_flow_regression.csv`)

Post-2024-01-11, HAC(5). **Intensity is flow ÷ prior mcap.** Coefficient ≈ **46.1** (t≈8.7). R²≈0.237. Same caveats as v0.1 on **identification**.

### 4.5 VAR / FEVD

- **Primary (4 variables):** `btc_ret`, `eth_ret`, `spy_ret`, `VIXCLS_d1` — Diebold–Yilmaz total connectedness **≈35.3%** (`var_fevd_meta_compact.json`, `fevd_10d_compact.csv`, Figure F07).  
- **Appendix (8 variables):** connectedness **≈27.3%** (`var_fevd_meta.json`, `fevd_10d.csv`, Figure F07b).  
Order sensitivity: see `cholesky_note` in each JSON.

### 4.6 Event studies (`event_studies.csv`; Figure F08)

Market model with SPY benchmark. **Placebo p-values** (`placebo_p_m5_p5`) compare the CAR to **200 random event dates** using the **[-5,+5]** window only — **the same p-value is repeated across window rows**; do **not** read [-1,+1] or [0,+30] CARs as sharing that placebo definition.

---

## 5. Robustness (`reports/tables/2026-04-19/robustness/`)

R1–R6 structure unchanged from v0.1; coefficients **scale** with the new intensity definition — cite **current** CSVs.

**Structural-break placebo:** y-shuffle preserves X covariance but not serial correlation; block bootstrap noted as future work.

---

## 6. Limitations (v1.0)

1. **No causal identification** for flows, volatility, or factor loadings.  
2. **MVRV / native metrics** can dominate BTC static fit — separate macro/TradFi claims from “full stack” R².  
3. **Multiple testing** across assets and events (e.g. ETH Chow p≈0.025) — Bonferroni or FDR should be mentioned in journal submission.  
4. **FEVD** depends on Cholesky ordering; primary vs appendix document two orders.  
5. **Event-study placebo** window fixed at [-5,+5] for the reported p-value.

---

## 7. Related literature (placeholders)

*To be filled with verified citations only — no fabricated references.* Suggested clusters: spot ETF literature, crypto factor models, market microstructure of crypto ETFs, structural break tests (Andrews, Bai–Perron).

---

## 8. Reproducibility

```bash
python scripts/01_build_master_panel.py
python scripts/02_run_analyses.py
python scripts/04_descriptives_and_summaries.py
python scripts/05_robustness.py
python scripts/03_make_figures.py
```

Or use `uv sync` then the same commands in the locked environment.

---

*End of v1.0 draft.*
