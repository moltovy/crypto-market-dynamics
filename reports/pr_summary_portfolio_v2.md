# Portfolio v2 PR Summary

## Title

Portfolio v2.1/v2.2 public-readiness release

## Summary

This branch turns the original research repo into **Crypto Market Factor Lab**,
a portfolio-grade BTC/ETH factor analytics system with frozen-data
reproducibility, polished release packets, public showcase docs, optional
free-data scaffolding, and CI/release engineering.

v2.1 is the main polished public release. v2.2 is the advanced diagnostics
extension for deeper quant discussion.

## Major Features

- Portfolio v2 baseline packet under `reports/portfolio_v2/`.
- Portfolio v2.1 packet under `reports/portfolio_v2_1/` with:
  - executive summary, analytics summary, technical report, data atlas,
    resume bullets, manifest, verification diagnostics, and model cards
  - block partial R2, ablations, ETF/stablecoin lead-lag labs, rolling
    correlations, stablecoin liquidity diagnostics, BTC-native factor lab
  - figures F10-F13, F20-F25, F30-F33, F40-F44, F50-F52, plus baseline copies
- Public showcase layer under `reports/portfolio_showcase/` with interview,
  recruiter, role-specific, figure-gallery, walkthrough, limitations, LinkedIn,
  and pinned-repo docs.
- Portfolio v2.2 packet under `reports/portfolio_v2_2/` with:
  - PCA block factors
  - exact block Shapley R2 and stepped rolling Shapley
  - exploratory residual CUSUM diagnostics
  - FEVD order sensitivity
  - rolling VAR/FEVD connectedness
  - BTC robustness grid
  - figures F70-F78, reports, model cards, manifest, and verification notes
- Optional free-data scaffolding for DefiLlama, CoinGecko, Binance public
  klines, and FRED, with static tests only and no network dependency.
- CI/release engineering:
  - `uv sync --all-extras` based CI
  - pytest, mypy, and focused Ruff checks
  - manual portfolio smoke workflow
  - Makefile targets for v2/v2.1/v2.2/optional-data/verify
  - PR template and release checklist
- Final README, artifact index, and public-readiness audit.

## Changed Areas

| Area | Paths |
|---|---|
| Portfolio reports | `reports/portfolio_v2/`, `reports/portfolio_v2_1/`, `reports/portfolio_v2_2/` |
| Showcase docs | `reports/portfolio_showcase/` |
| Optional data | `optional_data/`, `reports/optional_data/`, `src/cqresearch/optional_data/`, `scripts/optional_data/` |
| Analytics code | `src/cqresearch/analysis/`, `src/cqresearch/modeling/`, `src/cqresearch/features/` |
| Pipelines | `scripts/run_portfolio_pipeline.py`, `scripts/run_portfolio_v2_1_pipeline.py`, `scripts/run_portfolio_v2_2_pipeline.py` |
| Tests | `tests/unit/` |
| Release engineering | `.github/`, `Makefile`, `docs/release_checklist.md` |
| Public docs | `README.md`, `reports/artifact_index.md`, `reports/final_public_readiness_audit.md` |

## Verification

| Command / Check | Result |
|---|---:|
| `uv run pytest` | PASS, 43 passed |
| `uv run mypy src/cqresearch` | PASS, no issues in 37 source files |
| Focused Ruff pass from `Makefile` | PASS |
| `uv run python scripts/run_portfolio_v2_1_pipeline.py` | PASS |
| `uv run python scripts/run_portfolio_v2_2_pipeline.py` | PASS |
| `uv run pytest tests/unit/test_optional_data_sources.py` | PASS |
| README/artifact local link audit | PASS |
| v2.1/v2.2 manifest field audit | PASS |
| v2.1/v2.2 model-card section audit | PASS |
| `git status --short -- Data` | PASS, no output |

Repo-wide `uv run ruff check .` is intentionally not a blocking gate yet. It
currently reports legacy notebook/tooling/config lint issues; focused Ruff
passes for the maintainable portfolio and optional-data surfaces.

## Data Proof

- Raw `Data/` files were not modified.
- `git status --short -- Data` returned no output during Phase 0, Phase 3,
  Phase 4, Phase 5, Phase 6, and the final pre-summary check.
- Core portfolio releases use the frozen committed panel and existing data
  bundles; optional data remains separate scaffolding.

## Guardrails

- ETF-flow outputs are reduced-form association, exposure, lead-lag, and
  market-plumbing diagnostics, not causal identification.
- Current structural-break diagnostics are Chow plus single-break sup-F, not
  full Bai-Perron.
- v2.1 rolling attribution is drop-one/partial R2, not Shapley/Owen.
- v2.2 exact block Shapley R2 is implemented, tested, and separately labeled as
  predictive attribution.
- Optional free data does not create a live or paid dependency for v2.1/v2.2.

## Caveats

- `make lint` could not be executed locally because GNU Make is not installed in
  this PowerShell environment; its underlying commands were run directly and
  passed.
- v2.1/v2.2 pipelines emit known pandas log warnings from frozen feature
  transforms with non-positive values.
- v2.2 emits statsmodels frequency warnings in VAR/FEVD windows; outputs are
  generated successfully.

## Reviewer Checklist

- [ ] Start with `README.md` and `reports/artifact_index.md`.
- [ ] Review `reports/portfolio_v2_1/executive_summary.md` as the main public
      release.
- [ ] Review `reports/portfolio_v2_2/advanced_methods_summary.md` for advanced
      diagnostics.
- [ ] Confirm manifests and verification diagnostics are present.
- [ ] Confirm model cards include purpose, inputs, sample, method, outputs,
      interpretation, risks, and upgrade path.
- [ ] Confirm no raw `Data/` files are modified.
- [ ] Confirm ETF-flow, structural-break, and attribution guardrails are
      preserved.
