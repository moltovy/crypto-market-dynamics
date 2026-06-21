from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from cqresearch.reporting.public_surface import GALLERY_FIGURES
from cqresearch.reporting.public_surface import PUBLIC_FIGURES as REGISTRY_PUBLIC_FIGURES

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_FIGURE_PATHS = [Path(item.filename) for item in REGISTRY_PUBLIC_FIGURES]
EXPECTED_GALLERY_PATHS = [Path(item) for item in GALLERY_FIGURES]
BANNED_NAME_TERMS = ["dashboard", "contact_sheet", "gap", "triage", "before", "legacy"]


def test_public_visual_outputs_are_the_canonical_readme_set() -> None:
    assert 4 <= len(EXPECTED_FIGURE_PATHS) <= 6

    for relpath in EXPECTED_FIGURE_PATHS:
        path = ROOT / relpath
        assert path.exists(), relpath
        assert path.stat().st_size > 50_000, relpath
        assert path.with_suffix(".svg").exists(), relpath
        assert not any(term in path.name.lower() for term in BANNED_NAME_TERMS), relpath
        with Image.open(path) as image:
            width, height = image.size
            assert width > 1200, relpath
            assert height >= 675, relpath
            pixels = np.asarray(image.convert("RGB"))
        assert float(pixels.std()) > 3.0, relpath

    for relpath in EXPECTED_GALLERY_PATHS:
        path = ROOT / relpath
        assert path.exists(), relpath
        assert path.with_suffix(".svg").exists(), relpath


def test_public_figure_registry_matches_files_and_readme() -> None:
    registry = yaml.safe_load((ROOT / "config" / "public_figures.yml").read_text(encoding="utf-8"))
    registry_paths = [Path(item["filename"]) for item in registry["figures"]]
    assert registry_paths == EXPECTED_FIGURE_PATHS

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    image_paths = [Path(item) for item in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)]
    assert image_paths == EXPECTED_FIGURE_PATHS
    assert "outputs/" not in readme
    assert "public_contact_sheet" not in readme
    assert not re.search(r"figures/public/[FT]\d+", readme)
    for relpath in image_paths:
        assert "archive/" not in relpath.as_posix()
        assert "portfolio_v2" not in relpath.as_posix()
        assert (ROOT / relpath).exists(), relpath
