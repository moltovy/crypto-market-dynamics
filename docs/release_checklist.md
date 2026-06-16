# Portfolio Release Checklist

## Pre-Release

- Confirm branch is `portfolio_v2`.
- Confirm `Instructions.md` is untracked or intentionally excluded.
- Confirm `git status --short -- Data` returns no output.
- Regenerate the intended packet:
  - `uv run python scripts/run_portfolio_v2_1_pipeline.py`
  - `uv run python scripts/run_portfolio_v2_2_pipeline.py`
- Run verification:
  - `uv run pytest`
  - `uv run mypy src/cqresearch`
  - `make lint` or the focused Ruff command from `Makefile`

## Narrative Guardrails

- v2.1 is the main polished portfolio release.
- v2.2 is the advanced diagnostics extension.
- ETF-flow results are reduced-form associations only.
- CUSUM is exploratory and must not be described as full Bai-Perron.
- Drop-one partial R2 and exact Shapley R2 must be labeled separately.
- Optional free data remains outside the core release path.

## Artifact Checks

- README links point to existing files and figures.
- `reports/artifact_index.md` is updated.
- Each model card has purpose, inputs, sample, method, outputs, interpretation,
  risks, and upgrade path.
- Manifest files include generation timestamp, command list, tables, figures,
  reports, and method notes.

## PR Readiness

- Add or refresh `reports/pr_summary_portfolio_v2.md`.
- Add or refresh `reports/final_public_readiness_audit.md`.
- Review the PR template guardrails before opening the pull request.
