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
BANNED_ROOT_FIGURES = {
    Path("research/04_etf_institutional_plumbing/figures/02_etf_market_plumbing.png"),
    Path("research/09_market_concentration_state/figures/market_concentration_state.png"),
    Path("research/08_relative_major_asset_risk/figures/05_selected_major_asset_risk.png"),
}


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
    public_rows = [item for item in registry["figures"] if item.get("status") == "public"]
    registry_paths = [Path(item["filename"]) for item in public_rows]
    assert registry_paths == EXPECTED_FIGURE_PATHS
    for item in registry["figures"]:
        relpath = Path(item["filename"])
        assert (ROOT / relpath).exists(), relpath
        if item.get("svg_required"):
            assert (ROOT / relpath).with_suffix(".svg").exists(), relpath

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    image_paths = [Path(item) for item in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme)]
    assert image_paths == EXPECTED_FIGURE_PATHS
    assert not BANNED_ROOT_FIGURES.intersection(image_paths)
    assert len(image_paths) == 5
    assert "outputs/" not in readme
    assert "public_contact_sheet" not in readme
    assert not re.search(r"figures/public/[FT]\d+", readme)
    for relpath in image_paths:
        assert "archive/" not in relpath.as_posix()
        assert "portfolio_v2" not in relpath.as_posix()
        assert (ROOT / relpath).exists(), relpath


def test_root_figure_selection_documents_scoring() -> None:
    import pandas as pd

    selection = pd.read_csv(ROOT / "research" / "root_figure_selection.csv")
    required = {
        "figure_id",
        "module",
        "finding",
        "empirical_strength",
        "robustness",
        "economic_relevance",
        "june_2026_relevance",
        "cross_asset_breadth",
        "visual_quality",
        "weighted_score",
        "hard_exclusion",
        "selected",
        "reason",
    }
    assert required.issubset(selection.columns)
    selected = selection[selection["selected"].astype(str).str.lower().eq("true")]
    assert list(selected["figure_id"]) == [item.figure_id for item in REGISTRY_PUBLIC_FIGURES]
    assert not selected["hard_exclusion"].fillna("").str.strip().any()
