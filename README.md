# Crypto Market Factor Lab

> A reproducible Python research framework for BTC/ETH factor regimes, ETF-flow
> market plumbing, stablecoin liquidity, cross-asset connectedness, and
> crypto-native market structure using a frozen multi-source panel through
> April 2026.

This repository is positioned as a portfolio-grade crypto factor analytics
system built around frozen data and reproducible release pipelines. Curated
crypto, macro, ETF-flow, stablecoin, DeFi, and on-chain data are transformed
into tables, figures, model cards, and recruiter-friendly portfolio packets.

## First 60 Seconds

- **What it is:** a Python quant research lab for BTC/ETH factor diagnostics.
- **What it demonstrates:** data engineering, econometrics, market-structure
  reasoning, reproducible research, and careful visual communication.
- **What it does not claim:** causal proof that ETFs caused a structural break.
  ETF-flow results are framed as association, exposure, lead-lag evidence, and
  market-plumbing diagnostics.
- **Where to start:** run `python scripts/run_portfolio_v2_1_pipeline.py` and
  open [`reports/portfolio_v2_1/executive_summary.md`](reports/portfolio_v2_1/executive_summary.md).

## Quick Start

```powershell
uv sync --all-extras
uv run pytest
uv run python scripts/run_portfolio_v2_1_pipeline.py
```

For the historical research pipeline:

```powershell
uv run python scripts/run_full_pipeline.py
```

Data ingestion can require API keys and source availability. The portfolio
release uses the frozen dataset already committed under `Data/` and does not
require paid data.

## Repository Map

| Folder | Purpose |
|---|---|
| `Data/` | Frozen curated CSV data, documented by `Data/MASTER_DATA.md` and `Data/MASTER_DATA.csv`. |
| `config/` | Calendars, events, factor blocks, curation snapshots, and path constants. |
| `src/cqresearch/` | Reusable package for data loading, feature construction, modeling, and visualization helpers. |
| `scripts/` | Reproducible orchestration scripts, including `run_portfolio_pipeline.py` and `run_portfolio_v2_1_pipeline.py`. |
| `reports/panels/` | Frozen master panel metadata and generated parquet panels. |
| `reports/tables/` | Dated model and robustness outputs. |
| `reports/figures/` | Dated visual outputs from the analysis pipeline. |
| `reports/portfolio_v2/` | Stable baseline portfolio packet. |
| `reports/portfolio_v2_1/` | Enhanced analytics packet with block partial R^2, ablations, lead-lag labs, rolling correlations, stablecoin liquidity, native factors, figures, reports, model cards, and manifest. |
| `docs/specs/` | Research, data, methods, feature, and portfolio specifications. |
| `tests/` | Unit tests for config, fixtures, imports, and portfolio pipeline helpers. |

## Portfolio v2.1 Output

The v2.1 pipeline uses the frozen panel, writes a separate enhanced packet under
`reports/portfolio_v2_1/`, and leaves `Data/` untouched.

```powershell
uv run python scripts/run_portfolio_v2_1_pipeline.py
```

Expected outputs:

- [`reports/portfolio_v2_1/executive_summary.md`](reports/portfolio_v2_1/executive_summary.md)
- [`reports/portfolio_v2_1/technical_report.md`](reports/portfolio_v2_1/technical_report.md)
- [`reports/portfolio_v2_1/analytics_summary.md`](reports/portfolio_v2_1/analytics_summary.md)
- [`reports/portfolio_v2_1/data_atlas.md`](reports/portfolio_v2_1/data_atlas.md)
- [`reports/portfolio_v2_1/resume_bullets.md`](reports/portfolio_v2_1/resume_bullets.md)
- [`reports/portfolio_v2_1/model_cards/`](reports/portfolio_v2_1/model_cards/)
- [`reports/portfolio_v2_1/figures/`](reports/portfolio_v2_1/figures/)
- [`reports/portfolio_v2_1/tables/`](reports/portfolio_v2_1/tables/)
- [`reports/portfolio_v2_1/manifest.json`](reports/portfolio_v2_1/manifest.json)

## Hero Figures

### Data Architecture And Coverage

![Data coverage](reports/portfolio_v2_1/figures/F62_baseline_data_coverage.png)

### Factor Attribution

![BTC block partial R2](reports/portfolio_v2_1/figures/F10_btc_block_partial_r2_heatmap.png)

### ETF Flow Market Plumbing

![BTC ETF lead-lag](reports/portfolio_v2_1/figures/F22_btc_etf_lead_lag_heatmap.png)

### Cross-Asset Regimes

![BTC rolling correlations](reports/portfolio_v2_1/figures/F30_btc_rolling_correlations_180d.png)

### Stablecoin Liquidity And Native Factors

- [Stablecoin supply and TVL](reports/portfolio_v2_1/figures/F40_stablecoin_supply_and_tvl.png)
- [BTC native z-score dashboard](reports/portfolio_v2_1/figures/F50_btc_native_zscore_dashboard.png)

### Connectedness And Events

- [Compact VAR/FEVD connectedness heatmap](reports/portfolio_v2_1/figures/F60_baseline_fevd_compact_heatmap.png)
- [Event-study CARs](reports/portfolio_v2_1/figures/F61_baseline_event_study_cars.png)

## Interview Discussion Points

- Why full-vs-reduced block partial R^2 is useful, and why it is not
  Shapley/Owen attribution.
- Why ETF-flow intensity is market-plumbing evidence rather than causal proof.
- How stablecoin supply and TVL can be used as liquidity proxies without
  overselling them as identified shocks.
- Why MVRV is separated from non-MVRV BTC-native variables.

## Key Technical Skills Demonstrated

Python data engineering, reproducible artifact pipelines, stationary feature
engineering, HAC OLS, block attribution, lead-lag regressions, rolling
correlations, realized volatility, model cards, and public-facing quant
communication.

## Data Refresh

The frozen portfolio release does not need a refresh. If you intentionally want
to rebuild source data, use the curation tools and review `Data/_meta/curation_log.md`.

```powershell
make ingest
make curate
make inventory
make validate
```

## Method Notes

- Rolling attribution is **drop-one marginal R^2**, not Shapley/Owen.
- Structural break diagnostics are **Chow tests and single-break sup-F sweeps**,
  not a full Bai-Perron multiple-break estimator.
- ETF-flow intensity is scaled as daily USD ETF flow divided by prior-day USD
  market capitalization.
- Reports should use language such as association, exposure, factor
  contribution, market plumbing, lead-lag evidence, and regime diagnostics.

## License

See `LICENSE` if present; otherwise code under `src/cqresearch/` defaults to MIT
per the original project metadata. External datasets and third-party references
retain their upstream terms.
