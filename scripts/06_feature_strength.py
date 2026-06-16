"""Generate feature-strength, regime, and ablation tables T11–T27.

Reads the frozen daily panel, builds features, applies regime masks, and
produces the statistical tables that the Instructions.md identifies as missing.

Usage:
    uv run python scripts/06_feature_strength.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.feature_strength import (  # noqa: E402
    BLOCK_MAP,
    build_factor_dictionary,
    compute_block_strength,
    compute_core_correlation_matrix,
    compute_feature_strength,
    compute_pre_post_correlation_delta,
    compute_rolling_feature_rank,
    compute_same_support_ablation,
)
from cqresearch.analysis.regimes import (  # noqa: E402
    BTC_ETF_DATE,
    get_all_regimes,
    regimes_to_dataframe,
)
from cqresearch.features.panel import build_feature_panel  # noqa: E402
from cqresearch.features.returns import winsorize  # noqa: E402
from config.paths import PANELS_DIR  # noqa: E402

OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

# ── Block definitions (same as in 02_run_analyses.py / ablation.py) ──────────

MACRO = ["DGS10_d1", "DGS2_d1", "VIXCLS_d1", "DTWEXBGS_d1", "DFF_d1"]
TRADFI = ["spy_ret", "qqq_ret", "gld_ret"]
LIQUIDITY = ["defi_tvl_usd_ret", "stables_total_usd_ret"]
SENT = ["fng_value_d1"]
BTC_NATIVE_EX_MVRV = [
    "cme_btc_basis_close_d1",
    "btc_exchange_netflow_d1",
    "btc_miner_to_exchange_flow_d1",
]
BTC_MVRV = ["btc_mvrv_d1"]
ETH_NATIVE = ["cme_eth_basis_close_d1"]
BTC_ETF = ["btc_etf_intensity"]
ETH_ETF = ["eth_etf_intensity"]

BTC_FULL_FEATURES = MACRO + TRADFI + LIQUIDITY + SENT + BTC_NATIVE_EX_MVRV + BTC_MVRV
BTC_EX_MVRV_FEATURES = MACRO + TRADFI + LIQUIDITY + SENT + BTC_NATIVE_EX_MVRV
ETH_FULL_FEATURES = MACRO + TRADFI + LIQUIDITY + SENT + ETH_NATIVE

BTC_BLOCKS = {
    "Macro": MACRO,
    "TradFi": TRADFI,
    "Liquidity": LIQUIDITY,
    "Sentiment": SENT,
    "BTC Native ex MVRV": BTC_NATIVE_EX_MVRV,
    "BTC MVRV": BTC_MVRV,
}

ETH_BLOCKS = {
    "Macro": MACRO,
    "TradFi": TRADFI,
    "Liquidity": LIQUIDITY,
    "Sentiment": SENT,
    "ETH Native": ETH_NATIVE,
}

# Same-support ablation specs
BTC_ABLATION_SPECS = [
    ("M0_intercept", []),
    ("M1_macro", MACRO),
    ("M2_macro_tradfi", MACRO + TRADFI),
    ("M3_macro_tradfi_liquidity", MACRO + TRADFI + LIQUIDITY),
    ("M4_plus_sentiment", MACRO + TRADFI + LIQUIDITY + SENT),
    ("M5_plus_native_ex_mvrv", MACRO + TRADFI + LIQUIDITY + SENT + BTC_NATIVE_EX_MVRV),
    ("M6_plus_mvrv", MACRO + TRADFI + LIQUIDITY + SENT + BTC_NATIVE_EX_MVRV + BTC_MVRV),
    ("M7_mvrv_only", BTC_MVRV),
    ("M8_native_ex_mvrv_only", BTC_NATIVE_EX_MVRV),
]

ETH_ABLATION_SPECS = [
    ("M0_intercept", []),
    ("M1_macro", MACRO),
    ("M2_macro_tradfi", MACRO + TRADFI),
    ("M3_macro_tradfi_liquidity", MACRO + TRADFI + LIQUIDITY),
    ("M4_plus_sentiment", MACRO + TRADFI + LIQUIDITY + SENT),
    ("M5_plus_eth_native", MACRO + TRADFI + LIQUIDITY + SENT + ETH_NATIVE),
]

# Core features for correlation matrix
CORE_FEATURES = [
    "btc_ret", "eth_ret", "spy_ret", "qqq_ret", "gld_ret",
    "VIXCLS_d1", "DGS10_d1", "DTWEXBGS_d1",
    "stables_total_usd_ret", "defi_tvl_usd_ret",
    "btc_mvrv_d1",
    "cme_btc_basis_close_d1", "btc_exchange_netflow_d1",
    "fng_value_d1",
]

# Correlation pairs for pre/post delta
CORR_PAIRS = [
    ("btc_ret", "eth_ret"),
    ("btc_ret", "spy_ret"),
    ("btc_ret", "qqq_ret"),
    ("btc_ret", "gld_ret"),
    ("btc_ret", "VIXCLS_d1"),
    ("btc_ret", "DGS10_d1"),
    ("btc_ret", "btc_mvrv_d1"),
    ("btc_ret", "stables_total_usd_ret"),
    ("btc_ret", "defi_tvl_usd_ret"),
    ("eth_ret", "spy_ret"),
    ("eth_ret", "VIXCLS_d1"),
    ("eth_ret", "stables_total_usd_ret"),
]

# Key regimes for MVRV sensitivity
MVRV_REGIMES = [
    "full", "pre_btc_etf", "post_btc_etf",
    "year_2024", "year_2025", "year_2026_ytd",
]


def load_features() -> pd.DataFrame:
    """Load and winsorize the feature panel."""
    panel = pd.read_parquet(PANELS_DIR / "master_daily.parquet")
    feat = build_feature_panel(panel)
    for c in feat.columns:
        if feat[c].dtype.kind in "fc":
            feat[c] = winsorize(feat[c], q=0.01)
    return feat


def _write(df: pd.DataFrame, name: str) -> Path:
    path = TABLES / name
    df.to_csv(path, index="date" in df.columns or isinstance(df.index, pd.DatetimeIndex))
    print(f"  [ok] {name} ({len(df)} rows)")
    return path


def _write_md(text: str, name: str) -> Path:
    path = TABLES / name
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"  [ok] {name}")
    return path


def main() -> int:
    feat = load_features()
    print(f"Feature panel: {feat.shape[0]} rows × {feat.shape[1]} cols")

    # Get regimes
    btc_ret = feat.get("btc_ret")
    regimes = get_all_regimes(feat.index, btc_ret)
    regime_lookup = {r.name: r for r in regimes}

    # ── T11: Results at a Glance ─────────────────────────────────────────
    print("\n=== T11: Results at a Glance ===")
    # Gather key numbers from existing tables
    t03 = pd.read_csv(TABLES / "T03_block_attribution.csv")
    btc_full = t03[(t03["asset"] == "btc") & (t03["sample"] == "full")]
    full_r2 = btc_full.iloc[0]["full_r2"]
    mvrv_row = btc_full[btc_full["block"] == "BTC MVRV"].iloc[0]
    without_mvrv_r2 = mvrv_row["reduced_r2"]
    mvrv_delta_r2 = mvrv_row["partial_r2"]

    t07 = pd.read_csv(TABLES / "T07_native_factor_ablation.csv")
    mvrv_only_r2 = t07[t07["model_id"] == "N2_mvrv_only"].iloc[0]["r2"]
    native_ex_mvrv_r2 = t07[t07["model_id"] == "N1_native_ex_mvrv"].iloc[0]["r2"]

    t07_corr = pd.read_csv(TABLES / "T07_btc_native_correlations.csv")
    mvrv_corr = float(t07_corr.set_index("feature").loc["btc_mvrv_d1", "btc_ret"])

    t04 = pd.read_csv(TABLES / "T04_etf_lead_lag.csv")
    btc_lag0 = t04[
        (t04["asset"] == "btc")
        & (t04["target"] == "btc_ret")
        & (t04["lag"] == 0)
    ].iloc[0]
    etf_t_lag0 = btc_lag0["t"]

    t08 = pd.read_csv(TABLES / "T08_structural_breaks.csv")
    btc_chow_p = t08[t08["asset"] == "btc"].iloc[0]["chow_p"]

    t09_roll = pd.read_csv(TABLES / "T09_rolling_connectedness.csv")
    mean_conn = t09_roll["connectedness_pct"].mean()

    glance_md = f"""# Results at a Glance

