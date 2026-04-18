"""Assert that the YAML configs parse and contain the fields every agent depends on."""
from __future__ import annotations

import yaml

from config.paths import (
    CALENDARS_YML,
    CHAIN_TAXONOMY_YML,
    CURATION_SNAPSHOTS_YML,
    EVENTS_YML,
    FACTOR_BLOCKS_YML,
)


def _load(p):
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_calendars_yml_has_required_calendars() -> None:
    data = _load(CALENDARS_YML)
    assert "calendar_daily" in data
    assert data["calendar_daily"]["frequency"] == "D"


def test_factor_blocks_declares_five_blocks() -> None:
    data = _load(FACTOR_BLOCKS_YML)
    for block in ("macro", "institutional", "liquidity", "btc_native", "eth_native"):
        assert block in data, f"factor_blocks.yml missing block: {block}"
        assert "files" in data[block], f"{block} has no files list"


def test_events_yml_has_primary_breaks() -> None:
    data = _load(EVENTS_YML)
    ids = {e["id"] for e in data["primary_breaks"]}
    assert "btc_spot_etf_launch" in ids
    assert "eth_spot_etf_launch" in ids
    assert "bitcoin_halving_2024" in ids


def test_chain_taxonomy_blocks_summing_l1_and_l2() -> None:
    data = _load(CHAIN_TAXONOMY_YML)
    assert "ethereum_ecosystem" in data
    assert "l1" in data["ethereum_ecosystem"]
    assert "canonical_l2" in data["ethereum_ecosystem"]


def test_curation_snapshots_is_parsable() -> None:
    data = _load(CURATION_SNAPSHOTS_YML)
    assert "validate" in data
