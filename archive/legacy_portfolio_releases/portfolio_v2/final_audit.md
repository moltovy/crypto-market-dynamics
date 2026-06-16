# Portfolio v2 Final Consistency Audit

**Audit date:** 2026-06-16  
**Branch:** `portfolio_v2`  
**Result:** Pass for requested public-readiness scope.

## Checklist

| Check | Result | Notes |
|---|---|---|
| No active file frames the project as publication-first | Pass | README and portfolio packet frame the repo as Crypto Market Factor Lab. Legacy specs are explicitly marked legacy. |
| No active file claims ETF flows caused BTC/ETH returns | Pass | Remaining matches are explicit guardrails such as "Do not claim". Reports use association/market-plumbing language. |
| No active file labels current break code as full Bai-Perron | Pass | Current implementation is described as Chow plus single-break sup-F. Bai-Perron appears only as not implemented/future work. |
| No active file labels current rolling attribution as Shapley/Owen | Pass | Current implementation is described as drop-one marginal R^2. Shapley/Owen appears only as future work or negation. |
| Legacy specs clearly marked legacy | Pass | `research_spec.md`, `data_spec.md`, and `methods_spec.md` now have explicit legacy warnings. |
| README links to existing portfolio_v2 files only | Pass | README portfolio links resolve locally. |
| README links/embeds strongest figures | Pass | README embeds the cumulative-return hero and links rolling R^2, drop-one R^2, event CARs, FEVD, and coverage figures. |
| `portfolio_spec.md` acceptance criteria satisfied | Pass | Portfolio artifacts regenerate by one command; `Data/` is untouched; manager report, model cards, README, and outputs are present. |
| Model cards include required sections | Pass | Every model card has purpose, inputs, method, outputs, interpretation, risks, and upgrade path. |
| Manifest includes source bundle date, timestamp, commands | Pass | `manifest.json` includes `generated_at_utc`, `table_source_date`, `figure_source_date`, and `commands_run`. |
| `Data/` was not modified | Pass | `git status --short -- Data` returned no entries. |

## Original Manager Prompt Coverage

| Requirement group | Result | Evidence |
|---|---|---|
| 12-section deep research manager report | Pass | `manager_report.md` contains sections 1 through 12. |
| Repo evidence and suspected-fact verification | Pass | `manager_report.md` includes inspection coverage and suspected-fact verdicts tied to repo paths. |
| External research and source distinctions | Pass | `manager_report.md` separates academic, official/data, and methods sources and maps the requested research topics. |
| Optional free-data evaluation | Pass | `manager_report.md` includes a data-source decision table with overlap, value, burden, and decision. |
| Codex orchestration strategy and work packages | Pass | `manager_report.md` includes manager/implementer responsibilities and six ticket-style work packages. |
| Final artifact map and resume positioning | Pass | `manager_report.md`, `resume_bullets.md`, and `manifest.json` list portfolio artifacts and positioning. |
| Frozen data / no paid-data constraint | Pass | `Data/` is unmodified and optional live APIs are not core dependencies. |
| Honest, non-causal interpretation | Pass | Active reports use reduced-form association, exposure, market-plumbing, and regime-diagnostic language. |

## Commands Run

| Command | Result |
|---|---|
| `uv run python scripts/run_full_pipeline.py` | Pass: rebuilt panel, analyses, figures, summaries, and robustness outputs |
| `uv run pytest` | Pass: 13 passed |
| `uv run mypy src/cqresearch` | Pass: no issues in 18 source files |
| `uv run python scripts/run_portfolio_pipeline.py` | Pass: regenerated `reports/portfolio_v2/` from `reports/tables/2026-06-16` and `reports/figures/2026-06-16` |
| `uv run ruff check scripts/run_portfolio_pipeline.py tests/unit/test_portfolio_pipeline.py src/cqresearch/analysis/__init__.py src/cqresearch/modeling/__init__.py src/cqresearch/data/panel_builder.py` | Pass |

## Files Changed In This Audit

- `README.md`
- `docs/specs/data_spec.md`
- `docs/specs/methods_spec.md`
- `docs/specs/research_spec.md`
- `docs/specs/portfolio_spec.md`
- `scripts/run_portfolio_pipeline.py`
- `reports/portfolio_v2/manifest.json`
- `reports/portfolio_v2/manager_report.md`
- `reports/portfolio_v2/model_cards/*.md`
- `reports/portfolio_v2/final_audit.md`

## Unresolved Issues

None for the requested audit scope. Repo-wide Ruff still has pre-existing
notebook/tooling lint findings outside the focused public-readiness scope and
was intentionally not addressed here.
