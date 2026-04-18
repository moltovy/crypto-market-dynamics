"""Single source of truth for every project path.

Every script, tool, and notebook resolves its paths from this module instead of
re-deriving them from ``__file__`` / ``Path(__file__).parents[N]``. This eliminates
the four drifting root-resolution conventions observed across the tools/ tree as
of 2026-04-18.
"""

from __future__ import annotations

from pathlib import Path

# --- Anchor: this file lives at <root>/config/paths.py
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

# --- Top-level folders (all relative to PROJECT_ROOT)
DATA_DIR: Path = PROJECT_ROOT / "Data"
DATA_META_DIR: Path = DATA_DIR / "_meta"

CONFIG_DIR: Path = PROJECT_ROOT / "config"
SRC_DIR: Path = PROJECT_ROOT / "src" / "cqresearch"
SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"
NOTEBOOKS_DIR: Path = PROJECT_ROOT / "notebooks"
TOOLS_DIR: Path = PROJECT_ROOT / "tools"
TESTS_DIR: Path = PROJECT_ROOT / "tests"
PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"

REPORTS_DIR: Path = PROJECT_ROOT / "reports"
REPORTS_PANELS_DIR: Path = REPORTS_DIR / "panels"
REPORTS_FIGURES_DIR: Path = REPORTS_DIR / "figures"
REPORTS_TABLES_DIR: Path = REPORTS_DIR / "tables"
REPORTS_DRAFTS_DIR: Path = REPORTS_DIR / "drafts"
REPORTS_APPENDIX_DIR: Path = REPORTS_DIR / "appendix"
REPORTS_RUN_SUMMARIES_DIR: Path = REPORTS_DIR / "run_summaries"
REPORTS_PRIOR_AI_OUTPUTS_DIR: Path = REPORTS_DIR / "prior_ai_outputs"
REPORTS_DEEP_RESEARCH_DIR: Path = REPORTS_DIR / "deep_research"

# Short aliases (preferred in notebooks and scripts)
PANELS_DIR = REPORTS_PANELS_DIR
FIGURES_DIR = REPORTS_FIGURES_DIR
TABLES_DIR = REPORTS_TABLES_DIR
DRAFTS_DIR = REPORTS_DRAFTS_DIR
RUN_SUMMARIES_DIR = REPORTS_RUN_SUMMARIES_DIR
PRIOR_AI_OUTPUTS_DIR = REPORTS_PRIOR_AI_OUTPUTS_DIR

DOCS_DIR: Path = PROJECT_ROOT / "docs"
DOCS_CONTEXT_DIR: Path = DOCS_DIR / "context"
DOCS_MANAGER_DIR: Path = DOCS_DIR / "manager"
DOCS_SPECS_DIR: Path = DOCS_DIR / "specs"
DOCS_DECISIONS_DIR: Path = DOCS_DIR / "decisions"
DOCS_LITERATURE_DIR: Path = DOCS_DIR / "literature"

REFERENCES_DIR: Path = PROJECT_ROOT / "references"
ARCHIVE_DIR: Path = PROJECT_ROOT / "archive"

# --- Canonical config files
CALENDARS_YML: Path = CONFIG_DIR / "calendars.yml"
CHAIN_TAXONOMY_YML: Path = CONFIG_DIR / "chain_taxonomy.yml"
FACTOR_BLOCKS_YML: Path = CONFIG_DIR / "factor_blocks.yml"
EVENTS_YML: Path = CONFIG_DIR / "events.yml"
CURATION_SNAPSHOTS_YML: Path = CONFIG_DIR / "curation_snapshots.yml"


def ensure_exists(*paths: Path) -> None:
    """Create any of the given directories that do not exist. Idempotent."""
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "DATA_META_DIR",
    "CONFIG_DIR",
    "SRC_DIR",
    "SCRIPTS_DIR",
    "NOTEBOOKS_DIR",
    "TOOLS_DIR",
    "TESTS_DIR",
    "PROMPTS_DIR",
    "REPORTS_DIR",
    "REPORTS_PANELS_DIR",
    "REPORTS_FIGURES_DIR",
    "REPORTS_TABLES_DIR",
    "REPORTS_DRAFTS_DIR",
    "REPORTS_APPENDIX_DIR",
    "REPORTS_RUN_SUMMARIES_DIR",
    "REPORTS_PRIOR_AI_OUTPUTS_DIR",
    "REPORTS_DEEP_RESEARCH_DIR",
    "PANELS_DIR",
    "FIGURES_DIR",
    "TABLES_DIR",
    "DRAFTS_DIR",
    "RUN_SUMMARIES_DIR",
    "PRIOR_AI_OUTPUTS_DIR",
    "DOCS_DIR",
    "DOCS_CONTEXT_DIR",
    "DOCS_MANAGER_DIR",
    "DOCS_SPECS_DIR",
    "DOCS_DECISIONS_DIR",
    "DOCS_LITERATURE_DIR",
    "REFERENCES_DIR",
    "ARCHIVE_DIR",
    "CALENDARS_YML",
    "CHAIN_TAXONOMY_YML",
    "FACTOR_BLOCKS_YML",
    "EVENTS_YML",
    "CURATION_SNAPSHOTS_YML",
    "ensure_exists",
]
