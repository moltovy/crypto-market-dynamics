"""Shared matplotlib styling + palette.

Every figure in ``reports/figures/`` should start with
``from cqresearch.viz.style import setup; setup()`` so the paper has a
consistent look.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

PALETTE: dict[str, str] = {
    "btc": "#F2A900",         # orange
    "eth": "#627EEA",         # ethereum blue
    "macro": "#2F6F9F",       # blue-grey
    "institutional": "#21A179",
    "liquidity": "#B84C7D",
    "sentiment": "#7B7B7B",
    "crypto_native": "#E45B5B",
    "event": "#111111",
    "ok": "#21A179",
    "warn": "#D89614",
    "bad": "#D13D3D",
}


def setup() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 220,
            "savefig.bbox": "tight",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "legend.frameon": False,
            "font.family": "DejaVu Sans",
        }
    )


def add_footer(fig, text: str) -> None:
    fig.text(
        0.005, 0.005, text, ha="left", va="bottom", fontsize=7, color="#555555"
    )


__all__ = ["PALETTE", "setup", "add_footer"]
