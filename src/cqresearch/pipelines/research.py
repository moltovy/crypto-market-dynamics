"""Pipeline entry points for the canonical `research/` surface."""

from __future__ import annotations

from pathlib import Path

from config.paths import PROJECT_ROOT

from cqresearch.research.analytical_modules import (
    MODULE_SPECS,
    build_all_analytical_modules,
    build_analytical_module,
    build_research_only_figures,
)
from cqresearch.research.checks import check_research_surface
from cqresearch.research.data_foundation import MODULE_ID as DATA_FOUNDATION_ID
from cqresearch.research.data_foundation import build_data_foundation
from cqresearch.research.registry import module_by_id
from cqresearch.research.root_surface import build_root_research_surface


def run_research(module: str = "all", root: Path = PROJECT_ROOT) -> list[Path]:
    if module == DATA_FOUNDATION_ID:
        artifacts = build_data_foundation(root)
        return artifacts
    if module == "all":
        artifacts = build_data_foundation(root)
        artifacts.extend(build_all_analytical_modules(root))
        artifacts.extend(build_root_research_surface(root))
        return artifacts
    if module in MODULE_SPECS:
        return build_analytical_module(module, root)
    module_by_id(module)
    raise SystemExit(f"Research module {module} is registered but has no builder.")


def build_research_figures(module: str = "all", root: Path = PROJECT_ROOT) -> list[Path]:
    if module == DATA_FOUNDATION_ID:
        return []
    if module == "all" or module in MODULE_SPECS:
        return build_research_only_figures(module, root)
    module_by_id(module)
    raise SystemExit(f"Research module {module} is registered but has no figure builder.")


def check_research(module: str = "all", root: Path = PROJECT_ROOT):
    return check_research_surface(module=module, root=root)
