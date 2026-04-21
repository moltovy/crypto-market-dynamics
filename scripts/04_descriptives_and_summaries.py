"""Descriptive + summary tables used by the paper draft.

Produces:
* descriptive_stats.csv — mean, sd, skew, kurt, min, max, N by asset & sample
* correlation_matrix_pre.csv / correlation_matrix_post.csv
* block_r2_pre_post.csv — aggregate R² by factor block, pre vs post ETF
* etf_flow_regression.csv — BTC ret ~ ETF intensity + controls, post-launch
* rolling_r2_by_regime.csv — median rolling R² across calendar regimes
"""
from __future__ import annotations

import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

warnings.simplefilter("ignore")

from cqresearch.features.panel import build_feature_panel
from cqresearch.features.returns import winsorize
from cqresearch.modeling.ols import fit_ols
from config.paths import PANELS_DIR, REPORTS_TABLES_DIR

STAMP = datetime.utcnow().strftime("%Y-%m-%d")
TAB = REPORTS_TABLES_DIR / STAMP
TAB.mkdir(parents=True, exist_ok=True)

BTC_ETF = pd.Timestamp("2024-01-11")
ETH_ETF = pd.Timestamp("2024-07-23")

BLOCKS = {
    "Macro": ["DGS10_d1", "DGS2_d1", "VIXCLS_d1", "DTWEXBGS_d1", "DFF_d1"],
    "Institutional": ["spy_ret", "qqq_ret", "gld_ret"],
    "Liquidity": ["defi_tvl_usd_ret", "stables_total_usd_ret"],
    "Sentiment": ["fng_value_d1"],
    "Native_btc": [
        "cme_btc_basis_close_d1",
        "btc_exchange_netflow_d1",
        "btc_miner_to_exchange_flow_d1",
        "btc_mvrv_d1",
    ],
    "Native_eth": ["cme_eth_basis_close_d1"],
}


def load_features() -> pd.DataFrame:
    panel = pd.read_parquet(PANELS_DIR / "master_daily.parquet")
    feat = build_feature_panel(panel)
    for c in feat.columns:
        if feat[c].dtype.kind in "fc":
            feat[c] = winsorize(feat[c], q=0.01)
    return feat


def descriptive_stats(feat: pd.DataFrame) -> pd.DataFrame:
    cols = ["btc_ret", "eth_ret", "spy_ret", "gld_ret", "qqq_ret",
            "VIXCLS_d1", "DGS10_d1", "DXY_close" if "DXY_close" in feat.columns else "dxy_tv_ret"]
    cols = [c for c in cols if c in feat.columns]
    periods: dict[str, pd.DataFrame] = {
        "full_2020_2026": feat[cols],
        "pre_etf_2020_2024": feat.loc[feat.index < BTC_ETF, cols],
        "post_etf_2024_2026": feat.loc[feat.index >= BTC_ETF, cols],
    }
    rows = []
    for period, df in periods.items():
        for c in df.columns:
            s = df[c].dropna()
            rows.append({
                "period": period, "variable": c, "n": len(s),
                "mean_pct": round(float(s.mean() * 100), 4),
                "sd_pct": round(float(s.std() * 100), 4),
                "skew": round(float(s.skew()), 3),
                "kurt": round(float(s.kurtosis()), 3),
                "min_pct": round(float(s.min() * 100), 3),
                "max_pct": round(float(s.max() * 100), 3),
            })
    return pd.DataFrame(rows)


def corr_matrices(feat: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = ["btc_ret", "eth_ret", "spy_ret", "qqq_ret", "gld_ret",
            "defi_tvl_usd_ret", "stables_total_usd_ret",
            "VIXCLS_d1", "DGS10_d1"]
    cols = [c for c in cols if c in feat.columns]
    pre = feat.loc[feat.index < BTC_ETF, cols].corr()
    post = feat.loc[feat.index >= BTC_ETF, cols].corr()
    return pre.round(3), post.round(3)


def block_r2(feat: pd.DataFrame, asset: str, sample_mask: pd.Series) -> dict:
    y = feat.loc[sample_mask, f"{asset}_ret"].dropna()
    results = {"asset": asset}
    native_key = "Native_btc" if asset == "btc" else "Native_eth"
    for block, cols in BLOCKS.items():
        if block.startswith("Native_") and block != native_key:
            continue
        cols = [c for c in cols if c in feat.columns]
        if not cols:
            continue
        X = feat.loc[sample_mask, cols].dropna()
        yy = y.loc[X.index]
        if len(yy) < 30:
            continue
        res = fit_ols(yy, X, label=block)
        results[f"R2_{block}"] = round(res.r2, 4)
        results[f"N_{block}"] = res.nobs
    return results


def etf_flow_regression(feat: pd.DataFrame) -> pd.DataFrame:
    """Post-launch only: BTC ret ~ BTC ETF intensity (lag 0) + controls."""

    sub = feat.loc[feat.index >= BTC_ETF].dropna(subset=["btc_ret", "btc_etf_intensity"])
    if len(sub) < 60:
        return pd.DataFrame()
    regressors = ["btc_etf_intensity", "spy_ret", "VIXCLS_d1", "DGS10_d1"]
    regressors = [c for c in regressors if c in sub.columns]
    res = fit_ols(sub["btc_ret"], sub[regressors], label="etf_flow_regression")
    return res.to_frame().reset_index(names="regressor")


def main() -> None:
    feat = load_features()

    desc = descriptive_stats(feat)
    desc.to_csv(TAB / "descriptive_stats.csv", index=False)

    pre, post = corr_matrices(feat)
    pre.to_csv(TAB / "correlation_matrix_pre_etf.csv")
    post.to_csv(TAB / "correlation_matrix_post_etf.csv")

    # Block R² pre/post
    br_rows = []
    for asset in ("btc", "eth"):
        br_rows.append({"period": "full", **block_r2(feat, asset, pd.Series(True, index=feat.index))})
        br_rows.append({"period": "pre_etf", **block_r2(feat, asset, feat.index < BTC_ETF)})
        br_rows.append({"period": "post_etf", **block_r2(feat, asset, feat.index >= BTC_ETF)})
    pd.DataFrame(br_rows).to_csv(TAB / "block_r2_pre_post.csv", index=False)

    flow_df = etf_flow_regression(feat)
    flow_df.to_csv(TAB / "etf_flow_regression.csv", index=False)

    # Rolling R² median by calendar year
    for asset in ("btc", "eth"):
        roll = pd.read_csv(TAB / f"rolling_ols_{asset}_180d.csv", parse_dates=["date"]).set_index("date")
        by_year = roll["r2"].groupby(roll.index.year).median().rename("median_r2").to_frame()
        by_year.to_csv(TAB / f"rolling_r2_{asset}_median_by_year.csv")

    print("descriptive_stats rows:", len(desc))
    print("corr_pre shape:", pre.shape)
    print("corr_post shape:", post.shape)
    print("block_r2 rows:", len(br_rows))
    print("flow regression rows:", len(flow_df))


if __name__ == "__main__":
    main()
