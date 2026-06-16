"""Render README-ready institutional visuals from canonical output tables."""

from __future__ import annotations

import html
import shutil
import sys
import textwrap
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.build_visual_gallery import (  # noqa: E402
    build_current_contact_sheet,
    build_final_gallery,
)

from cqresearch.viz.annotations import add_event_markers, add_source_footer  # noqa: E402
from cqresearch.viz.cards import (  # noqa: E402
    add_card_background,
    add_header,
    add_pill,
)
from cqresearch.viz.design_system import (  # noqa: E402
    COLORS,
    FACTOR_COLORS,
    FIGURE_SET,
    HERO_SIZE,
    factor_color,
)
from cqresearch.viz.export import save_figure  # noqa: E402
from cqresearch.viz.theme import (  # noqa: E402
    apply_institutional_mpl_theme,
    close,
    style_axis,
    style_legend,
)

OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"
REPORT = OUTPUTS / "report"
DASHBOARD = OUTPUTS / "dashboard"
V21 = ROOT / "archive" / "legacy_portfolio_releases" / "portfolio_v2_1"
V22 = ROOT / "archive" / "legacy_portfolio_releases" / "portfolio_v2_2"

SUPPLEMENTAL_TABLES: tuple[tuple[Path, str], ...] = (
    (V21 / "tables" / "rolling_block_partial_r2_btc_180d.csv", "T03_rolling_block_partial_r2_btc_180d.csv"),
    (V21 / "tables" / "rolling_correlations.csv", "T05_rolling_correlations.csv"),
    (V21 / "tables" / "native_factor_registry.csv", "T07_native_factor_registry.csv"),
    (V21 / "tables" / "btc_native_correlations.csv", "T07_btc_native_correlations.csv"),
    (V22 / "tables" / "rolling_connectedness.csv", "T09_rolling_connectedness.csv"),
)


def ensure_dirs() -> None:
    for path in (FIGURES, TABLES, REPORT, DASHBOARD):
        path.mkdir(parents=True, exist_ok=True)


def ensure_supplemental_tables() -> list[str]:
    """Surface existing archived tables needed by the new public figures."""

    copied: list[str] = []
    for src, filename in SUPPLEMENTAL_TABLES:
        if not src.exists():
            continue
        dst = TABLES / filename
        shutil.copy2(src, dst)
        copied.append(dst.relative_to(ROOT).as_posix())
    return copied


def load_csv(filename: str, **kwargs: object) -> pd.DataFrame:
    path = TABLES / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, **kwargs)


