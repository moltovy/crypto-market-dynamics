# Model Card - VAR/FEVD

## Purpose

Summarize connectedness across BTC, ETH, equities, and volatility.

## Inputs

Baseline compact VAR feature set.

## Sample

Full baseline support after stationary transforms.

## Method

statsmodels VAR with 10-day FEVD under declared ordering.

## Output files

`baseline_fevd_10d_compact.csv`.

## Interpretation

Connectedness diagnostic, not structural shock identification.

## Risks / limitations

Ordering sensitivity and small-system simplification.

## Upgrade path

Add generalized FEVD and ordering-sensitivity appendices.
