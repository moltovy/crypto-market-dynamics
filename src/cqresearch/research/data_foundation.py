"""Build the canonical data-foundation research module."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from config.paths import PROJECT_ROOT

from cqresearch.core.artifacts import (
    artifact_record,
    read_csv_if_exists,
    write_csv,
    write_json,
    write_text,
)
from cqresearch.pipelines.final_research import (
    PROVIDER_DISPLAY_NAMES,
    license_note,
    provider_data_disposition,
    source_file_inventory,
)
from cqresearch.research.registry import ALLOWED_USAGE_STATUSES, module_by_id

MODULE_ID = "00_data_foundation"
REQUIRED_TABLES = [
    "provider_inventory.csv",
    "raw_series_inventory.csv",
    "feature_inventory.csv",
    "feature_usage_matrix.csv",
    "coverage_by_feature.csv",
    "missingness_by_feature.csv",
    "units_and_timing_audit.csv",
    "canonical_identity_audit.csv",
    "data_quality_flags.csv",
    "claims.csv",
]


def build_data_foundation(root: Path = PROJECT_ROOT) -> list[Path]:
    """Build data-foundation tables and module documentation."""

    module = module_by_id(MODULE_ID)
    module_dir = root / "research" / MODULE_ID
    tables_dir = module_dir / "tables"
    figures_dir = module_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    raw_inventory = source_file_inventory(root)
    provider_inventory = _provider_inventory(raw_inventory)
    raw_series_inventory = _raw_series_inventory(raw_inventory, provider_inventory)
    feature_registry = _feature_registry(root)
    panel_inventory = _panel_column_inventory(root)
    current_coverage = read_csv_if_exists(root / "outputs" / "tables" / "feature_coverage.csv")
    coverage = _coverage_by_feature(feature_registry, panel_inventory, current_coverage)
    missingness = _missingness_by_feature(panel_inventory)
    usage = _feature_usage_matrix(root, feature_registry, panel_inventory, coverage)
    units = _units_and_timing_audit(root, feature_registry, panel_inventory, usage)
    identity = _canonical_identity_audit(root)
    flags = _data_quality_flags(
        provider_inventory,
        raw_series_inventory,
        feature_registry,
        panel_inventory,
        coverage,
        usage,
        units,
        identity,
    )

    artifacts = [
        write_csv(tables_dir / "provider_inventory.csv", provider_inventory),
        write_csv(tables_dir / "raw_series_inventory.csv", raw_series_inventory),
        write_csv(tables_dir / "feature_inventory.csv", feature_registry),
        write_csv(tables_dir / "feature_usage_matrix.csv", usage),
        write_csv(tables_dir / "coverage_by_feature.csv", coverage),
        write_csv(tables_dir / "missingness_by_feature.csv", missingness),
        write_csv(tables_dir / "units_and_timing_audit.csv", units),
        write_csv(tables_dir / "canonical_identity_audit.csv", identity),
        write_csv(tables_dir / "data_quality_flags.csv", flags),
        write_csv(
            tables_dir / "claims.csv",
            _claims(provider_inventory, raw_series_inventory, feature_registry, usage, flags),
        ),
    ]

    docs = _write_docs(
        root=root,
        module_dir=module_dir,
        module_title=module.title,
        research_question=module.research_question,
        provider_inventory=provider_inventory,
        raw_series_inventory=raw_series_inventory,
        feature_registry=feature_registry,
        panel_inventory=panel_inventory,
        usage=usage,
        identity=identity,
        flags=flags,
    )
    artifacts.extend(docs)
    artifacts.append(_write_manifest(root, module_dir, artifacts))
    return artifacts


def _provider_inventory(raw_inventory: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "provider_id",
        "provider",
        "file_count",
        "csv_count",
        "total_bytes",
        "first_date",
        "last_date",
        "disposition",
        "release_recommendation",
        "license_note",
    ]
    if raw_inventory.empty:
        return pd.DataFrame(columns=columns)

    coverage_rows: list[dict[str, Any]] = []
    for source_group, group in raw_inventory.groupby("source_group", dropna=False):
        starts = pd.to_datetime(group["start_date"], errors="coerce").dropna()
        ends = pd.to_datetime(group["end_date"], errors="coerce").dropna()
        coverage_rows.append(
            {
                "source_group": str(source_group),
                "file_count": int(len(group)),
                "csv_count": int((group["suffix"] == ".csv").sum()),
                "total_bytes": int(pd.to_numeric(group["size_bytes"], errors="coerce").sum()),
                "first_date": starts.min().date().isoformat() if not starts.empty else "",
                "last_date": ends.max().date().isoformat() if not ends.empty else "",
                "license_note": license_note(str(source_group)),
            }
        )
    coverage = pd.DataFrame(coverage_rows).sort_values("source_group")
    disposition = provider_data_disposition(coverage)
    merged = coverage.merge(
        disposition, on=["source_group", "file_count", "first_date", "last_date"]
    )
    merged["provider_id"] = merged["source_group"].map(_provider_id)
    merged = merged.rename(columns={"source_group": "provider"})
    return merged[columns].sort_values("provider_id").reset_index(drop=True)


def _raw_series_inventory(
    raw_inventory: pd.DataFrame, provider_inventory: pd.DataFrame
) -> pd.DataFrame:
    columns = [
        "raw_series_id",
        "provider_id",
        "provider",
        "relpath",
        "suffix",
        "rows",
        "columns",
        "start_date",
        "end_date",
        "size_bytes",
        "read_status",
        "release_disposition",
    ]
    if raw_inventory.empty:
        return pd.DataFrame(columns=columns)
    disposition = provider_inventory.set_index("provider")["disposition"].to_dict()
    frame = raw_inventory.copy()
    frame["provider"] = frame["source_group"].astype(str)
    frame["provider_id"] = frame["provider"].map(_provider_id)
    frame["raw_series_id"] = frame["relpath"].map(_slug)
    frame["read_status"] = frame["status"].fillna("indexed")
    frame["release_disposition"] = (
        frame["provider"].map(disposition).fillna("derived-only recommended")
    )
    frame = frame.rename(columns={"size_bytes": "size_bytes"})
    return frame[columns].sort_values(["provider_id", "relpath"]).reset_index(drop=True)


def _feature_registry(root: Path) -> pd.DataFrame:
    registry_path = root / "config" / "feature_registry.yml"
    rows: list[dict[str, Any]] = []
    if registry_path.exists():
        payload = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
        rows = list(payload.get("features", []))
    frame = pd.DataFrame(rows)
    required = [
        "feature_id",
        "clean_label",
        "research_block",
        "raw_source",
        "raw_path_or_endpoint",
        "raw_field",
        "frequency",
        "transformation",
        "lag_days",
        "scaling_denominator",
        "first_valid_date",
        "last_valid_date",
        "missing_policy",
        "mechanical_link_risk",
        "valuation_contamination_risk",
        "contemporaneous_endogeneity_risk",
        "permitted_model_families",
        "prohibited_uses",
        "interpretation",
    ]
    for column in required:
        if column not in frame:
            frame[column] = ""
    return frame[required].sort_values("feature_id").reset_index(drop=True)


def _panel_column_inventory(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    processed = root / "data_local" / "processed"
    if not processed.exists():
        return pd.DataFrame(
            columns=[
                "feature_id",
                "panel",
                "frequency",
                "observations",
                "missing_count",
                "missing_pct",
                "first_valid_date",
                "last_valid_date",
                "dtype",
                "numeric",
            ]
        )
    panel_files = sorted(processed.glob("*.parquet"))
    for panel_path in panel_files:
        try:
            frame = pd.read_parquet(panel_path)
        except Exception as exc:
            rows.append(
                {
                    "feature_id": "__panel_read_error__",
                    "panel": panel_path.name,
                    "frequency": _panel_frequency(panel_path.name),
                    "observations": 0,
                    "missing_count": 0,
                    "missing_pct": 1.0,
                    "first_valid_date": "",
                    "last_valid_date": "",
                    "dtype": type(exc).__name__,
                    "numeric": False,
                }
            )
            continue
        index = frame.index
        if not isinstance(index, pd.DatetimeIndex) and "date" in frame.columns:
            index = pd.to_datetime(frame["date"], errors="coerce")
        for column in frame.columns:
            series = frame[column]
            valid = series.notna()
            dates = (
                pd.to_datetime(index[valid], errors="coerce")
                if len(index) == len(series)
                else pd.Series(dtype="datetime64[ns]")
            )
            dates = pd.Series(dates).dropna()
            observations = int(valid.sum())
            missing_count = int((~valid).sum())
            rows.append(
                {
                    "feature_id": str(column),
                    "panel": panel_path.name,
                    "frequency": _panel_frequency(panel_path.name),
                    "observations": observations,
                    "missing_count": missing_count,
                    "missing_pct": float(missing_count / len(series)) if len(series) else 1.0,
                    "first_valid_date": dates.min().date().isoformat()
                    if observations and not dates.empty
                    else "",
                    "last_valid_date": dates.max().date().isoformat()
                    if observations and not dates.empty
                    else "",
                    "dtype": str(series.dtype),
                    "numeric": bool(pd.api.types.is_numeric_dtype(series)),
                }
            )
    return pd.DataFrame(rows).sort_values(["panel", "feature_id"]).reset_index(drop=True)


def _coverage_by_feature(
    feature_registry: pd.DataFrame,
    panel_inventory: pd.DataFrame,
    current_coverage: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    if not current_coverage.empty:
        coverage = current_coverage.copy()
        coverage["source"] = "legacy_feature_coverage_table"
        rows.append(coverage)
    if not panel_inventory.empty:
        panel_cov = (
            panel_inventory.groupby(["feature_id", "frequency"], dropna=False)
            .agg(
                observations=("observations", "max"),
                first_valid_date=("first_valid_date", _min_date_text),
                last_valid_date=("last_valid_date", _max_date_text),
                missing_pct=("missing_pct", "min"),
            )
            .reset_index()
        )
        panel_cov["source"] = "processed_panel_inventory"
        rows.append(panel_cov)
    if not rows:
        return pd.DataFrame(
            columns=[
                "feature_id",
                "frequency",
                "observations",
                "first_valid_date",
                "last_valid_date",
                "missing_pct",
                "source",
                "registered_feature",
            ]
        )
    combined = pd.concat(rows, ignore_index=True, sort=False)
    combined["registered_feature"] = combined["feature_id"].isin(
        set(feature_registry["feature_id"])
    )
    combined = combined[
        [
            "feature_id",
            "frequency",
            "observations",
            "first_valid_date",
            "last_valid_date",
            "missing_pct",
            "source",
            "registered_feature",
        ]
    ]
    combined["observations"] = (
        pd.to_numeric(combined["observations"], errors="coerce").fillna(0).astype(int)
    )
    combined["missing_pct"] = pd.to_numeric(combined["missing_pct"], errors="coerce")
    return combined.sort_values(["feature_id", "frequency", "source"]).reset_index(drop=True)


def _missingness_by_feature(panel_inventory: pd.DataFrame) -> pd.DataFrame:
    if panel_inventory.empty:
        return pd.DataFrame(
            columns=[
                "feature_id",
                "panel",
                "frequency",
                "observations",
                "missing_count",
                "missing_pct",
                "first_valid_date",
                "last_valid_date",
                "dtype",
                "numeric",
            ]
        )
    return panel_inventory.sort_values(["panel", "feature_id"]).reset_index(drop=True)


def _feature_usage_matrix(
    root: Path,
    feature_registry: pd.DataFrame,
    panel_inventory: pd.DataFrame,
    coverage: pd.DataFrame,
) -> pd.DataFrame:
    registered = set(feature_registry["feature_id"])
    panel_features = set(panel_inventory["feature_id"]) if not panel_inventory.empty else set()
    features = sorted(registered | panel_features)
    feature_strength = _used_features_from_tables(root)
    registry_meta = feature_registry.set_index("feature_id").to_dict("index")
    coverage_obs = (
        coverage.groupby("feature_id")["observations"].max().to_dict() if not coverage.empty else {}
    )
    panel_meta = (
        panel_inventory.groupby("feature_id")
        .agg(
            panel=("panel", lambda values: "|".join(sorted(set(map(str, values))))),
            frequency=("frequency", lambda values: "|".join(sorted(set(map(str, values))))),
        )
        .to_dict("index")
        if not panel_inventory.empty
        else {}
    )
    rows = []
    for feature_id in features:
        meta = registry_meta.get(feature_id, {})
        observations = int(coverage_obs.get(feature_id, 0) or 0)
        status, rationale = _usage_status(feature_id, meta, observations, feature_strength)
        if status not in ALLOWED_USAGE_STATUSES:
            raise ValueError(f"Invalid usage status {status} for {feature_id}")
        panel_info = panel_meta.get(feature_id, {})
        rows.append(
            {
                "feature_id": feature_id,
                "clean_label": meta.get("clean_label", feature_id.replace("_", " ").title()),
                "research_block": meta.get("research_block", "unregistered_panel_column"),
                "usage_status": status,
                "status_rationale": rationale,
                "registered_feature": feature_id in registered,
                "used_in_current_models_or_tables": feature_id in feature_strength,
                "observations_max": observations,
                "frequency": meta.get("frequency", panel_info.get("frequency", "")),
                "source_panels": panel_info.get("panel", ""),
                "raw_source": meta.get("raw_source", ""),
                "transformation": meta.get("transformation", ""),
                "lag_days": meta.get("lag_days", ""),
                "mechanical_link_risk": meta.get("mechanical_link_risk", ""),
                "valuation_contamination_risk": meta.get("valuation_contamination_risk", ""),
                "contemporaneous_endogeneity_risk": meta.get(
                    "contemporaneous_endogeneity_risk", ""
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("feature_id").reset_index(drop=True)


def _units_and_timing_audit(
    root: Path,
    feature_registry: pd.DataFrame,
    panel_inventory: pd.DataFrame,
    usage: pd.DataFrame,
) -> pd.DataFrame:
    valuation = _first_existing_csv(
        [
            root / "outputs" / "tables" / "valuation_contamination_audit.csv",
            root
            / "research"
            / "05_stablecoin_defi_liquidity"
            / "tables"
            / "valuation_contamination_audit.csv",
        ]
    )
    valuation_map = (
        valuation.groupby("feature_id")["unit_disposition"].first().to_dict()
        if not valuation.empty and "feature_id" in valuation
        else {}
    )
    registry_meta = feature_registry.set_index("feature_id").to_dict("index")
    panel_meta = (
        panel_inventory.groupby("feature_id")
        .agg(panel=("panel", lambda values: "|".join(sorted(set(map(str, values))))))
        .to_dict("index")
        if not panel_inventory.empty
        else {}
    )
    rows = []
    for item in usage.to_dict("records"):
        feature_id = str(item["feature_id"])
        meta = registry_meta.get(feature_id, {})
        rows.append(
            {
                "feature_id": feature_id,
                "frequency": item.get("frequency", meta.get("frequency", "")),
                "transformation": meta.get("transformation", "carried panel column"),
                "lag_days": meta.get("lag_days", ""),
                "scaling_denominator": meta.get("scaling_denominator", ""),
                "raw_source": meta.get("raw_source", ""),
                "raw_field": meta.get("raw_field", ""),
                "source_panels": panel_meta.get(feature_id, {}).get("panel", ""),
                "timing_disposition": _timing_disposition(feature_id, meta),
                "unit_disposition": valuation_map.get(
                    feature_id, _unit_disposition(feature_id, meta)
                ),
                "mechanical_link_risk": meta.get(
                    "mechanical_link_risk", item.get("mechanical_link_risk", "")
                ),
                "valuation_contamination_risk": meta.get(
                    "valuation_contamination_risk", item.get("valuation_contamination_risk", "")
                ),
                "contemporaneous_endogeneity_risk": meta.get(
                    "contemporaneous_endogeneity_risk",
                    item.get("contemporaneous_endogeneity_risk", ""),
                ),
                "public_language_constraint": meta.get("prohibited_uses", ""),
            }
        )
    return pd.DataFrame(rows).sort_values("feature_id").reset_index(drop=True)


def _canonical_identity_audit(root: Path) -> pd.DataFrame:
    audit = _first_existing_csv(
        [
            root / "outputs" / "tables" / "asset_identity_audit.csv",
            root
            / "research"
            / "08_relative_major_asset_risk"
            / "tables"
            / "asset_identity_audit.csv",
            root / "research" / MODULE_ID / "tables" / "canonical_identity_audit.csv",
        ]
    )
    if audit.empty:
        return pd.DataFrame(
            [
                {
                    "check_id": "asset_identity_audit_missing",
                    "symbol": "",
                    "intended_name": "",
                    "canonical_asset_key": "",
                    "observed_rows": 0,
                    "failing_rows": 0,
                    "status": "missing",
                    "note": "No canonical identity audit was present in legacy or research tables.",
                }
            ]
        )
    return audit.sort_values("check_id").reset_index(drop=True)


def _data_quality_flags(
    provider_inventory: pd.DataFrame,
    raw_series_inventory: pd.DataFrame,
    feature_registry: pd.DataFrame,
    panel_inventory: pd.DataFrame,
    coverage: pd.DataFrame,
    usage: pd.DataFrame,
    units: pd.DataFrame,
    identity: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in provider_inventory.to_dict("records"):
        if row["disposition"] != "public/re-distributable":
            rows.append(
                {
                    "flag_id": f"release_risk_{row['provider_id']}",
                    "severity": "medium",
                    "scope": "provider_release",
                    "subject": row["provider"],
                    "evidence": row["disposition"],
                    "required_action": "Publish derived outputs only unless rights are verified.",
                }
            )
    for row in raw_series_inventory.to_dict("records"):
        if str(row["read_status"]).startswith("read_error"):
            rows.append(
                {
                    "flag_id": f"raw_read_error_{row['raw_series_id']}",
                    "severity": "high",
                    "scope": "raw_series",
                    "subject": row["relpath"],
                    "evidence": row["read_status"],
                    "required_action": "Resolve parser or exclude with explicit rationale.",
                }
            )
    registered = set(feature_registry["feature_id"])
    coverage_features = set(coverage["feature_id"]) if not coverage.empty else set()
    for feature_id in sorted(registered - coverage_features):
        rows.append(
            {
                "flag_id": f"registered_no_coverage_{feature_id}",
                "severity": "medium",
                "scope": "feature_coverage",
                "subject": feature_id,
                "evidence": "Registered feature has no coverage row.",
                "required_action": "Confirm feature construction or mark unavailable.",
            }
        )
    if not panel_inventory.empty:
        high_missing = panel_inventory[
            (pd.to_numeric(panel_inventory["missing_pct"], errors="coerce") > 0.8)
            & (panel_inventory["observations"] > 0)
        ]
        for row in high_missing.head(50).to_dict("records"):
            rows.append(
                {
                    "flag_id": f"high_missing_{_slug(row['panel'] + '_' + row['feature_id'])}",
                    "severity": "low",
                    "scope": "panel_missingness",
                    "subject": f"{row['panel']}::{row['feature_id']}",
                    "evidence": f"missing_pct={row['missing_pct']:.3f}",
                    "required_action": "Use complete-case samples and report effective n.",
                }
            )
    bad_identity = (
        identity[~identity["status"].isin(["pass"])] if "status" in identity else identity
    )
    for row in bad_identity.to_dict("records"):
        rows.append(
            {
                "flag_id": f"identity_{row.get('check_id', 'unknown')}",
                "severity": "high",
                "scope": "canonical_identity",
                "subject": row.get("symbol", ""),
                "evidence": row.get("status", "unknown"),
                "required_action": "Do not use affected identity mapping until resolved.",
            }
        )
    for row in units.to_dict("records"):
        if "unknown" in str(row["unit_disposition"]).lower():
            rows.append(
                {
                    "flag_id": f"unit_unknown_{row['feature_id']}",
                    "severity": "medium",
                    "scope": "units",
                    "subject": row["feature_id"],
                    "evidence": row["unit_disposition"],
                    "required_action": "Resolve unit before using outside diagnostics.",
                }
            )
    if not rows:
        rows.append(
            {
                "flag_id": "no_blocking_data_quality_flags",
                "severity": "info",
                "scope": "data_foundation",
                "subject": "data_foundation",
                "evidence": "No blocking data-quality flags produced by automated checks.",
                "required_action": "Continue manual review for visual and empirical claims.",
            }
        )
    return pd.DataFrame(rows).sort_values(["severity", "flag_id"]).reset_index(drop=True)


def _write_docs(
    root: Path,
    module_dir: Path,
    module_title: str,
    research_question: str,
    provider_inventory: pd.DataFrame,
    raw_series_inventory: pd.DataFrame,
    feature_registry: pd.DataFrame,
    panel_inventory: pd.DataFrame,
    usage: pd.DataFrame,
    identity: pd.DataFrame,
    flags: pd.DataFrame,
) -> list[Path]:
    restricted = int(
        provider_inventory["disposition"].ne("public/re-distributable").sum()
        if not provider_inventory.empty
        else 0
    )
    identity_failures = int(
        identity["status"].ne("pass").sum() if "status" in identity and not identity.empty else 0
    )
    primary_features = int((usage["usage_status"] == "primary_analysis").sum())
    diagnostic_features = int((usage["usage_status"] == "diagnostic_only").sum())
    excluded_features = int(usage["usage_status"].str.startswith("excluded_").sum())
    table_list = "\n".join(f"- `tables/{name}`" for name in REQUIRED_TABLES)
    summary = pd.DataFrame(
        [
            {"measure": "provider groups", "value": len(provider_inventory)},
            {"measure": "raw provider files", "value": len(raw_series_inventory)},
            {"measure": "registered features", "value": len(feature_registry)},
            {"measure": "processed panel columns", "value": len(panel_inventory)},
            {"measure": "primary-analysis features", "value": primary_features},
            {"measure": "diagnostic-only features", "value": diagnostic_features},
            {"measure": "excluded features", "value": excluded_features},
            {"measure": "non-public provider groups", "value": restricted},
            {"measure": "identity audit non-pass checks", "value": identity_failures},
            {"measure": "automated data-quality flags", "value": len(flags)},
        ]
    )
    docs = [
        write_text(
            module_dir / "README.md",
            f"""# {MODULE_ID}: {module_title}

