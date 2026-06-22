# Methodology

The data foundation scans `data_local/raw/`, parses `config/feature_registry.yml`, audits processed parquet panels under `data_local/processed/`, and reconciles selected-asset identity outputs where present.

The usage matrix assigns exactly one of the allowed statuses: `primary_analysis`, `robustness_or_sensitivity`, `diagnostic_only`, `excluded_insufficient_coverage`, `excluded_ambiguous_definition_or_unit`, `excluded_duplicate`, or `excluded_release_risk`.

Provider disposition governs what can be published. Local provider inputs may support deterministic private rebuilds while public artifacts remain derived semantic outputs.
