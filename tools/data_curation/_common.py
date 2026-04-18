"""Shared helpers for the Data/ curation pipeline.

All scripts in this folder import from this module.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Make the project root importable so `from config.paths import ...` works
# when this script is invoked directly (python tools/data_curation/XX_*.py).
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    # Canonical paths live in config/paths.py (single source of truth).
    from config.paths import DATA_DIR, DATA_META_DIR as META_DIR, PROJECT_ROOT as ROOT
except Exception:  # pragma: no cover - fall back if config/ not present yet
    ROOT = _ROOT
    DATA_DIR = ROOT / "Data"
    META_DIR = DATA_DIR / "_meta"

LOG_PATH = META_DIR / "curation_log.md"


def load_curation_snapshots() -> dict:
    """Load config/curation_snapshots.yml. Returns {} if file or PyYAML missing."""
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    p = ROOT / "config" / "curation_snapshots.yml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ensure_meta_dir() -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_data_files(exts: Iterable[str] = (".csv", ".txt", ".md")) -> list[Path]:
    out: list[Path] = []
    for p in DATA_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            out.append(p)
    return sorted(out, key=lambda x: str(x).lower())


def rel_to_data(path: Path) -> str:
    return str(path.relative_to(DATA_DIR)).replace("\\", "/")


def log(section: str, lines: list[str]) -> None:
    ensure_meta_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    header = f"\n## {section}  _(run {ts})_\n"
    body = "\n".join(lines) if lines else "_(no changes)_"
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(header + "\n" + body + "\n")


def reset_log() -> None:
    """Overwrite the curation log header. Called at the start of the pipeline."""
    ensure_meta_dir()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    LOG_PATH.write_text(
        "# Data curation log\n\n"
        f"First opened: {ts}.\n"
        "This file records what the curation scripts did to every file under `Data/`.\n",
        encoding="utf-8",
    )


_SLUG_RX = re.compile(r"[^A-Za-z0-9]+")


def slugify(s: str) -> str:
    return _SLUG_RX.sub("_", s).strip("_")
