from __future__ import annotations

from cqresearch.data.market_structure_cache import redact_text, redact_url


def test_redact_url_removes_query_keys_and_defillama_path_key() -> None:
    assert "REDACTED" in redact_url("https://example.com/path?api_key=abc123&x=1")
    safe = redact_url("https://pro-api.llama.fi/abcdefghijklmnopqrstuvwxyz123456/etfs")
    assert "abcdefghijklmnopqrstuvwxyz" not in safe
    assert "REDACTED" in safe


def test_redact_text_removes_env_style_secrets() -> None:
    text = "CMC_API_KEY=abc DEFILLAMA_API_KEY=def X-CMC_PRO_API_KEY: ghi"
    safe = redact_text(text, ["abc", "def", "ghi"])
    assert "abc" not in safe
    assert "def" not in safe
    assert "ghi" not in safe
