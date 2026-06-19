"""HTTP clients for optional market-structure data sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests  # type: ignore[import-untyped]

from cqresearch.data.market_structure_cache import (
    CacheLayout,
    append_manifest_row,
    read_json,
    redact_url,
    utc_now_iso,
    write_json,
)
from cqresearch.data.market_structure_endpoints import EndpointSpec


@dataclass(frozen=True)
class FetchResult:
    """Result metadata for one endpoint fetch attempt."""

    source: str
    dataset: str
    status: str
    cache_path: str
    safe_url: str
    message: str = ""
    row_count_hint: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "dataset": self.dataset,
            "status": self.status,
            "cache_path": self.cache_path,
            "safe_url": self.safe_url,
            "message": self.message,
            "row_count_hint": self.row_count_hint,
        }


def _row_count_hint(payload: Any) -> int | None:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("data", "protocols", "peggedAssets", "coins", "symbols"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
    return None


def fetch_json_spec(
    spec: EndpointSpec,
    layout: CacheLayout,
    *,
    dry_run: bool = False,
    cache_only: bool = False,
    timeout: int = 30,
    secrets: list[str] | None = None,
) -> FetchResult:
    """Fetch one endpoint or reuse/diagnose local cache."""

    layout.ensure()
    cache_path = layout.cache_path(spec.source, spec.dataset, spec.params)
    manifest_path = layout.manifest_dir(spec.source) / "fetch_manifest.jsonl"
    safe_url = spec.safe_url

    if dry_run:
        result = FetchResult(spec.source, spec.dataset, "dry_run", str(cache_path), safe_url)
        append_manifest_row(manifest_path, {**result.as_dict(), "generated_at_utc": utc_now_iso()}, secrets)
        return result

    if cache_only:
        if cache_path.exists():
            payload = read_json(cache_path)
            result = FetchResult(
                spec.source,
                spec.dataset,
                "cache_hit",
                str(cache_path),
                safe_url,
                row_count_hint=_row_count_hint(payload),
            )
        else:
            result = FetchResult(
                spec.source,
                spec.dataset,
                "cache_miss",
                str(cache_path),
                safe_url,
                "No cached payload available; no network call made.",
            )
        append_manifest_row(manifest_path, {**result.as_dict(), "generated_at_utc": utc_now_iso()}, secrets)
        return result

    if not spec.has_required_key:
        result = FetchResult(
            spec.source,
            spec.dataset,
            "skipped_missing_key",
            str(cache_path),
            safe_url,
            f"Missing required environment variable {spec.requires_key_env}.",
        )
        append_manifest_row(manifest_path, {**result.as_dict(), "generated_at_utc": utc_now_iso()}, secrets)
        return result

    try:
        response = requests.request(
            spec.method,
            spec.url,
            params=spec.params,
            headers=spec.resolved_headers(),
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status = "requires_pro_or_plan_access" if response_status(exc) in {401, 402, 403} else "http_error"
        result = FetchResult(spec.source, spec.dataset, status, str(cache_path), safe_url, str(exc))
        append_manifest_row(manifest_path, {**result.as_dict(), "generated_at_utc": utc_now_iso()}, secrets)
        return result
    except Exception as exc:
        result = FetchResult(spec.source, spec.dataset, "fetch_error", str(cache_path), safe_url, str(exc))
        append_manifest_row(manifest_path, {**result.as_dict(), "generated_at_utc": utc_now_iso()}, secrets)
        return result

    write_json(cache_path, payload)
    result = FetchResult(
        spec.source,
        spec.dataset,
        "fetched",
        str(cache_path),
        redact_url(response.url),
        row_count_hint=_row_count_hint(payload),
    )
    append_manifest_row(manifest_path, {**result.as_dict(), "generated_at_utc": utc_now_iso()}, secrets)
    return result


def response_status(exc: requests.HTTPError) -> int | None:
    """Extract response status from a requests HTTPError."""

    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None)


def fetch_many(
    specs: list[EndpointSpec],
    layout: CacheLayout,
    *,
    dry_run: bool = False,
    cache_only: bool = False,
    secrets: list[str] | None = None,
) -> list[FetchResult]:
    """Fetch or diagnose multiple endpoint specs."""

    results = []
    for spec in specs:
        results.append(
            fetch_json_spec(
                spec,
                layout,
                dry_run=dry_run,
                cache_only=cache_only,
                secrets=secrets,
            )
        )
    return results


def manifest_rows_from_results(results: list[FetchResult]) -> list[dict[str, Any]]:
    """Convert fetch results to serializable manifest rows."""

    return [result.as_dict() for result in results]


def fetch_cmc_fear_greed_history(
    spec: EndpointSpec,
    layout: CacheLayout,
    *,
    dry_run: bool = False,
    cache_only: bool = False,
    limit: int = 500,
    max_pages: int = 20,
    secrets: list[str] | None = None,
) -> list[FetchResult]:
    """Fetch CMC Fear & Greed history using offset pagination.

    CoinMarketCap caps the historical endpoint at 500 records per request. The
    API uses ``start`` as a 1-indexed offset, so cached page datasets are named
    ``fear_greed_historical_start_<offset>``.
    """

    results: list[FetchResult] = []
    start = int(spec.params.get("start", 1) or 1)
    for _ in range(max_pages):
        page_spec = EndpointSpec(
            source=spec.source,
            dataset=f"{spec.dataset}_start_{start}",
            url=spec.url,
            method=spec.method,
            params={**spec.params, "start": start, "limit": min(limit, 500)},
            headers=spec.headers,
            requires_key_env=spec.requires_key_env,
            tier=spec.tier,
            frequency=spec.frequency,
            notes=spec.notes,
        )
        result = fetch_json_spec(
            page_spec,
            layout,
            dry_run=dry_run,
            cache_only=cache_only,
            secrets=secrets,
        )
        results.append(result)
        if result.status not in {"fetched", "cache_hit"}:
            break
        try:
            payload = read_json(Path(result.cache_path))
            page_len = len(payload.get("data", [])) if isinstance(payload, dict) else 0
        except Exception:
            page_len = 0
        if dry_run or cache_only or page_len < min(limit, 500):
            break
        start += page_len
    return results
