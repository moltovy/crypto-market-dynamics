# Baseline Audit

Generated during Task 00 before feature implementation.

## Git State

| Item | Value |
|---|---|
| Starting branch | `main` |
| Starting HEAD | `d374198b9df215a5109fd23754d77127645cefa7` |
| Local `main` HEAD | `d374198b9df215a5109fd23754d77127645cefa7` |
| `origin/main` HEAD | `d374198b9df215a5109fd23754d77127645cefa7` |
| Final work branch | `codex/final-research-consolidation` |
| Remote | `https://github.com/moltovy/Crypto-Research-Paper-Data-Factors-Analysis-.git` |

Initial working tree contained only the local instruction folder as untracked material. The baseline pipeline later regenerated tracked output files; those changes are baseline churn and are intentionally left unstaged until superseded by the final canonical pipeline.

## Repository Size And Large Files

| Check | Result |
|---|---|
| `git count-objects -vH` loose objects | 343 objects, 18.72 MiB |
| Packed size | 120.80 MiB |
| Workspace size excluding caches/.git/.venv | 1,479 files, 231,635,609 bytes |

Largest tracked files at baseline include:

| Path | Approximate role |
|---|---|
| `outputs/tables/T52_constituent_daily_ohlcv.csv` | Current-top50 exploratory daily cohort |
| `Data/MarketStructure/DefiLlama/crypto_constituents_daily_ohlcv_top50_current_2020_2026.csv` | Source for exploratory current-top50 cohort |
| `Data/DefiLlama/TVL/Daily/tvl_by_chain_long_daily.csv` | DefiLlama TVL source |
| `outputs/tables/T05_rolling_correlations.csv` | Legacy rolling-correlation output |
| `outputs/tables/T40_crypto_universe_monthly.csv` | PIT monthly universe output |
| `outputs/tables/T56_rolling_beta_to_btc_eth.csv` | Exploratory current-cohort beta output |

## Environment

| Command | Result |
|---|---|
| `python --version` | Python 3.12.10 |
| `uv --version` | uv 0.11.21 |
| direct `ruff --version` | Not on PATH |
| direct `mypy --version` | Not on PATH |

Ruff and mypy are available through `uv run`.

## Baseline Verification Commands

| Command | Result | Notes |
|---|---|---|
| `uv sync --all-extras` | Pass | Resolved 103 packages, checked 96 packages. |
| `uv run pytest` | Pass | 71 passed in 10.21s. Test set still includes legacy portfolio and Shapley-era tests. |
| `uv run mypy src/cqresearch` | Pass | No issues in 53 source files. |
| `uv run python scripts/run_all.py` | Pass with warnings | Generated 34 tables, 20 figures, 10 model cards; emitted pandas/numpy runtime warnings in log/correlation steps. |
| `uv run python scripts/check_public_surface.py` | Pass | Existing checker is too permissive for final program because it allows the current F-numbered surface. |
| `uv run ruff check src/cqresearch scripts tests` | Fail | 95 baseline lint findings across legacy scripts/modules/tests. |

## Failure Classification

| Area | Classification |
|---|---|
| Ruff failure | Maintained-surface and legacy-surface debt: import sorting, ambiguous Unicode, non-lowercase model variables, unused imports, old scripts. |
| Runtime warnings in `run_all.py` | Data/modeling cleanup issue: invalid log and degenerate correlation warnings need explicit handling or documented skips. |
| Public-surface checker passing despite 12 README figures | Checker coverage gap: final checker must enforce figure registry, figure count, archive leakage, causal language, current-cohort caveats, and stale output names. |
| Legacy portfolio tests passing | Architecture debt: old workflows remain active in test and CI surfaces. |

## Public Artifact Inventory

Baseline README embeds 12 figures:

1. `outputs/figures/F01_mvrv_sensitivity_by_regime_v2.png`
2. `outputs/figures/F02_same_support_ablation.png`
3. `outputs/figures/F03_btc_ex_mvrv_strength.png`
4. `outputs/figures/F04_etf_flow_lead_lag.png`
5. `outputs/figures/F05_core_correlation_matrix.png`
6. `outputs/figures/F06_rolling_correlations.png`
7. `outputs/figures/F07_feature_strength_heatmap.png`
8. `outputs/figures/F08_connectedness_robustness.png`
9. `outputs/figures/F30_market_structure_dashboard.png`
10. `outputs/figures/F42_market_evolution_dashboard.png`
11. `outputs/figures/F47_market_structure_modeling_dashboard.png`
12. `outputs/figures/F53_rotation_dashboard.png`

Baseline outputs include 60 numbered table/report outputs, 20 generated figures according to `run_all.py`, old contact sheets, old visual audit files, gallery figures, a dashboard, and model cards tied to legacy factor/portfolio framing.

## Data Inventory

`Data/` contains the following source groups at baseline:

| Source group | File count |
|---|---:|
| AlternativeMe | 2 |
| Artemis | 49 |
| CryptoQuant | 389 |
| DefiLlama | 54 |
| Farside ETF Data | 5 |
| FRED | 23 |
| MarketStructure | 15 |
| Tradingview | 47 |
| `_meta` | 3 |
| MASTER_DATA files | 3 |

`Data/MASTER_DATA.csv`, `Data/MASTER_DATA.md`, and `Data/MASTER_DATA.txt` exist at baseline.

## T40/T41 Integrity Check

| File | Working-tree bytes | Header | Data rows | Git blob |
|---|---:|---|---:|---|
| `outputs/tables/T40_crypto_universe_monthly.csv` | 3,086,316 | `source,snapshot_date,month,asset_key,token_id,coingecko_id,symbol,asset_name,price_usd,market_cap_usd,source_rank_full_market,rank_full_market,is_partial_month,asset_class,in_full_top100,rank_ex_stable,rank_clean_risk,in_ex_stable_top100,in_clean_risk_top100` | 15,600 | `4b85e888228653f25896210194fd309035b9f229` |
| `outputs/tables/T41_clean_risk_top100_monthly.csv` | 1,114,666 | `snapshot_date,month,asset_key,token_id,coingecko_id,symbol,asset_name,asset_class,price_usd,market_cap_usd,rank_full_market,rank_clean_risk,is_partial_month` | 7,800 | `2f6a3fb840eaaa270aaf4b8137148c2e0bfb9ef8` |

The tracked Git blob sizes are 3,070,715 bytes for T40 and 1,106,865 bytes for T41. The working-tree byte counts differ because of platform line endings; hashes normalized by Git match the tracked blobs. Both files are non-empty in the working tree and in Git.

## CI And Maintained Surface

Baseline CI runs tests, mypy, and a focused Ruff list that still includes portfolio/v2 scripts and tests. It does not run the full final verification suite specified by the program, and it does not currently require the offline pipeline or public-surface checker in `ci.yml`.

## Initial Findings

- The safest implementation base is `main` at `d374198`, with PR #3 treated as selectively reusable but superseded.
- The existing repository can run offline, but the active surface is still release/portfolio/factor-lab oriented.
- Public outputs are over-broad, F-numbered, and include current-cohort exploratory material in the README.
- The public-surface checker must be tightened because it passes an output set that violates the final figure limit and semantic naming standard.
- T40/T41 are not empty and should be reused as PIT composition inputs only, with corrected taxonomy and no daily PIT performance claims.
