"""Main analysis driver.

Runs the full battery and writes results to ``reports/tables/`` and
``reports/run_summaries/``:

1. Static OLS of BTC & ETH returns on factor blocks, pre vs post 2024-01-11.
2. Rolling OLS with **drop-one marginal R²** (not Shapley) over a 180-day window.
3. Chow + **single-break sup-F** sweep (not full Bai–Perron multi-break) with placebo inference.
4. VAR + 10-day FEVD: **primary** 4-variable system + **appendix** 8-variable system.
5. Event study around the spot-ETF launches (placebo *p*-values use a **[-5,+5]** window benchmark).
6. Static OLS on **weekday-only** rows (headline robustness vs crypto-7 calendar).

Every write lands in a dated folder so reruns don't clobber prior outputs.
"""
from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.data.calendars import business_day_mask  # noqa: E402
from cqresearch.features.panel import build_feature_panel  # noqa: E402
from cqresearch.features.returns import winsorize  # noqa: E402
from cqresearch.modeling.ols import fit_ols, subsample_ols  # noqa: E402
from cqresearch.modeling.rolling import rolling_ols  # noqa: E402
from cqresearch.modeling.structural_breaks import chow_test, sup_f_sweep, placebo_breaks  # noqa: E402
from cqresearch.modeling.var_fevd import fit_var_fevd, connectedness_index  # noqa: E402
from cqresearch.modeling.event_study import market_model_event, placebo_cars  # noqa: E402
from config.paths import PANELS_DIR, REPORTS_TABLES_DIR, REPORTS_RUN_SUMMARIES_DIR  # noqa: E402

warnings.simplefilter("ignore")

STAMP = datetime.utcnow().strftime("%Y-%m-%d")
TABLES = REPORTS_TABLES_DIR / STAMP
TABLES.mkdir(parents=True, exist_ok=True)

BTC_ETF_DATE = pd.Timestamp("2024-01-11")
ETH_ETF_DATE = pd.Timestamp("2024-07-23")

# Regressor bundles (stationary features only).
MACRO = ["DGS10_d1", "DGS2_d1", "VIXCLS_d1", "DTWEXBGS_d1", "DFF_d1"]
INSTITUTIONAL = ["spy_ret", "qqq_ret", "gld_ret"]
LIQUIDITY = ["defi_tvl_usd_ret", "stables_total_usd_ret"]
SENT = ["fng_value_d1"]
BTC_NATIVE = [
    "cme_btc_basis_close_d1",
    "btc_exchange_netflow_d1",
    "btc_miner_to_exchange_flow_d1",
    "btc_mvrv_d1",
]
ETH_NATIVE = ["cme_eth_basis_close_d1"]


def _write_csv(df: pd.DataFrame, name: str) -> Path:
    p = TABLES / f"{name}.csv"
    df.to_csv(p)
    return p


def load_features() -> pd.DataFrame:
    panel = pd.read_parquet(PANELS_DIR / "master_daily.parquet")
    feat = build_feature_panel(panel)
    # Winsorize returns/diffs at 1/99% to dampen a handful of extreme days
    for c in feat.columns:
        if feat[c].dtype.kind in "fc":
            feat[c] = winsorize(feat[c], q=0.01)
    return feat


# ---------------------------------------------------------------------------
# 1. Static OLS (pre vs post ETF)
# ---------------------------------------------------------------------------
def static_ols(feat: pd.DataFrame, asset: str, *, calendar: str = "crypto7") -> list[dict]:
    """calendar='crypto7' uses all rows; 'weekday' restricts to Mon–Fri (see business_day_mask)."""

    regressors = MACRO + INSTITUTIONAL + LIQUIDITY + SENT + (BTC_NATIVE if asset == "btc" else ETH_NATIVE)
    regressors = [c for c in regressors if c in feat.columns]
    bp = BTC_ETF_DATE if asset == "btc" else ETH_ETF_DATE

    m = business_day_mask(feat.index) if calendar == "weekday" else pd.Series(True, index=feat.index)
    sub = feat.loc[m]
    y = sub[f"{asset}_ret"].dropna()
    Xall = sub[regressors]

    full = fit_ols(y, Xall.loc[y.index], label="full")
    subs = subsample_ols(y, Xall.loc[y.index], bp, labels=("pre_etf", "post_etf"))

    rows: list[dict] = []
    for lab, res in [("full", full), ("pre_etf", subs["pre_etf"]), ("post_etf", subs["post_etf"])]:
        df = res.to_frame().reset_index(names="regressor")
        df.insert(0, "sample", lab)
        df.insert(0, "asset", asset)
        df.insert(0, "calendar", calendar)
        rows.extend(df.to_dict("records"))
    return rows


