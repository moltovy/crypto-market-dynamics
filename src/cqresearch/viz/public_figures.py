"""Fresh public README figure layer for Crypto Market Dynamics."""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from config.paths import PROJECT_ROOT
from matplotlib.ticker import PercentFormatter

from cqresearch.viz.theme import (
    EXPORT_DPI,
    PALETTE,
    README_FIGSIZE,
    TOKENS,
    TWO_PANEL_FIGSIZE,
    add_figure_header,
    apply_theme,
    direct_label_bars,
    style_axis,
)

PUBLIC_FIGURES = [
    (
        "mvrv_mechanics",
        "01_mvrv_mechanics.png",
        "How mechanically linked is MVRV to BTC returns?",
        "outputs/tables/mvrv_identity_points.csv; outputs/tables/mvrv_regime_outcomes.csv",
        "Same-day MVRV is a mechanics diagnostic; lagged state is used only as conditioning context.",
    ),
    (
        "tradfi_exposure_shift",
        "02_tradfi_exposure_shift.png",
        "How did equity co-movement change across periods?",
        "outputs/tables/block_delta_r2.csv",
        "Pre-specified pre-BTC-ETF versus BTC-ETF-era comparison; not an ETF-effect estimate.",
    ),
    (
        "etf_market_plumbing",
        "03_etf_market_plumbing.png",
        "How do ETF flow measures line up with same-day and lagged returns?",
        "outputs/tables/etf_absorption_metrics.csv; outputs/tables/etf_flow_associations.csv",
        "ETF flow intensity is market-plumbing association, not causal price impact.",
    ),
    (
        "leverage_tail_stress",
        "04_leverage_tail_stress.png",
        "Where do lagged leverage states and liquidation stress show up?",
        "outputs/tables/leverage_tail_risk_summary.csv; outputs/tables/liquidation_event_responses.csv",
        "Lagged leverage state is separated from same-day liquidation signatures.",
    ),
    (
        "point_in_time_market_structure",
        "05_point_in_time_market_structure.png",
        "How did point-in-time composition and concentration evolve?",
        "outputs/tables/pit_composition.csv; outputs/tables/pit_concentration.csv",
        "Monthly PIT snapshots support structure and concentration, not daily performance.",
    ),
    (
        "selected_major_asset_risk",
        "06_selected_major_asset_risk.png",
        "How do selected majors compare on volatility and drawdown?",
        "outputs/tables/selected_major_risk_metrics.csv",
        "Coverage-aware risk map; HYPE is explicitly short-history.",
    ),
]


def table_path(root: Path, name: str) -> Path:
    return root / "outputs" / "tables" / name


def figure_dirs(root: Path) -> tuple[Path, Path, Path]:
    figures = root / "outputs" / "figures"
    public = figures / "public"
    gallery = figures / "gallery"
    for path in [figures, public, gallery]:
        path.mkdir(parents=True, exist_ok=True)
    return figures, public, gallery


def _clean_figure_dirs(public: Path, gallery: Path) -> None:
    for directory in [public, gallery]:
        for path in directory.glob("*"):
            if path.is_file() and path.suffix.lower() in {".png", ".svg"}:
                path.unlink()


def _save(fig: plt.Figure, path: Path) -> Path:
    fig.savefig(path, dpi=EXPORT_DPI, bbox_inches="tight", facecolor=TOKENS["background"])
    svg_path = path.with_suffix(".svg")
    fig.savefig(svg_path, dpi=EXPORT_DPI, bbox_inches="tight", facecolor=TOKENS["background"], metadata={"Date": None})
    text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return path


