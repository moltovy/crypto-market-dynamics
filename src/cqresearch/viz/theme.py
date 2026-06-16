"""Matplotlib and optional Plotly theme helpers for public artifacts."""

from __future__ import annotations

from typing import Any

import matplotlib as mpl
import matplotlib.axes
import matplotlib.pyplot as plt

from cqresearch.viz.design_system import COLORS, EXPORT_DPI, FONT_FAMILY, MONO_FONT_FAMILY


def apply_institutional_mpl_theme() -> None:
    """Apply the dark institutional Matplotlib theme used for public figures."""

    mpl.rcParams.update(
        {
            "figure.dpi": EXPORT_DPI,
            "savefig.dpi": EXPORT_DPI,
            "savefig.bbox": None,
            "savefig.facecolor": COLORS["bg"],
            "savefig.edgecolor": COLORS["bg"],
            "figure.facecolor": COLORS["bg"],
            "figure.edgecolor": COLORS["bg"],
            "axes.facecolor": COLORS["surface"],
            "axes.edgecolor": COLORS["axis"],
            "axes.labelcolor": COLORS["muted"],
            "axes.titlecolor": COLORS["text"],
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "grid.color": COLORS["grid"],
            "grid.linewidth": 0.7,
            "grid.alpha": 0.55,
            "xtick.color": COLORS["muted"],
            "ytick.color": COLORS["muted"],
            "text.color": COLORS["text"],
            "legend.facecolor": COLORS["surface"],
            "legend.edgecolor": COLORS["grid"],
            "legend.framealpha": 0.0,
            "font.family": "sans-serif",
            "font.sans-serif": FONT_FAMILY,
            "font.monospace": MONO_FONT_FAMILY,
            "font.size": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "patch.linewidth": 0.8,
        }
    )


def get_plotly_template() -> Any:
    """Return a Plotly template when Plotly is available.

    Plotly is optional for this project. Static README figures are rendered with
    Matplotlib, so this helper intentionally fails softly for environments
    without Plotly.
    """

    try:
        import plotly.graph_objects as go
    except Exception:
        return {
            "layout": {
                "paper_bgcolor": COLORS["bg"],
                "plot_bgcolor": COLORS["surface"],
                "font": {"color": COLORS["text"], "family": ", ".join(FONT_FAMILY[:3])},
            }
        }

    return go.layout.Template(
        layout={
            "paper_bgcolor": COLORS["bg"],
            "plot_bgcolor": COLORS["surface"],
            "font": {"color": COLORS["text"], "family": ", ".join(FONT_FAMILY[:3])},
            "xaxis": {"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["axis"]},
            "yaxis": {"gridcolor": COLORS["grid"], "zerolinecolor": COLORS["axis"]},
            "colorway": [
                COLORS["btc"],
                COLORS["eth"],
                COLORS["institutional"],
                COLORS["liquidity"],
                COLORS["native"],
                COLORS["gold"],
            ],
        }
    )


def style_axis(ax: matplotlib.axes.Axes, *, title: str | None = None, subtitle: str | None = None) -> None:
    """Style one axis without adding a Matplotlib default title block."""

    ax.set_facecolor(COLORS["surface"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis="both", colors=COLORS["muted"], length=0)
    ax.grid(color=COLORS["grid"], alpha=0.45, linewidth=0.7)
    if title:
        ax.text(
            0,
            1.03 if subtitle is None else 1.08,
            title,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=10,
            fontweight="semibold",
            color=COLORS["text"],
        )
    if subtitle:
        ax.text(
            0,
            1.025,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8,
            color=COLORS["muted"],
        )


def style_legend(ax: matplotlib.axes.Axes, *, ncol: int = 3, loc: str = "upper left") -> None:
    """Apply compact dark-theme legend styling."""

    legend = ax.legend(loc=loc, ncol=ncol, frameon=False)
    if legend is None:
        return
    for text in legend.get_texts():
        text.set_color(COLORS["muted"])


def close(fig: plt.Figure) -> None:
    """Small wrapper used by scripts after saving figures."""

    plt.close(fig)