| Diagnostic | Value | Source |
|---|---:|---|
| BTC full-model R² | {full_r2:.3f} | T03 |
| BTC R² without MVRV | {without_mvrv_r2:.3f} | T03 |
| BTC MVRV ΔR² (block removal) | {mvrv_delta_r2:.3f} | T03 |
| BTC MVRV-only standalone R² | {mvrv_only_r2:.3f} | T07 |
| BTC native-ex-MVRV standalone R² | {native_ex_mvrv_r2:.4f} | T07 |
| BTC–MVRV correlation | {mvrv_corr:.3f} | T07 |
| ETF-flow lag 0 HAC t-stat | {etf_t_lag0:.2f} | T04 |
| BTC Chow test p-value (ETF date) | {btc_chow_p:.4f} | T08 |
| Mean VAR connectedness index | {mean_conn:.1f}% | T09 |

The strongest empirical result is that BTC daily-return models are extremely
sensitive to MVRV-style valuation state. In the current daily linear setup,
`btc_mvrv_d1` has correlation ≈ {mvrv_corr:.3f} with `btc_ret`, and removing
MVRV from the full model drops R² from {full_r2:.3f} to {without_mvrv_r2:.3f}.
ETF-flow intensity shows strong same-day association (lag 0 t = {etf_t_lag0:.1f}),
but daily timing prevents causal interpretation. Non-MVRV native variables, macro,
TradFi, and liquidity blocks each contribute ΔR² < 0.01 in the full model.

