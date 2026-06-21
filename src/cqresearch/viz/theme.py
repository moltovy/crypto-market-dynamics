"""Shared visual design system for public research figures."""

from __future__ import annotations

from collections.abc import Iterable

import matplotlib as mpl
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import seaborn as sns

FONT_FAMILY = ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial", "sans-serif"]
MONO_FONT_FAMILY = ["DejaVu Sans Mono", "Consolas", "Menlo", "monospace"]

TOKENS = {
    "background": "#FFFFFF",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E8EBF2",
    "axis": "#D7DBE7",
}

PALETTE = {
    "btc": "#F0986E",
    "btc_dark": "#804126",
    "eth": "#5477C4",
    "eth_dark": "#2E4780",
    "stable": "#71B436",
    "stable_dark": "#386411",
    "stress": "#B85C5C",
    "stress_dark": "#7A3333",
    "risk": "#7A828F",
    "risk_dark": "#464C55",
    "gold": "#FFE15B",
    "slate": "#C5CAD3",
    "slate_light": "#E2E5EA",
    "other": "#A3BEFA",
    "wrapped": "#BD569B",
    "major": "#B8A037",
}

README_FIGSIZE = (12.0, 6.75)
TWO_PANEL_FIGSIZE = (14.0, 6.0)
EXPORT_DPI = 190


def apply_theme() -> None:
    """Apply the static public-chart theme."""

    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.dpi": EXPORT_DPI,
            "savefig.dpi": EXPORT_DPI,
            "figure.facecolor": TOKENS["background"],
            "figure.edgecolor": TOKENS["background"],
            "savefig.facecolor": TOKENS["background"],
            "savefig.edgecolor": TOKENS["background"],
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlelocation": "left",
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "grid.alpha": 1.0,
            "xtick.color": TOKENS["muted"],
            "ytick.color": TOKENS["muted"],
            "text.color": TOKENS["ink"],
            "legend.facecolor": TOKENS["panel"],
            "legend.edgecolor": TOKENS["panel"],
            "legend.framealpha": 0.0,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "font.monospace": MONO_FONT_FAMILY,
            "font.size": 11,
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "patch.linewidth": 1.0,
            "svg.hashsalt": "crypto-market-dynamics-public-viz",
        },
    )


def apply_institutional_mpl_theme() -> None:
    """Backward-compatible alias for older plotting helpers."""

    apply_theme()


def style_axis(ax: matplotlib.axes.Axes, *, y_grid: bool = True, x_grid: bool = False) -> None:
    """Apply quiet axis styling with visible left/bottom anchors."""

    ax.set_facecolor(TOKENS["panel"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(TOKENS["axis"])
    ax.spines["bottom"].set_color(TOKENS["axis"])
    ax.tick_params(axis="both", colors=TOKENS["muted"], length=0)
    if y_grid:
        ax.grid(axis="y", visible=True, color=TOKENS["grid"], linewidth=0.8)
    else:
        ax.grid(axis="y", visible=False)
    if x_grid:
        ax.grid(axis="x", visible=True, color=TOKENS["grid"], linewidth=0.8)
    else:
        ax.grid(axis="x", visible=False)


def add_figure_header(
    fig: matplotlib.figure.Figure,
    title: str,
    subtitle: str,
    *,
    left: float = 0.06,
    title_size: int = 16,
) -> None:
    """Add a consistent title/subtitle block."""

    fig.text(
        left,
        0.975,
        title,
        ha="left",
        va="top",
        fontsize=title_size,
        fontweight="semibold",
        color=TOKENS["ink"],
    )
    fig.text(left, 0.925, subtitle, ha="left", va="top", fontsize=11, color=TOKENS["muted"])


def direct_label_bars(
    ax: matplotlib.axes.Axes,
    bars: Iterable[mpl.patches.Rectangle],
    labels: Iterable[str],
    *,
    padding: float = 0.006,
) -> None:
    """Place compact numeric labels above vertical bars."""

    ymax = ax.get_ylim()[1]
    for bar, label in zip(bars, labels, strict=True):
        height = float(bar.get_height())
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + ymax * padding,
            label,
            ha="center",
            va="bottom",
            fontsize=10,
            color=TOKENS["ink"],
            fontfamily=MONO_FONT_FAMILY[0],
        )


def close(fig: plt.Figure) -> None:
    plt.close(fig)
