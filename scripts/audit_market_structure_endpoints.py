"""Audit market-structure endpoint coverage without exposing secrets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.data.market_structure_endpoints import (  # noqa: E402
    all_endpoint_specs,
    endpoint_audit_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print audit only; do not write diagnostics.")
    parser.add_argument("--write", action="store_true", help="Write data_cache endpoint audit diagnostics.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(ROOT / ".env")
    rows = endpoint_audit_rows(all_endpoint_specs())
    frame = pd.DataFrame(rows)
    print(frame[["source", "dataset", "tier", "frequency", "requires_key_env", "key_available"]].to_string(index=False))
    if args.write and not args.dry_run:
        out = ROOT / "data_cache" / "_diagnostics" / "market_structure_endpoint_audit.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(out, index=False)
        print(f"[ok] wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
