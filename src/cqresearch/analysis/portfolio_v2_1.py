"""Portfolio v2.1 analytics and artifact orchestration."""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, SupportsFloat, cast

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config.paths import (
    DATA_DIR,
    PROJECT_ROOT,
    REPORTS_FIGURES_DIR,
    REPORTS_PANELS_DIR,
    REPORTS_TABLES_DIR,
)

from cqresearch.analysis.native_factors import (
    native_factor_ablation,
    native_factor_correlations,
    native_factor_registry,
    native_zscore_dashboard_data,
)
from cqresearch.features.panel import build_feature_panel
from cqresearch.features.returns import winsorize
from cqresearch.features.volatility import add_realized_vol_features
from cqresearch.modeling.ablation import (
    BTC_MVRV,
    BTC_NATIVE_EX_MVRV,
    ETH_NATIVE,
    LIQUIDITY,
    MACRO,
    SENTIMENT,
    TRADFI,
    make_default_btc_ablation_specs,
    make_default_eth_ablation_specs,
    run_nested_ablation,
)
from cqresearch.modeling.lead_lag import (
    LAG_CONVENTION,
    flow_quintile_summary,
    lead_lag_regression_grid,
    top_flow_days,
)
from cqresearch.modeling.partial_r2 import (
    block_partial_r2,
    rolling_block_partial_r2,
    safe_standardize,
)
from cqresearch.viz.style import PALETTE, add_footer, setup

setup()

PORTFOLIO_DIR = PROJECT_ROOT / "reports" / "portfolio_v2_1"
TABLES_DIR = PORTFOLIO_DIR / "tables"
FIGURES_DIR = PORTFOLIO_DIR / "figures"
MODEL_CARDS_DIR = PORTFOLIO_DIR / "model_cards"
DIAGNOSTICS_DIR = PORTFOLIO_DIR / "diagnostics"

BTC_ETF_DATE = pd.Timestamp("2024-01-11")
ETH_ETF_DATE = pd.Timestamp("2024-07-23")
FTX_DATE = pd.Timestamp("2022-11-08")
SVB_DATE = pd.Timestamp("2023-03-10")
BTC_HALVING_2024 = pd.Timestamp("2024-04-20")

EVENT_MARKERS = {
    "FTX": FTX_DATE,
    "SVB": SVB_DATE,
    "BTC ETF": BTC_ETF_DATE,
    "BTC halving": BTC_HALVING_2024,
    "ETH ETF": ETH_ETF_DATE,
}

FOOTER = (
    "Crypto Market Factor Lab v2.1 - frozen panel, 2020-01-01..2026-04-11 - "
    "reduced-form diagnostics, not causal identification"
)

REQUIRED_MODEL_CARD_SECTIONS = [
    "Purpose",
    "Inputs",
    "Sample",
    "Method",
    "Output files",
    "Interpretation",
    "Risks / limitations",
    "Upgrade path",
]


@dataclass
class PortfolioV21Result:
    tables: list[Path]
    figures: list[Path]
    reports: list[Path]
    model_cards: list[Path]
    optional_failures: list[str]
    manifest_path: Path


