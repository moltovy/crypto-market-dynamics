"""Build analytical research modules from verified semantic artifacts."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from config.paths import PROJECT_ROOT
from matplotlib.ticker import PercentFormatter

from cqresearch.core.artifacts import (
    artifact_record,
    read_csv_if_exists,
    write_csv,
    write_json,
    write_text,
)
from cqresearch.research.registry import MODULES, ResearchModule, module_by_id
from cqresearch.viz.theme import apply_theme


@dataclass(frozen=True)
class AnalyticalModuleSpec:
    module_id: str
    source_tables: tuple[str, ...]
    source_figures: tuple[str, ...]
    method_summary: str
    interpretation: str
    limitations: str
    finding_builder: Callable[[Path, Path], tuple[list[str], list[dict[str, Any]]]]
    extra_tables_builder: Callable[[Path, Path], list[Path]] | None = None
    extra_figures_builder: Callable[[Path, Path], list[Path]] | None = None


def build_analytical_module(module_id: str, root: Path = PROJECT_ROOT) -> list[Path]:
    spec = MODULE_SPECS[module_id]
    module = module_by_id(module_id)
    module_dir = root / "research" / module_id
    tables_dir = module_dir / "tables"
    figures_dir = module_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    artifacts: list[Path] = []
    artifacts.extend(_copy_tables(root, tables_dir, spec.source_tables))
    artifacts.extend(_copy_figures(root, figures_dir, spec.source_figures))
    if spec.extra_tables_builder is not None:
        artifacts.extend(spec.extra_tables_builder(root, tables_dir))
    if spec.extra_figures_builder is not None:
        artifacts.extend(spec.extra_figures_builder(root, figures_dir))

    finding_lines, claims = spec.finding_builder(root, module_dir)
    claims_path = write_csv(tables_dir / "claims.csv", pd.DataFrame(_normalize_claims(claims)))
    artifacts.append(claims_path)
    artifacts.extend(
        _write_module_docs(
            root=root,
            module_dir=module_dir,
            module=module,
            spec=spec,
            finding_lines=finding_lines,
            table_names=_public_artifact_names(tables_dir),
            figure_names=_public_artifact_names(figures_dir),
        )
    )
    artifacts.append(_write_manifest(root, module_dir, artifacts))
    return artifacts


def build_all_analytical_modules(root: Path = PROJECT_ROOT) -> list[Path]:
    artifacts: list[Path] = []
    for module_id in MODULE_SPECS:
        artifacts.extend(build_analytical_module(module_id, root))
    return artifacts


def build_research_only_figures(module_id: str, root: Path = PROJECT_ROOT) -> list[Path]:
    module_ids = list(MODULE_SPECS) if module_id == "all" else [module_id]
    artifacts: list[Path] = []
    for item in module_ids:
        spec = MODULE_SPECS[item]
        figures_dir = root / "research" / item / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)
        artifacts.extend(_copy_figures(root, figures_dir, spec.source_figures))
        if spec.extra_figures_builder is not None:
            artifacts.extend(spec.extra_figures_builder(root, figures_dir))
    return artifacts


def _public_artifact_names(directory: Path) -> list[str]:
    return sorted(
        path.name
        for path in directory.glob("*")
        if path.is_file() and not path.name.startswith(".")
    )


def _copy_tables(root: Path, tables_dir: Path, table_names: tuple[str, ...]) -> list[Path]:
    artifacts: list[Path] = []
    for name in table_names:
        source = root / "outputs" / "tables" / name
        destination = tables_dir / name
        if source.suffix.lower() == ".md":
            if source.exists():
                artifacts.append(write_text(destination, source.read_text(encoding="utf-8")))
            elif destination.exists():
                artifacts.append(destination)
            continue
        if source.exists():
            frame = read_csv_if_exists(source)
        elif destination.exists():
            frame = read_csv_if_exists(destination)
        else:
            frame = pd.DataFrame(
                [
                    {
                        "source_table": name,
                        "status": "missing",
                        "note": f"Missing migration source table {name}",
                    }
                ]
            )
        artifacts.append(write_csv(destination, frame))
    return artifacts


def _copy_figures(root: Path, figures_dir: Path, figure_names: tuple[str, ...]) -> list[Path]:
    artifacts: list[Path] = []
    for relname in figure_names:
        source = root / "outputs" / "figures" / relname
        destination = figures_dir / source.name
        if not source.exists():
            if destination.exists():
                artifacts.append(destination)
            continue
        shutil.copy2(source, destination)
        artifacts.append(destination)
    return artifacts


def _write_module_docs(
    root: Path,
    module_dir: Path,
    module: ResearchModule,
    spec: AnalyticalModuleSpec,
    finding_lines: list[str],
    table_names: list[str],
    figure_names: list[str],
) -> list[Path]:
    table_list = "\n".join(f"- `tables/{name}`" for name in table_names) or "- No tables."
    figure_list = "\n".join(f"- `figures/{name}`" for name in figure_names) or "- No figures."
    findings = "\n".join(f"- {line}" for line in finding_lines)
    docs = [
        write_text(
            module_dir / "README.md",
            f"""# {module.module_id}: {module.title}

## Research Question

{module.research_question}

## Current Findings

{findings}

## Tables

{table_list}

## Figures

{figure_list}
""",
        ),
        write_text(
            module_dir / "methodology.md",
            f"""# Methodology

{spec.method_summary}

