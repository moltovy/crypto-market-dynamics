from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_portfolio_pipeline.py"


def load_pipeline_module():
    spec = importlib.util.spec_from_file_location("run_portfolio_pipeline", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_latest_complete_table_dir_skips_partial_newer_bundle(tmp_path):
    module = load_pipeline_module()
    required = {"a.csv", "b.json"}

    older_complete = tmp_path / "2026-04-19"
    older_complete.mkdir()
    for name in required:
        (older_complete / name).write_text("ok", encoding="utf-8")

    newer_partial = tmp_path / "2026-06-16"
    newer_partial.mkdir()
    (newer_partial / "a.csv").write_text("partial", encoding="utf-8")

    assert module.is_complete_table_dir(older_complete, required)
    assert not module.is_complete_table_dir(newer_partial, required)
    assert module.latest_complete_table_dir(tmp_path, required) == older_complete
