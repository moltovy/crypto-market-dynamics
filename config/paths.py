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
DATA_LOCAL_DIR: Path = PROJECT_ROOT / "data_local"
DATA_LOCAL_RAW_DIR: Path = DATA_LOCAL_DIR / "raw"
DATA_LOCAL_INTERIM_DIR: Path = DATA_LOCAL_DIR / "interim"
DATA_LOCAL_PROCESSED_DIR: Path = DATA_LOCAL_DIR / "processed"
DATA_LOCAL_CURATED_DIR: Path = DATA_LOCAL_DIR / "curated"
DATA_LOCAL_METADATA_DIR: Path = DATA_LOCAL_DIR / "metadata"
DATA_DIR: Path = DATA_LOCAL_RAW_DIR
DATA_META_DIR: Path = DATA_LOCAL_METADATA_DIR

CONFIG_DIR: Path = PROJECT_ROOT / "config"
SRC_DIR: Path = PROJECT_ROOT / "src" / "cqresearch"
SCRIPTS_DIR: Path = PROJECT_ROOT / "scripts"
NOTEBOOKS_DIR: Path = PROJECT_ROOT / "notebooks"
TOOLS_DIR: Path = PROJECT_ROOT / "tools"
TESTS_DIR: Path = PROJECT_ROOT / "tests"
PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"

PANELS_DIR = DATA_LOCAL_PROCESSED_DIR
RESEARCH_DIR: Path = PROJECT_ROOT / "research"

DOCS_DIR: Path = PROJECT_ROOT / "docs"
DOCS_CONTEXT_DIR: Path = DOCS_DIR / "context"
DOCS_MANAGER_DIR: Path = DOCS_DIR / "manager"
DOCS_SPECS_DIR: Path = DOCS_DIR / "specs"
DOCS_DECISIONS_DIR: Path = DOCS_DIR / "decisions"
DOCS_LITERATURE_DIR: Path = DOCS_DIR / "literature"

REFERENCES_DIR: Path = PROJECT_ROOT / "references"

# --- Canonical config files
CALENDARS_YML: Path = CONFIG_DIR / "calendars.yml"
CHAIN_TAXONOMY_YML: Path = CONFIG_DIR / "chain_taxonomy.yml"
FACTOR_BLOCKS_YML: Path = CONFIG_DIR / "factor_blocks.yml"
EVENTS_YML: Path = CONFIG_DIR / "events.yml"
CURATION_SNAPSHOTS_YML: Path = CONFIG_DIR / "curation_snapshots.yml"


def provider_data_dir(provider: str) -> Path:
    """Resolve a provider raw-data directory under the local-only layout."""

    local_map = {
        "cryptoquant": "cryptoquant",
        "artemis": "artemis",
        "tradingview": "tradingview",
        "defillama": "defillama",
        "farside": "farside",
        "fred": "fred",
        "alternativeme": "alternativeme",
        "market_structure": "market_structure",
    }
    key = provider.lower()
    if key not in local_map:
        raise KeyError(f"Unknown data provider: {provider}")
    return DATA_LOCAL_RAW_DIR / local_map[key]


def ensure_exists(*paths: Path) -> None:
    """Create any of the given directories that do not exist. Idempotent."""
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


__all__ = [
    "PROJECT_ROOT",
    "DATA_LOCAL_DIR",
    "DATA_LOCAL_RAW_DIR",
    "DATA_LOCAL_INTERIM_DIR",
    "DATA_LOCAL_PROCESSED_DIR",
    "DATA_LOCAL_CURATED_DIR",
    "DATA_LOCAL_METADATA_DIR",
    "DATA_DIR",
    "DATA_META_DIR",
    "CONFIG_DIR",
    "SRC_DIR",
    "SCRIPTS_DIR",
    "NOTEBOOKS_DIR",
    "TOOLS_DIR",
    "TESTS_DIR",
    "PROMPTS_DIR",
    "PANELS_DIR",
    "RESEARCH_DIR",
    "DOCS_DIR",
    "DOCS_CONTEXT_DIR",
    "DOCS_MANAGER_DIR",
    "DOCS_SPECS_DIR",
    "DOCS_DECISIONS_DIR",
    "DOCS_LITERATURE_DIR",
    "REFERENCES_DIR",
    "CALENDARS_YML",
    "CHAIN_TAXONOMY_YML",
    "FACTOR_BLOCKS_YML",
    "EVENTS_YML",
    "CURATION_SNAPSHOTS_YML",
    "ensure_exists",
    "provider_data_dir",
]
