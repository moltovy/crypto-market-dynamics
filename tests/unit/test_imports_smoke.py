"""Smoke tests: every public subpackage of cqresearch and config must import cleanly.

Keep this file fast and side-effect-free. Any import errors here mean the
skeleton is broken for every downstream agent.
"""
from __future__ import annotations


def test_config_paths_importable() -> None:
    from config.paths import (
        CALENDARS_YML,
        CHAIN_TAXONOMY_YML,
        CURATION_SNAPSHOTS_YML,
        DATA_DIR,
        EVENTS_YML,
        FACTOR_BLOCKS_YML,
        PANELS_DIR,
        PROJECT_ROOT,
        RUN_SUMMARIES_DIR,
    )

    assert PROJECT_ROOT.exists()
    assert DATA_DIR.exists()
    for yml in (CALENDARS_YML, CHAIN_TAXONOMY_YML, FACTOR_BLOCKS_YML, EVENTS_YML, CURATION_SNAPSHOTS_YML):
        assert yml.exists(), f"Missing config file: {yml}"
    assert str(PANELS_DIR).endswith("panels")
    assert str(RUN_SUMMARIES_DIR).endswith("run_summaries")


def test_cqresearch_subpackages_importable() -> None:
    import cqresearch
    from cqresearch import analysis, data, features, modeling, utils, viz  # noqa: F401

    assert cqresearch.__version__
