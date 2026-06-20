"""Contract tests for the final semantic research outputs."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"


def test_semantic_tables_exist() -> None:
    expected_tables = [
        "asset_identity_audit.csv",
        "asset_taxonomy.csv",
        "block_delta_r2.csv",
        "bootstrap_robustness.csv",
        "btc_ex_mvrv_feature_strength.csv",
        "claim_inventory.csv",
        "conventional_partial_r2.csv",
        "data_source_coverage.csv",
        "eth_feature_strength.csv",
        "evidence_ledger.csv",
        "feature_registry.csv",
        "mvrv_mechanical_link_audit.csv",
        "pit_composition.csv",
        "pit_market_structure_summary.csv",
        "selected_major_coverage.csv",
        "selected_major_risk_metrics.csv",
        "stablecoin_defi_liquidity_summary.csv",
    ]
    missing = [name for name in expected_tables if not (TABLES / name).exists()]
    assert not missing


def test_primary_feature_strength_tables_exclude_same_day_mvrv() -> None:
    for table_name in ["btc_ex_mvrv_feature_strength.csv", "eth_feature_strength.csv"]:
        frame = pd.read_csv(TABLES / table_name)
        assert not frame["feature_id"].str.contains("mvrv", case=False, na=False).any()
        assert set(frame["model_family"]) == {"ex_mvrv_primary_exposure"}

    mvrv = pd.read_csv(TABLES / "mvrv_mechanical_link_audit.csv")
    assert "same_day_mvrv_r2" in set(mvrv["metric"])
    row = mvrv.loc[mvrv["metric"] == "same_day_mvrv_r2"].iloc[0]
    assert "excluded from primary exposure model" in row["interpretation"]


def test_drop_block_delta_r2_is_not_labeled_partial_r2() -> None:
    block = pd.read_csv(TABLES / "block_delta_r2.csv")
    assert "drop_block_delta_r2" in block.columns
    assert not any("partial" in column.lower() for column in block.columns)
    assert block["method_note"].str.contains("not conventional partial", case=False).all()

    conventional = pd.read_csv(TABLES / "conventional_partial_r2.csv")
    assert "conventional_partial_r2" in conventional.columns
    assert conventional["formula"].str.contains("SSE_reduced").all()


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
    assert int(ton["observations"]) == 0
    assert "not present in the current daily constituent source" in ton["coverage_note"]

    risk = pd.read_csv(TABLES / "selected_major_risk_metrics.csv")
    assert risk.loc[risk["symbol"] == "TON", "status"].iloc[0] == "skipped_insufficient_data"


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
