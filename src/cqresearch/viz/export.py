"""Export helpers for Matplotlib and optional Plotly figures."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import matplotlib.figure

from cqresearch.viz.design_system import COLORS, EXPORT_DPI


def save_figure(
    fig: matplotlib.figure.Figure,
    path: str | Path,
    *,
    formats: Iterable[str] = ("png", "svg"),
    dpi: int = EXPORT_DPI,
    facecolor: str | None = None,
) -> list[Path]:
    """Save a Matplotlib figure to one or more formats."""

    base = Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for fmt in formats:
        fmt = fmt.lower().lstrip(".")
        out = base.with_suffix(f".{fmt}")
        fig.savefig(
            out,
            dpi=dpi,
            facecolor=facecolor or COLORS["bg"],
            edgecolor=facecolor or COLORS["bg"],
            bbox_inches=None,
        )
        saved.append(out)
    return saved


def save_plotly_figure(
    fig: Any,
    path: str | Path,
    *,
    formats: Iterable[str] = ("png", "svg", "html"),
) -> list[Path]:
    """Save a Plotly figure, falling back to HTML when static export is unavailable."""

    base = Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    static_failed = False
    for fmt in formats:
        fmt = fmt.lower().lstrip(".")
        out = base.with_suffix(f".{fmt}")
        if fmt == "html":
            fig.write_html(out, include_plotlyjs="cdn", full_html=True)
            saved.append(out)
            continue
        if static_failed:
            continue
        try:
            fig.write_image(out)
            saved.append(out)
        except Exception:
            static_failed = True
    if not any(path.suffix == ".html" for path in saved):
        out = base.with_suffix(".html")
        fig.write_html(out, include_plotlyjs="cdn", full_html=True)
        saved.append(out)
    return saved