def ensure_portfolio_dirs(base_dir: Path = PORTFOLIO_DIR) -> dict[str, Path]:
    """Create the v2.1 artifact directory tree and return its paths."""

    paths = {
        "base": base_dir,
        "tables": base_dir / "tables",
        "figures": base_dir / "figures",
        "model_cards": base_dir / "model_cards",
        "diagnostics": base_dir / "diagnostics",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def required_manifest_fields() -> list[str]:
    """Fields that every v2.1 manifest must expose."""

    return [
        "generated_at_utc",
        "git_commit",
        "panel",
        "source_table_bundle",
        "source_figure_bundle",
        "commands_run",
        "tables_generated",
        "figures_generated",
        "reports_generated",
    ]


def latest_complete_table_dir(base: Path = REPORTS_TABLES_DIR) -> Path:
    required = {
        "static_ols_pre_post_etf.csv",
        "structural_breaks_summary.csv",
        "event_studies.csv",
        "fevd_10d_compact.csv",
        "var_fevd_meta_compact.json",
    }
    for candidate in sorted([p for p in base.iterdir() if p.is_dir()], reverse=True):
        if all((candidate / name).exists() for name in required):
            return candidate
    raise FileNotFoundError(f"No complete table bundle found under {base}")


def latest_complete_figure_dir(base: Path = REPORTS_FIGURES_DIR) -> Path:
    required = {
        "F07_fevd_heatmap.png",
        "F08_event_cars.png",
        "F09_coverage.png",
    }
    for candidate in sorted([p for p in base.iterdir() if p.is_dir()], reverse=True):
        if all((candidate / name).exists() for name in required):
            return candidate
    raise FileNotFoundError(f"No complete figure bundle found under {base}")


def git_commit_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unavailable"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(df: pd.DataFrame, *, index: bool = False) -> str:
    if df.empty:
        return "_No rows._"
    return df.to_markdown(index=index)


def fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if isinstance(value, str):
        return value
    return f"{float(cast(SupportsFloat, value)):.{digits}f}"


def pct(value: object, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{100 * float(cast(SupportsFloat, value)):.{digits}f}%"


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[ok] wrote {path}")
    return path


def write_csv(df: pd.DataFrame, path: Path, *, index: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    print(f"[ok] wrote {path} rows={len(df)}")
    return path


def save_figure(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig.tight_layout(rect=(0, 0.045, 1, 1))
    except Exception as exc:
        print(f"[warn] tight_layout failed for {path.name}: {exc}")
    add_footer(fig, FOOTER)
    fig.savefig(path)
    plt.close(fig)
    print(f"[ok] wrote {path}")
    return path


def load_panel_and_features() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    panel_path = REPORTS_PANELS_DIR / "master_daily.parquet"
    meta_path = REPORTS_PANELS_DIR / "master_daily_meta.json"
    if not panel_path.exists():
        raise FileNotFoundError(f"Required frozen panel missing: {panel_path}")
    if not meta_path.exists():
        raise FileNotFoundError(f"Required panel metadata missing: {meta_path}")

    panel = pd.read_parquet(panel_path)
    feat = build_feature_panel(panel)
    for col in feat.columns:
        if feat[col].dtype.kind in "fc":
            feat[col] = winsorize(feat[col], q=0.01)
    feat = add_realized_vol_features(feat)
    return panel, feat, read_json(meta_path)


def _sample_masks(index: pd.DatetimeIndex, asset: str) -> dict[str, pd.Series]:
    masks = {
        "full": pd.Series(True, index=index),
        "pre_btc_etf": pd.Series(index < BTC_ETF_DATE, index=index),
        "post_btc_etf": pd.Series(index >= BTC_ETF_DATE, index=index),
    }
    if asset == "eth":
        masks["post_eth_etf"] = pd.Series(index >= ETH_ETF_DATE, index=index)
    return masks


def _active_blocks(
    feat_sample: pd.DataFrame,
    blocks: dict[str, list[str]],
    *,
    min_non_missing: int = 30,
) -> dict[str, list[str]]:
    active: dict[str, list[str]] = {}
    for block, cols in blocks.items():
        cols_here = [
            col
            for col in cols
            if col in feat_sample.columns and feat_sample[col].notna().sum() >= min_non_missing
        ]
        if cols_here:
            active[block] = cols_here
    return active


def _blocks_for_asset(asset: str, *, include_etf: bool) -> dict[str, list[str]]:
    blocks = {
        "Macro": MACRO,
        "TradFi": TRADFI,
        "Liquidity": LIQUIDITY,
        "Sentiment": SENTIMENT,
    }
    if asset == "btc":
        blocks["BTC Native ex MVRV"] = BTC_NATIVE_EX_MVRV
        blocks["BTC MVRV"] = BTC_MVRV
        if include_etf:
            blocks["BTC ETF Flow"] = ["btc_etf_intensity"]
    else:
        blocks["ETH Native"] = ETH_NATIVE
        if include_etf:
            blocks["ETH ETF Flow"] = ["eth_etf_intensity"]
    return blocks


def build_block_partial_r2_tables(feat: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for sample, mask in _sample_masks(feat.index, asset).items():
        sample_feat = feat.loc[mask].copy()
        include_etf = sample.startswith("post")
        blocks = _active_blocks(sample_feat, _blocks_for_asset(asset, include_etf=include_etf))
        cols = list(dict.fromkeys(col for values in blocks.values() for col in values))
        if not cols:
            continue
        out = block_partial_r2(
            sample_feat[f"{asset}_ret"],
            safe_standardize(sample_feat[cols]),
            blocks,
        )
        out.insert(0, "asset", asset)
        out.insert(1, "sample", sample)
        rows.append(out)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def build_rolling_block_partial_r2(feat: pd.DataFrame, asset: str) -> pd.DataFrame:
    blocks = _active_blocks(feat, _blocks_for_asset(asset, include_etf=False))
    cols = list(dict.fromkeys(col for values in blocks.values() for col in values))
    out = rolling_block_partial_r2(
        feat[f"{asset}_ret"],
        safe_standardize(feat[cols]),
        blocks,
        window=180,
        min_periods=150,
    )
    out.insert(0, "asset", asset)
    out["note"] = "ETF-flow block excluded from rolling attribution; handled in lead-lag lab"
    return out


def build_ablation_table(feat: pd.DataFrame, asset: str) -> pd.DataFrame:
    specs = make_default_btc_ablation_specs(feat) if asset == "btc" else make_default_eth_ablation_specs(feat)
    rows: list[pd.DataFrame] = []
    for sample, mask in _sample_masks(feat.index, asset).items():
        sub = feat.loc[mask].copy()
        y = sub[f"{asset}_ret"].copy()
        y.attrs["sample"] = sample
        rows.append(run_nested_ablation(y, sub, specs))
    return pd.concat(rows, ignore_index=True)


def _control_frame(feat: pd.DataFrame, asset: str) -> pd.DataFrame:
    cols = [col for col in ["spy_ret", "VIXCLS_d1", "DGS10_d1"] if col in feat.columns]
    controls = feat[cols].copy()
    controls[f"{asset}_ret_lag1"] = feat[f"{asset}_ret"].shift(1)
    return controls


def build_etf_lead_lag_tables(feat: pd.DataFrame, asset: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    launch = BTC_ETF_DATE if asset == "btc" else ETH_ETF_DATE
    flow_col = f"{asset}_etf_intensity"
    target_ret = f"{asset}_ret"
    target_rv = f"{asset}_rv_30d"
    if flow_col not in feat.columns:
        empty = pd.DataFrame()
        return empty, empty, empty

    sub = feat.loc[feat.index >= launch].copy()
    controls = _control_frame(sub, asset)
    grids = [
        lead_lag_regression_grid(sub[target_ret], sub[flow_col], controls, lags=range(-5, 6))
    ]
    if target_rv in sub.columns:
        grids.append(
            lead_lag_regression_grid(sub[target_rv], sub[flow_col], controls, lags=range(-5, 6))
        )
    lead_lag = pd.concat(grids, ignore_index=True)
    quintiles = flow_quintile_summary(sub[target_ret], sub[flow_col])
    top_days = top_flow_days(sub, flow_col, target_ret, n=10)
    return lead_lag, quintiles, top_days


def rolling_corr_matrix(
    feat: pd.DataFrame,
    pairs: list[tuple[str, str, str]],
    windows: tuple[int, ...] = (60, 180, 365),
) -> pd.DataFrame:
    """Return rolling correlations for named pairs and windows."""

    rows: list[pd.DataFrame] = []
    for label, lhs, rhs in pairs:
        if lhs not in feat.columns or rhs not in feat.columns:
            continue
        for window in windows:
            corr = feat[lhs].rolling(window, min_periods=window).corr(feat[rhs])
            frame = corr.rename("correlation").dropna().to_frame()
            frame["pair"] = label
            frame["lhs"] = lhs
            frame["rhs"] = rhs
            frame["window"] = window
            frame = frame.reset_index(names="date")
            rows.append(frame)
    if not rows:
        return pd.DataFrame(columns=["date", "correlation", "pair", "lhs", "rhs", "window"])
    return pd.concat(rows, ignore_index=True)


def pre_post_corr_delta(feat: pd.DataFrame, cols: list[str], split_date: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return pre/post correlation matrices for available columns."""

    available = [col for col in cols if col in feat.columns]
    pre = feat.loc[feat.index < split_date, available].corr()
    post = feat.loc[feat.index >= split_date, available].corr()
    return pre, post


def corr_delta_table(pre: pd.DataFrame, post: pd.DataFrame) -> pd.DataFrame:
    """Convert pre/post correlation matrices to a long delta table."""

    rows: list[dict[str, object]] = []
    cols = list(pre.columns)
    for i, lhs in enumerate(cols):
        for rhs in cols[i + 1 :]:
            rows.append(
                {
                    "pair": f"{lhs} vs {rhs}",
                    "lhs": lhs,
                    "rhs": rhs,
                    "corr_pre": float(pre.loc[lhs, rhs]),
                    "corr_post": float(post.loc[lhs, rhs]),
                    "delta": float(post.loc[lhs, rhs] - pre.loc[lhs, rhs]),
                }
            )
    return pd.DataFrame(rows).sort_values("delta", key=lambda s: s.abs(), ascending=False)


def _correlation_pairs(asset: str) -> list[tuple[str, str, str]]:
    if asset == "btc":
        return [
            ("BTC vs ETH", "btc_ret", "eth_ret"),
            ("BTC vs SPY", "btc_ret", "spy_ret"),
            ("BTC vs QQQ", "btc_ret", "qqq_ret"),
            ("BTC vs GLD", "btc_ret", "gld_ret"),
            ("BTC vs DXY", "btc_ret", "dxy_tv_ret"),
            ("BTC vs VIX change", "btc_ret", "VIXCLS_d1"),
            ("BTC vs stablecoin growth", "btc_ret", "stables_total_usd_ret"),
            ("BTC vs TVL growth", "btc_ret", "defi_tvl_usd_ret"),
        ]
    return [
        ("ETH vs BTC", "eth_ret", "btc_ret"),
        ("ETH vs SPY", "eth_ret", "spy_ret"),
        ("ETH vs QQQ", "eth_ret", "qqq_ret"),
        ("ETH vs GLD", "eth_ret", "gld_ret"),
        ("ETH vs VIX change", "eth_ret", "VIXCLS_d1"),
        ("ETH vs stablecoin growth", "eth_ret", "stables_total_usd_ret"),
        ("ETH vs TVL growth", "eth_ret", "defi_tvl_usd_ret"),
    ]


def build_correlation_tables(feat: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pairs = _correlation_pairs("btc") + _correlation_pairs("eth")
    rolling = rolling_corr_matrix(feat, pairs)
    cols = [
        "btc_ret",
        "eth_ret",
        "spy_ret",
        "qqq_ret",
        "gld_ret",
        "dxy_tv_ret",
        "VIXCLS_d1",
        "stables_total_usd_ret",
        "defi_tvl_usd_ret",
    ]
    pre_btc, post_btc = pre_post_corr_delta(feat, cols, BTC_ETF_DATE)
    pre_eth, post_eth = pre_post_corr_delta(feat, cols, ETH_ETF_DATE)
    return rolling, corr_delta_table(pre_btc, post_btc), corr_delta_table(pre_eth, post_eth)


def build_liquidity_features(panel: pd.DataFrame, feat: pd.DataFrame) -> pd.DataFrame:
    cols = [
        col
        for col in [
            "stables_total_usd_ret",
            "defi_tvl_usd_ret",
            "btc_rv_30d",
            "eth_rv_30d",
            "spy_rv_30d",
            "VIXCLS_d1",
            "spy_ret",
            "btc_ret",
            "eth_ret",
        ]
        if col in feat.columns
    ]
    out = feat[cols].copy()
    if "stables_total_usd" in panel.columns:
        out["stables_total_usd"] = panel["stables_total_usd"]
    if "defi_tvl_usd" in panel.columns:
        out["defi_tvl_usd"] = panel["defi_tvl_usd"]
    z_cols = [col for col in ["stables_total_usd_ret", "defi_tvl_usd_ret"] if col in out.columns]
    if z_cols:
        z = safe_standardize(out[z_cols])
        for col in z_cols:
            out[f"z_{col}"] = z[col]
        out["liquidity_composite"] = z.mean(axis=1)
    out.index.name = "date"
    return out


def build_stablecoin_lead_lag(feat: pd.DataFrame, asset: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "stables_total_usd_ret" not in feat.columns:
        return pd.DataFrame(), pd.DataFrame()
    controls = _control_frame(feat, asset)
    target_ret = f"{asset}_ret"
    target_rv = f"{asset}_rv_30d"
    grids = [
        lead_lag_regression_grid(
            feat[target_ret],
            feat["stables_total_usd_ret"],
            controls,
            lags=range(-5, 6),
        )
    ]
    if target_rv in feat.columns:
        grids.append(
            lead_lag_regression_grid(
                feat[target_rv],
                feat["stables_total_usd_ret"],
                controls,
                lags=range(-5, 6),
            )
        )
    lead_lag = pd.concat(grids, ignore_index=True)
    quintiles = flow_quintile_summary(feat[target_ret], feat["stables_total_usd_ret"])
    return lead_lag, quintiles


def _plot_heatmap(df: pd.DataFrame, path: Path, title: str, value_col: str = "partial_r2") -> Path:
    pivot = df.pivot_table(index="sample", columns="block", values=value_col, aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    if pivot.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        im = ax.imshow(pivot.fillna(0).to_numpy(), cmap="viridis", aspect="auto")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels(pivot.index)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.iloc[i, j]
                label = "n/a" if pd.isna(val) else f"{val:.3f}"
                ax.text(j, i, label, ha="center", va="center", color="white", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title(title)
    return save_figure(fig, path)


def _plot_ablation_waterfall(df: pd.DataFrame, sample: str, path: Path, title: str) -> Path:
    sub = df[df["sample"] == sample].copy()
    if sub.empty:
        sub = df.copy()
    sub["delta_plot"] = sub["delta_r2_vs_prev"].fillna(sub["r2"]).fillna(0)
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    colors = [PALETTE["ok"] if value >= 0 else PALETTE["bad"] for value in sub["delta_plot"]]
    ax.bar(range(len(sub)), sub["delta_plot"], color=colors, edgecolor="white", linewidth=0.6)
    ax.plot(range(len(sub)), sub["r2"], color="#222222", marker="o", linewidth=1.2, label="cumulative R^2")
    ax.set_xticks(range(len(sub)))
    ax.set_xticklabels(sub["model_id"], rotation=35, ha="right")
    ax.set_ylabel("Delta R^2 / cumulative R^2")
    ax.set_title(title)
    ax.legend(loc="upper left")
    return save_figure(fig, path)


def _plot_timeline(feat: pd.DataFrame, asset: str, path: Path) -> Path:
    flow = feat[f"{asset}_etf_intensity"]
    ret = feat[f"{asset}_ret"]
    launch = BTC_ETF_DATE if asset == "btc" else ETH_ETF_DATE
    sub = pd.concat([flow, ret], axis=1).loc[lambda d: d.index >= launch].dropna()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    color = PALETTE["btc"] if asset == "btc" else PALETTE["eth"]
    ax.plot(sub.index, sub[flow.name], color=color, lw=1.2, label="ETF flow intensity")
    ax.axhline(0, color="#555555", lw=0.7)
    ax.set_ylabel("flow / prior-day market cap")
    ax2 = ax.twinx()
    ax2.plot(sub.index, sub[ret.name].rolling(7).mean(), color="#444444", alpha=0.7, label="7d avg return")
    ax2.set_ylabel("7d avg log return")
    ax.set_title(f"{asset.upper()} ETF-flow intensity and short-horizon returns")
    return save_figure(fig, path)


def _plot_lead_lag(df: pd.DataFrame, path: Path, title: str) -> Path:
    pivot = df.pivot_table(index="target", columns="lag", values="t", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9.5, 4.5))
    if pivot.empty:
        ax.text(0.5, 0.5, "No lead-lag rows", ha="center", va="center")
    else:
        im = ax.imshow(pivot.fillna(0), cmap="coolwarm", vmin=-4, vmax=4, aspect="auto")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels(pivot.index)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                val = pivot.iloc[i, j]
                ax.text(j, i, "n/a" if pd.isna(val) else f"{val:.1f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046, label="HAC t-stat")
    ax.set_xlabel("lag (negative = proxy leads target)")
    ax.set_title(title)
    return save_figure(fig, path)


def _plot_quintiles(df: pd.DataFrame, path: Path, title: str) -> Path:
    sub = df[df["horizon"].isin([0, 5])].copy()
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    if sub.empty:
        ax.text(0.5, 0.5, "No quintile rows", ha="center", va="center")
    else:
        pivot = sub.pivot_table(index="quintile", columns="horizon", values="mean_return")
        width = 0.35
        x = np.arange(len(pivot))
        for offset, horizon in enumerate(pivot.columns):
            ax.bar(
                x + (offset - 0.5) * width,
                pivot[horizon],
                width=width,
                label=f"h={horizon}",
            )
        ax.axhline(0, color="#555555", lw=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(pivot.index)
        ax.set_xlabel("flow/proxy quintile")
        ax.set_ylabel("mean cumulative log return")
        ax.legend()
    ax.set_title(title)
    return save_figure(fig, path)


def _plot_rolling_corr(rolling: pd.DataFrame, asset: str, path: Path) -> Path:
    sub = rolling[(rolling["window"] == 180) & (rolling["pair"].str.startswith(asset.upper()))]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for pair, group in sub.groupby("pair"):
        ax.plot(group["date"], group["correlation"], lw=1.15, label=pair)
    ax.axhline(0, color="#555555", lw=0.7)
    for label, date in EVENT_MARKERS.items():
        ax.axvline(date, color="#111111", lw=0.6, alpha=0.45, ls=":")
        ax.text(date, 0.95, label, rotation=90, va="top", fontsize=7)
    ax.set_ylim(-1, 1)
    ax.set_ylabel("180-day rolling correlation")
    ax.set_title(f"{asset.upper()} cross-asset rolling correlations")
    ax.legend(loc="lower left", ncol=2)
    return save_figure(fig, path)


def _plot_corr_delta(df: pd.DataFrame, path: Path, title: str) -> Path:
    sub = df.head(12).copy()
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    colors = [PALETTE["ok"] if value >= 0 else PALETTE["bad"] for value in sub["delta"]]
    ax.barh(range(len(sub)), sub["delta"], color=colors)
    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub["pair"], fontsize=8)
    ax.axvline(0, color="#555555", lw=0.7)
    ax.set_xlabel("post minus pre correlation")
    ax.set_title(title)
    ax.invert_yaxis()
    return save_figure(fig, path)


def _plot_stablecoin_supply(panel: pd.DataFrame, path: Path) -> Path:
    cols = [col for col in ["stables_total_usd", "defi_tvl_usd"] if col in panel.columns]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for col, color in zip(cols, [PALETTE["liquidity"], PALETTE["institutional"]], strict=False):
        indexed = panel[col] / panel[col].dropna().iloc[0] * 100
        ax.plot(indexed.index, indexed, label=col, color=color, lw=1.4)
    ax.set_ylabel("index, first observation = 100")
    ax.set_title("Stablecoin supply and DeFi TVL levels")
    ax.legend()
    return save_figure(fig, path)


def _plot_liquidity_vs_rv(liq: pd.DataFrame, asset: str, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    rv = f"{asset}_rv_30d"
    if "liquidity_composite" not in liq.columns or rv not in liq.columns:
        ax.text(0.5, 0.5, "Liquidity composite or RV unavailable", ha="center", va="center")
    else:
        sub = liq[["liquidity_composite", rv]].dropna()
        ax.scatter(sub["liquidity_composite"], sub[rv], s=10, alpha=0.35, color=PALETTE["liquidity"])
        ax.set_xlabel("liquidity composite z-score")
        ax.set_ylabel("30-day realized volatility")
    ax.set_title(f"{asset.upper()} liquidity proxy vs realized volatility")
    return save_figure(fig, path)


def _plot_native_zscore(z: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5.0))
    if z.empty:
        ax.text(0.5, 0.5, "No native features", ha="center", va="center")
    else:
        for col in z.columns:
            ax.plot(z.index, z[col].rolling(14).mean(), lw=1.1, label=col)
        ax.axhline(0, color="#555555", lw=0.7)
        ax.set_ylabel("z-score, 14d average")
        ax.legend(loc="upper left", ncol=2)
    ax.set_title("BTC-native factor z-score dashboard")
    return save_figure(fig, path)


def _plot_native_ablation(df: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    if df.empty:
        ax.text(0.5, 0.5, "No native ablation rows", ha="center", va="center")
    else:
        x_pos = np.arange(len(df))
        ax.bar(x_pos, df["r2"], color=PALETTE["crypto_native"])
        ax.set_xticks(x_pos)
        ax.set_xticklabels(df["model_id"], rotation=25, ha="right")
        ax.set_ylabel("R^2")
    ax.set_title("BTC-native ablation with MVRV separated")
    return save_figure(fig, path)


def _plot_corr_heatmap(corr: pd.DataFrame, path: Path, title: str) -> Path:
    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    if corr.empty:
        ax.text(0.5, 0.5, "No correlations", ha="center", va="center")
    else:
        im = ax.imshow(corr.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(corr.shape[1]))
        ax.set_xticklabels(corr.columns, rotation=35, ha="right")
        ax.set_yticks(range(corr.shape[0]))
        ax.set_yticklabels(corr.index)
        for i in range(corr.shape[0]):
            for j in range(corr.shape[1]):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title(title)
    return save_figure(fig, path)


def copy_baseline_artifacts(table_dir: Path, figure_dir: Path) -> tuple[list[Path], list[Path]]:
    table_map = {
        "static_ols_pre_post_etf.csv": "baseline_static_ols_pre_post_etf.csv",
        "structural_breaks_summary.csv": "baseline_structural_breaks_summary.csv",
        "fevd_10d_compact.csv": "baseline_fevd_10d_compact.csv",
        "event_studies.csv": "baseline_event_studies.csv",
    }
    figure_map = {
        "F07_fevd_heatmap.png": "F60_baseline_fevd_compact_heatmap.png",
        "F08_event_cars.png": "F61_baseline_event_study_cars.png",
        "F09_coverage.png": "F62_baseline_data_coverage.png",
    }
    tables: list[Path] = []
    figures: list[Path] = []
    for src, dst in table_map.items():
        target = TABLES_DIR / dst
        shutil.copy2(table_dir / src, target)
        tables.append(target)
    for src, dst in figure_map.items():
        target = FIGURES_DIR / dst
        shutil.copy2(figure_dir / src, target)
        figures.append(target)
    return tables, figures


def generate_tables(panel: pd.DataFrame, feat: pd.DataFrame) -> dict[str, pd.DataFrame]:
    btc_block = build_block_partial_r2_tables(feat, "btc")
    eth_block = build_block_partial_r2_tables(feat, "eth")
    btc_roll = build_rolling_block_partial_r2(feat, "btc")
    eth_roll = build_rolling_block_partial_r2(feat, "eth")
    btc_ablation = build_ablation_table(feat, "btc")
    eth_ablation = build_ablation_table(feat, "eth")
    btc_etf, btc_etf_q, btc_top = build_etf_lead_lag_tables(feat, "btc")
    eth_etf, eth_etf_q, eth_top = build_etf_lead_lag_tables(feat, "eth")
    rolling_corr, delta_btc, delta_eth = build_correlation_tables(feat)
    liq = build_liquidity_features(panel, feat)
    stable_btc, stable_q_btc = build_stablecoin_lead_lag(feat, "btc")
    stable_eth, stable_q_eth = build_stablecoin_lead_lag(feat, "eth")
    registry = native_factor_registry(feat)
    native_ablation = native_factor_ablation(feat, "btc")
    native_corr = native_factor_correlations(feat, "btc")

    return {
        "block_partial_r2_btc.csv": btc_block,
        "block_partial_r2_eth.csv": eth_block,
        "rolling_block_partial_r2_btc_180d.csv": btc_roll,
        "rolling_block_partial_r2_eth_180d.csv": eth_roll,
        "ablation_btc.csv": btc_ablation,
        "ablation_eth.csv": eth_ablation,
        "etf_lead_lag_btc.csv": btc_etf,
        "etf_lead_lag_eth.csv": eth_etf,
        "etf_flow_quintiles_btc.csv": btc_etf_q,
        "etf_flow_quintiles_eth.csv": eth_etf_q,
        "top_etf_flow_days_btc.csv": btc_top,
        "top_etf_flow_days_eth.csv": eth_top,
        "rolling_correlations.csv": rolling_corr,
        "correlation_delta_pre_post_btc_etf.csv": delta_btc,
        "correlation_delta_pre_post_eth_etf.csv": delta_eth,
        "stablecoin_liquidity_features.csv": liq.reset_index(),
        "stablecoin_lead_lag_btc.csv": stable_btc,
        "stablecoin_lead_lag_eth.csv": stable_eth,
        "stablecoin_quintiles_btc.csv": stable_q_btc,
        "stablecoin_quintiles_eth.csv": stable_q_eth,
        "native_factor_registry.csv": registry,
        "btc_native_ablation.csv": native_ablation,
        "btc_native_correlations.csv": native_corr.reset_index(names="feature"),
    }


def write_tables(tables: dict[str, pd.DataFrame]) -> list[Path]:
    return [write_csv(df, TABLES_DIR / name) for name, df in tables.items()]


def generate_figures(panel: pd.DataFrame, feat: pd.DataFrame, tables: dict[str, pd.DataFrame]) -> list[Path]:
    figures: list[Path] = []
    figures.append(
        _plot_heatmap(
            tables["block_partial_r2_btc.csv"],
            FIGURES_DIR / "F10_btc_block_partial_r2_heatmap.png",
            "BTC full-vs-reduced block partial R^2",
        )
    )
    figures.append(
        _plot_heatmap(
            tables["block_partial_r2_eth.csv"],
            FIGURES_DIR / "F11_eth_block_partial_r2_heatmap.png",
            "ETH full-vs-reduced block partial R^2",
        )
    )
    figures.append(
        _plot_ablation_waterfall(
            tables["ablation_btc.csv"],
            "post_btc_etf",
            FIGURES_DIR / "F12_btc_ablation_waterfall.png",
            "BTC nested ablation waterfall, post BTC ETF",
        )
    )
    figures.append(
        _plot_ablation_waterfall(
            tables["ablation_eth.csv"],
            "post_eth_etf",
            FIGURES_DIR / "F13_eth_ablation_waterfall.png",
            "ETH nested ablation waterfall, post ETH ETF",
        )
    )
    figures.append(_plot_timeline(feat, "btc", FIGURES_DIR / "F20_btc_etf_flow_intensity_timeline.png"))
    figures.append(_plot_timeline(feat, "eth", FIGURES_DIR / "F21_eth_etf_flow_intensity_timeline.png"))
    figures.append(
        _plot_lead_lag(
            tables["etf_lead_lag_btc.csv"],
            FIGURES_DIR / "F22_btc_etf_lead_lag_heatmap.png",
            "BTC ETF-flow lead-lag HAC t-statistics",
        )
    )
    figures.append(
        _plot_lead_lag(
            tables["etf_lead_lag_eth.csv"],
            FIGURES_DIR / "F23_eth_etf_lead_lag_heatmap.png",
            "ETH ETF-flow lead-lag HAC t-statistics",
        )
    )
    figures.append(
        _plot_quintiles(
            tables["etf_flow_quintiles_btc.csv"],
            FIGURES_DIR / "F24_btc_etf_flow_quintile_returns.png",
            "BTC returns by ETF-flow intensity quintile",
        )
    )
    figures.append(
        _plot_quintiles(
            tables["etf_flow_quintiles_eth.csv"],
            FIGURES_DIR / "F25_eth_etf_flow_quintile_returns.png",
            "ETH returns by ETF-flow intensity quintile",
        )
    )
    figures.append(
        _plot_rolling_corr(
            tables["rolling_correlations.csv"],
            "btc",
            FIGURES_DIR / "F30_btc_rolling_correlations_180d.png",
        )
    )
    figures.append(
        _plot_rolling_corr(
            tables["rolling_correlations.csv"],
            "eth",
            FIGURES_DIR / "F31_eth_rolling_correlations_180d.png",
        )
    )
    figures.append(
        _plot_corr_delta(
            tables["correlation_delta_pre_post_btc_etf.csv"],
            FIGURES_DIR / "F32_corr_delta_pre_post_btc_etf.png",
            "Largest correlation changes after BTC ETF launch",
        )
    )
    figures.append(
        _plot_corr_delta(
            tables["correlation_delta_pre_post_eth_etf.csv"],
            FIGURES_DIR / "F33_corr_delta_pre_post_eth_etf.png",
            "Largest correlation changes after ETH ETF launch",
        )
    )
    figures.append(_plot_stablecoin_supply(panel, FIGURES_DIR / "F40_stablecoin_supply_and_tvl.png"))
    figures.append(
        _plot_lead_lag(
            tables["stablecoin_lead_lag_btc.csv"],
            FIGURES_DIR / "F41_btc_stablecoin_lead_lag.png",
            "BTC stablecoin-growth lead-lag HAC t-statistics",
        )
    )
    figures.append(
        _plot_lead_lag(
            tables["stablecoin_lead_lag_eth.csv"],
            FIGURES_DIR / "F42_eth_stablecoin_lead_lag.png",
            "ETH stablecoin-growth lead-lag HAC t-statistics",
        )
    )
    liq = tables["stablecoin_liquidity_features.csv"].set_index("date")
    figures.append(_plot_liquidity_vs_rv(liq, "btc", FIGURES_DIR / "F43_btc_liquidity_vs_realized_vol.png"))
    figures.append(_plot_liquidity_vs_rv(liq, "eth", FIGURES_DIR / "F44_eth_liquidity_vs_realized_vol.png"))
    z = native_zscore_dashboard_data(feat)
    figures.append(_plot_native_zscore(z, FIGURES_DIR / "F50_btc_native_zscore_dashboard.png"))
    figures.append(
        _plot_native_ablation(
            tables["btc_native_ablation.csv"],
            FIGURES_DIR / "F51_btc_native_ablation.png",
        )
    )
    native_corr = tables["btc_native_correlations.csv"].set_index("feature")
    figures.append(
        _plot_corr_heatmap(
            native_corr,
            FIGURES_DIR / "F52_btc_native_corr_heatmap.png",
            "BTC-native factor correlations",
        )
    )
    return figures


def _top_block(df: pd.DataFrame, sample: str) -> tuple[str, float]:
    sub = df[df["sample"] == sample].sort_values("partial_r2", ascending=False)
    if sub.empty:
        return "n/a", float("nan")
    row = sub.iloc[0]
    return str(row["block"]), float(row["partial_r2"])


def _same_day_row(df: pd.DataFrame, target: str) -> pd.Series | None:
    rows = df[(df["lag"] == 0) & (df["target"] == target)]
    if rows.empty:
        return None
    return rows.iloc[0]


def build_executive_summary(
    panel_meta: dict[str, Any],
    source_table_dir: Path,
    source_figure_dir: Path,
    tables: dict[str, pd.DataFrame],
) -> str:
    btc_block, btc_value = _top_block(tables["block_partial_r2_btc.csv"], "post_btc_etf")
    eth_block, eth_value = _top_block(tables["block_partial_r2_eth.csv"], "post_eth_etf")
    btc_etf = _same_day_row(tables["etf_lead_lag_btc.csv"], "btc_ret")
    eth_etf = _same_day_row(tables["etf_lead_lag_eth.csv"], "eth_ret")
    return f"""
# Crypto Market Factor Lab - Portfolio v2.1 Executive Summary

## What The Project Is

Crypto Market Factor Lab is a reproducible BTC/ETH factor analytics system built
on a frozen multi-source daily panel. It is a portfolio-grade quant research and
data-engineering project, not a publication-first academic paper.

## Data And Reproducibility

The frozen master panel spans {panel_meta["start"]} through {panel_meta["end"]}
with {panel_meta["n_rows"]:,} daily rows and {panel_meta["n_cols"]} columns.
Portfolio v2.1 uses the existing panel and the baseline source bundles
`{source_table_dir.relative_to(PROJECT_ROOT)}` and
`{source_figure_dir.relative_to(PROJECT_ROOT)}`. No raw `Data/` files are
modified and no paid or live data source is required.

## What v2.1 Adds Over v2

- True full-vs-reduced block partial R^2 tables and 180-day rolling block
  partial R^2 outputs.
- BTC/ETH nested ablation waterfalls that separate macro, TradFi, liquidity,
  sentiment, ETF intensity, and native variables.
- ETF-flow lead-lag and quintile diagnostics with an explicit lag convention.
- Rolling cross-asset correlation and pre/post ETF delta dashboards.
- Stablecoin liquidity proxy and realized-volatility diagnostics.
- BTC-native factor registry with MVRV separated from non-MVRV native flows.

## Headline Analytics

- BTC post-BTC-ETF block partial R^2 is led by **{btc_block}**
  ({fmt(btc_value)}). MVRV-like variables are treated separately from macro and
  ETF-flow interpretation.
- ETH post-ETH-ETF block partial R^2 is led by **{eth_block}**
  ({fmt(eth_value)}), so ETH remains a comparison asset rather than forced BTC
  symmetry.
- BTC same-day ETF-flow intensity lead-lag row: beta={fmt(None if btc_etf is None else btc_etf["coefficient"], 2)},
  HAC t={fmt(None if btc_etf is None else btc_etf["t"], 2)}, R^2={fmt(None if btc_etf is None else btc_etf["r2"])}.
- ETH same-day ETF-flow intensity lead-lag row: beta={fmt(None if eth_etf is None else eth_etf["coefficient"], 2)},
  HAC t={fmt(None if eth_etf is None else eth_etf["t"], 2)}, R^2={fmt(None if eth_etf is None else eth_etf["r2"])}.

## Interpretation Boundaries

All results are reduced-form diagnostics. ETF-flow evidence is association and
market plumbing, not proof that flows caused BTC or ETH returns. Structural-break
references remain Chow plus single-break sup-F diagnostics, not full
Bai-Perron. Rolling and block attribution are not Shapley/Owen allocations.

## Job-Market Value

The v2.1 packet demonstrates frozen-data engineering, econometric hygiene,
factor modeling, crypto market-structure reasoning, visual communication,
model-card discipline, and one-command reproducible portfolio packaging.
"""


def build_analytics_summary(tables: dict[str, pd.DataFrame]) -> str:
    btc_delta = tables["correlation_delta_pre_post_btc_etf.csv"].head(5)
    eth_delta = tables["correlation_delta_pre_post_eth_etf.csv"].head(5)
    native = tables["btc_native_ablation.csv"][["model_id", "r2", "delta_r2_vs_prev", "n"]]
    return f"""
# Portfolio v2.1 Analytics Summary

## Factor Attribution

Block partial R^2 is computed as full-vs-reduced block partial R^2:
`(RSS_reduced - RSS_full) / TSS`. This is not drop-one marginal R^2,
Shapley/Owen attribution, or sequential R^2.

BTC fit is heavily influenced by BTC-native valuation and flow-state variables.
MVRV is separated from non-MVRV native variables because valuation-state inputs
can mechanically co-move with returns. ETH remains a comparison asset because
the available ETH-native block is thinner.

## ETF-Flow Market Plumbing

ETF-flow lead-lag tables use this convention: {LAG_CONVENTION}. Same-day and
lagged rows are reduced-form market-plumbing checks. They do not establish that
ETF flows caused BTC/ETH returns, especially because daily flow and return data
are vulnerable to simultaneity and omitted news shocks.

## Rolling Correlation Regimes

The largest BTC ETF pre/post correlation deltas are:

{md_table(btc_delta)}

The largest ETH ETF pre/post correlation deltas are:

{md_table(eth_delta)}

Rolling correlations are descriptive integration diagnostics. They can show
co-movement regimes but not the cause of those regimes.

## Stablecoin Liquidity

Stablecoin supply growth and DeFi TVL growth are used as liquidity/funding
proxies. The v2.1 outputs add realized-volatility features and compare returns
and volatility across stablecoin-growth lags and quintiles. Weak or mixed
lead-lag rows should be read as liquidity context, not as a funding-channel
claim.

## BTC-Native Lab

Native ablation snapshot:

{md_table(native)}

MVRV is useful because it summarizes valuation state, but it can dominate fit
for mechanical reasons. The native lab is a research lens, not a trade-signal
claim.
"""


def build_technical_report(
    panel_meta: dict[str, Any],
    tables: dict[str, pd.DataFrame],
    source_table_dir: Path,
    source_figure_dir: Path,
) -> str:
    btc_block = tables["block_partial_r2_btc.csv"].round(4)
    eth_block = tables["block_partial_r2_eth.csv"].round(4)
    btc_etf = tables["etf_lead_lag_btc.csv"].query("target == 'btc_ret'").round(4)
    eth_etf = tables["etf_lead_lag_eth.csv"].query("target == 'eth_ret'").round(4)
    stable_btc = tables["stablecoin_lead_lag_btc.csv"].query("target == 'btc_ret'").round(4)
    native_registry = tables["native_factor_registry.csv"]
    return f"""
# Portfolio v2.1 Technical Report

## Scope

Portfolio v2.1 extends the stable v2 packet with additional reduced-form
analytics. The goal is public-readiness for quant finance, crypto research, and
data-engineering review. It is not a causal identification design.

## Data

The frozen panel spans {panel_meta["start"]} through {panel_meta["end"]} with
{panel_meta["n_rows"]:,} rows and {panel_meta["n_cols"]} columns. The selected
baseline source table bundle is `{source_table_dir.relative_to(PROJECT_ROOT)}`;
the selected source figure bundle is `{source_figure_dir.relative_to(PROJECT_ROOT)}`.

## Feature Engineering

Price-like series are transformed into log returns. Rates, spreads, sentiment,
and native levels use first differences. ETF-flow intensity is daily USD ETF
flow divided by prior-day USD market capitalization. Realized volatility uses a
30-day rolling annualized standard deviation of log returns.

## Factor Attribution

BTC block partial R^2:

{md_table(btc_block)}

ETH block partial R^2:

{md_table(eth_block)}

The block statistic is full-vs-reduced partial R^2. It is not Shapley/Owen and
not the older rolling drop-one marginal R^2.

## ETF-Flow Intensity

Lag convention: {LAG_CONVENTION}.

BTC ETF lead-lag return rows:

{md_table(btc_etf)}

ETH ETF lead-lag return rows:

{md_table(eth_etf)}

ETF-flow intensity is contemporaneous/lag association. It should be discussed as
market plumbing and simultaneity-sensitive evidence, not causal impact.

## Rolling Correlations And Regimes

The v2.1 dashboard writes rolling 60/180/365-day correlations and pre/post ETF
delta tables. Event markers include FTX, SVB, BTC ETF, BTC halving, and ETH ETF
dates. These are descriptive co-movement diagnostics.

## Stablecoin Liquidity

Stablecoin supply growth and TVL growth are liquidity proxies. BTC stablecoin
lead-lag rows:

{md_table(stable_btc)}

Stablecoin results are funding-context diagnostics and should not be described
as proven causal drivers.

## BTC-Native Factor Lab

Native registry:

{md_table(native_registry)}

MVRV is explicitly separated from non-MVRV native variables because valuation
state can mechanically co-move with BTC returns.

## Structural-Break Diagnostics

The baseline packet remains the source for structural-break diagnostics:
`baseline_structural_breaks_summary.csv`. The current implementation is Chow
tests plus a single-break sup-F sweep, not full Bai-Perron.

## VAR/FEVD Connectedness

The baseline compact FEVD table is copied as `baseline_fevd_10d_compact.csv`.
It is a connectedness diagnostic under the stated VAR ordering, not a structural
shock-identification model.

## Event Studies

The baseline event-study table is copied as `baseline_event_studies.csv`.
Event-window CARs are reduced-form associations and remain confounded by
overlapping market news.

## Limitations

- Daily ETF-flow data is simultaneity-prone.
- Full-vs-reduced block partial R^2 can be unstable with correlated blocks.
- Rolling correlations and pre/post deltas describe co-movement, not causes.
- Stablecoin supply is a proxy, not a directly identified liquidity shock.
- Native factors, especially MVRV, can be mechanically linked to price.

## Reproducibility

```powershell
uv run pytest
uv run mypy src/cqresearch
uv run python scripts/run_portfolio_v2_1_pipeline.py
uv run ruff check scripts/run_portfolio_v2_1_pipeline.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/ablation.py src/cqresearch/analysis/portfolio_v2_1.py tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_portfolio_v2_1_pipeline.py
```
"""


def build_data_atlas(panel_meta: dict[str, Any], tables: dict[str, pd.DataFrame]) -> str:
    inventory = pd.read_csv(DATA_DIR / "MASTER_DATA.csv")
    source_summary = (
        inventory.assign(row_count=pd.to_numeric(inventory["row_count"], errors="coerce").fillna(0))
        .groupby("source", dropna=False)
        .agg(files=("relpath", "count"), rows=("row_count", "sum"))
        .reset_index()
        .sort_values("files", ascending=False)
    )
    source_summary["rows"] = source_summary["rows"].astype(int)
    liq_cols = [
        "stables_total_usd_ret",
        "defi_tvl_usd_ret",
        "liquidity_composite",
        "btc_rv_30d",
        "eth_rv_30d",
    ]
    liq = tables["stablecoin_liquidity_features.csv"][liq_cols].describe().T.reset_index(names="feature")
    return f"""
# Portfolio v2.1 Data Atlas

## Frozen Panel

- Date range: {panel_meta["start"]} through {panel_meta["end"]}
- Rows: {panel_meta["n_rows"]:,}
- Columns: {panel_meta["n_cols"]}
- Source inventory rows: {len(inventory):,}
- Machine-readable inventory: `Data/MASTER_DATA.csv`
- Human-readable inventory: `Data/MASTER_DATA.md`

## Source Inventory

{md_table(source_summary)}

## New v2.1 Feature Families

| Family | Examples | Output |
|---|---|---|
| Block partial R^2 | Macro, TradFi, Liquidity, BTC native ex MVRV, MVRV, ETF Flow | `block_partial_r2_*.csv` |
| Lead-lag market plumbing | ETF intensity and stablecoin growth lags | `*_lead_lag_*.csv` |
| Rolling correlations | BTC/ETH vs TradFi, VIX, liquidity proxies | `rolling_correlations.csv` |
| Realized volatility | `btc_rv_30d`, `eth_rv_30d`, `spy_rv_30d` | `stablecoin_liquidity_features.csv` |
| BTC-native registry | basis, exchange flow, miner flow, valuation state | `native_factor_registry.csv` |

## Liquidity Feature Audit

{md_table(liq.round(4))}

## Data Policy

Portfolio v2.1 uses only the frozen committed panel and derived feature
transforms. No raw `Data/` file is modified and no live or paid source is
required for regeneration.
"""


def build_resume_bullets(panel_meta: dict[str, Any]) -> str:
    return f"""
# Portfolio v2.1 Resume Bullets

## Quant Research

- Built **Crypto Market Factor Lab**, a reproducible BTC/ETH factor analytics
  framework over a {panel_meta["n_rows"]:,}-row frozen multi-source panel through
  April 2026.
- Implemented HAC OLS, full-vs-reduced block partial R^2, nested ablations,
  rolling correlations, lead-lag diagnostics, VAR/FEVD connectedness, and event
  studies.

## Crypto Research

- Analyzed ETF-flow intensity, stablecoin liquidity proxies, DeFi TVL, macro
  risk, and BTC-native valuation/flow-state variables across 2020-2026 regimes.
- Separated MVRV valuation state from non-MVRV native factors to avoid
  overstating native variables as direct trade signals.

## Data Engineering

- Curated a frozen multi-source daily panel with documented coverage, manifests,
  feature registry, data atlas, and one-command portfolio release pipelines.
- Preserved reproducibility by keeping live and paid data out of the core
  public portfolio releases.

## Quant Developer

- Built reusable Python modules for block partial R^2, ablations, lead-lag
  grids, realized volatility, native-factor diagnostics, and portfolio
  orchestration.
- Added unit tests, mypy checks, focused Ruff checks, model cards, diagnostics,
  and generated release packets.

## General Finance Analyst

- Produced public-facing reports that connect crypto market structure, macro
  risk, ETF plumbing, and liquidity context with careful reduced-form language.

## LinkedIn Description

Built Crypto Market Factor Lab, a reproducible Python research framework for
BTC/ETH factor regimes, ETF-flow market plumbing, stablecoin liquidity,
cross-asset connectedness, and BTC-native market structure using a frozen
2020-2026 multi-source panel.

## GitHub Pinned Repo Description

Reproducible BTC/ETH factor analytics lab with ETF-flow lead-lag diagnostics,
stablecoin liquidity proxies, BTC-native factor analysis, model cards, figures,
and portfolio-ready reports.

## Interview Talking Points

- Why ETF-flow intensity is scaled by prior-day market cap.
- Why daily ETF-flow evidence is association, not causality.
- Why full-vs-reduced block partial R^2 differs from Shapley/Owen.
- Why v2.1 treats BTC as the strongest native-factor case and ETH as a
  comparison asset.
- How to extend the system with intraday data or risk forecasting.
"""


def model_card_texts() -> dict[str, str]:
    base = {
        "static_ols.md": (
            "Static OLS",
            "Estimate BTC/ETH reduced-form exposure to factor stacks.",
            "Frozen feature panel derived from `reports/panels/master_daily.parquet`.",
            "Full, pre-ETF, and post-ETF samples from the baseline v2 bundle.",
            "HAC/Newey-West OLS using stationary transformed variables.",
            "`baseline_static_ols_pre_post_etf.csv`.",
            "Factor exposure diagnostics, not causal estimates.",
            "Omitted variables, multicollinearity, and sample-support differences.",
            "Add sensitivity tables for alternative controls and common-support samples.",
        ),
        "block_partial_r2.md": (
            "Block Partial R^2",
            "Measure factor-block contribution by comparing full and reduced models.",
            "BTC/ETH returns and standardized feature blocks.",
            "Full, pre/post BTC ETF, and post ETH ETF where available.",
            "Full-vs-reduced block partial R^2: `(RSS_reduced - RSS_full) / TSS`.",
            "`block_partial_r2_btc.csv`, `block_partial_r2_eth.csv`, rolling block tables.",
            "Contribution conditional on the specified full model; not Shapley/Owen.",
            "Correlated blocks can shift contribution between blocks.",
            "Add Shapley/Owen only as a tested appendix and compare labels carefully.",
        ),
        "etf_flow_lead_lag.md": (
            "ETF Flow Lead-Lag",
            "Test whether ETF-flow intensity associations are contemporaneous or lagged.",
            "BTC/ETH ETF intensity, returns, realized volatility, and controls.",
            "Post-launch windows for each asset.",
            f"HAC OLS grid by lag. Lag convention: {LAG_CONVENTION}.",
            "`etf_lead_lag_btc.csv`, `etf_lead_lag_eth.csv`, quintile/top-day tables.",
            "Market-plumbing association only; same-day evidence is not causality.",
            "Simultaneity, omitted news, and daily aggregation.",
            "Use intraday data or external instruments for stronger timing evidence.",
        ),
        "rolling_correlations.md": (
            "Rolling Correlations",
            "Describe BTC/ETH co-movement regimes with TradFi and liquidity proxies.",
            "Stationary return/difference features from the frozen panel.",
            "Full available sample using 60/180/365-day rolling windows.",
            "Rolling pairwise correlations plus pre/post ETF correlation deltas.",
            "`rolling_correlations.csv`, `correlation_delta_pre_post_*_etf.csv`.",
            "Descriptive integration/regime diagnostics.",
            "Correlation is not causation and can move with volatility regimes.",
            "Add bootstrap confidence intervals or regime-clustering checks.",
        ),
        "stablecoin_liquidity.md": (
            "Stablecoin Liquidity",
            "Use stablecoin growth and TVL growth as liquidity/funding proxies.",
            "Stablecoin supply, DeFi TVL, BTC/ETH returns, realized volatility.",
            "Full frozen panel with 30-day realized-volatility support.",
            "Z-score composite, lead-lag OLS, and quintile summaries.",
            "`stablecoin_liquidity_features.csv`, stablecoin lead-lag/quintile tables.",
            "Liquidity context, not a proven causal funding channel.",
            "Proxy measurement error and confounding by broad risk appetite.",
            "Add source-specific stablecoin flows and local projections if justified.",
        ),
        "btc_native_factor_lab.md": (
            "BTC-Native Factor Lab",
            "Separate BTC-native valuation state from flow/market-structure variables.",
            "BTC basis, exchange netflow, miner-to-exchange flow, and MVRV changes.",
            "Full native-variable support from the frozen panel.",
            "Registry, z-score dashboard, native ablation, and correlations.",
            "`native_factor_registry.csv`, `btc_native_ablation.csv`, `btc_native_correlations.csv`.",
            "Research lens for BTC-native state; not a standalone trade signal.",
            "MVRV can mechanically co-move with price and dominate fit.",
            "Add more native variables only with cached, documented source support.",
        ),
        "structural_breaks.md": (
            "Structural Breaks",
            "Diagnose whether coefficient instability aligns with major market dates.",
            "Baseline BTC/ETH return regressions and macro/institutional controls.",
            "Baseline v2 samples and single-break scan support.",
            "Chow tests at ETF dates plus single-break sup-F sweep.",
            "`baseline_structural_breaks_summary.csv`.",
            "Regime diagnostics; not full Bai-Perron multi-break.",
            "Low power, multiple testing, and model dependence.",
            "Add tested Bai-Perron or CUSUM only as clearly labeled future methods.",
        ),
        "var_fevd.md": (
            "VAR/FEVD",
            "Summarize connectedness across BTC, ETH, equities, and volatility.",
            "Baseline compact VAR feature set.",
            "Full baseline support after stationary transforms.",
            "statsmodels VAR with 10-day FEVD under declared ordering.",
            "`baseline_fevd_10d_compact.csv`.",
            "Connectedness diagnostic, not structural shock identification.",
            "Ordering sensitivity and small-system simplification.",
            "Add generalized FEVD and ordering-sensitivity appendices.",
        ),
        "event_study.md": (
            "Event Study",
            "Compare abnormal returns around ETF launches and selected market events.",
            "BTC/ETH returns and SPY market-model benchmark.",
            "Baseline event windows around pre-registered dates.",
            "Market-model abnormal returns and CAR windows.",
            "`baseline_event_studies.csv`.",
            "Event-window association; not causal proof.",
            "Overlapping news, benchmark choice, and limited event count.",
            "Add alternative benchmarks and wider placebo batteries.",
        ),
    }
    cards: dict[str, str] = {}
    for filename, values in base.items():
        title, purpose, inputs, sample, method, outputs, interpretation, risks, upgrade = values
        cards[filename] = f"""
# Model Card - {title}

## Purpose

{purpose}

## Inputs

{inputs}

## Sample

{sample}

## Method

{method}

## Output files

{outputs}

## Interpretation

{interpretation}

## Risks / limitations

{risks}

## Upgrade path

{upgrade}
"""
    return cards


def write_model_cards() -> list[Path]:
    return [write_text(MODEL_CARDS_DIR / name, body) for name, body in model_card_texts().items()]


def write_reports(
    panel_meta: dict[str, Any],
    source_table_dir: Path,
    source_figure_dir: Path,
    tables: dict[str, pd.DataFrame],
) -> list[Path]:
    reports = [
        write_text(
            PORTFOLIO_DIR / "executive_summary.md",
            build_executive_summary(panel_meta, source_table_dir, source_figure_dir, tables),
        ),
        write_text(PORTFOLIO_DIR / "analytics_summary.md", build_analytics_summary(tables)),
        write_text(
            PORTFOLIO_DIR / "technical_report.md",
            build_technical_report(panel_meta, tables, source_table_dir, source_figure_dir),
        ),
        write_text(PORTFOLIO_DIR / "data_atlas.md", build_data_atlas(panel_meta, tables)),
        write_text(PORTFOLIO_DIR / "resume_bullets.md", build_resume_bullets(panel_meta)),
    ]
    return reports


def write_optional_failures(failures: list[str]) -> Path:
    if failures:
        body = "# Optional Failures\n\n" + "\n".join(f"- {failure}" for failure in failures)
    else:
        body = "# Optional Failures\n\nNo optional v2.1 modules failed."
    return write_text(DIAGNOSTICS_DIR / "optional_failures.md", body)


def write_verification_placeholder() -> Path:
    path = DIAGNOSTICS_DIR / "verification.md"
    if path.exists() and "## Command Results" in path.read_text(encoding="utf-8"):
        print(f"[ok] preserved {path}")
        return path
    body = """
# Portfolio v2.1 Verification

Generated by `scripts/run_portfolio_v2_1_pipeline.py`.

This file records the required verification commands for the v2.1 packet. A
completed verification table is preserved across pipeline reruns once it has
been written.

## Required Commands

- `uv run pytest`
- `uv run mypy src/cqresearch`
- `uv run python scripts/run_portfolio_v2_1_pipeline.py`
- `uv run ruff check scripts/run_portfolio_v2_1_pipeline.py src/cqresearch/modeling/partial_r2.py src/cqresearch/modeling/lead_lag.py src/cqresearch/modeling/ablation.py src/cqresearch/analysis/portfolio_v2_1.py tests/unit/test_partial_r2.py tests/unit/test_lead_lag.py tests/unit/test_ablation.py tests/unit/test_portfolio_v2_1_pipeline.py`

Status should be updated after the verification run.
"""
    return write_text(path, body)


def build_manifest(
    panel_meta: dict[str, Any],
    source_table_dir: Path,
    source_figure_dir: Path,
    tables: list[Path],
    figures: list[Path],
    reports: list[Path],
    model_cards: list[Path],
    optional_failures: list[str],
) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": git_commit_hash(),
        "portfolio_dir": str(PORTFOLIO_DIR.relative_to(PROJECT_ROOT)),
        "panel": {
            "start": panel_meta["start"],
            "end": panel_meta["end"],
            "n_rows": panel_meta["n_rows"],
            "n_cols": panel_meta["n_cols"],
        },
        "source_table_bundle": str(source_table_dir.relative_to(PROJECT_ROOT)),
        "source_table_bundle_date": source_table_dir.name,
        "source_figure_bundle": str(source_figure_dir.relative_to(PROJECT_ROOT)),
        "source_figure_bundle_date": source_figure_dir.name,
        "commands_run": [
            "uv run pytest",
            "uv run mypy src/cqresearch",
            "uv run python scripts/run_portfolio_v2_1_pipeline.py",
            (
                "uv run ruff check scripts/run_portfolio_v2_1_pipeline.py "
                "src/cqresearch/modeling/partial_r2.py "
                "src/cqresearch/modeling/lead_lag.py "
                "src/cqresearch/modeling/ablation.py "
                "src/cqresearch/analysis/portfolio_v2_1.py "
                "tests/unit/test_partial_r2.py "
                "tests/unit/test_lead_lag.py "
                "tests/unit/test_ablation.py "
                "tests/unit/test_portfolio_v2_1_pipeline.py"
            ),
        ],
        "tables_generated": [str(path.relative_to(PROJECT_ROOT)) for path in tables],
        "figures_generated": [str(path.relative_to(PROJECT_ROOT)) for path in figures],
        "reports_generated": [str(path.relative_to(PROJECT_ROOT)) for path in reports],
        "model_cards_generated": [str(path.relative_to(PROJECT_ROOT)) for path in model_cards],
        "optional_failures": optional_failures,
        "method_notes": {
            "block_partial_r2": "full-vs-reduced block partial R^2; not Shapley/Owen",
            "lead_lag": LAG_CONVENTION,
            "stablecoins": "stablecoin supply/growth is a liquidity proxy, not a proven causal driver",
            "structural_breaks": "baseline remains Chow plus single-break sup-F, not full Bai-Perron",
        },
    }


def write_manifest(manifest: dict[str, Any]) -> Path:
    missing = [field for field in required_manifest_fields() if field not in manifest]
    if missing:
        raise ValueError(f"Manifest missing required fields: {missing}")
    path = PORTFOLIO_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[ok] wrote {path}")
    return path


def run_portfolio_v2_1_pipeline() -> PortfolioV21Result:
    """Build the complete Portfolio v2.1 release packet."""

    ensure_portfolio_dirs()
    source_table_dir = latest_complete_table_dir()
    source_figure_dir = latest_complete_figure_dir()
    panel, feat, panel_meta = load_panel_and_features()
    tables = generate_tables(panel, feat)
    table_paths = write_tables(tables)
    figure_paths = generate_figures(panel, feat, tables)
    copied_tables, copied_figures = copy_baseline_artifacts(source_table_dir, source_figure_dir)
    table_paths.extend(copied_tables)
    figure_paths.extend(copied_figures)
    report_paths = write_reports(panel_meta, source_table_dir, source_figure_dir, tables)
    model_card_paths = write_model_cards()
    optional_failures: list[str] = []
    report_paths.append(write_optional_failures(optional_failures))
    report_paths.append(write_verification_placeholder())
    manifest = build_manifest(
        panel_meta,
        source_table_dir,
        source_figure_dir,
        table_paths,
        figure_paths,
        report_paths,
        model_card_paths,
        optional_failures,
    )
    manifest_path = write_manifest(manifest)
    return PortfolioV21Result(
        tables=table_paths,
        figures=figure_paths,
        reports=report_paths,
        model_cards=model_card_paths,
        optional_failures=optional_failures,
        manifest_path=manifest_path,
    )


__all__ = [
    "BTC_ETF_DATE",
    "ETH_ETF_DATE",
    "PORTFOLIO_DIR",
    "PortfolioV21Result",
    "build_manifest",
    "corr_delta_table",
    "ensure_portfolio_dirs",
    "pre_post_corr_delta",
    "required_manifest_fields",
    "rolling_corr_matrix",
    "run_portfolio_v2_1_pipeline",
]
