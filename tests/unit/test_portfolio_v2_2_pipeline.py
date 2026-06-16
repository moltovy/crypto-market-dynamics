from __future__ import annotations

from pathlib import Path

from config.paths import PROJECT_ROOT

from cqresearch.analysis.portfolio_v2_2 import (
    build_manifest,
    ensure_portfolio_dirs,
    required_manifest_fields,
)


def test_ensure_portfolio_v2_2_dirs_creates_expected_tree(tmp_path: Path) -> None:
    paths = ensure_portfolio_dirs(tmp_path / "portfolio_v2_2")

    assert paths["base"].exists()
    assert paths["tables"].exists()
    assert paths["figures"].exists()
    assert paths["model_cards"].exists()
    assert paths["diagnostics"].exists()


def test_v2_2_manifest_includes_required_fields() -> None:
    panel_meta = {"start": "2020-01-01", "end": "2026-04-11", "n_rows": 2293, "n_cols": 63}
    manifest = build_manifest(
        panel_meta,
        [PROJECT_ROOT / "reports" / "portfolio_v2_2" / "tables" / "x.csv"],
        [PROJECT_ROOT / "reports" / "portfolio_v2_2" / "figures" / "x.png"],
        [PROJECT_ROOT / "reports" / "portfolio_v2_2" / "executive_summary.md"],
        [PROJECT_ROOT / "reports" / "portfolio_v2_2" / "model_cards" / "x.md"],
        [],
    )

    for field in required_manifest_fields():
        assert field in manifest
    assert manifest["panel"]["n_rows"] == 2293
    assert any("run_portfolio_v2_2_pipeline.py" in cmd for cmd in manifest["commands_run"])
