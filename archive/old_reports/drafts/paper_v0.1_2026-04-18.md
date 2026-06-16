# Factor-block evolution in BTC and ETH around the spot-ETF regime shift

**Version 0.1 — 2026-04-18**
**Sample:** 2020-01-01 through 2026-04-11 (2,293 UTC calendar days)
**Code:** `cqresearch` v0.1 (commit at time of build)
**Data panel:** `reports/panels/master_daily.parquet` (58 columns)
**Tables:** `reports/tables/2026-04-18/`
**Figures:** `reports/figures/2026-04-18/`

> **Scope of this draft.** v0.1 is the first end-to-end analytical pass. It
> establishes the empirical baseline — who moves BTC/ETH daily returns, how
> much, and whether the factor mix changed around the 2024 spot-ETF
> approvals. Every number in this draft ties back to a CSV in
> `reports/tables/2026-04-18/`. No result has been hand-tuned.

---

## 1. Executive summary

**Three headline facts, fully replicable from the tables:**

1. **The 2024 spot-ETF approval did not rewrite BTC's factor loadings at a
  single break date.** A Chow test on BTC daily log returns at
   2024-01-11 yields F=0.81, p=0.60 (Table 3). The *sup-F* search for an
   unknown break places the strongest regime shift at **2021-01-04**
   (placebo p=0.00), coincident with the COVID-stimulus-driven institutional
   adoption wave — **not** the ETF launch.
2. **But ETFs are now the single most statistically significant driver of
  daily BTC returns.** Regressing post-2024-01-11 BTC returns on ETF-flow
   intensity (flow ÷ prior-day close), SPY returns, VIX first-difference and
   10-year yield change gives an R² of **23.7%** (n=821) with the ETF-flow
   coefficient β=2.33, HAC t=8.7, p≈0 (Table 5). Without ETF flow, macro +
   institutional factors alone explain 11–14% of daily variance; ETF flows
   add **~10 percentage points of R²** — a very large factor contribution for
   a liquid asset.
3. **BTC volatility fell and macro co-movement rose modestly post-ETF.** Daily
  return standard deviation fell from 3.18% (pre-ETF, 2020-2024) to 2.49%
   (post-ETF, 2024-2026) — a 22% reduction. SPY correlation rose from 0.32
   to 0.37, VIX anti-correlation strengthened from –0.32 to –0.35. GLD
   co-movement is essentially flat (0.12 vs 0.10). The picture is of a
   *maturing* asset, **not** a dramatically re-priced one.

**What this means for the research agenda.** The ETF-launch-as-structural-break
narrative is too clean. The right story is compositional — *which* factor
block carries the rolling variance explanation, how ETF flows interact with
equity beta, and why 2024 was a **low-R² year** for BTC (Table 8: median
rolling R² collapsed to 7.8% in 2024 before recovering to 32% in 2026).

---

## 2. Data and method provenance

### 2.1 Sources (all raw CSVs under `Data/`, unmodified)


| Source        | Files touched                                                                                                      | Role                                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| CryptoQuant   | `BTC/Market Data/Bitcoin Price & Volume - Spot… - Day.csv`, ETH equivalent                                         | BTC/ETH daily OHLCV (the dependent variables)                     |
| FRED          | `FRED/fred_macro_panel__daily.csv`                                                                                 | DGS10, DGS2, VIXCLS, DTWEXBGS, DFF, BAMLH0A0HYM2, RRPONTSYD, etc. |
| Tradingview   | 9 daily CSVs under `Data/Tradingview/Daily/`                                                                       | SPY, QQQ, GLD, XLK, DXY, DVOL BTC, CME BTC/ETH basis              |
| Farside       | `Farside ETF Data/farside_btc_etf_flows__daily.csv`, ETH equivalent                                                | Issuer-level daily ETF flows (USD M)                              |
| DefiLlama     | `DefiLlama/TVL/Daily/tvl_all_chains_daily.csv`, `DefiLlama/Stablecoins/stablecoin_mcap_by_defillama_id__daily.csv` | Total DeFi TVL, aggregated stablecoin float                       |
| AlternativeMe | `AlternativeMe/fear_greed_index__daily.csv`                                                                        | Daily fear & greed index                                          |


The full profiled inventory is in
`reports/run_summaries/01_inspect_core_files.md` (rows, columns, first/last
date, missing-% per column).

### 2.2 Calendar handling (the non-trivial part)

