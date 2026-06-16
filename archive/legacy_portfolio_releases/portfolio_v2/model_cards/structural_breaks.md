# Model Card - Structural-Break Diagnostics

## Purpose

Test whether ETF launch dates align with detectable coefficient instability and
scan for single unknown break dates.

## Inputs

BTC/ETH returns and selected macro/institutional regressors.

## Method

Chow tests at pre-registered ETF dates plus single-break sup-F sweeps with
placebo inference.

## Outputs

`structural_breaks_summary.csv`, `sup_f_series_btc.csv`, and
`sup_f_series_eth.csv`.

## Interpretation

Regime diagnostic only. Current implementation is not Bai-Perron multi-break.

## Risks

Low power around noisy events, multiple testing, and model-dependence.

## Upgrade Path

Add a full Bai-Perron multi-break estimator only with tested assumptions,
simulation checks, and clear separation from the current Chow/sup-F diagnostics.
