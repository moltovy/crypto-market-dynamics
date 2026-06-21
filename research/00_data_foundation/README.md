# 00_data_foundation: Data Foundation

## Research Question

What data, units, timing, coverage, identity, and release-risk constraints govern every later result?

## Evidence Summary

| measure                        |   value |
|:-------------------------------|--------:|
| provider groups                |       8 |
| raw provider files             |     584 |
| registered features            |      31 |
| processed panel columns        |     796 |
| primary-analysis features      |      25 |
| diagnostic-only features       |      69 |
| excluded features              |     103 |
| non-public provider groups     |       7 |
| identity audit non-pass checks |       0 |
| automated data-quality flags   |     153 |

## Tables

- `tables/provider_inventory.csv`
- `tables/raw_series_inventory.csv`
- `tables/feature_inventory.csv`
- `tables/feature_usage_matrix.csv`
- `tables/coverage_by_feature.csv`
- `tables/missingness_by_feature.csv`
- `tables/units_and_timing_audit.csv`
- `tables/canonical_identity_audit.csv`
- `tables/data_quality_flags.csv`
- `tables/claims.csv`

## Interpretation Boundary

This module defines admissible data, timing, units, coverage, identity, and release-risk constraints. It does not estimate market relationships by itself. Later modules must cite these tables when they use local provider inputs, engineered features, or point-in-time identity mappings.
