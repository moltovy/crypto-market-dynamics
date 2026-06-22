"""Build the root `research/` index, manifest, and figure specifications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from config.paths import PROJECT_ROOT

from cqresearch.core.artifacts import (
    artifact_record,
    sha256_file,
    write_csv,
    write_json,
    write_text,
)
from cqresearch.research.registry import MODULES


def build_root_research_surface(root: Path = PROJECT_ROOT) -> list[Path]:
    research_dir = root / "research"
    research_dir.mkdir(parents=True, exist_ok=True)

    module_rows = _module_rows(root)
    figure_specs = _figure_specs(root)
    usage_counts = _usage_counts(root)

    artifacts: list[Path] = [
        write_csv(research_dir / "figure_specs.csv", figure_specs),
        write_text(
            research_dir / "README.md", _root_readme(module_rows, figure_specs, usage_counts)
        ),
    ]
    artifacts.append(_write_root_manifest(root, module_rows, figure_specs, usage_counts, artifacts))
    return artifacts


def _module_rows(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for module in MODULES:
        module_dir = root / "research" / module.module_id
        manifest_path = module_dir / "manifest.json"
        manifest = _read_json(manifest_path)
        artifacts = manifest.get("artifacts", []) if isinstance(manifest, dict) else []
        tables = sorted(path.name for path in (module_dir / "tables").glob("*") if path.is_file())
        figures = sorted(
            path.name for path in (module_dir / "figures").glob("*.png") if path.is_file()
        )
        rows.append(
            {
                "module_id": module.module_id,
                "title": module.title,
                "research_question": module.research_question,
                "path": f"research/{module.module_id}",
                "manifest_path": f"research/{module.module_id}/manifest.json",
                "manifest_sha256": sha256_file(manifest_path) if manifest_path.exists() else "",
                "artifact_count": len(artifacts),
                "table_count": len(tables),
                "figure_count": len(figures),
            }
        )
    return pd.DataFrame(rows)


def _figure_specs(root: Path) -> pd.DataFrame:
    registry = _public_figure_registry(root)
    rows: list[dict[str, Any]] = []
    for png_path in sorted((root / "research").glob("*/figures/*.png")):
        relpath = png_path.relative_to(root).as_posix()
        module_id = png_path.relative_to(root / "research").parts[0]
        module = next(item for item in MODULES if item.module_id == module_id)
        registered = registry.get(relpath, {})
        source_tables = registered.get("source_tables") or _claim_source_tables(
            root, module_id, png_path.name
        )
        model_ids = _model_ids_from_source_tables(source_tables)
        rows.append(
            {
                "figure_id": registered.get("figure_id", png_path.stem),
                "module": module_id,
                "research_question": registered.get("research_question", module.research_question),
                "model_ids": model_ids,
                "source_tables": source_tables,
                "chart_type": registered.get("chart_type", _chart_type_from_name(png_path.stem)),
                "x": registered.get("x", "see source table"),
                "y": registered.get("y", "see source table"),
                "interval": registered.get(
                    "interval", "shown where source model reports uncertainty"
                ),
                "sample": registered.get("sample", "see source table"),
                "figure_path": relpath,
                "svg_path": png_path.with_suffix(".svg").relative_to(root).as_posix(),
                "title": registered.get("caption", png_path.stem.replace("_", " ").title()),
                "subtitle": registered.get("units", "derived analytical output"),
                "interpretation": registered.get(
                    "caption", "See module findings and interpretation."
                ),
                "limitation": registered.get("caveat", "See module limitations."),
                "root_readme": registered.get("status") == "public",
                "visual_qa_status": registered.get("visual_qa_status", "manual_review_required"),
            }
        )
    return pd.DataFrame(rows)


def _public_figure_registry(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "config" / "public_figures.yml"
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(item.get("filename", "")): item for item in payload.get("figures", [])}


def _claim_source_tables(root: Path, module_id: str, figure_name: str) -> str:
    claims_path = root / "research" / module_id / "tables" / "claims.csv"
    if not claims_path.exists():
        return f"research/{module_id}/tables/claims.csv"
    claims = pd.read_csv(claims_path)
    if "source_figure" in claims:
        matches = claims[
            claims["source_figure"].astype(str).str.contains(figure_name, regex=False, na=False)
        ]
        if not matches.empty:
            return "; ".join(matches["source_table"].dropna().astype(str).unique())
    return f"research/{module_id}/tables/claims.csv"


def _model_ids_from_source_tables(source_tables: str) -> str:
    ids: list[str] = []
    for item in str(source_tables).replace(",", ";").split(";"):
        item = item.strip()
        if not item:
            continue
        ids.append(f"table:{Path(item).stem}")
    return "; ".join(ids) or "table:claims"


def _chart_type_from_name(name: str) -> str:
    if "mvrv" in name:
        return "measurement_decomposition"
    if "event" in name:
        return "event_placebo_response"
    if "risk" in name:
        return "risk_decomposition"
    if "concentration" in name:
        return "state_conditioned_concentration"
    return "analytical_result"


def _usage_counts(root: Path) -> dict[str, int]:
    path = root / "research" / "00_data_foundation" / "tables" / "feature_usage_matrix.csv"
    if not path.exists():
        return {}
    usage = pd.read_csv(path)
    return {str(key): int(value) for key, value in usage["usage_status"].value_counts().items()}


def _root_readme(
    module_rows: pd.DataFrame, figure_specs: pd.DataFrame, usage_counts: dict[str, int]
) -> str:
    module_table = "\n".join(
        "| [{module_id}]({relpath}/README.md) | {title} | {question} |".format(
            module_id=row.module_id,
            relpath=Path(row.path).relative_to("research").as_posix(),
            title=row.title,
            question=row.research_question,
        )
        for row in module_rows.itertuples(index=False)
    )
    root_figures = figure_specs[figure_specs["root_readme"].eq(True)]
    figure_list = "\n\n".join(
        "![{title}]({path})\n\nSource: `{source}`. Boundary: {limitation}".format(
            title=str(row.title),
            path=Path(str(row.figure_path)).relative_to("research").as_posix(),
            source=str(row.source_tables),
            limitation=str(row.limitation),
        )
        for row in root_figures.itertuples(index=False)
    )
    status_list = "\n".join(f"- `{key}`: {value}" for key, value in sorted(usage_counts.items()))
    return f"""# Research Surface

