"""Build visual contact sheets for public figure review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cqresearch.viz.design_system import COLORS  # noqa: E402

FIGURES = ROOT / "outputs" / "figures"
V21 = ROOT / "archive" / "legacy_portfolio_releases" / "portfolio_v2_1" / "figures"
V22 = ROOT / "archive" / "legacy_portfolio_releases" / "portfolio_v2_2" / "figures"

ORIGINAL_FIGURES: tuple[tuple[Path, str], ...] = (
    (V21 / "F62_baseline_data_coverage.png", "F01 data coverage"),
    (V21 / "F10_btc_block_partial_r2_heatmap.png", "F02 block attribution"),
    (V21 / "F22_btc_etf_lead_lag_heatmap.png", "F03 ETF lead-lag"),
    (V21 / "F30_btc_rolling_correlations_180d.png", "F04 rolling correlations"),
    (V21 / "F40_stablecoin_supply_and_tvl.png", "F05 stablecoin/TVL"),
    (V21 / "F50_btc_native_zscore_dashboard.png", "F06 BTC native"),
    (V22 / "F77_rolling_connectedness.png", "F07 connectedness"),
    (V22 / "F78_robustness_grid_heatmap.png", "F08 robustness"),
)

FINAL_FIGURES: tuple[str, ...] = (
    "F00_project_summary_card.png",
    "F01_data_coverage.png",
    "F02_btc_block_attribution.png",
    "F03_btc_etf_lead_lag.png",
    "F04_btc_rolling_correlations.png",
    "F05_stablecoin_supply_tvl.png",
    "F06_btc_native_dashboard.png",
    "F07_connectedness.png",
    "F08_robustness_grid.png",
    "F09_key_results_cards.png",
    "T00_key_results_table.png",
)


def _fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
    try:
        return ImageFont.truetype("arial.ttf", 22), ImageFont.truetype("arial.ttf", 14)
    except Exception:
        return ImageFont.load_default(), ImageFont.load_default()


def build_contact_sheet(
    items: list[tuple[Path, str]],
    output: Path,
    *,
    subtitle: str,
    cols: int = 2,
) -> Path:
    """Create a dark thumbnail sheet from image paths."""

    output.parent.mkdir(parents=True, exist_ok=True)
    title_font, small_font = _fonts()
    thumb_w, thumb_h = 460, 259
    pad, label_h = 28, 58
    rows = (len(items) + cols - 1) // cols
    width = cols * thumb_w + (cols + 1) * pad
    height = rows * (thumb_h + label_h) + (rows + 1) * pad
    canvas = Image.new("RGB", (width, height), COLORS["bg"])
    draw = ImageDraw.Draw(canvas)

    for idx, (path, label) in enumerate(items):
        row, col = divmod(idx, cols)
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        draw.rounded_rectangle(
            [x - 8, y - 8, x + thumb_w + 8, y + thumb_h + label_h + 8],
            radius=14,
            fill=COLORS["surface"],
            outline=COLORS["grid"],
            width=2,
        )
        draw.text((x, y + 6), label, fill=COLORS["text"], font=title_font)
        draw.text((x, y + 34), subtitle, fill=COLORS["muted"], font=small_font)
        if not path.exists():
            draw.text((x + 16, y + label_h + 40), "missing", fill=COLORS["risk"], font=title_font)
            continue
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x_offset = x + (thumb_w - image.width) // 2
            y_offset = y + label_h + (thumb_h - image.height) // 2
            canvas.paste(image, (x_offset, y_offset))

    canvas.save(output)
    return output


def build_current_contact_sheet() -> Path:
    return build_contact_sheet(
        [(path, label) for path, label in ORIGINAL_FIGURES],
        FIGURES / "current_contact_sheet.png",
        subtitle="before redesign: archived diagnostic plots",
    )


def build_final_gallery() -> Path:
    items = [(FIGURES / filename, filename.replace("_", " ").replace(".png", "")) for filename in FINAL_FIGURES]
    return build_contact_sheet(items, FIGURES / "visual_gallery.png", subtitle="final public visual system")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["current", "final", "all"], default="all")
    args = parser.parse_args(argv)
    if args.kind in {"current", "all"}:
        print(f"[ok] {build_current_contact_sheet().relative_to(ROOT)}")
    if args.kind in {"final", "all"}:
        print(f"[ok] {build_final_gallery().relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
