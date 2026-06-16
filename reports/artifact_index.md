# Crypto Market Factor Lab Artifact Index

This index maps the public portfolio artifacts produced on the `portfolio_v2`
branch. v2.1 is the main polished release; v2.2 is the advanced diagnostics
extension.

## Root Entry Points

| Artifact | Purpose |
|---|---|
| [`README.md`](../README.md) | Public landing page and release map. |
| [`docs/release_checklist.md`](../docs/release_checklist.md) | Release and PR verification checklist. |
| [`.github/pull_request_template.md`](../.github/pull_request_template.md) | PR guardrails and reviewer checklist. |
| [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | CI quality gate: pytest, mypy, focused Ruff. |
| [`.github/workflows/portfolio-smoke.yml`](../.github/workflows/portfolio-smoke.yml) | Manual v2.1/v2.2 portfolio smoke workflow. |

## Portfolio Packets

| Packet | Status | Start Here |
|---|---|---|
| [`reports/portfolio_v2/`](portfolio_v2/) | Baseline portfolio packet | [`executive_summary.md`](portfolio_v2/executive_summary.md) |
| [`reports/portfolio_v2_1/`](portfolio_v2_1/) | Main polished release | [`executive_summary.md`](portfolio_v2_1/executive_summary.md) |
| [`reports/portfolio_v2_2/`](portfolio_v2_2/) | Advanced diagnostics extension | [`executive_summary.md`](portfolio_v2_2/executive_summary.md) |
| [`reports/portfolio_showcase/`](portfolio_showcase/) | GitHub-facing showcase and reviewer navigation layer | [`README_SHOWCASE.md`](portfolio_showcase/README_SHOWCASE.md) |
| [`reports/optional_data/`](optional_data/) | Optional free-data extension notes | [`free_data_addon_plan.md`](optional_data/free_data_addon_plan.md) |

## v2.1 Main Release

| Artifact | Purpose |
|---|---|
| [`portfolio_v2_1/executive_summary.md`](portfolio_v2_1/executive_summary.md) | Manager-ready summary. |
| [`portfolio_v2_1/technical_report.md`](portfolio_v2_1/technical_report.md) | Methods, limitations, and interpretation. |
| [`portfolio_v2_1/analytics_summary.md`](portfolio_v2_1/analytics_summary.md) | Workstream-by-workstream analytics summary. |
| [`portfolio_v2_1/data_atlas.md`](portfolio_v2_1/data_atlas.md) | Dataset and feature inventory. |
| [`portfolio_v2_1/manifest.json`](portfolio_v2_1/manifest.json) | Machine-readable artifact manifest. |
| [`portfolio_v2_1/diagnostics/verification.md`](portfolio_v2_1/diagnostics/verification.md) | Verification command results. |
| [`portfolio_v2_1/final_audit.md`](portfolio_v2_1/final_audit.md) | v2.1 public-readiness audit. |

## v2.2 Advanced Diagnostics

| Artifact | Purpose |
|---|---|
| [`portfolio_v2_2/executive_summary.md`](portfolio_v2_2/executive_summary.md) | Advanced diagnostics overview. |
| [`portfolio_v2_2/technical_report.md`](portfolio_v2_2/technical_report.md) | v2.2 methods and caveats. |
| [`portfolio_v2_2/advanced_methods_summary.md`](portfolio_v2_2/advanced_methods_summary.md) | Concise advanced-method explanation. |
| [`portfolio_v2_2/data_atlas.md`](portfolio_v2_2/data_atlas.md) | v2.2 table/source coverage. |
| [`portfolio_v2_2/manifest.json`](portfolio_v2_2/manifest.json) | Machine-readable artifact manifest. |
| [`portfolio_v2_2/diagnostics/verification.md`](portfolio_v2_2/diagnostics/verification.md) | Verification command results. |
| [`portfolio_v2_2/model_cards/`](portfolio_v2_2/model_cards/) | Model cards for PCA, Shapley, CUSUM, FEVD, connectedness, and robustness. |

## Figure Gallery

| Figure | Release |
|---|---|
| [`F10_btc_block_partial_r2_heatmap.png`](portfolio_v2_1/figures/F10_btc_block_partial_r2_heatmap.png) | v2.1 |
| [`F22_btc_etf_lead_lag_heatmap.png`](portfolio_v2_1/figures/F22_btc_etf_lead_lag_heatmap.png) | v2.1 |
| [`F30_btc_rolling_correlations_180d.png`](portfolio_v2_1/figures/F30_btc_rolling_correlations_180d.png) | v2.1 |
| [`F40_stablecoin_supply_and_tvl.png`](portfolio_v2_1/figures/F40_stablecoin_supply_and_tvl.png) | v2.1 |
| [`F50_btc_native_zscore_dashboard.png`](portfolio_v2_1/figures/F50_btc_native_zscore_dashboard.png) | v2.1 |
| [`F71_pca_factor_trajectories.png`](portfolio_v2_2/figures/F71_pca_factor_trajectories.png) | v2.2 |
| [`F72_btc_shapley_r2_stack.png`](portfolio_v2_2/figures/F72_btc_shapley_r2_stack.png) | v2.2 |
| [`F77_rolling_connectedness.png`](portfolio_v2_2/figures/F77_rolling_connectedness.png) | v2.2 |
| [`F78_robustness_grid_heatmap.png`](portfolio_v2_2/figures/F78_robustness_grid_heatmap.png) | v2.2 |

## Reproduction Commands

```powershell
uv sync --all-extras
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_portfolio_v2_1_pipeline.py
uv run python scripts/run_portfolio_v2_2_pipeline.py
uv run ruff check scripts/run_portfolio_pipeline.py scripts/run_portfolio_v2_1_pipeline.py scripts/run_portfolio_v2_2_pipeline.py scripts/optional_data src/cqresearch/analysis/native_factors.py src/cqresearch/analysis/portfolio_v2_1.py src/cqresearch/analysis/portfolio_v2_2.py src/cqresearch/features/volatility.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/ablation.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/pca_blocks.py src/cqresearch/modeling/shapley_r2.py src/cqresearch/modeling/cusum.py src/cqresearch/modeling/fevd_sensitivity.py src/cqresearch/modeling/rolling_connectedness.py src/cqresearch/modeling/robustness_grid.py src/cqresearch/optional_data tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_volatility.py tests/unit/test_pca_blocks.py tests/unit/test_shapley_r2.py tests/unit/test_cusum.py tests/unit/test_fevd_sensitivity.py tests/unit/test_rolling_connectedness.py tests/unit/test_robustness_grid.py tests/unit/test_portfolio_v2_1_pipeline.py tests/unit/test_portfolio_v2_2_pipeline.py tests/unit/test_optional_data_sources.py
```

## Release Candidate Docs

| Artifact | Purpose |
|---|---|
| [`final_public_readiness_audit.md`](final_public_readiness_audit.md) | Final local release-readiness audit and guardrail review. |
| [`pr_summary_portfolio_v2.md`](pr_summary_portfolio_v2.md) | PR-ready summary, verification notes, and reviewer checklist. |
| [`pr_review_package.md`](pr_review_package.md) | Concise reviewer navigation package. |
| [`release_notes_portfolio_v2.md`](release_notes_portfolio_v2.md) | Draft GitHub release notes and suggested tag. |

## Guardrail Summary

- Core releases use the frozen committed panel and do not require paid/live
  data.
- Raw `Data/` files should remain unchanged.
- ETF-flow outputs are reduced-form association and lead-lag diagnostics, not
  causal identification.
- v2.1 rolling attribution is drop-one marginal R2.
- v2.2 exact block Shapley R2 is separately labeled and tested.
- Structural-break outputs remain Chow and single-break sup-F unless a full
  Bai-Perron implementation is added later.
