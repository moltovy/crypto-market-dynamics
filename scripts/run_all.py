"""Canonical public reproduction entry point.

The maintained analytics artifacts are tracked in the repository. This wrapper
exports the clean public packet under outputs/ without refreshing raw Data/.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.export_outputs import main as export_outputs_main  # noqa: E402


def main() -> int:
    return export_outputs_main()


if __name__ == "__main__":
    raise SystemExit(main())
