"""Check public files for market-structure guardrail violations."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.analysis.market_structure_pipeline import (  # noqa: E402
    public_surface_findings,
    write_public_surface_report,
)


def main() -> int:
    findings = public_surface_findings(ROOT)
    report = write_public_surface_report(ROOT)
    print(f"[ok] {report.relative_to(ROOT)}")
    violations = findings[findings["status"] == "violation"]
    if not violations.empty:
        print(violations.to_string(index=False))
        return 1
    print("[ok] public surface guardrails pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
