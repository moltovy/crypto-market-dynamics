"""Backward-compatible plotting style helpers.

New public artifacts use ``cqresearch.viz.theme`` and the institutional design
system. This module remains for legacy figure scripts that import ``setup``.
"""

from __future__ import annotations

from cqresearch.viz.design_system import COLORS
from cqresearch.viz.theme import apply_institutional_mpl_theme

PALETTE: dict[str, str] = {
    "btc": COLORS["btc"],
    "eth": COLORS["eth"],
    "macro": COLORS["macro"],
    "institutional": COLORS["institutional"],
    "liquidity": COLORS["liquidity"],
    "sentiment": COLORS["neutral"],
    "crypto_native": COLORS["native"],
    "event": COLORS["muted"],
    "ok": COLORS["positive"],
    "warn": COLORS["gold"],
    "bad": COLORS["negative"],
}


def setup() -> None:
    apply_institutional_mpl_theme()


def add_footer(fig, text: str) -> None:
    fig.text(0.005, 0.005, text, ha="left", va="bottom", fontsize=7, color=COLORS["muted"])


__all__ = ["PALETTE", "add_footer", "setup"]