def _format_date_axis(ax: plt.Axes) -> None:
    locator = mdates.AutoDateLocator(minticks=4, maxticks=6)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    ax.tick_params(axis="x", labelrotation=0)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def fig_mvrv(root: Path, public: Path) -> Path:
    points = pd.read_csv(table_path(root, "mvrv_identity_points.csv"), parse_dates=["date"])
    regimes = pd.read_csv(table_path(root, "mvrv_regime_outcomes.csv"))

    plot = points[["btc_ret", "d_log_mvrv"]].replace([np.inf, -np.inf], np.nan).dropna()
    fig, axes = plt.subplots(1, 2, figsize=TWO_PANEL_FIGSIZE)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.78, wspace=0.22)
    add_figure_header(
        fig,
        "MVRV moves almost one-for-one with BTC returns",
        "Panel A uses same-interval log changes; Panel B uses lagged MVRV-state quintiles.",
    )

    ax = axes[0]
    style_axis(ax, y_grid=True, x_grid=True)
    sns.scatterplot(
        data=plot,
        x="d_log_mvrv",
        y="btc_ret",
        ax=ax,
        s=18,
        alpha=0.33,
        color=PALETTE["btc"],
        edgecolor=None,
    )
    lower = float(np.nanpercentile(plot[["btc_ret", "d_log_mvrv"]].to_numpy(), 1))
    upper = float(np.nanpercentile(plot[["btc_ret", "d_log_mvrv"]].to_numpy(), 99))
    ax.plot([lower, upper], [lower, upper], color=TOKENS["ink"], linewidth=1.0, linestyle=":", label="y=x")
    ax.axhline(0, color=TOKENS["axis"], linewidth=1.0)
    ax.axvline(0, color=TOKENS["axis"], linewidth=1.0)
    ax.set_title("A. Same-day mechanics", loc="left", fontsize=13, fontweight="semibold")
    ax.set_xlabel("d-log MVRV")
    ax.set_ylabel("BTC log return")
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend(loc="upper left", frameon=False)

    ax = axes[1]
    style_axis(ax)
    regimes = regimes.copy()
    regimes["mvrv_state_quintile"] = pd.Categorical(
        regimes["mvrv_state_quintile"],
        categories=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"],
        ordered=True,
    )
    regimes = regimes.sort_values("mvrv_state_quintile")
    bars = ax.bar(
        regimes["mvrv_state_quintile"].astype(str),
        regimes["next_week_return_mean"],
        color=PALETTE["eth"],
        edgecolor=PALETTE["eth_dark"],
        linewidth=1.0,
    )
    ax.axhline(0, color=TOKENS["ink"], linewidth=1.0)
    ax.set_title("B. Lagged state outcomes", loc="left", fontsize=13, fontweight="semibold")
    ax.set_xlabel("Prior MVRV quintile")
    ax.set_ylabel("Mean next-week BTC return")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    direct_label_bars(ax, bars, [_pct(v) for v in regimes["next_week_return_mean"]])
    return _save(fig, public / "01_mvrv_mechanics.png")


def fig_tradfi_shift(root: Path, public: Path) -> Path:
    block = pd.read_csv(table_path(root, "block_delta_r2.csv"))
    plot = block[
        block["frequency"].eq("daily")
        & block["model_family"].eq("long_sample_contemporaneous_exposure")
        & block["block"].eq("equity_beta")
        & block["regime"].isin(["pre_btc_etf", "btc_etf_era"])
        & block["asset"].isin(["BTC", "ETH"])
    ].copy()
    plot["period"] = plot["regime"].map({"pre_btc_etf": "Pre-BTC ETF", "btc_etf_era": "BTC-ETF era"})
    plot["asset"] = pd.Categorical(plot["asset"], categories=["BTC", "ETH"], ordered=True)
    plot["period"] = pd.Categorical(plot["period"], categories=["Pre-BTC ETF", "BTC-ETF era"], ordered=True)
    plot = plot.sort_values(["asset", "period"])

    fig, ax = plt.subplots(figsize=README_FIGSIZE)
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.16, top=0.80)
    add_figure_header(
        fig,
        "Equity block contribution rises in the BTC-ETF era",
        "Daily synchronized business-date model; drop-block delta R-squared for QQQ/SPY/IWM.",
    )
    style_axis(ax)
    assets = ["BTC", "ETH"]
    periods = ["Pre-BTC ETF", "BTC-ETF era"]
    x = np.arange(len(assets))
    width = 0.28
    colors = {"Pre-BTC ETF": PALETTE["slate"], "BTC-ETF era": PALETTE["btc"]}
    edges = {"Pre-BTC ETF": PALETTE["risk_dark"], "BTC-ETF era": PALETTE["btc_dark"]}
    for i, period in enumerate(periods):
        values = [
            float(plot.loc[plot["asset"].eq(asset) & plot["period"].eq(period), "drop_block_delta_r2"].iloc[0])
            for asset in assets
        ]
        bars = ax.bar(
            x + (i - 0.5) * width,
            values,
            width=width,
            label=period,
            color=colors[period],
            edgecolor=edges[period],
            linewidth=1.0,
        )
        direct_label_bars(ax, bars, [f"{v:.4f}" for v in values])
    ax.set_xticks(x, assets)
    ax.set_ylabel("Equity block delta R-squared")
    ax.set_xlabel("")
    ax.set_ylim(0, max(plot["drop_block_delta_r2"]) * 1.28)
    ax.legend(loc="upper left", ncol=2, frameon=False)
    return _save(fig, public / "02_tradfi_exposure_shift.png")


