"""Contract tests for the final semantic research outputs."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

import numpy as np
import pandas as pd

from cqresearch.pipelines.final_research import classify_pit_asset

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"

TABLE_MAP = {
    "asset_identity_audit.csv": "08_relative_major_asset_risk/tables/asset_identity_audit.csv",
    "asset_taxonomy.csv": "08_relative_major_asset_risk/tables/asset_taxonomy.csv",
    "block_delta_r2.csv": "02_macro_cross_asset_exposure/tables/block_delta_r2.csv",
    "btc_ex_mvrv_feature_strength.csv": "02_macro_cross_asset_exposure/tables/btc_ex_mvrv_feature_strength.csv",
    "claim_inventory.csv": "11_cross_module_synthesis/tables/claim_inventory.csv",
    "conventional_partial_r2.csv": "02_macro_cross_asset_exposure/tables/conventional_partial_r2.csv",
    "data_source_coverage.csv": "00_data_foundation/tables/provider_inventory.csv",
    "eth_feature_strength.csv": "02_macro_cross_asset_exposure/tables/eth_feature_strength.csv",
    "evidence_ledger.csv": "11_cross_module_synthesis/tables/evidence_ledger.csv",
    "evidence_map.md": "11_cross_module_synthesis/tables/evidence_map.md",
    "feature_registry.csv": "00_data_foundation/tables/feature_inventory.csv",
    "frequency_robustness.csv": "02_macro_cross_asset_exposure/tables/frequency_robustness.csv",
    "leverage_feature_registry.csv": "03_derivatives_leverage_liquidations/tables/leverage_feature_registry.csv",
    "leverage_tail_risk_summary.csv": "03_derivatives_leverage_liquidations/tables/leverage_tail_risk_summary.csv",
    "liquidity_associations.csv": "05_stablecoin_defi_liquidity/tables/liquidity_associations.csv",
    "local_window_correlation_distribution.csv": "02_macro_cross_asset_exposure/tables/local_window_correlation_distribution.csv",
    "mvrv_identity_points.csv": "06_onchain_valuation_holder_state/tables/mvrv_identity_points.csv",
    "mvrv_mechanical_link_audit.csv": "06_onchain_valuation_holder_state/tables/mvrv_mechanical_link_audit.csv",
    "pit_concentration.csv": "09_market_concentration_state/tables/pit_concentration.csv",
    "pit_market_structure_summary.csv": "09_market_concentration_state/tables/pit_market_structure_summary.csv",
    "pit_turnover.csv": "09_market_concentration_state/tables/pit_turnover.csv",
    "provider_data_disposition.csv": "00_data_foundation/tables/provider_inventory.csv",
    "rolling_tradfi_exposures.csv": "02_macro_cross_asset_exposure/tables/rolling_tradfi_exposures.csv",
    "selected_major_comparable_window_metrics.csv": "08_relative_major_asset_risk/tables/selected_major_comparable_window_metrics.csv",
    "selected_major_coverage.csv": "08_relative_major_asset_risk/tables/selected_major_coverage.csv",
    "selected_major_risk_metrics.csv": "08_relative_major_asset_risk/tables/selected_major_risk_metrics.csv",
    "stablecoin_defi_liquidity_summary.csv": "05_stablecoin_defi_liquidity/tables/stablecoin_defi_liquidity_summary.csv",
    "stablecoin_liquidity_features.csv": "05_stablecoin_defi_liquidity/tables/stablecoin_liquidity_features.csv",
    "tail_risk_models.csv": "03_derivatives_leverage_liquidations/tables/tail_risk_models.csv",
    "valuation_contamination_audit.csv": "05_stablecoin_defi_liquidity/tables/valuation_contamination_audit.csv",
    "event_inference.csv": "10_event_sensitivity/tables/event_inference.csv",
    "event_response_matrix.csv": "10_event_sensitivity/tables/event_response_matrix.csv",
}


class ResearchTables:
    def __truediv__(self, name: str) -> Path:
        return RESEARCH / TABLE_MAP[name]


TABLES = ResearchTables()


def test_semantic_tables_exist() -> None:
    expected_tables = [
        "asset_identity_audit.csv",
        "asset_taxonomy.csv",
        "block_delta_r2.csv",
        "btc_ex_mvrv_feature_strength.csv",
        "claim_inventory.csv",
        "conventional_partial_r2.csv",
        "data_source_coverage.csv",
        "eth_feature_strength.csv",
        "evidence_ledger.csv",
        "feature_registry.csv",
        "local_window_correlation_distribution.csv",
        "mvrv_mechanical_link_audit.csv",
        "pit_concentration.csv",
        "pit_market_structure_summary.csv",
        "provider_data_disposition.csv",
        "rolling_tradfi_exposures.csv",
        "selected_major_coverage.csv",
        "selected_major_comparable_window_metrics.csv",
        "selected_major_risk_metrics.csv",
        "stablecoin_defi_liquidity_summary.csv",
        "valuation_contamination_audit.csv",
    ]
    missing = [name for name in expected_tables if not (TABLES / name).exists()]
    assert not missing


def test_primary_feature_strength_tables_exclude_same_day_mvrv() -> None:
    for table_name in ["btc_ex_mvrv_feature_strength.csv", "eth_feature_strength.csv"]:
        frame = pd.read_csv(TABLES / table_name)
        assert not frame["feature_id"].str.contains("mvrv", case=False, na=False).any()
        assert {
            "long_sample_contemporaneous_exposure",
            "long_sample_lagged_state_association",
            "etf_era_augmented",
        }.issubset(set(frame["model_family"]))

    mvrv = pd.read_csv(TABLES / "mvrv_mechanical_link_audit.csv")
    assert "same_day_mvrv_r2_diagnostic" in set(mvrv["metric"])
    row = mvrv.loc[mvrv["metric"] == "same_day_mvrv_r2_diagnostic"].iloc[0]
    assert "excluded from primary exposure model" in row["interpretation"]


def test_drop_block_delta_r2_is_not_labeled_partial_r2() -> None:
    block = pd.read_csv(TABLES / "block_delta_r2.csv")
    assert "drop_block_delta_r2" in block.columns
    assert not any("partial" in column.lower() for column in block.columns)
    assert block["method_note"].str.contains("not conventional partial", case=False).all()
    assert block["same_support"].all()
    assert (block["n_full"] == block["n_reduced"]).all()
    assert (block["full_r2"] + 1e-10 >= block["reduced_r2"]).all()
    assert (block["drop_block_delta_r2"] >= -1e-10).all()
    assert {"calendar", "calendar_assumption", "close_time_assumption"}.issubset(block.columns)

    conventional = pd.read_csv(TABLES / "conventional_partial_r2.csv")
    assert "conventional_partial_r2" in conventional.columns
    assert conventional["formula"].str.contains("SSE_reduced").all()
    assert conventional["same_support"].all()
    assert (conventional["n_full"] == conventional["n_reduced"]).all()
    assert (
        (conventional["conventional_partial_r2"] >= -1e-10)
        & (conventional["conventional_partial_r2"] <= 1 + 1e-10)
    ).all()


def test_tradfi_models_use_synchronized_business_and_friday_calendars() -> None:
    block = pd.read_csv(TABLES / "block_delta_r2.csv")
    daily = block[
        block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["frequency"].eq("daily")
    ]
    weekly = block[
        block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["frequency"].eq("weekly")
    ]
    assert set(daily["calendar"]) == {"tradfi_business_daily"}
    assert set(weekly["calendar"]) == {"tradfi_friday_weekly"}
    assert (
        daily["calendar_assumption"]
        .str.contains("consecutive common TradFi business-date", regex=False)
        .all()
    )

    etf = block[block["model_family"].eq("etf_era_augmented")]
    assert {"etf_trading_daily", "etf_friday_weekly"}.issubset(set(etf["calendar"]))

    rolling = pd.read_csv(TABLES / "rolling_tradfi_exposures.csv")
    assert set(rolling["calendar"]) == {"tradfi_business_daily"}
    assert {180, 365} == set(rolling["window_days"])


def test_weekly_models_have_valid_samples_and_transformations() -> None:
    frequency = pd.read_csv(TABLES / "frequency_robustness.csv")
    weekly_passed = frequency[
        (frequency["frequency"] == "weekly") & (frequency["status"] == "passed")
    ]
    assert not weekly_passed.empty
    assert (weekly_passed["n"] > 0).all()
    long_weekly = weekly_passed[weekly_passed["model_family"] != "etf_era_augmented"]
    assert (long_weekly["n"] >= 100).all()

    # CI runs the canonical build before pytest, so these checks validate fresh artifacts.
    liquidity = pd.read_csv(TABLES / "stablecoin_liquidity_features.csv", parse_dates=["date"])
    assert liquidity["date"].is_monotonic_increasing
    assert set(liquidity["date"].dt.dayofweek.dropna().unique()) <= {6}
    recomputed_stable_growth = np.log(
        liquidity["stablecoin_supply_usd"].where(liquidity["stablecoin_supply_usd"] > 0)
    ).diff()
    np.testing.assert_allclose(
        liquidity["stablecoin_supply_growth"].to_numpy(),
        recomputed_stable_growth.to_numpy(),
        equal_nan=True,
        atol=1e-12,
    )
    assert "valuation_sensitive_defi_tvl_growth" in liquidity.columns
    assert set(liquidity["calendar"].dropna()) == {"crypto_week_sunday"}


def test_valuation_contamination_audit_and_oi_scaling() -> None:
    audit = pd.read_csv(TABLES / "valuation_contamination_audit.csv")
    tvl = audit[audit["feature_id"].eq("valuation_sensitive_defi_tvl_growth")]
    assert set(tvl["asset"]) == {"BTC", "ETH"}
    assert tvl["mechanical_link_risk"].eq("high_usd_price_content").all()
    assert tvl["unit_disposition"].str.contains("USD TVL embeds asset-price effects").all()

    feature_registry = pd.read_csv(TABLES / "feature_registry.csv")
    required_features = {
        "valuation_sensitive_defi_tvl_growth",
        "valuation_sensitive_defi_tvl_growth_lag1",
        "btc_oi_to_mcap_growth_lag1",
        "eth_oi_to_mcap_growth_lag1",
    }
    assert required_features.issubset(set(feature_registry["feature_id"]))
    assert "valuation_contamination_risk" in feature_registry.columns
    tvl_registry = feature_registry[
        feature_registry["feature_id"].eq("valuation_sensitive_defi_tvl_growth")
    ]
    assert tvl_registry["valuation_contamination_risk"].eq("high_usd_price_content").all()


def test_mvrv_identity_terms_are_same_interval_and_scaled() -> None:
    # See note above: committed output CSVs keep this test independent of generated parquet panels.
    points = pd.read_csv(TABLES / "mvrv_identity_points.csv")
    residual = points["d_log_mvrv"] - (points["d_log_market_cap"] - points["d_log_realized_cap"])
    diff = (residual - points["identity_residual"]).dropna().abs()
    assert diff.max() < 1e-12

    audit = pd.read_csv(TABLES / "mvrv_mechanical_link_audit.csv")
    required = {
        "corr_btc_return_d_log_mvrv",
        "same_day_mvrv_r2_diagnostic",
        "identity_residual_mean",
        "identity_residual_abs_median",
        "identity_residual_abs_median_to_median_abs_btc_return",
        "identity_residual_q01",
        "identity_residual_q99",
    }
    assert required.issubset(set(audit["metric"]))


def test_pit_market_structure_is_point_in_time_and_state_based() -> None:
    summary = pd.read_csv(TABLES / "pit_market_structure_summary.csv")
    assert {"top10_share", "hhi", "rank_persistence", "snapshot_date", "is_partial_month"}.issubset(
        summary.columns
    )
    latest = summary.sort_values("snapshot_date").iloc[-1]
    assert latest["snapshot_date"] == "2026-06-16"
    assert latest["month"] == "2026-06"
    assert bool(latest["is_partial_month"])

    turnover = pd.read_csv(TABLES / "pit_turnover.csv")
    assert {"entries", "exits", "rank_persistence"}.issubset(turnover.columns)
    concentration = pd.read_csv(TABLES / "pit_concentration.csv")
    assert {"top5_share", "top10_share", "hhi", "clean_risk_count"}.issubset(concentration.columns)


def test_selected_major_identity_and_coverage_caveats() -> None:
    audit = pd.read_csv(TABLES / "asset_identity_audit.csv")
    checks = set(audit["check_id"])
    assert {
        "toncoin_not_tokamak",
        "sol_not_wrapped_sol",
        "xrp_not_binance_peg_xrp",
        "doge_not_binance_peg_doge",
    }.issubset(checks)
    assert (audit.loc[audit["check_id"] == "toncoin_not_tokamak", "status"] == "pass").all()

    coverage = pd.read_csv(TABLES / "selected_major_coverage.csv")
    ton = coverage.loc[coverage["symbol"] == "TON"].iloc[0]
    assert int(ton["observations"]) > 0
    assert ton["source_symbols"] == "GRAM"
    assert "canonical coingecko_id" in ton["coverage_note"]

    risk = pd.read_csv(TABLES / "selected_major_risk_metrics.csv")
    assert risk.loc[risk["symbol"] == "TON", "status"].iloc[0] == "computed"

    comparable = pd.read_csv(TABLES / "selected_major_comparable_window_metrics.csv")
    assert set(coverage["symbol"]) == set(comparable["symbol"])
    assert comparable["common_start"].nunique() == 1
    assert comparable["common_end"].nunique() == 1


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
                    "symbol": "TON",
                    "asset_name": "Tokamak Network",
                    "coingecko_id": "coingecko:tokamak-network",
                    "asset_key": "coingecko:tokamak-network",
                }
            )
        )
        != "selected majors ex BTC/ETH"
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
    assert (
        classify_pit_asset(
            pd.Series(
                {
                    "symbol": "LDO",
                    "asset_name": "Lido DAO",
                    "coingecko_id": "coingecko:lido-dao",
                    "asset_key": "coingecko:lido-dao",
                }
            )
        )
        == "governance/infrastructure risk assets"
    )

    audit = pd.read_csv(TABLES / "asset_identity_audit.csv")
    assert "failing_rows" in audit.columns
    assert pd.api.types.is_numeric_dtype(audit["failing_rows"])
    assert (audit["failing_rows"] == 0).all()


def test_liquidation_ratio_units_and_event_windows() -> None:
    registry = pd.read_csv(TABLES / "leverage_feature_registry.csv")
    liquidation_rows = registry[registry["feature_id"].str.contains("liq", na=False)]
    assert not liquidation_rows.empty
    assert (
        liquidation_rows["scaling"]
        .str.contains("percent|basis points", case=False, regex=True)
        .all()
    )
    assert not liquidation_rows["scaling"].str.contains("log1p /", regex=False).any()

    events = pd.read_csv(TABLES / "event_inference.csv")
    assert (events["actual_observations"] == events["block_size"]).all()
    assert (events["block_size"] == 10).all()
    assert events["method"].str.contains("empirical_placebo_window_test").all()
    assert events["event_window_convention"].eq("+1 through +10, excluding event day").all()

    response = pd.read_csv(TABLES / "event_response_matrix.csv")
    assert (response["actual_observations"] == 10).all()


def test_public_figure_2_uses_pre_specified_periods_and_event_missing_not_zero_filled() -> None:
    block = pd.read_csv(TABLES / "block_delta_r2.csv")
    subset = block[
        block["frequency"].eq("daily")
        & block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["block"].eq("equity_beta")
        & block["regime"].isin(["pre_btc_etf", "btc_etf_era"])
        & block["asset"].isin(["BTC", "ETH"])
    ]
    assert set(subset["regime"]) == {"pre_btc_etf", "btc_etf_era"}
    assert set(subset["asset"]) == {"BTC", "ETH"}

    source = (ROOT / "src" / "cqresearch" / "viz" / "public_figures.py").read_text(encoding="utf-8")
    fig_event_source = source.split("def fig_event_gallery", 1)[1].split("def contact_sheet", 1)[0]
    assert ".fillna(0)" not in fig_event_source
    assert "masked_invalid" in fig_event_source


def test_headline_readme_numbers_match_generated_evidence_map() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    evidence_map = (TABLES / "evidence_map.md").read_text(encoding="utf-8").strip()
    assert "Same-day MVRV is a measurement warning" in readme
    assert "research/11_cross_module_synthesis/tables/evidence_ledger.csv" in readme
    assert "09_market_concentration_state" in evidence_map
    assert "Results At A Glance" not in readme
    assert "See block_delta_r2.csv" not in readme
    assert "See leverage_tail_risk_summary.csv" not in readme
    assert "volatility and concentration" not in readme.lower()
    assert "event response?" not in readme.lower()
    assert "2026-06-01" not in readme
    assert "outputs/" not in readme


def test_provider_data_disposition_has_release_risk_categories() -> None:
    disposition = pd.read_csv(TABLES / "provider_data_disposition.csv")
    assert {
        "public/re-distributable",
        "uncertain/restricted",
        "derived-only recommended",
    }.issubset(set(disposition["disposition"]))


def test_claim_inventory_demotes_current_top50_daily_returns() -> None:
    claims = pd.read_csv(TABLES / "claim_inventory.csv")
    row = claims.loc[
        claims["claim"] == "Current-top50 daily returns are historical altseason evidence."
    ].iloc[0]
    assert row["disposition"] == "demote"
    assert "PIT monthly" in row["replacement"]


def test_readme_content_matches_final_surface() -> None:
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Crypto Market Dynamics" in content
    assert "MVRV remains a valuation-state diagnostic" in content
    assert "research/02_macro_cross_asset_exposure/figures/01_tradfi_exposure_shift.png" in content
    assert (
        "research/08_relative_major_asset_risk/figures/05_selected_major_asset_risk.png" in content
    )
    assert (
        "research/09_market_concentration_state/figures/market_concentration_state.png" in content
    )
    assert "04_point_in_time_market_structure" not in content
    assert "pit_composition" not in content
    assert "public_contact_sheet" not in content
    assert "archive/" not in content
    assert "local under `data_local/raw/`" in content
    assert "data_local/raw" in content
    assert "research/02_macro_cross_asset_exposure/tables/block_delta_r2.csv" in content
    assert "research/11_cross_module_synthesis/tables/evidence_ledger.csv" in content
    assert "research/05_stablecoin_defi_liquidity" in content
    assert "outputs/" not in content
    assert "not affiliated" in content
    assert "v2.0" not in content
    assert "v2.1" not in content
    assert "v2.2" not in content


def test_research_modules_are_consolidated_and_claims_are_specific() -> None:
    assert (RESEARCH / "README.md").exists()
    assert (RESEARCH / "manifest.json").exists()
    assert (RESEARCH / "figure_specs.csv").exists()

    module_dirs = sorted(path for path in RESEARCH.iterdir() if path.is_dir())
    assert len(module_dirs) == 12
    for module_dir in module_dirs:
        for name in [
            "README.md",
            "methodology.md",
            "findings.md",
            "interpretation.md",
            "limitations.md",
            "module.yml",
            "manifest.json",
        ]:
            assert (module_dir / name).exists(), f"{module_dir.name} missing {name}"
        claims = pd.read_csv(module_dir / "tables" / "claims.csv")
        assert not claims.empty
        assert "claim_text" in claims.columns
        assert "source_model_ids" in claims.columns
        assert not claims["claim_text"].str.contains("See `outputs/tables/`", regex=False).any()


def test_package_metadata_has_project_name_and_no_provider_affiliation() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert metadata["name"] == "crypto-market-dynamics"
    authors = " ".join(author["name"] for author in metadata["authors"])
    assert "CryptoQuant Research Team" not in authors
    assert "Crypto Market Dynamics contributors" in authors


def test_ci_keeps_public_checks_and_optional_local_data_build() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    pytest_idx = workflow.index("uv run pytest")
    surface_idx = workflow.index("uv run python scripts/check_research_surface.py --module all")
    assert pytest_idx < surface_idx
    assert "uv run ruff format --check src/cqresearch scripts tests" in workflow
    assert "Canonical offline build when local provider data is available" in workflow
    assert "hashFiles('data_local/raw/**')" in workflow
    assert "Data/**" not in workflow
    assert "Generated artifact diff gate when local provider data is available" in workflow
    assert 'allowed_prefixes = ("research/",)' in workflow


def test_raw_data_and_panels_are_not_tracked() -> None:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            "Data",
            "data_local",
            "data_cache",
            "reports",
            "archive",
            "references",
            "CryptoQuant",
            "Artemis",
            "Tradingview",
            "TradingView",
            "DefiLlama",
            "Defi",
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
