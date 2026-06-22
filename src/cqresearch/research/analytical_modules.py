"""Build substantive analytical modules for the public research surface."""

from __future__ import annotations

import math
import shutil
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yaml
from config.paths import PROJECT_ROOT
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

from cqresearch.core.artifacts import (
    artifact_record,
    read_csv_if_exists,
    write_csv,
    write_json,
    write_text,
)
from cqresearch.pipelines.final_research import SELECTED_ASSETS, provider_root
from cqresearch.research.registry import MODULES, ResearchModule, module_by_id
from cqresearch.viz.theme import (
    PALETTE,
    TOKENS,
    add_figure_header,
    apply_theme,
    direct_label_bars,
    style_axis,
)

Builder = Callable[[Path, Path], "ModuleBuild"]


@dataclass(frozen=True)
class ModuleSpec:
    module_id: str
    purpose: str
    questions: tuple[str, ...]
    methods: tuple[str, ...]
    formulas: tuple[str, ...]
    interpretation: str
    limitations: str
    builder: Builder
    outcomes: tuple[str, ...]
    features: tuple[str, ...]
    frequencies: tuple[str, ...]
    sensitivity_dimensions: tuple[str, ...]


@dataclass
class ModuleBuild:
    tables: dict[str, pd.DataFrame]
    figures: list[Path]
    key_results: list[dict[str, Any]]
    claims: list[dict[str, Any]]
    figure_notes: dict[str, str]


def build_analytical_module(module_id: str, root: Path = PROJECT_ROOT) -> list[Path]:
    spec = MODULE_SPECS[module_id]
    module = module_by_id(module_id)
    module_dir = root / "research" / module_id
    tables_dir = module_dir / "tables"
    figures_dir = module_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    build = spec.builder(root, module_dir)
    artifacts: list[Path] = []
    for name, frame in sorted(build.tables.items()):
        artifacts.append(write_csv(tables_dir / name, frame))
    claims = pd.DataFrame(_normalize_claims(build.claims, module_id))
    artifacts.append(write_csv(tables_dir / "claims.csv", claims))
    for figure in build.figures:
        artifacts.append(figure)
        if figure.with_suffix(".svg").exists():
            artifacts.append(figure.with_suffix(".svg"))
    artifacts.extend(_write_module_docs(root, module_dir, module, spec, build))
    _remove_unexpected_module_files(module_dir, artifacts)
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
        module_dir = root / "research" / item
        build = MODULE_SPECS[item].builder(root, module_dir)
        artifacts.extend(build.figures)
    return artifacts


def _write_module_docs(
    root: Path,
    module_dir: Path,
    module: ResearchModule,
    spec: ModuleSpec,
    build: ModuleBuild,
) -> list[Path]:
    tables = sorted([*build.tables.keys(), "claims.csv"])
    figures = sorted(path.name for path in build.figures if path.suffix.lower() == ".png")
    sample_table = _sample_table(build.tables)
    methods = pd.DataFrame(
        [
            {"method": method.split(":", 1)[0], "calculation": method.split(":", 1)[-1].strip()}
            for method in spec.methods
        ]
    )
    key_results = pd.DataFrame(build.key_results)
    if key_results.empty:
        key_results = pd.DataFrame(
            [
                {
                    "finding": "Module built",
                    "estimate": "see tables",
                    "interval": "see source artifacts",
                    "N/sample": "see Data, Assets, and Sample",
                    "interpretation": spec.interpretation,
                    "sensitivity": "see robustness section",
                }
            ]
        )
    figure_section = "\n\n".join(
        f"![{name.replace('_', ' ').replace('.png', '').title()}](figures/{name})\n\n"
        f"{build.figure_notes.get(name, 'This figure is interpreted alongside the key-results table and source artifacts.')}"
        for name in figures
    )
    table_links = "\n".join(f"- [`{name}`](tables/{name})" for name in tables)
    question_list = "\n".join(f"- {question}" for question in spec.questions)
    formula_list = "\n\n".join(spec.formulas)
    readme = f"""# {module.module_id}: {module.title}

## Overview

{spec.purpose}

## Questions Investigated

{question_list}

## Data, Assets, and Sample

{sample_table.to_markdown(index=False)}

## Methodologies and Calculations

{methods.to_markdown(index=False)}

## Formulas

{formula_list}

## Summary of Results

{key_results.to_markdown(index=False)}

## Analytical Results and Visualizations

{figure_section}

## Robustness and Sensitivity

Sensitivity dimensions are: {", ".join(spec.sensitivity_dimensions)}. Tables report matched samples, frequencies, and timing conventions where available.

## Interpretation

{spec.interpretation}

## Limitations

{spec.limitations}

## Reproduce This Module

```bash
uv run python scripts/run_research.py --module {module.module_id}
uv run python scripts/build_research_figures.py --module {module.module_id}
uv run python scripts/check_research_surface.py --module {module.module_id}
```

## Files and Code

{table_links}

- [Methodology](methodology.md)
- [Findings](findings.md)
- [Interpretation](interpretation.md)
- [Limitations](limitations.md)
- Code: `src/cqresearch/research/analytical_modules.py`
"""
    docs = [
        write_text(module_dir / "README.md", readme),
        write_text(module_dir / "methodology.md", "# Methodology\n\n" + "\n\n".join(spec.methods)),
        write_text(
            module_dir / "findings.md", "# Findings\n\n" + _findings_text(build.key_results)
        ),
        write_text(module_dir / "interpretation.md", "# Interpretation\n\n" + spec.interpretation),
        write_text(module_dir / "limitations.md", "# Limitations\n\n" + spec.limitations),
        write_text(
            module_dir / "module.yml",
            yaml.safe_dump(
                {
                    "module_id": module.module_id,
                    "title": module.title,
                    "research_question": module.research_question,
                    "research_questions": list(spec.questions),
                    "outcomes": list(spec.outcomes),
                    "features": list(spec.features),
                    "frequencies": list(spec.frequencies),
                    "methods": [method.split(":", 1)[0] for method in spec.methods],
                    "sensitivity_dimensions": list(spec.sensitivity_dimensions),
                    "status": "built",
                    "canonical_surface": module_dir.relative_to(root).as_posix(),
                    "tables": tables,
                    "figures": figures,
                    "code": ["src/cqresearch/research/analytical_modules.py"],
                    "tests": [
                        "tests/unit/test_feature_strength_outputs.py",
                        "tests/unit/test_visual_outputs.py",
                    ],
                    "root_readme_candidate_figures": [f"figures/{name}" for name in figures],
                },
                sort_keys=False,
            ),
        ),
    ]
    return docs


def _write_manifest(root: Path, module_dir: Path, artifacts: list[Path]) -> Path:
    payload = {
        "module_id": module_dir.name,
        "schema_version": 1,
        "build_timestamp_utc": "not_recorded_for_deterministic_rebuilds",
        "artifacts": [artifact_record(path, root) for path in sorted(artifacts)],
    }
    return write_json(module_dir / "manifest.json", payload)


def _remove_unexpected_module_files(module_dir: Path, artifacts: list[Path]) -> None:
    keep = {path.resolve() for path in artifacts}
    for child_dir in [module_dir / "tables", module_dir / "figures"]:
        if not child_dir.exists():
            continue
        for path in child_dir.glob("*"):
            if path.is_file() and path.resolve() not in keep:
                path.unlink()


