"""Build the master daily panel and write coverage + meta to reports/panels/."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.data.panel_builder import build_master_panel, write_panel  # noqa: E402
from config.paths import PANELS_DIR, REPORTS_RUN_SUMMARIES_DIR  # noqa: E402


def main() -> None:
    panel, report = build_master_panel()
    parquet, coverage, meta = write_panel(panel, report, PANELS_DIR)

    # Human-readable run summary
    summary = REPORTS_RUN_SUMMARIES_DIR / "02_build_master_panel.md"
    REPORTS_RUN_SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append(f"# Master panel build — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    lines.append(f"Window: **{report.master_start.date()}** → **{report.master_end.date()}** "
                 f"({report.n_rows} rows × {panel.shape[1]} columns)\n")
    lines.append(f"Parquet: `{parquet.relative_to(ROOT)}`  ")
    lines.append(f"Coverage: `{coverage.relative_to(ROOT)}`  ")
    lines.append(f"Meta: `{meta.relative_to(ROOT)}`\n")

    cov = report.coverage_by_col
    lines.append("## Column coverage\n")
    lines.append("| column | first | last | missing % |")
    lines.append("| --- | --- | --- | ---: |")
    for _, r in cov.iterrows():
        lines.append(f"| `{r['column']}` | {r['first']} | {r['last']} | {r['missing_pct']} |")
    summary.write_text("\n".join(lines), encoding="utf-8")

    print(f"[ok] panel shape={panel.shape}")
    print(f"[ok] parquet={parquet}")
    print(f"[ok] summary={summary}")
    print(
        json.dumps(
            {
                "n_rows": report.n_rows,
                "n_cols": int(panel.shape[1]),
                "first": report.master_start.date().isoformat(),
                "last": report.master_end.date().isoformat(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
