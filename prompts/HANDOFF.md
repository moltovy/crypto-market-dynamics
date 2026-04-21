# CryptoQuant v0.1 — Handoff to the next agent

**Last updated:** 2026-04-18 · branch: `cursor/repo-reorg-scaffold`

This document is the single entry point for any LLM or human continuing this
project. It tells you *what works*, *what the numbers say*, *what is
unfinished*, and *exactly what to run next*. Every claim in this file is
anchored to a file path you can read.

---

## 1. Current state in 60 seconds

- **Research question**: How have BTC and ETH factor loadings (macro,
  institutional, liquidity, sentiment, crypto-native) evolved across the
  2020–2026 window, and did the 2024 spot-ETF approvals constitute a
  structural break?
- **Paper draft v0.1**: `reports/drafts/paper_v0.1_2026-04-18.md` — 7
  sections plus robustness appendix, every number tied to a CSV.
- **Headline findings** (all with HAC-5 inference, n=821 in post-ETF spec):
  1. BTC return volatility fell 22% post-ETF (3.18% → 2.49% daily SD).
  2. Post-ETF, `btc_etf_intensity = flow_t / close_{t-1}` has β = **2.33**,
     HAC-t = **8.7**, R² jumps from ~14% to **23.7%** (Table 5).
  3. The Chow test at 2024-01-11 is **insignificant** (F=0.81, p=0.60). The
     sup-F test places the dominant structural break at **2021-01-04**.
  4. Robustness: R1 (lagged flow reveals next-day mean reversion of –1/3),
     R2 (no-winsor), R3 (HAC 5/10/20/40) all confirm the ETF-flow coefficient.
- **Master panel**: `reports/panels/master_daily.parquet` — 2,293 rows ×
  58 cols (2020-01-01 → 2026-04-11) built from 16 source CSVs.

---

## 2. Environment

```bash
# Python 3.10.0, all deps already installed in the active interpreter
pip install -e .               # re-runs cleanly
python -m pytest -q            # 9 unit tests, all green
```

Data folder is **read-only**. Every analysis output lands under `reports/`
in a **dated** folder, e.g. `reports/tables/2026-04-18/`. Reruns **never**
overwrite prior results — they write a new dated folder.

---

## 3. Pipeline (reproduce everything)

```bash
python scripts/run_full_pipeline.py
```

or, step-by-step:

| Step | Script | Writes |
|---|---|---|
| 0 | `scripts/inspect_core_files.py` | `reports/run_summaries/01_inspect_core_files.md` (+ JSON) |
| 1 | `scripts/01_build_master_panel.py` | `reports/panels/master_daily.parquet`, `_coverage.csv`, `_meta.json` |
| 2 | `scripts/02_run_analyses.py` | `reports/tables/<DATE>/{static_ols_pre_post_etf, rolling_ols_*_180d, structural_breaks_summary, sup_f_series_*, fevd_10d, event_studies}.csv` |
| 3 | `scripts/03_make_figures.py` | `reports/figures/<DATE>/F01…F10*.png` |
| 4 | `scripts/04_descriptives_and_summaries.py` | `descriptive_stats.csv`, `block_r2_pre_post.csv`, `correlation_matrix_*.csv`, `etf_flow_regression.csv`, `rolling_r2_*_median_by_year.csv` |
| 5 | `scripts/05_robustness.py` | `reports/tables/<DATE>/robustness/R1…R6.csv` |

Total runtime: ~3-4 min on a standard laptop (the placebo permutations in
step 2 are the slowest piece, ~2.5 min).

---

## 4. Code map (what lives where)