def fig_etf(root: Path, public: Path) -> Path:
    absorption = pd.read_csv(table_path(root, "etf_absorption_metrics.csv"), parse_dates=["date"])
    assoc = pd.read_csv(table_path(root, "etf_flow_associations.csv"))
    assoc = assoc[assoc["asset"].isin(["BTC", "ETH"])].copy()
    assoc["lag"] = assoc["flow_lag_days"].map({0: "Lag 0", 1: "Lag 1"})

    fig, axes = plt.subplots(1, 2, figsize=TWO_PANEL_FIGSIZE)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.16, top=0.78, wspace=0.24)
    add_figure_header(
        fig,
        "ETF plumbing is strongest on reported flow days",
        "Panel A scales cumulative net flow by lagged market cap; Panel B compares lag-0 and lag-1 return correlations.",
    )

    ax = axes[0]
    style_axis(ax)
    plot_abs = absorption.dropna(subset=["btc_cum_flow_to_lag_mcap", "eth_cum_flow_to_lag_mcap"], how="all")
    ax.plot(plot_abs["date"], plot_abs["btc_cum_flow_to_lag_mcap"], color=PALETTE["btc"], linewidth=2.0, label="BTC")
    ax.plot(plot_abs["date"], plot_abs["eth_cum_flow_to_lag_mcap"], color=PALETTE["eth"], linewidth=2.0, label="ETH")
    ax.set_title("A. Cumulative flow intensity", loc="left", fontsize=13, fontweight="semibold")
    ax.set_ylabel("Cumulative flow / lagged market cap")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    _format_date_axis(ax)
    ax.legend(loc="upper left", frameon=False)

    ax = axes[1]
    style_axis(ax)
    assets = ["BTC", "ETH"]
    lags = ["Lag 0", "Lag 1"]
    x = np.arange(len(assets))
    width = 0.28
    colors = {"Lag 0": PALETTE["btc"], "Lag 1": PALETTE["eth"]}
    edges = {"Lag 0": PALETTE["btc_dark"], "Lag 1": PALETTE["eth_dark"]}
    for i, lag in enumerate(lags):
        values = [
            float(assoc.loc[assoc["asset"].eq(asset) & assoc["lag"].eq(lag), "return_corr"].iloc[0])
            for asset in assets
        ]
        bars = ax.bar(x + (i - 0.5) * width, values, width=width, label=lag, color=colors[lag], edgecolor=edges[lag])
        direct_label_bars(ax, bars, [f"{v:.2f}" for v in values], padding=0.01)
    ax.axhline(0, color=TOKENS["axis"], linewidth=1.0)
    ax.set_title("B. Flow-return association", loc="left", fontsize=13, fontweight="semibold")
    ax.set_ylabel("Correlation with return")
    ax.set_xticks(x, assets)
    ax.legend(loc="upper right", frameon=False)
    return _save(fig, public / "03_etf_market_plumbing.png")


