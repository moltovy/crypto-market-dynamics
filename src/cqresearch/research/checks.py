"""Validation for the canonical research surface."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from config.paths import PROJECT_ROOT

from cqresearch.core.artifacts import sha256_file
from cqresearch.research.data_foundation import REQUIRED_TABLES as DATA_FOUNDATION_TABLES
from cqresearch.research.registry import ALLOWED_USAGE_STATUSES, MODULES, module_by_id

REQUIRED_MODULE_FILES = [
    "README.md",
    "methodology.md",
    "findings.md",
    "interpretation.md",
    "limitations.md",
    "module.yml",
    "manifest.json",
]
REQUIRED_CLAIM_COLUMNS = {
    "claim_id",
    "module_id",
    "claim_text",
    "sample",
    "method",
    "uncertainty",
    "evidence_grade",
    "source_table",
    "source_figure",
    "limitation",
    "status",
}
EXTENDED_CLAIM_COLUMNS = {
    "module",
    "finding",
    "outcome",
    "feature_or_block",
    "estimate_summary",
    "uncertainty_summary",
    "sample_summary",
    "frequency",
    "timing",
    "sensitivity_summary",
    "interpretation",
    "alternative_explanation",
    "source_model_ids",
}
REQUIRED_MODULE_YML_FIELDS = {
    "module_id",
    "title",
    "research_questions",
    "outcomes",
    "features",
    "frequencies",
    "methods",
    "sensitivity_dimensions",
    "tables",
    "figures",
    "code",
    "tests",
    "root_readme_candidate_figures",
}
BANNED_FIGURE_NAME_TERMS = {
    "dashboard",
    "market_share",
    "composition",
    "stacked",
}


def check_research_surface(module: str = "all", root: Path = PROJECT_ROOT) -> pd.DataFrame:
    module_ids = (
        [item.module_id for item in MODULES]
        if module == "all"
        else [module_by_id(module).module_id]
    )
    rows: list[dict[str, Any]] = []
    if module == "all":
        rows.extend(_check_root_surface(root))
    for module_id in module_ids:
        rows.extend(_check_module(root, module_id))
    result = pd.DataFrame(rows)
    failures = result[result["status"].eq("fail")]
    if not failures.empty:
        message = failures[["module_id", "check_id", "detail"]].to_string(index=False)
        raise SystemExit(f"Research-surface check failed:\n{message}")
    return result


def _check_module(root: Path, module_id: str) -> list[dict[str, Any]]:
    module_dir = root / "research" / module_id
    rows: list[dict[str, Any]] = []
    rows.append(
        _row(module_id, "module_directory_exists", module_dir.exists(), module_dir.as_posix())
    )
    if not module_dir.exists():
        return rows
    for relpath in REQUIRED_MODULE_FILES:
        path = module_dir / relpath
        rows.append(_row(module_id, f"required_file_{relpath}", path.exists(), relpath))
    rows.append(
        _row(module_id, "tables_directory_exists", (module_dir / "tables").exists(), "tables/")
    )
    rows.append(
        _row(module_id, "figures_directory_exists", (module_dir / "figures").exists(), "figures/")
    )
    rows.extend(_check_module_contract(module_dir, module_id))

    if module_id == "00_data_foundation":
        rows.extend(_check_data_foundation(module_dir))
    rows.extend(_check_manifest(root, module_dir, module_id))
    return rows


def _check_module_contract(module_dir: Path, module_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    claims_path = module_dir / "tables" / "claims.csv"
    rows.append(_row(module_id, "claims_table_exists", claims_path.exists(), "tables/claims.csv"))
    if claims_path.exists():
        claims = pd.read_csv(claims_path)
        missing = REQUIRED_CLAIM_COLUMNS - set(claims.columns)
        missing_extended = EXTENDED_CLAIM_COLUMNS - set(claims.columns)
        rows.append(
            _row(
                module_id,
                "claims_schema",
                not missing and not claims.empty,
                ",".join(sorted(missing)) if missing else f"claims rows={len(claims)}",
            )
        )
        rows.append(
            _row(
                module_id,
                "claims_extended_schema",
                not missing_extended,
                ",".join(sorted(missing_extended))
                if missing_extended
                else "extended claims schema present",
            )
        )
        if "module_id" in claims:
            rows.append(
                _row(
                    module_id,
                    "claims_module_id_matches",
                    set(claims["module_id"].dropna().astype(str)) == {module_id},
                    "claim module_id column matches directory",
                )
            )
    module_yml = module_dir / "module.yml"
    if module_yml.exists():
        payload = yaml.safe_load(module_yml.read_text(encoding="utf-8")) or {}
        missing_yml = REQUIRED_MODULE_YML_FIELDS - set(payload)
        rows.append(
            _row(
                module_id,
                "module_yml_status_built",
                payload.get("status") == "built",
                str(payload.get("status", "")),
            )
        )
        rows.append(
            _row(
                module_id,
                "module_yml_required_fields",
                not missing_yml,
                ",".join(sorted(missing_yml)) if missing_yml else "required fields present",
            )
        )
    table_files = list((module_dir / "tables").glob("*"))
    rows.append(
        _row(module_id, "has_table_artifacts", len(table_files) > 0, f"tables={len(table_files)}")
    )
    figure_names = [
        path.name.lower() for path in (module_dir / "figures").glob("*") if path.is_file()
    ]
    banned = [
        name for name in figure_names if any(term in name for term in BANNED_FIGURE_NAME_TERMS)
    ]
    rows.append(
        _row(
            module_id,
            "figure_names_avoid_banned_terms",
            not banned,
            ",".join(banned) if banned else "no banned figure-name terms",
        )
    )
    return rows


def _check_root_surface(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    research_dir = root / "research"
    readme_path = research_dir / "README.md"
    manifest_path = research_dir / "manifest.json"
    figure_specs_path = research_dir / "figure_specs.csv"
    rows.append(
        _row("research", "root_research_directory_exists", research_dir.exists(), "research/")
    )
    rows.append(_row("research", "root_readme_exists", readme_path.exists(), "research/README.md"))
    rows.append(
        _row("research", "root_manifest_exists", manifest_path.exists(), "research/manifest.json")
    )
    rows.append(
        _row(
            "research",
            "root_figure_specs_exists",
            figure_specs_path.exists(),
            "research/figure_specs.csv",
        )
    )
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
        rows.append(
            _row(
                "research",
                "root_readme_figure_count",
                4 <= len(images) <= 6,
                f"figures={len(images)}",
            )
        )
        rows.append(
            _row(
                "research",
                "root_readme_no_outputs_links",
                "outputs/" not in readme,
                "outputs/ absent",
            )
        )
        for image in images:
            rows.append(
                _row(
                    "research",
                    f"root_readme_image_exists_{image}",
                    (research_dir / image).exists(),
                    image,
                )
            )
    if manifest_path.exists():
        rows.extend(_check_root_manifest(root, manifest_path))
    if figure_specs_path.exists():
        rows.extend(_check_figure_specs(root, figure_specs_path))
    rows.extend(_check_release_hygiene(root))
    return rows


def _check_root_manifest(root: Path, manifest_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [_row("research", "root_manifest_valid_json", False, str(exc))]
    rows.append(_row("research", "root_manifest_valid_json", True, "parsed"))
    modules = payload.get("modules", [])
    module_ids = {str(item.get("module_id", "")) for item in modules}
    expected = {item.module_id for item in MODULES}
    rows.append(
        _row(
            "research",
            "root_manifest_modules_match_registry",
            module_ids == expected,
            ",".join(sorted(expected - module_ids))
            if module_ids != expected
            else "module ids match",
        )
    )
    rows.append(
        _row(
            "research",
            "root_manifest_public_figure_count",
            4 <= int(payload.get("public_figure_count", 0)) <= 6,
            str(payload.get("public_figure_count", "")),
        )
    )
    for artifact in payload.get("artifacts", []):
        path = root / artifact.get("path", "")
        exists = path.exists()
        rows.append(
            _row(
                "research",
                f"root_manifest_artifact_exists_{artifact.get('path')}",
                exists,
                str(path),
            )
        )
        if exists:
            rows.append(
                _row(
                    "research",
                    f"root_manifest_sha256_{artifact.get('path')}",
                    sha256_file(path) == artifact.get("sha256"),
                    artifact.get("path", ""),
                )
            )
    return rows


def _check_figure_specs(root: Path, figure_specs_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    specs = pd.read_csv(figure_specs_path)
    figure_paths = sorted(
        path.relative_to(root).as_posix() for path in (root / "research").glob("*/figures/*.png")
    )
    spec_paths = set(specs.get("figure_path", pd.Series(dtype=str)).dropna().astype(str))
    missing = sorted(set(figure_paths) - spec_paths)
    rows.append(
        _row(
            "research",
            "figure_specs_cover_all_pngs",
            not missing,
            ",".join(missing) if missing else f"figures={len(figure_paths)}",
        )
    )
    required = {
        "figure_id",
        "module",
        "research_question",
        "model_ids",
        "source_tables",
        "chart_type",
        "figure_path",
        "svg_path",
        "interpretation",
        "limitation",
    }
    missing_columns = required - set(specs.columns)
    rows.append(
        _row(
            "research",
            "figure_specs_schema",
            not missing_columns,
            ",".join(sorted(missing_columns)) if missing_columns else "figure specs schema present",
        )
    )
    if not missing_columns:
        nonempty = specs[list(required)].notna().all().all() and (
            specs[list(required)].astype(str).apply(lambda col: col.str.strip().ne("")).all().all()
        )
        rows.append(
            _row(
                "research",
                "figure_specs_required_values",
                bool(nonempty),
                "required values non-empty",
            )
        )
        for relpath in specs["figure_path"].dropna().astype(str):
            rows.append(
                _row(
                    "research",
                    f"figure_spec_png_exists_{relpath}",
                    (root / relpath).exists(),
                    relpath,
                )
            )
        for relpath in specs["svg_path"].dropna().astype(str):
            rows.append(
                _row(
                    "research",
                    f"figure_spec_svg_exists_{relpath}",
                    (root / relpath).exists(),
                    relpath,
                )
            )
    return rows


def _check_release_hygiene(root: Path) -> list[dict[str, Any]]:
    rows = [
        _row("research", "old_outputs_surface_absent", not (root / "outputs").exists(), "outputs/"),
    ]
    if (root / ".git").exists():
        tracked_outputs = _git_ls_files(root, ["outputs"])
        tracked_raw = _git_ls_files(root, ["data_local"])
        tracked_pack = _git_ls_files(
            root, ["crypto_market_dynamics_empirical_rebuild_manager_pack"]
        )
        rows.extend(
            [
                _row(
                    "research",
                    "old_outputs_not_tracked",
                    not tracked_outputs,
                    ",".join(tracked_outputs[:5]),
                ),
                _row(
                    "research", "raw_data_not_tracked", not tracked_raw, ",".join(tracked_raw[:5])
                ),
                _row(
                    "research",
                    "manager_pack_not_tracked",
                    not tracked_pack,
                    ",".join(tracked_pack[:5]),
                ),
            ]
        )
    return rows


def _git_ls_files(root: Path, paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", *paths], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return ["git ls-files failed"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _check_data_foundation(module_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    tables_dir = module_dir / "tables"
    for name in DATA_FOUNDATION_TABLES:
        path = tables_dir / name
        rows.append(_row("00_data_foundation", f"table_exists_{name}", path.exists(), name))
        if path.exists():
            frame = pd.read_csv(path)
            rows.append(
                _row(
                    "00_data_foundation",
                    f"table_nonempty_{name}",
                    not frame.empty,
                    f"{name} rows={len(frame)}",
                )
            )
    usage_path = tables_dir / "feature_usage_matrix.csv"
    if usage_path.exists():
        usage = pd.read_csv(usage_path)
        statuses = set(usage.get("usage_status", pd.Series(dtype=str)).dropna().astype(str))
        invalid = statuses - set(ALLOWED_USAGE_STATUSES)
        rows.append(
            _row(
                "00_data_foundation",
                "usage_statuses_allowed",
                not invalid,
                ",".join(sorted(invalid)) if invalid else "all statuses allowed",
            )
        )
        duplicate = usage["feature_id"].duplicated().any() if "feature_id" in usage else True
        rows.append(
            _row(
                "00_data_foundation",
                "one_status_per_feature",
                not duplicate and usage["usage_status"].notna().all(),
                "feature_id unique and usage_status non-null",
            )
        )
    return rows


def _check_manifest(root: Path, module_dir: Path, module_id: str) -> list[dict[str, Any]]:
    manifest_path = module_dir / "manifest.json"
    rows: list[dict[str, Any]] = []
    if not manifest_path.exists():
        return rows
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [_row(module_id, "manifest_valid_json", False, str(exc))]
    rows.append(_row(module_id, "manifest_valid_json", True, "parsed"))
    artifacts = payload.get("artifacts", [])
    for artifact in artifacts:
        path = root / artifact.get("path", "")
        exists = path.exists()
        rows.append(
            _row(module_id, f"manifest_artifact_exists_{artifact.get('path')}", exists, str(path))
        )
        if exists:
            rows.append(
                _row(
                    module_id,
                    f"manifest_sha256_{artifact.get('path')}",
                    sha256_file(path) == artifact.get("sha256"),
                    artifact.get("path", ""),
                )
            )
    return rows


def _row(module_id: str, check_id: str, passed: bool, detail: str) -> dict[str, Any]:
    return {
        "module_id": module_id,
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "detail": detail,
    }
