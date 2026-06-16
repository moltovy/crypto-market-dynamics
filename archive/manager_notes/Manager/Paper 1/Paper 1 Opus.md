# Paper 1 — Research synthesis (v1.0 implementation)

**Date:** 2026-04-19  
**Role:** Blueprint + execution record for *BTC/ETH factor-exposure evolution* (Paper 1).

This file complements the v0.1 manager reviews (Codex / Gemini / Opus) with a **single implementation checkpoint** after the v1.0 pipeline run.

## What shipped in code (v1.0)

- **Calendar / ffill:** `config/calendars.yml` is the source of truth; `align_to_master(..., ffill_limit_days=None)` reads the configured master limit. **Headline mixed-frequency work** should state the **market-day (Mon–Fri)** vs **crypto-7** split (`static_ols_pre_post_etf.csv` includes a `calendar` column).
- **ETF intensity:** `btc_etf_intensity` / `eth_etf_intensity` = Farside flow (USD M) × 1e6 ÷ **prior-day USD market cap** (not price). Flow/price remains available as a robustness narrative only.
- **Labels:** Structural breaks are **Chow + single-break sup-F** (Andrews-style sweep), *not* full Bai–Perron multi-break. Rolling “partial R²” is **drop-one marginal R²**, not Shapley/Owen.
- **Event studies:** `placebo_p_m5_p5` is tied to the **[-5,+5]** CAR benchmark only (`placebo_benchmark_window` column).
- **CryptoQuant-native block (pre-registered):** see `docs/specs/paper_1_native_metrics.yml` — exchange netflow, miner→exchange, MVRV (first differences) in static OLS + robustness lists.
- **VAR:** Primary **4-variable** FEVD (`fevd_10d_compact.csv`, `var_fevd_meta_compact.json`); **8-variable** appendix (`fevd_10d.csv`, `F07b_*`).
- **Repro:** `uv.lock` + `requires-python >= 3.11`; CI runs `pytest` on Python 3.11 (`.github/workflows/ci.yml`).

## Primary artifact paths (build 2026-04-19)

| Artifact | Path |
|----------|------|
| Draft (v1.0) | `reports/drafts/paper_v1.0_2026-04-19.md` |
| Tables | `reports/tables/2026-04-19/` |
| Figures | `reports/figures/2026-04-19/` |
| Panel | `reports/panels/master_daily.parquet` |

## Hostile-referee risks still requiring prose discipline

1. **MVRV (and the native block) can dominate BTC R²** when included — macro/TradFi blocks stay modest; the paper must **not** over-claim “ETF as sole story” when valuation metrics explain most of the static fit.
2. **Association only** for ETF flows; R1 lag structure underscores simultaneity / mean reversion.
3. **Cholesky FEVD** is order-sensitive — compact and full orderings are logged in JSON metadata.

## Next optional upgrades (not blocking v1.0)

- Block-bootstrap placebo for structural breaks; optional `ruptures` k-break robustness.
- Quarto / PDF submission shell; vector figures.

---

*End of synthesis. Detailed narrative, tables, and citations: `reports/drafts/paper_v1.0_2026-04-19.md`.*