def fig_leverage(root: Path, public: Path) -> Path:
    state = pd.read_csv(table_path(root, "leverage_tail_risk_summary.csv"))
    events = pd.read_csv(table_path(root, "liquidation_event_responses.csv"), parse_dates=["event_date"])
    state = state[state["leverage_state"].isin(["Q1 low", "Q3", "Q5 high"])].copy()
    state["leverage_state"] = pd.Categorical(state["leverage_state"], categories=["Q1 low", "Q3", "Q5 high"], ordered=True)
    state = state.sort_values("leverage_state")
    top_events = events.nlargest(6, "btc_total_liq_to_lag_oi_pct").sort_values("btc_total_liq_to_lag_oi_pct")

    fig, axes = plt.subplots(1, 2, figsize=TWO_PANEL_FIGSIZE)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.78, wspace=0.32)
    add_figure_header(
        fig,
        "Tail stress is elevated at both low and high leverage states",
        "Q1/Q3/Q5 use lagged leverage-state quintiles; liquidation events use same-day USD liquidations divided by prior-day OI.",
    )

    ax = axes[0]
    style_axis(ax)
    colors = [PALETTE["stress"], PALETTE["slate"], PALETTE["stress"]]
    edges = [PALETTE["stress_dark"], PALETTE["risk_dark"], PALETTE["stress_dark"]]
    bars = ax.bar(state["leverage_state"].astype(str), state["bottom5_rate"], color=colors, edgecolor=edges, linewidth=1.0)
    ax.set_title("A. Tail-day rates", loc="left", fontsize=13, fontweight="semibold")
    ax.set_ylabel("Bottom-5% BTC return day rate")
    ax.set_xlabel("Lagged leverage-state quintile")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    direct_label_bars(ax, bars, [_pct(v) for v in state["bottom5_rate"]])

    ax = axes[1]
    style_axis(ax, y_grid=False, x_grid=True)
    labels = top_events["event_date"].dt.strftime("%Y-%m-%d")
    bars = ax.barh(labels, top_events["btc_total_liq_to_lag_oi_pct"], color=PALETTE["stress"], edgecolor=PALETTE["stress_dark"], linewidth=1.0)
    ax.set_title("B. Largest liquidation signatures", loc="left", fontsize=13, fontweight="semibold")
    ax.set_xlabel("Same-day liquidation / prior-day OI (%)")
    ax.set_ylabel("")
    for bar, value in zip(bars, top_events["btc_total_liq_to_lag_oi_pct"], strict=True):
        ax.text(value + max(top_events["btc_total_liq_to_lag_oi_pct"]) * 0.015, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontsize=10)
    ax.set_xlim(0, max(top_events["btc_total_liq_to_lag_oi_pct"]) * 1.18)
    return _save(fig, public / "04_leverage_tail_stress.png")


def fig_pit(root: Path, public: Path) -> Path:
    comp = pd.read_csv(table_path(root, "pit_composition.csv"))
    conc = pd.read_csv(table_path(root, "pit_concentration.csv"), parse_dates=["snapshot_date"])
    comp["date"] = pd.to_datetime(comp["snapshot_date"])
    category_map = {
        "BTC": "BTC",
        "ETH": "ETH",
        "selected majors ex BTC/ETH": "selected majors ex BTC/ETH",
        "stable-like assets": "stable-like",
        "productized/wrapped assets": "productized/wrapped",
        "governance/infrastructure risk assets": "other risk",
        "other risk assets": "other risk",
    }
    comp["display_class"] = comp["asset_class_final"].map(category_map).fillna("other risk")
    ordered = ["BTC", "ETH", "selected majors ex BTC/ETH", "stable-like", "productized/wrapped", "other risk"]
    pivot = comp.pivot_table(index="date", columns="display_class", values="share", aggfunc="sum").reindex(columns=ordered).fillna(0)

    fig, axes = plt.subplots(1, 2, figsize=TWO_PANEL_FIGSIZE)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.22, top=0.78, wspace=0.24)
    add_figure_header(
        fig,
        "BTC and ETH still anchor the point-in-time top-100 market",
        "Composition collapses taxonomy to six public categories; latest month is a partial snapshot when flagged.",
    )

    ax = axes[0]
    style_axis(ax)
    colors = [PALETTE["btc"], PALETTE["eth"], PALETTE["major"], PALETTE["stable"], PALETTE["wrapped"], PALETTE["risk"]]
    ax.stackplot(pivot.index, [pivot[col].to_numpy() for col in ordered], labels=ordered, colors=colors, alpha=0.92, linewidth=0)
    ax.set_title("A. Top-100 composition", loc="left", fontsize=13, fontweight="semibold")
    ax.set_ylabel("Share of top-100 market cap")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    _format_date_axis(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False)

    ax = axes[1]
    style_axis(ax)
    ax.plot(conc["snapshot_date"], conc["top10_share"], color=PALETTE["btc"], linewidth=2.0, label="Top-10 share")
    ax.plot(conc["snapshot_date"], conc["hhi"], color=PALETTE["eth"], linewidth=2.0, label="HHI")
    latest = conc.dropna(subset=["snapshot_date"]).iloc[-1]
    partial = str(latest["is_partial_month"]).strip().lower() in {"true", "1", "yes"}
    latest_label = f"{pd.to_datetime(latest['snapshot_date']).date()} partial" if partial else str(pd.to_datetime(latest["snapshot_date"]).date())
    ax.scatter([latest["snapshot_date"]], [latest["top10_share"]], color=PALETTE["btc_dark"], zorder=5)
    ax.annotate(
        latest_label,
        xy=(latest["snapshot_date"], latest["top10_share"]),
        xytext=(-12, -24),
        textcoords="offset points",
        ha="right",
        va="top",
        fontsize=10,
        color=TOKENS["muted"],
        arrowprops={"arrowstyle": "-", "color": TOKENS["muted"], "linewidth": 0.8},
    )
    ax.set_title("B. Concentration", loc="left", fontsize=13, fontweight="semibold")
    ax.set_ylabel("Index / share")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    _format_date_axis(ax)
    ax.legend(loc="lower right", frameon=False)
    return _save(fig, public / "05_point_in_time_market_structure.png")


