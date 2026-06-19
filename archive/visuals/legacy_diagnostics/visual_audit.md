# Visual Audit

## Current Canonical Figures

The pre-redesign contact sheet is `outputs/figures/current_contact_sheet.png`.

| Figure | Current story | README-ready? | Weakness | Decision |
|---|---|---:|---|---|
| F01 data coverage | Dense coverage matrix | No | Tiny labels, white background, no grouped source story | Redesign as grouped source timeline |
| F02 block attribution | Raw heatmap | No | Default colormap, cramped labels, weak hierarchy | Replace with rolling stack plus static block summary |
| F03 ETF lead-lag | Raw t-stat heatmap | No | Small labels and caveat buried in footer | Replace with lag bar card and visible association warning |
| F04 rolling correlations | Crowded line chart | Partial | Too many series, weak event markers, default legend | Reduce series and annotate regimes |
| F05 stablecoin/TVL | Basic line chart | Partial | Dual story lacks proxy caveat and context panel | Rebuild as indexed liquidity plus realized-vol context |
| F06 native dashboard | Noisy z-score lines | No | Over-plotted, hard to separate MVRV from flows | Replace with native ablation and correlation dashboard |
| F07 connectedness | Single default line | No | No FEVD matrix or ordering caveat in visual | Combine FEVD matrix with rolling connectedness |
| F08 robustness | Raw heatmap | No | Default Viridis look and little interpretation | Replace with side-by-side robustness heatmaps |

## Visual System Weaknesses

- Font: default Matplotlib sizing and no consistent hierarchy.
- Colors: white backgrounds, Viridis defaults, and inconsistent block colors.
- Layout: no card system, inconsistent aspect ratios, cramped legends.
- Annotations: event markers and interpretation guardrails were not visible enough.
- README fit: figures depended on surrounding text and were not self-contained.

## Proposed Final Figure Set

F00 summary card, F01 source coverage, F02 BTC attribution, F03 ETF lead-lag,
F04 rolling correlations, F05 stablecoin/TVL, F06 BTC-native dashboard, F07
connectedness, F08 robustness, F09 key-results cards, and T00 key-results table.

## Design Acceptance Rubric

- 16:9 README-ready PNG plus SVG for F00-F09.
- Dark institutional theme with consistent source/method footer.
- Visible title, subtitle, and interpretation caveat where relevant.
- No causal ETF-flow language.
- No Bai-Perron label for current structural-break diagnostics.
- No Shapley/Owen label for block partial R2 figures.
- README image paths resolve and avoid archived release folders.