This directory is the canonical public research surface for Crypto Market Dynamics. It organizes the 2020-2026 descriptive and associational evidence into self-contained modules with methods, findings, interpretation, limitations, tables, figures, and manifests.

## Module Map

| Module | Title | Question |
|---|---|---|
{module_table}

## Root Figure Set

{figure_list}

## Data-Usage Status Counts

{status_list}

Every local raw or engineered feature discovered by the data-foundation module is assigned one usage or exclusion status in [`00_data_foundation/tables/feature_usage_matrix.csv`](00_data_foundation/tables/feature_usage_matrix.csv).

## Provenance

- Root manifest: [`manifest.json`](manifest.json)
- Figure specifications: [`figure_specs.csv`](figure_specs.csv)
- Cross-module evidence ledger: [`11_cross_module_synthesis/tables/evidence_ledger.csv`](11_cross_module_synthesis/tables/evidence_ledger.csv)

## Rebuild

```bash
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py --module all
```
"""


def _write_root_manifest(
    root: Path,
    module_rows: pd.DataFrame,
    figure_specs: pd.DataFrame,
    usage_counts: dict[str, int],
    artifacts: list[Path],
) -> Path:
    module_payload = module_rows.to_dict(orient="records")
    root_records = [artifact_record(path, root) for path in sorted(artifacts)]
    module_manifest_records = [
        artifact_record(root / str(row["manifest_path"]), root)
        for row in module_payload
        if (root / str(row["manifest_path"])).exists()
    ]
    payload = {
        "schema_version": 1,
        "canonical_surface": "research",
        "build_timestamp_utc": "not_recorded_for_deterministic_rebuilds",
        "module_count": len(module_payload),
        "modules": module_payload,
        "public_figure_count": int(figure_specs["root_readme"].eq(True).sum())
        if not figure_specs.empty
        else 0,
        "figure_count": int(len(figure_specs)),
        "data_usage_status_counts": usage_counts,
        "artifacts": root_records + module_manifest_records,
    }
    return write_json(root / "research" / "manifest.json", payload)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
