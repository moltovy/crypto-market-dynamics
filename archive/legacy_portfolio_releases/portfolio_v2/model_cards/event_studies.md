# Model Card - Event Studies

## Purpose

Compare abnormal BTC/ETH returns around ETF launches and selected market events.

## Inputs

Daily log returns for BTC/ETH and SPY market-model benchmark.

## Method

Market-model abnormal returns over event windows with placebo p-values.

## Outputs

`event_studies.csv` and `event_study_cars.png`.

## Interpretation

Event-window association. Not causal proof of event impact.

## Risks

Confounding news, overlapping shocks, crypto 24/7 calendar differences, and
limited sample size.

## Upgrade Path

Add alternative market benchmarks and wider placebo batteries before using event
windows as stronger evidence.
