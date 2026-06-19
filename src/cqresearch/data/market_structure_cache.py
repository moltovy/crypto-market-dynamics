"""Cache and manifest helpers for optional market-structure data pulls."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SECRET_QUERY_KEYS = {
    "api_key",
    "apikey",
    "key",
    "token",
    "access_token",
    "secret",
    "x-cmc_pro_api_key",
}


def utc_now_iso() -> str:
    """Return an ISO UTC timestamp."""

    return datetime.now(UTC).replace(microsecond=0).isoformat()


def hash_payload(payload: Any) -> str:
    """Return a stable short hash for JSON-like payloads."""

    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:12]


def redact_url(url: str) -> str:
    """Redact likely key material from a URL before writing public manifests."""

    split = urlsplit(url)
    query = []
    for key, value in parse_qsl(split.query, keep_blank_values=True):
        if key.lower() in SECRET_QUERY_KEYS:
            query.append((key, "REDACTED"))
        else:
            query.append((key, value))
    path = re.sub(r"(/)([A-Za-z0-9_-]{20,})(/)", r"\1REDACTED\3", split.path)
    if "pro-api.llama.fi" in split.netloc:
        path = re.sub(r"^/[^/]+", "/REDACTED", path)
    return urlunsplit((split.scheme, split.netloc, path, urlencode(query), split.fragment))


def redact_text(text: str, secrets: list[str] | None = None) -> str:
    """Redact explicit secrets and common API-key patterns from text."""

    redacted = text
    for secret in secrets or []:
        if secret:
            redacted = redacted.replace(secret, "REDACTED")
    redacted = re.sub(r"X-CMC_PRO_API_KEY[:=]\s*[A-Za-z0-9_.-]+", "X-CMC_PRO_API_KEY=REDACTED", redacted)
    redacted = re.sub(r"DEFILLAMA_API_KEY[:=]\s*[A-Za-z0-9_.-]+", "DEFILLAMA_API_KEY=REDACTED", redacted)
    redacted = re.sub(r"CMC_API_KEY[:=]\s*[A-Za-z0-9_.-]+", "CMC_API_KEY=REDACTED", redacted)
    return redacted


@dataclass(frozen=True)
class CacheLayout:
    """Filesystem layout for local raw cache and tracked curated outputs."""

    root: Path

    @classmethod
    def from_env(cls, project_root: Path) -> CacheLayout:
        cache_dir = Path(os.getenv("DATA_CACHE_DIR", "data_cache"))
        if not cache_dir.is_absolute():
            cache_dir = project_root / cache_dir
        return cls(cache_dir)

    def source_dir(self, source: str) -> Path:
        return self.root / source

    def raw_dir(self, source: str) -> Path:
        return self.source_dir(source) / "raw"

    def manifest_dir(self, source: str) -> Path:
        return self.source_dir(source) / "manifests"

    def diagnostics_dir(self) -> Path:
        return self.root / "_diagnostics"

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.diagnostics_dir().mkdir(parents=True, exist_ok=True)

    def cache_path(self, source: str, dataset: str, params: dict[str, Any] | None = None) -> Path:
        suffix = hash_payload(params or {})
        return self.raw_dir(source) / f"{dataset}__{suffix}.json"


def write_json(path: Path, payload: Any) -> None:
    """Write JSON with stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    """Read a JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def append_manifest_row(path: Path, row: dict[str, Any], secrets: list[str] | None = None) -> None:
    """Append a JSONL manifest row with secret redaction."""

    path.parent.mkdir(parents=True, exist_ok=True)
    safe_row = json.loads(redact_text(json.dumps(row, default=str), secrets=secrets))
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(safe_row, sort_keys=True, default=str) + "\n")


def env_flag(name: str, default: bool = False) -> bool:
    """Parse a boolean environment flag."""

    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