## Research Question

{research_question}

## Evidence Summary

{summary.to_markdown(index=False)}

## Tables

{table_list}

## Interpretation Boundary

This module defines admissible data, timing, units, coverage, identity, and release-risk constraints. It does not estimate market relationships by itself. Later modules must cite these tables when they use local provider inputs, engineered features, or point-in-time identity mappings.
""",
        ),
        write_text(
            module_dir / "methodology.md",
            """# Methodology

Raw-file inventory is generated by scanning `data_local/raw/` and recording provider group, file size, suffix, readable row/column counts, and detected date ranges. Provider disposition is assigned with the repository data-governance rules and does not grant redistribution permission.

Feature inventory is read from `config/feature_registry.yml`. Coverage and missingness combine committed semantic output coverage with processed parquet panel columns under `data_local/processed/`.

The usage matrix assigns exactly one status from the allowed status set to each registered feature and processed panel column. Status assignment uses current model/table references, coverage, timing, unit-risk metadata, and whether the item is a raw carried level, engineered feature, or diagnostics-only field.

Canonical identity checks are migrated from the current research identity audit when present. Missing or non-pass identity checks are high-severity data-quality flags.
""",
        ),
        write_text(
            module_dir / "findings.md",
            f"""# Findings

- The local raw universe has {len(raw_series_inventory)} files across {len(provider_inventory)} provider groups.
- {restricted} provider groups are not classified as public/re-distributable, so public artifacts must remain derived outputs unless rights are separately verified.
- The configured registry contains {len(feature_registry)} features; processed panels expose {len(panel_inventory)} panel-column entries across local parquet artifacts.
- The usage matrix assigns {primary_features} primary-analysis, {diagnostic_features} diagnostic-only, and {excluded_features} excluded statuses.
- The canonical identity audit has {identity_failures} non-pass checks.
- Automated data-quality review emitted {len(flags)} flags. Severity and required action are in `tables/data_quality_flags.csv`.
""",
        ),
        write_text(
            module_dir / "interpretation.md",
            """# Interpretation

