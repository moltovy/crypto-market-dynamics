from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_FIGURES = ROOT / "outputs" / "figures" / "public"

EXPECTED_FIGURES = [
    "01_mvrv_mechanics.png",
    "02_tradfi_exposure_shift.png",
    "03_etf_market_plumbing.png",
    "04_leverage_tail_stress.png",
    "05_point_in_time_market_structure.png",
    "06_selected_major_asset_risk.png",
]
BANNED_NAME_TERMS = ["dashboard", "contact_sheet", "gap", "triage", "before", "legacy"]


def test_public_visual_outputs_are_exactly_the_canonical_six() -> None:
    png_names = sorted(path.name for path in PUBLIC_FIGURES.glob("*.png"))
    assert png_names == EXPECTED_FIGURES

    for filename in EXPECTED_FIGURES:
        path = PUBLIC_FIGURES / filename
        assert path.stat().st_size > 50_000, filename
        assert path.with_suffix(".svg").exists(), filename
        assert not any(term in filename.lower() for term in BANNED_NAME_TERMS), filename
        with Image.open(path) as image:
            width, height = image.size
            assert width > 1200, filename
            assert height >= 675, filename
            pixels = np.asarray(image.convert("RGB"))
        assert float(pixels.std()) > 3.0, filename


def test_public_figure_registry_matches_files_and_readme() -> None:
    registry = yaml.safe_load((ROOT / "config" / "public_figures.yml").read_text(encoding="utf-8"))
    registry_paths = [Path(item["filename"]).name for item in registry["figures"]]
    assert registry_paths == EXPECTED_FIGURES

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
    assert image_paths == [f"outputs/figures/public/{name}" for name in EXPECTED_FIGURES]
    assert "public_contact_sheet" not in readme
    assert not re.search(r"outputs/figures/public/[FT]\d+", readme)
    for raw_path in image_paths:
        assert "archive/" not in raw_path
        assert "portfolio_v2" not in raw_path
        assert (ROOT / raw_path).exists(), raw_path
