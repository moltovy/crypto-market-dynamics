"""Build the repository root README, research index, manifests, and figure specs."""

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

ROOT_FIGURE_SELECTION_COLUMNS = [
    "figure_id",
    "module",
    "finding",
    "empirical_strength",
    "robustness",
    "economic_relevance",
    "june_2026_relevance",
    "cross_asset_breadth",
    "visual_quality",
    "weighted_score",
    "hard_exclusion",
    "selected",
    "reason",
]


def build_root_research_surface(root: Path = PROJECT_ROOT) -> list[Path]:
    research_dir = root / "research"
    research_dir.mkdir(parents=True, exist_ok=True)

    module_rows = _module_rows(root)
    figure_specs = _figure_specs(root)
    selection = _root_figure_selection(figure_specs)
    usage_counts = _usage_counts(root)

    research_readme = _research_index(module_rows, figure_specs, usage_counts)
    root_readme = _root_readme(module_rows, figure_specs, selection, usage_counts)
    artifacts: list[Path] = [
        write_csv(research_dir / "figure_specs.csv", figure_specs),
        write_csv(research_dir / "root_figure_selection.csv", selection),
        write_text(research_dir / "README.md", research_readme),
        write_text(root / "README.md", root_readme),
    ]
    artifacts.append(
        _write_root_manifest(root, module_rows, figure_specs, selection, usage_counts, artifacts)
    )
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
                "question": module.research_question,
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
    registry = _figure_registry(root)
    rows: list[dict[str, Any]] = []
    modules = {item.module_id: item for item in MODULES}
    for png_path in sorted((root / "research").glob("*/figures/*.png")):
        relpath = png_path.relative_to(root).as_posix()
        module_id = png_path.relative_to(root / "research").parts[0]
        if module_id not in modules:
            continue
        module = modules[module_id]
        registered = registry.get(relpath, {})
        source_tables = registered.get("source_tables") or _claim_source_tables(
            root, module_id, png_path.name
        )
        rows.append(
            {
                "figure_id": registered.get("figure_id", png_path.stem),
                "module": module_id,
                "research_question": registered.get("research_question", module.research_question),
                "model_ids": _model_ids_from_source_tables(source_tables),
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


def _figure_registry(root: Path) -> dict[str, dict[str, Any]]:
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


def _root_figure_selection(figure_specs: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if figure_specs.empty:
        return pd.DataFrame(columns=ROOT_FIGURE_SELECTION_COLUMNS)
    excluded_terms = {
        "mvrv": "measurement warning belongs in methodology/appendix, not default root slot",
        "concentration": "raw concentration/rank persistence is excluded from root figures",
        "market_concentration": "raw concentration/rank persistence is excluded from root figures",
        "selected_major_asset_risk": "basic volatility/drawdown scatter is excluded",
        "cumulative": "ETF cumulative-flow root figure is excluded",
    }
    for row in figure_specs.to_dict("records"):
        figure_id = str(row["figure_id"])
        figure_path = str(row["figure_path"])
        text = f"{figure_id} {figure_path} {row.get('chart_type', '')}".lower()
        hard_exclusion = ""
        for term, reason in excluded_terms.items():
            if term in text:
                hard_exclusion = reason
                break
        selected = bool(row.get("root_readme", False)) and not hard_exclusion
        empirical_strength = _score(row, "empirical")
        robustness = _score(row, "robustness")
        economic = _score(row, "economic")
        june = _score(row, "june")
        breadth = _score(row, "breadth")
        visual = _score(row, "visual")
        weighted = round(
            0.25 * empirical_strength
            + 0.20 * robustness
            + 0.20 * economic
            + 0.15 * june
            + 0.10 * breadth
            + 0.10 * visual,
            2,
        )
        rows.append(
            {
                "figure_id": figure_id,
                "module": row["module"],
                "finding": row.get("title", figure_id),
                "empirical_strength": empirical_strength,
                "robustness": robustness,
                "economic_relevance": economic,
                "june_2026_relevance": june,
                "cross_asset_breadth": breadth,
                "visual_quality": visual,
                "weighted_score": weighted,
                "hard_exclusion": hard_exclusion,
                "selected": selected,
                "reason": "selected root evidence map figure"
                if selected
                else hard_exclusion or "module/appendix figure retained outside root selection",
            }
        )
    return pd.DataFrame(rows)[ROOT_FIGURE_SELECTION_COLUMNS].reset_index(drop=True)


def _score(row: dict[str, Any], dimension: str) -> int:
    text = f"{row.get('figure_id', '')} {row.get('chart_type', '')} {row.get('source_tables', '')} {row.get('module', '')}".lower()
    if dimension == "empirical":
        return (
            5
            if any(
                term in text for term in ["pca", "lag_response", "tail", "delta", "decomposition"]
            )
            else 3
        )
    if dimension == "robustness":
        return (
            5
            if any(
                term in text
                for term in ["bootstrap", "ridge", "fdr", "same-support", "pca", "lag_response"]
            )
            else 3
        )
    if dimension == "economic":
        return (
            5
            if any(term in text for term in ["macro", "etf", "leverage", "risk", "dependence"])
            else 3
        )
    if dimension == "june":
        return (
            5
            if any(term in text for term in ["etf", "leverage", "macro", "cross_asset", "relative"])
            else 3
        )
    if dimension == "breadth":
        return 5 if any(term in text for term in ["cross_asset", "relative", "macro"]) else 3
    if dimension == "visual":
        return 5 if str(row.get("visual_qa_status", "")).startswith("pass") else 3
    return 3


def _usage_counts(root: Path) -> dict[str, int]:
    path = (
        root / "research" / "00_data_measurement_foundation" / "tables" / "feature_usage_matrix.csv"
    )
    if not path.exists():
        return {}
    usage = pd.read_csv(path)
    return {str(key): int(value) for key, value in usage["usage_status"].value_counts().items()}


def _root_readme(
    module_rows: pd.DataFrame,
    figure_specs: pd.DataFrame,
    selection: pd.DataFrame,
    usage_counts: dict[str, int],
) -> str:
    selected = selection[selection["selected"].eq(True)] if not selection.empty else pd.DataFrame()
    fig_map = figure_specs.set_index("figure_id").to_dict("index") if not figure_specs.empty else {}
    figure_sections = []
    for item in selected.itertuples(index=False):
        spec = fig_map.get(item.figure_id, {})
        figure_sections.append(
            f"### {item.finding}\n\n"
            f"![{item.finding}]({spec.get('figure_path', '')})\n\n"
            f"Sample and method: {spec.get('sample', 'see source table')}; {spec.get('chart_type', 'analytical result')} from `{spec.get('source_tables', '')}`.\n\n"
            f"Interpretation: {spec.get('interpretation', item.finding)} Boundary: {spec.get('limitation', '')} "
            f"Selection score: {item.weighted_score:.2f} ([selection table](research/root_figure_selection.csv))."
        )
    figure_text = "\n\n".join(figure_sections)
    module_map = "\n".join(
        f"| [{row.module_id}]({row.path}/README.md) | {row.title} | {row.question} |"
        for row in module_rows.itertuples(index=False)
    )
    headline = _headline_findings(module_rows)
    methods = "\n".join(
        [
            "| Method family | Used for | Key boundary |",
            "|---|---|---|",
            "| Correlation, partial correlation, clustered heatmaps | dependence/regime diagnostics | association, not causation |",
            "| PCA/common-factor decomposition | selected-major and cross-asset structure | descriptive factor structure only |",
            "| HAC OLS, block/partial R-squared, FDR, VIF, ridge | macro/TradFi exposure | contemporaneous co-movement |",
            "| Quantile/tail, logit-style state tables, event/placebo windows | derivatives and event stress | stress diagnostics |",
            "| Lag-response and block bootstrap | ETF flow plumbing | timing/simultaneity caveats |",
            "| Coverage, unit, timing, and measurement-risk audits | data governance | release risk and semantics before claims |",
        ]
    )
    status_list = ", ".join(f"`{key}`={value}" for key, value in sorted(usage_counts.items()))
    return f"""# Crypto Market Dynamics

## Project Overview

Crypto Market Dynamics is an empirical research and experimentation repository that uses the full available crypto, market, macro, derivatives, ETF, stablecoin/DeFi, on-chain, chain-fundamental, and point-in-time data universe to investigate price behavior, cross-asset relationships, liquidity, leverage, market-microstructure proxies, risk transmission, and the evolution of the broader crypto market and relevant assets and sectors.

The repository is descriptive and associational. Forecasting and trading-strategy claims are outside scope.

## What This Repository Analyzes

- Cross-asset crypto and TradFi dependence, common-factor structure, and lower-tail co-exceedance.
- Macro/TradFi integration through synchronized exposure models and rolling co-movement diagnostics.
- Derivatives leverage, funding, open-interest scaling, and liquidation stress states.
- ETF flow timing, lag-response, absorption, and flow-shock/placebo diagnostics.
- Stablecoin/DeFi balance-sheet state proxies and valuation-contamination checks.
- On-chain valuation/holder behavior with same-day MVRV treated as measurement mechanics.
- Chain fundamentals, monthly point-in-time sector/state variables, relative selected-asset risk, and event stress synthesis.

## Data Universe and Asset Coverage

The data-foundation module inventories provider files, processed panels, feature semantics, asset identity, timing, units, and release risk. Current data-usage counts are {status_list or "available in the data-foundation module"}.

The selected crypto universe audits BTC, ETH, BNB, SOL, XRP, DOGE, TRX, TON, ADA, HYPE, and any locally covered current-cohort assets. TradFi/macro coverage includes SPY, QQQ, IWM, DXY, gold, VIX, nominal and real yield changes where local panels support matched samples.

## Research Modules

| Module | Title | Scope |
|---|---|---|
{module_map}

## Headline Findings

{headline}

## Selected Analytical Results

{figure_text}

## Methods Used

{methods}

## Important Limitations

- Current-cohort daily selected-major analysis is survivorship-biased and cannot establish historical altseason behavior.
- ETF flows are market-plumbing associations with timing and simultaneity concerns.
- Stablecoin supply, DeFi TVL, and related balance-sheet measures are endogenous state proxies; raw USD TVL is valuation-sensitive.
- Same-day MVRV is a mechanically price-linked valuation-state diagnostic and is excluded from primary BTC/ETH models.
- Monthly point-in-time data supports composition, concentration, turnover, and state variables only, not daily constituent returns.

## Reproduce

```bash
uv sync --all-extras
uv run ruff check src/cqresearch scripts tests
uv run ruff format --check src/cqresearch scripts tests
uv run mypy src/cqresearch
uv run pytest -q
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py --module all
```

## Repository Structure

- [`research/`](research/README.md): canonical public research surface.
- [`src/cqresearch/`](src/cqresearch): pipeline, research, and visualization code.
- [`scripts/`](scripts): thin command-line entry points.
- [`config/`](config): feature, figure, module, and event registries.
- `data_local/`: local raw and processed provider data; intentionally untracked.

## Data Policy and Citation

Raw/provider data stays local under `data_local/` and outside Git. Public tables and figures are derived semantic outputs designed for review and reproducibility without redistributing restricted exports.

This repository is independent research infrastructure and is not affiliated with any provider. Cite the repository, commit hash, module, table, figure, sample definition, and limitations when referencing a result.
"""


def _research_index(
    module_rows: pd.DataFrame, figure_specs: pd.DataFrame, usage_counts: dict[str, int]
) -> str:
    module_map = "\n".join(
        "| [{module_id}]({relpath}/README.md) | {title} | {tables} | {figures} |".format(
            module_id=row.module_id,
            relpath=Path(row.path).relative_to("research").as_posix(),
            title=row.title,
            tables=row.table_count,
            figures=row.figure_count,
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

This directory is the canonical public research surface for Crypto Market Dynamics. It contains generated modules, tables, figures, manifests, and the root figure-selection audit.

## Module Map

| Module | Title | Tables | Figures |
|---|---|---:|---:|
{module_map}

## Root Figure Set

{figure_list}

## Data-Usage Status Counts

{status_list}

## Provenance

- Root manifest: [`manifest.json`](manifest.json)
- Figure specifications: [`figure_specs.csv`](figure_specs.csv)
- Root figure selection: [`root_figure_selection.csv`](root_figure_selection.csv)
- Cross-module evidence ledger: [`09_event_stress_cross_module_synthesis/tables/evidence_ledger.csv`](09_event_stress_cross_module_synthesis/tables/evidence_ledger.csv)

## Rebuild

```bash
uv run python scripts/run_research.py --module all
uv run python scripts/build_research_figures.py --module all
uv run python scripts/check_research_surface.py --module all
```
"""


def _headline_findings(module_rows: pd.DataFrame) -> str:
    rows = []
    for module in module_rows["module_id"]:
        claims_path = Path("research") / str(module) / "tables" / "claims.csv"
        if not claims_path.exists():
            continue
        claims = pd.read_csv(claims_path)
        if claims.empty:
            continue
        claim = claims.iloc[0]
        rows.append(
            "| {module} | {finding} | {grade} | [{table}]({table}) | {limitation} |".format(
                module=module,
                finding=str(claim.get("claim_text", "")),
                grade=str(claim.get("evidence_grade", "")),
                table=str(claim.get("source_table", ""))
                .split(";")[0]
                .replace("tables/", f"research/{module}/tables/"),
                limitation=str(claim.get("limitation", "")),
            )
        )
    header = "| Module | Finding | Grade | Source | Limitation |\n|---|---|---|---|---|"
    return header + "\n" + "\n".join(rows[:10])


def _write_root_manifest(
    root: Path,
    module_rows: pd.DataFrame,
    figure_specs: pd.DataFrame,
    selection: pd.DataFrame,
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
        "selected_root_figures": selection[selection["selected"].eq(True)]["figure_id"].tolist()
        if not selection.empty
        else [],
        "data_usage_status_counts": usage_counts,
        "artifacts": root_records + module_manifest_records,
    }
    return write_json(root / "research" / "manifest.json", payload)


def _model_ids_from_source_tables(source_tables: str) -> str:
    ids: list[str] = []
    for item in str(source_tables).replace(",", ";").split(";"):
        item = item.strip()
        if item:
            ids.append(f"table:{Path(item).stem}")
    return "; ".join(ids) or "table:claims"


def _chart_type_from_name(name: str) -> str:
    if "correlation" in name:
        return "correlation_heatmap"
    if "pca" in name or "factor" in name:
        return "factor_decomposition"
    if "etf" in name:
        return "etf_lag_response"
    if "mvrv" in name:
        return "measurement_decomposition"
    if "event" in name:
        return "event_placebo_response"
    if "risk" in name or "tail" in name:
        return "risk_decomposition"
    return "analytical_result"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
