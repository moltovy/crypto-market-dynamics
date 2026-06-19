# Visualization Quality Audit

Generated: 2026-06-19

Scope: `outputs/figures/F30_market_structure_dashboard.png` through `outputs/figures/F53_rotation_dashboard.png`.

## Standards Applied

- Chart form follows the relationship being shown: ranking, composition, time trend, signed change, or dashboard context.
- Color is consistent across the packet and is not the only encoding for signs or categories.
- Titles state the analytical takeaway; subtitles state source scope, units, and key caveats.
- Dense daily series are smoothed where the chart is meant to show regime movement, while raw readings remain faint context.
- Legends are replaced with direct labels where possible; dashboard legends are avoided when they collide with panel titles.
- Stacked-area views are limited to four grouped classes so composition remains readable.
- Current-top50 charts are explicitly labeled exploratory and survivorship-biased, not point-in-time top100 backtests.

## References Used

- Financial Times Visual Vocabulary: chart choice by analytical relationship.
- Urban Institute Data Visualization Style Guide: consistent typography, palette, labeling, and annotation discipline.
- Harvard Digital Accessibility data visualization guidance: accessible labels, contrast, and avoiding color-only meaning.
- CDC COVE stacked-area guidance: stacked areas should be used sparingly and with limited categories.
- Claus Wilke, *Fundamentals of Data Visualization*: titles and captions should provide context, not decoration.
- From Data to Viz: chart-type caveats and avoiding misleading encodings.

## QA Result

Verdict: pass.

Regenerated the packet with `uv run python scripts/build_market_structure_outputs.py`, visually inspected the rewritten market-structure and current-cohort PNGs, and fixed observed title/legend collisions before final verification.

Known limitation: the current-cohort daily lab remains exploratory because it uses a current-top50 cohort. The figures preserve that caveat in subtitles and report text.
