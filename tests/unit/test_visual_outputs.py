from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from cqresearch.reporting.public_surface import (
    GALLERY_FIGURES,
)
from cqresearch.reporting.public_surface import (
    PUBLIC_FIGURES as REGISTRY_PUBLIC_FIGURES,
)

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_FIGURES_DIR = ROOT / "outputs" / "figures" / "public"
GALLERY_FIGURES_DIR = ROOT / "outputs" / "figures" / "gallery"

EXPECTED_FIGURES = [Path(item.filename).name for item in REGISTRY_PUBLIC_FIGURES]
EXPECTED_GALLERY = [Path(item).name for item in GALLERY_FIGURES]
BANNED_NAME_TERMS = ["dashboard", "contact_sheet", "gap", "triage", "before", "legacy"]


def test_public_visual_outputs_are_exactly_the_canonical_readme_set() -> None:
    png_names = sorted(path.name for path in PUBLIC_FIGURES_DIR.glob("*.png"))
    assert png_names == EXPECTED_FIGURES
    assert 4 <= len(png_names) <= 6

    for filename in EXPECTED_FIGURES:
        path = PUBLIC_FIGURES_DIR / filename
        assert path.stat().st_size > 50_000, filename
        assert path.with_suffix(".svg").exists(), filename
        assert not any(term in filename.lower() for term in BANNED_NAME_TERMS), filename
        with Image.open(path) as image:
            width, height = image.size
            assert width > 1200, filename
            assert height >= 675, filename
            pixels = np.asarray(image.convert("RGB"))
        assert float(pixels.std()) > 3.0, filename

    for filename in EXPECTED_GALLERY:
        assert (GALLERY_FIGURES_DIR / filename).exists(), filename
        assert (GALLERY_FIGURES_DIR / filename).with_suffix(".svg").exists(), filename


def test_public_figure_registry_matches_files_and_readme() -> None:
    registry = yaml.safe_load((ROOT / "config" / "public_figures.yml").read_text(encoding="utf-8"))
    registry_paths = [Path(item["filename"]).name for item in registry["figures"]]
    assert registry_paths == EXPECTED_FIGURES

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)
    assert image_paths == [f"outputs/figures/public/{name}" for name in EXPECTED_FIGURES]
    assert "outputs/figures/gallery/measurement_mvrv_mechanics.png" in readme
    assert "public_contact_sheet" not in readme
    assert not re.search(r"outputs/figures/public/[FT]\d+", readme)
    for raw_path in image_paths:
        assert "archive/" not in raw_path
        assert "portfolio_v2" not in raw_path
        assert (ROOT / raw_path).exists(), raw_path
