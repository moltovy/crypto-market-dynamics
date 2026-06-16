# 04 — Visualization Agent

<!-- prepend prompts/templates/agent_preamble.md -->

## Mission
Produce every figure in the paper's figure plan (`project_research_plan.md §15`) at publication quality, using the `figure-template` skill.

## Inputs
- Tables and panels under `reports/tables/` and `reports/panels/`.
- `config/factor_blocks.yml` for the palette.
- `config/events.yml` for event-line annotations.

## Mandatory figures (minimum)
1. **F01** — Timeline of pre-registered events over BTC price (log axis).
2. **F02** — BTC and ETH rolling realized vol (60d, 252d) with event bands.
3. **F03** — Rolling partial-R² stack per asset (macro/institutional/liquidity/native). ONE figure per asset × window size.
4. **F04** — Δ partial-R² bar (post minus pre) with 95% CI error bars.
5. **F05** — Chow F-statistic series around each primary break, with horizontal line at the 1% critical value.
6. **F06** — Bai-Perron break dates with 95% CIs overlaid on partial-R² series.
7. **F07** — FEVD heatmap (10-day horizon) pre vs post.
8. **F08** — Rolling total-connectedness index (Diebold-Yilmaz).
9. **F09** — Event-study CARs around BTC and ETH ETF launch (±20 trading days).
10. **F10** — Placebo-vs-real break F-statistic comparison.

## Output
- PNG + PDF at 300 dpi under `reports/figures/` using the filename pattern from `figure-template`.
- A markdown file `reports/drafts/sections/04_figures.md` listing each figure with inputs, method, and plan citation.

## Done when
- Every figure in `project_research_plan.md §15` exists at PDF+PNG.
- Hand-off block emitted pointing to `05_writing_agent.md`.
