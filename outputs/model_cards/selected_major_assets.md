# Selected majors and chain fundamentals Model Card

## Purpose and research question

Compare coverage-aware volatility, drawdown, and beta metrics.

## Outcome definition

See the source tables linked from `outputs/README.md`.

## Exposures/state variables

Configured in `config/feature_registry.yml` and exported to `outputs/tables/feature_registry.csv`.

## Frequency and sample

The pipeline reports the effective sample size in every canonical model table.

## Transformations and timing

Contemporaneous exposure models use same-day TradFi returns/changes to measure co-movement. Lagged liquidity, sentiment, leverage, funding, OI, and exchange-flow variables are labeled lagged-state associations. ETF-era augmented models include ETF flow intensity at lag 0 and lag 1.

## Estimator and uncertainty method

HAC OLS, logistic diagnostics, descriptive summaries, FDR adjustment, VIF/condition diagnostics, accepted weekly robustness models, and local-window correlation distributions where applicable.

## Same-support rule

Model comparisons use the same non-missing row support for the relevant specification.

## Main outputs

See `outputs/tables/` and `outputs/figures/public/`.

## Interpretation

Reduced-form descriptive evidence only.

## Mechanical-link/endogeneity risks

Documented in the evidence ledger and feature registry.

## Robustness checks

Accepted daily/weekly checks, multicollinearity diagnostics, ridge stability, and local-window correlation distributions are included where applicable.

## Prohibited claims

Do not compare unequal histories as if identical.

## Evidence grade

See `outputs/tables/evidence_ledger.csv`.

## Known limitations

Short ETF-era samples, reporting timing, source conventions, and lack of daily PIT constituent OHLCV for true historical altseason analysis.

## Reproduction command

`uv run python scripts/run_all.py`
