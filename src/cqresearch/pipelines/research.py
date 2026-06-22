"""Pipeline entry points for the canonical `research/` surface."""

from __future__ import annotations

import shutil
from pathlib import Path

from config.paths import PROJECT_ROOT

from cqresearch.research.analytical_modules import (
    MODULE_SPECS,
    build_all_analytical_modules,
    build_analytical_module,
)
from cqresearch.research.checks import check_research_surface
from cqresearch.research.data_foundation import MODULE_ID as DATA_FOUNDATION_ID
from cqresearch.research.data_foundation import build_data_foundation
from cqresearch.research.registry import MODULES, module_by_id
from cqresearch.research.root_surface import build_root_research_surface


def run_research(module: str = "all", root: Path = PROJECT_ROOT) -> list[Path]:
    if module == DATA_FOUNDATION_ID:
        artifacts = build_data_foundation(root)
        return artifacts
    if module == "all":
        artifacts = build_data_foundation(root)
        artifacts.extend(build_all_analytical_modules(root))
        artifacts.extend(_remove_stale_research_dirs(root))
        artifacts.extend(build_root_research_surface(root))
        return artifacts
    if module in MODULE_SPECS:
        return build_analytical_module(module, root)
    module_by_id(module)
    raise SystemExit(f"Research module {module} is registered but has no builder.")


def build_research_figures(module: str = "all", root: Path = PROJECT_ROOT) -> list[Path]:
    if module == DATA_FOUNDATION_ID:
        return build_data_foundation(root)
    if module == "all":
        return run_research(module="all", root=root)
    if module in MODULE_SPECS:
        return build_analytical_module(module, root)
    module_by_id(module)
    raise SystemExit(f"Research module {module} is registered but has no figure builder.")


def check_research(module: str = "all", root: Path = PROJECT_ROOT):
    return check_research_surface(module=module, root=root)


def _remove_stale_research_dirs(root: Path) -> list[Path]:
    """Remove tracked legacy module directories after migration has copied useful work."""

    research = root / "research"
    expected = {module.module_id for module in MODULES}
    removed: list[Path] = []
    if not research.exists():
        return removed
    for path in sorted(item for item in research.iterdir() if item.is_dir()):
        if path.name in expected:
            continue
        shutil.rmtree(path)
        removed.append(path)
    return removed
