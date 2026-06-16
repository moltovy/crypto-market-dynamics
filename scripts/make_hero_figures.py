"""Generate canonical visual artifacts from frozen output tables.

Produces research-question-driven figures F01-F08 from the statistical tables
T11-T27 plus the existing T03-T10 tables.
"""

import html
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cqresearch.analysis.feature_strength import BLOCK_MAP
from cqresearch.viz.design_system import COLORS, FACTOR_COLORS, HERO_SIZE
from cqresearch.viz.theme import apply_institutional_mpl_theme

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


def save_fig(fig: plt.Figure, filename: str, gallery: bool = False) -> list[Path]:
    target_dir = GALLERY if gallery else FIGURES
    png_path = target_dir / filename
    svg_path = png_path.with_suffix(".svg")
    fig.savefig(png_path, dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor(), transparent=False)
    fig.savefig(svg_path, format="svg", bbox_inches="tight",
                facecolor=fig.get_facecolor(), transparent=False)
    plt.close(fig)
    return [png_path, svg_path]


def _light_axis(ax: plt.Axes) -> None:
    """Style axis for clean institutional look."""
    ax.set_facecolor(COLORS["bg"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS.get("axis", "#CBD5E1"))
    ax.spines["bottom"].set_color(COLORS.get("axis", "#CBD5E1"))
    ax.tick_params(colors=COLORS["text"], labelsize=9)


# ══════════════════════════════════════════════════════════════════════════════
# F01 — MVRV Sensitivity by Regime (the core research-question figure)
# ══════════════════════════════════════════════════════════════════════════════

def render_f01() -> list[Path]:
    """MVRV sensitivity by regime - directly answers 'does MVRV dominance persist?'"""

    t25 = load_csv("T25_mvrv_sensitivity_by_regime.csv")
    regime_labels = {
        "full": "Full 2020-2026",
        "pre_btc_etf": "Pre-BTC ETF",
        "post_btc_etf": "Post-BTC ETF",
        "year_2024": "2024",
        "year_2025": "2025",
        "year_2026_ytd": "2026 YTD",
    }
    t25["label"] = t25["regime"].map(regime_labels)
    t25 = t25.dropna(subset=["label"])

    apply_institutional_mpl_theme()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("BTC MVRV Sensitivity by Regime", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)

    # Panel A: Model R² comparison
    x = np.arange(len(t25))
    width = 0.25
    ax1.barh(x + width, t25["full_with_mvrv_r2"], width,
             label="Full with MVRV", color=COLORS.get("native", "#7C3AED"))
    ax1.barh(x, t25["mvrv_only_r2"], width,
             label="MVRV only", color=COLORS["btc"])
    ax1.barh(x - width, t25["ex_mvrv_r2"], width,
             label="Ex-MVRV", color=COLORS.get("macro", "#2563EB"))

    ax1.set_yticks(x)
    ax1.set_yticklabels(t25["label"], fontsize=9)
    ax1.set_xlabel("R²", fontsize=10)
    ax1.set_title("A. Standalone Model R²", fontsize=11, color=COLORS["text"], loc="left")
    ax1.set_xlim(0, 1.05)
    _light_axis(ax1)

    # Panel B: ΔR² from removing MVRV
    colors_b = [COLORS["btc"]] * len(t25)
    ax2.barh(x, t25["delta_r2"], color=colors_b, height=0.5)
    for i, v in enumerate(t25["delta_r2"]):
        ax2.text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=9, color=COLORS["text"])

    ax2.set_yticks(x)
    ax2.set_yticklabels(t25["label"], fontsize=9)
    ax2.set_xlabel("ΔR²", fontsize=10)
    ax2.set_title("B. ΔR² from Removing MVRV", fontsize=11, color=COLORS["text"], loc="left")
    ax2.set_xlim(0, 1.0)
    _light_axis(ax2)

    # Add figure-level legend at the bottom center to prevent overlapping chart bars
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.02))

    fig.tight_layout(rect=[0.02, 0.08, 0.98, 0.90])
    return save_fig(fig, "F01_mvrv_sensitivity_by_regime.png")


# ══════════════════════════════════════════════════════════════════════════════
# F02 — Same-Support Ablation (corrected figure)
# ══════════════════════════════════════════════════════════════════════════════