Data-foundation tables define constraints rather than results. A feature marked `primary_analysis` is admissible for the current descriptive research design, not necessarily strong or stable. A `diagnostic_only` status means the series can explain measurement mechanics, coverage, identity, timing, or units, but should not be promoted into a headline empirical claim.

Provider disposition is a release-risk classification. It does not change whether a local build may use the data; it changes what the public repository should publish.
""",
        ),
        write_text(
            module_dir / "limitations.md",
            """# Limitations

- File-level inventory cannot prove provider licensing terms.
- CSV date detection is heuristic and depends on recognized date-column names.
- Panel columns that are not registered features are conservatively classified from names, coverage, and observed use; each high-value unregistered feature still needs manual review before becoming a public claim.
- This module audits availability and semantics. It does not validate visual design, statistical stability, or economic interpretation in later modules.
""",
        ),
    ]
    module_yml = {
        "module_id": MODULE_ID,
        "title": module_title,
        "research_question": research_question,
        "research_questions": [research_question],
        "outcomes": [
            "provider inventory",
            "raw series coverage",
            "feature usage status",
            "unit and timing audit",
            "release-risk classification",
        ],
        "features": [
            "all discovered raw files",
            "configured feature registry entries",
            "processed panel columns",
        ],
        "frequencies": ["file-level inventory", "daily", "weekly", "monthly"],
        "methods": [
            "filesystem inventory",
            "feature registry reconciliation",
            "coverage and missingness audit",
            "unit and timing classification",
            "release-risk review",
        ],
        "sensitivity_dimensions": [
            "registered versus unregistered features",
            "public versus restricted provider disposition",
            "coverage and missingness thresholds",
        ],
        "status": "built",
        "canonical_surface": (module_dir.relative_to(root)).as_posix(),
        "tables": REQUIRED_TABLES,
        "figures": [],
        "code": [
            "src/cqresearch/research/data_foundation.py",
            "src/cqresearch/pipelines/research.py",
        ],
        "tests": [
            "tests/unit/test_config_yamls.py",
            "tests/unit/test_feature_strength_outputs.py",
        ],
        "root_readme_candidate_figures": [],
        "source_inputs": [
            "data_local/raw/",
            "data_local/processed/",
            "config/feature_registry.yml",
            "research/08_relative_major_asset_risk/tables/asset_identity_audit.csv",
            "research/05_stablecoin_defi_liquidity/tables/valuation_contamination_audit.csv",
        ],
    }
    docs.append(write_text(module_dir / "module.yml", yaml.safe_dump(module_yml, sort_keys=False)))
    return docs


def _write_manifest(root: Path, module_dir: Path, artifacts: list[Path]) -> Path:
    manifest = {
        "module_id": MODULE_ID,
        "schema_version": 1,
        "build_timestamp_utc": "not_recorded_for_deterministic_rebuilds",
        "artifacts": [artifact_record(path, root) for path in sorted(artifacts)],
    }
    return write_json(module_dir / "manifest.json", manifest)


def _claims(
    provider_inventory: pd.DataFrame,
    raw_series_inventory: pd.DataFrame,
    feature_registry: pd.DataFrame,
    usage: pd.DataFrame,
    flags: pd.DataFrame,
) -> pd.DataFrame:
    rows = [
        {
            "claim_id": "data_foundation_inventory_01",
            "module_id": MODULE_ID,
            "claim_text": (
                f"The local inventory covers {len(raw_series_inventory)} raw files across "
                f"{len(provider_inventory)} provider groups and {len(feature_registry)} registered features."
            ),
            "sample": "Files currently present under data_local/raw and processed local panels.",
            "method": "File-system inventory, feature-registry parse, and processed-panel column audit.",
            "uncertainty": "Licensing and source terms are classified as release risk, not legal permission.",
            "evidence_grade": "A for local file inventory; B for release-risk classification.",
            "source_table": "tables/provider_inventory.csv; tables/raw_series_inventory.csv; tables/feature_inventory.csv",
            "source_figure": "",
            "limitation": "Date detection and unit classification require manual review for unregistered columns.",
            "status": "accepted_qualified",
        },
        {
            "claim_id": "data_foundation_usage_01",
            "module_id": MODULE_ID,
            "claim_text": (
                f"Every discovered registered feature or processed panel column has exactly one usage status; "
                f"{int((usage['usage_status'] == 'primary_analysis').sum())} are marked primary_analysis."
            ),
            "sample": "Union of feature registry entries and processed parquet panel columns.",
            "method": "Deterministic status assignment using registration, coverage, model/table use, unit risk, and timing metadata.",
            "uncertainty": "Unregistered panel columns remain review debt until promoted or excluded by a module-specific decision.",
            "evidence_grade": "B",
            "source_table": "tables/feature_usage_matrix.csv; tables/data_quality_flags.csv",
            "source_figure": "",
            "limitation": f"Automated review produced {len(flags)} data-quality flags for release risk, missingness, or unit review.",
            "status": "accepted_qualified",
        },
    ]
    for row in rows:
        _extend_claim(row)
    return pd.DataFrame(rows)


def _extend_claim(row: dict[str, Any]) -> None:
    claim_text = str(row.get("claim_text", ""))
    row.setdefault("module", row.get("module_id", ""))
    row.setdefault("finding", claim_text)
    row.setdefault("outcome", "data foundation")
    row.setdefault("feature_or_block", "all discovered local features")
    row.setdefault("estimate_summary", claim_text)
    row.setdefault("uncertainty_summary", row.get("uncertainty", "See source table."))
    row.setdefault("sample_summary", row.get("sample", "See source table."))
    row.setdefault("frequency", "mixed local source frequencies")
    row.setdefault("timing", "source-specific timing audited in units_and_timing_audit.csv")
    row.setdefault("sensitivity_summary", row.get("method", "See source table."))
    row.setdefault("interpretation", claim_text)
    row.setdefault("alternative_explanation", row.get("limitation", "See module limitations."))
    row.setdefault("source_model_ids", _model_ids_from_source_tables(row.get("source_table", "")))


def _model_ids_from_source_tables(source_table: Any) -> str:
    ids: list[str] = []
    for item in str(source_table).replace(",", ";").split(";"):
        item = item.strip()
        if item:
            ids.append(f"table:{Path(item).stem}")
    return "; ".join(ids) or "table:claims"


def _used_features_from_tables(root: Path) -> set[str]:
    used: set[str] = set()
    for table_name in [
        "btc_ex_mvrv_feature_strength.csv",
        "eth_feature_strength.csv",
        "fdr_adjusted_inference.csv",
        "multicollinearity_diagnostics.csv",
        "ridge_stability.csv",
        "tail_risk_models.csv",
        "liquidity_associations.csv",
        "valuation_contamination_audit.csv",
    ]:
        frame = _first_existing_csv(_candidate_research_tables(root, table_name))
        if not frame.empty and "feature_id" in frame:
            used.update(frame["feature_id"].dropna().astype(str))
        if not frame.empty and "liquidity_feature" in frame:
            used.update(frame["liquidity_feature"].dropna().astype(str))
    block = _first_existing_csv(_candidate_research_tables(root, "block_delta_r2.csv"))
    if not block.empty:
        for column in ["feature_list", "dropped_features"]:
            if column in block:
                for value in block[column].dropna().astype(str):
                    used.update(part for part in value.split("|") if part)
    return used


def _usage_status(
    feature_id: str,
    meta: dict[str, Any],
    observations: int,
    used_features: set[str],
) -> tuple[str, str]:
    if observations == 0 and not meta:
        return "excluded_insufficient_coverage", "Unregistered panel field has no observed values."
    if observations and observations < 40:
        return (
            "excluded_insufficient_coverage",
            "Coverage below the minimum descriptive-analysis threshold.",
        )
    if "date" in feature_id.lower() or feature_id in {
        "calendar",
        "calendar_assumption",
        "close_time_assumption",
    }:
        return "diagnostic_only", "Calendar or timing metadata."
    if not meta:
        if _looks_like_raw_level(feature_id):
            return (
                "diagnostic_only",
                "Unregistered carried level used for denominators, timing, or construction checks.",
            )
        return (
            "excluded_definition_or_unit_ambiguity",
            "Unregistered panel column requires definition review before public use.",
        )
    risk = str(meta.get("mechanical_link_risk", "")).lower()
    valuation = str(meta.get("valuation_contamination_risk", "")).lower()
    block = str(meta.get("research_block", "")).lower()
    if feature_id in {"d_log_mvrv", "d_log_market_cap", "d_log_realized_cap", "identity_residual"}:
        return (
            "diagnostic_only",
            "MVRV identity component or residual used for measurement mechanics.",
        )
    if "mvrv" in feature_id and "lag" not in feature_id:
        return "diagnostic_only", "Same-day MVRV-related field is mechanically linked to price."
    if "high_usd_price_content" in valuation:
        return (
            "robustness_or_sensitivity",
            "USD valuation-sensitive proxy must be audited against price content.",
        )
    if "unknown" in risk or "unknown" in valuation:
        return "excluded_definition_or_unit_ambiguity", "Risk or unit metadata is unresolved."
    if feature_id in used_features or block in {
        "target",
        "macro_risk",
        "etf_institutional",
        "leverage",
        "liquidity",
        "onchain_state",
        "market_structure",
    }:
        return (
            "primary_analysis",
            "Registered and used in current semantic models or module tables.",
        )
    return (
        "robustness_or_sensitivity",
        "Registered feature retained for sensitivity or future module review.",
    )


def _timing_disposition(feature_id: str, meta: dict[str, Any]) -> str:
    lag = str(meta.get("lag_days", ""))
    if lag and lag not in {"0", "0.0"}:
        return f"lagged by {lag} day(s) or period(s) as registered"
    if "lag" in feature_id:
        return "lagged by feature construction"
    if "ret" in feature_id or "return" in str(meta.get("clean_label", "")).lower():
        return "same-period outcome or contemporaneous exposure"
    return "level or state variable; inspect transformation and calendar before modeling"


def _unit_disposition(feature_id: str, meta: dict[str, Any]) -> str:
    denominator = str(meta.get("scaling_denominator", ""))
    if denominator:
        return f"scaled by {denominator}"
    if feature_id.endswith("_ret") or "return" in str(meta.get("clean_label", "")).lower():
        return "log return or return-like transformation"
    if "usd" in feature_id or "tvl" in feature_id:
        return (
            "USD-valued series; inspect valuation contamination before causal or liquidity language"
        )
    if not meta:
        return "unknown unit for unregistered panel column"
    return "registered unit and transformation"


def _looks_like_raw_level(feature_id: str) -> bool:
    terms = [
        "_close",
        "_level",
        "_usd",
        "_mcap",
        "market_cap",
        "realized_cap",
        "_oi",
        "funding",
        "dominance",
        "calendar",
    ]
    return any(term in feature_id.lower() for term in terms)


def _provider_id(source_group: str) -> str:
    reverse = {display: key for key, display in PROVIDER_DISPLAY_NAMES.items()}
    return reverse.get(str(source_group), _slug(str(source_group)))


def _first_existing_csv(paths: list[Path]) -> pd.DataFrame:
    for path in paths:
        if path.exists():
            return read_csv_if_exists(path)
    return pd.DataFrame()


def _candidate_research_tables(root: Path, table_name: str) -> list[Path]:
    return [
        root / "outputs" / "tables" / table_name,
        *sorted((root / "research").glob(f"*/tables/{table_name}")),
    ]


def _slug(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return clean or "unknown"


def _panel_frequency(name: str) -> str:
    lower = name.lower()
    if "monthly" in lower:
        return "monthly"
    if "weekly" in lower:
        return "weekly"
    if "daily" in lower:
        return "daily"
    return "unknown"


def _min_date_text(values: pd.Series) -> str:
    dates = pd.to_datetime(values, errors="coerce").dropna()
    return dates.min().date().isoformat() if not dates.empty else ""


def _max_date_text(values: pd.Series) -> str:
    dates = pd.to_datetime(values, errors="coerce").dropna()
    return dates.max().date().isoformat() if not dates.empty else ""
