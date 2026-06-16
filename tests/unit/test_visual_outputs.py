from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "outputs" / "figures"

EXPECTED_FIGURES = [
    "F00_project_summary_card.png",
    "F01_data_coverage.png",
    "F02_btc_block_attribution.png",
    "F03_btc_etf_lead_lag.png",
    "F04_btc_rolling_correlations.png",
    "F05_stablecoin_supply_tvl.png",
    "F06_btc_native_dashboard.png",
    "F07_connectedness.png",
    "F08_robustness_grid.png",
    "F09_key_results_cards.png",
    "T00_key_results_table.png",
]


def test_canonical_visual_outputs_exist_and_are_readme_ready() -> None:
    for filename in EXPECTED_FIGURES:
        path = FIGURES / filename
        assert path.exists(), filename
        assert path.stat().st_size > 20_000, filename
        assert path.with_suffix(".svg").exists(), filename
        with Image.open(path) as image:
            width, height = image.size
            assert width >= 1200, filename
            assert height >= 675, filename
            pixels = np.asarray(image.convert("RGB"))
        assert float(pixels.std()) > 3.0, filename


def test_readme_image_links_resolve_to_public_outputs() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
    assert image_paths
    for raw_path in image_paths:
        assert "archive/" not in raw_path
        assert "portfolio_v2" not in raw_path
        path = ROOT / raw_path
        assert path.exists(), raw_path
