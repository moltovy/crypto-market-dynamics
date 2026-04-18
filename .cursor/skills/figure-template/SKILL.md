---
name: figure-template
description: Produce publication-grade matplotlib figures using the project palette, rcParams, and citation footer. Use whenever creating any figure destined for reports/ or the paper.
---

# figure-template

## Non-negotiables
- Use `src/cqresearch/viz/palette.py` (block colors are mirrored from `config/factor_blocks.yml`).
- Use `src/cqresearch/viz/rcparams.py` (font, dpi, size, tick style).
- No emojis, no rainbow colormaps, no default `C0..C9` colors.
- Output two files at 300 dpi: `.png` for draft review, `.pdf` for paper build.

## Required elements
1. Title at the top-left (no centering), 12pt bold.
2. Source line at bottom-left, 8pt grey:
   `Source: Data/FRED/..., Data/CryptoQuant/... — computed YYYY-MM-DD`
3. Plan citation at bottom-right, 8pt grey:
   `project_research_plan.md §X.Y`
4. For time series: shaded bands at pre-registered events from `config/events.yml` (annotated once on the rightmost axis).
5. For FEVD / connectedness: values in cell, symmetric row/col order, block-color row/col labels.

## Filenames
`reports/figures/<section>_<fig-id>_<tag>_<YYYY-MM-DD>.{png,pdf}`
Example: `reports/figures/f03_rolling_partial_r2_btc_2026-04-18.pdf`.

## Run summary
Every figure ships with a markdown entry in `reports/run_summaries/<date>_figure_<fig-id>.md` listing:
- Inputs (file paths).
- Method (source function in `src/cqresearch/viz/`).
- Parameter block (window, model spec, block membership).
- Confidence label.

## Anti-patterns
- Screenshotting a Jupyter cell. Always re-render from code.
- Manually setting per-line colors. Always use the palette.
- Saving only PNG (we need PDF for the paper).
- Figure without a spec reference.
