"""Annotation helpers for public research figures."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date

import matplotlib.axes
import matplotlib.dates as mdates
import matplotlib.figure

from cqresearch.viz.design_system import COLORS, EVENTS, FOOTER_Y


def add_event_markers(
    ax: matplotlib.axes.Axes,
    *,
    events: Iterable[tuple[date, str, str]] = EVENTS,
    label_y: float = 0.98,
    alpha: float = 0.78,
) -> None:
    """Draw vertical event lines with compact labels."""

    y_min, y_max = ax.get_ylim()
    for event_date, label, color in events:
        x_value = mdates.date2num(event_date)
        ax.axvline(x_value, color=color, linestyle=":", linewidth=1.0, alpha=alpha, zorder=2)
        ax.text(
            x_value,
            y_min + (y_max - y_min) * label_y,
            label,
            rotation=90,
            ha="right",
            va="top",
            fontsize=7,
            color=color,
            alpha=0.95,
        )


def add_source_footer(fig: matplotlib.figure.Figure, text: str) -> None:
    """Add a consistent source/method footer."""

    fig.text(0.055, FOOTER_Y, text, ha="left", va="bottom", fontsize=7.2, color=COLORS["muted"])


def add_badge(
    ax: matplotlib.axes.Axes,
    text: str,
    *,
    x: float,
    y: float,
    color: str,
    text_color: str = COLORS["text"],
) -> None:
    """Draw a small axes-relative badge."""

    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        ha="left",
        va="center",
        fontsize=7.6,
        color=text_color,
        bbox={
            "boxstyle": "round,pad=0.32,rounding_size=0.12",
            "facecolor": color,
            "edgecolor": color,
            "alpha": 0.92,
        },
        zorder=10,
    )


def add_callout(
    ax: matplotlib.axes.Axes,
    text: str,
    *,
    xy: tuple[float, float],
    xytext: tuple[float, float],
    color: str = COLORS["gold"],
) -> None:
    """Add a compact callout arrow."""

    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        textcoords="data",
        ha="left",
        va="center",
        fontsize=7.8,
        color=COLORS["text"],
        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.9, "alpha": 0.8},
        bbox={
            "boxstyle": "round,pad=0.35,rounding_size=0.12",
            "facecolor": COLORS["surface2"],
            "edgecolor": color,
            "alpha": 0.94,
        },
        zorder=9,
    )
