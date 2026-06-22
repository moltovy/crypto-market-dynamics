"""Compatibility helpers for the canonical research figure surface.

The maintained figure builder now lives in `cqresearch.research.analytical_modules`
and is invoked through `cqresearch.pipelines.research.build_research_figures`.
This module keeps older imports working without maintaining a second figure
registry or stale public chart definitions.
"""

from __future__ import annotations

from pathlib import Path

from config.paths import PROJECT_ROOT

from cqresearch.pipelines.research import build_research_figures
from cqresearch.reporting.public_surface import GALLERY_FIGURES, PUBLIC_FIGURES


def build_public_figures(root: Path = PROJECT_ROOT) -> list[Path]:
    """Build the current canonical research figures."""

    return build_research_figures(module="all", root=root)


def public_figure_paths(root: Path = PROJECT_ROOT) -> list[Path]:
    """Return existing public figure paths from the current registry."""

    return [root / figure.filename for figure in PUBLIC_FIGURES]


def gallery_figure_paths(root: Path = PROJECT_ROOT) -> list[Path]:
    """Return existing gallery figure paths from the current registry."""

    return [root / relpath for relpath in GALLERY_FIGURES]
