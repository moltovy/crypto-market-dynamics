"""Step 01: Record SHA-256 of every file under Data/ to Data/_meta/raw_manifest.csv.

Provides a baseline to diff against later curation stages.
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    DATA_DIR,
    META_DIR,
    ensure_meta_dir,
    iter_data_files,
    log,
    rel_to_data,
    reset_log,
    sha256_of_file,
)


def main() -> None:
    ensure_meta_dir()
    # Only reset the log on the initial manifest run.
    if not (META_DIR / "curation_log.md").exists():
        reset_log()

    files = iter_data_files(exts=(".csv", ".txt", ".md"))
    out_path = META_DIR / "raw_manifest.csv"
    rows = []
    for p in files:
        try:
            size = p.stat().st_size
            digest = sha256_of_file(p)
        except OSError as e:
            rows.append({
                "relpath": rel_to_data(p),
                "size_bytes": -1,
                "sha256": f"ERROR:{e}",
                "mtime_utc": "",
            })
            continue
        mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        rows.append({
            "relpath": rel_to_data(p),
            "size_bytes": size,
            "sha256": digest,
            "mtime_utc": mtime,
        })

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["relpath", "size_bytes", "sha256", "mtime_utc"]
        )
        w.writeheader()
        w.writerows(rows)

    log(
        "Step 01 — raw hash manifest",
        [
            f"Scanned {len(rows)} files under `Data/`.",
            f"Wrote manifest to `Data/_meta/raw_manifest.csv`.",
        ],
    )
    print(f"Step 01 done: {len(rows)} files -> {out_path}")


if __name__ == "__main__":
    main()