# ---------------------------------------------------------------------------
# 2. Rolling OLS with partial R²
# ---------------------------------------------------------------------------
def rolling_analysis(feat: pd.DataFrame, asset: str, window: int = 180) -> pd.DataFrame:
    regressors = MACRO + INSTITUTIONAL + LIQUIDITY + SENT + (BTC_NATIVE if asset == "btc" else ETH_NATIVE)
    y = feat[f"{asset}_ret"]
    X = feat[regressors]
    roll = rolling_ols(y, X, window=window)
    return roll


# ---------------------------------------------------------------------------
# 3. Structural breaks
# ---------------------------------------------------------------------------
def structural_breaks(feat: pd.DataFrame, asset: str) -> dict:
    regressors = INSTITUTIONAL + MACRO  # focus on institutional + macro block
    y = feat[f"{asset}_ret"]
    X = feat[regressors]
    bp = BTC_ETF_DATE if asset == "btc" else ETH_ETF_DATE

    chow = chow_test(y, X, bp)
    sup = sup_f_sweep(y, X, trim=0.15)
    p_val, null = placebo_breaks(y, X, n_permutations=300, trim=0.15, seed=42)
    return {
        "asset": asset,
        "chow_breakpoint": bp.date().isoformat(),
        "chow_f": chow.f_stat, "chow_p": chow.p_value,
        "sup_f": sup.sup_f, "sup_f_argmax_date": sup.argmax_date.date().isoformat(),
        "sup_f_placebo_p": p_val,
        "null_mean": float(np.mean(null)), "null_95th": float(np.percentile(null, 95)),
        "n": chow.n, "k": chow.k,
    }, sup.f_series


# ---------------------------------------------------------------------------
# 4. VAR + FEVD (Diebold-Yilmaz connectedness)
# ---------------------------------------------------------------------------
def var_fevd_analysis(
    feat: pd.DataFrame, *, label: str, columns: list[str],
) -> tuple[pd.DataFrame, dict]:
    cols = [c for c in columns if c in feat.columns]
    sub = feat[cols].dropna()
    fev = fit_var_fevd(sub, horizon=10, maxlags=10)
    total = connectedness_index(fev)
    meta = {
        "label": label,
        "lag_order": fev.lag_order,
        "n": fev.n,
        "horizon": fev.horizon,
        "dy_total_connectedness_pct": round(total, 2),
        "columns": cols,
        "cholesky_note": "FEVD uses statsmodels VAR with Cholesky ordering = column order listed in 'columns'.",
    }
    return fev.table, meta


VAR_COLS_FULL = [
    "btc_ret", "eth_ret", "spy_ret", "gld_ret",
    "DGS10_d1", "VIXCLS_d1", "stables_total_usd_ret", "defi_tvl_usd_ret",
]
VAR_COLS_COMPACT = ["btc_ret", "eth_ret", "spy_ret", "VIXCLS_d1"]