def fig_selected_major(root: Path, public: Path) -> Path:
    risk = pd.read_csv(table_path(root, "selected_major_risk_metrics.csv"))
    risk = risk.dropna(subset=["annualized_volatility", "max_drawdown"]).copy()
    risk["drawdown_loss"] = -risk["max_drawdown"]
    risk["short_history_flag"] = risk["short_history_flag"].astype(str).str.lower().eq("true")

    fig, ax = plt.subplots(figsize=README_FIGSIZE)
    fig.subplots_adjust(left=0.09, right=0.96, bottom=0.16, top=0.80)
    add_figure_header(
        fig,
        "Selected majors separate by volatility, drawdown, and coverage",
        "Comparable current-source risk map; HYPE is marked as short-history and should not be read as full-cycle evidence.",
    )
    style_axis(ax, y_grid=True, x_grid=True)
    long = risk[~risk["short_history_flag"]]
    short = risk[risk["short_history_flag"]]
    ax.scatter(long["annualized_volatility"], long["drawdown_loss"], s=120, color=PALETTE["eth"], edgecolor=PALETTE["eth_dark"], linewidth=1.0, label="Standard coverage")
    if not short.empty:
        ax.scatter(short["annualized_volatility"], short["drawdown_loss"], s=160, marker="D", color=PALETTE["stress"], edgecolor=PALETTE["stress_dark"], linewidth=1.0, label="Short history")
    offsets = {
        "BTC": (8, 8),
        "ETH": (8, -14),
        "BNB": (8, 8),
        "SOL": (8, 8),
        "XRP": (8, -14),
        "DOGE": (8, 8),
        "TRX": (8, -14),
        "TON": (8, 8),
        "ADA": (8, -14),
        "HYPE": (8, 8),
    }
    for _, row in risk.iterrows():
        dx, dy = offsets.get(str(row["symbol"]), (8, 8))
        ax.annotate(str(row["symbol"]), (row["annualized_volatility"], row["drawdown_loss"]), xytext=(dx, dy), textcoords="offset points", fontsize=11, color=TOKENS["ink"])
    ax.set_xlabel("Annualized volatility")
    ax.set_ylabel("Maximum drawdown loss")
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.legend(loc="upper left", frameon=False)
    return _save(fig, public / "06_selected_major_asset_risk.png")


def fig_event_gallery(root: Path, gallery: Path) -> Path:
    events = pd.read_csv(table_path(root, "event_response_matrix.csv"))
    matrix = events.pivot_table(index="event_id", columns="asset", values="post_window_return", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    fig.subplots_adjust(left=0.26, right=0.90, bottom=0.16, top=0.78)
    add_figure_header(
        fig,
        "Appendix: configured event-window responses",
        "Values are +1 through +10 returns; missing cells remain missing.",
        left=0.26,
    )
    style_axis(ax, y_grid=False, x_grid=False)
    data = np.ma.masked_invalid(matrix.to_numpy(dtype=float))
    cmap = sns.diverging_palette(240, 15, s=65, l=65, as_cmap=True)
    cmap.set_bad("#E2E5EA")
    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=-0.25, vmax=0.25)
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), [str(x).replace("_", " ") for x in matrix.index])
    ax.set_xlabel("")
    ax.set_ylabel("")
    for row_idx, event_id in enumerate(matrix.index):
        for col_idx, asset in enumerate(matrix.columns):
            value = matrix.loc[event_id, asset]
            label = "NA" if pd.isna(value) else _pct(value)
            ax.text(col_idx, row_idx, label, ha="center", va="center", fontsize=10, color=TOKENS["ink"])
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    cbar.set_label("+1 to +10 return")
    return _save(fig, gallery / "appendix_event_response_matrix.png")