def render_f02() -> list[Path]:
    """Same-support BTC ablation — clean R² ladder on identical sample."""

    t19 = load_csv("T19_same_support_ablation_btc.csv")

    model_labels = {
        "M0_intercept": "Intercept only",
        "M1_macro": "Macro",
        "M2_macro_tradfi": "+ TradFi",
        "M3_macro_tradfi_liquidity": "+ Liquidity",
        "M4_plus_sentiment": "+ Sentiment",
        "M5_plus_native_ex_mvrv": "+ Native ex-MVRV",
        "M6_plus_mvrv": "+ MVRV",
        "M7_mvrv_only": "MVRV only",
        "M8_native_ex_mvrv_only": "Native ex-MVRV only",
    }
    t19["label"] = t19["model_id"].map(model_labels)

    apply_institutional_mpl_theme()
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("BTC Same-Support Model Ablation", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)

    y_pos = np.arange(len(t19))
    colors = []
    for _, row in t19.iterrows():
        mid = row["model_id"]
        if mid == "M0_intercept":
            colors.append(COLORS["neutral"])
        elif mid == "M1_macro":
            colors.append(COLORS["macro"])
        elif mid == "M2_macro_tradfi":
            colors.append(COLORS["gold"])
        elif mid == "M3_macro_tradfi_liquidity":
            colors.append(COLORS["liquidity"])
        elif mid == "M4_plus_sentiment":
            colors.append(COLORS["neutral"])
        elif mid in ("M5_plus_native_ex_mvrv", "M8_native_ex_mvrv_only"):
            colors.append("#C084FC")  # Native flow
        elif mid in ("M6_plus_mvrv", "M7_mvrv_only"):
            colors.append(COLORS["native"])  # MVRV valuation
        else:
            colors.append(COLORS["neutral"])

    ax.barh(y_pos, t19["r2"], color=colors, height=0.6)
    for i, (r2, _n) in enumerate(zip(t19["r2"], t19["n"], strict=False)):
        ax.text(r2 + 0.01, i, f"{r2:.3f}", va="center", fontsize=9, color=COLORS["text"])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(t19["label"], fontsize=9)
    ax.set_xlabel(f"R² (same support, n = {int(t19.iloc[0]['n'])})", fontsize=10)
    ax.set_xlim(0, 1.05)
    ax.invert_yaxis()
    _light_axis(ax)

    fig.tight_layout(rect=[0.15, 0.05, 0.95, 0.90])
    return save_fig(fig, "F02_same_support_ablation.png")


# ══════════════════════════════════════════════════════════════════════════════
# F03 — BTC Ex-MVRV Feature Strength
# ══════════════════════════════════════════════════════════════════════════════

def render_f03() -> list[Path]:
    """Which features matter once MVRV is excluded."""

    t15 = load_csv("T15_feature_strength_btc_ex_mvrv.csv")
    t15 = t15.sort_values("abs_correlation", ascending=True)

    apply_institutional_mpl_theme()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("BTC Feature Strength (ex-MVRV Model)", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)

    # Panel A: Absolute correlation
    colors_a = [FACTOR_COLORS.get(BLOCK_MAP.get(f, "Unknown"), COLORS["neutral"])
                for f in t15["feature"]]
    ax1.barh(range(len(t15)), t15["abs_correlation"], color=colors_a, height=0.6)
    ax1.set_yticks(range(len(t15)))
    clean_names = [f.replace("_d1", " Δ").replace("_ret", "").replace("_", " ").title()
                   for f in t15["feature"]]
    ax1.set_yticklabels(clean_names, fontsize=8)
    ax1.set_xlabel("|Correlation|", fontsize=10)
    ax1.set_title("A. Absolute Correlation", fontsize=11, color=COLORS["text"], loc="left")
    _light_axis(ax1)

    # Panel B: Multivariate HAC t-stat
    t_vals = t15["multivar_hac_t"].fillna(0)
    colors_b = [COLORS.get("risk", "#DC2626") if abs(t) > 2
                else COLORS.get("neutral", "#64748B")
                for t in t_vals]
    ax2.barh(range(len(t15)), t_vals.abs(), color=colors_b, height=0.6)
    ax2.axvline(2, color=COLORS.get("risk", "#DC2626"), linestyle="--", alpha=0.4, linewidth=1)
    ax2.set_yticks(range(len(t15)))
    ax2.set_yticklabels(clean_names, fontsize=8)
    ax2.set_xlabel("|HAC t-stat|", fontsize=10)
    ax2.set_title("B. Multivariate HAC |t|", fontsize=11, color=COLORS["text"], loc="left")
    _light_axis(ax2)

    fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.90])
    return save_fig(fig, "F03_btc_ex_mvrv_strength.png")


# ══════════════════════════════════════════════════════════════════════════════
# F04 — ETF Flow Lead-Lag (kept from before, cleaned)
# ══════════════════════════════════════════════════════════════════════════════

