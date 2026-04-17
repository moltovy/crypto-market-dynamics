"""Step 02: Detect byte-identical duplicates in Data/Defi/ and archive them.

Policy (conservative, per plan):
- Only files with identical SHA-256 are treated as duplicates.
- Keeps the more descriptive name (heuristic below).
- Moves the duplicate(s) to Data/Defi/_raw_parts/duplicates/.
- Near-identical-but-not-byte-equal files are LEFT UNTOUCHED and flagged in the log
  for human review.
"""
from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DATA_DIR, log, rel_to_data, sha256_of_file  # noqa: E402

DEFI_DIR = DATA_DIR / "Defi"
DUP_ARCHIVE = DEFI_DIR / "_raw_parts" / "duplicates"


def _descriptiveness_score(name: str) -> int:
    """Higher is better. Prefers names that describe content.

    Heuristics:
    - `(1)` / `(2)` copies lose points (they are usually browser "already exists" copies).
    - Longer base names (more words separated by spaces / underscores) win ties.
    - Names containing thematic keywords ("volume", "Fees and revenue") win over generic.
    """
    score = 0
    base = Path(name).stem
    if "(1)" in base or "(2)" in base or "(3)" in base:
        score -= 50
    # Word count — more descriptive names are usually longer
    words = [w for w in base.replace("_", " ").replace("-", " ").split() if w]
    score += len(words)
    # Thematic keywords
    for kw in ("fees", "revenue", "volume", "tvl", "metrics", "mcap", "flow"):
        if kw in base.lower():
            score += 2
    return score


def main() -> None:
    if not DEFI_DIR.is_dir():
        print(f"Defi dir not found: {DEFI_DIR}")
        return

    # Only top-level files of Defi (subfolders like DefiLlama CSV are separate).
    files = [p for p in DEFI_DIR.glob("*.csv") if p.is_file()]
    digest_to_paths: dict[str, list[Path]] = defaultdict(list)
    for p in files:
        digest_to_paths[sha256_of_file(p)].append(p)

    lines: list[str] = []
    archived = 0
    dup_groups = 0
    for digest, group in digest_to_paths.items():
        if len(group) < 2:
            continue
        dup_groups += 1
        # Choose keeper
        group_sorted = sorted(group, key=lambda p: _descriptiveness_score(p.name), reverse=True)
        keeper = group_sorted[0]
        losers = group_sorted[1:]
        lines.append(f"- Group `{digest[:12]}`: kept `{rel_to_data(keeper)}`.")
        DUP_ARCHIVE.mkdir(parents=True, exist_ok=True)
        for loser in losers:
            dest = DUP_ARCHIVE / loser.name
            # If dest exists, suffix until unique (should be rare).
            counter = 1
            while dest.exists():
                dest = DUP_ARCHIVE / f"{loser.stem}__{counter}{loser.suffix}"
                counter += 1
            shutil.move(str(loser), str(dest))
            archived += 1
            lines.append(f"  - Archived duplicate `{rel_to_data(loser)}` -> `{rel_to_data(dest)}`.")

    # Also flag suspected near-duplicates for human review, without touching them.
    suspected_groups = [
        [
            "all_metrics_2026-04-17.csv",
            "all_metrics_2026-04-17 (1) volume.csv",
        ],
        [
            "ethereum_metrics_2026-04-17 (1).csv",
            "ethereum_metrics_2026-04-17 Fees and revenue.csv",
            "ethereum_metrics_2026-04-17 volume.csv",
        ],
    ]
    survivors = {p.name for p in DEFI_DIR.glob("*.csv")}
    flag_lines: list[str] = []
    for grp in suspected_groups:
        present = [n for n in grp if n in survivors]
        if len(present) >= 2:
            digests = {n: sha256_of_file(DEFI_DIR / n)[:12] for n in present}
            flag_lines.append(
                "- Near-duplicate candidate group still present (different bytes, left untouched): "
                + ", ".join(f"`{n}` (sha={digests[n]})" for n in present)
            )

    if dup_groups == 0:
        lines.append("- No byte-identical duplicates found in `Data/Defi/`.")
    if flag_lines:
        lines.append("")
        lines.append("**Flagged for human review (not byte-identical, not touched):**")
        lines.extend(flag_lines)

    log("Step 02 — Defi dedupe", lines)
    print(f"Step 02 done: {dup_groups} duplicate group(s), {archived} file(s) archived.")


if __name__ == "__main__":
    main()