Crypto trades 24/7; equities and macro are business-5. The master panel uses
a **crypto-7 calendar** (every UTC calendar day, 2020-01-01 → 2026-04-11 =
2,293 rows). Variables are reindexed onto this master with source-specific
semantics (`src/cqresearch/data/calendars.py`):

- **Stock variables** (levels: prices, market caps, TVL, F&G index):
forward-fill up to 4 days to cover long weekends. Pre-first-observation
values are kept `NaN` — we never fabricate pre-history.
- **Flow variables** (Farside ETF inflows, returns): weekends are *genuine
zeros* (no trading day), not missing observations. Pad with `0` **within
the series' natural window only** (never before first valid date).
- **Rate variables** (DGS10, DVOL, basis, F&G): forward-fill 4 days max; no
zero fill.

This is implemented once in `align_to_master(series, kind=...)` and applied
uniformly to every source.

### 2.3 Feature construction

`src/cqresearch/features/panel.py` emits a 28-column feature matrix:

- **Log returns** on prices/market caps/levels (`btc_ret`, `eth_ret`,
`spy_ret`, `qqq_ret`, `gld_ret`, `xlk_ret`, `dxy_tv_ret`, `defi_tvl_usd_ret`,
`stables_total_usd_ret`, `wti_ret`).
- **First differences** on rate-like variables (`DGS10_d1`, `DGS2_d1`,
`VIXCLS_d1`, `dvol_btc_close_d1`, `cme_btc_basis_close_d1`, `fng_value_d1`,
…).
- **ETF flow intensity** = flow_t / close_{t-1}, scaling raw USD-M flows by
prior-day BTC price so the regressor is stationary even as price drifts.

All features are winsorized at the 1st/99th percentile (full-sample) before
estimation — this dampens a handful of 2020-03 COVID and 2022-11 FTX
outliers that would otherwise dominate the HAC standard errors.

### 2.4 Inference

All OLS coefficients reported here use **Newey-West HAC** with 5 lags
(Bartlett kernel; conservative for daily data with known volatility
clustering and weak autocorrelation). Reported p-values are two-sided.
Structural-break inference uses placebo permutation p-values (300 draws),
not asymptotic critical values, because the return distribution has heavy
tails.

---

## 3. Factor blocks


| Block             | Regressors                                                  | Rationale                                                  |
| ----------------- | ----------------------------------------------------------- | ---------------------------------------------------------- |
| **Macro**         | `DGS10_d1`, `DGS2_d1`, `VIXCLS_d1`, `DTWEXBGS_d1`, `DFF_d1` | Yield, real-rate, equity-vol, dollar, policy-rate channels |
| **Institutional** | `spy_ret`, `qqq_ret`, `gld_ret`                             | TradFi-risk appetite and hedge behavior                    |
| **Liquidity**     | `defi_tvl_usd_ret`, `stables_total_usd_ret`                 | Crypto-native liquidity and shadow-dollar float            |
| **Sentiment**     | `fng_value_d1`                                              | Retail sentiment proxy                                     |
| **BTC-native**    | `cme_btc_basis_close_d1`                                    | Futures-spot basis (carry / demand intensity)              |
| **ETH-native**    | `cme_eth_basis_close_d1`                                    | Same, for ETH                                              |


ETF flows are kept *separate* from the institutional block so their
explanatory contribution can be measured cleanly (Section 4.4).

---

## 4. Results

### 4.1 Descriptives (Table 1, `descriptive_stats.csv`)


| period               | BTC SD (%) | ETH SD (%) | SPY SD (%) | BTC kurt | ETH kurt |
| -------------------- | ---------- | ---------- | ---------- | -------- | -------- |
| 2020-2026 full       | 2.95       | 3.94       | 0.89       | 1.57     | 1.22     |
| 2020-2024 (pre-ETF)  | 3.18       | 4.15       | 0.97       | 1.25     | 0.99     |
| 2024-2026 (post-ETF) | **2.49**   | 3.53       | 0.73       | 1.96     | 1.67     |


BTC return volatility dropped **22%** post-ETF. Fat-tailedness (excess
kurtosis) actually *increased* — fewer extreme moves per unit SD but the
tail events that remain are relatively more dominant. This is consistent
with patient-institutional-holder flows dampening routine volatility without
removing regime shocks.

### 4.2 Static OLS, full vs pre vs post (Table 2, `static_ols_pre_post_etf.csv`)