def render_f04() -> list[Path]:
    """ETF-flow lead-lag lollipop chart."""

    ll = load_csv("T04_etf_lead_lag.csv")
    btc = ll[
        (ll["asset"] == "btc") & (ll["x"] == "btc_etf_intensity") & (ll["target"] == "btc_ret")
    ].sort_values("lag")

    apply_institutional_mpl_theme()
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("ETF Flow Lead-Lag", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)

    lags = btc["lag"].values
    t_vals = btc["t"].values

    colors = [COLORS["btc"] if abs(t) > 2 else COLORS.get("neutral", "#64748B")
              for t in t_vals]
    ax.vlines(lags, 0, t_vals, colors=colors, linewidth=2)
    ax.scatter(lags, t_vals, color=colors, s=50, zorder=5)
    ax.axhline(0, color=COLORS["text"], linewidth=1, alpha=0.5)
    ax.axhline(2, color=COLORS.get("risk", "#DC2626"), linestyle="--", alpha=0.3)
    ax.axhline(-2, color=COLORS.get("risk", "#DC2626"), linestyle="--", alpha=0.3)
    ax.set_xlabel("ETF-flow lag", fontsize=10)
    ax.set_ylabel("HAC t-statistic", fontsize=10)
    _light_axis(ax)

    fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.90])
    return save_fig(fig, "F04_etf_flow_lead_lag.png")


# ══════════════════════════════════════════════════════════════════════════════
# F05 — Core Correlation Matrix
# ══════════════════════════════════════════════════════════════════════════════

def render_f05() -> list[Path]:
    """Compact correlation matrix with masked diagonal."""

    t23 = load_csv("T23_core_correlation_matrix.csv")
    # First column is the index
    if t23.columns[0] in ("", "Unnamed: 0") or t23.columns[0] in t23.values[:, 0]:
        t23 = t23.set_index(t23.columns[0])

    mat = t23.values.astype(float).copy()
    np.fill_diagonal(mat, np.nan)

    labels = [c.replace("_d1", " Δ").replace("_ret", "").replace("_", " ").title()
              for c in t23.columns]

    apply_institutional_mpl_theme()
    fig, ax = plt.subplots(figsize=(10, 8), facecolor=COLORS["bg"])
    fig.suptitle("Core Feature Correlation Matrix", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.98)

    im = ax.imshow(mat, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(labels, fontsize=8)

    # Annotate cells
    for i in range(len(labels)):
        for j in range(len(labels)):
            if not np.isnan(mat[i, j]):
                color = "white" if abs(mat[i, j]) > 0.5 else "black"
                ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center",
                        fontsize=7, color=color, fontweight="bold")

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Correlation")
    fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.95])
    return save_fig(fig, "F05_core_correlation_matrix.png")


# ══════════════════════════════════════════════════════════════════════════════
# F06 — Rolling Correlations (small multiples, kept)
# ══════════════════════════════════════════════════════════════════════════════

