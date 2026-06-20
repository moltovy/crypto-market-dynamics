"""Clean, data-first chart components."""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cqresearch.viz.design_system import COLORS


def add_lollipop(ax: plt.Axes, y: pd.Series, x: pd.Series, color: str = COLORS["institutional"], highlight_idx: int | None = None, highlight_color: str = COLORS["btc"]) -> None:
    """Draw a lollipop chart."""
    x_vals = np.array(x)
    y_vals = np.array(y)

    ax.vlines(x=x_vals, ymin=0, ymax=y_vals, color=color, alpha=0.7, linewidth=2)
    ax.scatter(x_vals, y_vals, color=color, s=50, zorder=3)

    if highlight_idx is not None:
        ax.vlines(x=x_vals[highlight_idx], ymin=0, ymax=y_vals[highlight_idx], color=highlight_color, alpha=1.0, linewidth=3.5)
        ax.scatter(x_vals[highlight_idx], y_vals[highlight_idx], color=highlight_color, s=90, zorder=4)

def add_horizontal_bar(ax: plt.Axes, labels: Sequence[str], values: Sequence[float], color: str = COLORS["institutional"], highlight_idx: int | None = None, highlight_color: str = COLORS["btc"]) -> None:
    """Draw a clean horizontal bar chart."""
    y_pos = np.arange(len(labels))
    colors = [highlight_color if i == highlight_idx else color for i in range(len(labels))]

    bars = ax.barh(y_pos, values, height=0.6, color=colors, alpha=0.9, zorder=3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # Labels read top-to-bottom

    # Add data labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.01, bar.get_y() + bar.get_height()/2, f"{width:.3f}",
                va='center', ha='left', fontsize=9, color=COLORS["text"], fontweight="semibold")

def add_gantt(ax: plt.Axes, labels: Sequence[str], starts: Sequence[pd.Timestamp], ends: Sequence[pd.Timestamp], counts: Sequence[int], color: str = COLORS["btc"]) -> None:
    """Draw a Gantt-style timeline for data coverage."""
    y_pos = np.arange(len(labels))

    for i in range(len(labels)):
        ax.barh(y_pos[i], ends[i] - starts[i], left=starts[i], height=0.5, color=color, alpha=0.8)
        # Add file count text to the right
        ax.text(ends[i] + pd.Timedelta(days=60), y_pos[i], f"{counts[i]:,} files",
                va='center', fontsize=9, color=COLORS["muted"])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()

def style_small_multiple(ax: plt.Axes) -> None:
    """Clean up an axis for a small multiple grid."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLORS["grid"])
    ax.spines["bottom"].set_color(COLORS["grid"])
    ax.tick_params(axis="both", colors=COLORS["muted"], labelsize=8)
    ax.grid(True, linestyle="--", alpha=0.3, color=COLORS["grid"])

def add_date_axis(ax: plt.Axes) -> None:
    """Format x-axis as dates."""
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.tick_params(axis="x", rotation=45)
