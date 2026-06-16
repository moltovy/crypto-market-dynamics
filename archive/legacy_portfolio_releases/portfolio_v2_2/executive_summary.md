# Portfolio v2.2 Executive Summary

Portfolio v2.2 is the advanced diagnostics extension for **Crypto Market Factor
Lab**. The main public portfolio release remains v2.1; v2.2 adds PCA factor
compression, exact block Shapley R2, exploratory CUSUM diagnostics, FEVD
ordering sensitivity, rolling connectedness, and a compact BTC robustness grid.

## Dataset

- Frozen panel: `2020-01-01` to `2026-04-11`
- Rows: `2293`
- Columns: `63`
- Raw `Data/` files are not refreshed or modified.

## Read First

- `technical_report.md` documents methods and caveats.
- `advanced_methods_summary.md` gives an interview-ready explanation of each
  diagnostic.
- `manifest.json` records generated artifacts, commands, and method notes.
- Model cards in `model_cards/` state purpose, inputs, outputs, interpretation,
  risks, and upgrade paths.

## Static Exact Shapley R2 Leaders

BTC:

| block    |   shapley_r2 |   full_r2 |    n |
|:---------|-------------:|----------:|-----:|
| BTC MVRV |    0.82833   |  0.920749 | 1940 |
| TradFi   |    0.0468101 |  0.920749 | 1940 |
| Macro    |    0.0423025 |  0.920749 | 1940 |

ETH:

| block     |   shapley_r2 |   full_r2 |    n |
|:----------|-------------:|----------:|-----:|
| TradFi    |   0.0938933  |  0.178544 | 1559 |
| Macro     |   0.0748966  |  0.178544 | 1559 |
| Liquidity |   0.00640645 |  0.178544 | 1559 |

## Guardrails

ETF-flow relationships are interpreted as reduced-form associations only. CUSUM
is an exploratory residual path diagnostic, not Bai-Perron. FEVD sensitivity is
ordering-sensitive VAR accounting, not structural identification.
