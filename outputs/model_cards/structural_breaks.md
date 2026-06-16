# Model Card - Structural Breaks

## Purpose

Diagnose whether coefficient instability aligns with major market dates.

## Inputs

Baseline BTC/ETH return regressions and macro/institutional controls.

## Sample

Baseline samples and single-break scan support.

## Method

Chow tests at ETF dates plus single-break sup-F sweep.

## Output files

`baseline_structural_breaks_summary.csv`.

## Interpretation

Regime diagnostics; not full Bai-Perron multi-break.

## Risks / limitations

Low power, multiple testing, and model dependence.

## Upgrade path

Add tested Bai-Perron or CUSUM only as clearly labeled future methods.
