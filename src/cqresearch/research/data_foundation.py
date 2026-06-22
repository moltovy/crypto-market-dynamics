"""Build the canonical data and measurement foundation module."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
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
    SELECTED_ASSETS,
    license_note,
    provider_data_disposition,
    source_file_inventory,
)
from cqresearch.research.registry import ALLOWED_USAGE_STATUSES, module_by_id
from cqresearch.viz.theme import PALETTE, TOKENS, add_figure_header, apply_theme, style_axis

MODULE_ID = "00_data_measurement_foundation"

REQUIRED_TABLES = [
    "provider_inventory.csv",
    "raw_file_inventory.csv",
    "raw_series_inventory.csv",
    "feature_inventory.csv",
    "feature_usage_matrix.csv",
    "asset_universe_audit.csv",
    "chain_token_mapping_audit.csv",
    "coverage_missingness.csv",
    "units_timing_scaling_audit.csv",
    "measurement_risk_audit.csv",
    "claims.csv",
]


def build_data_foundation(root: Path = PROJECT_ROOT) -> list[Path]:
    """Build data-governance tables, figures, docs, and manifest."""

    module = module_by_id(MODULE_ID)
    module_dir = root / "research" / MODULE_ID
    tables_dir = module_dir / "tables"
    figures_dir = module_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    raw_files = _raw_file_inventory(root)
    providers = _provider_inventory(raw_files)
    raw_series = _raw_series_inventory(raw_files, providers)
    feature_inventory = _feature_inventory(root)
    panel_inventory = _panel_inventory(root)
    usage = _feature_usage_matrix(feature_inventory, panel_inventory)
    coverage = _coverage_missingness(feature_inventory, panel_inventory)
    units = _units_timing_scaling_audit(feature_inventory, panel_inventory, usage)
    assets = _asset_universe_audit(root)
    mapping = _chain_token_mapping_audit(root, assets)
    measurement = _measurement_risk_audit(providers, feature_inventory, usage, units, assets)
    claims = _claims(providers, raw_series, feature_inventory, usage, measurement)

    artifacts = [
        write_csv(tables_dir / "provider_inventory.csv", providers),
        write_csv(tables_dir / "raw_file_inventory.csv", raw_files),
        write_csv(tables_dir / "raw_series_inventory.csv", raw_series),
        write_csv(tables_dir / "feature_inventory.csv", feature_inventory),
        write_csv(tables_dir / "feature_usage_matrix.csv", usage),
        write_csv(tables_dir / "asset_universe_audit.csv", assets),
        write_csv(tables_dir / "chain_token_mapping_audit.csv", mapping),
        write_csv(tables_dir / "coverage_missingness.csv", coverage),
        write_csv(tables_dir / "units_timing_scaling_audit.csv", units),
        write_csv(tables_dir / "measurement_risk_audit.csv", measurement),
        write_csv(tables_dir / "claims.csv", claims),
    ]
    for figure in _write_figures(figures_dir, providers, usage, coverage):
        artifacts.append(figure)
        if figure.with_suffix(".svg").exists():
            artifacts.append(figure.with_suffix(".svg"))
    artifacts.extend(
        _write_docs(
            root=root,
            module_dir=module_dir,
            title=module.title,
            research_question=module.research_question,
            providers=providers,
            raw_series=raw_series,
            feature_inventory=feature_inventory,
            usage=usage,
            assets=assets,
            measurement=measurement,
        )
    )
    artifacts.append(_write_manifest(root, module_dir, artifacts))
    return artifacts


def _raw_file_inventory(root: Path) -> pd.DataFrame:
    frame = source_file_inventory(root)
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "raw_file_id",
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
        )
    frame = frame.copy()
    frame["provider"] = frame["source_group"].astype(str)
    frame["raw_file_id"] = frame["relpath"].map(_slug)
    frame["read_status"] = frame.get("status", "indexed")
    disposition = provider_data_disposition(
        frame.groupby("source_group", dropna=False)
        .agg(
            file_count=("relpath", "count"),
            first_date=("start_date", _min_date_text),
            last_date=("end_date", _max_date_text),
        )
        .reset_index()
    )
    disposition_map = disposition.set_index("source_group")["disposition"].to_dict()
    frame["release_disposition"] = (
        frame["source_group"].map(disposition_map).fillna("derived-only recommended")
    )
    columns = [
        "raw_file_id",
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
    for column in columns:
        if column not in frame:
            frame[column] = ""
    return frame[columns].sort_values(["provider", "relpath"]).reset_index(drop=True)


def _provider_inventory(raw_files: pd.DataFrame) -> pd.DataFrame:
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
    if raw_files.empty:
        return pd.DataFrame(columns=columns)
    grouped = (
        raw_files.groupby("provider", dropna=False)
        .agg(
            file_count=("relpath", "count"),
            csv_count=("suffix", lambda value: int((value == ".csv").sum())),
            total_bytes=(
                "size_bytes",
                lambda value: int(pd.to_numeric(value, errors="coerce").sum()),
            ),
            first_date=("start_date", _min_date_text),
            last_date=("end_date", _max_date_text),
        )
        .reset_index()
    )
    disposition_input = grouped.rename(columns={"provider": "source_group"})
    disposition = provider_data_disposition(disposition_input)
    merged = grouped.merge(
        disposition.rename(columns={"source_group": "provider"}),
        on=["provider", "file_count", "first_date", "last_date"],
        how="left",
    )
    merged["provider_id"] = merged["provider"].map(_provider_id)
    merged["license_note"] = merged["provider"].map(lambda value: license_note(str(value)))
    return merged[columns].sort_values("provider_id").reset_index(drop=True)


def _raw_series_inventory(raw_files: pd.DataFrame, providers: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "raw_series_id",
        "provider_id",
        "provider",
        "relpath",
        "rows",
        "columns",
        "start_date",
        "end_date",
        "read_status",
        "release_disposition",
        "series_granularity",
    ]
    if raw_files.empty:
        return pd.DataFrame(columns=columns)
    provider_ids = providers.set_index("provider")["provider_id"].to_dict()
    frame = raw_files.copy()
    frame["raw_series_id"] = frame["raw_file_id"]
    frame["provider_id"] = frame["provider"].map(provider_ids).fillna(frame["provider"].map(_slug))
    frame["series_granularity"] = frame["relpath"].map(_series_granularity)
    return frame[columns].sort_values(["provider_id", "relpath"]).reset_index(drop=True)


def _feature_inventory(root: Path) -> pd.DataFrame:
    registry_path = root / "config" / "feature_registry.yml"
    payload = (
        yaml.safe_load(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
    )
    frame = pd.DataFrame(payload.get("features", []) if isinstance(payload, dict) else [])
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


def _panel_inventory(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted((root / "data_local" / "processed").glob("*.parquet")):
        try:
            frame = pd.read_parquet(path)
        except Exception as exc:
            rows.append(
                {
                    "feature_id": "__panel_read_error__",
                    "panel": path.name,
                    "frequency": _panel_frequency(path.name),
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
        if not isinstance(index, pd.DatetimeIndex) and "date" in frame:
            index = pd.to_datetime(frame["date"], errors="coerce")
        for column in frame.columns:
            series = frame[column]
            valid = series.notna()
            if len(index) == len(series):
                dates = pd.Series(pd.to_datetime(index[valid], errors="coerce")).dropna()
            else:
                dates = pd.Series(dtype="datetime64[ns]")
            rows.append(
                {
                    "feature_id": str(column),
                    "panel": path.name,
                    "frequency": _panel_frequency(path.name),
                    "observations": int(valid.sum()),
                    "missing_count": int((~valid).sum()),
                    "missing_pct": float((~valid).sum() / len(series)) if len(series) else 1.0,
                    "first_valid_date": dates.min().date().isoformat() if not dates.empty else "",
                    "last_valid_date": dates.max().date().isoformat() if not dates.empty else "",
                    "dtype": str(series.dtype),
                    "numeric": bool(pd.api.types.is_numeric_dtype(series)),
                }
            )
    return pd.DataFrame(rows).sort_values(["panel", "feature_id"]).reset_index(drop=True)


def _feature_usage_matrix(
    feature_inventory: pd.DataFrame, panel_inventory: pd.DataFrame
) -> pd.DataFrame:
    registered = set(feature_inventory["feature_id"])
    panel_features = set(panel_inventory["feature_id"]) if not panel_inventory.empty else set()
    feature_ids = sorted(registered | panel_features)
    meta = feature_inventory.set_index("feature_id").to_dict("index")
    coverage = (
        panel_inventory.groupby("feature_id")["observations"].max().to_dict()
        if not panel_inventory.empty
        else {}
    )
    panel_meta = (
        panel_inventory.groupby("feature_id")
        .agg(
            source_panels=("panel", lambda value: "|".join(sorted(set(map(str, value))))),
            frequency=("frequency", lambda value: "|".join(sorted(set(map(str, value))))),
        )
        .to_dict("index")
        if not panel_inventory.empty
        else {}
    )
    rows: list[dict[str, Any]] = []
    for feature_id in feature_ids:
        item = meta.get(feature_id, {})
        observations = int(coverage.get(feature_id, 0) or 0)
        status, rationale = _usage_status(feature_id, item, observations)
        if status not in ALLOWED_USAGE_STATUSES:
            raise ValueError(f"Invalid usage status {status} for {feature_id}")
        pmeta = panel_meta.get(feature_id, {})
        rows.append(
            {
                "feature_id": feature_id,
                "clean_label": item.get("clean_label", feature_id.replace("_", " ").title()),
                "research_block": item.get("research_block", "unregistered_panel_column"),
                "usage_status": status,
                "status_rationale": rationale,
                "registered_feature": feature_id in registered,
                "observations_max": observations,
                "frequency": item.get("frequency", pmeta.get("frequency", "")),
                "source_panels": pmeta.get("source_panels", ""),
                "raw_source": item.get("raw_source", ""),
                "transformation": item.get("transformation", ""),
                "lag_days": item.get("lag_days", ""),
                "scaling_denominator": item.get("scaling_denominator", ""),
                "mechanical_link_risk": item.get("mechanical_link_risk", ""),
                "valuation_contamination_risk": item.get("valuation_contamination_risk", ""),
                "contemporaneous_endogeneity_risk": item.get(
                    "contemporaneous_endogeneity_risk", ""
                ),
            }
        )
    return pd.DataFrame(rows).sort_values("feature_id").reset_index(drop=True)


def _coverage_missingness(
    feature_inventory: pd.DataFrame, panel_inventory: pd.DataFrame
) -> pd.DataFrame:
    registered = feature_inventory[["feature_id", "research_block"]].copy()
    if panel_inventory.empty:
        registered["panel"] = ""
        registered["frequency"] = registered.get("frequency", "")
        registered["observations"] = 0
        registered["missing_count"] = 0
        registered["missing_pct"] = 1.0
        registered["first_valid_date"] = ""
        registered["last_valid_date"] = ""
        registered["coverage_rule"] = "registered feature; no local processed panel coverage"
        return registered
    merged = panel_inventory.merge(registered, on="feature_id", how="outer")
    merged["coverage_rule"] = "registered or discovered processed-panel column"
    for column in ["observations", "missing_count"]:
        merged[column] = pd.to_numeric(merged[column], errors="coerce").fillna(0).astype(int)
    merged["missing_pct"] = pd.to_numeric(merged["missing_pct"], errors="coerce").fillna(1.0)
    return (
        merged[
            [
                "feature_id",
                "research_block",
                "panel",
                "frequency",
                "observations",
                "missing_count",
                "missing_pct",
                "first_valid_date",
                "last_valid_date",
                "coverage_rule",
            ]
        ]
        .sort_values(["feature_id", "panel"])
        .reset_index(drop=True)
    )


def _units_timing_scaling_audit(
    feature_inventory: pd.DataFrame, panel_inventory: pd.DataFrame, usage: pd.DataFrame
) -> pd.DataFrame:
    meta = feature_inventory.set_index("feature_id").to_dict("index")
    panel_meta = (
        panel_inventory.groupby("feature_id")
        .agg(panel=("panel", lambda values: "|".join(sorted(set(map(str, values))))))
        .to_dict("index")
        if not panel_inventory.empty
        else {}
    )
    rows = []
    for row in usage.to_dict("records"):
        feature_id = str(row["feature_id"])
        item = meta.get(feature_id, {})
        rows.append(
            {
                "feature_id": feature_id,
                "frequency": row.get("frequency", item.get("frequency", "")),
                "transformation": item.get("transformation", "carried panel column"),
                "lag_days": item.get("lag_days", ""),
                "scaling_denominator": item.get("scaling_denominator", ""),
                "source_panels": panel_meta.get(feature_id, {}).get("panel", ""),
                "timing_disposition": _timing_disposition(feature_id, item),
                "unit_disposition": _unit_disposition(feature_id, item),
                "mechanical_link_risk": item.get("mechanical_link_risk", ""),
                "valuation_contamination_risk": item.get("valuation_contamination_risk", ""),
                "contemporaneous_endogeneity_risk": item.get(
                    "contemporaneous_endogeneity_risk", ""
                ),
                "public_language_constraint": item.get("prohibited_uses", ""),
            }
        )
    return pd.DataFrame(rows).sort_values("feature_id").reset_index(drop=True)


def _asset_universe_audit(root: Path) -> pd.DataFrame:
    coverage = _first_existing_csv(
        [
            root
            / "research"
            / "08_relative_major_asset_risk"
            / "tables"
            / "selected_major_coverage.csv",
            root
            / "research"
            / "08_relative_asset_risk_factor_structure"
            / "tables"
            / "selected_major_coverage.csv",
        ]
    )
    rows: list[dict[str, Any]] = []
    coverage_map = coverage.set_index("symbol").to_dict("index") if not coverage.empty else {}
    for asset in SELECTED_ASSETS:
        symbol = str(asset["symbol"])
        item = coverage_map.get(symbol, {})
        observations = int(float(item.get("observations", 0) or 0))
        rows.append(
            {
                "asset": symbol,
                "asset_name": asset["name"],
                "canonical_key": asset["asset_key"],
                "coingecko_id": f"coingecko:{asset['coingecko_id']}",
                "asset_type": asset.get("asset_type", ""),
                "selected_major": bool(asset.get("selected_major", False)),
                "observations": observations,
                "first_valid_date": item.get("first_valid_date", item.get("first_date", "")),
                "last_valid_date": item.get("last_valid_date", item.get("last_date", "")),
                "coverage_status": "usable_current_cohort_daily"
                if observations >= 60
                else "insufficient_or_missing_daily_coverage",
                "analysis_boundary": "current-cohort daily returns are survivorship-biased; monthly PIT data supports structure/state analysis only",
            }
        )
    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)


def _chain_token_mapping_audit(root: Path, assets: pd.DataFrame) -> pd.DataFrame:
    identity = _first_existing_csv(
        [
            root
            / "research"
            / "08_relative_major_asset_risk"
            / "tables"
            / "asset_identity_audit.csv",
            root
            / "research"
            / "08_relative_asset_risk_factor_structure"
            / "tables"
            / "asset_identity_audit.csv",
        ]
    )
    rows: list[dict[str, Any]] = []
    if not identity.empty:
        for row in identity.to_dict("records"):
            rows.append(
                {
                    "mapping_check": row.get("check_id", ""),
                    "asset": row.get("symbol", ""),
                    "canonical_key": row.get("canonical_asset_key", ""),
                    "status": row.get("status", ""),
                    "failing_rows": row.get("failing_rows", 0),
                    "mapping_boundary": row.get("note", "canonical identity audit"),
                }
            )
    for row in assets.to_dict("records"):
        rows.append(
            {
                "mapping_check": f"selected_major_{str(row['asset']).lower()}",
                "asset": row["asset"],
                "canonical_key": row["canonical_key"],
                "status": row["coverage_status"],
                "failing_rows": 0 if row["observations"] else 1,
                "mapping_boundary": row["analysis_boundary"],
            }
        )
    return pd.DataFrame(rows).sort_values(["asset", "mapping_check"]).reset_index(drop=True)


def _measurement_risk_audit(
    providers: pd.DataFrame,
    features: pd.DataFrame,
    usage: pd.DataFrame,
    units: pd.DataFrame,
    assets: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for provider in providers.to_dict("records"):
        if provider.get("disposition") != "public/re-distributable":
            rows.append(
                {
                    "risk_id": f"release_{provider['provider_id']}",
                    "risk_type": "release_risk",
                    "severity": "high",
                    "subject": provider["provider"],
                    "evidence": provider.get("disposition", ""),
                    "required_handling": "publish derived semantic artifacts only unless rights are separately verified",
                }
            )
    for feature in features.to_dict("records"):
        text = " ".join(
            str(feature.get(column, ""))
            for column in [
                "mechanical_link_risk",
                "valuation_contamination_risk",
                "contemporaneous_endogeneity_risk",
                "prohibited_uses",
            ]
        ).lower()
        if any(term in text for term in ["high", "mvrv", "price", "endogeneity", "causal"]):
            rows.append(
                {
                    "risk_id": f"measurement_{feature['feature_id']}",
                    "risk_type": "measurement_or_endogeneity",
                    "severity": "medium",
                    "subject": feature["feature_id"],
                    "evidence": text[:220],
                    "required_handling": "state timing, denominator, and prohibited language before use",
                }
            )
    excluded = usage[usage["usage_status"].astype(str).str.startswith("excluded_")]
    for row in excluded.head(200).to_dict("records"):
        rows.append(
            {
                "risk_id": f"usage_{row['feature_id']}",
                "risk_type": "feature_exclusion",
                "severity": "medium",
                "subject": row["feature_id"],
                "evidence": row["usage_status"],
                "required_handling": row["status_rationale"],
            }
        )
    for row in assets[assets["coverage_status"].ne("usable_current_cohort_daily")].to_dict(
        "records"
    ):
        rows.append(
            {
                "risk_id": f"asset_coverage_{str(row['asset']).lower()}",
                "risk_type": "asset_coverage",
                "severity": "medium",
                "subject": row["asset"],
                "evidence": row["coverage_status"],
                "required_handling": row["analysis_boundary"],
            }
        )
    if not rows:
        rows.append(
            {
                "risk_id": "no_blocking_measurement_risk",
                "risk_type": "data_foundation",
                "severity": "info",
                "subject": "data_foundation",
                "evidence": "No automated release, usage, or measurement flags emitted.",
                "required_handling": "Continue manual empirical and visual review.",
            }
        )
    return pd.DataFrame(rows).sort_values(["severity", "risk_id"]).reset_index(drop=True)


def _write_figures(
    figures_dir: Path,
    providers: pd.DataFrame,
    usage: pd.DataFrame,
    coverage: pd.DataFrame,
) -> list[Path]:
    apply_theme()
    artifacts: list[Path] = []

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.78, wspace=0.34)
    add_figure_header(
        fig,
        "Data-governance surface spans providers, features, and release boundaries",
        "Provider bars count local raw files; usage bars count registered or discovered processed features.",
    )
    ax = axes[0]
    style_axis(ax)
    if not providers.empty:
        plot = providers.sort_values("file_count", ascending=False).head(10)
        ax.barh(
            plot["provider"],
            plot["file_count"],
            color=PALETTE["eth"],
            edgecolor=PALETTE["eth_dark"],
        )
        ax.invert_yaxis()
    ax.set_xlabel("Raw file count")
    ax.set_ylabel("")
    ax.set_title("A. Provider inventory", loc="left", fontsize=13, fontweight="semibold")

    ax = axes[1]
    style_axis(ax)
    counts = usage["usage_status"].value_counts().reindex(sorted(ALLOWED_USAGE_STATUSES)).fillna(0)
    ax.barh(counts.index, counts.values, color=PALETTE["btc"], edgecolor=PALETTE["btc_dark"])
    ax.invert_yaxis()
    ax.set_xlabel("Feature count")
    ax.set_ylabel("")
    ax.set_title("B. Usage disposition", loc="left", fontsize=13, fontweight="semibold")
    artifacts.append(_save_figure(fig, figures_dir / "data_governance_inventory.png"))

    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Coverage audit separates observed panels from registered feature intent",
        "Bars show median non-missing observations by research block where processed panels are available.",
    )
    style_axis(ax)
    if not coverage.empty:
        plot = (
            coverage.groupby("research_block", dropna=False)["observations"]
            .median()
            .sort_values(ascending=False)
            .head(12)
        )
        labels = pd.Index(plot.index).fillna("unregistered").astype(str)
        ax.barh(labels, plot.values, color=PALETTE["stable"], edgecolor=PALETTE["stable_dark"])
        ax.invert_yaxis()
    ax.set_xlabel("Median non-missing observations")
    ax.set_ylabel("")
    artifacts.append(_save_figure(fig, figures_dir / "coverage_missingness_by_block.png"))
    return artifacts


def _write_docs(
    root: Path,
    module_dir: Path,
    title: str,
    research_question: str,
    providers: pd.DataFrame,
    raw_series: pd.DataFrame,
    feature_inventory: pd.DataFrame,
    usage: pd.DataFrame,
    assets: pd.DataFrame,
    measurement: pd.DataFrame,
) -> list[Path]:
    primary = int(usage["usage_status"].eq("primary_analysis").sum())
    robust = int(usage["usage_status"].eq("robustness_or_sensitivity").sum())
    diagnostic = int(usage["usage_status"].eq("diagnostic_only").sum())
    excluded = int(usage["usage_status"].astype(str).str.startswith("excluded_").sum())
    restricted = (
        int(providers["disposition"].ne("public/re-distributable").sum())
        if not providers.empty
        else 0
    )
    sample_table = pd.DataFrame(
        [
            {
                "surface": "Raw provider files",
                "observations": len(raw_series),
                "sample": _sample_range(raw_series),
                "coverage rule": "local files under data_local/raw; never committed",
            },
            {
                "surface": "Registered features",
                "observations": len(feature_inventory),
                "sample": "config/feature_registry.yml",
                "coverage rule": "feature must receive exactly one usage status",
            },
            {
                "surface": "Selected assets",
                "observations": len(assets),
                "sample": "canonical selected-major universe",
                "coverage rule": "current-cohort daily is survivorship-biased",
            },
        ]
    )
    methods = pd.DataFrame(
        [
            {
                "method": "File inventory",
                "calculation": "scan local raw files and infer provider/date coverage",
                "output": "raw_file_inventory.csv; raw_series_inventory.csv",
            },
            {
                "method": "Usage disposition",
                "calculation": "assign one allowed status from registration, coverage, unit, and release risk",
                "output": "feature_usage_matrix.csv",
            },
            {
                "method": "Measurement-risk audit",
                "calculation": "flag release, mechanical-link, valuation, endogeneity, and asset-coverage risks",
                "output": "measurement_risk_audit.csv",
            },
        ]
    )
    key_results = pd.DataFrame(
        [
            {
                "result": "Provider groups",
                "estimate": len(providers),
                "interval": "deterministic file inventory",
                "N/sample": len(raw_series),
                "interpretation": f"{restricted} provider groups require derived-only or restricted handling.",
                "sensitivity": "rerun after adding/removing local provider files",
            },
            {
                "result": "Feature usage status",
                "estimate": f"{primary} primary, {robust} robustness, {diagnostic} diagnostic, {excluded} excluded",
                "interval": "rule-based status taxonomy",
                "N/sample": len(usage),
                "interpretation": "Every registered or discovered processed feature has one disposition.",
                "sensitivity": "registration and coverage thresholds",
            },
            {
                "result": "Measurement-risk flags",
                "estimate": len(measurement),
                "interval": "automated audit plus manual review required",
                "N/sample": len(feature_inventory),
                "interpretation": "Flags constrain public language and model eligibility.",
                "sensitivity": "provider license review and feature metadata",
            },
        ]
    )
    table_links = "\n".join(f"- [`{name}`](tables/{name})" for name in REQUIRED_TABLES)
    readme = f"""# {MODULE_ID}: {title}