# ---------------------------------------------------------------------------
# 5. Event study
# ---------------------------------------------------------------------------
def event_studies(feat: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    events = [
        ("btc", "BTC spot ETF launch (2024-01-11)", BTC_ETF_DATE),
        ("eth", "ETH spot ETF launch (2024-07-23)", ETH_ETF_DATE),
        ("btc", "Fed pivot signal (2022-11-02 FOMC)", pd.Timestamp("2022-11-02")),
        ("btc", "FTX collapse (2022-11-08)", pd.Timestamp("2022-11-08")),
        ("btc", "Silicon Valley Bank failure (2023-03-10)", pd.Timestamp("2023-03-10")),
    ]
    market = feat["spy_ret"]
    for asset, label, date in events:
        asset_ret = feat[f"{asset}_ret"]
        try:
            res = market_model_event(asset_ret, market, date)
            p5, null5, actual5 = placebo_cars(
                asset_ret, market, date, window=(-5, 5), n_placebos=200
            )
            df = res.car_by_window.copy()
            df["alpha"] = res.alpha
            df["beta"] = res.beta
            df["sigma_e"] = res.sigma_e
            df["placebo_p_m5_p5"] = p5
            df["placebo_benchmark_window"] = "[-5,+5]"
            df["asset"] = asset
            df["event"] = label
            df["event_date"] = date.date().isoformat()
            rows.extend(df.to_dict("records"))
        except Exception as exc:
            rows.append({"event": label, "error": str(exc), "asset": asset})
    return rows


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def main() -> None:
    feat = load_features()
    print(f"features: {feat.shape[0]} rows x {feat.shape[1]} cols")

    # 1. Static OLS (crypto-7 + weekday headline)
    static_rows: list[dict] = []
    for a in ("btc", "eth"):
        static_rows.extend(static_ols(feat, a, calendar="crypto7"))
        static_rows.extend(static_ols(feat, a, calendar="weekday"))
    static_df = pd.DataFrame(static_rows)
    _write_csv(static_df, "static_ols_pre_post_etf")
    print(f"[ok] static_ols rows={len(static_df)}")

    # 2. Rolling OLS
    for a in ("btc", "eth"):
        roll = rolling_analysis(feat, a)
        _write_csv(roll, f"rolling_ols_{a}_180d")
        print(f"[ok] rolling_ols {a}: {roll.shape}")

    # 3. Structural breaks
    sb_rows: list[dict] = []
    for a in ("btc", "eth"):
        res, f_series = structural_breaks(feat, a)
        sb_rows.append(res)
        _write_csv(f_series.to_frame(), f"sup_f_series_{a}")
    sb_df = pd.DataFrame(sb_rows)
    _write_csv(sb_df, "structural_breaks_summary")
    print(f"[ok] structural_breaks done")

    # 4. VAR + FEVD (compact primary + full appendix)
    fevd_compact, meta_c = var_fevd_analysis(feat, label="compact_4var", columns=VAR_COLS_COMPACT)
    _write_csv(fevd_compact, "fevd_10d_compact")
    (TABLES / "var_fevd_meta_compact.json").write_text(json.dumps(meta_c, indent=2), encoding="utf-8")
    fevd_tab, meta = var_fevd_analysis(feat, label="full_8var", columns=VAR_COLS_FULL)
    _write_csv(fevd_tab, "fevd_10d")
    (TABLES / "var_fevd_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[ok] VAR compact lag={meta_c['lag_order']} DY={meta_c['dy_total_connectedness_pct']}%")
    print(f"[ok] VAR full lag={meta['lag_order']}  DY connectedness={meta['dy_total_connectedness_pct']}")

    # 5. Event studies
    ev_rows = event_studies(feat)
    ev_df = pd.DataFrame(ev_rows)
    _write_csv(ev_df, "event_studies")
    print(f"[ok] event_studies rows={len(ev_df)}")

    # Summary markdown
    summary = REPORTS_RUN_SUMMARIES_DIR / "03_run_analyses.md"
    lines: list[str] = []
    lines.append(f"# Analysis run — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    lines.append(f"Outputs: `reports/tables/{STAMP}/`\n")

    lines.append("## 1. Static OLS (pre vs post ETF)\n")
    lines.append("See `static_ols_pre_post_etf.csv`. Headline R² (full/pre/post):\n")
    head = (
        static_df[
            (static_df["regressor"] == "const") & (static_df["calendar"] == "crypto7")
        ][["asset", "sample", "r2", "n"]]
        .drop_duplicates()
    )
    for _, r in head.iterrows():
        lines.append(f"- {r['asset'].upper()} / {r['sample']}: R²={r['r2']:.3f}, N={r['n']}")

    lines.append("\n## 2. Rolling OLS with partial R² — see `rolling_ols_*_180d.csv`\n")

    lines.append("## 3. Structural-break tests\n")
    lines.append("| asset | Chow F @ ETF date | Chow p | supF | argmax date | placebo p |")
    lines.append("| --- | ---: | ---: | ---: | --- | ---: |")
    for r in sb_rows:
        lines.append(
            f"| {r['asset'].upper()} | {r['chow_f']:.2f} | {r['chow_p']:.4g} | "
            f"{r['sup_f']:.2f} | {r['sup_f_argmax_date']} | {r['sup_f_placebo_p']:.4g} |"
        )

    lines.append("\n## 4. VAR + FEVD (10-day horizon)\n")
    lines.append("### 4a Primary (4-variable compact)\n")
    lines.append(f"BIC lag: **{meta_c['lag_order']}**  DY: **{meta_c['dy_total_connectedness_pct']:.1f}%**  cols={meta_c['columns']}")
    lines.append("\n" + fevd_compact.round(3).to_markdown())
    lines.append("\n### 4b Appendix (8-variable)\n")
    lines.append(f"BIC-selected lag order: **{meta['lag_order']}**  ")
    lines.append(f"Diebold-Yilmaz total connectedness: **{meta['dy_total_connectedness_pct']:.1f}%** over {meta['columns']}.")
    lines.append("\nFEVD table (rows = 'from', cols = 'to'):\n")
    lines.append(fevd_tab.round(3).to_markdown())

    lines.append("\n## 5. Event studies\n")
    lines.append(ev_df.round(4).to_markdown(index=False))

    summary.write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] summary={summary}")


if __name__ == "__main__":
    main()
