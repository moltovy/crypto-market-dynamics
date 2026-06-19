"""Canonical public reproduction entry point.

The maintained analytics artifacts are tracked in the repository. This wrapper
exports the clean public packet under outputs/ without refreshing raw Data/.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.build_visual_gallery import build_public_contact_sheet  # noqa: E402
from scripts.export_outputs import main as export_outputs_main  # noqa: E402

from cqresearch.analysis.constituent_rotation import (  # noqa: E402
    ingest_defillama_daily_constituents,
)
from cqresearch.analysis.market_structure_pipeline import (  # noqa: E402
    build_outputs as build_market_structure_outputs,
)
from cqresearch.analysis.market_structure_pipeline import (  # noqa: E402
    normalize_cache_to_curated,
)
from cqresearch.analysis.market_universe import ingest_defillama_monthly_universe  # noqa: E402


def main() -> int:
    status = export_outputs_main()
    if status != 0:
        return status
    ingest_defillama_monthly_universe(ROOT)
    ingest_defillama_daily_constituents(ROOT)
    normalize_cache_to_curated(ROOT, cache_only=True)
    build_market_structure_outputs(ROOT)
    build_public_contact_sheet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