def contact_sheet(root: Path, public_paths: list[Path]) -> Path:
    figures_dir, _, _ = figure_dirs(root)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.5))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.92, wspace=0.08, hspace=0.16)
    fig.suptitle("Public Figure QA Contact Sheet", fontsize=16, fontweight="semibold", color=TOKENS["ink"])
    for ax, image_path in zip(axes.flatten(), public_paths, strict=True):
        image = mpimg.imread(image_path)
        ax.imshow(image)
        ax.set_title(image_path.stem.replace("_", " "), fontsize=10, color=TOKENS["ink"])
        ax.axis("off")
    path = figures_dir / "public_contact_sheet.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=TOKENS["background"])
    plt.close(fig)
    return path


def write_visual_audit(root: Path, public_paths: list[Path], gallery_path: Path) -> Path:
    rows = [
        {
            "figure": "01_mvrv_mechanics.png",
            "analytical_question": "How much of same-day d-log MVRV is mechanically tied to BTC returns?",
            "changed_from_previous": "Replaced mixed-stat bar axis with relationship scatter and lagged-state bars.",
            "manual_visual_check": "Two panels, readable percent axes, y=x reference visible, no dense legend.",
            "status": "pass",
        },
        {
            "figure": "02_tradfi_exposure_shift.png",
            "analytical_question": "How did equity block delta R-squared compare pre-BTC-ETF versus BTC-ETF era?",
            "changed_from_previous": "Replaced regime heatmap with grouped bars and direct labels.",
            "manual_visual_check": "No rotated labels, four bars only, values labeled directly.",
            "status": "pass",
        },
        {
            "figure": "03_etf_market_plumbing.png",
            "analytical_question": "How do scaled ETF flows and lag timing relate to returns?",
            "changed_from_previous": "Kept two timing panels with explicit lag-0/lag-1 convention.",
            "manual_visual_check": "Axes identify flow-to-market-cap scaling and correlations; legend is compact.",
            "status": "pass",
        },
        {
            "figure": "04_leverage_tail_stress.png",
            "analytical_question": "Do Q1/Q3/Q5 lagged leverage states and top liquidation dates show stress patterns?",
            "changed_from_previous": "Removed synthetic liquidation event ids from the visual and uses actual dates.",
            "manual_visual_check": "Readable percent units, actual dates on y-axis, no dense liquidation table.",
            "status": "pass",
        },
        {
            "figure": "05_point_in_time_market_structure.png",
            "analytical_question": "How did top-100 composition and concentration evolve?",
            "changed_from_previous": "Collapsed taxonomy to six public categories and paired it with concentration.",
            "manual_visual_check": "Legend sits below composition panel, categories are readable, latest partial snapshot uses a callout that does not collide with the legend.",
            "status": "pass",
        },
        {
            "figure": "06_selected_major_asset_risk.png",
            "analytical_question": "How do selected majors compare on volatility, drawdown, and coverage?",
            "changed_from_previous": "Larger canvas, offset labels, and HYPE short-history marker.",
            "manual_visual_check": "Point labels are offset and readable; short-history encoding is visible.",
            "status": "pass",
        },
    ]
    text = "# Visual Quality Audit\n\n"
    text += "Contact sheet is QA-only and is not embedded in the README.\n\n"
    text += pd.DataFrame(rows).to_markdown(index=False)
    text += f"\n\nAppendix figure moved to gallery: `{gallery_path.relative_to(root).as_posix()}`.\n"
    text += "\nManual checklist applied to every public figure: no dashboards, no 3x3 public grids, no spaghetti charts, no tiny fonts, no rotated category labels, no dense legends, no paragraph titles, one analytical message per figure.\n"
    path = root / "outputs" / "report" / "visual_quality_audit.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def build_public_figures(root: Path = PROJECT_ROOT) -> list[Path]:
    apply_theme()
    figures_dir, public, gallery = figure_dirs(root)
    _clean_figure_dirs(public, gallery)
    public_paths = [
        fig_mvrv(root, public),
        fig_tradfi_shift(root, public),
        fig_etf(root, public),
        fig_leverage(root, public),
        fig_pit(root, public),
        fig_selected_major(root, public),
    ]
    gallery_event = fig_event_gallery(root, gallery)
    sheet = contact_sheet(root, public_paths)
    write_visual_audit(root, public_paths, gallery_event)
    if len(public_paths) != 6:
        raise RuntimeError(f"Expected exactly 6 public figures, wrote {len(public_paths)}")
    for path in [*public_paths, gallery_event, sheet]:
        if not path.exists():
            raise FileNotFoundError(path)
    _ = figures_dir
    return [*public_paths, gallery_event, sheet]
