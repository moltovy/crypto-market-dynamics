"""Contract tests for the final semantic research outputs."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from cqresearch.pipelines.final_research import classify_pit_asset

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"


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
        "pit_composition.csv",
        "pit_market_structure_summary.csv",
        "provider_data_disposition.csv",
        "rolling_tradfi_exposures.csv",
        "selected_major_coverage.csv",
        "selected_major_comparable_window_metrics.csv",
        "selected_major_risk_metrics.csv",
        "stablecoin_defi_liquidity_summary.csv",
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

    conventional = pd.read_csv(TABLES / "conventional_partial_r2.csv")
    assert "conventional_partial_r2" in conventional.columns
    assert conventional["formula"].str.contains("SSE_reduced").all()
    assert conventional["same_support"].all()
    assert (conventional["n_full"] == conventional["n_reduced"]).all()
    assert ((conventional["conventional_partial_r2"] >= -1e-10) & (conventional["conventional_partial_r2"] <= 1 + 1e-10)).all()


def test_weekly_models_have_valid_samples_and_transformations() -> None:
    frequency = pd.read_csv(TABLES / "frequency_robustness.csv")
    weekly_passed = frequency[(frequency["frequency"] == "weekly") & (frequency["status"] == "passed")]
    assert not weekly_passed.empty
    assert (weekly_passed["n"] > 0).all()
    long_weekly = weekly_passed[weekly_passed["model_family"] != "etf_era_augmented"]
    assert (long_weekly["n"] >= 100).all()

    # CI runs pytest before the canonical build step, so these checks use committed output CSVs.
    liquidity = pd.read_csv(TABLES / "stablecoin_liquidity_features.csv", parse_dates=["date"])
    assert liquidity["date"].is_monotonic_increasing
    assert set(liquidity["date"].dt.dayofweek.dropna().unique()) <= {6}
    recomputed_stable_growth = np.log(liquidity["stablecoin_supply_usd"].where(liquidity["stablecoin_supply_usd"] > 0)).diff()
    np.testing.assert_allclose(
        liquidity["stablecoin_supply_growth"].to_numpy(),
        recomputed_stable_growth.to_numpy(),
        equal_nan=True,
        atol=1e-12,
    )


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


def test_pit_composition_is_point_in_time_and_sums_to_one() -> None:
    composition = pd.read_csv(TABLES / "pit_composition.csv")
    monthly_share = composition.groupby("month")["share"].sum()
    assert ((monthly_share - 1).abs() < 1e-9).all()

    summary = pd.read_csv(TABLES / "pit_market_structure_summary.csv")
    assert {"top10_share", "hhi", "rank_persistence"}.issubset(summary.columns)

    turnover = pd.read_csv(TABLES / "pit_turnover.csv")
    assert {"entries", "exits", "rank_persistence"}.issubset(turnover.columns)


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
    assert classify_pit_asset(pd.Series({"symbol": "SOL", "asset_name": "Wrapped SOL", "coingecko_id": "coingecko:wrapped-sol", "asset_key": "coingecko:wrapped-sol"})) == "productized/wrapped assets"
    assert classify_pit_asset(pd.Series({"symbol": "TON", "asset_name": "Tokamak Network", "coingecko_id": "coingecko:tokamak-network", "asset_key": "coingecko:tokamak-network"})) != "selected majors ex BTC/ETH"
    assert classify_pit_asset(pd.Series({"symbol": "GRAM", "asset_name": "Toncoin", "coingecko_id": "coingecko:the-open-network", "asset_key": "coingecko:the-open-network"})) == "selected majors ex BTC/ETH"
    assert classify_pit_asset(pd.Series({"symbol": "XRP", "asset_name": "Binance-Peg XRP", "coingecko_id": "coingecko:binance-peg-xrp", "asset_key": "coingecko:binance-peg-xrp"})) == "productized/wrapped assets"
    assert classify_pit_asset(pd.Series({"symbol": "LDO", "asset_name": "Lido DAO", "coingecko_id": "coingecko:lido-dao", "asset_key": "coingecko:lido-dao"})) == "governance/infrastructure risk assets"

    audit = pd.read_csv(TABLES / "asset_identity_audit.csv")
    assert "failing_rows" in audit.columns
    assert pd.api.types.is_numeric_dtype(audit["failing_rows"])
    assert (audit["failing_rows"] == 0).all()


def test_liquidation_ratio_units_and_event_windows() -> None:
    registry = pd.read_csv(TABLES / "leverage_feature_registry.csv")
    liquidation_rows = registry[registry["feature_id"].str.contains("liq", na=False)]
    assert not liquidation_rows.empty
    assert liquidation_rows["scaling"].str.contains("percent|basis points", case=False, regex=True).all()
    assert not liquidation_rows["scaling"].str.contains("log1p /", regex=False).any()

    events = pd.read_csv(TABLES / "event_inference.csv")
    assert (events["actual_observations"] == events["block_size"]).all()
    assert (events["block_size"] == 10).all()
    assert events["method"].str.contains("empirical_placebo_window_test").all()
    assert events["event_window_convention"].eq("+1 through +10, excluding event day").all()

    response = pd.read_csv(TABLES / "event_response_matrix.csv")
    assert (response["actual_observations"] == 10).all()


def test_public_figure_2_has_multiple_regimes_and_event_missing_not_zero_filled() -> None:
    block = pd.read_csv(TABLES / "block_delta_r2.csv")
    subset = block[
        block["frequency"].eq("daily")
        & block["model_family"].eq("long_sample_contemporaneous_exposure")
    ]
    assert subset["regime"].nunique() >= 3

    source = (ROOT / "src" / "cqresearch" / "pipelines" / "final_research.py").read_text(encoding="utf-8")
    fig_event_source = source.split("def fig_event", 1)[1].split("def contact_sheet", 1)[0]
    assert ".fillna(0)" not in fig_event_source
    assert "masked_invalid" in fig_event_source


def test_headline_readme_numbers_match_generated_glance() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    glance = (TABLES / "results_at_a_glance.md").read_text(encoding="utf-8").strip()
    assert glance in readme
    assert "See block_delta_r2.csv" not in readme
    assert "See leverage_tail_risk_summary.csv" not in readme


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
    assert "MVRV is a valuation-state diagnostic" in content
    assert "outputs/figures/public/01_mvrv_mechanics.png" in content
    assert "outputs/tables/block_delta_r2.csv" in content
    assert "outputs/tables/claim_inventory.csv" in content
    assert "v2.0" not in content
    assert "v2.1" not in content
    assert "v2.2" not in content


def test_raw_data_changes_are_limited_to_generated_inventory() -> None:
    result = subprocess.run(
        ["git", "status", "--short", "--", "Data"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    allowed = {"Data/MASTER_DATA.csv", "Data/MASTER_DATA.md", "Data/MASTER_DATA.txt"}
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    changed_paths = {line[3:].strip() for line in changed}
    assert changed_paths <= allowed, result.stdout
