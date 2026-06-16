# Model Card - Rolling Connectedness

## Purpose

Track time variation in compact VAR/FEVD total connectedness.

## Inputs

BTC, ETH, SPY, and VIX-derived return/difference features.

## Sample

252-day windows stepped every 30 days.

## Method

Fit compact VARs and compute Diebold-Yilmaz-style total connectedness from 10-day FEVD.

## Output files

`rolling_connectedness.csv`, `F77`.

## Interpretation

Highlights periods where cross-market variance accounting becomes more or less linked.

## Risks / limitations

Small VARs and BIC lag selection can be unstable in stressed windows.

## Upgrade path

Add larger asset sets, generalized FEVD, and bootstrap intervals.