## Overview

This module is the repository's data-governance and measurement-control layer. It inventories local provider files, processed panels, registered features, selected assets, timing, units, denominators, release risk, and measurement constraints before any empirical claim is promoted.

## Questions Investigated

- Which provider groups and raw files are locally available, and what may be published?
- Which features are admissible for primary analysis, robustness, diagnostics, or exclusion?
- Which assets and token mappings are defensible for cross-asset and point-in-time analysis?
- Where do mechanical price links, valuation contamination, timing, and denominator risks constrain interpretation?

## Data, Assets, and Sample

{sample_table.to_markdown(index=False)}

## Methodologies and Calculations

{methods.to_markdown(index=False)}

## Formulas

Missingness is measured as $\\text{{missing pct}} = \\frac{{N_{{missing}}}}{{N_{{rows}}}}$.

Feature usage is a deterministic one-status assignment over the union of registered features and discovered processed-panel columns.

## Summary of Results

{key_results.to_markdown(index=False)}

## Analytical Results and Visualizations

![Data governance inventory](figures/data_governance_inventory.png)

The first panel shows the local provider inventory that supports private rebuilds; the second panel shows whether discovered features are primary, sensitivity, diagnostic, or excluded. Release risk is a publishing constraint, not evidence quality.

![Coverage missingness by block](figures/coverage_missingness_by_block.png)

