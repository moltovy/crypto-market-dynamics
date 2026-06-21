"""Validate the canonical `research/` surface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.research import check_research


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="all", help="Module id or 'all'.")
    args = parser.parse_args()
    result = check_research(module=args.module, root=ROOT)
    print(result.to_string(index=False))


if __name__ == "__main__":
    main()
