"""Robustness checks for the v0.1 paper.

R1  — re-estimate Table 5 with lagged ETF flow intensity (remove simultaneity).
R2  — Table 5 without winsorization.
R3  — HAC lag sensitivity (lags = 5, 10, 20).
R4  — re-estimate static pre/post OLS on the post-2021 sub-window to check
      that pre-ETF results aren't driven by the 2020 COVID spike.
R5  — split panel around the sup-F argmax (2021-01-04 for BTC) and compare
      block-R² across *that* break instead of the ETF date.
R6  — alt-sample: restrict to the common window where every regressor is live
      (first date where all chosen cols have a non-NaN value); re-run Table 2.

Writes each output under reports/tables/<stamp>/robustness/.
"""
from __future__ import annotations

import sys
import warnings
from datetime import datetime
from pathlib import Path

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
OUT = REPORTS_TABLES_DIR / STAMP / "robustness"
OUT.mkdir(parents=True, exist_ok=True)

BTC_ETF = pd.Timestamp("2024-01-11")
BTC_SUPF = pd.Timestamp("2021-01-04")

MACRO = ["DGS10_d1", "DGS2_d1", "VIXCLS_d1", "DTWEXBGS_d1", "DFF_d1"]
INST = ["spy_ret", "qqq_ret", "gld_ret"]
LIQ = ["defi_tvl_usd_ret", "stables_total_usd_ret"]
SENT = ["fng_value_d1"]
NATIVE_BTC = ["cme_btc_basis_close_d1"]


def load(winsor: bool = True) -> pd.DataFrame:
    panel = pd.read_parquet(PANELS_DIR / "master_daily.parquet")
    feat = build_feature_panel(panel)
    if winsor:
        for c in feat.columns:
            if feat[c].dtype.kind in "fc":
                feat[c] = winsorize(feat[c], q=0.01)
    return feat


# R1 — lagged ETF flow
def r1_lagged_flow(feat: pd.DataFrame) -> pd.DataFrame:
    sub = feat.loc[feat.index >= BTC_ETF].copy()
    sub["btc_etf_intensity_lag1"] = sub["btc_etf_intensity"].shift(1)
    rows = []
    for regressors, label in [
        (["btc_etf_intensity_lag1"], "lag1_only"),
        (["btc_etf_intensity_lag1", "spy_ret", "VIXCLS_d1"], "lag1_plus_controls"),
        (["btc_etf_intensity", "btc_etf_intensity_lag1", "spy_ret", "VIXCLS_d1"], "contemp_plus_lag1"),
    ]:
        s = sub.dropna(subset=["btc_ret"] + regressors)
        if len(s) < 60:
            continue
        res = fit_ols(s["btc_ret"], s[regressors], label=label)
        df = res.to_frame().reset_index(names="regressor")
        df.insert(0, "spec", label)
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


# R2 — no winsorization
def r2_no_winsor() -> pd.DataFrame:
    feat = load(winsor=False)
    sub = feat.loc[feat.index >= BTC_ETF].dropna(subset=["btc_ret", "btc_etf_intensity"])
    regressors = ["btc_etf_intensity", "spy_ret", "VIXCLS_d1", "DGS10_d1"]
    res = fit_ols(sub["btc_ret"], sub[regressors], label="no_winsor")
    df = res.to_frame().reset_index(names="regressor")
    df.insert(0, "spec", "no_winsor_post_etf")
    return df


# R3 — HAC lag sensitivity
def r3_hac_sensitivity(feat: pd.DataFrame) -> pd.DataFrame:
    sub = feat.loc[feat.index >= BTC_ETF].dropna(subset=["btc_ret", "btc_etf_intensity"])
    regressors = ["btc_etf_intensity", "spy_ret", "VIXCLS_d1", "DGS10_d1"]
    rows = []
    for lags in (5, 10, 20, 40):
        res = fit_ols(sub["btc_ret"], sub[regressors], hac_lags=lags, label=f"hac{lags}")
        df = res.to_frame().reset_index(names="regressor")
        df["hac_lags"] = lags
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


# R4 — static pre/post starting 2021
def r4_post2021(feat: pd.DataFrame) -> pd.DataFrame:
    f = feat.loc[feat.index >= pd.Timestamp("2021-01-01")]
    y = f["btc_ret"].dropna()
    regs = MACRO + INST + LIQ + SENT + NATIVE_BTC
    X = f[regs]
    rows = []
    for lab, mask in [
        ("pre_etf_2021_2024", f.index < BTC_ETF),
        ("post_etf_2024_2026", f.index >= BTC_ETF),
    ]:
        yy = y.loc[mask[y.index.isin(y.index)] if False else y[y.index.isin(f.index[mask])].index]
        xx = X.loc[yy.index]
        res = fit_ols(yy, xx, label=lab)
        df = res.to_frame().reset_index(names="regressor")
        df["sample"] = lab
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


# R5 — split around sup-F argmax (2021-01-04)
def r5_supf_split(feat: pd.DataFrame) -> pd.DataFrame:
    y = feat["btc_ret"].dropna()
    regs = MACRO + INST + LIQ + SENT + NATIVE_BTC
    X = feat[regs]
    rows = []
    for lab, mask in [
        ("pre_supF_2020_2021", feat.index < BTC_SUPF),
        ("post_supF_2021_2026", feat.index >= BTC_SUPF),
    ]:
        yy = y[y.index.isin(feat.index[mask])]
        xx = X.loc[yy.index]
        res = fit_ols(yy, xx, label=lab)
        df = res.to_frame().reset_index(names="regressor")
        df["sample"] = lab
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


# R6 — common-support window
def r6_common_support(feat: pd.DataFrame) -> pd.DataFrame:
    cols = ["btc_ret"] + MACRO + INST + LIQ + SENT + NATIVE_BTC
    sub = feat[cols].dropna()
    first = sub.index.min()
    rows = []
    for lab, mask in [
        ("pre_etf", sub.index < BTC_ETF),
        ("post_etf", sub.index >= BTC_ETF),
    ]:
        s = sub.loc[mask]
        res = fit_ols(s["btc_ret"], s[MACRO + INST + LIQ + SENT + NATIVE_BTC], label=lab)
        df = res.to_frame().reset_index(names="regressor")
        df["sample"] = lab
        df["first_common_date"] = first.date().isoformat()
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    feat = load(winsor=True)

    r1 = r1_lagged_flow(feat)
    r1.to_csv(OUT / "R1_lagged_etf_flow.csv", index=False)

    r2 = r2_no_winsor()
    r2.to_csv(OUT / "R2_no_winsor_post_etf.csv", index=False)

    r3 = r3_hac_sensitivity(feat)
    r3.to_csv(OUT / "R3_hac_lag_sensitivity.csv", index=False)

    r4 = r4_post2021(feat)
    r4.to_csv(OUT / "R4_post2021_static_ols.csv", index=False)

    r5 = r5_supf_split(feat)
    r5.to_csv(OUT / "R5_supF_split.csv", index=False)

    r6 = r6_common_support(feat)
    r6.to_csv(OUT / "R6_common_support.csv", index=False)

    for name, df in [("R1", r1), ("R2", r2), ("R3", r3), ("R4", r4), ("R5", r5), ("R6", r6)]:
        print(f"{name}: {df.shape}")


if __name__ == "__main__":
    main()