```
src/cqresearch/
  data/
    calendars.py         Crypto-7 vs Business-5 calendar semantics; the
                         align_to_master(series, kind=stock|flow|rate) helper.
    loaders.py           One typed loader per source family (CryptoQuant,
                         FRED, Tradingview, Farside, DefiLlama, AlternativeMe).
    panel_builder.py     Assembles the master daily panel; emits a coverage
                         report per column.
  features/
    returns.py           log_return, first_diff, winsorize, realized_vol,
                         garman_klass, zscore.
    panel.py             Builds the feature frame (log returns, diffs, ETF
                         flow intensity) used by every model.
  modeling/
    ols.py               OLS + Newey-West HAC; subsample_ols for pre/post.
    rolling.py           Rolling OLS with partial-R² decomposition.
    structural_breaks.py Chow, sup-F sweep (Andrews trim=0.15), placebo
                         permutation p-values.
    var_fevd.py          VAR with BIC lag selection; 10-day FEVD and
                         Diebold-Yilmaz total connectedness.
    event_study.py       Market-model CARs + placebo p-values.
  viz/
    style.py             Palette + matplotlib rcParams + add_footer().

scripts/
  inspect_core_files.py  # step 0
  01_build_master_panel.py
  02_run_analyses.py
  03_make_figures.py
  04_descriptives_and_summaries.py
  05_robustness.py
  run_full_pipeline.py   # orchestrator

config/
  paths.py               Single source of truth for every filesystem path.
  calendars.yml          Calendar policies.
  factor_blocks.yml      Five-block factor catalog.
  events.yml             Pre-registered event dates.

reports/
  panels/                Parquet panels (master + per-asset when built).
  tables/<date>/         CSVs (all numeric results).
  tables/<date>/robustness/  R1–R6 sensitivity checks.
  figures/<date>/        PNGs.
  run_summaries/         Dated Markdown logs of every run.
  drafts/                Paper drafts (keep immutable; author new versions).
  prior_ai_outputs/      Legacy / source material, read-only.
```

---

## 5. Key data decisions (the ones you must respect or explicitly challenge)

1. **Sample window is 2020-01-01 → 2026-04-11.** Reason: BTC ETFs launch
   2024-01-11; we need ≥ 4 years of pre-history. Extending earlier brings in
   a very different market-structure regime (no stablecoins, no CME, no
   ETFs). Override in `cqresearch.data.calendars.DEFAULT_START` if you
   explicitly want 2018+.
2. **Crypto-7 calendar is master.** Equity / macro series are forward-filled
   up to 4 days (covers long weekends + Monday holidays). Farside ETF flows
   are zero-filled on weekends *within* the series' active window — a
   weekend is a genuine zero-flow day, not missing data.
3. **Returns are log-returns, rates are first-differenced.** Mixing the two
   in one regressor is a bug and the types are disjoint in
   `cqresearch.features.panel.PRICE_COLS` vs `DIFF_COLS`.
4. **Winsorization is symmetric 1/99% full-sample.** Robustness check R2
   confirms this isn't where the signal comes from, but if you prefer not
   to winsorize (tail-event analysis), turn it off in `load_features`.
5. **HAC = 5 lags** is the default. Robustness R3 covers 5/10/20/40.
6. **Event-study market benchmark is SPY.** Using a crypto-factor benchmark
   (e.g. BTC itself for ETH events) would change CARs materially. This is
   flagged in Section 5 of the paper.

---

## 6. Known weaknesses / open tasks (prioritized)

### P0 — highest marginal value, ~1 day each

- **P0.1 ETF-flow issuer decomposition.** The panel has 13 individual
  issuer columns (`btc_etf_ibit`, `…_fbtc`, etc). Re-run Table 5 with each
  as a separate regressor to expose rotating leadership (IBIT → FBTC →
  …). Code skeleton: copy `etf_flow_regression()` in
  `scripts/04_descriptives_and_summaries.py`; change the regressors list.
- **P0.2 TVP-VAR connectedness.** `cqresearch.modeling.var_fevd` currently
  does a single full-sample VAR. Implement a 180-day rolling VAR and plot
  the time path of the Diebold-Yilmaz total connectedness index; compare
  to Figure F02 rolling R². This is the single missing "time-varying"
  figure the paper needs.