def render_f06() -> list[Path]:
    """Small multiples of rolling correlations."""

    rolling = load_csv("T05_rolling_correlations.csv", parse_dates=["date"])
    pairs = [
        ("btc_ret", "eth_ret", "BTC-ETH", COLORS.get("eth", "#627EEA")),
        ("btc_ret", "spy_ret", "BTC-SPY", COLORS.get("macro", "#2563EB")),
        ("btc_ret", "VIXCLS_d1", "BTC-VIX", COLORS.get("risk", "#DC2626")),
        ("btc_ret", "gld_ret", "BTC-Gold", COLORS.get("gold", "#D4A843") if "gold" in COLORS else "#D4A843"),
    ]

    apply_institutional_mpl_theme()
    fig, axes = plt.subplots(2, 2, figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("Rolling 180d Correlations", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)
    axes = axes.flatten()

    for idx, (target, feature, label, color) in enumerate(pairs):
        ax = axes[idx]
        mask = (rolling["lhs"] == target) & (rolling["rhs"] == feature)
        data = rolling[mask].sort_values("date")

        ax.plot(data["date"], data["correlation"], color=color, linewidth=1.5)
        ax.axhline(0, color=COLORS["text"], linewidth=0.5, alpha=0.3)
        ax.set_title(label, fontsize=10, color=COLORS["text"], pad=6)
        ax.set_ylim(-0.8, 1.0)
        _light_axis(ax)

        if not data.empty:
            last = data.iloc[-1]
            ax.text(last["date"], last["correlation"], f" {last['correlation']:.2f}",
                    va="center", fontsize=8, color=color, fontweight="semibold")

    fig.tight_layout(rect=[0.03, 0.03, 0.97, 0.90])
    return save_fig(fig, "F06_rolling_correlations.png")


# ══════════════════════════════════════════════════════════════════════════════
# F07 — Feature Strength by Regime Heatmap
# ══════════════════════════════════════════════════════════════════════════════

def render_f07() -> list[Path]:
    """Feature strength heatmap across regimes (ex-MVRV model)."""

    t17 = load_csv("T17_feature_strength_by_regime.csv")
    # Pivot: features x regimes, value = multivar HAC t-stat
    pivot = t17.pivot_table(
        index="feature", columns="regime", values="multivar_hac_t", aggfunc="first"
    )
    # Order columns
    regime_order = ["full", "pre_btc_etf", "post_btc_etf", "year_2024", "year_2025",
                    "year_2026_ytd", "high_vol", "low_vol"]
    available_regimes = [r for r in regime_order if r in pivot.columns]
    pivot = pivot[available_regimes]

    # Order rows by full-sample abs t-stat
    full_t = pivot["full"].abs() if "full" in pivot.columns else pivot.iloc[:, 0].abs()
    pivot = pivot.loc[full_t.sort_values(ascending=True).index]

    labels_y = [f.replace("_d1", " Δ").replace("_ret", "").replace("_", " ").title()
                for f in pivot.index]
    labels_x = [r.replace("_", " ").title() for r in pivot.columns]

    apply_institutional_mpl_theme()
    fig, ax = plt.subplots(figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("BTC Feature Strength by Regime (ex-MVRV, HAC t-stat)", fontsize=13,
                 fontweight="bold", color=COLORS["text"], y=0.95)

    mat = pivot.values.astype(float)
    vmax = max(abs(np.nanmin(mat)), abs(np.nanmax(mat)), 3)
    im = ax.imshow(mat, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(np.arange(len(labels_x)))
    ax.set_yticks(np.arange(len(labels_y)))
    ax.set_xticklabels(labels_x, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(labels_y, fontsize=9)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isfinite(v):
                color = "white" if abs(v) > vmax * 0.5 else "black"
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7, color=color)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="HAC t-stat")
    fig.tight_layout(rect=[0.12, 0.02, 0.98, 0.90])
    return save_fig(fig, "F07_feature_strength_heatmap.png")


# ══════════════════════════════════════════════════════════════════════════════
# F08 — Connectedness and Robustness (kept)
# ══════════════════════════════════════════════════════════════════════════════

def render_f08() -> list[Path]:
    """Rolling connectedness + with/without MVRV robustness."""

    roll_conn = load_csv("T09_rolling_connectedness.csv", parse_dates=["date"])
    roll_conn = roll_conn.sort_values("date")

    rob = load_csv("T10_robustness.csv")
    btc_rob = rob.groupby(["window", "include_mvrv"])["r2"].mean().unstack()

    apply_institutional_mpl_theme()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=HERO_SIZE, facecolor=COLORS["bg"])
    fig.suptitle("Connectedness and Robustness", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)

    ax1.plot(roll_conn["date"], roll_conn["connectedness_pct"],
             color=COLORS.get("institutional", "#2563EB"), linewidth=1.5)
    ax1.set_title("Total Connectedness Index", fontsize=11, color=COLORS["text"], loc="left")
    ax1.set_ylim(0, 100)
    _light_axis(ax1)

    x = np.arange(len(btc_rob.index))
    width = 0.35
    ax2.bar(x - width / 2, btc_rob[True], width, label="With MVRV", color=COLORS["btc"])
    ax2.bar(x + width / 2, btc_rob[False], width, label="Without MVRV",
            color=COLORS.get("macro", "#2563EB"))
    ax2.set_title("Model R² by Window", fontsize=11, color=COLORS["text"], loc="left")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{w}d" for w in btc_rob.index])
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=9)
    ax2.set_ylim(0, 1.0)
    _light_axis(ax2)

    fig.tight_layout(rect=[0.03, 0.05, 0.97, 0.90])
    return save_fig(fig, "F08_connectedness_robustness.png")


# ══════════════════════════════════════════════════════════════════════════════
# Gallery figures (moved from hero to gallery)
# ══════════════════════════════════════════════════════════════════════════════

