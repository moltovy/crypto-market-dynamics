"""Build figures for canonical research modules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.pipelines.research import build_research_figures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", default="all", help="Module id or 'all'.")
    args = parser.parse_args()
    artifacts = build_research_figures(module=args.module, root=ROOT)
    print(f"wrote {len(artifacts)} research artifacts")


if __name__ == "__main__":
    main()
