"""組裝 Liquid Glass 深色 .pptx 模板。
用法：python3 build_pptx.py [-o dist/liquid-glass-dark.pptx] [--calibration]"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pptx import Presentation  # noqa: E402

from builder import load_tokens  # noqa: E402
from builder.components import add_component_slides  # noqa: E402
from builder.content import add_calibration_slide, add_example_slides  # noqa: E402
from builder.layouts import build_layouts  # noqa: E402
from builder.theme import write_theme  # noqa: E402


def build(out_path, calibration: bool = False) -> None:
    tokens = load_tokens()
    prs = Presentation(HERE / "skeleton.pptx")
    write_theme(prs, tokens)
    layouts = build_layouts(prs, tokens)
    add_example_slides(prs, layouts, tokens)
    add_component_slides(prs, layouts, tokens)
    if calibration:
        add_calibration_slide(prs, layouts, tokens)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    print(f"built: {out_path}（{out_path.stat().st_size / 1048576:.1f} MB）")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", default=str(HERE / "dist" / "liquid-glass-dark.pptx"))
    ap.add_argument("--calibration", action="store_true")
    args = ap.parse_args()
    build(args.o, calibration=args.calibration)