def render_g01() -> list[Path]:
    """BTC native correlation matrix → gallery."""
    df = load_csv("T07_btc_native_correlations.csv").set_index("feature")
    rename_map = {
        "btc_ret": "BTC return", "cme_btc_basis_close_d1": "CME basis",
        "btc_exchange_netflow_d1": "Exchange netflow",
        "btc_miner_to_exchange_flow_d1": "Miner→exchange",
        "btc_mvrv_d1": "MVRV",
    }
    df = df.rename(columns=rename_map, index=rename_map)
    df = df.loc[list(rename_map.values()), list(rename_map.values())]
    mat = df.values.copy()
    np.fill_diagonal(mat, np.nan)

    apply_institutional_mpl_theme()
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=COLORS["bg"])
    fig.suptitle("BTC Native State Correlation Matrix", fontsize=13,
                 fontweight="bold", color=COLORS["text"], y=0.98)
    im = ax.imshow(mat, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(df.index, fontsize=9)
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            if not np.isnan(mat[i, j]):
                c = "white" if abs(mat[i, j]) > 0.5 else "black"
                ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center",
                        color=c, fontsize=9)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.95])
    return save_fig(fig, "G01_native_state_detail.png", gallery=True)


def render_g02() -> list[Path]:
    """Stablecoins and TVL → gallery."""
    monthly = load_csv("T06_stablecoin_liquidity.csv", parse_dates=["date"])
    apply_institutional_mpl_theme()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=HERO_SIZE, facecolor=COLORS["bg"], sharex=True)
    fig.suptitle("Stablecoins and TVL", fontsize=14,
                 fontweight="bold", color=COLORS["text"], y=0.95)
    ax1.plot(monthly["date"], monthly["stables_total_usd"],
             color=COLORS.get("institutional", "#2563EB"), linewidth=1.5)
    ax1.set_title("Stablecoin Supply (USD)", fontsize=10, color=COLORS["text"], loc="left")
    ax1.set_yscale("log")
    _light_axis(ax1)
    ax2.plot(monthly["date"], monthly["defi_tvl_usd"],
             color=COLORS.get("eth", "#627EEA"), linewidth=1.5)
    ax2.set_title("DeFi TVL (USD)", fontsize=10, color=COLORS["text"], loc="left")
    ax2.set_yscale("log")
    _light_axis(ax2)
    fig.tight_layout(rect=[0.05, 0.05, 0.95, 0.90])
    return save_fig(fig, "G02_liquidity_context.png", gallery=True)


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════════════════════════════════════════

def write_dashboard() -> list[Path]:
    figures = [
        "F01_mvrv_sensitivity_by_regime.png",
        "F02_same_support_ablation.png",
        "F03_btc_ex_mvrv_strength.png",
        "F04_etf_flow_lead_lag.png",
        "F05_core_correlation_matrix.png",
        "F06_rolling_correlations.png",
        "F07_feature_strength_heatmap.png",
        "F08_connectedness_robustness.png",
    ]
    cards = "\n".join(
        f"<section class='card'><h2>{html.escape(f.replace('_', ' ').replace('.png', ''))}</h2>"
        f"<img src='../figures/{f}' alt='{html.escape(f)}'></section>"
        for f in figures
    )
    html_path = DASHBOARD / "index.html"
    html_content = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Crypto Market Factor Lab Dashboard</title>
<style>
body{{margin:0;background:#FAFAF7;color:#111827;font-family:Inter,Segoe UI,Arial,sans-serif}}
header{{padding:32px 5vw 18px;border-bottom:1px solid #E5E7EB;background:#FFFFFF}}
h1{{margin:0 0 8px;font-size:32px}}
p{{margin:0;color:#6B7280;max-width:980px;line-height:1.5}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:22px;padding:28px 5vw}}
.card{{background:#FFFFFF;border:1px solid #E5E7EB;border-radius:14px;padding:16px}}
.card h2{{font-size:15px;color:#6B7280;margin:0 0 12px;text-transform:uppercase;letter-spacing:.04em}}
img{{width:100%;height:auto;border-radius:8px;border:1px solid #E5E7EB}}
</style>
</head>
<body>
<header>
<h1>Crypto Market Factor Lab</h1>
<p>Static dashboard of public canonical figures.</p>
</header>
<main>
{cards}
</main>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")
    return [html_path]


# ══════════════════════════════════════════════════════════════════════════════
# Orchestration
# ══════════════════════════════════════════════════════════════════════════════

def render_all_figures() -> list[Path]:
    ensure_dirs()
    written: list[Path] = []
    written.extend(render_f01())
    written.extend(render_f02())
    written.extend(render_f03())
    written.extend(render_f04())
    written.extend(render_f05())
    written.extend(render_f06())
    written.extend(render_f07())
    written.extend(render_f08())
    written.extend(render_g01())
    written.extend(render_g02())
    written.extend(write_dashboard())
    return written


def main() -> int:
    written = render_all_figures()
    for path in written:
        print(f"[ok] {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