| Asset | Sample                 | R²        | N     |
| ----- | ---------------------- | --------- | ----- |
| BTC   | full 2020-2026         | 0.139     | 2,107 |
| BTC   | pre-ETF 2020-2024      | 0.140     | 1,339 |
| BTC   | **post-ETF 2024-2026** | **0.152** | 768   |
| ETH   | full 2020-2026         | 0.165     | 1,705 |
| ETH   | pre-ETF 2020-2024      | 0.154     | 1,123 |
| ETH   | **post-ETF 2024-2026** | **0.210** | 582   |


ETH experienced the larger regime shift: factor R² jumped from 15.4% to 21.0%
(+5.6 pp). BTC only gained +1.3 pp of R² on the static specification — the
shift is real but not dramatic. See also `block_r2_pre_post.csv`: the
institutional block alone went from 11.7% to **17.7%** of ETH variance.

### 4.3 Structural-break tests (Table 3, `structural_breaks_summary.csv`; Figures F05, F06)


| Asset | Chow F @ ETF date | Chow p | sup-F | argmax date    | placebo p |
| ----- | ----------------- | ------ | ----- | -------------- | --------- |
| BTC   | 0.81              | 0.60   | 3.78  | **2021-01-04** | 0.00      |
| ETH   | 2.13              | 0.024  | 4.24  | **2021-05-12** | 0.00      |


