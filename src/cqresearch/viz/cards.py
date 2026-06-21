"""Card-style Matplotlib helpers for README-ready research artifacts."""

from __future__ import annotations

import textwrap
from collections.abc import Sequence

import matplotlib.figure
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from cqresearch.viz.design_system import COLORS, HEADER_Y, HERO_SIZE, SUBTITLE_Y


def make_card_figure(
    *,
    size: tuple[float, float] = HERO_SIZE,
    title: str,
    subtitle: str,
    footer: str | None = None,
) -> tuple[matplotlib.figure.Figure, plt.Axes]:
    """Create a dark research card with a single full-card drawing axis."""

    fig = plt.figure(figsize=size, facecolor=COLORS["bg"])
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_axis_off()
    ax.set_facecolor(COLORS["bg"])
    add_card_background(fig, [0.025, 0.045, 0.95, 0.90])
    add_header(fig, title, subtitle)
    if footer:
        fig.text(0.055, 0.055, footer, ha="left", va="bottom", fontsize=7.2, color=COLORS["muted"])
    return fig, ax


def add_card_background(fig: matplotlib.figure.Figure, bounds: Sequence[float]) -> None:
    """Add a rounded dark panel to a figure."""

    patch = FancyBboxPatch(
        (bounds[0], bounds[1]),
        bounds[2],
        bounds[3],
        transform=fig.transFigure,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=COLORS["surface"],
        edgecolor=COLORS["grid"],
        linewidth=1.0,
        zorder=-10,
    )
    fig.patches.append(patch)


def add_header(fig: matplotlib.figure.Figure, title: str, subtitle: str) -> None:
    """Add consistent title and subtitle text."""

    fig.text(
        0.055,
        HEADER_Y,
        textwrap.fill(title, width=82, break_long_words=False),
        ha="left",
        va="top",
        fontsize=18,
        fontweight="semibold",
        color=COLORS["text"],
    )
    fig.text(
        0.055,
        SUBTITLE_Y,
        textwrap.fill(subtitle, width=122, break_long_words=False),
        ha="left",
        va="top",
        fontsize=9.5,
        color=COLORS["muted"],
        linespacing=1.25,
    )


def add_metric_badge(
    fig: matplotlib.figure.Figure,
    *,
    x: float,
    y: float,
    label: str,
    value: str,
    color: str,
    width: float = 0.16,
    height: float = 0.105,
) -> None:
    """Draw a compact metric badge in figure coordinates."""

    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        transform=fig.transFigure,
        boxstyle="round,pad=0.012,rounding_size=0.016",
        facecolor=COLORS["surface2"],
        edgecolor=color,
        linewidth=1.0,
        alpha=0.96,
        zorder=3,
    )
    fig.patches.append(patch)
    fig.text(
        x + 0.018, y + height - 0.031, label.upper(), fontsize=6.9, color=COLORS["muted"], zorder=4
    )
    fig.text(
        x + 0.018,
        y + 0.026,
        value,
        fontsize=13,
        fontweight="semibold",
        color=color,
        zorder=4,
    )


def add_pill(
    fig: matplotlib.figure.Figure,
    *,
    x: float,
    y: float,
    text: str,
    color: str,
) -> None:
    """Draw a small labeled pill."""

    fig.text(
        x,
        y,
        text,
        fontsize=8,
        color=COLORS["text"],
        ha="left",
        va="center",
        bbox={
            "boxstyle": "round,pad=0.35,rounding_size=0.12",
            "facecolor": color,
            "edgecolor": color,
            "alpha": 0.82,
        },
    )


def add_panel_label(
    ax: plt.Axes,
    title: str,
    *,
    subtitle: str | None = None,
) -> None:
    """Add a compact panel label above an axes."""

    ax.text(
        0,
        1.06 if subtitle else 1.025,
        title,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.5,
        fontweight="semibold",
        color=COLORS["text"],
    )
    if subtitle:
        ax.text(
            0,
            1.015,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=7.8,
            color=COLORS["muted"],
        )
