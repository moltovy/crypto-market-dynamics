# MVRV mechanics Model Card

## Purpose and research question

Audit same-day MVRV target overlap and lagged valuation-state regimes.

## Outcome definition

See the source tables linked from `outputs/README.md`.

## Exposures/state variables

Configured in `config/feature_registry.yml` and exported to `outputs/tables/feature_registry.csv`.

## Frequency and sample

The pipeline reports the effective sample size in every canonical model table.

## Transformations and timing

Predictive/tail-state regressors are lagged where used as state variables. Contemporaneous diagnostics are labeled separately.

## Estimator and uncertainty method

HAC OLS, logistic diagnostics, descriptive summaries, FDR adjustment, VIF/condition diagnostics, and moving-block robustness where applicable.

## Same-support rule

Model comparisons use the same non-missing row support for the relevant specification.

## Main outputs

See `outputs/tables/` and `outputs/figures/public/`.

## Interpretation

Reduced-form descriptive evidence only.

## Mechanical-link/endogeneity risks

Documented in the evidence ledger and feature registry.

## Robustness checks

Daily/weekly checks, multicollinearity diagnostics, ridge stability, and moving-block robustness are included where applicable.

## Prohibited claims

Do not call MVRV the strongest independent factor.

## Evidence grade

See `outputs/tables/evidence_ledger.csv`.

## Known limitations

Short ETF-era samples, reporting timing, source conventions, and lack of daily PIT constituent OHLCV for true historical altseason analysis.

## Reproduction command

`uv run python scripts/run_all.py`
