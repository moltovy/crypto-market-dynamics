"""Unit tests for the new Feature Strength and Regime Analysis outputs."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"
FIGURES = OUTPUTS / "figures"


def test_tables_exist():
    """Verify that all new T11-T27 tables are generated and present in the outputs directory."""
    expected_tables = [
        "T11_results_at_a_glance.md",
        "T12_regime_definitions.csv",
        "T13_factor_dictionary.csv",
        "T13_factor_dictionary.md",
        "T14_feature_strength_btc_full.csv",
        "T15_feature_strength_btc_ex_mvrv.csv",
        "T16_feature_strength_eth.csv",
        "T17_feature_strength_by_regime.csv",
        "T18_block_strength_by_regime.csv",
        "T19_same_support_ablation_btc.csv",
        "T20_same_support_ablation_eth.csv",
        "T21_top_correlations_btc.csv",
        "T22_top_correlations_eth.csv",
        "T23_core_correlation_matrix.csv",
        "T24_pre_post_correlation_delta.csv",
        "T25_mvrv_sensitivity_by_regime.csv",
        "T26_etf_era_feature_strength.csv",
        "T27_rolling_feature_rank_stability.csv",
    ]
    for table in expected_tables:
        path = TABLES / table
        assert path.exists(), f"Missing table: {table}"


def test_t25_regimes_and_columns():
    """Verify that T25 contains the correct regimes and all expected columns."""
    t25_path = TABLES / "T25_mvrv_sensitivity_by_regime.csv"
    assert t25_path.exists()

    df = pd.read_csv(t25_path)

    # Check expected columns
    expected_cols = {
        "regime", "n", "full_with_mvrv_r2", "ex_mvrv_r2",
        "mvrv_only_r2", "delta_r2", "note"
    }
    assert expected_cols.issubset(df.columns), f"Missing columns in T25: {expected_cols - set(df.columns)}"

    # Check expected regimes
    expected_regimes = {
        "full", "pre_btc_etf", "post_btc_etf",
        "year_2024", "year_2025", "year_2026_ytd"
    }
    assert expected_regimes.issubset(df["regime"].values), f"Missing regimes in T25: {expected_regimes - set(df['regime'].values)}"


def test_feature_strength_metrics():
    """Verify that T14 and T15 contain the expected feature-strength diagnostic columns."""
    for table_name in ["T14_feature_strength_btc_full.csv", "T15_feature_strength_btc_ex_mvrv.csv"]:
        path = TABLES / table_name
        assert path.exists()
        df = pd.read_csv(path)

        expected_cols = {
            "feature", "block", "correlation", "abs_correlation",
            "univariate_beta", "univariate_hac_t", "univariate_r2",
            "standardized_multivar_beta", "multivar_hac_t", "multivar_p",
            "drop_one_delta_r2", "rank_by_abs_corr", "rank_by_abs_t", "rank_by_delta_r2"
        }
        assert expected_cols.issubset(df.columns), f"Missing columns in {table_name}: {expected_cols - set(df.columns)}"


def test_top_btc_correlations():
    """Verify that top correlations for BTC includes MVRV and is sorted descending."""
    path = TABLES / "T21_top_correlations_btc.csv"
    assert path.exists()

    df = pd.read_csv(path)
    assert "btc_mvrv_d1" in df["feature"].values

    # Check sorting of absolute correlations
    corrs = df["abs_correlation"].values
    assert all(corrs[i] >= corrs[i+1] for i in range(len(corrs)-1)), "T21 is not sorted descending by absolute correlation"


def test_readme_content():
    """Verify that the public README.md contains 'Results at a Glance', links new tables/figures, and avoids AI slop."""
    readme_path = ROOT / "README.md"
    assert readme_path.exists()
    content = readme_path.read_text(encoding="utf-8")

    # Check for core narrative section
    assert "Results at a Glance" in content, "README missing 'Results at a Glance'"

    # Check for some new figures/tables references
    assert "T11_results_at_a_glance.md" in content, "README missing reference to T11"
    assert "F01_mvrv_sensitivity_by_regime" in content, "README missing reference to F01"
    assert "F02_same_support_ablation" in content, "README missing reference to F02"

    # Check for legacy version strings (should be removed or updated)
    assert "v2.1" not in content, "README should not mention 'v2.1'"
    assert "v2.2" not in content, "README should not mention 'v2.2'"
    assert "v2.0" not in content, "README should not mention 'v2.0'"


def test_data_untouched():
    """Ensure raw Data/ remains untouched except allowed market-structure inventory outputs."""
    result = subprocess.run(
        ["git", "status", "--short", "--", "Data"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True
    )
    allowed = {
        "M Data/MASTER_DATA.csv",
        "M Data/MASTER_DATA.md",
        "?? Data/MarketStructure/",
    }
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    unexpected = changed - allowed
    assert not unexpected, f"Raw Data/ folder has unexpected modifications: {result.stdout}"
