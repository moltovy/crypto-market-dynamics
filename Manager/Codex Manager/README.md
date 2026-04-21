# Codex Manager Review Artifacts

Date: 2026-04-18

This folder contains the Codex implementation of the CryptoQuant manager-review plan. It is intentionally scoped to management, audit, protocol, and workflow artifacts. It does not modify `Data/`, source code, configs, generated reports, or prior AI outputs.

## Files

- `codex_manager_review_2026-04-18.md` - evidence-first 19-section manager review and decision memo.
- `four_paper_protocols_v0.md` - v0 protocols for the recommended four-paper portfolio.
- `data_calendar_metric_strategy_v0.md` - mixed-frequency policy, source precedence, and overlap guidance.
- `multi_agent_workflow_and_quality_gates_v0.md` - professional LLM operating model and quality gates.
- `p0_execution_backlog.md` - implementation backlog with dependencies and acceptance criteria.

## Status

Verified current repo facts before writing:

- `Data/MASTER_DATA.csv` currently lists 490 CSV files.
- Source counts are AlternativeMe 1, Artemis 48, CryptoQuant 345, DefiLlama 28, Farside ETF Data 3, FRED 21, Tradingview 44.
- Frequency counts are daily 436, weekly 31, monthly 13, snapshot 9, and `~4d` 1.
- `python -m pytest -q` passed with 9 tests.

Evidence: `Data/MASTER_DATA.csv`; `reports/run_summaries/02_build_master_panel.md`; `reports/run_summaries/03_run_analyses.md`; `tests/unit/`.

## Boundaries

These artifacts implement the plan as a decision and execution layer. They do not implement high-impact method or calendar changes because `AGENTS.md` requires human approval before changing event dates, calendar/fill policy, Data curation boundaries, method labels, core figures/tables, or the headline direction.

