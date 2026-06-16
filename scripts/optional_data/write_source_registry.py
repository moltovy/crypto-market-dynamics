"""Write the optional free-data source registry to reports/optional_data."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.optional_data import optional_source_registry  # noqa: E402


def main() -> int:
    out_dir = ROOT / "reports" / "optional_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = optional_source_registry()
    out_path = out_dir / "source_decision_table.csv"
    registry.to_csv(out_path, index=False)
    print(f"[ok] wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
