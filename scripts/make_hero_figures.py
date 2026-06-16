"""Generate canonical visual artifacts from frozen output tables."""

import html
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from cqresearch.viz.cards import add_header
from cqresearch.viz.clean_charts import (
    add_gantt,
    add_horizontal_bar,
    add_lollipop,
    style_small_multiple,
    add_date_axis,
)
from cqresearch.viz.design_system import COLORS, HERO_SIZE
from cqresearch.viz.theme import apply_institutional_mpl_theme, style_axis

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
TABLES = OUTPUTS / "tables"
FIGURES = OUTPUTS / "figures"
GALLERY = FIGURES / "gallery"
DASHBOARD = OUTPUTS / "dashboard"
REPORT = OUTPUTS / "report"

def ensure_dirs() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    GALLERY.mkdir(parents=True, exist_ok=True)
    DASHBOARD.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)

def load_csv(filename: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    path = TABLES / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing {filename}")
    return pd.read_csv(path, parse_dates=parse_dates)

def make_chart(
    filename: str,
    title: str,
    *,
    axes_rect: list[float] | None = None,
    figsize: tuple[float, float] = HERO_SIZE,
    gallery: bool = False
) -> tuple[plt.Figure, plt.Axes]:
    apply_institutional_mpl_theme()
    fig = plt.figure(figsize=figsize, facecolor=COLORS["bg"])
    add_header(fig, title, "")
    ax = fig.add_axes(axes_rect or [0.075, 0.17, 0.85, 0.61])
    style_axis(ax)
    fig.set_label(filename)
    return fig, ax

def save_fig(fig: plt.Figure, filename: str, gallery: bool = False) -> list[Path]:
    target_dir = GALLERY if gallery else FIGURES
    png_path = target_dir / filename
    svg_path = png_path.with_suffix(".svg")
    fig.savefig(png_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor(), transparent=False)
    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor(), transparent=False)
    plt.close(fig)
    return [png_path, svg_path]

def render_f01() -> list[Path]:
    inventory = load_csv("T01_source_inventory.csv", parse_dates=["start_date", "end_date"])
    grouped = (
        inventory.dropna(subset=["start_date", "end_date"])
        .groupby("source", as_index=False)
        .agg(start=("start_date", "min"), end=("end_date", "max"), files=("relpath", "count"))
        .sort_values("start")
    )
    fig, ax = make_chart("F01_data_inventory.png", "Data Inventory", axes_rect=[0.15, 0.15, 0.75, 0.65])
    add_gantt(ax, grouped["source"], grouped["start"], grouped["end"], grouped["files"], color=COLORS["institutional"])
    add_date_axis(ax)

    # Just vertical lines for ETF launches
    ax.axvline(pd.Timestamp("2024-01-11"), color=COLORS["btc"], linestyle=":", alpha=0.5)
    ax.axvline(pd.Timestamp("2024-07-23"), color=COLORS["eth"], linestyle=":", alpha=0.5)

    ax.set_xlabel("")
    return save_fig(fig, "F01_data_inventory.png")

def render_f02() -> list[Path]:
    attr = load_csv("T03_block_attribution.csv")
    btc_attr = attr[(attr["asset"] == "btc") & (attr["sample"] == "full")].copy()

    # Extract R2 values
    full_r2 = btc_attr.iloc[0]["full_r2"]
    mvrv_row = btc_attr[btc_attr["block"] == "BTC MVRV"].iloc[0]
    without_mvrv_r2 = mvrv_row["reduced_r2"]

    labels = ["Full model", "Without MVRV", "Native ex-MVRV", "MVRV only", "Macro + TradFi + Liquidity"]
    values = [
        full_r2,
        without_mvrv_r2,
        btc_attr[btc_attr["block"] == "BTC Native ex MVRV"].iloc[0]["partial_r2"],
        mvrv_row["partial_r2"],
        btc_attr[btc_attr["block"].isin(["Macro", "TradFi", "Liquidity"])]["partial_r2"].sum()
    ]

    fig, ax = make_chart("F02_btc_model_sensitivity.png", "BTC Model Sensitivity", axes_rect=[0.25, 0.15, 0.65, 0.65])
    add_horizontal_bar(ax, labels, values, highlight_idx=1, highlight_color=COLORS["btc"])
    ax.set_xlabel("R-squared")
    return save_fig(fig, "F02_btc_model_sensitivity.png")

def render_f03() -> list[Path]:
    ll = load_csv("T04_etf_lead_lag.csv")
    btc = ll[(ll["asset"] == "btc") & (ll["x"] == "btc_etf_intensity") & (ll["target"] == "btc_ret")].sort_values("lag")

    fig, ax = make_chart("F03_etf_flow_lead_lag.png", "ETF Flow Lead-Lag")

    zero_idx = list(btc["lag"]).index(0)
    add_lollipop(ax, btc["t"], btc["lag"], highlight_idx=zero_idx)

    ax.axhline(0, color=COLORS["text"], linewidth=1, alpha=0.5)
    ax.axhline(2, color=COLORS["risk"], linestyle="--", alpha=0.3)
    ax.axhline(-2, color=COLORS["risk"], linestyle="--", alpha=0.3)

    ax.set_xlabel("ETF-flow lag")
    ax.set_ylabel("HAC t-statistic")
    return save_fig(fig, "F03_etf_flow_lead_lag.png")