def money_b(value: float) -> str:
    return f"USD {value / 1_000_000_000:,.0f}B"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def add_date_axis(ax: plt.Axes, *, max_ticks: int = 7) -> None:
    locator = mdates.AutoDateLocator(minticks=4, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def make_chart(
    filename: str,
    title: str,
    subtitle: str | None = None,
    footer: str | None = None,
    *,
    axes_rect: list[float] | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    apply_institutional_mpl_theme()
    fig = plt.figure(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(fig, title, subtitle or "")
    ax = fig.add_axes(axes_rect or [0.075, 0.17, 0.85, 0.61])
    style_axis(ax)
    if footer:
        add_source_footer(fig, footer)
    fig.set_label(filename)
    return fig, ax


def save_public(fig: plt.Figure, filename: str) -> list[Path]:
    output = FIGURES / filename
    saved = save_figure(fig, output, formats=("png", "svg"))
    close(fig)
    return saved


def render_f00() -> list[Path]:
    fig, ax = make_chart(
        "F00_project_summary_card.png",
        "Project Pipeline",
        "",
        "",
        axes_rect=[0.055, 0.12, 0.89, 0.68],
    )
    ax.set_axis_off()
    methods = [
        ("Data", COLORS["btc"]),
        ("Features", COLORS["eth"]),
        ("Models", COLORS["institutional"]),
        ("Outputs", COLORS["gold"]),
    ]
    for idx, (label, color) in enumerate(methods):
        x = 0.15 + idx * 0.22
        y = 0.5
        add_pill(fig, x=x, y=y, text=label, color=color)
        if idx < len(methods) - 1:
            ax.annotate("", xy=(x + 0.14, y), xytext=(x + 0.08, y), arrowprops={"arrowstyle": "->", "color": COLORS["text"], "lw": 2}, xycoords="figure fraction")
    return save_public(fig, "F00_project_summary_card.png")


def render_f01() -> list[Path]:
    inventory = load_csv("T01_source_inventory.csv")
    inventory["start_date"] = pd.to_datetime(inventory["start_date"], errors="coerce")
    inventory["end_date"] = pd.to_datetime(inventory["end_date"], errors="coerce")
    grouped = (
        inventory.dropna(subset=["start_date", "end_date"])
        .groupby("source", as_index=False)
        .agg(start=("start_date", "min"), end=("end_date", "max"), files=("relpath", "count"))
        .sort_values("start")
    )
    fig, ax = make_chart(
        "F01_data_coverage.png",
        "Data Coverage",
        "",
        "",
    )
    y = np.arange(len(grouped))
    left = mdates.date2num(grouped["start"].dt.to_pydatetime())
    right = mdates.date2num(grouped["end"].dt.to_pydatetime())
    colors = [COLORS["btc"], COLORS["eth"], COLORS["institutional"], COLORS["liquidity"], COLORS["macro"], COLORS["native"], COLORS["gold"]]
    for idx, row in grouped.reset_index(drop=True).iterrows():
        ax.barh(idx, right[idx] - left[idx], left=left[idx], height=0.58, color=colors[idx % len(colors)], alpha=0.86)
        ax.text(right[idx] + 28, idx, f"{int(row['files'])} files", va="center", fontsize=7.5, color=COLORS["muted"])
    ax.set_yticks(y, grouped["source"])
    ax.set_xlim(pd.Timestamp("2019-09-01"), pd.Timestamp("2026-08-01"))
    ax.set_ylim(-0.8, len(grouped) - 0.2)
    ax.invert_yaxis()
    add_date_axis(ax)
    add_event_markers(ax, label_y=0.94)
    ax.set_xlabel("Source coverage window")

    return save_public(fig, "F01_data_coverage.png")


def render_f02() -> list[Path]:
    static = load_csv("T03_block_attribution.csv")
    rolling = load_csv("T03_rolling_block_partial_r2_btc_180d.csv", parse_dates=["date"])
    full = static.query("asset == 'btc' and sample == 'full'").copy()
    fig = plt.figure(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(
        fig,
        "BTC Factor Attribution",
        "",
    )
    ax = fig.add_axes([0.07, 0.18, 0.58, 0.58])
    ax2 = fig.add_axes([0.71, 0.18, 0.22, 0.58])
    style_axis(ax)
    style_axis(ax2)
    pivot = (
        rolling.pivot_table(index="date", columns="block", values="partial_r2", aggfunc="mean")
        .sort_index()
        .resample("MS")
        .mean()
        .fillna(0)
        .clip(lower=0)
    )
    block_order = [block for block in FACTOR_COLORS if block in pivot.columns]
    block_order += [block for block in pivot.columns if block not in block_order]
    pivot = pivot[block_order]
    ax.stackplot(
        pivot.index,
        *[pivot[col] for col in pivot.columns],
        labels=pivot.columns,
        colors=[factor_color(col) for col in pivot.columns],
        alpha=0.86,
        linewidth=0,
    )
    ax.set_ylabel("Rolling block partial R2")
    ax.set_ylim(bottom=0)
    add_date_axis(ax)
    add_event_markers(ax, label_y=0.97)
    style_legend(ax, ncol=2, loc="upper left")

    full = full.sort_values("partial_r2", ascending=True)
    ax2.barh(full["block"], full["partial_r2"], color=[factor_color(block) for block in full["block"]], alpha=0.9)
    ax2.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax2.set_xlabel("Full-sample drop")
    ax2.grid(axis="x", color=COLORS["grid"], alpha=0.55)
    ax2.grid(axis="y", visible=False)
    ax2.set_title("Static block removal", fontsize=9, color=COLORS["text"], loc="left", pad=10)
    mvrv = full.loc[full["block"].eq("BTC MVRV"), "partial_r2"]
    if not mvrv.empty:
        ax2.text(
            float(mvrv.iloc[0]),
            list(full["block"]).index("BTC MVRV"),
            f"  {pct(float(mvrv.iloc[0]))}",
            va="center",
            fontsize=8,
            color=COLORS["text"],
        )

    return save_public(fig, "F02_btc_block_attribution.png")


def render_f03() -> list[Path]:
    lead_lag = load_csv("T04_etf_lead_lag.csv")
    btc = lead_lag.query("asset == 'btc' and target == 'btc_ret'").sort_values("lag")
    fig, ax = make_chart(
        "F03_btc_etf_lead_lag.png",
        "ETF Flow Lead-Lag",
        "",
        "",
    )
    colors = [
        COLORS["neutral"] if lag < 0 else COLORS["institutional"] if lag == 0 else COLORS["btc"]
        for lag in btc["lag"]
    ]
    ax.bar(btc["lag"], btc["t"], color=colors, edgecolor=COLORS["surface2"], linewidth=0.8, alpha=0.92)
    ax.axhline(0, color=COLORS["axis"], linewidth=0.8)
    ax.axhline(1.96, color=COLORS["grid"], linestyle="--", linewidth=0.8)
    ax.axhline(-1.96, color=COLORS["grid"], linestyle="--", linewidth=0.8)
    ax.set_xlabel("Lag convention: lag < 0 means flow leads return")
    ax.set_ylabel("HAC t-statistic")
    ax.set_xticks(btc["lag"])
    ax.set_ylim(min(-2.5, float(btc["t"].min()) - 1.0), float(btc["t"].max()) + 1.4)

    same_day = btc.loc[btc["lag"].eq(0)].iloc[0]
    ax.text(
        same_day["lag"] + 0.35,
        same_day["t"],
        f"same-day t={same_day['t']:.1f}\\ncoef={same_day['coefficient']:.1f}",
        fontsize=8,
        color=COLORS["text"],
        va="center",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": COLORS["surface2"], "edgecolor": COLORS["institutional"]},
    )
    return save_public(fig, "F03_btc_etf_lead_lag.png")


def render_f04() -> list[Path]:
    corr = load_csv("T05_rolling_correlations.csv", parse_dates=["date"])
    pairs = ["BTC vs ETH", "BTC vs SPY", "BTC vs GLD", "BTC vs DXY", "BTC vs VIX change"]
    labels = {
        "BTC vs ETH": "ETH",
        "BTC vs SPY": "SPY",
        "BTC vs GLD": "Gold",
        "BTC vs DXY": "DXY",
        "BTC vs VIX change": "VIX chg",
    }
    colors = {
        "BTC vs ETH": COLORS["eth"],
        "BTC vs SPY": COLORS["institutional"],
        "BTC vs GLD": COLORS["gold"],
        "BTC vs DXY": COLORS["macro"],
        "BTC vs VIX change": COLORS["risk"],
    }
    fig, ax = make_chart(
        "F04_btc_rolling_correlations.png",
        "Rolling Correlations",
        "",
        "",
    )
    plot = corr.loc[corr["window"].eq(180) & corr["pair"].isin(pairs)].copy()
    for pair in pairs:
        part = plot.loc[plot["pair"].eq(pair)].sort_values("date")
        ax.plot(part["date"], part["correlation"], label=labels[pair], color=colors[pair], linewidth=1.45)
    ax.axhline(0, color=COLORS["axis"], linewidth=0.8)
    ax.set_ylim(-0.75, 1.0)
    ax.set_ylabel("180-day correlation")
    add_date_axis(ax)
    add_event_markers(ax, label_y=0.96)
    style_legend(ax, ncol=5, loc="upper left")
    return save_public(fig, "F04_btc_rolling_correlations.png")


def render_f05() -> list[Path]:
    liq = load_csv("T06_stablecoin_liquidity.csv", parse_dates=["date"])
    liq = liq.sort_values("date").set_index("date")
    monthly = liq.resample("MS").mean(numeric_only=True)
    for col in ("stables_total_usd", "defi_tvl_usd"):
        first = monthly[col].dropna().iloc[0]
        monthly[f"{col}_idx"] = monthly[col] / first * 100
    fig = plt.figure(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(
        fig,
        "Stablecoins and TVL",
        "",
    )
    ax = fig.add_axes([0.07, 0.42, 0.86, 0.33])
    ax2 = fig.add_axes([0.07, 0.17, 0.86, 0.17], sharex=ax)
    style_axis(ax)
    style_axis(ax2)
    ax.plot(monthly.index, monthly["stables_total_usd_idx"], color=COLORS["stablecoin"], label="Stablecoin supply", linewidth=1.8)
    ax.plot(monthly.index, monthly["defi_tvl_usd_idx"], color=COLORS["liquidity"], label="DeFi TVL", linewidth=1.8)
    ax.set_ylabel("Index, Jan 2020 = 100")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    style_legend(ax, ncol=2, loc="upper left")
    ax2.plot(monthly.index, monthly["btc_rv_30d"], color=COLORS["btc"], label="BTC RV", linewidth=1.1)
    ax2.plot(monthly.index, monthly["eth_rv_30d"], color=COLORS["eth"], label="ETH RV", linewidth=1.1)
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax2.set_ylabel("30d RV")
    style_legend(ax2, ncol=2, loc="upper left")
    for axis in (ax, ax2):
        add_date_axis(axis)
        add_event_markers(axis, label_y=0.94, alpha=0.55)

    final_supply = money_b(float(monthly["stables_total_usd"].dropna().iloc[-1]))
    final_tvl = money_b(float(monthly["defi_tvl_usd"].dropna().iloc[-1]))
    ax.text(
        0.72,
        0.12,
        f"Apr 2026 context\\nStablecoins: {final_supply}\\nDeFi TVL: {final_tvl}",
        transform=ax.transAxes,
        fontsize=8,
        color=COLORS["text"],
        bbox={"boxstyle": "round,pad=0.35", "facecolor": COLORS["surface2"], "edgecolor": COLORS["grid"]},
    )

    return save_public(fig, "F05_stablecoin_supply_tvl.png")


def render_f06() -> list[Path]:
    ablation = load_csv("T07_native_factor_ablation.csv")
    corr = load_csv("T07_btc_native_correlations.csv")
    fig = plt.figure(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(
        fig,
        "BTC Native State",
        "",
    )
    ax = fig.add_axes([0.095, 0.18, 0.36, 0.58])
    ax2 = fig.add_axes([0.56, 0.18, 0.36, 0.58])
    style_axis(ax)
    style_axis(ax2)
    plot = ablation.loc[ablation["model_id"].ne("N0_intercept")].copy()
    label_map = {
        "N1_native_ex_mvrv": "Flow ex-MVRV",
        "N2_mvrv_only": "MVRV only",
        "N3_all_native": "All native",
    }
    plot["label"] = plot["model_id"].map(label_map).fillna(plot["model_id"])
    plot = plot.sort_values("r2", ascending=True)
    colors = [COLORS["native"] if "Mvrv" in label else COLORS["btc"] for label in plot["label"]]
    ax.barh(plot["label"], plot["r2"], color=colors, alpha=0.9)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("R2")
    ax.set_title("Native ablation", loc="left", fontsize=9.5, color=COLORS["text"], pad=10)
    for y_pos, row in enumerate(plot.itertuples(index=False)):
        value = float(row.r2)
        if value > 0.25:
            ax.text(value - 0.018, y_pos, pct(value), ha="right", va="center", fontsize=8, color=COLORS["text"])
        else:
            ax.text(value + 0.015, y_pos, pct(value), ha="left", va="center", fontsize=8, color=COLORS["text"])

    features = [col for col in corr.columns if col != "feature"]
    matrix = corr.set_index("feature")[features].loc[features]
    cmap = LinearSegmentedColormap.from_list("native_heat", [COLORS["surface2"], COLORS["macro"], COLORS["native"]])
    im = ax2.imshow(matrix.values, vmin=-1, vmax=1, cmap=cmap, aspect="auto")
    ax2.set_xticks(np.arange(len(features)), [label.replace("_d1", "").replace("_", " ") for label in features], rotation=35, ha="right")
    ax2.set_yticks(np.arange(len(features)), [label.replace("_d1", "").replace("_", " ") for label in features])
    for row_idx in range(matrix.shape[0]):
        for col_idx in range(matrix.shape[1]):
            val = matrix.values[row_idx, col_idx]
            ax2.text(col_idx, row_idx, f"{val:.2f}", ha="center", va="center", fontsize=6.8, color=COLORS["text"])
    ax2.set_title("Native correlation matrix", loc="left", fontsize=9.5, color=COLORS["text"], pad=10)
    cbar = fig.colorbar(im, ax=ax2, fraction=0.035, pad=0.02)
    cbar.ax.tick_params(colors=COLORS["muted"], labelsize=7, length=0)


    return save_public(fig, "F06_btc_native_dashboard.png")


def render_f07() -> list[Path]:
    fevd = load_csv("T09_connectedness.csv").set_index("to")
    rolling = load_csv("T09_rolling_connectedness.csv", parse_dates=["date"])
    fig = plt.figure(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(
        fig,
        "Connectedness",
        "",
    )
    ax = fig.add_axes([0.07, 0.19, 0.38, 0.56])
    ax2 = fig.add_axes([0.55, 0.19, 0.38, 0.56])
    style_axis(ax)
    style_axis(ax2)
    cmap = LinearSegmentedColormap.from_list("fevd_heat", [COLORS["surface2"], COLORS["macro"], COLORS["eth"], COLORS["btc"]])
    im = ax.imshow(fevd.values, vmin=0, vmax=1, cmap=cmap)
    ax.set_xticks(np.arange(fevd.shape[1]), fevd.columns, rotation=35, ha="right")
    ax.set_yticks(np.arange(fevd.shape[0]), fevd.index)
    ax.set_title("10-day FEVD share", loc="left", fontsize=9.5, color=COLORS["text"], pad=10)
    for row_idx in range(fevd.shape[0]):
        for col_idx in range(fevd.shape[1]):
            val = fevd.values[row_idx, col_idx]
            ax.text(col_idx, row_idx, f"{val:.2f}", ha="center", va="center", fontsize=7.2, color=COLORS["text"])
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.03)
    cbar.ax.tick_params(colors=COLORS["muted"], labelsize=7, length=0)

    ax2.plot(rolling["date"], rolling["connectedness_pct"], color=COLORS["risk"], linewidth=1.7)
    ax2.fill_between(rolling["date"], rolling["connectedness_pct"], color=COLORS["risk"], alpha=0.12)
    ax2.set_ylabel("Total connectedness index")
    ax2.set_title("Rolling VAR/FEVD connectedness", loc="left", fontsize=9.5, color=COLORS["text"], pad=10)
    add_date_axis(ax2)
    add_event_markers(ax2, label_y=0.95, alpha=0.6)


    return save_public(fig, "F07_connectedness.png")


def render_f08() -> list[Path]:
    robust = load_csv("T10_robustness.csv")
    grouped = (
        robust.dropna(subset=["r2"])
        .groupby(["window", "hac_lags", "include_mvrv"], as_index=False)
        .agg(r2=("r2", "mean"))
    )
    fig = plt.figure(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(
        fig,
        "Robustness Grid",
        "",
    )
    axes = [fig.add_axes([0.075, 0.20, 0.38, 0.54]), fig.add_axes([0.545, 0.20, 0.38, 0.54])]
    cmap = LinearSegmentedColormap.from_list("robust_heat", [COLORS["surface2"], COLORS["macro"], COLORS["liquidity"], COLORS["gold"]])
    ims = []
    for ax, include_mvrv, title in zip(axes, [True, False], ["With MVRV", "Without MVRV"], strict=True):
        style_axis(ax)
        matrix = grouped.loc[grouped["include_mvrv"].eq(include_mvrv)].pivot(index="window", columns="hac_lags", values="r2")
        im = ax.imshow(matrix.values, vmin=0, vmax=1, cmap=cmap, aspect="auto")
        ims.append(im)
        ax.set_xticks(np.arange(len(matrix.columns)), matrix.columns)
        ax.set_yticks(np.arange(len(matrix.index)), matrix.index)
        ax.set_xlabel("HAC lags")
        ax.set_ylabel("Training window")
        ax.set_title(title, loc="left", fontsize=9.5, color=COLORS["text"], pad=10)
        for row_idx in range(matrix.shape[0]):
            for col_idx in range(matrix.shape[1]):
                val = matrix.values[row_idx, col_idx]
                ax.text(col_idx, row_idx, f"{val:.2f}", ha="center", va="center", fontsize=8, color=COLORS["text"])
    cbar = fig.colorbar(ims[0], ax=axes, fraction=0.025, pad=0.02)
    cbar.ax.tick_params(colors=COLORS["muted"], labelsize=7, length=0)


    return save_public(fig, "F08_robustness_grid.png")


def key_result_rows() -> list[dict[str, str]]:
    attribution = load_csv("T03_block_attribution.csv")
    lead_lag = load_csv("T04_etf_lead_lag.csv")
    liq = load_csv("T06_stablecoin_liquidity.csv", parse_dates=["date"])
    fevd = load_csv("T09_connectedness.csv").set_index("to")
    robust = load_csv("T10_robustness.csv")
    mvrv = attribution.query("asset == 'btc' and sample == 'full' and block == 'BTC MVRV'")["partial_r2"].iloc[0]
    same_day = lead_lag.query("asset == 'btc' and target == 'btc_ret' and lag == 0").iloc[0]
    final_liq = liq.dropna(subset=["stables_total_usd", "defi_tvl_usd"]).iloc[-1]
    with_mvrv = robust.loc[robust["include_mvrv"].eq(True), "r2"].mean()
    without_mvrv = robust.loc[robust["include_mvrv"].eq(False), "r2"].mean()
    return [
        {
            "result": "BTC native valuation state dominates full-stack fit",
            "stat": pct(float(mvrv)),
            "artifact": "T03 / F02",
            "interpretation": "Block partial R2 is conditional on the selected full model; not Shapley/Owen.",
        },
        {
            "result": "BTC ETF-flow intensity has a strong same-day association",
            "stat": f"t={same_day['t']:.1f}",
            "artifact": "T04 / F03",
            "interpretation": "Daily lead-lag evidence is market-plumbing association, not causal impact.",
        },
        {
            "result": "Stablecoin and DeFi liquidity context remains large by Apr 2026",
            "stat": f"{money_b(float(final_liq['stables_total_usd']))} / {money_b(float(final_liq['defi_tvl_usd']))}",
            "artifact": "T06 / F05",
            "interpretation": "Supply and TVL are liquidity proxies, not identified funding shocks.",
        },
        {
            "result": "ETH variance is materially explained by BTC shocks in compact FEVD",
            "stat": pct(float(fevd.loc["eth_ret", "btc_ret"])),
            "artifact": "T09 / F07",
            "interpretation": "FEVD output is Cholesky-order sensitive.",
        },
        {
            "result": "Robustness grid separates valuation-state fit from non-MVRV fit",
            "stat": f"{pct(float(with_mvrv))} vs {pct(float(without_mvrv))}",
            "artifact": "T10 / F08",
            "interpretation": "Grid summarizes sensitivity across windows, HAC lags, winsorization, and calendars.",
        },
    ]


def render_f09() -> list[Path]:
    rows = key_result_rows()
    fig, ax = make_chart(
        "F09_key_results_cards.png",
        "Key Results",
        "",
        "",
        axes_rect=[0.055, 0.15, 0.89, 0.66],
    )
    ax.set_axis_off()
    card_w, card_h = 0.42, 0.20
    x_positions = [0.02, 0.52]
    y_positions = [0.74, 0.47, 0.20]
    colors = [COLORS["native"], COLORS["institutional"], COLORS["stablecoin"], COLORS["eth"], COLORS["gold"]]
    for idx, row in enumerate(rows):
        x = x_positions[idx % 2]
        y = y_positions[idx // 2]
        rect = Rectangle((x, y), card_w, card_h, transform=ax.transAxes, color=COLORS["surface2"], ec=colors[idx], lw=1.0)
        ax.add_patch(rect)
        ax.text(x + 0.025, y + card_h - 0.045, row["stat"], transform=ax.transAxes, fontsize=16, fontweight="semibold", color=colors[idx])
        ax.text(
            x + 0.025,
            y + card_h - 0.095,
            textwrap.fill(row["result"], width=42),
            transform=ax.transAxes,
            fontsize=8.4,
            color=COLORS["text"],
        )

    return save_public(fig, "F09_key_results_cards.png")


def write_key_results_tables() -> list[Path]:
    rows = key_result_rows()
    md = [
        "# Key Results",
        "",
        "| Result | Stat | Artifact | Interpretation guardrail |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        md.append(
            f"| {row['result']} | {row['stat']} | {row['artifact']} | {row['interpretation']} |"
        )
    md_path = TABLES / "key_results.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    css = """
<style>
body{margin:0;background:#080B12;color:#E5E7EB;font-family:Inter,Segoe UI,Arial,sans-serif}
.wrap{max-width:1100px;margin:28px auto;padding:24px;background:#0F172A;border:1px solid #243044;border-radius:14px}
h1{font-size:24px;margin:0 0 8px}
p{color:#94A3B8;margin:0 0 20px}
table{border-collapse:collapse;width:100%;font-size:14px}
th{text-align:left;color:#94A3B8;font-size:12px;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #243044;padding:12px}
td{border-bottom:1px solid #243044;padding:14px 12px;vertical-align:top}
td:nth-child(2){color:#FBBF24;font-weight:700;white-space:nowrap}
.artifact{color:#2DD4BF;font-family:Consolas,monospace}
</style>
"""
    body_rows = []
    for row in rows:
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(row['result'])}</td>"
            f"<td>{html.escape(row['stat'])}</td>"
            f"<td class='artifact'>{html.escape(row['artifact'])}</td>"
            f"<td>{html.escape(row['interpretation'])}</td>"
            "</tr>"
        )
    html_path = TABLES / "key_results.html"
    html_path.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Key Results</title>"
        + css
        + "</head><body><div class='wrap'><h1>Crypto Market Factor Lab - Key Results</h1>"
        + "<p>Summary table generated from canonical output tables. Guardrails are part of the result.</p>"
        + "<table><thead><tr><th>Result</th><th>Stat</th><th>Artifact</th><th>Interpretation guardrail</th></tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></div></body></html>\n",
        encoding="utf-8",
    )

    table_readme = """
# Tables

CSV tables are the canonical machine-readable outputs. `key_results.md` and
`key_results.html` provide a compact public presentation layer for README and
dashboard review.

## Featured

- `key_results.md`
- `key_results.html`
- `T00_key_results_table.png` in `outputs/figures/`

## Canonical CSVs

- `T01_source_inventory.csv`
- `T02_panel_coverage.csv`
- `T03_block_attribution.csv`
- `T03_rolling_block_partial_r2_btc_180d.csv`
- `T04_etf_lead_lag.csv`
- `T05_correlation_regime.csv`
- `T05_rolling_correlations.csv`
- `T06_stablecoin_liquidity.csv`
- `T07_native_factor_ablation.csv`
- `T07_native_factor_registry.csv`
- `T07_btc_native_correlations.csv`
- `T08_structural_breaks.csv`
- `T09_connectedness.csv`
- `T09_rolling_connectedness.csv`
- `T10_robustness.csv`
"""
    readme_path = TABLES / "README.md"
    readme_path.write_text(table_readme.strip() + "\n", encoding="utf-8")
    return [md_path, html_path, readme_path]


def render_t00() -> list[Path]:
    rows = key_result_rows()
    fig, ax = make_chart(
        "T00_key_results_table.png",
        "Key Results Table",
        "",
        "",
        axes_rect=[0.05, 0.15, 0.90, 0.66],
    )
    ax.set_axis_off()
    col_x = [0.02, 0.52, 0.72, 0.83]
    headers = ["Result", "Stat", "Artifact", "Guardrail"]
    for x, header in zip(col_x, headers, strict=True):
        ax.text(x, 0.96, header.upper(), transform=ax.transAxes, fontsize=7.2, color=COLORS["muted"], fontweight="semibold")
    y = 0.84
    for idx, row in enumerate(rows):
        color = [COLORS["native"], COLORS["institutional"], COLORS["stablecoin"], COLORS["eth"], COLORS["gold"]][idx]
        ax.plot([0.02, 0.98], [y + 0.075, y + 0.075], transform=ax.transAxes, color=COLORS["grid"], linewidth=0.8)
        ax.text(col_x[0], y, textwrap.fill(row["result"], width=48), transform=ax.transAxes, fontsize=8.2, color=COLORS["text"])
        ax.text(col_x[1], y, row["stat"], transform=ax.transAxes, fontsize=10.5, color=color, fontweight="semibold")
        ax.text(col_x[2], y, row["artifact"], transform=ax.transAxes, fontsize=7.8, color=COLORS["institutional"])

        y -= 0.16
    return save_public(fig, "T00_key_results_table.png")


def write_dashboard() -> list[Path]:
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    figures = [
        "F00_project_summary_card.png",
        "F01_data_coverage.png",
        "F02_btc_block_attribution.png",
        "F03_btc_etf_lead_lag.png",
        "F04_btc_rolling_correlations.png",
        "F05_stablecoin_supply_tvl.png",
        "F06_btc_native_dashboard.png",
        "F07_connectedness.png",
        "F08_robustness_grid.png",
        "F09_key_results_cards.png",
        "T00_key_results_table.png",
    ]
    cards = "\n".join(
        f"<section class='card'><h2>{html.escape(filename.replace('_', ' ').replace('.png', ''))}</h2><img src='../figures/{filename}' alt='{html.escape(filename)}'></section>"
        for filename in figures
    )
    html_path = DASHBOARD / "index.html"
    html_path.write_text(
        """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Crypto Market Factor Lab Dashboard</title>
<style>
body{margin:0;background:#080B12;color:#E5E7EB;font-family:Inter,Segoe UI,Arial,sans-serif}
header{padding:32px 5vw 18px;border-bottom:1px solid #243044;background:#0F172A}
h1{margin:0 0 8px;font-size:32px}
p{margin:0;color:#94A3B8;max-width:980px;line-height:1.5}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:22px;padding:28px 5vw}
.card{background:#0F172A;border:1px solid #243044;border-radius:14px;padding:16px}
.card h2{font-size:15px;color:#94A3B8;margin:0 0 12px;text-transform:uppercase;letter-spacing:.04em}
img{width:100%;height:auto;border-radius:8px;border:1px solid #243044}
a{color:#2DD4BF}
</style>
</head>
<body>
<header>
<h1>Crypto Market Factor Lab</h1>
<p>Static, no-server dashboard assembled from reproducible outputs. The visuals are generated from frozen local artifacts and do not call live APIs.</p>
</header>
<main>
"""
        + cards
        + "\n</main></body></html>\n",
        encoding="utf-8",
    )
    readme_path = DASHBOARD / "README.md"
    readme_path.write_text(
        """# Static Dashboard

Open `index.html` to review the public visual packet as a standalone dashboard.
It embeds generated PNGs from `outputs/figures/` and uses no live APIs, server,
or external data refresh.
""",
        encoding="utf-8",
    )
    return [html_path, readme_path]


def write_visual_audit() -> Path:
    content = """
# Visual Audit

## Current Canonical Figures

The pre-redesign contact sheet is `outputs/figures/current_contact_sheet.png`.

| Figure | Current story | README-ready? | Weakness | Decision |
|---|---|---:|---|---|
| F01 data coverage | Dense coverage matrix | No | Tiny labels, white background, no grouped source story | Redesign as grouped source timeline |
| F02 block attribution | Raw heatmap | No | Default colormap, cramped labels, weak hierarchy | Replace with rolling stack plus static block summary |
| F03 ETF lead-lag | Raw t-stat heatmap | No | Small labels and caveat buried in footer | Replace with lag bar card and visible association warning |
| F04 rolling correlations | Crowded line chart | Partial | Too many series, weak event markers, default legend | Reduce series and annotate regimes |
| F05 stablecoin/TVL | Basic line chart | Partial | Dual story lacks proxy caveat and context panel | Rebuild as indexed liquidity plus realized-vol context |
| F06 native dashboard | Noisy z-score lines | No | Over-plotted, hard to separate MVRV from flows | Replace with native ablation and correlation dashboard |
| F07 connectedness | Single default line | No | No FEVD matrix or ordering caveat in visual | Combine FEVD matrix with rolling connectedness |
| F08 robustness | Raw heatmap | No | Default Viridis look and little interpretation | Replace with side-by-side robustness heatmaps |

## Visual System Weaknesses

- Font: default Matplotlib sizing and no consistent hierarchy.
- Colors: white backgrounds, Viridis defaults, and inconsistent block colors.
- Layout: no card system, inconsistent aspect ratios, cramped legends.
- Annotations: event markers and interpretation guardrails were not visible enough.
- README fit: figures depended on surrounding text and were not self-contained.

## Proposed Final Figure Set

F00 summary card, F01 source coverage, F02 BTC attribution, F03 ETF lead-lag,
F04 rolling correlations, F05 stablecoin/TVL, F06 BTC-native dashboard, F07
connectedness, F08 robustness, F09 key-results cards, and T00 key-results table.

## Design Acceptance Rubric

- 16:9 README-ready PNG plus SVG for F00-F09.
- Dark institutional theme with consistent source/method footer.
- Visible title, subtitle, and interpretation caveat where relevant.
- No causal ETF-flow language.
- No Bai-Perron label for current structural-break diagnostics.
- No Shapley/Owen label for block partial R2 figures.
- README image paths resolve and avoid archived release folders.
"""
    path = REPORT / "visual_audit.md"
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def figure_quality_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for meta in FIGURE_SET:
        png = FIGURES / meta.filename
        svg = png.with_suffix(".svg")
        width = height = 0
        dark_theme = False
        if png.exists():
            with Image.open(png) as image:
                width, height = image.size
                corner = image.crop((0, 0, min(80, width), min(80, height))).convert("L")
                dark_theme = float(np.asarray(corner).mean()) < 80
        rows.append(
            {
                "figure": meta.filename,
                "png": png.exists(),
                "svg": svg.exists(),
                "width": width,
                "height": height,
                "size_kb": round(png.stat().st_size / 1024, 1) if png.exists() else 0,
                "dark_theme": dark_theme,
            }
        )
    return rows


def write_visual_quality_check() -> Path:
    rows = figure_quality_rows()
    table = [
        "| Figure | PNG | SVG | Dimensions | Size KB | Dark theme |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        table.append(
            f"| {row['figure']} | {row['png']} | {row['svg']} | {row['width']}x{row['height']} | {row['size_kb']} | {row['dark_theme']} |"
        )
    content = f"""
# Visual Quality Check

Generated at: {datetime.now(UTC).isoformat()}

## Final Figures

{chr(10).join(table)}

## README Link Rules

- README image paths point to `outputs/figures/`.
- README does not point to archived portfolio release folders.
- F00-F09 are generated as both PNG and SVG.

## Dashboard

`outputs/dashboard/index.html` is a standalone static HTML dashboard built from
generated PNGs. Plotly/Kaleido is not required for the public static release.

## Known Visual Limitations

- F06 uses public ablation and correlation tables rather than a hidden raw
  native z-score time series, so it is a dashboard-style native summary instead
  of a dense line-z-score plot.
- F04 links to both rolling-correlation and pre/post delta outputs because the
  visual story uses rolling correlations while the public table also includes
  event deltas.
- All visuals remain reduced-form research artifacts and avoid causal claims.
"""
    path = REPORT / "visual_quality_check.md"
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def render_all_figures() -> list[Path]:
    ensure_dirs()
    ensure_supplemental_tables()
    build_current_contact_sheet()
    written: list[Path] = []
    written.extend(render_f00())
    written.extend(render_f01())
    written.extend(render_f02())
    written.extend(render_f03())
    written.extend(render_f04())
    written.extend(render_f05())
    written.extend(render_f06())
    written.extend(render_f07())
    written.extend(render_f08())
    write_key_results_tables()
    written.extend(render_f09())
    written.extend(render_t00())
    written.extend(write_dashboard())
    written.append(build_final_gallery())
    written.append(write_visual_audit())
    written.append(write_visual_quality_check())
    return written


def main() -> int:
    written = render_all_figures()
    for path in written:
        print(f"[ok] {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
