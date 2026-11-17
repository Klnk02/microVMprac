# -*- coding: utf-8 -*-
"""通用组装：目录里的 p*.png → 1920 导出 + 960x540 PPTX。"""
import os, sys, glob
from PIL import Image
from pptx import Presentation
from pptx.util import Inches


def main(src, pptx_path, out1080):
    files = sorted(glob.glob(os.path.join(src, "p*.png")))
    if not files:
        print("no png found in", src)
        return
    os.makedirs(out1080, exist_ok=True)
    for f in files:
        im = Image.open(f).convert("RGB")
        im.resize((1920, 1080), Image.LANCZOS).save(
            os.path.join(out1080, os.path.basename(f)), optimize=True)

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    for f in files:
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(f, 0, 0, width=Inches(10), height=Inches(5.625))
    prs.save(pptx_path)
    print("pages:", len(files), "->", pptx_path, "size MB:", round(os.path.getsize(pptx_path) / 1048576, 2))


if __name__ == "__main__":
    src = sys.argv[1]
    pptx = sys.argv[2]
    out1080 = sys.argv[3]
    main(src, pptx, out1080)