Coverage varies sharply by research block, so later modules state matched samples rather than assuming every registered feature is usable everywhere.

## Robustness and Sensitivity

The inventory is deterministic conditional on local files. Statuses should be regenerated after any new data source, feature-registration change, or provider-rights review.

## Interpretation

A `primary_analysis` status means the current repository permits use under the descriptive design. It does not mean the variable is strong, exogenous, or suitable for causal language. Diagnostics-only fields explain measurement, timing, identity, or units.

## Limitations

File inspection cannot grant legal redistribution rights. Unregistered processed columns remain conservative until promoted by a documented module decision. Current-cohort daily selected-major data is survivorship-biased.

## Reproduce This Module

```bash
uv run python scripts/run_research.py --module {MODULE_ID}
uv run python scripts/check_research_surface.py --module {MODULE_ID}
```

## Files and Code

{table_links}

- [Methodology](methodology.md)
- [Findings](findings.md)
- [Interpretation](interpretation.md)
- [Limitations](limitations.md)
- Code: `src/cqresearch/research/data_foundation.py`
"""
    docs = [
        write_text(module_dir / "README.md", readme),
        write_text(
            module_dir / "methodology.md",
            """# Methodology

The data foundation scans `data_local/raw/`, parses `config/feature_registry.yml`, audits processed parquet panels under `data_local/processed/`, and reconciles selected-asset identity outputs where present.