We report both full and ex-MVRV models because MVRV is a valuation-state
variable highly correlated with BTC returns — not a clean exogenous factor.
"""
    _write_md(glance_md, "T11_results_at_a_glance.md")

    # ── T12: Regime Definitions ──────────────────────────────────────────
    print("\n=== T12: Regime Definitions ===")
    regime_df = regimes_to_dataframe(regimes)
    _write(regime_df, "T12_regime_definitions.csv")

    # ── T13: Factor Dictionary ───────────────────────────────────────────
    print("\n=== T13: Factor Dictionary ===")
    all_features = list(dict.fromkeys(
        BTC_FULL_FEATURES + ETH_NATIVE + BTC_ETF + ETH_ETF + ["btc_ret", "eth_ret"]
    ))
    available_features = [f for f in all_features if f in feat.columns]
    dict_df = build_factor_dictionary(available_features)
    _write(dict_df, "T13_factor_dictionary.csv")

    # Also write markdown version
    dict_md = "# Factor Dictionary\n\n"
    dict_md += dict_df.to_markdown(index=False)
    _write_md(dict_md, "T13_factor_dictionary.md")

    # ── T14: BTC Feature Strength (full model with MVRV) ────────────────
    print("\n=== T14: BTC Feature Strength (full with MVRV) ===")
    btc_features_avail = [f for f in BTC_FULL_FEATURES if f in feat.columns]
    t14 = compute_feature_strength(
        feat, "btc_ret", btc_features_avail, model_family="btc_full_with_mvrv"
    )
    _write(t14, "T14_feature_strength_btc_full.csv")

    # ── T15: BTC Feature Strength (ex-MVRV model) ───────────────────────
    print("\n=== T15: BTC Feature Strength (ex-MVRV) ===")
    btc_ex_mvrv_avail = [f for f in BTC_EX_MVRV_FEATURES if f in feat.columns]
    t15 = compute_feature_strength(
        feat, "btc_ret", btc_ex_mvrv_avail, model_family="btc_ex_mvrv"
    )
    _write(t15, "T15_feature_strength_btc_ex_mvrv.csv")

    # ── T16: ETH Feature Strength ────────────────────────────────────────
    print("\n=== T16: ETH Feature Strength ===")
    eth_features_avail = [f for f in ETH_FULL_FEATURES if f in feat.columns]
    t16 = compute_feature_strength(
        feat, "eth_ret", eth_features_avail, model_family="eth_full"
    )
    _write(t16, "T16_feature_strength_eth.csv")

    # ── T17: Feature Strength by Regime ──────────────────────────────────
    print("\n=== T17: Feature Strength by Regime ===")
    t17_parts = []
    key_regimes = [r for r in regimes if r.name in MVRV_REGIMES + ["high_vol", "low_vol"]]
    for regime in key_regimes:
        if regime.n < 30:
            continue
        fs = compute_feature_strength(
            feat, "btc_ret", btc_ex_mvrv_avail,
            regime_mask=regime.mask, model_family=f"btc_ex_mvrv_{regime.name}"
        )
        fs.insert(0, "regime", regime.name)
        t17_parts.append(fs)
    if t17_parts:
        t17 = pd.concat(t17_parts, ignore_index=True)
        _write(t17, "T17_feature_strength_by_regime.csv")

    # ── T18: Block Strength by Regime ────────────────────────────────────
    print("\n=== T18: Block Strength by Regime ===")
    t18_parts = []
    for regime in key_regimes:
        if regime.n < 30:
            continue
        bs = compute_block_strength(
            feat, "btc_ret", BTC_BLOCKS,
            regime_mask=regime.mask, regime_name=regime.name
        )
        t18_parts.append(bs)
    if t18_parts:
        t18 = pd.concat(t18_parts, ignore_index=True)
        _write(t18, "T18_block_strength_by_regime.csv")

    # ── T19: Same-support Ablation BTC ───────────────────────────────────
    print("\n=== T19: Same-support Ablation BTC ===")
    t19 = compute_same_support_ablation(
        feat, "btc_ret", BTC_ABLATION_SPECS, regime_name="full"
    )
    _write(t19, "T19_same_support_ablation_btc.csv")

    # ── T20: Same-support Ablation ETH ───────────────────────────────────
    print("\n=== T20: Same-support Ablation ETH ===")
    t20 = compute_same_support_ablation(
        feat, "eth_ret", ETH_ABLATION_SPECS, regime_name="full"
    )
    _write(t20, "T20_same_support_ablation_eth.csv")

    # ── T21: Top Correlations BTC ────────────────────────────────────────
    print("\n=== T21: Top Correlations BTC ===")
    all_explanatory = [f for f in BTC_FULL_FEATURES + BTC_ETF if f in feat.columns]
    df_corr = feat[["btc_ret"] + all_explanatory].dropna()
    btc_corrs = df_corr.corr()["btc_ret"].drop("btc_ret")
    t21 = pd.DataFrame({
        "feature": btc_corrs.index,
        "block": [BLOCK_MAP.get(f, "Unknown") for f in btc_corrs.index],
        "correlation": btc_corrs.round(4).values,
        "abs_correlation": btc_corrs.abs().round(4).values,
    }).sort_values("abs_correlation", ascending=False).reset_index(drop=True)
    _write(t21, "T21_top_correlations_btc.csv")

    # ── T22: Top Correlations ETH ────────────────────────────────────────
    print("\n=== T22: Top Correlations ETH ===")
    eth_expl = [f for f in ETH_FULL_FEATURES + ETH_ETF if f in feat.columns]
    df_corr_eth = feat[["eth_ret"] + eth_expl].dropna()
    eth_corrs = df_corr_eth.corr()["eth_ret"].drop("eth_ret")
    t22 = pd.DataFrame({
        "feature": eth_corrs.index,
        "block": [BLOCK_MAP.get(f, "Unknown") for f in eth_corrs.index],
        "correlation": eth_corrs.round(4).values,
        "abs_correlation": eth_corrs.abs().round(4).values,
    }).sort_values("abs_correlation", ascending=False).reset_index(drop=True)
    _write(t22, "T22_top_correlations_eth.csv")

    # ── T23: Core Correlation Matrix ─────────────────────────────────────
    print("\n=== T23: Core Correlation Matrix ===")
    t23 = compute_core_correlation_matrix(feat, CORE_FEATURES)
    _write(t23, "T23_core_correlation_matrix.csv")

    # ── T24: Pre/Post Correlation Delta ──────────────────────────────────
    print("\n=== T24: Pre/Post Correlation Delta ===")
    t24 = compute_pre_post_correlation_delta(feat, CORR_PAIRS, BTC_ETF_DATE)
    _write(t24, "T24_pre_post_correlation_delta.csv")

    # ── T25: MVRV Sensitivity by Regime ──────────────────────────────────
    print("\n=== T25: MVRV Sensitivity by Regime ===")
    t25_rows = []
    for regime in regimes:
        if regime.name not in MVRV_REGIMES:
            continue
        if regime.n < 30:
            t25_rows.append({
                "regime": regime.name, "n": regime.n,
                "full_with_mvrv_r2": None, "ex_mvrv_r2": None,
                "mvrv_only_r2": None, "delta_r2": None,
                "note": "insufficient_obs",
            })
            continue

        mask = regime.mask

        # Full with MVRV
        full_abl = compute_same_support_ablation(
            feat, "btc_ret",
            [("full_with_mvrv", BTC_FULL_FEATURES), ("mvrv_only", BTC_MVRV),
             ("ex_mvrv", BTC_EX_MVRV_FEATURES)],
            regime_mask=mask, regime_name=regime.name,
        )
        full_r2_val = full_abl[full_abl["model_id"] == "full_with_mvrv"].iloc[0]["r2"]
        mvrv_only_val = full_abl[full_abl["model_id"] == "mvrv_only"].iloc[0]["r2"]
        ex_mvrv_val = full_abl[full_abl["model_id"] == "ex_mvrv"].iloc[0]["r2"]

        delta = full_r2_val - ex_mvrv_val if (
            pd.notna(full_r2_val) and pd.notna(ex_mvrv_val)
        ) else None

        t25_rows.append({
            "regime": regime.name,
            "n": int(full_abl.iloc[0]["n"]),
            "full_with_mvrv_r2": round(full_r2_val, 4) if pd.notna(full_r2_val) else None,
            "ex_mvrv_r2": round(ex_mvrv_val, 4) if pd.notna(ex_mvrv_val) else None,
            "mvrv_only_r2": round(mvrv_only_val, 4) if pd.notna(mvrv_only_val) else None,
            "delta_r2": round(delta, 4) if delta is not None else None,
            "note": "same_support",
        })
    t25 = pd.DataFrame(t25_rows)
    _write(t25, "T25_mvrv_sensitivity_by_regime.csv")

    # ── T26: ETF-era Feature Strength ────────────────────────────────────
    print("\n=== T26: ETF-era Feature Strength ===")
    post_etf = regime_lookup.get("post_btc_etf")
    if post_etf and post_etf.n >= 30:
        # Include ETF intensity in post-ETF model
        etf_era_features = BTC_EX_MVRV_FEATURES + BTC_ETF
        etf_avail = [f for f in etf_era_features if f in feat.columns]
        t26 = compute_feature_strength(
            feat, "btc_ret", etf_avail,
            regime_mask=post_etf.mask, model_family="btc_etf_era_ex_mvrv"
        )
        t26.insert(0, "regime", "post_btc_etf")
        _write(t26, "T26_etf_era_feature_strength.csv")

    # ── T27: Rolling Feature Rank Stability ──────────────────────────────
    print("\n=== T27: Rolling Feature Rank Stability ===")
    t27 = compute_rolling_feature_rank(
        feat, "btc_ret", btc_features_avail, window=180, step=30
    )
    _write(t27, "T27_rolling_feature_rank_stability.csv")

    print(f"\n=== Done. {len(list(TABLES.glob('T1*'))) + len(list(TABLES.glob('T2*')))} T1x/T2x tables generated. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