- **P0.3 Stablecoin sub-basket split.** `stables_total_usd` is a naïve sum.
  Use `Data/DefiLlama/Stablecoins/stablecoins.csv` metadata (`pegMechanism`
  field) to build two separate series: *fiat-backed* (USDT, USDC, PYUSD,
  USD1, FDUSD, …) and *crypto-backed* (DAI, USDe, USDS, USDf, USDD). Re-run
  FEVD — expect very different DY connectedness.
- **P0.4 Causal identification for ETF flow.** R1 already shows the lagged
  flow is insignificant (overshoot reverts), but that rules out simple
  *predictive* flow→return causality only. Proper DML or IV design (e.g.
  using GBTC conversion-discount pressure as an instrument) is the right
  next step.

### P1 — important, ~2-3 days each

- **P1.1 Bai-Perron multiple breaks.** Our sup-F is single-break. A
  proper k-break DP search (Bai-Perron 1998) on BTC returns would tell us
  whether 2021-01 *and* 2022-11 *and* 2024-01 all jointly matter. The
  `cqresearch.modeling.structural_breaks` module is where this belongs.
- **P1.2 On-chain factor block**. CryptoQuant ships a dense set of
  exchange-flow, miner-flow, and supply metrics under
  `Data/CryptoQuant/BTC/`. Picking ~6 high-signal columns (exchange net
  flow, miner-to-exchange flow, coinbase premium index, SOPR, MVRV Z-score,
  realized cap delta) and adding them as a 6th factor block is the
  obvious "crypto-native" complement to Section 4.2.
- **P1.3 ETH-specific extensions.** Staking yield (ETH 2.0 deposits),
  L2-as-share-of-total-TVL, and a Merge / Pectra event study are all
  under-done. Data: `Data/CryptoQuant/ETH/ETH 2.0/`, TVL by chain panel.
- **P1.4 Placebo design upgrade.** `placebo_breaks` permutes y only — a
  block-bootstrap (50-day blocks) placebo is the gold-standard under
  heavy tails + autocorrelation.

### P2 — nice-to-have

- **P2.1 Quantile regression** on extreme-return days — the 5%/95%
  quantile betas on SPY and VIX likely differ from the OLS mean-beta,
  especially post-ETF.
- **P2.2 Regime-detection HMM** on rolling R² and connectedness to label
  "macro-dominated", "flow-dominated", and "native-dominated" regimes and
  measure their duration.
- **P2.3 RWA / DAT blocks.** `Data/DefiLlama/RWA/` and `Data/DefiLlama/DATs/`
  are currently untouched. These are small but fast-growing; a modest
  descriptive section would strengthen the paper's "liquidity" story.

---

## 7. Files you should read first

1. `reports/drafts/paper_v0.1_2026-04-18.md` — the whole argument
2. `reports/run_summaries/03_run_analyses.md` — numbers at a glance
3. `reports/tables/2026-04-18/etf_flow_regression.csv` — the headline
4. `project_research_plan.md` — the 18-section research & execution plan
5. `config/factor_blocks.yml` — canonical factor taxonomy
6. `.cursor/rules/evidence-confidence.mdc` — citation & confidence rules
7. `AGENTS.md` — operating constitution for agents

---

## 8. Contracts for the next agent

If you modify or extend anything:

1. **Preserve dated folders.** Every write goes under
   `reports/**/YYYY-MM-DD/`, creating a new folder for your run — never
   overwrite the 2026-04-18 folder.
2. **Add your run-summary.** Drop a `reports/run_summaries/NN_<slug>.md`
   with (a) what you changed, (b) what you ran, (c) what files you wrote,
   (d) what the top-line finding was, (e) a confidence score.
3. **Cite file paths for every empirical claim.** Do not assert "ETH
   correlation increased" without pointing at a specific column in a
   specific CSV.
4. **Do not modify `Data/`.** Raw is sacred. Transform to
   `reports/panels/` or `reports/tables/` only.
5. **Tests:** `python -m pytest -q` must remain green after your changes.
6. **Commits:** one logical change per commit, informative message, never
   `git push --force` on shared branches.

Welcome. Everything is wired for you to pick up.