The usage matrix assigns exactly one of the allowed statuses: `primary_analysis`, `robustness_or_sensitivity`, `diagnostic_only`, `excluded_insufficient_coverage`, `excluded_ambiguous_definition_or_unit`, `excluded_duplicate`, or `excluded_release_risk`.

Provider disposition governs what can be published. Local provider inputs may support deterministic private rebuilds while public artifacts remain derived semantic outputs.
""",
        ),
        write_text(
            module_dir / "findings.md",
            f"""# Findings

- Local inventory covers {len(raw_series)} raw series across {len(providers)} provider groups.
- {restricted} provider groups are not marked `public/re-distributable`.
- The feature surface has {primary} primary-analysis features, {robust} robustness/sensitivity features, {diagnostic} diagnostic-only features, and {excluded} excluded features.
- The selected-asset universe audit covers {len(assets)} canonical assets and explicitly labels current-cohort daily survivorship bias.
- Measurement-risk audit emitted {len(measurement)} rows constraining public language and model eligibility.
""",
        ),
        write_text(
            module_dir / "interpretation.md",
            """# Interpretation

Data availability is not the same as claim strength. This module defines the allowed empirical surface and public-language constraints before later modules estimate associations.
""",
        ),
        write_text(
            module_dir / "limitations.md",
            """# Limitations

