"""Artifact-writing helpers for deterministic research modules."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def write_csv(path: Path, frame: pd.DataFrame) -> Path:
    """Write a CSV artifact with stable row order supplied by the caller."""

    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n")
    return path


def write_text(path: Path, text: str) -> Path:
    """Write markdown/text with one trailing newline."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8", newline="\n")
    return path


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """Write JSON deterministically."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: Path, root: Path) -> dict[str, Any]:
    relpath = path.relative_to(root).as_posix()
    return {
        "path": relpath,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
