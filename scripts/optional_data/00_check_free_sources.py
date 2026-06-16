"""Print the optional free-data source registry without network calls."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.optional_data import optional_source_registry  # noqa: E402


def main() -> int:
    registry = optional_source_registry()
    print(registry.to_markdown(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
