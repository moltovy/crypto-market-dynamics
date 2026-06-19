from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "outputs" / "figures"

EXPECTED_FIGURES = [
    "F01_mvrv_sensitivity_by_regime_v2.png",
    "F02_same_support_ablation.png",
    "F03_btc_ex_mvrv_strength.png",
    "F04_etf_flow_lead_lag.png",
    "F05_core_correlation_matrix.png",
    "F07_feature_strength_heatmap.png",
    "F38_market_structure_composition.png",
    "F39_top100_concentration.png",
    "F40_rank_turnover.png",
    "F41_cycle_phase_market_structure.png",
    "F42_market_evolution_dashboard.png",
    "F45_market_structure_composition_shift.png",
]

CORE_SVG_FIGURES = {
    "F01_mvrv_sensitivity_by_regime_v2.png",
    "F02_same_support_ablation.png",
    "F03_btc_ex_mvrv_strength.png",
    "F04_etf_flow_lead_lag.png",
    "F05_core_correlation_matrix.png",
    "F07_feature_strength_heatmap.png",
}

LEGACY_DIAGNOSTICS = [
    "F00_project_summary_card.png",
    "F01_data_coverage.png",
    "F01_data_inventory.png",
    "F02_btc_block_attribution.png",
    "F02_btc_model_sensitivity.png",
    "F03_btc_etf_lead_lag.png",
    "F04_btc_rolling_correlations.png",
    "F05_stablecoin_supply_tvl.png",
    "F06_btc_native_dashboard.png",
    "F07_connectedness.png",
    "F08_robustness_grid.png",
    "F09_key_results_cards.png",
    "T00_key_results_table.png",
    "current_contact_sheet.png",
    "triage_before_contact_sheet.png",
    "visual_gallery.png",
]

CURRENT_TOP50_FIGURES = [
    "F48_altseason_breadth.png",
    "F49_constituent_return_indexes.png",
    "F50_return_dispersion.png",
    "F51_rolling_beta_to_btc.png",
    "F52_event_response_top50.png",
    "F53_rotation_dashboard.png",
]


def test_canonical_visual_outputs_exist_and_are_readme_ready() -> None:
    for filename in EXPECTED_FIGURES:
        path = FIGURES / filename
        assert path.exists(), filename
        assert path.stat().st_size > 20_000, filename
        if filename in CORE_SVG_FIGURES:
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
    allowed = set(EXPECTED_FIGURES)
    for raw_path in image_paths:
        assert "archive/" not in raw_path
        assert "portfolio_v2" not in raw_path
        assert Path(raw_path).name in allowed
        path = ROOT / raw_path
        assert path.exists(), raw_path


def test_public_surface_excludes_archived_and_exploratory_figures() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "before redesign" not in readme.lower()
    assert (
        "Exploratory current-top50 cohort diagnostics. Survivorship-biased. "
        "Not point-in-time. Not the primary altseason backtest."
    ) in readme
    for filename in LEGACY_DIAGNOSTICS:
        assert filename not in readme
        assert not (FIGURES / filename).exists(), filename
        assert not (FIGURES / filename).with_suffix(".svg").exists(), filename
    for filename in CURRENT_TOP50_FIGURES:
        assert filename not in readme
        assert not (FIGURES / filename).exists(), filename
        assert (FIGURES / "gallery" / filename).exists(), filename


def test_public_contact_sheet_is_canonical_only() -> None:
    path = FIGURES / "public_contact_sheet.png"
    assert path.exists()
    with Image.open(path) as image:
        width, height = image.size
        assert width >= 900
        assert height >= 900
        pixels = np.asarray(image.convert("RGB"))
    assert float(pixels.std()) > 3.0

    script = (ROOT / "scripts" / "build_visual_gallery.py").read_text(encoding="utf-8")
    assert "before redesign" not in script.lower()
    assert "ORIGINAL_FIGURES" not in script
    for filename in LEGACY_DIAGNOSTICS + CURRENT_TOP50_FIGURES:
        assert filename not in script
