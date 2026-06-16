"""Offline placeholder for an optional microstructure panel builder.

The core portfolio releases do not depend on this. A future sprint can extend
it to read versioned optional samples and write derived panel artifacts outside
the curated raw `Data/` tree.
"""
from __future__ import annotations


def main() -> int:
    print("[ok] optional microstructure panel builder placeholder; no inputs read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