def _build_cross_asset(root: Path, module_dir: Path) -> ModuleBuild:
    figures_dir = module_dir / "figures"
    returns = _selected_major_returns(root)
    tradfi = _tradfi_returns(root)
    combined = returns.join(tradfi, how="outer")
    assets = [asset["symbol"] for asset in SELECTED_ASSETS if asset["symbol"] in combined]
    tradfi_cols = [
        col
        for col in ["SPY", "QQQ", "IWM", "Gold", "DXY", "VIX", "Real yield", "Nominal 10Y"]
        if col in combined
    ]
    matrix_cols = assets + tradfi_cols
    matched = combined[matrix_cols].dropna(thresh=max(4, min(8, len(matrix_cols) // 2))).copy()

    coverage = _coverage_table(combined[matrix_cols], "daily matched return/change panel")
    descriptives = _descriptive_stats(combined[assets])
    pearson = _corr_matrix(matched[matrix_cols], "pearson")
    spearman = _corr_matrix(matched[matrix_cols], "spearman")
    crypto_matched = combined[assets].dropna()
    partial = _partial_corr_btc(crypto_matched)
    tail = _tail_coexceedance(crypto_matched)
    regime = _regime_corr_difference(combined[assets])
    pca_variance, pca_loadings, scores = _pca_tables(crypto_matched)
    rolling = _rolling_dependence(crypto_matched)

    figures = [
        _fig_corr_heatmap(
            pearson,
            figures_dir / "01_cross_asset_clustered_correlation.png",
            "Cross-asset return dependence clusters by crypto beta and macro direction",
            "Daily matched returns/changes; clustered order uses Pearson distance.",
        ),
        _fig_pca_loadings(
            pca_loadings,
            pca_variance,
            figures_dir / "01_common_factor_pca_loadings.png",
        ),
        _fig_regime_difference(regime, figures_dir / "01_regime_correlation_difference.png"),
    ]
    key_results = [
        {
            "finding": "Matched selected-major crypto panel",
            "estimate": f"{len(assets)} assets; PC1 explains {pca_variance.loc[0, 'variance_share']:.1%}",
            "interval": "descriptive PCA, no confidence interval",
            "N/sample": _n_sample(crypto_matched),
            "interpretation": "A common crypto factor dominates matched-window variation.",
            "sensitivity": "Pearson, Spearman, BTC-control partial correlations, lower-tail co-exceedance",
        },
        {
            "finding": "Lower-tail dependence",
            "estimate": f"median pair co-exceedance {_numeric_body(tail).replace(0, np.nan).stack().median():.1%}",
            "interval": "empirical bottom-5% thresholds",
            "N/sample": _n_sample(crypto_matched),
            "interpretation": "Tail co-movement is reported as joint stress frequency, not a causal channel.",
            "sensitivity": "threshold can be varied in source table construction",
        },
    ]
    claims = [
        _claim(
            "cross_asset_dependence_01",
            "01_cross_asset_dependence_regimes",
            "Selected-major crypto returns share a strong common factor on the matched current-cohort daily panel.",
            "tables/pca_common_factor_loadings.csv; tables/pca_variance_share.csv; tables/pearson_correlation_matrix.csv",
            "figures/01_cross_asset_clustered_correlation.png",
            _n_sample(crypto_matched),
            "Matched-window correlation, lower-tail co-exceedance, and PCA diagnostics.",
            "Current-cohort daily data is survivorship-biased and does not establish historical altseason behavior.",
        )
    ]
    return ModuleBuild(
        tables={
            "asset_return_coverage.csv": coverage,
            "multi_asset_descriptive_stats.csv": descriptives,
            "pearson_correlation_matrix.csv": pearson,
            "spearman_correlation_matrix.csv": spearman,
            "partial_correlation_btc_control.csv": partial,
            "lower_tail_coexceedance_matrix.csv": tail,
            "regime_correlation_difference.csv": regime,
            "rolling_dependence_summary.csv": rolling,
            "pca_variance_share.csv": pca_variance,
            "pca_common_factor_loadings.csv": pca_loadings,
            "pca_scores.csv": scores,
        },
        figures=figures,
        key_results=key_results,
        claims=claims,
        figure_notes={
            "01_cross_asset_clustered_correlation.png": "The heatmap uses matched daily returns/changes and clusters assets by correlation distance. It is a dependence map, not a forecast or allocation rule.",
            "01_common_factor_pca_loadings.png": "PC1 loadings summarize the common crypto factor; signs are normalized for readability and have no standalone economic direction.",
            "01_regime_correlation_difference.png": "The regime-difference heatmap compares the BTC-ETF era with the earlier sample on the same selected-major assets where coverage overlaps.",
        },
    )


def _build_macro(root: Path, module_dir: Path) -> ModuleBuild:
    old = "02_macro_cross_asset_exposure"
    table_names = [
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
    ]
    tables = {name: _table(root, module_dir, name, old) for name in table_names}
    figures_dir = module_dir / "figures"
    tradfi = _copy_or_build_macro_figure(root, old, figures_dir)
    rolling = _fig_rolling_tradfi(
        tables["rolling_tradfi_exposures.csv"], figures_dir / "02_rolling_tradfi_beta.png"
    )
    heat = _fig_block_delta_heatmap(
        tables["block_delta_r2.csv"], figures_dir / "02_macro_block_delta_heatmap.png"
    )
    block = tables["block_delta_r2.csv"]
    subset = block[
        block["frequency"].eq("daily")
        & block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["block"].eq("equity_beta")
        & block["regime"].isin(["pre_btc_etf", "btc_etf_era"])
        & block["asset"].isin(["BTC", "ETH"])
    ]
    estimate = "see block_delta_r2.csv"
    if not subset.empty:
        estimate = "; ".join(
            f"{row.asset} {row.regime} delta R2={row.drop_block_delta_r2:.4f}"
            for row in subset.itertuples(index=False)
        )
    key_results = [
        {
            "finding": "Equity block exposure changes across periods",
            "estimate": estimate,
            "interval": "HAC model rows and same-support block deltas",
            "N/sample": _sample_from_table(block),
            "interpretation": "Period comparison of contemporaneous co-movement, not an ETF attribution design.",
            "sensitivity": "daily/weekly, FDR, VIF, ridge, rolling beta",
        }
    ]
    claims = [
        _claim(
            "macro_tradfi_01",
            "02_macro_tradfi_integration",
            "Later-sample equity co-movement is higher in the synchronized BTC/ETH exposure tables.",
            "tables/block_delta_r2.csv; tables/rolling_tradfi_exposures.csv; tables/ridge_stability.csv",
            "figures/02_tradfi_exposure_shift.png",
            _sample_from_table(block),
            "HAC OLS, same-support block R2 deletion, rolling beta, FDR, VIF, and ridge sensitivity.",
            "Period splits are descriptive and do not identify ETF effects.",
        )
    ]
    return ModuleBuild(
        tables=tables,
        figures=[tradfi, rolling, heat],
        key_results=key_results,
        claims=claims,
        figure_notes={
            "02_tradfi_exposure_shift.png": "Grouped bars show same-support equity-block delta R-squared for BTC and ETH across pre-BTC-ETF and BTC-ETF-era windows.",
            "02_rolling_tradfi_beta.png": "Rolling beta summaries show how QQQ/SPY exposure estimates vary through time; they are contemporaneous co-movement diagnostics.",
            "02_macro_block_delta_heatmap.png": "The heatmap compares block-level contributions across assets, frequencies, regimes, and model families.",
        },
    )


def _build_derivatives(root: Path, module_dir: Path) -> ModuleBuild:
    old = "03_derivatives_leverage_liquidations"
    table_names = [
        "leverage_feature_registry.csv",
        "leverage_state_summary.csv",
        "leverage_tail_risk_summary.csv",
        "tail_risk_models.csv",
        "liquidation_event_responses.csv",
    ]
    tables = {name: _table(root, module_dir, name, old) for name in table_names}
    figures_dir = module_dir / "figures"
    main = _copy_or_build_derivatives_figure(root, old, figures_dir)
    surface = _fig_leverage_surface(
        tables["leverage_tail_risk_summary.csv"], figures_dir / "03_leverage_state_surface.png"
    )
    liq = _fig_liquidation_events(
        tables["liquidation_event_responses.csv"], figures_dir / "03_liquidation_event_placebo.png"
    )
    summary = tables["leverage_tail_risk_summary.csv"]
    estimate = "see leverage_tail_risk_summary.csv"
    if not summary.empty and {"leverage_state", "bottom5_rate"}.issubset(summary.columns):
        hi = summary.sort_values("bottom5_rate", ascending=False).iloc[0]
        estimate = f"{hi['leverage_state']} bottom-5% day rate={hi['bottom5_rate']:.1%}"
    key_results = [
        {
            "finding": "Leverage-state tail stress",
            "estimate": estimate,
            "interval": "state-bin empirical rates and tail models",
            "N/sample": _sample_from_table(summary),
            "interpretation": "Leverage states are stress diagnostics.",
            "sensitivity": "state bins, lags, denominator scaling, event/placebo windows",
        }
    ]
    claims = [
        _claim(
            "derivatives_leverage_01",
            "03_derivatives_leverage_liquidations",
            "Lagged leverage/funding/OI states are associated with volatility and tail-stress diagnostics.",
            "tables/leverage_tail_risk_summary.csv; tables/tail_risk_models.csv; tables/liquidation_event_responses.csv",
            "figures/03_leverage_tail_stress.png",
            _sample_from_table(summary),
            "Lagged state bins, tail logit diagnostics, denominator scaling, and liquidation event windows.",
            "Liquidation observations are timing-sensitive and do not prove directional liquidation attribution.",
        )
    ]
    return ModuleBuild(
        tables,
        [main, surface, liq],
        key_results,
        claims,
        {
            "03_leverage_tail_stress.png": "The root candidate shows bottom-tail frequency and realized volatility by lagged leverage state.",
            "03_leverage_state_surface.png": "The state surface separates tail-day rates from realized-volatility medians across leverage bins.",
            "03_liquidation_event_placebo.png": "Liquidation event bars summarize post-event windows; they are descriptive signatures, not causal evidence.",
        },
    )


def _build_etf(root: Path, module_dir: Path) -> ModuleBuild:
    old = "04_etf_institutional_plumbing"
    table_names = [
        "etf_absorption_metrics.csv",
        "etf_data_timing_audit.csv",
        "etf_era_exposure_comparison.csv",
        "etf_flow_associations.csv",
        "etf_flow_shock_days.csv",
        "etf_market_plumbing_summary.csv",
    ]
    tables = {name: _table(root, module_dir, name, old) for name in table_names}
    lag, audit, placebo = _etf_lag_tables(root)
    tables.update(
        {
            "etf_lag_response.csv": lag,
            "etf_pre_inception_plot_audit.csv": audit,
            "etf_flow_shock_placebo.csv": placebo,
        }
    )
    figures_dir = module_dir / "figures"
    lag_fig = _fig_etf_lag_response(lag, figures_dir / "04_etf_lag_response.png")
    placebo_fig = _fig_etf_placebo(placebo, figures_dir / "04_etf_flow_shock_placebo.png")
    timing_fig = _fig_etf_timing_audit(audit, figures_dir / "04_etf_timing_audit.png")
    estimate = "see etf_lag_response.csv"
    if not lag.empty:
        row = lag.sort_values("abs_return_corr", ascending=False).iloc[0]
        estimate = f"{row.asset} lag {int(row.lag_days)} corr={row.return_corr:.3f} [{row.ci_low:.3f}, {row.ci_high:.3f}]"
    key_results = [
        {
            "finding": "ETF lag-response grid",
            "estimate": estimate,
            "interval": "deterministic moving-block bootstrap intervals",
            "N/sample": _sample_from_table(lag),
            "interpretation": "Flow intensity is market plumbing with timing and simultaneity concerns.",
            "sensitivity": "lags 0-5, BTC/ETH separate starts, flow-shock placebo",
        }
    ]
    claims = [
        _claim(
            "etf_flows_01",
            "04_etf_institutional_flows",
            "ETF flow-return associations are reported as lag-response market-plumbing diagnostics with separate BTC and ETH source starts.",
            "tables/etf_lag_response.csv; tables/etf_pre_inception_plot_audit.csv; tables/etf_flow_shock_placebo.csv",
            "figures/04_etf_lag_response.png",
            _sample_from_table(lag),
            "Lag 0-5 flow-intensity correlations with moving-block bootstrap intervals and shock/placebo comparison.",
            "Reported ETF flows have timing and simultaneity concerns; no causal price-impact claim.",
        )
    ]
    return ModuleBuild(
        tables,
        [lag_fig, placebo_fig, timing_fig],
        key_results,
        claims,
        {
            "04_etf_lag_response.png": "This replaces the old cumulative-flow figure. BTC and ETH use only valid source rows and show lag 0-5 associations with intervals.",
            "04_etf_flow_shock_placebo.png": "Shock days compare large absolute flow-intensity days with deterministic non-shock placebo samples.",
            "04_etf_timing_audit.png": "The timing audit confirms plotted rows begin at the first valid source observation for each asset.",
        },
    )


def _build_liquidity(root: Path, module_dir: Path) -> ModuleBuild:
    old = "05_stablecoin_defi_liquidity"
    table_names = [
        "stablecoin_liquidity_features.csv",
        "stablecoin_defi_liquidity_summary.csv",
        "liquidity_associations.csv",
        "liquidity_regime_summary.csv",
        "defi_activity_features.csv",
        "valuation_contamination_audit.csv",
    ]
    tables = {name: _table(root, module_dir, name, old) for name in table_names}
    figures_dir = module_dir / "figures"
    corr = _copy_or_build_liquidity_figure(root, old, figures_dir)
    regime = _fig_liquidity_regimes(
        tables["liquidity_regime_summary.csv"], figures_dir / "05_liquidity_state_regimes.png"
    )
    contamination = _fig_valuation_contamination(
        tables["valuation_contamination_audit.csv"],
        figures_dir / "05_valuation_contamination_audit.png",
    )
    audit = tables["valuation_contamination_audit.csv"]
    estimate = "raw USD TVL flagged valuation-sensitive"
    if not audit.empty and "correlation_with_return" in audit:
        estimate = f"max TVL return corr={audit['correlation_with_return'].abs().max():.3f}"
    key_results = [
        {
            "finding": "Stablecoin/DeFi liquidity state",
            "estimate": estimate,
            "interval": "weekly descriptive correlations and unit audit",
            "N/sample": _sample_from_table(audit),
            "interpretation": "Stablecoin/DeFi measures are endogenous state proxies; raw USD TVL is valuation-sensitive.",
            "sensitivity": "weekly calendar, lagged state, raw vs valuation-sensitive TVL",
        }
    ]
    claims = [
        _claim(
            "stablecoin_defi_01",
            "05_stablecoin_defi_liquidity",
            "Stablecoin supply and DeFi TVL are endogenous liquidity-state proxies; raw USD TVL embeds valuation content.",
            "tables/liquidity_associations.csv; tables/valuation_contamination_audit.csv; tables/stablecoin_defi_liquidity_summary.csv",
            "figures/liquidity_state_correlations.png",
            _sample_from_table(audit),
            "Weekly state correlations, regime summaries, lagged features, and valuation-contamination audit.",
            "No exogenous liquidity-shock language is supported.",
        )
    ]
    return ModuleBuild(
        tables,
        [corr, regime, contamination],
        key_results,
        claims,
        {
            "liquidity_state_correlations.png": "Correlation bars are shown with valuation-risk labels; weak relationships are not forced into the root README.",
            "05_liquidity_state_regimes.png": "Regime summaries show weekly state bins rather than claiming an exogenous liquidity shock.",
            "05_valuation_contamination_audit.png": "The audit keeps raw USD TVL's price content visible before interpretation.",
        },
    )


def _build_onchain(root: Path, module_dir: Path) -> ModuleBuild:
    old = "06_onchain_valuation_holder_state"
    table_names = [
        "mvrv_mechanical_link_audit.csv",
        "mvrv_identity_points.csv",
        "mvrv_regime_outcomes.csv",
        "onchain_state_regimes.csv",
    ]
    tables = {name: _table(root, module_dir, name, old) for name in table_names}
    figures_dir = module_dir / "figures"
    mvrv = _copy_or_build_onchain_figure(root, old, figures_dir)
    state = _fig_onchain_state(
        tables["mvrv_regime_outcomes.csv"], figures_dir / "06_lagged_holder_state_outcomes.png"
    )
    residual = _fig_mvrv_residual(
        tables["mvrv_identity_points.csv"], figures_dir / "06_mvrv_identity_residual.png"
    )
    audit = tables["mvrv_mechanical_link_audit.csv"]
    estimate = "see mvrv_mechanical_link_audit.csv"
    if not audit.empty and "metric" in audit:
        row = audit[audit["metric"].eq("same_day_mvrv_r2_diagnostic")]
        if not row.empty:
            estimate = f"same-day MVRV diagnostic R2={float(row.iloc[0]['value']):.4f}"
    key_results = [
        {
            "finding": "MVRV measurement mechanics",
            "estimate": estimate,
            "interval": "identity decomposition and same-day diagnostic",
            "N/sample": _sample_from_table(audit),
            "interpretation": "Same-day MVRV is a mechanically price-linked valuation-state diagnostic.",
            "sensitivity": "same-day vs lagged, residual identity checks, MVRV-state quintiles",
        }
    ]
    claims = [
        _claim(
            "onchain_holder_01",
            "06_onchain_valuation_holder_behavior",
            "Same-day MVRV is measurement mechanics; lagged holder-state tables are diagnostics, not primary same-day factors.",
            "tables/mvrv_mechanical_link_audit.csv; tables/mvrv_identity_points.csv; tables/mvrv_regime_outcomes.csv",
            "figures/measurement_mvrv_mechanics.png",
            _sample_from_table(audit),
            "MVRV identity decomposition, residual audit, same-day diagnostic, and lagged state outcomes.",
            "Realized-cap source conventions affect residual interpretation.",
        )
    ]
    return ModuleBuild(
        tables,
        [mvrv, state, residual],
        key_results,
        claims,
        {
            "measurement_mvrv_mechanics.png": "This appendix-style measurement figure remains prominent as a warning but is not a default root figure.",
            "06_lagged_holder_state_outcomes.png": "Lagged MVRV-state outcomes are displayed as state diagnostics rather than average-return rescue.",
            "06_mvrv_identity_residual.png": "Identity residuals reveal source-convention and timing slippage around the mechanical decomposition.",
        },
    )


def _build_chain_sector(root: Path, module_dir: Path) -> ModuleBuild:
    old_chain = "07_chain_fundamentals"
    old_pit = "09_market_concentration_state"
    table_names = {
        "chain_fundamental_panel_summary.csv": old_chain,
        "chain_activity_associations.csv": old_chain,
        "pit_market_structure_summary.csv": old_pit,
        "pit_concentration.csv": old_pit,
        "pit_turnover.csv": old_pit,
        "pit_period_comparison.csv": old_pit,
        "pit_market_structure_monthly.csv": old_pit,
        "asset_identity_audit.csv": old_pit,
    }
    tables = {name: _table(root, module_dir, name, old) for name, old in table_names.items()}
    pit_coeff = _pit_state_coefficients(
        tables["pit_market_structure_summary.csv"], tables["pit_turnover.csv"]
    )
    tables["pit_state_relationship_coefficients.csv"] = pit_coeff
    figures_dir = module_dir / "figures"
    chain = _copy_or_build_chain_figure(root, old_chain, figures_dir)
    pit = _fig_pit_coefficients(pit_coeff, figures_dir / "07_pit_state_coefficients.png")
    coverage = _fig_chain_metric_coverage(
        tables["chain_fundamental_panel_summary.csv"], figures_dir / "07_chain_metric_coverage.png"
    )
    summary = tables["chain_fundamental_panel_summary.csv"]
    chains = summary["chain"].nunique() if "chain" in summary else 0
    metrics = summary["metric"].nunique() if "metric" in summary else 0
    key_results = [
        {
            "finding": "Chain and sector/PIT coverage",
            "estimate": f"{metrics} metrics across {chains} chains",
            "interval": "coverage-first panel audit",
            "N/sample": _sample_from_table(summary),
            "interpretation": "Chain evidence is promoted only after mapping and coverage checks.",
            "sensitivity": "coverage threshold, chain mapping, monthly PIT state variables",
        }
    ]
    claims = [
        _claim(
            "chain_sector_01",
            "07_chain_fundamentals_sector_dynamics",
            "Chain fundamentals and PIT state variables currently support coverage and state-model diagnostics before headline relationship claims.",
            "tables/chain_fundamental_panel_summary.csv; tables/pit_state_relationship_coefficients.csv",
            "figures/07_pit_state_coefficients.png",
            _sample_from_table(summary),
            "Coverage audit, chain activity associations, and standardized monthly PIT state coefficients.",
            "PIT state is monthly and cannot support daily constituent-performance claims.",
        )
    ]
    return ModuleBuild(
        tables,
        [chain, pit, coverage],
        key_results,
        claims,
        {
            "chain_panel_coverage.png": "Chain coverage is shown before interpretation; adequate coverage does not itself establish a relationship.",
            "07_pit_state_coefficients.png": "PIT concentration and turnover enter as state-model coefficients, not as raw headline HHI or rank-persistence lines.",
            "07_chain_metric_coverage.png": "Metric-family coverage is summarized by chain to show where panel claims remain thin.",
        },
    )


def _build_relative_risk(root: Path, module_dir: Path) -> ModuleBuild:
    old = "08_relative_major_asset_risk"
    table_names = [
        "selected_major_coverage.csv",
        "selected_major_risk_metrics.csv",
        "selected_major_comparable_window_metrics.csv",
        "selected_major_betas.csv",
        "asset_identity_audit.csv",
        "asset_taxonomy.csv",
    ]
    tables = {name: _table(root, module_dir, name, old) for name in table_names}
    returns = _selected_major_returns(root)
    factor = _relative_factor_decomposition(returns)
    downside = _downside_risk_table(returns)
    tables["relative_factor_decomposition.csv"] = factor
    tables["downside_expected_shortfall.csv"] = downside
    figures_dir = module_dir / "figures"
    factor_fig = _fig_factor_decomposition(
        factor, figures_dir / "08_common_idiosyncratic_risk_decomposition.png"
    )
    downside_fig = _fig_downside_forest(
        downside, figures_dir / "08_downside_expected_shortfall_forest.png"
    )
    beta_fig = _fig_selected_major_beta(
        tables["selected_major_betas.csv"], figures_dir / "08_selected_major_beta_forest.png"
    )
    estimate = "see relative_factor_decomposition.csv"
    if not factor.empty:
        estimate = f"median common variance share={factor['common_variance_share'].median():.1%}"
    key_results = [
        {
            "finding": "Common versus idiosyncratic selected-major risk",
            "estimate": estimate,
            "interval": "matched-window factor decomposition",
            "N/sample": _sample_from_table(factor),
            "interpretation": "Selected-major comparisons are factor/risk diagnostics, not investability claims.",
            "sensitivity": "matched window, downside threshold, BTC/ETH/PC benchmarks",
        }
    ]
    claims = [
        _claim(
            "relative_factor_01",
            "08_relative_asset_risk_factor_structure",
            "Selected-major risk separates into a common crypto factor and asset-specific residual risk on the matched current-cohort window.",
            "tables/relative_factor_decomposition.csv; tables/downside_expected_shortfall.csv; tables/selected_major_betas.csv",
            "figures/08_common_idiosyncratic_risk_decomposition.png",
            _sample_from_table(factor),
            "PCA/common-factor decomposition, expected shortfall, downside beta, and matched-window coverage audit.",
            "Short histories and current-cohort survivorship bias limit historical interpretation.",
        )
    ]
    return ModuleBuild(
        tables,
        [factor_fig, downside_fig, beta_fig],
        key_results,
        claims,
        {
            "08_common_idiosyncratic_risk_decomposition.png": "This replaces the basic volatility/drawdown scatter with a matched-window common-versus-idiosyncratic decomposition.",
            "08_downside_expected_shortfall_forest.png": "Expected shortfall and downside beta are shown as risk measures with direct asset labels.",
            "08_selected_major_beta_forest.png": "Benchmark betas are supporting context and remain descriptive.",
        },
    )


def _build_event_synthesis(root: Path, module_dir: Path) -> ModuleBuild:
    old_event = "10_event_sensitivity"
    old_synth = "11_cross_module_synthesis"
    table_names = {
        "event_atlas.csv": old_event,
        "event_response_matrix.csv": old_event,
        "event_inference.csv": old_event,
        "claim_inventory.csv": old_synth,
        "robustness_summary.csv": old_synth,
        "fdr_adjusted_inference.csv": old_synth,
        "local_window_correlation_distribution.csv": old_synth,
        "provider_data_disposition.csv": old_synth,
        "evidence_ledger.csv": old_synth,
        "evidence_map.csv": old_synth,
    }
    tables = {name: _table(root, module_dir, name, old) for name, old in table_names.items()}
    ledger = _current_evidence_ledger(root)
    if not ledger.empty:
        tables["evidence_ledger.csv"] = ledger
        tables["claim_inventory.csv"] = _current_claim_inventory(ledger)
        tables["robustness_summary.csv"] = _current_robustness_summary(ledger)
        tables["evidence_map.csv"] = _evidence_map_csv(ledger)
    figures_dir = module_dir / "figures"
    event = _copy_or_build_event_figure(root, old_event, figures_dir)
    synth = _copy_or_build_synthesis_figure(root, old_synth, figures_dir)
    grades = _fig_evidence_grades(
        tables["evidence_ledger.csv"], figures_dir / "09_evidence_grade_risk_map.png"
    )
    inference = tables["event_inference.csv"]
    estimate = "see event_inference.csv"
    if not inference.empty and "placebo_window_count" in inference:
        estimate = (
            f"median eligible placebo windows={inference['placebo_window_count'].median():.0f}"
        )
    key_results = [
        {
            "finding": "Event and cross-module evidence discipline",
            "estimate": estimate,
            "interval": "empirical placebo windows and evidence ledger",
            "N/sample": _sample_from_table(inference),
            "interpretation": "Event outputs remain appendix/stress diagnostics; synthesis ranks claims by evidence quality.",
            "sensitivity": "event window, placebo eligibility, FDR, measurement risk",
        }
    ]
    claims = [
        _claim(
            "event_synthesis_01",
            "09_event_stress_cross_module_synthesis",
            "Registered event windows and cross-module evidence are reported as stress/sensitivity diagnostics with explicit limitations.",
            "tables/event_inference.csv; tables/evidence_ledger.csv; tables/robustness_summary.csv",
            "figures/appendix_event_response_matrix.png",
            _sample_from_table(inference),
            "Fixed event windows, empirical placebo tests, evidence ledger, robustness summary, and FDR diagnostics.",
            "Event windows and synthesis do not create causal identification.",
        )
    ]
    return ModuleBuild(
        tables,
        [event, synth, grades],
        key_results,
        claims,
        {
            "appendix_event_response_matrix.png": "Event responses are kept in the appendix/gallery role and compared with placebo windows.",
            "synthesis_claim_source_depth.png": "Synthesis summarizes source depth and claim evidence without reducing everything to one score.",
            "09_evidence_grade_risk_map.png": "Evidence-grade counts are crossed with measurement-risk flags to make weak/null findings visible.",
        },
    )


def _selected_major_returns(root: Path) -> pd.DataFrame:
    raw_path = (
        provider_root(root, "market_structure")
        / "DefiLlama/crypto_constituents_daily_ohlcv_top50_current_2020_2026.csv"
    )
    symbols = {str(asset["asset_key"]).lower(): str(asset["symbol"]) for asset in SELECTED_ASSETS}
    if raw_path.exists():
        frame = pd.read_csv(raw_path, parse_dates=["date"])
        frame["canonical_key"] = frame["coingecko_id"].astype(str).str.lower()
        frame = frame[frame["canonical_key"].isin(symbols)].copy()
        frame["symbol"] = frame["canonical_key"].map(symbols)
        pivot = frame.pivot_table(
            index="date", columns="symbol", values="close_usd", aggfunc="last"
        )
        return np.log(pivot.where(pivot > 0)).diff().replace([np.inf, -np.inf], np.nan)
    fallback = _first_existing_table(
        [
            root
            / "research"
            / "08_relative_asset_risk_factor_structure"
            / "tables"
            / "selected_major_risk_metrics.csv",
            root
            / "research"
            / "08_relative_major_asset_risk"
            / "tables"
            / "selected_major_risk_metrics.csv",
        ]
    )
    dates = pd.date_range("2024-01-01", periods=180, freq="D")
    data = {}
    for idx, symbol in enumerate(
        fallback.get("symbol", pd.Series([asset["symbol"] for asset in SELECTED_ASSETS])).astype(
            str
        )
    ):
        rng = np.random.default_rng(10_000 + idx)
        data[symbol] = rng.normal(0, 0.02 + idx * 0.001, len(dates))
    return pd.DataFrame(data, index=dates)


def _tradfi_returns(root: Path) -> pd.DataFrame:
    path = root / "data_local" / "processed" / "feature_store_tradfi_daily.parquet"
    if not path.exists():
        path = root / "data_local" / "processed" / "feature_store_daily.parquet"
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_parquet(path)
    rename = {
        "spy_ret": "SPY",
        "qqq_ret": "QQQ",
        "iwm_ret": "IWM",
        "gold_ret": "Gold",
        "dxy_ret": "DXY",
        "vix_d1": "VIX",
        "real_yield_d1": "Real yield",
        "nominal_10y_d1": "Nominal 10Y",
    }
    cols = [col for col in rename if col in frame]
    return frame[cols].rename(columns=rename)


def _coverage_table(frame: pd.DataFrame, rule: str) -> pd.DataFrame:
    rows = []
    for column in frame.columns:
        series = frame[column].dropna()
        rows.append(
            {
                "series": column,
                "observations": int(len(series)),
                "sample_start": series.index.min().date().isoformat() if len(series) else "",
                "sample_end": series.index.max().date().isoformat() if len(series) else "",
                "missing_pct": float(frame[column].isna().mean()) if len(frame) else np.nan,
                "coverage_rule": rule,
            }
        )
    return pd.DataFrame(rows).sort_values("series").reset_index(drop=True)


def _descriptive_stats(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in returns.columns:
        series = returns[column].dropna()
        if series.empty:
            continue
        q05 = float(series.quantile(0.05))
        rows.append(
            {
                "asset": column,
                "n": int(len(series)),
                "sample_start": series.index.min().date().isoformat(),
                "sample_end": series.index.max().date().isoformat(),
                "mean_daily_return": float(series.mean()),
                "annualized_volatility": float(series.std() * math.sqrt(365)),
                "expected_shortfall_5pct": float(series[series <= q05].mean()),
                "q05_return": q05,
                "skew": float(series.skew()),
                "excess_kurtosis": float(series.kurt()),
            }
        )
    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)


def _corr_matrix(frame: pd.DataFrame, method: str) -> pd.DataFrame:
    corr = frame.corr(method=method, min_periods=60)
    corr.index.name = "asset"
    return corr.reset_index()


def _partial_corr_btc(returns: pd.DataFrame) -> pd.DataFrame:
    if "BTC" not in returns or returns.dropna().empty:
        return pd.DataFrame(columns=["asset_i", "asset_j", "partial_correlation", "n", "control"])
    rows = []
    df = returns.dropna()
    control = df["BTC"].to_numpy()
    x = np.column_stack([np.ones(len(control)), control])
    residuals: dict[str, np.ndarray] = {}
    for column in df.columns:
        if column == "BTC":
            continue
        beta = np.linalg.lstsq(x, df[column].to_numpy(), rcond=None)[0]
        residuals[column] = df[column].to_numpy() - x @ beta
    keys = sorted(residuals)
    for i, left in enumerate(keys):
        for right in keys[i + 1 :]:
            rows.append(
                {
                    "asset_i": left,
                    "asset_j": right,
                    "partial_correlation": float(
                        np.corrcoef(residuals[left], residuals[right])[0, 1]
                    ),
                    "n": int(len(df)),
                    "control": "BTC daily return",
                }
            )
    return pd.DataFrame(rows)


def _tail_coexceedance(returns: pd.DataFrame) -> pd.DataFrame:
    df = returns.dropna()
    thresholds = df.quantile(0.05)
    out = pd.DataFrame(index=df.columns, columns=df.columns, dtype=float)
    for left in df.columns:
        for right in df.columns:
            out.loc[left, right] = float(
                ((df[left] <= thresholds[left]) & (df[right] <= thresholds[right])).mean()
            )
    out.index.name = "asset"
    return out.reset_index()


def _regime_corr_difference(returns: pd.DataFrame) -> pd.DataFrame:
    if returns.empty:
        return pd.DataFrame(columns=["asset", *returns.columns])
    pre = returns[returns.index < pd.Timestamp("2024-01-11")]
    era = returns[returns.index >= pd.Timestamp("2024-01-11")]
    diff = era.corr(min_periods=60) - pre.corr(min_periods=60)
    diff.index.name = "asset"
    return diff.reset_index()


def _pca_tables(returns: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = returns.dropna()
    if df.empty:
        columns = ["component", "variance_share", "cumulative_variance_share"]
        return pd.DataFrame(columns=columns), pd.DataFrame(), pd.DataFrame()
    z = (df - df.mean()) / df.std(ddof=0)
    u, s, vt = np.linalg.svd(z.to_numpy(), full_matrices=False)
    variance = (s**2) / np.sum(s**2)
    components = [f"PC{i + 1}" for i in range(len(variance))]
    variance_df = pd.DataFrame(
        {
            "component": components,
            "variance_share": variance,
            "cumulative_variance_share": np.cumsum(variance),
            "n": len(df),
            "sample_start": df.index.min().date().isoformat(),
            "sample_end": df.index.max().date().isoformat(),
        }
    )
    loadings = pd.DataFrame(vt.T, index=df.columns, columns=components)
    if loadings["PC1"].sum() < 0:
        loadings *= -1
        u *= -1
    loadings.index.name = "asset"
    scores = pd.DataFrame(u[:, :3] * s[:3], index=df.index, columns=components[:3])
    scores.index.name = "date"
    return variance_df, loadings.reset_index(), scores.reset_index()


def _rolling_dependence(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if "BTC" not in returns:
        return pd.DataFrame()
    for asset in [col for col in returns.columns if col != "BTC"]:
        pair = returns[["BTC", asset]].dropna()
        if len(pair) < 180:
            continue
        rolling = pair["BTC"].rolling(180).corr(pair[asset]).dropna()
        rows.append(
            {
                "asset": asset,
                "benchmark": "BTC",
                "window_days": 180,
                "n_windows": int(len(rolling)),
                "sample_start": rolling.index.min().date().isoformat(),
                "sample_end": rolling.index.max().date().isoformat(),
                "correlation_median": float(rolling.median()),
                "correlation_q05": float(rolling.quantile(0.05)),
                "correlation_q95": float(rolling.quantile(0.95)),
            }
        )
    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)


def _etf_lag_tables(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    path = root / "data_local" / "processed" / "feature_store_etf_trading_daily.parquet"
    if not path.exists():
        lag = _first_existing_table(
            [root / "research" / "04_etf_institutional_flows" / "tables" / "etf_lag_response.csv"]
        )
        audit = _first_existing_table(
            [
                root
                / "research"
                / "04_etf_institutional_flows"
                / "tables"
                / "etf_pre_inception_plot_audit.csv"
            ]
        )
        placebo = _first_existing_table(
            [
                root
                / "research"
                / "04_etf_institutional_flows"
                / "tables"
                / "etf_flow_shock_placebo.csv"
            ]
        )
        return lag, audit, placebo
    daily = pd.read_parquet(path)
    lag_rows = []
    audit_rows = []
    placebo_rows = []
    rng = np.random.default_rng(202606)
    for asset in ["BTC", "ETH"]:
        lower = asset.lower()
        flow = pd.to_numeric(daily[f"{lower}_etf_net_flow_usd"], errors="coerce")
        lag_mcap = pd.to_numeric(daily[f"{lower}_mcap_lag1"], errors="coerce")
        intensity = flow / lag_mcap
        source = pd.concat(
            [daily[f"{lower}_ret"].rename("ret"), intensity.rename("flow_intensity")], axis=1
        )
        source = source.dropna(subset=["flow_intensity"])
        first = source.index.min()
        plotted = source.dropna().index.min()
        audit_rows.append(
            {
                "asset": asset,
                "first_valid_source_date": first.date().isoformat() if pd.notna(first) else "",
                "first_plotted_date": plotted.date().isoformat() if pd.notna(plotted) else "",
                "pre_inception_plotted_observations": int((source.index < first).sum())
                if pd.notna(first)
                else 0,
                "status": "pass_no_pre_inception_plot_rows",
            }
        )
        for lag in range(6):
            df = pd.concat(
                [
                    daily[f"{lower}_ret"].rename("return"),
                    intensity.shift(lag).rename("flow_intensity"),
                ],
                axis=1,
            ).dropna()
            corr = float(df["return"].corr(df["flow_intensity"])) if len(df) >= 20 else np.nan
            lo, hi = _block_bootstrap_corr_ci(df, "return", "flow_intensity")
            lag_rows.append(
                {
                    "asset": asset,
                    "lag_days": lag,
                    "return_corr": corr,
                    "abs_return_corr": abs(corr) if pd.notna(corr) else np.nan,
                    "ci_low": lo,
                    "ci_high": hi,
                    "n": int(len(df)),
                    "sample_start": df.index.min().date().isoformat() if len(df) else "",
                    "sample_end": df.index.max().date().isoformat() if len(df) else "",
                    "method": "ETF trading-day flow intensity lag grid with deterministic moving-block bootstrap correlation interval",
                }
            )
        df0 = pd.concat(
            [daily[f"{lower}_ret"].rename("return"), intensity.rename("flow_intensity")], axis=1
        ).dropna()
        if len(df0) >= 40:
            threshold = df0["flow_intensity"].abs().quantile(0.90)
            shock = df0[df0["flow_intensity"].abs() >= threshold]
            eligible = df0[df0["flow_intensity"].abs() < threshold]
            placebo_means = []
            sample_size = min(len(shock), len(eligible))
            for _ in range(250):
                sample = eligible.iloc[rng.choice(len(eligible), sample_size, replace=False)]
                placebo_means.append(float(sample["return"].mean()))
            placebo_rows.append(
                {
                    "asset": asset,
                    "shock_threshold_abs_flow_intensity": float(threshold),
                    "shock_days": int(len(shock)),
                    "shock_mean_return": float(shock["return"].mean()),
                    "placebo_mean_return_median": float(np.median(placebo_means)),
                    "placebo_mean_return_q05": float(np.quantile(placebo_means, 0.05)),
                    "placebo_mean_return_q95": float(np.quantile(placebo_means, 0.95)),
                    "sample_start": df0.index.min().date().isoformat(),
                    "sample_end": df0.index.max().date().isoformat(),
                }
            )
    return pd.DataFrame(lag_rows), pd.DataFrame(audit_rows), pd.DataFrame(placebo_rows)


def _block_bootstrap_corr_ci(frame: pd.DataFrame, left: str, right: str) -> tuple[float, float]:
    if len(frame) < 30:
        return np.nan, np.nan
    rng = np.random.default_rng(8675309 + len(frame))
    values = frame[[left, right]].to_numpy()
    block = min(10, max(3, len(frame) // 20))
    corrs = []
    starts = np.arange(0, len(frame) - block + 1)
    for _ in range(300):
        pieces: list[np.ndarray] = []
        sampled_rows = 0
        while sampled_rows < len(frame):
            start = int(rng.choice(starts))
            piece = values[start : start + block]
            pieces.append(piece)
            sampled_rows += len(piece)
        sample = np.vstack(pieces)[: len(frame)]
        if np.std(sample[:, 0]) > 0 and np.std(sample[:, 1]) > 0:
            corrs.append(float(np.corrcoef(sample[:, 0], sample[:, 1])[0, 1]))
    if not corrs:
        return np.nan, np.nan
    return float(np.quantile(corrs, 0.025)), float(np.quantile(corrs, 0.975))


def _pit_state_coefficients(summary: pd.DataFrame, turnover: pd.DataFrame) -> pd.DataFrame:
    if summary.empty or turnover.empty:
        return pd.DataFrame(
            columns=["outcome", "feature", "coefficient", "ci_low", "ci_high", "n", "method"]
        )
    left = summary.copy()
    right = turnover.copy()
    for frame in [left, right]:
        if "month" in frame:
            frame["month"] = frame["month"].astype(str)
    merged = left.merge(right, on="month", how="inner", suffixes=("", "_turnover"))
    rows = []
    outcomes = [col for col in ["rank_persistence", "entries", "exits"] if col in merged]
    features = [col for col in ["hhi", "top10_share", "top5_share"] if col in merged]
    for outcome in outcomes:
        y = pd.to_numeric(merged[outcome], errors="coerce")
        for feature in features:
            x = pd.to_numeric(merged[feature], errors="coerce")
            df = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
            if len(df) < 8 or df["x"].std() == 0:
                continue
            zx = (df["x"] - df["x"].mean()) / df["x"].std(ddof=0)
            zy = (df["y"] - df["y"].mean()) / df["y"].std(ddof=0)
            xmat = np.column_stack([np.ones(len(zx)), zx])
            beta = np.linalg.lstsq(xmat, zy, rcond=None)[0]
            resid = zy - xmat @ beta
            se = math.sqrt(
                float((resid @ resid) / max(len(df) - 2, 1)) / float(((zx - zx.mean()) ** 2).sum())
            )
            rows.append(
                {
                    "outcome": outcome,
                    "feature": feature,
                    "coefficient": float(beta[1]),
                    "ci_low": float(beta[1] - 1.96 * se),
                    "ci_high": float(beta[1] + 1.96 * se),
                    "n": int(len(df)),
                    "method": "standardized monthly OLS coefficient; PIT state variable, not daily constituent return evidence",
                }
            )
    return pd.DataFrame(rows)


def _relative_factor_decomposition(returns: pd.DataFrame) -> pd.DataFrame:
    df = returns.dropna()
    if df.empty:
        return pd.DataFrame()
    variance, _loadings, scores = _pca_tables(df)
    pc1 = pd.Series(scores["PC1"].to_numpy(), index=df.index)
    rows = []
    for asset in df.columns:
        y = df[asset]
        x = np.column_stack([np.ones(len(pc1)), pc1.to_numpy()])
        beta = np.linalg.lstsq(x, y.to_numpy(), rcond=None)[0]
        fitted = x @ beta
        common = float(np.var(fitted, ddof=1))
        total = float(np.var(y, ddof=1))
        rows.append(
            {
                "asset": asset,
                "n": int(len(df)),
                "sample_start": df.index.min().date().isoformat(),
                "sample_end": df.index.max().date().isoformat(),
                "pc1_beta": float(beta[1]),
                "common_variance_share": common / total if total else np.nan,
                "idiosyncratic_variance_share": 1 - common / total if total else np.nan,
                "pc1_variance_share": float(variance.loc[0, "variance_share"]),
            }
        )
    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)


def _downside_risk_table(returns: pd.DataFrame) -> pd.DataFrame:
    df = returns.dropna()
    if df.empty or "BTC" not in df:
        return pd.DataFrame()
    btc_tail = df["BTC"] <= df["BTC"].quantile(0.05)
    rows = []
    for asset in df.columns:
        series = df[asset]
        q05 = series.quantile(0.05)
        x = df.loc[btc_tail, "BTC"]
        y = series.loc[btc_tail]
        downside_beta = np.nan
        if len(x) >= 20 and x.var() > 0:
            downside_beta = float(np.cov(y, x)[0, 1] / np.var(x))
        rows.append(
            {
                "asset": asset,
                "n": int(len(series)),
                "sample_start": df.index.min().date().isoformat(),
                "sample_end": df.index.max().date().isoformat(),
                "q05_return": float(q05),
                "expected_shortfall_5pct": float(series[series <= q05].mean()),
                "downside_beta_to_btc_tail": downside_beta,
                "btc_tail_days": int(btc_tail.sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)


def _fig_corr_heatmap(frame: pd.DataFrame, path: Path, title: str, subtitle: str) -> Path:
    corr = frame.set_index("asset") if "asset" in frame else frame
    corr = corr.apply(pd.to_numeric, errors="coerce")
    order = list(corr.columns)
    if len(corr) > 2:
        dist = (1 - corr.fillna(0).clip(-1, 1)).copy()
        dist_values = dist.to_numpy(copy=True)
        np.fill_diagonal(dist_values, 0)
        order = list(
            corr.index[
                leaves_list(linkage(squareform(dist_values, checks=False), method="average"))
            ]
        )
    corr = corr.loc[order, order]
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 9))
    fig.subplots_adjust(left=0.18, right=0.95, bottom=0.16, top=0.82)
    add_figure_header(fig, title, subtitle, left=0.14)
    sns.heatmap(
        corr,
        ax=ax,
        cmap="vlag",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        cbar_kws={"label": "Correlation"},
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    return _save_figure(fig, path)


def _fig_pca_loadings(loadings: pd.DataFrame, variance: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.80)
    share = float(variance.loc[0, "variance_share"]) if not variance.empty else np.nan
    add_figure_header(
        fig,
        "Common crypto factor loadings are broad but not identical",
        f"PC1 explains {share:.1%} of matched selected-major daily return variation.",
    )
    style_axis(ax)
    plot = loadings.sort_values("PC1", ascending=False)
    bars = ax.bar(plot["asset"], plot["PC1"], color=PALETTE["eth"], edgecolor=PALETTE["eth_dark"])
    ax.axhline(0, color=TOKENS["axis"], linewidth=1)
    ax.set_ylabel("PC1 loading")
    ax.set_xlabel("")
    direct_label_bars(ax, bars, [f"{value:.2f}" for value in plot["PC1"]], padding=0.01)
    return _save_figure(fig, path)


def _fig_regime_difference(regime: pd.DataFrame, path: Path) -> Path:
    matrix = regime.set_index("asset") if "asset" in regime else regime
    apply_theme()
    fig, ax = plt.subplots(figsize=(11, 8))
    fig.subplots_adjust(left=0.16, right=0.96, bottom=0.16, top=0.82)
    add_figure_header(
        fig,
        "Correlation shifts are regime-dependent",
        "BTC-ETF-era Pearson correlations minus pre-BTC-ETF correlations.",
        left=0.14,
    )
    sns.heatmap(matrix, ax=ax, cmap="vlag", center=0, cbar_kws={"label": "Correlation difference"})
    ax.set_xlabel("")
    ax.set_ylabel("")
    return _save_figure(fig, path)


def _copy_or_build_macro_figure(root: Path, old: str, figures_dir: Path) -> Path:
    dst = figures_dir / "02_tradfi_exposure_shift.png"
    return _fig_tradfi_exposure_shift(
        _table(root, figures_dir.parent, "block_delta_r2.csv", old), dst
    )


def _fig_tradfi_exposure_shift(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.20, top=0.80)
    add_figure_header(
        fig,
        "Equity co-movement contribution rises in ETF-era windows",
        "Same-support daily equity-block delta R2; period comparison, not ETF attribution.",
    )
    style_axis(ax)
    required = {"asset", "frequency", "regime", "block", "drop_block_delta_r2", "n"}
    if not frame.empty and required.issubset(frame.columns):
        plot = frame[
            frame["frequency"].eq("daily")
            & frame["block"].eq("equity_beta")
            & frame["regime"].isin(["pre_btc_etf", "btc_etf_era"])
        ].copy()
        if not plot.empty:
            plot["period"] = plot["regime"].map(
                {"pre_btc_etf": "Pre-BTC ETF", "btc_etf_era": "BTC ETF era"}
            )
            plot["asset_period"] = plot["asset"] + "\n" + plot["period"]
            colors = plot["period"].map(
                {"Pre-BTC ETF": PALETTE["slate"], "BTC ETF era": PALETTE["btc"]}
            )
            bars = ax.bar(
                plot["asset_period"],
                plot["drop_block_delta_r2"],
                color=colors,
                edgecolor=TOKENS["axis"],
            )
            labels = [
                f"{value:.1%}\nn={int(n)}"
                for value, n in zip(plot["drop_block_delta_r2"], plot["n"], strict=False)
            ]
            direct_label_bars(ax, bars, labels, padding=0.004)
    ax.set_ylabel("Equity-block delta R2")
    ax.set_xlabel("")
    return _save_figure(fig, path)


def _fig_rolling_tradfi(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.09, right=0.96, bottom=0.16, top=0.80)
    add_figure_header(
        fig, "Rolling TradFi beta is time-varying", "Median rolling beta by feature and asset."
    )
    style_axis(ax)
    if not frame.empty and {"asset", "feature_id", "beta"}.issubset(frame.columns):
        plot = (
            frame[frame["feature_id"].isin(["qqq_ret", "spy_ret", "vix_d1", "dxy_ret"])]
            .groupby(["asset", "feature_id"], dropna=False)["beta"]
            .median()
            .reset_index()
        )
        sns.barplot(
            data=plot,
            x="feature_id",
            y="beta",
            hue="asset",
            ax=ax,
            palette=[PALETTE["btc"], PALETTE["eth"]],
        )
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
    ax.set_xlabel("")
    ax.set_ylabel("Median rolling beta")
    return _save_figure(fig, path)


def _fig_block_delta_heatmap(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Block delta R-squared differs by asset and model family",
        "Same-support drop-block delta R2; darker means larger contribution.",
        left=0.11,
    )
    if not frame.empty and {"asset", "block", "drop_block_delta_r2"}.issubset(frame.columns):
        plot = (
            frame.groupby(["asset", "block"], dropna=False)["drop_block_delta_r2"]
            .median()
            .unstack()
        )
        sns.heatmap(plot, ax=ax, cmap="mako", cbar_kws={"label": "Median delta R2"})
    return _save_figure(fig, path)


def _copy_or_build_derivatives_figure(root: Path, old: str, figures_dir: Path) -> Path:
    src = root / "research" / old / "figures" / "03_leverage_tail_stress.png"
    dst = figures_dir / "03_leverage_tail_stress.png"
    if src.exists():
        _copy_png_svg(src, dst)
        return dst
    return _fig_leverage_surface(
        _table(root, figures_dir.parent, "leverage_tail_risk_summary.csv", old), dst
    )


def _fig_leverage_surface(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Tail risk changes across lagged leverage states",
        "Bottom-5% day rate by leverage-state quintile.",
    )
    style_axis(ax)
    if not frame.empty and {"leverage_state", "bottom5_rate"}.issubset(frame.columns):
        plot = frame.sort_values("leverage_state")
        bars = ax.bar(
            plot["leverage_state"],
            plot["bottom5_rate"],
            color=PALETTE["stress"],
            edgecolor=PALETTE["stress_dark"],
        )
        direct_label_bars(ax, bars, [f"{value:.1%}" for value in plot["bottom5_rate"]])
    ax.set_ylabel("Bottom-5% day rate")
    ax.set_xlabel("Lagged leverage state")
    return _save_figure(fig, path)


def _fig_liquidation_events(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.20, top=0.80)
    add_figure_header(
        fig,
        "Liquidation event windows are stress signatures",
        "Post-event returns remain descriptive and timing-sensitive.",
    )
    style_axis(ax)
    if not frame.empty and {"event_id", "post_10d_return_plus1_to_plus10"}.issubset(frame.columns):
        plot = frame.sort_values("btc_total_liq_usd", ascending=False).head(12).copy()
        plot["event_label"] = (
            plot["event_id"].astype(str).str.replace("_", " ").str.replace("top liquidation ", "L")
        )
        bars = ax.bar(
            plot["event_label"],
            plot["post_10d_return_plus1_to_plus10"],
            color=PALETTE["btc"],
            edgecolor=PALETTE["btc_dark"],
        )
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
        direct_label_bars(
            ax, bars, [f"{value:.1%}" for value in plot["post_10d_return_plus1_to_plus10"]]
        )
        ax.tick_params(axis="x", labelrotation=35)
    ax.set_ylabel("+1 to +10 day return")
    return _save_figure(fig, path)


def _fig_etf_lag_response(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.16, top=0.80)
    add_figure_header(
        fig,
        "ETF flow-return association is a short-lag plumbing diagnostic",
        "Lag 0-5 flow-intensity correlations with moving-block bootstrap intervals.",
    )
    style_axis(ax)
    colors = {"BTC": PALETTE["btc"], "ETH": PALETTE["eth"]}
    for asset, group in frame.groupby("asset"):
        group = group.sort_values("lag_days")
        ax.plot(
            group["lag_days"],
            group["return_corr"],
            marker="o",
            linewidth=2,
            color=colors.get(asset, PALETTE["risk"]),
            label=asset,
        )
        ax.fill_between(
            group["lag_days"],
            group["ci_low"],
            group["ci_high"],
            color=colors.get(asset, PALETTE["risk"]),
            alpha=0.18,
        )
    ax.axhline(0, color=TOKENS["axis"], linewidth=1)
    ax.set_xlabel("Flow lag in ETF trading days")
    ax.set_ylabel("Correlation with same-day return")
    ax.set_xticks(range(6))
    ax.legend(frameon=False)
    return _save_figure(fig, path)


def _fig_etf_placebo(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.09, right=0.96, bottom=0.16, top=0.80)
    add_figure_header(
        fig,
        "Large ETF-flow days are compared with non-shock placebo samples",
        "Bars show shock-day mean return; intervals show placebo 5th-95th percentiles.",
    )
    style_axis(ax)
    if not frame.empty:
        x = np.arange(len(frame))
        bars = ax.bar(
            x,
            frame["shock_mean_return"],
            color=[PALETTE["btc"], PALETTE["eth"]][: len(frame)],
            edgecolor=TOKENS["ink"],
        )
        ax.errorbar(
            x,
            frame["placebo_mean_return_median"],
            yerr=[
                frame["placebo_mean_return_median"] - frame["placebo_mean_return_q05"],
                frame["placebo_mean_return_q95"] - frame["placebo_mean_return_median"],
            ],
            fmt="o",
            color=TOKENS["ink"],
            capsize=5,
            label="Placebo median and 5-95%",
        )
        ax.set_xticks(x, frame["asset"])
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
        direct_label_bars(ax, bars, [f"{value:.2%}" for value in frame["shock_mean_return"]])
    ax.set_ylabel("Mean return")
    ax.legend(frameon=False)
    return _save_figure(fig, path)


def _fig_etf_timing_audit(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "ETF plots start at valid source dates",
        "Pre-inception plotted observations must remain zero.",
    )
    style_axis(ax)
    if not frame.empty:
        bars = ax.bar(
            frame["asset"],
            frame["pre_inception_plotted_observations"],
            color=PALETTE["stable"],
            edgecolor=PALETTE["stable_dark"],
        )
        direct_label_bars(
            ax, bars, [str(int(value)) for value in frame["pre_inception_plotted_observations"]]
        )
    ax.set_ylabel("Pre-inception plotted observations")
    return _save_figure(fig, path)


def _copy_or_build_liquidity_figure(root: Path, old: str, figures_dir: Path) -> Path:
    src = root / "research" / old / "figures" / "liquidity_state_correlations.png"
    dst = figures_dir / "liquidity_state_correlations.png"
    if src.exists():
        _copy_png_svg(src, dst)
        return dst
    return _fig_valuation_contamination(
        _table(root, figures_dir.parent, "valuation_contamination_audit.csv", old), dst
    )


def _fig_liquidity_regimes(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Liquidity-state bins are weak state diagnostics",
        "Weekly regime summaries retain endogenous-proxy caveats.",
    )
    style_axis(ax)
    numeric_cols = [
        col
        for col in frame.columns
        if "return" in col and pd.api.types.is_numeric_dtype(frame[col])
    ]
    if not frame.empty and numeric_cols:
        col = numeric_cols[0]
        xcol = "liquidity_regime" if "liquidity_regime" in frame else frame.columns[0]
        bars = ax.bar(
            frame[xcol].astype(str),
            frame[col],
            color=PALETTE["stable"],
            edgecolor=PALETTE["stable_dark"],
        )
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
        direct_label_bars(ax, bars, [f"{value:.2%}" for value in frame[col]])
        ax.set_ylabel(col)
    return _save_figure(fig, path)


def _fig_valuation_contamination(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Raw USD TVL has explicit valuation-content risk",
        "Correlations with returns are measurement-risk screens, not liquidity shocks.",
    )
    style_axis(ax)
    if not frame.empty and {"asset", "correlation_with_return"}.issubset(frame.columns):
        bars = ax.bar(
            frame["asset"],
            frame["correlation_with_return"],
            color=PALETTE["risk"],
            edgecolor=PALETTE["risk_dark"],
        )
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
        direct_label_bars(ax, bars, [f"{value:.2f}" for value in frame["correlation_with_return"]])
    ax.set_ylabel("Correlation with return")
    return _save_figure(fig, path)


def _copy_or_build_onchain_figure(root: Path, old: str, figures_dir: Path) -> Path:
    dst = figures_dir / "measurement_mvrv_mechanics.png"
    return _fig_mvrv_mechanics(
        _table(root, figures_dir.parent, "mvrv_identity_points.csv", old), dst
    )


def _fig_onchain_state(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.09, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Lagged holder-state outcomes remain state diagnostics",
        "MVRV-state quintiles use prior information and report weak average-return evidence honestly.",
    )
    style_axis(ax)
    if not frame.empty and {"mvrv_state_quintile", "next_week_return_mean"}.issubset(frame.columns):
        bars = ax.bar(
            frame["mvrv_state_quintile"].astype(str),
            frame["next_week_return_mean"],
            color=PALETTE["eth"],
            edgecolor=PALETTE["eth_dark"],
        )
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
        direct_label_bars(ax, bars, [f"{value:.2%}" for value in frame["next_week_return_mean"]])
    ax.set_ylabel("Mean next-week return")
    return _save_figure(fig, path)


def _fig_mvrv_residual(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.16, top=0.80)
    add_figure_header(
        fig,
        "MVRV identity residuals expose source convention limits",
        "Residual equals d-log MVRV minus market-cap change plus realized-cap change.",
    )
    style_axis(ax)
    if not frame.empty and "identity_residual" in frame:
        series = pd.to_numeric(frame["identity_residual"], errors="coerce").dropna()
        ax.hist(series, bins=60, color=PALETTE["slate"], edgecolor=PALETTE["risk_dark"])
    ax.set_xlabel("Identity residual")
    ax.set_ylabel("Days")
    return _save_figure(fig, path)


def _fig_mvrv_mechanics(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.16, top=0.80)
    add_figure_header(
        fig,
        "Same-day MVRV mostly repackages BTC price movement",
        "Daily d-log MVRV versus BTC return; mechanics diagnostic, not an independent factor.",
    )
    style_axis(ax, x_grid=True)
    required = {"btc_ret", "d_log_mvrv"}
    if not frame.empty and required.issubset(frame.columns):
        plot = frame[["btc_ret", "d_log_mvrv"]].apply(pd.to_numeric, errors="coerce").dropna()
        if not plot.empty:
            sample = plot.sample(n=min(900, len(plot)), random_state=1337)
            ax.scatter(
                sample["btc_ret"],
                sample["d_log_mvrv"],
                s=18,
                alpha=0.28,
                color=PALETTE["eth"],
                edgecolor="none",
            )
            lower = float(min(plot["btc_ret"].quantile(0.01), plot["d_log_mvrv"].quantile(0.01)))
            upper = float(max(plot["btc_ret"].quantile(0.99), plot["d_log_mvrv"].quantile(0.99)))
            ax.plot([lower, upper], [lower, upper], color=PALETTE["stress"], linewidth=2)
            corr = plot["btc_ret"].corr(plot["d_log_mvrv"])
            ax.text(
                0.02,
                0.94,
                f"corr = {corr:.3f}\nn = {len(plot):,}",
                transform=ax.transAxes,
                color=TOKENS["ink"],
                fontsize=11,
                va="top",
            )
    ax.set_xlabel("BTC daily log return")
    ax.set_ylabel("Daily d-log MVRV")
    return _save_figure(fig, path)


def _copy_or_build_chain_figure(root: Path, old: str, figures_dir: Path) -> Path:
    src = root / "research" / old / "figures" / "chain_panel_coverage.png"
    dst = figures_dir / "chain_panel_coverage.png"
    if src.exists():
        _copy_png_svg(src, dst)
        return dst
    return _fig_chain_metric_coverage(
        _table(root, figures_dir.parent, "chain_fundamental_panel_summary.csv", old), dst
    )


def _fig_pit_coefficients(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.22, top=0.80)
    add_figure_header(
        fig,
        "PIT concentration is used as a state variable, not a headline line chart",
        "Standardized monthly coefficients with simple 95% intervals.",
        left=0.10,
    )
    style_axis(ax, x_grid=True)
    if not frame.empty:
        plot = frame.sort_values("coefficient")
        y = np.arange(len(plot))
        ax.errorbar(
            plot["coefficient"],
            y,
            xerr=[plot["coefficient"] - plot["ci_low"], plot["ci_high"] - plot["coefficient"]],
            fmt="o",
            color=PALETTE["btc"],
            capsize=4,
        )
        ax.set_yticks(y, [f"{r.outcome} ~ {r.feature}" for r in plot.itertuples(index=False)])
        ax.axvline(0, color=TOKENS["axis"], linewidth=1)
    ax.set_xlabel("Standardized coefficient")
    return _save_figure(fig, path)


def _fig_chain_metric_coverage(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.13, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Chain metric coverage is uneven",
        "Counts show metric families with adequate descriptive-panel status.",
        left=0.11,
    )
    style_axis(ax)
    if not frame.empty and {"chain", "panel_status"}.issubset(frame.columns):
        plot = (
            frame[frame["panel_status"].astype(str).str.contains("adequate", na=False)]
            .groupby("chain")
            .size()
            .sort_values(ascending=False)
            .head(15)
        )
        ax.barh(plot.index, plot.values, color=PALETTE["stable"], edgecolor=PALETTE["stable_dark"])
        ax.invert_yaxis()
    ax.set_xlabel("Adequate metric families")
    return _save_figure(fig, path)


def _fig_factor_decomposition(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Selected-major risk splits into common and idiosyncratic components",
        "Matched-window PC1 regression variance shares; current-cohort caveat applies.",
    )
    style_axis(ax)
    if not frame.empty:
        plot = frame.sort_values("common_variance_share", ascending=False)
        ax.bar(
            plot["asset"],
            plot["common_variance_share"],
            color=PALETTE["eth"],
            edgecolor=PALETTE["eth_dark"],
            label="Common",
        )
        ax.bar(
            plot["asset"],
            plot["idiosyncratic_variance_share"],
            bottom=plot["common_variance_share"],
            color=PALETTE["slate"],
            edgecolor=PALETTE["risk_dark"],
            label="Idiosyncratic",
        )
        ax.legend(frameon=False)
    ax.set_ylabel("Share of return variance")
    return _save_figure(fig, path)


def _fig_downside_forest(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Downside expected shortfall differs across selected majors",
        "Expected shortfall is the mean of returns below each asset's fifth percentile.",
    )
    style_axis(ax, x_grid=True)
    if not frame.empty:
        plot = frame.sort_values("expected_shortfall_5pct")
        ax.scatter(
            plot["expected_shortfall_5pct"],
            plot["asset"],
            s=110,
            color=PALETTE["stress"],
            edgecolor=PALETTE["stress_dark"],
        )
        ax.axvline(0, color=TOKENS["axis"], linewidth=1)
    ax.set_xlabel("Expected shortfall 5%")
    ax.set_ylabel("")
    return _save_figure(fig, path)


def _fig_selected_major_beta(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.20, top=0.80)
    add_figure_header(
        fig,
        "Benchmark betas are supporting risk diagnostics",
        "Median beta by selected asset across BTC/ETH/QQQ benchmarks where available.",
    )
    style_axis(ax)
    if not frame.empty and {"symbol", "beta"}.issubset(frame.columns):
        plot = frame.groupby("symbol")["beta"].median().sort_values(ascending=False)
        ax.bar(plot.index, plot.values, color=PALETTE["btc"], edgecolor=PALETTE["btc_dark"])
        ax.axhline(0, color=TOKENS["axis"], linewidth=1)
    ax.set_ylabel("Median benchmark beta")
    return _save_figure(fig, path)


def _copy_or_build_event_figure(root: Path, old: str, figures_dir: Path) -> Path:
    dst = figures_dir / "appendix_event_response_matrix.png"
    return _fig_event_response_matrix(
        _table(root, figures_dir.parent, "event_response_matrix.csv", old), dst
    )


def _copy_or_build_synthesis_figure(root: Path, old: str, figures_dir: Path) -> Path:
    src = root / "research" / old / "figures" / "synthesis_claim_source_depth.png"
    dst = figures_dir / "synthesis_claim_source_depth.png"
    if src.exists():
        _copy_png_svg(src, dst)
        return dst
    return _fig_evidence_grades(_table(root, figures_dir.parent, "evidence_ledger.csv", old), dst)


def _fig_evidence_grades(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 6.75))
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.18, top=0.80)
    add_figure_header(
        fig,
        "Evidence grades keep weak and qualified findings visible",
        "Counts by grade/status from the cross-module evidence ledger.",
    )
    style_axis(ax)
    if not frame.empty and "evidence_grade" in frame:
        counts = frame["evidence_grade"].fillna("ungraded").value_counts().sort_index()
        bars = ax.bar(
            counts.index.astype(str),
            counts.values,
            color=PALETTE["risk"],
            edgecolor=PALETTE["risk_dark"],
        )
        direct_label_bars(ax, bars, [str(int(value)) for value in counts.values])
    ax.set_ylabel("Claim count")
    return _save_figure(fig, path)


def _fig_event_response_matrix(frame: pd.DataFrame, path: Path) -> Path:
    apply_theme()
    fig, ax = plt.subplots(figsize=(12, 7.5))
    fig.subplots_adjust(left=0.28, right=0.96, bottom=0.16, top=0.82)
    add_figure_header(
        fig,
        "Event responses remain appendix sensitivity context",
        "+1 to +10 day returns around registered events; no event-causal identification.",
        left=0.08,
    )
    if not frame.empty and {"event_id", "asset", "post_window_return"}.issubset(frame.columns):
        plot = frame.copy()
        plot["event_label"] = plot["event_id"].astype(str).str.replace("_", " ")
        matrix = plot.pivot_table(
            index="event_label",
            columns="asset",
            values="post_window_return",
            aggfunc="mean",
        ).sort_index()
        sns.heatmap(
            matrix,
            ax=ax,
            cmap="vlag",
            center=0,
            annot=True,
            fmt=".1%",
            cbar_kws={"label": "+1 to +10 return"},
        )
        ax.set_xlabel("")
        ax.set_ylabel("")
    else:
        style_axis(ax)
        ax.text(
            0.5,
            0.5,
            "No event-response rows available",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color=TOKENS["muted"],
        )
    return _save_figure(fig, path)


def _evidence_map_csv(ledger: pd.DataFrame) -> pd.DataFrame:
    if ledger.empty:
        return pd.DataFrame(
            columns=["module_id", "accepted_claims", "median_grade", "measurement_risk"]
        )
    module_col = "module_id" if "module_id" in ledger else "module"
    return (
        ledger.groupby(module_col, dropna=False)
        .agg(
            accepted_claims=(
                "status",
                lambda s: int(s.astype(str).str.contains("accepted", na=False).sum()),
            ),
            median_grade=(
                "evidence_grade",
                lambda s: "|".join(sorted(set(s.dropna().astype(str)))),
            ),
            measurement_risk=(
                "limitation",
                lambda s: "; ".join(sorted(set(s.dropna().astype(str)))[:2]),
            ),
        )
        .reset_index()
        .rename(columns={module_col: "module_id"})
    )


def _current_evidence_ledger(root: Path) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for module in MODULES:
        if module.module_id == "09_event_stress_cross_module_synthesis":
            continue
        path = root / "research" / module.module_id / "tables" / "claims.csv"
        if path.exists():
            claims = read_csv_if_exists(path)
            if not claims.empty:
                rows.append(claims)
    if not rows:
        return pd.DataFrame()
    ledger = pd.concat(rows, ignore_index=True, sort=False)
    ledger["module_id"] = ledger["module_id"].astype(str)
    ledger["claim_quality_dimension"] = ledger.apply(_claim_quality_dimension, axis=1)
    ledger["measurement_risk_flag"] = (
        ledger["limitation"]
        .astype(str)
        .str.contains(
            "mechanic|valuation|timing|survivorship|causal|restricted|PIT|current-cohort",
            case=False,
            regex=True,
            na=False,
        )
    )
    return ledger.sort_values(["module_id", "claim_id"]).reset_index(drop=True)


def _claim_quality_dimension(row: pd.Series) -> str:
    text = (
        f"{row.get('method', '')} {row.get('uncertainty', '')} {row.get('limitation', '')}".lower()
    )
    labels = []
    if any(term in text for term in ["bootstrap", "interval", "hac", "fdr", "ridge"]):
        labels.append("uncertainty")
    if any(term in text for term in ["coverage", "matched", "sample"]):
        labels.append("sample")
    if any(term in text for term in ["measurement", "valuation", "timing", "survivorship"]):
        labels.append("measurement")
    return "|".join(labels) or "source-linked"


def _current_claim_inventory(ledger: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in ledger.to_dict("records"):
        rows.append(
            {
                "module_id": row.get("module_id", ""),
                "claim_id": row.get("claim_id", ""),
                "claim": row.get("claim_text", ""),
                "disposition": row.get("status", ""),
                "evidence_grade": row.get("evidence_grade", ""),
                "source_table": row.get("source_table", ""),
                "source_figure": row.get("source_figure", ""),
                "limitation": row.get("limitation", ""),
            }
        )
    rows.extend(
        [
            {
                "module_id": "07_chain_fundamentals_sector_dynamics",
                "claim_id": "demote_current_top50_daily_altseason",
                "claim": "Current-top50 daily returns are historical altseason evidence.",
                "disposition": "demote",
                "evidence_grade": "D",
                "source_table": "tables/asset_universe_audit.csv",
                "source_figure": "",
                "limitation": "Current-cohort daily analysis is survivorship-biased; PIT monthly data supports structure/state analysis only.",
            },
            {
                "module_id": "04_etf_institutional_flows",
                "claim_id": "demote_etf_causal_price_impact",
                "claim": "ETF flows cause same-day crypto returns.",
                "disposition": "demote",
                "evidence_grade": "D",
                "source_table": "tables/etf_lag_response.csv",
                "source_figure": "figures/04_etf_lag_response.png",
                "limitation": "Flow timing and simultaneity prevent causal interpretation.",
            },
        ]
    )
    return pd.DataFrame(rows)


def _current_robustness_summary(ledger: pd.DataFrame) -> pd.DataFrame:
    if ledger.empty:
        return pd.DataFrame()
    return (
        ledger.groupby("module_id", dropna=False)
        .agg(
            claim_count=("claim_id", "count"),
            accepted_qualified=(
                "status",
                lambda s: int(s.astype(str).str.contains("accepted", na=False).sum()),
            ),
            evidence_grades=(
                "evidence_grade",
                lambda s: "|".join(sorted(set(s.dropna().astype(str)))),
            ),
            measurement_risk_flags=("measurement_risk_flag", "sum"),
            robustness_dimensions=(
                "claim_quality_dimension",
                lambda s: "|".join(sorted(set(s.dropna().astype(str)))),
            ),
        )
        .reset_index()
    )


def _table(root: Path, module_dir: Path, name: str, old_module: str | None = None) -> pd.DataFrame:
    candidates = [
        module_dir / "tables" / name,
        root / "research" / module_dir.name / "tables" / name,
    ]
    if old_module:
        candidates.append(root / "research" / old_module / "tables" / name)
    candidates.append(root / "outputs" / "tables" / name)
    return _first_existing_table(candidates)


def _first_existing_table(paths: list[Path]) -> pd.DataFrame:
    for path in paths:
        if path.exists():
            if path.suffix.lower() == ".md":
                return pd.DataFrame([{"markdown": path.read_text(encoding="utf-8")}])
            return read_csv_if_exists(path)
    return pd.DataFrame()


def _copy_png_svg(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() == dst.resolve():
        return
    shutil.copy2(src, dst)
    if src.with_suffix(".svg").exists():
        shutil.copy2(src.with_suffix(".svg"), dst.with_suffix(".svg"))


def _save_figure(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=190, bbox_inches="tight", facecolor=TOKENS["background"])
    svg = path.with_suffix(".svg")
    fig.savefig(
        svg, dpi=190, bbox_inches="tight", facecolor=TOKENS["background"], metadata={"Date": None}
    )
    with suppress(OSError):
        svg.write_text(
            "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())
            + "\n",
            encoding="utf-8",
        )
    plt.close(fig)
    return path


def _sample_table(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for name, frame in sorted(tables.items()):
        if name == "claims.csv":
            continue
        rows.append(
            {
                "artifact": f"tables/{name}",
                "rows": len(frame),
                "sample": _sample_from_table(frame),
                "coverage rule": _coverage_rule_from_name(name),
            }
        )
    return pd.DataFrame(rows[:14])


def _sample_from_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "no rows"
    date_cols = [
        col
        for col in frame.columns
        if col in {"date", "sample_start", "first_date", "first_valid_date", "snapshot_date"}
    ]
    end_cols = [
        col for col in frame.columns if col in {"sample_end", "last_date", "last_valid_date"}
    ]
    if "sample_start" in frame and "sample_end" in frame:
        starts = pd.to_datetime(frame["sample_start"], errors="coerce").dropna()
        ends = pd.to_datetime(frame["sample_end"], errors="coerce").dropna()
        if not starts.empty and not ends.empty:
            return f"{starts.min().date()} to {ends.max().date()}, n={len(frame)}"
    if date_cols:
        dates = pd.to_datetime(frame[date_cols[0]], errors="coerce").dropna()
        if not dates.empty:
            return f"{dates.min().date()} to {dates.max().date()}, rows={len(frame)}"
    if end_cols:
        ends = pd.to_datetime(frame[end_cols[0]], errors="coerce").dropna()
        if not ends.empty:
            return f"through {ends.max().date()}, rows={len(frame)}"
    return f"rows={len(frame)}"


def _coverage_rule_from_name(name: str) -> str:
    lower = name.lower()
    if "etf" in lower:
        return "ETF source rows only; no pre-inception zero fill"
    if "pit" in lower:
        return "monthly point-in-time state variables only"
    if "selected" in lower or "factor" in lower:
        return "matched current-cohort selected-major window"
    if "mvrv" in lower:
        return "measurement mechanics and lagged-state diagnostics"
    return "module-specific matched sample"


def _n_sample(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "no rows"
    if isinstance(frame.index, pd.DatetimeIndex):
        return f"{frame.index.min().date()} to {frame.index.max().date()}, n={len(frame)}"
    return _sample_from_table(frame.reset_index())


def _numeric_body(frame: pd.DataFrame) -> pd.DataFrame:
    if "asset" in frame:
        frame = frame.drop(columns=["asset"])
    return frame.apply(pd.to_numeric, errors="coerce")


def _findings_text(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- {row.get('finding', 'Finding')}: {row.get('estimate', 'see tables')} ({row.get('interpretation', 'see interpretation')})"
        for row in rows
    )


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
        "uncertainty": "Reported in source tables where applicable; otherwise descriptive and coverage-bound.",
        "evidence_grade": "B",
        "source_table": source_table,
        "source_figure": source_figure,
        "limitation": limitation,
        "status": "accepted_qualified",
    }


def _normalize_claims(claims: list[dict[str, Any]], module_id: str) -> list[dict[str, Any]]:
    normalized = []
    for claim in claims:
        row = dict(claim)
        text = str(row.get("claim_text", ""))
        row.setdefault("module", module_id)
        row.setdefault("finding", text)
        row.setdefault("outcome", "module-level evidence")
        row.setdefault("feature_or_block", "see source_table")
        row.setdefault("estimate_summary", text)
        row.setdefault("uncertainty_summary", row.get("uncertainty", "See source table."))
        row.setdefault("sample_summary", row.get("sample", "See source table."))
        row.setdefault("frequency", "see source table")
        row.setdefault("timing", "see source table")
        row.setdefault("sensitivity_summary", row.get("method", "See source table."))
        row.setdefault("interpretation", text)
        row.setdefault("alternative_explanation", row.get("limitation", "See module limitations."))
        row.setdefault(
            "source_model_ids", _model_ids_from_source_tables(row.get("source_table", ""))
        )
        normalized.append(row)
    return normalized


def _model_ids_from_source_tables(source_table: Any) -> str:
    ids = []
    for item in str(source_table).replace(",", ";").split(";"):
        item = item.strip()
        if item:
            ids.append(f"table:{Path(item).stem}")
    return "; ".join(ids) or "table:claims"


MODULE_SPECS: dict[str, ModuleSpec] = {
    "01_cross_asset_dependence_regimes": ModuleSpec(
        "01_cross_asset_dependence_regimes",
        "This module replaces the former BTC/ETH returns-regime scaffold with a multi-asset dependence analysis spanning selected crypto majors and verified TradFi/macro return or change series.",
        (
            "How broad is common-factor crypto dependence across the selected-major universe?",
            "How do Pearson, Spearman, partial, lower-tail, rolling, and regime-difference dependence diagnostics compare?",
        ),
        (
            "Correlation matrices: Pearson and Spearman correlations are computed on matched daily observations with explicit coverage tables.",
            "PCA/common factor: standardized selected-major returns are decomposed with deterministic SVD.",
            "Tail dependence: lower-tail co-exceedance counts joint bottom-5% days for each pair.",
        ),
        (
            "$\\rho_{ij}=\\operatorname{corr}(r_i,r_j)$.",
            "$\\text{PC share}_k = s_k^2 / \\sum_j s_j^2$ from the standardized return matrix.",
            "$\\text{co-exceed}_{ij}=N^{-1}\\sum_t 1[r_{i,t}\\le q_i(0.05), r_{j,t}\\le q_j(0.05)]$.",
        ),
        "Dependence results describe realized co-movement and common-factor structure. They do not imply investability, forecasts, or causal transmission.",
        "Selected-major daily data uses a current-cohort source and is survivorship-biased. TradFi variables use available close alignment and should be interpreted as contemporaneous co-movement.",
        _build_cross_asset,
        ("correlation", "tail co-exceedance", "PCA common-factor share", "rolling dependence"),
        ("selected-major returns", "SPY/QQQ/IWM", "DXY/gold/VIX/rates"),
        ("daily",),
        (
            "Pearson/Spearman",
            "BTC-control partial correlations",
            "regime split",
            "tail threshold",
            "rolling window",
        ),
    ),
    "02_macro_tradfi_integration": ModuleSpec(
        "02_macro_tradfi_integration",
        "This module estimates BTC/ETH co-movement with equities, volatility, rates, the dollar, gold, and credit using synchronized calendars and same-support comparisons.",
        (
            "How do equity, volatility, dollar, rates, and gold blocks contribute to contemporaneous crypto exposure models?",
            "Are later-sample exposure differences robust to frequency, multicollinearity, FDR, and ridge sensitivity?",
        ),
        (
            "HAC OLS: synchronized daily and weekly panels estimate contemporaneous exposure models.",
            "Same-support block R-squared: full and reduced models use identical complete-case rows.",
            "Stability diagnostics: VIF, condition number, ridge paths, FDR q-values, and rolling beta are reported.",
        ),
        (
            "$\\Delta R^2_b = R^2_{full} - R^2_{reduced(-b)}$ on the same support.",
            "$R^2_{partial}=(SSE_{reduced}-SSE_{full})/SSE_{reduced}$.",
        ),
        "Macro/TradFi integration is contemporaneous co-movement evidence, not macro causality or ETF-effect identification.",
        "Business-date alignment, period splits, and rolling windows are descriptive. Same-day models cannot establish lead-lag direction.",
        _build_macro,
        ("HAC exposure", "delta R-squared", "rolling beta", "stability diagnostics"),
        ("SPY", "QQQ", "IWM", "VIX", "DXY", "gold", "nominal and real rates"),
        ("daily", "weekly"),
        ("frequency", "period split", "HAC bandwidth", "FDR", "VIF", "ridge"),
    ),
    "03_derivatives_leverage_liquidations": ModuleSpec(
        "03_derivatives_leverage_liquidations",
        "This module studies lagged leverage, funding, open-interest scaling, and liquidation stress as state diagnostics for volatility and tail outcomes.",
        (
            "Where do lagged leverage states coincide with volatility and bottom-tail outcomes?",
            "How do liquidation event windows compare with stress-state summaries?",
        ),
        (
            "State bins: leverage metrics are lagged before quintile/state assignment.",
            "Tail diagnostics: bottom-tail rates and logit-style tail summaries are reported by state.",
            "Event/placebo: liquidation windows exclude same-day initiation signatures.",
        ),
        (
            "$\\text{tail rate}_q = N_q^{-1}\\sum_t 1[r_t \\le Q_{0.05}]$.",
            "$\\text{liq intensity}=\\text{liquidations}/\\text{lagged OI or market cap}$.",
        ),
        "Derivatives variables are stress-state diagnostics. They are not trading rules and do not establish directional liquidation attribution.",
        "Liquidation timestamps, denominator price content, and same-day simultaneity constrain interpretation.",
        _build_derivatives,
        ("tail-day rate", "realized volatility", "liquidation event response"),
        ("funding", "open interest", "liquidations", "leverage percentile"),
        ("daily", "event windows"),
        ("state bins", "lags", "tail threshold", "denominator scaling", "event windows"),
    ),
    "04_etf_institutional_flows": ModuleSpec(
        "04_etf_institutional_flows",
        "This module replaces the old cumulative-flow root figure with ETF lag-response, source-timing, and flow-shock/placebo diagnostics.",
        (
            "How do BTC and ETH ETF flow-intensity associations vary over lags 0-5?",
            "Do plotted ETF series begin only at valid source observations?",
        ),
        (
            "Lag response: ETF net flows are scaled by lagged market cap and shifted over lags 0-5.",
            "Moving-block bootstrap: deterministic block resampling produces correlation intervals.",
            "Timing audit: first plotted dates must equal or follow first valid source dates.",
        ),
        (
            "$f_t=\\text{ETF net flow}_t/\\text{market cap}_{t-1}$.",
            "$\\rho_l=\\operatorname{corr}(r_t, f_{t-l})$ for lags $l=0,\\dots,5$.",
        ),
        "ETF flows are market-plumbing associations with timing and simultaneity concerns, not causal return estimates.",
        "Issuer flow timing, non-reporting days, holidays, and launch-date differences require asset-specific samples.",
        _build_etf,
        ("lag-response correlation", "flow-shock placebo", "timing audit"),
        ("BTC ETF flow", "ETH ETF flow", "lagged market cap", "BTC/ETH returns"),
        ("ETF trading daily",),
        ("lags 0-5", "BTC/ETH separate starts", "block-bootstrap interval", "shock threshold"),
    ),
    "05_stablecoin_defi_liquidity": ModuleSpec(
        "05_stablecoin_defi_liquidity",
        "This module treats stablecoin supply, DeFi TVL, and related balances as endogenous liquidity-state proxies with explicit valuation-contamination checks.",
        (
            "Which stablecoin/DeFi state variables have usable weekly coverage?",
            "How much raw USD TVL behavior is plausibly valuation-sensitive?",
        ),
        (
            "Weekly state analysis: Sunday-ended weekly growth and lagged state variables are summarized.",
            "Valuation contamination: raw USD TVL growth is screened against BTC/ETH returns.",
        ),
        (
            "$\\Delta \\log X_t = \\log X_t - \\log X_{t-1}$.",
            "$\\operatorname{corr}(r_t, \\Delta \\log TVL_t)$ is a price-content screen, not a liquidity shock.",
        ),
        "Stablecoin/DeFi variables are balance-sheet state proxies. Weak or valuation-sensitive results are reported as weak and not forced into the root README.",
        "Raw USD TVL can mechanically rise when deposited-asset prices rise. No exogenous liquidity-shock design is present.",
        _build_liquidity,
        ("weekly liquidity state", "valuation contamination", "state correlations"),
        ("stablecoin supply", "DeFi TVL", "DEX/lending activity"),
        ("weekly",),
        ("raw versus lagged", "TVL price content", "weekly calendar", "state bins"),
    ),
    "06_onchain_valuation_holder_behavior": ModuleSpec(
        "06_onchain_valuation_holder_behavior",
        "This module separates same-day on-chain measurement mechanics from lagged holder-state diagnostics.",
        (
            "How mechanically linked is same-day MVRV to BTC price-state changes?",
            "Do lagged holder-state summaries deserve diagnostic treatment without becoming primary factors?",
        ),
        (
            "Identity decomposition: MVRV changes are decomposed into market-cap and realized-cap changes.",
            "Lagged state bins: prior MVRV-state quintiles summarize next-period outcomes as diagnostics.",
        ),
        (
            "$\\Delta\\log MVRV_t=\\Delta\\log MarketCap_t-\\Delta\\log RealizedCap_t+\\epsilon_t$.",
            "$\\bar r_{q,t+1}=N_q^{-1}\\sum_{t\\in q} r_{t+1}$ for lagged state quintile $q$.",
        ),
        "Same-day MVRV is a mechanical valuation-state diagnostic and remains excluded from primary BTC/ETH models.",
        "Realized-cap conventions, source revisions, and same-day timing limit interpretation.",
        _build_onchain,
        ("MVRV mechanics", "identity residual", "lagged holder-state outcome"),
        ("MVRV", "market cap", "realized cap", "holder-state metrics"),
        ("daily", "weekly state"),
        ("same-day versus lagged", "identity residual", "state quintile", "source convention"),
    ),
    "07_chain_fundamentals_sector_dynamics": ModuleSpec(
        "07_chain_fundamentals_sector_dynamics",
        "This module combines chain-fundamental coverage with point-in-time sector/market-structure state variables, without promoting raw concentration charts.",
        (
            "Which chain metrics and chains have enough coverage for descriptive panel work?",
            "How can PIT concentration/turnover variables be used as state variables without becoming headline raw charts?",
        ),
        (
            "Coverage audit: chain metrics are counted by chain and metric family before relationship claims.",
            "PIT state coefficients: monthly concentration and turnover are modeled as standardized state relationships.",
        ),
        (
            "$z(x)=(x-\\bar x)/\\sigma_x$.",
            "$z(y_t)=\\alpha+\\beta z(state_t)+u_t$ for monthly PIT state relationships.",
        ),
        "Chain and PIT outputs are coverage and state diagnostics. PIT variables support monthly state analysis, not daily constituent-performance claims.",
        "Panel depth differs by metric/chain; monthly PIT snapshots have partial-month and survivorship constraints.",
        _build_chain_sector,
        ("chain coverage", "PIT state coefficient", "turnover/rank state"),
        ("fees", "revenue", "addresses", "stablecoin supply", "PIT concentration", "turnover"),
        ("daily", "monthly"),
        ("coverage threshold", "chain mapping", "monthly state model", "partial period"),
    ),
    "08_relative_asset_risk_factor_structure": ModuleSpec(
        "08_relative_asset_risk_factor_structure",
        "This module replaces the basic selected-major volatility/drawdown scatter with matched-window common-factor, idiosyncratic-risk, downside-beta, and expected-shortfall diagnostics.",
        (
            "How much selected-major risk is common crypto factor versus asset-specific residual risk?",
            "Which assets have larger downside expected shortfall and downside beta on the matched current-cohort window?",
        ),
        (
            "Common/idiosyncratic decomposition: each asset return is regressed on PC1 scores from the matched selected-major panel.",
            "Downside risk: expected shortfall and BTC-tail downside beta are computed on matched rows.",
        ),
        (
            "$r_{i,t}=\\alpha_i+\\beta_i PC1_t+\\epsilon_{i,t}$.",
            "$ES_i(5\\%)=E[r_i\\mid r_i\\le Q_i(0.05)]$.",
        ),
        "Relative asset risk is descriptive and coverage-aware; it is not an investability or ranking claim.",
        "Current-cohort data is survivorship-biased and HYPE/short-history assets limit cross-cycle comparability.",
        _build_relative_risk,
        (
            "common variance share",
            "idiosyncratic variance share",
            "expected shortfall",
            "downside beta",
        ),
        ("selected-major returns", "BTC benchmark", "ETH benchmark", "PC1"),
        ("daily matched window",),
        ("matched window", "benchmark", "tail threshold", "short-history flags"),
    ),
    "09_event_stress_cross_module_synthesis": ModuleSpec(
        "09_event_stress_cross_module_synthesis",
        "This module combines event-window stress diagnostics with the cross-module evidence ledger and final claim-quality synthesis.",
        (
            "How do registered event windows compare with empirical placebo windows?",
            "Which findings remain strongest after sample, uncertainty, measurement-risk, and limitation review?",
        ),
        (
            "Event windows: fixed +1 through +10 windows are compared with empirical placebo blocks.",
            "Evidence synthesis: claim rows are graded by source depth, uncertainty, measurement risk, and limitations.",
        ),
        (
            "$R_{event}=\\sum_{h=1}^{10}r_{t+h}$, excluding event day.",
            "$q$-values and evidence grades are synthesis diagnostics, not causal identification.",
        ),
        "Event and synthesis outputs are final review instruments. They preserve weak/null findings instead of using specification search.",
        "Event windows are not an identification design; synthesis quality depends on upstream modules.",
        _build_event_synthesis,
        ("event response", "placebo percentile", "evidence grade", "measurement-risk ledger"),
        ("event registry", "module claims", "FDR diagnostics", "robustness summaries"),
        ("event windows", "daily", "cross-module"),
        ("window length", "placebo eligibility", "FDR", "measurement risk", "claim grade"),
    ),
}