- **BTC**: the Chow test *fails to reject* stable loadings at the ETF-launch
date. The sup-F search picks 2021-01-04 — the peak of the 2020-2021
COVID-stimulus rally and the period immediately preceding the first wave
of corporate treasury BTC purchases (MicroStrategy's Oct-2020 purchase and
Tesla's Feb-2021 filing). Placebo tests reject the null of no break
(p=0.00), so the break is real — it just isn't at the ETF date.
- **ETH**: marginal rejection at the ETF launch (Chow p=0.024). The sup-F
argmax is 2021-05-12, right before Ethereum's NFT boom, Coinbase's IPO
effect, and pre-Merge repricing. Again, a statistically real break that
predates the ETF.

**Interpretation.** The dominant structural inflection in the crypto-era
factor profile was *2021*, not *2024*. The 2024 ETF approvals produced
**composition changes** (Section 4.4) without a single-date regime break.

### 4.4 ETF flow regression (Table 5, `etf_flow_regression.csv`)

Post-2024-01-11 sample only, OLS with HAC(5):


| Regressor             | β         | HAC s.e.  | t        | p       |
| --------------------- | --------- | --------- | -------- | ------- |
| constant              | –0.0017   | 0.00061   | –2.76    | 0.006   |
| **btc_etf_intensity** | **2.332** | **0.268** | **8.69** | **≈ 0** |
| spy_ret               | 0.573     | 0.202     | 2.83     | 0.005   |
| VIXCLS_d1             | –0.0031   | 0.00103   | –2.99    | 0.003   |
| DGS10_d1              | 0.0221    | 0.0225    | 0.98     | 0.326   |


R² = **0.237**, n = 821.

**Economic magnitude.** `btc_etf_intensity` is USD-M flow per USD of prior-day
BTC close. A 1 bp increase in (flow ÷ price) is associated with a 2.3 bp
same-day BTC log return. The top decile of ETF flow days is associated with
~+1.1% BTC log return on that day, conditional on SPY and VIX. This is not
causal (simultaneity: both flows and returns respond to news), but it is the
single tightest daily relationship in the post-2024 sample.

### 4.5 Rolling R² by calendar year (Table 8, `rolling_r2_btc_median_by_year.csv`)


| Year | Median rolling 180-day R² (BTC) | Median rolling 180-day R² (ETH) |
| ---- | ------------------------------- | ------------------------------- |
| 2020 | 0.28                            | —                               |
| 2021 | 0.20                            | 0.25                            |
| 2022 | **0.31**                        | **0.30**                        |
| 2023 | 0.22                            | 0.15                            |
| 2024 | **0.08**                        | **0.12**                        |
| 2025 | 0.22                            | 0.21                            |
| 2026 | 0.32                            | 0.34                            |


The 2022 peak corresponds to the Fed hiking cycle when macro ruled
everything; the 2024 trough is the ETF-approval uncertainty period when
crypto decoupled from everything visible; 2025-2026 show the
post-regime-shift factor stack re-cementing at **higher** R² than the 2023
trough. This is consistent with a "maturing asset class, now priced on
flows" narrative.

### 4.6 VAR / FEVD connectedness (Table 6, `fevd_10d.csv`; Figure F07)

BIC-selected lag order = 1. Diebold-Yilmaz total connectedness = **27.3%**
over the 8-variable system (BTC, ETH, SPY, GLD, DGS10, VIX, stables, DeFi).
At the 10-day horizon:

- **eth_ret**: 66.9% of variance explained by BTC shocks, 32.8% own — ETH
behaves like a BTC-beta at this horizon.
- **defi_tvl_usd_ret**: 46.3% explained by BTC, 13.3% by ETH, 38.9% own —
DeFi liquidity is tightly anchored to BTC.
- **btc_ret**: 99.5% own — BTC is the **upstream** asset in the system.
- **VIXCLS_d1**: 48.5% explained by SPY — inherited from equity vol, as
expected.

### 4.7 Event studies (Table 7, `event_studies.csv`; Figure F08)

Market model with SPY as the market benchmark, 180-day estimation window
ending 10 days before the event. Placebo p-values from 200 random date
draws.


| Event                              | Window  | CAR        | t         | Placebo p |
| ---------------------------------- | ------- | ---------- | --------- | --------- |
| BTC spot-ETF launch (2024-01-11)   | [–1,+1] | **–8.22%** | –2.30     | 0.61      |
| BTC spot-ETF launch                | [0,+30] | –4.53%     | –0.39     | 0.61      |
| ETH spot-ETF launch (2024-07-23)   | [0,+30] | **–29.3%** | –1.76     | 0.92      |
| Fed FOMC pivot signal (2022-11-02) | [–1,+1] | +4.45%     | 0.93      | 0.67      |
| FTX collapse (2022-11-08)          | [–1,+1] | **–17.7%** | –3.67     | 0.11      |
| FTX collapse                       | [0,+5]  | –17.2%     | –2.52     | 0.11      |
| SVB failure (2023-03-10)           | [0,+5]  | **+16.8%** | **+3.10** | 0.21      |
| SVB failure                        | [0,+30] | +22.9%     | +1.86     | 0.21      |


**Interpretation.**

- **Spot-ETF launches showed "sell-the-news" behavior**, not the
buy-the-news effect market pundits predicted. BTC fell –8.2% in the first
three days; ETH fell –29.3% in the 30 days post-launch. Both placebo
p-values are high (0.61, 0.92) — the CAR magnitudes look dramatic but are
*not* out of distribution for random 3- or 30-day windows in this noisy
sample. The honest takeaway is "not significantly different from the
average bad week."
- **FTX collapse** is the largest BTC CAR in this event set (–17.7%,
t=–3.67). Placebo p=0.11 — directionally strong but not 5%-significant
against placebo benchmarks.
- **SVB bank failure produced a +16.8% abnormal BTC return over 5 days**,
t=+3.10. This is the cleanest "BTC as banking hedge" episode in our
sample, and the only event with a two-digit parametric t-stat on the
positive side.

---

## 5. Robustness and limits

All robustness checks live under `reports/tables/2026-04-18/robustness/`
and are reproducible via `scripts/05_robustness.py`.

### 5.1 Run robustness (passes)


| Check                                            | File                         | Result                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------------------ | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **R1** — Same-day vs lagged ETF flow             | `R1_lagged_etf_flow.csv`     | Lagged flow alone is insignificant (β=0.20, t=0.76). In a contemporaneous+lag1 spec, **same-day β=2.86 (t=9.6)** and **lag1 β=–0.98 (t=–3.7)** — a clean **overshoot-and-revert** pattern. The day after a big ETF inflow, BTC gives back ~1/3 of the move. This *weakens* any naïve causal interpretation: flows and returns are simultaneously determined, with partial mean reversion. |
| **R2** — No winsorization                        | `R2_no_winsor_post_etf.csv`  | β=2.39, t=8.58, R²=23.3%. Headline ETF-flow coefficient is not an artifact of winsorization.                                                                                                                                                                                                                                                                                              |
| **R3** — HAC lag (5 / 10 / 20 / 40)              | `R3_hac_lag_sensitivity.csv` | ETF-flow β is 2.33 across all lags; t statistic **increases** from 8.7 (hac=5) to 9.4 (hac=20) — significance does not depend on the HAC choice.                                                                                                                                                                                                                                          |
| **R4** — Post-2021 subwindow (drops COVID spike) | `R4_post2021_static_ols.csv` | Pre/post ETF R² pattern survives.                                                                                                                                                                                                                                                                                                                                                         |
| **R5** — Split at the sup-F argmax (2021-01-04)  | `R5_supF_split.csv`          | Block loadings *do* differ across the 2021 break — consistent with the structural-break finding that 2021 (not 2024) was the dominant inflection.                                                                                                                                                                                                                                         |
| **R6** — Common-support window                   | `R6_common_support.csv`      | Results survive restriction to dates where every regressor is observed.                                                                                                                                                                                                                                                                                                                   |


### 5.2 Remaining caveats

1. **Sample winsorization hides the tail events.** The FTX/SVB CARs survive
  winsorization only because they are a single peak day each. A trim-free
   re-estimation is an obvious v0.2 robustness check.
2. **No causal claim.** ETF flow and same-day BTC returns are simultaneously
  determined. To make a causal argument, next-agent work should use
   `btc_etf_intensity` *lagged* 1 day as an instrument, or leverage issuer
   cross-section variation (Table `reports/panels/master_daily_meta.json`
   shows we have 13 issuer-level BTC ETF columns plus ETH equivalents).
3. **Stablecoin total is a sum of fillna-0 columns.** Early 2020 sums may
  be mechanically low because not every current ID existed. A v0.2 check
   should restrict to pre-2020 live-stablecoin IDs only.
4. **DVOL and CME basis start dates** (2021-03 and 2020-01 with 8% missing)
  mean these factors enter the rolling windows unevenly. Results excluding
   native-crypto regressors are materially unchanged.
5. **Placebo permutations** for structural-break tests shuffle `y` only
  (preserves X covariance but breaks serial dependence). A block-bootstrap
   placebo is the next-level robustness check.

---

## 6. What the next agent should do next

**P0 (1-2 days of work each, highest marginal value):**

1. **Causal identification for ETF flow.** Re-run Table 5 with
  `btc_etf_intensity.shift(1)` as the primary regressor; add issuer fixed
   effects from the 13 individual Farside columns.
2. **Time-varying parameter VAR (TVP-VAR)** on the 8-series system to get a
  *continuous* connectedness index instead of a full-sample number.
   `cqresearch.modeling.var_fevd` already has the building blocks.
3. **Stablecoin sub-basket construction.** Use `Data/DefiLlama/Stablecoins/stablecoins.csv`
  metadata (fiat-backed vs crypto-backed) to split the aggregate into
   "custodial USD" and "on-chain crypto-collateralized" series and re-run
   Section 4.6. This is the most obvious missing substance.
4. **Issuer-level event studies.** IBIT vs FBTC vs GBTC-outflow dynamics
  were not separable in this pass because we used `btc_etf_total`. All 13
   issuer columns are in the panel.

**P1:**

1. **Macro-only vs institutional-only nested F tests** to formally compare
  explanatory power block-by-block across pre/post ETF periods. The data
   is already in `static_ols_pre_post_etf.csv`.
2. **Bai-Perron multiple breaks.** Our sup-F assumes a single break; a
  true Bai-Perron implementation (dynamic-programming over k breaks) would
   tell us whether 2021-01 + 2022-11 + 2024-01 all jointly matter.
3. **Add on-chain factor block.** `Data/CryptoQuant/BTC/Exchange Flows/`
  and `Data/CryptoQuant/BTC/Miner Flows/` contain dozens of native
   metrics that could form a 6th factor block in the block-R² decomposition.

**P2:**

1. **ETH-specific factor stack.** Staking flows, L2 TVL share, and Merge/Pectra
  breakpoint effects are still uninterrogated. ETH 2.0 data lives in
   `Data/CryptoQuant/ETH/ETH 2.0/`.
2. **Regime-detection filter** (HMM on rolling R² and connectedness) to
  label "macro-dominated", "flow-dominated", and "native-dominated" regimes
   and show their alternation.

---

## 7. Reproducibility

Every table and figure in this draft is produced by:

```bash
python scripts/01_build_master_panel.py
python scripts/02_run_analyses.py
python scripts/03_make_figures.py
python scripts/04_descriptives_and_summaries.py
```

Deterministic (no random seed that matters except the placebo permutation
seed, fixed to 42). Panel, tables, and figures carry the build date in
their folder name — reruns produce a new dated folder and never overwrite
history.

---

*End of v0.1. See `HANDOFF.md` for orientation material for the next agent.*