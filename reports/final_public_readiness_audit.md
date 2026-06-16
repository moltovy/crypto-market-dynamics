# Final Public-Readiness Audit

## Verdict

**Locally PR-ready; remote push requires a GitHub token refresh with `workflow`
scope.** The portfolio branch now has a polished v2.1 main release, a v2.2
advanced diagnostics extension, GitHub-facing showcase docs, optional free-data
scaffolding, CI/release engineering, and reproducibility checks that leave raw
`Data/` untouched.

## Branch And Commit Summary

- Branch: `portfolio_v2`
- Latest verified commit before this audit refresh: `9a02bd4`
- Last local verification refresh: `2026-06-16T11:46:26.5360740-05:00`
- Local prompt files handled outside the repo: `Instructions.md` and
  `Instructions P2.md` are excluded through `.git/info/exclude`.
- Continuation sprint commits reviewed:
  - `ace93e4 feat(portfolio): add v2.1 analytics expansion pipeline`
  - `1541d0b docs(portfolio): add v2 and v2.1 release packets`
  - `433a070 docs(readme): surface portfolio v2.1 analytics gallery`
  - `a8229e7 chore(portfolio): harden v2.1 release packet`
  - `141e30a docs(showcase): add portfolio showcase layer`
  - `962f310 feat(portfolio): add v2.2 advanced quant diagnostics`
  - `e21bbe9 feat(optional-data): scaffold free data extension layer`
  - `ad0f4f2 ci: add portfolio verification and release checklist`
  - `91e87e8 docs: finalize public portfolio presentation`
  - `ffde97b docs: add portfolio PR summary`
  - `2d42d54 chore(portfolio): close instructions compliance gaps`
  - `9a02bd4 docs: update final release verification`

## Remote And PR Status

| Item | Status | Notes |
|---|---:|---|
| `git push -u origin portfolio_v2` | BLOCKED | GitHub rejected workflow updates because the current OAuth token lacks `workflow` scope. |
| `git ls-remote --heads origin portfolio_v2` | NOT PRESENT | No remote branch was visible after the blocked push. |
| `gh auth status` | AUTHENTICATED | Active scopes: `gist`, `read:org`, `repo`; missing `workflow`. |
| PR creation | PENDING | Requires branch push first. Manual instructions are in `reports/manual_pr_instructions.md`. |
| Remote CI | PENDING | Requires branch push/PR first. Manual instructions are in `reports/manual_ci_check_instructions.md`. |

## Packet Presence

| Packet | Status | Notes |
|---|---:|---|
| `reports/portfolio_v2/` | PASS | Baseline packet preserved. |
| `reports/portfolio_v2_1/` | PASS | Main polished release; regenerated successfully. |
| `reports/portfolio_v2_2/` | PASS | Advanced diagnostics extension; regenerated successfully. |
| `reports/portfolio_showcase/` | PASS | GitHub-facing showcase, figure gallery, walkthrough, and reviewer navigation docs present. |
| `reports/optional_data/` | PASS | Optional source decision docs and registry output present. |
| `reports/artifact_index.md` | PASS | Central artifact map added. |
| `reports/manual_push_instructions.md` | PASS | Documents workflow-scope blocker and exact push path. |
| `reports/manual_pr_instructions.md` | PASS | Documents CLI/browser PR creation. |
| `reports/manual_ci_check_instructions.md` | PASS | Documents remote CI checks and failure triage. |

## Verification Results

| Command / Check | Result | Notes |
|---|---:|---|
| `uv run pytest` | PASS | 43 passed |
| `uv run mypy src/cqresearch` | PASS | Success: no issues in 37 source files |
| Focused Ruff on maintained portfolio/optional-data paths | PASS | All checks passed |
| `uv run python scripts/run_portfolio_v2_1_pipeline.py` | PASS | Generated 27 tables, 25 figures, 7 report/diagnostic docs, 9 model cards |
| `uv run python scripts/run_portfolio_v2_2_pipeline.py` | PASS | Generated 14 tables, 9 figures, 7 report/diagnostic docs, 6 model cards |
| `uv run pytest tests/unit/test_optional_data_sources.py` | PASS | 6 passed |
| README + artifact-index link check | PASS | All local links resolve |
| v2.1/v2.2 manifest field check | PASS | Required fields present; table/figure counts recorded |
| v2.1/v2.2 model-card section check | PASS | Required sections present |
| `git status --short -- Data` | PASS | No output; raw data untouched |
| `uv run ruff check src/cqresearch scripts tests` | DOCUMENTED FAIL | 78 legacy findings in older scripts/core/test files outside the new maintained portfolio surface |
| `make lint` | NOT RUN | GNU Make is not installed in this PowerShell environment; underlying commands passed directly |