def render_f04() -> list[Path]:
    rolling = load_csv("T05_rolling_correlations.csv", parse_dates=["date"])
    pairs = [
        ("btc_ret", "eth_ret", "BTC-ETH", COLORS["eth"]),
        ("btc_ret", "spy_ret", "BTC-SPY", COLORS["macro"]),
        ("btc_ret", "VIXCLS_d1", "BTC-VIX", COLORS["risk"]),
        ("btc_ret", "gld_ret", "BTC-Gold", COLORS["gold"])
    ]

    apply_institutional_mpl_theme()
    fig, axes = plt.subplots(2, 2, figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_header(fig, "Rolling Correlations", "")
    axes = axes.flatten()

    for idx, (target, feature, label, color) in enumerate(pairs):
        ax = axes[idx]
        mask = (rolling["lhs"] == target) & (rolling["rhs"] == feature)
        data = rolling[mask].sort_values("date")

        ax.plot(data["date"], data["correlation"], color=color, linewidth=2)
        style_small_multiple(ax)
        ax.set_title(label, fontsize=10, color=COLORS["text"], pad=8)

        ax.axhline(0, color=COLORS["text"], linewidth=1, alpha=0.2)
        ax.set_ylim(-0.8, 1.0)

        # Direct label last value
        if not data.empty:
            last = data.iloc[-1]
            ax.text(last["date"], last["correlation"], f" {last['correlation']:.2f}",
                    va='center', fontsize=9, color=color, fontweight="semibold")

    fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.85])
    return save_fig(fig, "F04_rolling_correlations.png")

def render_f05() -> list[Path]:
    monthly = load_csv("T06_stablecoin_liquidity.csv", parse_dates=["date"])

    apply_institutional_mpl_theme()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=HERO_SIZE, facecolor=COLORS["bg"], sharex=True)
    add_header(fig, "Stablecoins and TVL", "")

    # Stablecoin panel
    ax1.plot(monthly["date"], monthly["stables_total_usd"], color=COLORS["stablecoin"], linewidth=2)
    style_small_multiple(ax1)
    ax1.set_title("Stablecoin Supply (USD)", fontsize=10, color=COLORS["text"], loc="left")
    ax1.set_yscale("log")

    # TVL panel
    ax2.plot(monthly["date"], monthly["defi_tvl_usd"], color=COLORS["eth"], linewidth=2)
    style_small_multiple(ax2)
    ax2.set_title("DeFi TVL (USD)", fontsize=10, color=COLORS["text"], loc="left")
    ax2.set_yscale("log")

    fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.85])
    return save_fig(fig, "F05_liquidity_context.png")

def render_f06() -> list[Path]:
    roll_conn = load_csv("T09_rolling_connectedness.csv", parse_dates=["date"])
    roll_conn = roll_conn.sort_values("date")

    rob = load_csv("T10_robustness.csv")
    btc_rob = rob.groupby(["window", "include_mvrv"])["r2"].mean().unstack()

    apply_institutional_mpl_theme()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=HERO_SIZE, facecolor=COLORS["bg"])
    add_header(fig, "Connectedness and Robustness", "")

    # Left: Rolling Connectedness
    ax1.plot(roll_conn["date"], roll_conn["connectedness_pct"], color=COLORS["institutional"], linewidth=2)
    style_small_multiple(ax1)
    ax1.set_title("Total Connectedness Index", fontsize=10, color=COLORS["text"], loc="left")
    ax1.set_ylim(0, 100)

    # Right: Robustness Grid (with/without MVRV)
    x = np.arange(len(btc_rob.index))
    width = 0.35
    ax2.bar(x - width/2, btc_rob[True], width, label="With MVRV", color=COLORS["btc"])
    ax2.bar(x + width/2, btc_rob[False], width, label="Without MVRV", color=COLORS["macro"])
    style_small_multiple(ax2)
    ax2.set_title("Model R-squared by Window", fontsize=10, color=COLORS["text"], loc="left")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{w}d" for w in btc_rob.index])
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    ax2.set_ylim(0, 1.0)

    fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.85])
    return save_fig(fig, "F06_connectedness_and_robustness.png")

