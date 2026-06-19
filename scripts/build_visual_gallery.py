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

PUBLIC_FIGURES: tuple[str, ...] = (
    "F01_mvrv_sensitivity_by_regime_v2.png",
    "F02_same_support_ablation.png",
    "F03_btc_ex_mvrv_strength.png",
    "F04_etf_flow_lead_lag.png",
    "F05_core_correlation_matrix.png",
    "F07_feature_strength_heatmap.png",
    "F38_market_structure_composition.png",
    "F39_top100_concentration.png",
    "F40_rank_turnover.png",
    "F41_cycle_phase_market_structure.png",
    "F42_market_evolution_dashboard.png",
    "F45_market_structure_composition_shift.png",
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

def build_public_contact_sheet() -> Path:
    items = [
        (FIGURES / filename, filename.replace("_", " ").replace(".png", ""))
        for filename in PUBLIC_FIGURES
    ]
    return build_contact_sheet(
        items,
        FIGURES / "public_contact_sheet.png",
        subtitle="canonical public figure set",
    )

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["public"], default="public")
    args = parser.parse_args(argv)
    if args.kind == "public":
        print(f"[ok] {build_public_contact_sheet().relative_to(ROOT)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
