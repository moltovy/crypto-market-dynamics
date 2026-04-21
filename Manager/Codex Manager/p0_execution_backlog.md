# P0 Execution Backlog

Date: 2026-04-18

Purpose: convert the manager review into implementable work items. This backlog does not itself authorize high-impact changes that `AGENTS.md` says require human approval.

## P0.1 Confirm Portfolio and Scope

Decision needed: approve the recommended four-paper portfolio.

Default recommendation:

1. BTC/ETH factor-exposure evolution.
2. ETF flow, wrapper, basis, and plumbing.
3. Stablecoin settlement liquidity.
4. DeFi credit, lending, and RWA bridge.

Fallback: replace Paper 4 with ETH staking/LST/LRT collateral transformation if lending/RWA data fail coverage checks.

Acceptance criteria:

- A dated decision note exists.
- Each paper has a one-page protocol.
- Each paper has a primary outcome, baseline panel, robustness plan, and kill criteria.

Evidence: `AGENTS.md`; `Manager/Codex Manager/four_paper_protocols_v0.md`.

## P0.2 Reconcile Governance Docs

Problem: `AGENTS.md` says four-paper program; older docs and Cursor rules still describe one paper.

Files likely affected after approval:

- `README.md`
- `HANDOFF.md`
- `.cursor/rules/global-constitution.mdc`
- possibly `project_research_plan.md` front matter

Acceptance criteria:

- All governance docs point to `AGENTS.md` as controlling.
- No file says the project is only one paper.
- Python version guidance is consistent with `AGENTS.md`.
- Commit message guidance is consistent.

Evidence: `AGENTS.md`; `README.md`; `HANDOFF.md`; `.cursor/rules/*.mdc`; `project_research_plan.md`.

## P0.3 Resolve Pipeline Entry-Point Contract

Problem: root `run_pipeline.py` and `scripts/run_full_pipeline.py` serve different roles, but docs/rules do not consistently explain this.

Recommended decision:

- Keep `run_pipeline.py` as curation/collection entry point.
- Keep `scripts/run_full_pipeline.py` as research-analysis entry point.
- Document the distinction.
- Later consider a top-level orchestrator only if it reduces confusion.

Acceptance criteria:

- One README section explains curation vs research analysis.
- Agent rules tell builders which command to run for each task.
- No generated output is silently overwritten without explicit rerun policy.

Evidence: `run_pipeline.py`; `scripts/run_full_pipeline.py`; `.cursor/rules/global-constitution.mdc`.

## P0.4 Fix Config Path Drift

Problem: `config/factor_blocks.yml` references paths that do not match current inventory; loader code uses different existing files.

Acceptance criteria:

- Add a config path validation test or script.
- Fix or document any missing paths.
- Research scripts consume config where practical instead of hardcoded lists.

Evidence: `config/factor_blocks.yml`; `src/cqresearch/data/loaders.py`; `Data/MASTER_DATA.csv`.

## P0.5 Decide Calendar and Fill Policy

Problem: calendar/fill behavior is a central empirical decision, not a code detail.

Default recommendation:

- Papers 1-2 headline regressions: market-day panels.
- Crypto-only diagnostics and Paper 4: calendar-day panels.
- Weekly robustness for mixed-frequency models.
- No blind forward-fill of returns, flows, fees, addresses, volumes, or exchange flows.

Acceptance criteria after approval:

- `config/calendars.yml` becomes executable source of truth.
- `src/cqresearch/data/calendars.py` reads or matches config.
- Tests cover weekend, holiday, forward-fill, zero-fill, and T+1 flow cases.
- Reports disclose calendar and fill choices.

Evidence: `config/calendars.yml`; `src/cqresearch/data/calendars.py`; `src/cqresearch/data/panel_builder.py`.

## P0.6 Correct Method Labels or Implement Methods

Problem: current labels can overstate implementation.

Required fixes:

- Do not say Bai-Perron unless true multiple-break implementation is present.
- Do not say Shapley/Owen partial R2 unless implemented.
- Label current ETF intensity as flow-per-price or rebuild it as flow/market cap, AUM, or volume.
- Label event placebo p-values as `[-5,+5]` benchmark unless window-specific p-values are computed.
- Describe VAR/FEVD assumptions and stability diagnostics.

Acceptance criteria:

- Draft and report language matches code.
- Tests cover event-window placebo logic.
- Tables contain method notes.

Evidence: `src/cqresearch/modeling/structural_breaks.py`; `src/cqresearch/modeling/rolling.py`; `src/cqresearch/features/panel.py`; `scripts/02_run_analyses.py`; `reports/drafts/paper_v0.1_2026-04-18.md`.

## P0.7 Build Metric Dictionary and Source-Overlap Registry

Problem: the inventory is large and overlapping; variable selection needs governance.

Acceptance criteria:

- Metric dictionary schema exists.
- Source precedence is recorded for each baseline concept.
- Overlap diagnostics exist for ETF flows, stablecoins, TVL, dollar index, ETH market cap, OI, fees, addresses, exchange flows, RWA, and lending.
- Each paper panel has a manifest.

Evidence: `Data/MASTER_DATA.csv`; `Manager/Codex Manager/data_calendar_metric_strategy_v0.md`.

## P0.8 Expand Tests

Current state: `python -m pytest -q` passes 9 tests, but coverage is thin.

Required tests:

- Config path validation.
- Calendar/fill behavior.
- ETF unit conversion and timing.
- Event-study placebo windows.
- Rolling attribution math and label checks.
- Structural-break fixture tests.
- Source-overlap reproducibility tests.

Evidence: `tests/unit/`; `scripts/02_run_analyses.py`; `src/cqresearch/`.

## P0.9 Citation and Prior-AI Quarantine

Problem: prior AI outputs contain citation-risk material.

Acceptance criteria:

- No `turn...` citations in drafts.
- Every citation has DOI, SSRN, arXiv, journal page, official page, or durable source URL.
- Prior AI files are not cited as evidence for empirical claims.
- Citation audit file exists before draft promotion.

Evidence: `reports/prior_ai_outputs/`; `Latest Output.txt`; `AGENTS.md`.

## P0.10 Visual QA Before Publication Figures

Problem: current figures are useful diagnostics but not publication-ready.

Acceptance criteria:

- Each paper figure has source data.
- Each figure has vector and PNG output.
- Labels and legends are reviewed at manuscript size.
- Event-study figures do not mix window-specific and benchmark p-values.
- Diagnostic figures are separated from publication figures.

Evidence: `reports/figures/2026-04-18/`; `scripts/03_make_figures.py`.

## Suggested Implementation Order

1. Confirm human decisions on portfolio and calendar.
2. Reconcile governance docs.
3. Add config path validation.
4. Implement calendar/fill tests before changing panel construction.
5. Fix method labels or code in Paper 1.
6. Build metric dictionary and source-overlap registry.
7. Build paper-specific panels.
8. Redesign figures and citation workflow.

## Current Quality Gate

- Inputs read: `Data/MASTER_DATA.csv`; `reports/run_summaries/02_build_master_panel.md`; `reports/run_summaries/03_run_analyses.md`; `src/cqresearch/features/panel.py`; `scripts/02_run_analyses.py`; `Manager/Gemini Manager/Project_Audit_Report.md`; `Manager/Opus Manager/comprehensive_review.md`; user-supplied `AGENTS.md`.
- Outputs written: `Manager/Codex Manager/*.md`.
- Tests run: `python -m pytest -q`, 9 passed.
- Confidence: 84 percent for manager-level priorities; lower for Paper 4 until coverage and signal checks are run.

