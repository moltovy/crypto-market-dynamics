"""Contract tests for the final analytical-overhaul research surface."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

from cqresearch.pipelines.final_research import classify_pit_asset

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"

EXPECTED_MODULES = [
    "00_data_measurement_foundation",
    "01_cross_asset_dependence_regimes",
    "02_macro_tradfi_integration",
    "03_derivatives_leverage_liquidations",
    "04_etf_institutional_flows",
    "05_stablecoin_defi_liquidity",
    "06_onchain_valuation_holder_behavior",
    "07_chain_fundamentals_sector_dynamics",
    "08_relative_asset_risk_factor_structure",
    "09_event_stress_cross_module_synthesis",
]

DATA_FOUNDATION_TABLES = {
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
}

ALLOWED_USAGE_STATUSES = {
    "primary_analysis",
    "robustness_or_sensitivity",
    "diagnostic_only",
    "excluded_insufficient_coverage",
    "excluded_ambiguous_definition_or_unit",
    "excluded_duplicate",
    "excluded_release_risk",
}


def test_final_module_architecture_is_exact() -> None:
    module_dirs = sorted(path.name for path in RESEARCH.iterdir() if path.is_dir())
    assert module_dirs == EXPECTED_MODULES

    forbidden = {
        "00_data_foundation",
        "01_returns_risk_regimes",
        "02_macro_cross_asset_exposure",
        "04_etf_institutional_plumbing",
        "06_onchain_valuation_holder_state",
        "07_chain_fundamentals",
        "08_relative_major_asset_risk",
        "09_market_concentration_state",
        "10_event_sensitivity",
        "11_cross_module_synthesis",
    }
    assert not forbidden.intersection(module_dirs)


def test_data_foundation_tables_and_usage_statuses_are_complete() -> None:
    tables_dir = RESEARCH / "00_data_measurement_foundation" / "tables"
    assert DATA_FOUNDATION_TABLES.issubset({path.name for path in tables_dir.glob("*.csv")})

    usage = pd.read_csv(tables_dir / "feature_usage_matrix.csv")
    assert not usage.empty
    statuses = set(usage["usage_status"].dropna().astype(str))
    assert statuses <= ALLOWED_USAGE_STATUSES
    assert not usage["feature_id"].duplicated().any()
    assert usage["usage_status"].notna().all()

    assets = pd.read_csv(tables_dir / "asset_universe_audit.csv")
    required_assets = {"BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "TRX", "TON", "ADA", "HYPE"}
    assert required_assets.issubset(set(assets["asset"]))
    assert assets["analysis_boundary"].str.contains("survivorship", case=False).any()


def test_root_readme_positioning_sections_and_no_single_question() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Research Question" not in readme
    required_order = [
        "## Project Overview",
        "## What This Repository Analyzes",
        "## Data Universe and Asset Coverage",
        "## Research Modules",
        "## Headline Findings",
        "## Selected Analytical Results",
        "## Methods Used",
        "## Important Limitations",
        "## Reproduce",
        "## Repository Structure",
        "## Data Policy and Citation",
    ]
    positions = [readme.index(heading) for heading in required_order]
    assert positions == sorted(positions)
    assert "empirical research and experimentation repository" in readme
    assert readme.count("Forecasting") <= 1
    assert "Results At A Glance" not in readme
    assert "outputs/" not in readme


def test_module_readmes_embed_figures_methods_formulas_and_results() -> None:
    for module_id in EXPECTED_MODULES:
        content = (RESEARCH / module_id / "README.md").read_text(encoding="utf-8")
        for heading in [
            "## Overview",
            "## Questions Investigated",
            "## Data, Assets, and Sample",
            "## Methodologies and Calculations",
            "## Formulas",
            "## Summary of Results",
            "## Analytical Results and Visualizations",
            "## Robustness and Sensitivity",
            "## Interpretation",
            "## Limitations",
            "## Reproduce This Module",
            "## Files and Code",
        ]:
            assert heading in content, f"{module_id} missing {heading}"
        images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
        assert 2 <= len(images) <= 4, module_id
        assert "$" in content, f"{module_id} has no formula math"


def test_cross_asset_module_is_multi_asset_and_has_dependence_methods() -> None:
    base = RESEARCH / "01_cross_asset_dependence_regimes" / "tables"
    pearson = pd.read_csv(base / "pearson_correlation_matrix.csv")
    assets = set(pearson["asset"])
    assert {"BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "TRX", "TON", "ADA", "HYPE"}.issubset(assets)
    assert {"SPY", "QQQ", "IWM", "Gold", "DXY", "VIX"}.issubset(set(pearson.columns))

    pca = pd.read_csv(base / "pca_variance_share.csv")
    assert pca.loc[0, "variance_share"] > 0.4

    partial = pd.read_csv(base / "partial_correlation_btc_control.csv")
    assert not partial.empty
    assert partial["control"].eq("BTC daily return").all()

    tail = pd.read_csv(base / "lower_tail_coexceedance_matrix.csv")
    numeric_tail = tail.drop(columns=["asset"]).apply(pd.to_numeric, errors="coerce")
    assert numeric_tail.notna().sum().sum() > 0

    regime = pd.read_csv(base / "regime_correlation_difference.csv")
    assert regime.drop(columns=["asset"]).notna().sum().sum() > 0


def test_macro_tables_preserve_same_support_and_mvrv_guardrail() -> None:
    base = RESEARCH / "02_macro_tradfi_integration" / "tables"
    block = pd.read_csv(base / "block_delta_r2.csv")
    assert block["same_support"].all()
    assert (block["n_full"] == block["n_reduced"]).all()
    assert (block["full_r2"] + 1e-10 >= block["reduced_r2"]).all()
    assert block["method_note"].str.contains("not conventional partial", case=False).all()

    for name in ["btc_ex_mvrv_feature_strength.csv", "eth_feature_strength.csv"]:
        frame = pd.read_csv(base / name)
        assert not frame["feature_id"].str.contains("mvrv", case=False, na=False).any()


def test_etf_lag_response_has_no_pre_inception_plot_rows() -> None:
    base = RESEARCH / "04_etf_institutional_flows" / "tables"
    lag = pd.read_csv(base / "etf_lag_response.csv")
    assert set(lag["asset"]) == {"BTC", "ETH"}
    assert set(lag["lag_days"]) == set(range(6))
    assert {"return_corr", "ci_low", "ci_high", "n", "sample_start", "sample_end"}.issubset(
        lag.columns
    )
    assert lag["n"].min() >= 50

    audit = pd.read_csv(base / "etf_pre_inception_plot_audit.csv")
    assert set(audit["asset"]) == {"BTC", "ETH"}
    assert (audit["pre_inception_plotted_observations"] == 0).all()
    assert (
        pd.to_datetime(audit["first_plotted_date"])
        >= pd.to_datetime(audit["first_valid_source_date"])
    ).all()

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "04_etf_lag_response.png" in readme
    assert "02_etf_market_plumbing.png" not in readme
    assert "cumulative-flow" not in readme.lower()


def test_no_standalone_concentration_or_basic_selected_scatter_remains() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "09_market_concentration_state" not in readme
    assert "market_concentration_state.png" not in readme
    assert "05_selected_major_asset_risk.png" not in readme

    selection = pd.read_csv(RESEARCH / "root_figure_selection.csv")
    selected = selection[selection["selected"].astype(str).str.lower().eq("true")]
    assert (
        not selected["figure_id"]
        .str.contains("concentration|mvrv|selected_major_asset_risk", case=False)
        .any()
    )

    pit_coeff = pd.read_csv(
        RESEARCH
        / "07_chain_fundamentals_sector_dynamics"
        / "tables"
        / "pit_state_relationship_coefficients.csv"
    )
    assert {"outcome", "feature", "coefficient", "ci_low", "ci_high"}.issubset(pit_coeff.columns)


def test_relative_asset_risk_uses_factor_and_downside_outputs() -> None:
    base = RESEARCH / "08_relative_asset_risk_factor_structure" / "tables"
    factor = pd.read_csv(base / "relative_factor_decomposition.csv")
    assert {"common_variance_share", "idiosyncratic_variance_share", "pc1_variance_share"}.issubset(
        factor.columns
    )
    assert set(factor["asset"]).issuperset({"BTC", "ETH", "SOL", "XRP", "DOGE", "HYPE"})
    np.testing.assert_allclose(
        factor["common_variance_share"] + factor["idiosyncratic_variance_share"],
        1.0,
        atol=1e-8,
    )

    downside = pd.read_csv(base / "downside_expected_shortfall.csv")
    assert {"expected_shortfall_5pct", "downside_beta_to_btc_tail"}.issubset(downside.columns)


def test_mvrv_identity_terms_and_liquidity_valuation_guardrails() -> None:
    points = pd.read_csv(
        RESEARCH / "06_onchain_valuation_holder_behavior" / "tables" / "mvrv_identity_points.csv"
    )
    residual = points["d_log_mvrv"] - (points["d_log_market_cap"] - points["d_log_realized_cap"])
    diff = (residual - points["identity_residual"]).dropna().abs()
    assert diff.max() < 1e-12

    audit = pd.read_csv(
        RESEARCH / "05_stablecoin_defi_liquidity" / "tables" / "valuation_contamination_audit.csv"
    )
    tvl = audit[audit["feature_id"].eq("valuation_sensitive_defi_tvl_growth")]
    assert set(tvl["asset"]) == {"BTC", "ETH"}
    assert tvl["mechanical_link_risk"].eq("high_usd_price_content").all()


def test_event_synthesis_uses_current_modules_and_demotes_bad_claims() -> None:
    base = RESEARCH / "09_event_stress_cross_module_synthesis" / "tables"
    ledger = pd.read_csv(base / "evidence_ledger.csv")
    assert set(ledger["module_id"]).issubset(set(EXPECTED_MODULES))
    assert "01_returns_risk_regimes" not in set(ledger["module_id"])

    inventory = pd.read_csv(base / "claim_inventory.csv")
    row = inventory.loc[
        inventory["claim"] == "Current-top50 daily returns are historical altseason evidence."
    ].iloc[0]
    assert row["disposition"] == "demote"
    assert "survivorship" in row["limitation"].lower()

    row = inventory.loc[inventory["claim"] == "ETF flows cause same-day crypto returns."].iloc[0]
    assert row["disposition"] == "demote"


def test_canonical_id_collision_handling_is_not_symbol_first() -> None:
    assert (
        classify_pit_asset(
            pd.Series(
                {
                    "symbol": "SOL",
                    "asset_name": "Wrapped SOL",
                    "coingecko_id": "coingecko:wrapped-sol",
                    "asset_key": "coingecko:wrapped-sol",
                }
            )
        )
        == "productized/wrapped assets"
    )
    assert (
        classify_pit_asset(
            pd.Series(
                {
                    "symbol": "GRAM",
                    "asset_name": "Toncoin",
                    "coingecko_id": "coingecko:the-open-network",
                    "asset_key": "coingecko:the-open-network",
                }
            )
        )
        == "selected majors ex BTC/ETH"
    )
    assert (
        classify_pit_asset(
            pd.Series(
                {
                    "symbol": "XRP",
                    "asset_name": "Binance-Peg XRP",
                    "coingecko_id": "coingecko:binance-peg-xrp",
                    "asset_key": "coingecko:binance-peg-xrp",
                }
            )
        )
        == "productized/wrapped assets"
    )


def test_package_metadata_ci_and_raw_data_policy() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert metadata["name"] == "crypto-market-dynamics"
    authors = " ".join(author["name"] for author in metadata["authors"])
    assert "Crypto Market Dynamics contributors" in authors

    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "uv run python scripts/check_research_surface.py --module all" in workflow
    assert "hashFiles('data_local/raw/**')" in workflow
    assert 'allowed_prefixes = ("research/",)' in workflow

    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            "data_local",
            "data_cache",
            "reports",
            "archive",
            "CryptoQuant",
            "Artemis",
            "Tradingview",
            "TradingView",
            "DefiLlama",
            "Farside ETF Data",
            "FRED",
            "AlternativeMe",
            "MarketStructure",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == ""