def render_g01() -> list[Path]:
    df = load_csv("T07_btc_native_correlations.csv", parse_dates=None).set_index("feature")

    # Rename labels
    rename_map = {
        "btc_ret": "BTC return",
        "cme_btc_basis_close_d1": "CME basis",
        "btc_exchange_netflow_d1": "Exchange netflow",
        "btc_miner_to_exchange_flow_d1": "Miner->exchange flow",
        "btc_mvrv_d1": "MVRV"
    }
    df = df.rename(columns=rename_map, index=rename_map)
    df = df.loc[list(rename_map.values()), list(rename_map.values())]

    # Mask diagonal
    mat = df.values.copy()
    np.fill_diagonal(mat, np.nan)

    fig, ax = make_chart("G01_native_state_detail.png", "BTC Native State Correlation Matrix", gallery=True)
    im = ax.imshow(mat, cmap="coolwarm", vmin=-1, vmax=1)

    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(df.index, fontsize=9)

    # Loop over data dimensions and create text annotations.
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f"{mat[i, j]:.2f}",
                               ha="center", va="center", color="black" if abs(mat[i, j]) < 0.5 else "white")

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return save_fig(fig, "G01_native_state_detail.png", gallery=True)

def render_g02() -> list[Path]:
    rob = load_csv("T10_robustness.csv")
    fig, ax = make_chart("G02_full_robustness_grid.png", "Full Robustness Grid", gallery=True)

    pivoted = rob.pivot_table(index="window", columns=["hac_lags", "include_mvrv"], values="r2")

    im = ax.imshow(pivoted.values, cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(pivoted.columns)))
    ax.set_yticks(np.arange(len(pivoted.index)))

    labels = [f"Lag {lag}\nMVRV: {'Yes' if m else 'No'}" for lag, m in pivoted.columns]
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels([f"{w}d" for w in pivoted.index], fontsize=9)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return save_fig(fig, "G02_full_robustness_grid.png", gallery=True)

def render_g03() -> list[Path]:
    df = load_csv("T09_connectedness.csv", parse_dates=None)
    # Filter to FEVD matrix
    cols = [c for c in df.columns if c != "to" and c in df["to"].values]
    if not cols:
        return []

    mat_df = df.set_index("to")[cols].astype(float)

    # Mask diagonal for off-diagonal focus
    mat = mat_df.values.copy()
    np.fill_diagonal(mat, np.nan)

    fig, ax = make_chart("G03_fevd_matrix.png", "FEVD Matrix (Off-Diagonal)", gallery=True)
    im = ax.imshow(mat, cmap="YlOrRd")

    ax.set_xticks(np.arange(len(mat_df.columns)))
    ax.set_yticks(np.arange(len(mat_df.index)))
    ax.set_xticklabels(mat_df.columns, rotation=90, fontsize=7)
    ax.set_yticklabels(mat_df.index, fontsize=7)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return save_fig(fig, "G03_fevd_matrix.png", gallery=True)

def write_dashboard() -> list[Path]:
    figures = [
        "F01_data_inventory.png",
        "F02_btc_model_sensitivity.png",
        "F03_etf_flow_lead_lag.png",
        "F04_rolling_correlations.png",
        "F05_liquidity_context.png",
        "F06_connectedness_and_robustness.png",
    ]
    cards = "\n".join(
        f"<section class='card'><h2>{html.escape(filename.replace('_', ' ').replace('.png', ''))}</h2><img src='../figures/{filename}' alt='{html.escape(filename)}'></section>"
        for filename in figures
    )
    html_path = DASHBOARD / "index.html"
    html_path.write_text(
        "<!doctype html>\\n<html>\\n<head>\\n<meta charset=\"utf-8\">\\n<title>Crypto Market Factor Lab Dashboard</title>\\n"
        "<style>\\nbody{margin:0;background:#FAFAF7;color:#111827;font-family:Inter,Segoe UI,Arial,sans-serif}\\n"
        "header{padding:32px 5vw 18px;border-bottom:1px solid #E5E7EB;background:#FFFFFF}\\n"
        "h1{margin:0 0 8px;font-size:32px}\\n"
        "p{margin:0;color:#6B7280;max-width:980px;line-height:1.5}\\n"
        "main{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:22px;padding:28px 5vw}\\n"
        ".card{background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;padding:16px}\\n"
        ".card h2{font-size:15px;color:#6B7280;margin:0 0 12px;text-transform:uppercase;letter-spacing:.04em}\\n"
        "img{width:100%;height:auto;border-radius:8px;border:1px solid #E5E7EB}\\n"
        "a{color:#2563EB}\\n</style>\\n</head>\\n<body>\\n<header>\\n<h1>Crypto Market Factor Lab</h1>\\n"
        "<p>Static, minimal dashboard of public canonical figures.</p>\\n</header>\\n<main>\\n"
        + cards
        + "\\n</main></body></html>\\n",
        encoding="utf-8",
    )
    return [html_path]

def render_all_figures() -> list[Path]:
    ensure_dirs()
    written: list[Path] = []
    written.extend(render_f01())
    written.extend(render_f02())
    written.extend(render_f03())
    written.extend(render_f04())
    written.extend(render_f05())
    written.extend(render_f06())
    written.extend(render_g01())
    written.extend(render_g02())
    written.extend(render_g03())
    written.extend(write_dashboard())
    return written

def main() -> int:
    written = render_all_figures()
    for path in written:
        print(f"[ok] {path.relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