## Known Warnings

- v2.1 and v2.2 pipeline runs emit pandas `invalid value encountered in log`
  warnings from frozen feature transforms with non-positive inputs.
- v2.2 emits statsmodels `No frequency information was provided` warnings in
  VAR/FEVD windows; the pipeline completes and writes expected outputs.
- Broad Ruff over `src/cqresearch scripts tests` still fails on pre-existing
  legacy scripts, older core modules, and legacy test style. This was
  intentionally kept out of scope; CI uses a focused maintainable path list.

## Guardrail Audit

| Guardrail | Status | Evidence |
|---|---:|---|
| No raw `Data/` edits | PASS | `git status --short -- Data` returned no output. |
| No paid/live dependency for core releases | PASS | v2.1/v2.2 use frozen panels; optional data is separate scaffolding. |
| No causal ETF-flow claim | PASS | Matches are explicit caveats such as "do not establish" or "does not claim". |
| No current full Bai-Perron label | PASS | Structural-break text says Chow plus single-break sup-F, or explicitly "not full Bai-Perron". |
| Drop-one attribution not mislabeled | PASS | v2.1 labels drop-one/partial R2 separately; v2.2 exact Shapley R2 is implemented and tested. |
| Legacy specs marked legacy where needed | PASS | Active specs separate current methods from future upgrades. |
| README links to existing files | PASS | Local link audit passed. |
| README links strongest figures | PASS | v2.1 hero gallery and v2.2 advanced gallery are linked. |

## Release Engineering

- `.github/workflows/ci.yml` now installs with `uv sync --all-extras`, runs
  pytest, mypy, and focused Ruff.
- `.github/workflows/portfolio-smoke.yml` provides a manual v2.1/v2.2 packet
  regeneration workflow and checks `Data/`.
- `Makefile` now uses `uv run` targets for `portfolio-v2`, `portfolio-v2-1`,
  `portfolio-v2-2`, `optional-data`, `lint`, and `verify`.
- `.github/pull_request_template.md` and `docs/release_checklist.md` document
  reviewer guardrails.
- Branch push is currently blocked only by local GitHub token scope, not by
  repository content. Refresh the token with `gh auth refresh -h github.com -s
  workflow`, then rerun `git push -u origin portfolio_v2`.

## Caveats

- v2.2 is advanced diagnostics, not the main public portfolio release. Lead with
  v2.1 in the README and PR narrative; use v2.2 as the advanced-method appendix.
- Exact Shapley R2 is predictive attribution over the chosen block design, not
  causal identification.
- CUSUM is exploratory residual diagnostics, not full Bai-Perron.
- Optional free data should not be wired into core reproduction without a
  separate cache/versioning design.

## Suggested PR Body

Title: `Portfolio v2.1/v2.2 public-readiness release`

Summary:

- Adds a polished v2.1 portfolio release packet with reports, model cards,
  figures, tables, manifest, verification diagnostics, and public showcase docs.
- Adds v2.2 advanced diagnostics: PCA blocks, exact block Shapley R2, CUSUM,
  FEVD-order sensitivity, rolling connectedness, and BTC robustness grid.
- Adds optional free-data scaffolding for DefiLlama, CoinGecko, Binance public
  klines, and FRED using offline URL builders/normalizers and static tests.
- Adds CI, manual portfolio smoke workflow, Makefile targets, PR template,
  release checklist, and artifact index.
- Preserves raw `Data/` and keeps all ETF-flow language reduced-form.

Verification:

- `uv run pytest` -> 43 passed
- `uv run mypy src/cqresearch` -> pass
- Focused Ruff -> pass
- `uv run python scripts/run_portfolio_v2_1_pipeline.py` -> pass
- `uv run python scripts/run_portfolio_v2_2_pipeline.py` -> pass
- `git status --short -- Data` -> no output
