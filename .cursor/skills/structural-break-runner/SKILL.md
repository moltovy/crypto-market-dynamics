---
name: structural-break-runner
description: Run the standard structural-break battery (Bai-Perron, Chow, CUSUM) for a series or regression around a pre-registered event date. Produces tables, figures, and a run-summary markdown. Use for any break-date verification.
---

# structural-break-runner

## Purpose
Stop hand-picked, over-fit break detection. Enforce the project's pre-registered protocol from `project_research_plan.md §11.4`.

## Pre-registered inputs
- Event date(s) MUST come from `config/events.yml` (`primary_breaks` or `secondary_candidates`). Never add a new date without an ADR in `docs/decisions/`.
- Series MUST come from `reports/panels/master_daily.parquet` (or a block panel) built by `src/cqresearch/analysis/`.
- Windows: `windows.short=5`, `windows.medium=20`, `windows.long=60` trading days from `config/events.yml`.

## Standard battery (all four, every time)
1. **Chow test** on a specified regression model, conditioning on the event date.
2. **Bai-Perron** multiple-break search restricted to a ±60 day window around each event, reporting F-statistics, supF, UDmax, WDmax, break locations, and 95% CIs.
3. **CUSUM / CUSUM-of-squares** plots to detect parameter drift without pre-specified dates.
4. **Placebo test.** Repeat the whole battery on the dates in `config/events.yml.placebos`. If any placebo gives a significant break, lower the confidence on the real break.

## Output contract
Every run writes:
- `reports/tables/break_<tag>_<YYYY-MM-DD>.csv` — table of F-stats, p-values, break dates, 95% CIs.
- `reports/figures/break_<tag>_<YYYY-MM-DD>.png` — CUSUM plot + F-statistic series.
- `reports/run_summaries/<YYYY-MM-DD>_break_<tag>.md` — one page with: model spec, series, event date, all four results, placebo comparison, confidence label, plan section reference.

## Required checks before claiming a break
- [ ] Robust to ±20 trading-day window shift? If not, reduce confidence.
- [ ] Robust to Newey-West lag choice? Report 2 lag choices (0 and HAC-optimal).
- [ ] Placebo clean?
- [ ] Economic magnitude interpretable (coefficient change explains > 0.05 in partial R²)?

Only if all four boxes tick do you write a **High** confidence claim. Otherwise Medium or Low.