All migrated tables keep their original row-level sample, calendar, timing, and method fields where those fields exist. Module claims are restricted to the copied or newly computed tables in this directory.
""",
        ),
        write_text(module_dir / "findings.md", f"# Findings\n\n{findings}"),
        write_text(module_dir / "interpretation.md", f"# Interpretation\n\n{spec.interpretation}"),
        write_text(module_dir / "limitations.md", f"# Limitations\n\n{spec.limitations}"),
    ]
    module_yml = {
        "module_id": module.module_id,
        "title": module.title,
        "research_question": module.research_question,
        "research_questions": [module.research_question],
        "outcomes": _module_outcomes(module.module_id),
        "features": _module_features(module.module_id),
        "frequencies": _module_frequencies(module.module_id),
        "methods": _module_methods(spec.method_summary),
        "sensitivity_dimensions": _module_sensitivity_dimensions(module.module_id),
        "status": "built",
        "canonical_surface": module_dir.relative_to(root).as_posix(),
        "tables": table_names,
        "figures": figure_names,
        "code": [
            "src/cqresearch/research/analytical_modules.py",
            "src/cqresearch/pipelines/research.py",
        ],
        "tests": [
            "tests/unit/test_feature_strength_outputs.py",
            "tests/unit/test_visual_outputs.py",
        ],
        "root_readme_candidate_figures": [
            f"figures/{name}" for name in figure_names if name.lower().endswith(".png")
        ],
    }
    docs.append(write_text(module_dir / "module.yml", yaml.safe_dump(module_yml, sort_keys=False)))
    return docs


def _write_manifest(root: Path, module_dir: Path, artifacts: list[Path]) -> Path:
    payload = {
        "module_id": module_dir.name,
        "schema_version": 1,
        "build_timestamp_utc": "not_recorded_for_deterministic_rebuilds",
        "artifacts": [artifact_record(path, root) for path in sorted(artifacts)],
    }
    return write_json(module_dir / "manifest.json", payload)


def _normalize_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for claim in claims:
        row = dict(claim)
        claim_text = str(row.get("claim_text", ""))
        row.setdefault("module", row.get("module_id", ""))
        row.setdefault("finding", claim_text)
        row.setdefault("outcome", "module-level evidence")
        row.setdefault("feature_or_block", "see source_table")
        row.setdefault("estimate_summary", claim_text)
        row.setdefault("uncertainty_summary", row.get("uncertainty", "See source table."))
        row.setdefault("sample_summary", row.get("sample", "See source table."))
        row.setdefault("frequency", "see source table")
        row.setdefault("timing", "see source table")
        row.setdefault("sensitivity_summary", row.get("method", "See source table."))
        row.setdefault("interpretation", claim_text)
        row.setdefault("alternative_explanation", row.get("limitation", "See module limitations."))
        row.setdefault(
            "source_model_ids", _model_ids_from_source_tables(row.get("source_table", ""))
        )
        normalized.append(row)
    return normalized


def _model_ids_from_source_tables(source_table: Any) -> str:
    ids: list[str] = []
    for item in str(source_table).replace(",", ";").split(";"):
        item = item.strip()
        if item:
            ids.append(f"table:{Path(item).stem}")
    return "; ".join(ids) or "table:claims"


def _module_methods(method_summary: str) -> list[str]:
    lowered = method_summary.lower()
    methods = ["descriptive statistics"]
    for token, label in [
        ("hac", "HAC OLS"),
        ("r2", "same-support block and partial R-squared"),
        ("rolling", "rolling exposure diagnostics"),
        ("logit", "tail-event logit diagnostics"),
        ("quantile", "quantile/tail diagnostics"),
        ("placebo", "event/placebo comparison"),
        ("fdr", "FDR adjustment"),
        ("ridge", "ridge stability"),
        ("panel", "panel-readiness audit"),
    ]:
        if token in lowered:
            methods.append(label)
    return list(dict.fromkeys(methods))


def _module_outcomes(module_id: str) -> list[str]:
    return {
        "01_returns_risk_regimes": ["BTC/ETH returns", "volatility", "drawdown", "tail loss"],
        "02_macro_cross_asset_exposure": ["BTC/ETH returns", "co-movement R-squared"],
        "03_derivatives_leverage_liquidations": [
            "volatility",
            "tail-event frequency",
            "liquidation event response",
        ],
        "04_etf_institutional_plumbing": ["BTC/ETH returns", "flow intensity", "absorption"],
        "05_stablecoin_defi_liquidity": [
            "returns",
            "volatility",
            "tail state",
            "valuation contamination",
        ],
        "06_onchain_valuation_holder_state": [
            "MVRV mechanics",
            "holder-state regimes",
            "tail/volatility state",
        ],
        "07_chain_fundamentals": ["chain coverage", "activity association", "panel readiness"],
        "08_relative_major_asset_risk": ["volatility", "drawdown", "beta", "matched-window risk"],
        "09_market_concentration_state": ["monthly concentration", "turnover", "rank persistence"],
        "10_event_sensitivity": ["event-window return", "volatility change", "placebo percentile"],
        "11_cross_module_synthesis": [
            "evidence grade",
            "stability",
            "measurement risk",
            "null findings",
        ],
    }.get(module_id, ["module-level evidence"])


def _module_features(module_id: str) -> list[str]:
    return {
        "01_returns_risk_regimes": ["BTC price", "ETH price", "realized volatility", "drawdown"],
        "02_macro_cross_asset_exposure": ["equities", "VIX", "DXY", "gold", "nominal/real yields"],
        "03_derivatives_leverage_liquidations": [
            "open interest",
            "funding",
            "leverage",
            "liquidations",
        ],
        "04_etf_institutional_plumbing": [
            "ETF net flow",
            "ETF AUM",
            "lagged market capitalization",
        ],
        "05_stablecoin_defi_liquidity": ["stablecoin supply", "TVL", "DEX/lending activity"],
        "06_onchain_valuation_holder_state": [
            "MVRV",
            "market cap",
            "realized cap",
            "holder-state metrics",
        ],
        "07_chain_fundamentals": ["fees", "revenue", "addresses", "transactions", "chain TVL"],
        "08_relative_major_asset_risk": [
            "selected-major returns",
            "BTC benchmark",
            "ETH benchmark",
        ],
        "09_market_concentration_state": [
            "HHI",
            "top-share fields",
            "turnover",
            "rank persistence",
        ],
        "10_event_sensitivity": ["event registry", "pre-event state", "placebo windows"],
        "11_cross_module_synthesis": ["module claims", "evidence grades", "measurement-risk flags"],
    }.get(module_id, ["see feature usage matrix"])


def _module_frequencies(module_id: str) -> list[str]:
    if module_id == "09_market_concentration_state":
        return ["monthly"]
    if module_id in {"05_stablecoin_defi_liquidity", "07_chain_fundamentals"}:
        return ["weekly", "daily where source support exists"]
    if module_id == "10_event_sensitivity":
        return ["event windows", "daily"]
    return ["daily", "weekly"]


def _module_sensitivity_dimensions(module_id: str) -> list[str]:
    return {
        "01_returns_risk_regimes": ["daily versus weekly", "era definitions", "tail thresholds"],
        "02_macro_cross_asset_exposure": [
            "daily versus weekly",
            "era split",
            "HAC bandwidth",
            "ridge penalty",
        ],
        "03_derivatives_leverage_liquidations": [
            "state bins",
            "lags",
            "tail threshold",
            "raw versus scaled",
        ],
        "04_etf_institutional_plumbing": [
            "flow lag",
            "raw versus scaled flow",
            "BTC versus ETH start date",
        ],
        "05_stablecoin_defi_liquidity": [
            "raw versus scaled TVL",
            "Sunday weekly calendar",
            "lagged state",
        ],
        "06_onchain_valuation_holder_state": [
            "same-day versus lagged",
            "level versus z-score",
            "mechanical overlap",
        ],
        "07_chain_fundamentals": ["coverage threshold", "chain mapping", "metric family"],
        "08_relative_major_asset_risk": ["matched window", "benchmark asset", "coverage threshold"],
        "09_market_concentration_state": ["partial snapshot", "state bins", "monthly lag"],
        "10_event_sensitivity": ["window horizon", "event-day exclusion", "placebo eligibility"],
        "11_cross_module_synthesis": ["evidence grade", "measurement risk", "outcome family"],
    }.get(module_id, ["module-specific sensitivity"])


def _returns_extra_tables(root: Path, tables_dir: Path) -> list[Path]:
    daily_path = root / "data_local" / "processed" / "feature_store_daily.parquet"
    daily = pd.read_parquet(daily_path)
    rows = []
    for asset, ret_col, vol_col, drawdown_col in [
        ("BTC", "btc_ret", "btc_realized_vol_30d", "btc_drawdown"),
        ("ETH", "eth_ret", "eth_realized_vol_30d", "eth_drawdown"),
    ]:
        if ret_col not in daily:
            continue
        returns = pd.to_numeric(daily[ret_col], errors="coerce").dropna()
        downside = returns[returns < 0]
        tail = returns.quantile(0.05)
        rows.append(
            {
                "asset": asset,
                "n": int(len(returns)),
                "sample_start": returns.index.min().date().isoformat(),
                "sample_end": returns.index.max().date().isoformat(),
                "mean_daily_log_return": float(returns.mean()),
                "annualized_volatility": float(returns.std() * np.sqrt(365)),
                "downside_volatility": float(downside.std() * np.sqrt(365))
                if len(downside)
                else np.nan,
                "skew": float(returns.skew()),
                "excess_kurtosis": float(returns.kurt()),
                "q05_log_return": float(tail),
                "expected_shortfall_5pct": float(returns[returns <= tail].mean()),
                "max_drawdown": float(pd.to_numeric(daily.get(drawdown_col), errors="coerce").min())
                if drawdown_col in daily
                else np.nan,
                "median_realized_vol_30d": float(
                    pd.to_numeric(daily.get(vol_col), errors="coerce").median()
                )
                if vol_col in daily
                else np.nan,
            }
        )
    summary = pd.DataFrame(rows)
    regime_rows = []
    regimes = {
        "pre_btc_etf": daily.index < pd.Timestamp("2024-01-11"),
        "btc_etf_era": daily.index >= pd.Timestamp("2024-01-11"),
        "eth_etf_era": daily.index >= pd.Timestamp("2024-07-23"),
    }
    for regime, mask in regimes.items():
        for asset, ret_col in [("BTC", "btc_ret"), ("ETH", "eth_ret")]:
            returns = pd.to_numeric(daily.loc[mask, ret_col], errors="coerce").dropna()
            if returns.empty:
                continue
            tail = returns.quantile(0.05)
            regime_rows.append(
                {
                    "asset": asset,
                    "regime": regime,
                    "n": int(len(returns)),
                    "sample_start": returns.index.min().date().isoformat(),
                    "sample_end": returns.index.max().date().isoformat(),
                    "annualized_volatility": float(returns.std() * np.sqrt(365)),
                    "q05_log_return": float(tail),
                    "expected_shortfall_5pct": float(returns[returns <= tail].mean()),
                    "method": "descriptive fixed-date regime split",
                }
            )
    return [
        write_csv(tables_dir / "returns_distribution_summary.csv", summary),
        write_csv(tables_dir / "returns_regime_risk_summary.csv", pd.DataFrame(regime_rows)),
    ]


def _market_structure_figure(root: Path, figures_dir: Path) -> list[Path]:
    source = root / "outputs" / "tables" / "pit_market_structure_summary.csv"
    frame = read_csv_if_exists(source)
    if frame.empty:
        return []
    frame["month_date"] = pd.to_datetime(frame["month"] + "-01", errors="coerce")
    frame = frame.dropna(subset=["month_date"]).sort_values("month_date")
    apply_theme()
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    axes[0].plot(frame["month_date"], frame["hhi"], color="#2F5D62", linewidth=2)
    axes[0].set_ylabel("HHI")
    axes[0].set_title("Monthly point-in-time concentration")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[1].plot(frame["month_date"], frame["rank_persistence"], color="#7A4E2D", linewidth=2)
    axes[1].set_ylabel("Rank persistence")
    axes[1].set_title("Top-100 rank persistence")
    axes[1].grid(True, axis="y", alpha=0.25)
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Monthly Concentration and Top-100 Rank Persistence")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save_module_figure(fig, figures_dir / "market_concentration_state.png")


def _returns_risk_figure(root: Path, figures_dir: Path) -> list[Path]:
    source = (
        root
        / "research"
        / "01_returns_risk_regimes"
        / "tables"
        / "returns_distribution_summary.csv"
    )
    frame = read_csv_if_exists(source)
    if frame.empty:
        return []
    apply_theme()
    plot = frame[frame["asset"].isin(["BTC", "ETH"])].copy()
    plot["max_drawdown_loss"] = -pd.to_numeric(plot["max_drawdown"], errors="coerce")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.80, wspace=0.32)
    fig.suptitle(
        "BTC and ETH realized risk is summarized, not forecast", fontsize=14, fontweight="semibold"
    )
    _bar_with_labels(
        axes[0],
        plot["asset"],
        pd.to_numeric(plot["annualized_volatility"], errors="coerce"),
        "Annualized volatility",
        "Daily realized distribution",
        percent=True,
    )
    _bar_with_labels(
        axes[1],
        plot["asset"],
        plot["max_drawdown_loss"],
        "Maximum drawdown loss",
        "Full-sample drawdown",
        percent=True,
        color="#9A5A44",
        edge="#6E3C2F",
    )
    return _save_module_figure(fig, figures_dir / "returns_risk_distribution.png")


def _liquidity_state_figure(root: Path, figures_dir: Path) -> list[Path]:
    source = (
        root / "research" / "05_stablecoin_defi_liquidity" / "tables" / "liquidity_associations.csv"
    )
    frame = read_csv_if_exists(source)
    if frame.empty:
        return []
    apply_theme()
    features = [
        "stablecoin_supply_growth",
        "valuation_sensitive_defi_tvl_growth",
        "stablecoin_to_tvl",
    ]
    outcomes = ["btc_ret", "eth_ret"]
    plot = frame[frame["liquidity_feature"].isin(features) & frame["outcome"].isin(outcomes)].copy()
    if plot.empty:
        return []
    labels = {
        "stablecoin_supply_growth": "Stablecoin supply growth",
        "valuation_sensitive_defi_tvl_growth": "USD TVL growth",
        "stablecoin_to_tvl": "Stablecoin / TVL",
        "btc_ret": "BTC",
        "eth_ret": "ETH",
    }
    plot["feature_label"] = plot["liquidity_feature"].map(labels)
    plot["outcome_label"] = plot["outcome"].map(labels)
    pivot = plot.pivot_table(
        index="feature_label", columns="outcome_label", values="correlation", aggfunc="mean"
    ).reindex(index=[labels[item] for item in features], columns=["BTC", "ETH"])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.subplots_adjust(left=0.24, right=0.96, bottom=0.18, top=0.80)
    fig.suptitle(
        "Liquidity-state correlations are strongest where valuation content is high",
        fontsize=14,
        fontweight="semibold",
    )
    _style_module_axis(ax)
    y = np.arange(len(pivot.index))
    width = 0.28
    colors = {"BTC": "#2F5D62", "ETH": "#7A4E2D"}
    for idx, asset in enumerate(["BTC", "ETH"]):
        values = pivot[asset].to_numpy(dtype=float)
        bars = ax.barh(
            y + (idx - 0.5) * width,
            values,
            height=width,
            color=colors[asset],
            edgecolor="#263238",
            linewidth=0.8,
            label=asset,
        )
        for bar, value in zip(bars, values, strict=False):
            ax.text(
                value + (0.015 if value >= 0 else -0.015),
                bar.get_y() + bar.get_height() / 2,
                f"{value:.2f}",
                ha="left" if value >= 0 else "right",
                va="center",
                fontsize=9,
            )
    ax.axvline(0, color="#263238", linewidth=0.9)
    ax.set_yticks(y, pivot.index)
    ax.set_xlabel("Weekly return correlation")
    ax.set_title(
        "Sunday-ended weekly panel; USD TVL is valuation-sensitive", loc="left", fontsize=11
    )
    ax.legend(loc="lower right", frameon=False)
    return _save_module_figure(fig, figures_dir / "liquidity_state_correlations.png")


def _chain_fundamentals_figure(root: Path, figures_dir: Path) -> list[Path]:
    source = (
        root
        / "research"
        / "07_chain_fundamentals"
        / "tables"
        / "chain_fundamental_panel_summary.csv"
    )
    frame = read_csv_if_exists(source)
    if frame.empty:
        return []
    apply_theme()
    adequate = frame[frame["panel_status"].eq("adequate_for_descriptive_panel")].copy()
    if adequate.empty:
        adequate = frame.copy()
    summary = (
        adequate.groupby("chain", as_index=False)
        .agg(metric_count=("metric", "nunique"), median_observations=("observations", "median"))
        .sort_values(["metric_count", "median_observations"], ascending=False)
        .head(12)
    )
    fig, ax = plt.subplots(figsize=(10, 5.4))
    fig.subplots_adjust(left=0.25, right=0.96, bottom=0.15, top=0.82)
    fig.suptitle("Chain-fundamental evidence is coverage-first", fontsize=14, fontweight="semibold")
    _style_module_axis(ax)
    y = np.arange(len(summary))
    bars = ax.barh(
        y,
        summary["metric_count"],
        color="#2F5D62",
        edgecolor="#1F3F43",
        linewidth=0.8,
    )
    ax.set_yticks(y, summary["chain"])
    ax.invert_yaxis()
    ax.set_xlabel("Adequate metric families")
    ax.set_title(
        "Top chains by descriptive-panel coverage; no relationship claim", loc="left", fontsize=11
    )
    for bar, row in zip(bars, summary.itertuples(index=False), strict=False):
        ax.text(
            bar.get_width() + 0.08,
            bar.get_y() + bar.get_height() / 2,
            f"{int(row.metric_count)} metrics; median n={int(row.median_observations)}",
            va="center",
            fontsize=9,
        )
    ax.set_xlim(0, max(summary["metric_count"]) + 2)
    return _save_module_figure(fig, figures_dir / "chain_panel_coverage.png")


def _synthesis_evidence_figure(root: Path, figures_dir: Path) -> list[Path]:
    source = root / "research" / "11_cross_module_synthesis" / "tables" / "evidence_ledger.csv"
    frame = read_csv_if_exists(source)
    if frame.empty:
        return []
    apply_theme()
    source_counts = (
        frame.assign(
            source_count=frame["source_table"]
            .fillna("")
            .astype(str)
            .str.split(";")
            .map(lambda values: len([value for value in values if value.strip()]))
        )
        .groupby("module_id", as_index=False)
        .agg(claim_count=("claim_id", "count"), source_count=("source_count", "sum"))
        .sort_values("module_id")
    )
    title_by_module = {item.module_id: f"{item.module_id[:2]} {item.title}" for item in MODULES}
    source_counts["module_label"] = source_counts["module_id"].map(title_by_module)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    fig.subplots_adjust(left=0.35, right=0.96, bottom=0.15, top=0.82)
    fig.suptitle(
        "Synthesis keeps claim counts and source depth visible", fontsize=14, fontweight="semibold"
    )
    _style_module_axis(ax)
    y = np.arange(len(source_counts))
    height = 0.34
    ax.barh(
        y - height / 2,
        source_counts["source_count"],
        height=height,
        color="#7A4E2D",
        edgecolor="#563620",
        linewidth=0.8,
        label="Source-table links",
    )
    ax.barh(
        y + height / 2,
        source_counts["claim_count"],
        height=height,
        color="#2F5D62",
        edgecolor="#1F3F43",
        linewidth=0.8,
        label="Claims",
    )
    ax.set_yticks(y, source_counts["module_label"])
    ax.invert_yaxis()
    ax.set_xlabel("Count")
    ax.set_title(
        "Every module contributes accepted-qualified claims; source depth varies",
        loc="left",
        fontsize=11,
    )
    ax.legend(loc="lower right", frameon=False)
    return _save_module_figure(fig, figures_dir / "synthesis_claim_source_depth.png")


def _bar_with_labels(
    ax: plt.Axes,
    labels: pd.Series,
    values: pd.Series,
    ylabel: str,
    title: str,
    *,
    percent: bool = False,
    color: str = "#2F5D62",
    edge: str = "#1F3F43",
) -> None:
    _style_module_axis(ax)
    bars = ax.bar(labels.astype(str), values, color=color, edgecolor=edge, linewidth=0.8)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=11)
    if percent:
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    for bar, value in zip(bars, values, strict=False):
        label = f"{value:.1%}" if percent else f"{value:.2f}"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_ylim(0, float(values.max()) * 1.22)


def _style_module_axis(ax: plt.Axes) -> None:
    ax.grid(True, axis="x", alpha=0.22)
    ax.grid(True, axis="y", alpha=0.18)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _save_module_figure(fig: plt.Figure, png: Path) -> list[Path]:
    svg = png.with_suffix(".svg")
    fig.savefig(png, dpi=180, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight", metadata={"Date": None})
    text = svg.read_text(encoding="utf-8")
    svg.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return [png, svg]


def _synthesis_extra_tables(root: Path, tables_dir: Path) -> list[Path]:
    claim_frames = []
    for claims_path in sorted((root / "research").glob("*/tables/claims.csv")):
        if claims_path.parts[-3] == "11_cross_module_synthesis":
            continue
        claim_frames.append(pd.read_csv(claims_path))
    ledger = (
        pd.concat(claim_frames, ignore_index=True, sort=False) if claim_frames else pd.DataFrame()
    )
    if not ledger.empty:
        ledger = ledger[
            [
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
            ]
        ].sort_values(["module_id", "claim_id"])
    evidence_rows = []
    for row in ledger.to_dict("records"):
        evidence_rows.append(
            {
                "Module": row["module_id"],
                "Finding": row["claim_text"],
                "Evidence": row["source_table"],
                "Boundary": row["limitation"],
            }
        )
    evidence_map = pd.DataFrame(evidence_rows)
    ledger_path = write_csv(tables_dir / "evidence_ledger.csv", ledger)
    evidence_csv = write_csv(tables_dir / "evidence_map.csv", evidence_map)
    evidence_md = write_text(
        tables_dir / "evidence_map.md",
        evidence_map.to_markdown(index=False)
        if not evidence_map.empty
        else "| Module | Finding |\n|---|---|",
    )
    return [ledger_path, evidence_csv, evidence_md]


def _returns_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    table = pd.read_csv(module_dir / "tables" / "returns_distribution_summary.csv")
    lines = []
    claims = []
    for row in table.to_dict("records"):
        lines.append(
            f"{row['asset']} has n={int(row['n'])} daily observations, annualized volatility={row['annualized_volatility']:.2%}, max drawdown={row['max_drawdown']:.2%}."
        )
    claims.append(
        _claim(
            "returns_risk_01",
            "01_returns_risk_regimes",
            "BTC and ETH risk summaries are reported as descriptive return-distribution and drawdown statistics.",
            "tables/returns_distribution_summary.csv; tables/returns_regime_risk_summary.csv",
            "figures/returns_risk_distribution.png",
            "Daily log-return sample from local processed feature store.",
            "Descriptive moments, expected shortfall, drawdown, and fixed-date regime splits.",
            "No investability or strategy inference.",
        )
    )
    return lines, claims


def _macro_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    block = pd.read_csv(module_dir / "tables" / "block_delta_r2.csv")
    subset = block[
        block["frequency"].eq("daily")
        & block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["block"].eq("equity_beta")
        & block["regime"].isin(["pre_btc_etf", "btc_etf_era"])
    ]
    lines = []
    for asset in ["BTC", "ETH"]:
        rows = subset[subset["asset"].eq(asset)].set_index("regime")
        if {"pre_btc_etf", "btc_etf_era"}.issubset(rows.index):
            lines.append(
                f"{asset} daily equity-block delta R2 moved from {rows.loc['pre_btc_etf', 'drop_block_delta_r2']:.4f} pre-BTC-ETF to {rows.loc['btc_etf_era', 'drop_block_delta_r2']:.4f} in the BTC-ETF era."
            )
    return lines, [
        _claim(
            "macro_exposure_01",
            "02_macro_cross_asset_exposure",
            "Contemporaneous TradFi exposure is evaluated on synchronized business-date and Friday panels.",
            "tables/block_delta_r2.csv; tables/conventional_partial_r2.csv; tables/rolling_tradfi_exposures.csv",
            "figures/01_tradfi_exposure_shift.png",
            "Effective sample reported per model row.",
            "Same-support HAC OLS, drop-block delta R2, conventional partial R2, FDR, VIF, ridge, and rolling exposure diagnostics.",
            "Period comparison is descriptive and not an ETF-effect estimate.",
        )
    ]


def _leverage_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    table = pd.read_csv(module_dir / "tables" / "leverage_tail_risk_summary.csv")
    states = table[["leverage_state", "n", "bottom5_rate"]].dropna()
    lines = [
        "; ".join(
            f"{row['leverage_state']} tail-day rate={row['bottom5_rate']:.2%} (n={int(row['n'])})"
            for row in states.to_dict("records")
        )
    ]
    return lines, [
        _claim(
            "leverage_tail_01",
            "03_derivatives_leverage_liquidations",
            "Lagged leverage states are reported as stress diagnostics with visible tail-rate differences.",
            "tables/leverage_tail_risk_summary.csv; tables/tail_risk_models.csv; tables/liquidation_event_responses.csv",
            "figures/03_leverage_tail_stress.png",
            "Daily BTC rows with available leverage-state fields.",
            "Descriptive leverage-state quintiles, lagged logit diagnostics, and fixed post-event windows.",
            "Liquidations are same-day stress signatures, not identified price-move causes.",
        )
    ]


def _etf_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    assoc = pd.read_csv(module_dir / "tables" / "etf_flow_associations.csv")
    lines = []
    for asset in ["BTC", "ETH"]:
        rows = assoc[assoc["asset"].eq(asset)].set_index("flow_lag_days")
        if {0, 1}.issubset(set(rows.index.astype(int))):
            lag0 = rows.loc[0, "return_corr"]
            lag1 = rows.loc[1, "return_corr"]
            lines.append(
                f"{asset} ETF flow-intensity return correlation is {lag0:.3f} at lag 0 versus {lag1:.3f} at lag 1."
            )
    return lines, [
        _claim(
            "etf_plumbing_01",
            "04_etf_institutional_plumbing",
            "ETF flow intensity is a market-plumbing association grid, not a causal price-impact estimate.",
            "tables/etf_flow_associations.csv; tables/etf_absorption_metrics.csv; tables/etf_data_timing_audit.csv",
            "figures/02_etf_market_plumbing.png",
            "ETF trading dates with local Farside flow data and lagged market-cap denominators.",
            "Correlation grid, absorption ratios, timing audit, and augmented exposure table.",
            "Daily flow timestamps and simultaneity prevent causal interpretation.",
        )
    ]


def _liquidity_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    assoc = pd.read_csv(module_dir / "tables" / "liquidity_associations.csv")
    tvl = assoc[assoc["liquidity_feature"].str.contains("defi_tvl", na=False)]
    lines = []
    if not tvl.empty:
        btc = tvl[tvl["outcome"].eq("btc_ret")]
        eth = tvl[tvl["outcome"].eq("eth_ret")]
        if not btc.empty and not eth.empty:
            lines.append(
                f"Raw USD TVL same-week correlations are BTC={btc.iloc[0]['correlation']:.3f} and ETH={eth.iloc[0]['correlation']:.3f}; the unit audit labels TVL valuation-sensitive."
            )
    return lines or [
        "Stablecoin and DeFi outputs are retained as liquidity-state diagnostics with valuation-contamination warnings."
    ], [
        _claim(
            "liquidity_state_01",
            "05_stablecoin_defi_liquidity",
            "Stablecoin supply and DeFi TVL are endogenous liquidity-state proxies; raw USD TVL is valuation-sensitive.",
            "tables/liquidity_associations.csv; tables/stablecoin_defi_liquidity_summary.csv; tables/valuation_contamination_audit.csv",
            "figures/liquidity_state_correlations.png",
            "Sunday-ended weekly crypto panel.",
            "Weekly correlations, regime summaries, and unit/valuation contamination audit.",
            "No liquidity-shock or exogenous-flow language.",
        )
    ]


def _onchain_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    audit = pd.read_csv(module_dir / "tables" / "mvrv_mechanical_link_audit.csv").set_index(
        "metric"
    )
    corr = audit.loc["corr_btc_return_d_log_mvrv", "value"]
    r2 = audit.loc["same_day_mvrv_r2_diagnostic", "value"]
    residual = audit.loc["identity_residual_abs_median_to_median_abs_btc_return", "value"]
    return [
        f"Same-day BTC return and d-log MVRV correlation is {corr:.4f}; same-day diagnostic R2 is {r2:.4f}; residual scale ratio is {residual:.2e}."
    ], [
        _claim(
            "onchain_mvrv_01",
            "06_onchain_valuation_holder_state",
            "Same-day MVRV is a mechanical valuation-state diagnostic, not an independent primary factor.",
            "tables/mvrv_mechanical_link_audit.csv; tables/mvrv_identity_points.csv",
            "figures/measurement_mvrv_mechanics.png",
            "Daily BTC rows with MVRV and realized-cap fields.",
            "Same-interval identity audit, same-day HAC diagnostic, residual quantiles, and lagged state table.",
            "Source conventions and realized-cap updates affect residual interpretation.",
        )
    ]


def _chain_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    summary = pd.read_csv(module_dir / "tables" / "chain_fundamental_panel_summary.csv")
    chains = summary["chain"].nunique() if "chain" in summary else 0
    metrics = summary["metric"].nunique() if "metric" in summary else 0
    return [
        f"Chain fundamentals inventory spans {metrics} metrics across {chains} chains; panel status remains coverage-first until estimable models pass module-specific checks."
    ], [
        _claim(
            "chain_fundamentals_01",
            "07_chain_fundamentals",
            "Chain fundamentals currently support coverage and panel-readiness review before public relationship claims.",
            "tables/chain_fundamental_panel_summary.csv; tables/chain_activity_associations.csv",
            "figures/chain_panel_coverage.png",
            "Local Artemis/chain fundamentals coverage table.",
            "Coverage inventory and explicit association-status table.",
            "No chain-fundamental effect claim until panel specification and sensitivity checks are complete.",
        )
    ]


def _relative_risk_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    comparable = pd.read_csv(module_dir / "tables" / "selected_major_comparable_window_metrics.csv")
    symbols = comparable["symbol"].nunique()
    start = comparable["common_start"].iloc[0]
    end = comparable["common_end"].iloc[0]
    return [
        f"{symbols} selected majors share a comparable weekly window from {start} to {end}; short-history caveats remain visible."
    ], [
        _claim(
            "relative_risk_01",
            "08_relative_major_asset_risk",
            "Selected-major comparisons are matched-window descriptive risk summaries.",
            "tables/selected_major_risk_metrics.csv; tables/selected_major_comparable_window_metrics.csv; tables/selected_major_betas.csv",
            "figures/05_selected_major_asset_risk.png",
            "Selected major assets with local coverage and canonical identity mapping.",
            "Matched-window volatility, downside volatility, drawdown, positive-week share, beta, and coverage audit.",
            "Short histories, especially HYPE, limit cross-asset comparability.",
        )
    ]


def _market_structure_findings(
    root: Path, module_dir: Path
) -> tuple[list[str], list[dict[str, Any]]]:
    summary = pd.read_csv(module_dir / "tables" / "pit_market_structure_summary.csv")
    latest = summary.sort_values("snapshot_date").iloc[-1]
    return [
        f"Latest PIT snapshot {latest['snapshot_date']} has top10 share={latest['top10_share']:.2%}, HHI={latest['hhi']:.3f}, and rank persistence={latest['rank_persistence']:.2%}."
    ], [
        _claim(
            "market_concentration_01",
            "09_market_concentration_state",
            "Monthly point-in-time data supports concentration, turnover, and rank-persistence state analysis.",
            "tables/pit_market_structure_summary.csv; tables/pit_concentration.csv; tables/pit_turnover.csv",
            "figures/market_concentration_state.png",
            "Monthly PIT top-200 snapshots with top-100 concentration state.",
            "HHI, top-share fields, entries, exits, and rank persistence.",
            "No daily constituent-performance claim; visualization uses concentration and rank persistence only.",
        )
    ]


def _event_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    inference = pd.read_csv(module_dir / "tables" / "event_inference.csv")
    med_placebos = inference["placebo_window_count"].median()
    assets = ",".join(sorted(inference["asset"].unique()))
    return [
        f"{assets} event windows use block size 10 with median eligible placebo windows={med_placebos:.0f}; windows exclude event day."
    ], [
        _claim(
            "event_sensitivity_01",
            "10_event_sensitivity",
            "Registered event windows are descriptive and compared with empirical placebo windows.",
            "tables/event_response_matrix.csv; tables/event_inference.csv; tables/event_atlas.csv",
            "figures/appendix_event_response_matrix.png",
            "Registered primary and exploratory events with BTC/ETH return windows.",
            "Fixed +1 through +10 windows, volatility-change summaries, and empirical placebo p-values.",
            "Event windows are sensitivity diagnostics, not causal identification.",
        )
    ]


def _synthesis_findings(root: Path, module_dir: Path) -> tuple[list[str], list[dict[str, Any]]]:
    ledger = pd.read_csv(module_dir / "tables" / "evidence_ledger.csv")
    grades = ledger["evidence_grade"].value_counts().to_dict()
    accepted = int(ledger["status"].astype(str).str.contains("accepted", na=False).sum())
    return [
        f"Evidence ledger contains {len(ledger)} claims, {accepted} accepted-qualified entries, and grade counts {grades}."
    ], [
        _claim(
            "synthesis_01",
            "11_cross_module_synthesis",
            "Cross-module synthesis ranks evidence by claim, sample, method, uncertainty, measurement risk, and limitation rather than by a single score.",
            "tables/evidence_ledger.csv; tables/robustness_summary.csv; tables/claim_inventory.csv",
            "figures/synthesis_claim_source_depth.png",
            "All migrated module evidence rows.",
            "Evidence ledger, robustness summary, claim inventory, FDR/local-window diagnostics.",
            "Synthesis depends on upstream module quality and does not create new causal identification.",
        )
    ]


def _claim(
    claim_id: str,
    module_id: str,
    claim_text: str,
    source_table: str,
    source_figure: str,
    sample: str,
    method: str,
    limitation: str,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "module_id": module_id,
        "claim_text": claim_text,
        "sample": sample,
        "method": method,
        "uncertainty": "Reported in source tables where model estimates are present; otherwise descriptive and coverage-bound.",
        "evidence_grade": "B",
        "source_table": source_table,
        "source_figure": source_figure,
        "limitation": limitation,
        "status": "accepted_qualified",
    }


MODULE_SPECS: dict[str, AnalyticalModuleSpec] = {
    "01_returns_risk_regimes": AnalyticalModuleSpec(
        module_id="01_returns_risk_regimes",
        source_tables=("cycle_state_summary.csv",),
        source_figures=(),
        method_summary="Daily BTC/ETH log returns are summarized with moments, annualized volatility, downside volatility, expected shortfall, drawdown, and fixed-date regime splits.",
        interpretation="Risk summaries describe realized sample behavior. They are not trading rules or expected-return forecasts.",
        limitations="Regime splits are descriptive calendar partitions and do not identify the source of risk changes.",
        finding_builder=_returns_findings,
        extra_tables_builder=_returns_extra_tables,
        extra_figures_builder=_returns_risk_figure,
    ),
    "02_macro_cross_asset_exposure": AnalyticalModuleSpec(
        module_id="02_macro_cross_asset_exposure",
        source_tables=(
            "block_delta_r2.csv",
            "conventional_partial_r2.csv",
            "btc_ex_mvrv_feature_strength.csv",
            "eth_feature_strength.csv",
            "rolling_tradfi_exposures.csv",
            "rolling_exposure_summary.csv",
            "exposure_regime_comparison.csv",
            "multicollinearity_diagnostics.csv",
            "ridge_stability.csv",
            "fdr_adjusted_inference.csv",
            "frequency_robustness.csv",
            "local_window_correlation_distribution.csv",
        ),
        source_figures=(
            "public/01_tradfi_exposure_shift.png",
            "public/01_tradfi_exposure_shift.svg",
        ),
        method_summary="Models use synchronized daily business-date and Friday weekly panels, HAC OLS, same-support block deletion, conventional partial R2, FDR, VIF, ridge, and rolling beta/correlation diagnostics.",
        interpretation="The module estimates contemporaneous exposure and co-movement, not macro causality or forecasts.",
        limitations="Period splits and rolling windows are descriptive; ETF-era changes are not identified ETF effects.",
        finding_builder=_macro_findings,
    ),
    "03_derivatives_leverage_liquidations": AnalyticalModuleSpec(
        module_id="03_derivatives_leverage_liquidations",
        source_tables=(
            "leverage_feature_registry.csv",
            "leverage_state_summary.csv",
            "leverage_tail_risk_summary.csv",
            "tail_risk_models.csv",
            "liquidation_event_responses.csv",
        ),
        source_figures=("public/03_leverage_tail_stress.png", "public/03_leverage_tail_stress.svg"),
        method_summary="Lagged leverage-state quintiles, funding z-scores, OI/market-cap scaling, liquidation ratios, logit diagnostics, and fixed post-event windows are used as stress diagnostics.",
        interpretation="Leverage and liquidation measures describe stress states and signatures.",
        limitations="Liquidation observations are timing-sensitive and cannot establish that liquidations caused subsequent returns.",
        finding_builder=_leverage_findings,
    ),
    "04_etf_institutional_plumbing": AnalyticalModuleSpec(
        module_id="04_etf_institutional_plumbing",
        source_tables=(
            "etf_absorption_metrics.csv",
            "etf_data_timing_audit.csv",
            "etf_era_exposure_comparison.csv",
            "etf_flow_associations.csv",
            "etf_flow_shock_days.csv",
            "etf_market_plumbing_summary.csv",
        ),
        source_figures=("public/02_etf_market_plumbing.png", "public/02_etf_market_plumbing.svg"),
        method_summary="ETF net flows are scaled by lagged market capitalization and evaluated with lag grids, absorption metrics, timing audit, flow-shock days, and augmented exposure rows.",
        interpretation="Flow intensity is market plumbing. Same-day associations may reflect simultaneity and reporting timing.",
        limitations="No daily flow result is causal price impact.",
        finding_builder=_etf_findings,
    ),
    "05_stablecoin_defi_liquidity": AnalyticalModuleSpec(
        module_id="05_stablecoin_defi_liquidity",
        source_tables=(
            "stablecoin_liquidity_features.csv",
            "stablecoin_defi_liquidity_summary.csv",
            "liquidity_associations.csv",
            "liquidity_regime_summary.csv",
            "defi_activity_features.csv",
            "valuation_contamination_audit.csv",
        ),
        source_figures=(),
        method_summary="Weekly stablecoin supply, DeFi TVL, TVL ratios, and crypto returns are summarized on a Sunday-ended calendar with explicit valuation-contamination checks.",
        interpretation="Stablecoin and DeFi variables are endogenous state proxies. USD TVL is valuation-sensitive.",
        limitations="Weak or valuation-sensitive liquidity relationships are not promoted into root README figures.",
        finding_builder=_liquidity_findings,
        extra_figures_builder=_liquidity_state_figure,
    ),
    "06_onchain_valuation_holder_state": AnalyticalModuleSpec(
        module_id="06_onchain_valuation_holder_state",
        source_tables=(
            "mvrv_mechanical_link_audit.csv",
            "mvrv_identity_points.csv",
            "mvrv_regime_outcomes.csv",
            "onchain_state_regimes.csv",
        ),
        source_figures=(
            "gallery/measurement_mvrv_mechanics.png",
            "gallery/measurement_mvrv_mechanics.svg",
        ),
        method_summary="MVRV is decomposed through same-interval market-cap and realized-cap changes, residual quantiles, same-day HAC diagnostic, and lagged valuation-state summaries.",
        interpretation="Same-day MVRV is measurement mechanics. Lagged holder-state variables may be state diagnostics when clearly timed.",
        limitations="Realized-cap conventions and source updates affect identity residuals.",
        finding_builder=_onchain_findings,
    ),
    "07_chain_fundamentals": AnalyticalModuleSpec(
        module_id="07_chain_fundamentals",
        source_tables=("chain_fundamental_panel_summary.csv", "chain_activity_associations.csv"),
        source_figures=(),
        method_summary="Chain-level activity inputs are first assessed for chain mapping, metric coverage, sample windows, and panel-readiness before any relationship model is promoted.",
        interpretation="Coverage and definition clarity come before cross-chain inference.",
        limitations="Current migrated outputs do not yet support a strong public chain-fundamentals relationship claim.",
        finding_builder=_chain_findings,
        extra_figures_builder=_chain_fundamentals_figure,
    ),
    "08_relative_major_asset_risk": AnalyticalModuleSpec(
        module_id="08_relative_major_asset_risk",
        source_tables=(
            "selected_major_coverage.csv",
            "selected_major_risk_metrics.csv",
            "selected_major_comparable_window_metrics.csv",
            "selected_major_betas.csv",
            "asset_identity_audit.csv",
            "asset_taxonomy.csv",
        ),
        source_figures=(
            "public/05_selected_major_asset_risk.png",
            "public/05_selected_major_asset_risk.svg",
        ),
        method_summary="Selected majors use canonical identity mapping, coverage checks, max-coverage risk metrics, matched-window metrics, and benchmark beta/correlation summaries.",
        interpretation="Relative risk is descriptive and coverage-aware.",
        limitations="Short histories and exchange/listing differences limit cross-asset comparisons.",
        finding_builder=_relative_risk_findings,
    ),
    "09_market_concentration_state": AnalyticalModuleSpec(
        module_id="09_market_concentration_state",
        source_tables=(
            "pit_market_structure_summary.csv",
            "pit_concentration.csv",
            "pit_turnover.csv",
            "pit_period_comparison.csv",
            "pit_market_structure_monthly.csv",
            "asset_identity_audit.csv",
        ),
        source_figures=(),
        method_summary="Monthly point-in-time snapshots are used for HHI, top-share fields, entries, exits, rank persistence, and identity audit. Market-share charts are deliberately excluded.",
        interpretation="PIT data supports market-structure state analysis, not daily historical constituent returns.",
        limitations="Partial months and monthly frequency limit timing precision.",
        finding_builder=_market_structure_findings,
        extra_figures_builder=_market_structure_figure,
    ),
    "10_event_sensitivity": AnalyticalModuleSpec(
        module_id="10_event_sensitivity",
        source_tables=("event_atlas.csv", "event_response_matrix.csv", "event_inference.csv"),
        source_figures=(
            "gallery/appendix_event_response_matrix.png",
            "gallery/appendix_event_response_matrix.svg",
        ),
        method_summary="Registered events use fixed +1 through +10 return windows, volatility-change summaries, and empirical placebo windows that exclude registered-event neighborhoods.",
        interpretation="Event outputs are sensitivity diagnostics and historical context.",
        limitations="No event claim is causal without an identification design.",
        finding_builder=_event_findings,
    ),
    "11_cross_module_synthesis": AnalyticalModuleSpec(
        module_id="11_cross_module_synthesis",
        source_tables=(
            "claim_inventory.csv",
            "robustness_summary.csv",
            "fdr_adjusted_inference.csv",
            "local_window_correlation_distribution.csv",
            "provider_data_disposition.csv",
        ),
        source_figures=(),
        method_summary="Cross-module evidence is assembled by claim, source artifact, sample, method, uncertainty, measurement risk, endogeneity risk, evidence grade, and limitation.",
        interpretation="Synthesis compares evidence quality without turning heterogeneous diagnostics into one score.",
        limitations="The synthesis inherits upstream module coverage, timing, and measurement limitations.",
        finding_builder=_synthesis_findings,
        extra_tables_builder=_synthesis_extra_tables,
        extra_figures_builder=_synthesis_evidence_figure,
    ),
}