- Provider rights and licensing still require human review.
- Source date detection is heuristic for heterogeneous CSV files.
- Current-cohort daily constituent data cannot establish historical altseason behavior.
- Unit and denominator risks remain module-specific when raw USD levels are used.
""",
        ),
        write_text(
            module_dir / "module.yml",
            yaml.safe_dump(
                {
                    "module_id": MODULE_ID,
                    "title": title,
                    "research_question": research_question,
                    "research_questions": [
                        "Which data, asset, timing, unit, and release constraints govern the analysis?",
                        "Which features are admissible, diagnostic, or excluded?",
                    ],
                    "outcomes": [
                        "provider inventory",
                        "feature usage status",
                        "asset universe audit",
                        "measurement risk audit",
                    ],
                    "features": ["all registered features", "all processed panel columns"],
                    "frequencies": ["file-level", "daily", "weekly", "monthly"],
                    "methods": ["inventory", "coverage audit", "usage classification"],
                    "sensitivity_dimensions": [
                        "registered versus unregistered",
                        "release risk",
                        "coverage threshold",
                    ],
                    "status": "built",
                    "canonical_surface": module_dir.relative_to(root).as_posix(),
                    "tables": REQUIRED_TABLES,
                    "figures": [
                        "data_governance_inventory.png",
                        "coverage_missingness_by_block.png",
                    ],
                    "code": ["src/cqresearch/research/data_foundation.py"],
                    "tests": ["tests/unit/test_feature_strength_outputs.py"],
                    "root_readme_candidate_figures": [],
                },
                sort_keys=False,
            ),
        ),
    ]
    return docs


def _claims(
    providers: pd.DataFrame,
    raw_series: pd.DataFrame,
    feature_inventory: pd.DataFrame,
    usage: pd.DataFrame,
    measurement: pd.DataFrame,
) -> pd.DataFrame:
    primary = int(usage["usage_status"].eq("primary_analysis").sum())
    return pd.DataFrame(
        [
            _claim(
                "data_measurement_inventory_01",
                f"The local inventory covers {len(raw_series)} raw series across {len(providers)} provider groups and {len(feature_inventory)} registered features.",
                "Files currently present under data_local/raw plus config/feature_registry.yml.",
                "Filesystem inventory, feature-registry parse, and processed-panel coverage audit.",
                "License status is release-risk classification, not legal permission.",
                "A for local inventory; B for release-risk classification.",
                "tables/provider_inventory.csv; tables/raw_file_inventory.csv; tables/feature_inventory.csv",
                "figures/data_governance_inventory.png",
                "Provider files remain local and untracked.",
            ),
            _claim(
                "data_measurement_usage_01",
                f"Every registered or discovered processed feature receives one usage status; {primary} are marked primary_analysis.",
                "Union of registered features and local processed-panel columns.",
                "Deterministic one-status taxonomy using coverage, registration, unit, timing, and measurement risk.",
                "Automated status does not prove empirical strength.",
                "B",
                "tables/feature_usage_matrix.csv; tables/measurement_risk_audit.csv",
                "figures/coverage_missingness_by_block.png",
                f"{len(measurement)} measurement-risk rows constrain later modules.",
            ),
        ]
    )


def _claim(
    claim_id: str,
    claim_text: str,
    sample: str,
    method: str,
    uncertainty: str,
    evidence_grade: str,
    source_table: str,
    source_figure: str,
    limitation: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "claim_id": claim_id,
        "module_id": MODULE_ID,
        "claim_text": claim_text,
        "sample": sample,
        "method": method,
        "uncertainty": uncertainty,
        "evidence_grade": evidence_grade,
        "source_table": source_table,
        "source_figure": source_figure,
        "limitation": limitation,
        "status": "accepted_qualified",
    }
    _extend_claim(row)
    return row


def _extend_claim(row: dict[str, Any]) -> None:
    claim_text = str(row.get("claim_text", ""))
    row.setdefault("module", row.get("module_id", ""))
    row.setdefault("finding", claim_text)
    row.setdefault("outcome", "data and measurement governance")
    row.setdefault("feature_or_block", "all local data")
    row.setdefault("estimate_summary", claim_text)
    row.setdefault("uncertainty_summary", row.get("uncertainty", "See source table."))
    row.setdefault("sample_summary", row.get("sample", "See source table."))
    row.setdefault("frequency", "mixed")
    row.setdefault("timing", "source-specific timing audited")
    row.setdefault("sensitivity_summary", row.get("method", "See source table."))
    row.setdefault("interpretation", claim_text)
    row.setdefault("alternative_explanation", row.get("limitation", "See limitations."))
    row.setdefault("source_model_ids", _model_ids_from_source_tables(row.get("source_table", "")))


def _write_manifest(root: Path, module_dir: Path, artifacts: list[Path]) -> Path:
    payload = {
        "module_id": MODULE_ID,
        "schema_version": 1,
        "build_timestamp_utc": "not_recorded_for_deterministic_rebuilds",
        "artifacts": [artifact_record(path, root) for path in sorted(artifacts)],
    }
    return write_json(module_dir / "manifest.json", payload)


def _save_figure(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, bbox_inches="tight", facecolor=TOKENS["background"])
    svg = path.with_suffix(".svg")
    fig.savefig(
        svg, dpi=190, bbox_inches="tight", facecolor=TOKENS["background"], metadata={"Date": None}
    )
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
    return path


def _usage_status(feature_id: str, meta: dict[str, Any], observations: int) -> tuple[str, str]:
    lower = feature_id.lower()
    if observations and observations < 40:
        return "excluded_insufficient_coverage", "Coverage below the minimum descriptive threshold."
    if "duplicate" in lower:
        return "excluded_duplicate", "Feature appears duplicate or redundant by naming."
    if not meta:
        if _looks_like_raw_level(feature_id):
            return (
                "diagnostic_only",
                "Unregistered carried level retained for construction or denominator checks.",
            )
        return (
            "excluded_ambiguous_definition_or_unit",
            "Unregistered panel column requires definition and unit review.",
        )
    if "date" in lower or lower in {"calendar", "calendar_assumption", "close_time_assumption"}:
        return "diagnostic_only", "Calendar or timing metadata."
    risk = str(meta.get("mechanical_link_risk", "")).lower()
    valuation = str(meta.get("valuation_contamination_risk", "")).lower()
    raw_source = str(meta.get("raw_source", "")).lower()
    block = str(meta.get("research_block", "")).lower()
    if "restricted" in raw_source or "license" in raw_source:
        return (
            "excluded_release_risk",
            "Release-risk metadata requires exclusion from public analysis.",
        )
    if lower in {"d_log_mvrv", "d_log_market_cap", "d_log_realized_cap", "identity_residual"}:
        return "diagnostic_only", "MVRV identity component used for measurement mechanics."
    if "mvrv" in lower and "lag" not in lower:
        return "diagnostic_only", "Same-day MVRV is mechanically price-linked."
    if "unknown" in risk or "unknown" in valuation:
        return (
            "excluded_ambiguous_definition_or_unit",
            "Mechanical-link or valuation metadata is unresolved.",
        )
    if "high_usd_price_content" in valuation:
        return (
            "robustness_or_sensitivity",
            "USD-valued proxy requires valuation-contamination sensitivity.",
        )
    if block in {
        "target",
        "macro_risk",
        "etf_institutional",
        "leverage",
        "liquidity",
        "onchain_state",
        "market_structure",
    }:
        return "primary_analysis", "Registered feature used by the current empirical surface."
    return (
        "robustness_or_sensitivity",
        "Registered feature retained for sensitivity or future module review.",
    )


def _timing_disposition(feature_id: str, meta: dict[str, Any]) -> str:
    lag = str(meta.get("lag_days", ""))
    if lag and lag not in {"0", "0.0"}:
        return f"lagged by {lag} day(s) or period(s)"
    if "lag" in feature_id:
        return "lagged by feature construction"
    if feature_id.endswith("_ret") or "return" in str(meta.get("clean_label", "")).lower():
        return "same-period outcome or contemporaneous exposure"
    return "level or state variable; inspect calendar before modeling"


def _unit_disposition(feature_id: str, meta: dict[str, Any]) -> str:
    denominator = str(meta.get("scaling_denominator", ""))
    if denominator:
        return f"scaled by {denominator}"
    if feature_id.endswith("_ret") or "return" in str(meta.get("clean_label", "")).lower():
        return "return-like transformation"
    if "usd" in feature_id or "tvl" in feature_id:
        return "USD-valued series; inspect valuation contamination"
    if not meta:
        return "unknown unit for unregistered panel column"
    return "registered unit and transformation"


def _looks_like_raw_level(feature_id: str) -> bool:
    return any(
        term in feature_id.lower()
        for term in [
            "_close",
            "_level",
            "_usd",
            "_mcap",
            "market_cap",
            "realized_cap",
            "_oi",
            "funding",
            "dominance",
        ]
    )


def _first_existing_csv(paths: list[Path]) -> pd.DataFrame:
    for path in paths:
        if path.exists():
            return read_csv_if_exists(path)
    return pd.DataFrame()


def _provider_id(source_group: str) -> str:
    reverse = {display: key for key, display in PROVIDER_DISPLAY_NAMES.items()}
    return reverse.get(str(source_group), _slug(str(source_group)))


def _series_granularity(path: str) -> str:
    lower = path.lower()
    if "daily" in lower:
        return "daily"
    if "weekly" in lower:
        return "weekly"
    if "monthly" in lower:
        return "monthly"
    return "file"


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


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(value)).strip("_").lower() or "unknown"


def _sample_range(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "no local files"
    start = _min_date_text(frame.get("start_date", pd.Series(dtype=str)))
    end = _max_date_text(frame.get("end_date", pd.Series(dtype=str)))
    return f"{start} to {end}" if start or end else "dates unavailable"


def _model_ids_from_source_tables(source_table: Any) -> str:
    ids = []
    for item in str(source_table).replace(",", ";").split(";"):
        item = item.strip()
        if item:
            ids.append(f"table:{Path(item).stem}")
    return "; ".join(ids) or "table:claims"
