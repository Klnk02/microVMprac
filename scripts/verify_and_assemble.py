# -*- coding: utf-8 -*-
"""验收与组装：
1) 色板检查（出现频率高的颜色必须落在色板或其抗锯齿混合内）
2) 导出 1920x1080
3) 用 python-pptx 组装 960x540 的 PPTX
"""
import os, sys, glob
from collections import Counter
from PIL import Image
from pptx import Presentation
from pptx.util import Inches

ROOT = r"D:\learning\Learning\microVMprac"
SRC = os.path.join(ROOT, "04-AgentENV", "图片-30页")
OUT1080 = os.path.join(ROOT, "04-AgentENV", "图片-30页-1920")
PPTX = os.path.join(ROOT, "04-AgentENV", "AgentENV-复习课件-30页.pptx")

PALETTE = {
    "1D2125": (0x1D, 0x21, 0x25), "047761": (0x04, 0x77, 0x61),
    "E3F2EE": (0xE3, 0xF2, 0xEE), "ECF6F4": (0xEC, 0xF6, 0xF4),
    "DF962A": (0xDF, 0x96, 0x2A), "C97A12": (0xC9, 0x7A, 0x12),
    "FDF3E1": (0xFD, 0xF3, 0xE1), "D9573B": (0xD9, 0x57, 0x3B),
    "FBEDE8": (0xFB, 0xED, 0xE8), "7D848C": (0x7D, 0x84, 0x8C),
    "5B626A": (0x5B, 0x62, 0x6A), "F6F7F8": (0xF6, 0xF7, 0xF8),
    "E1E5E8": (0xE1, 0xE5, 0xE8), "FFFFFF": (0xFF, 0xFF, 0xFF),
    "F0F2F1": (0xF0, 0xF2, 0xF1), "AAB6B2": (0xAA, 0xB6, 0xB2),
}

def dist(a, b):
    return max(abs(a[0]-b[0]), abs(a[1]-b[1]), abs(a[2]-b[2]))

def check_palette(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((800, 800))
    cnt = Counter(im.getdata())
    total = sum(cnt.values())
    bad = []
    for color, n in cnt.most_common(60):
        share = n / total
        if share < 0.0008:
            continue
        d = min(dist(color, p) for p in PALETTE.values())
        if d > 26:
            bad.append((color, round(share*100, 2), d))
    return bad

def main():
    os.makedirs(OUT1080, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "p*.png")))
    print("pages:", len(files))
    problems = 0
    for f in files:
        bad = check_palette(f)
        if bad:
            problems += 1
            print("  palette issue", os.path.basename(f), bad[:3])
    print("palette pages with issues:", problems)

    # 1920x1080 导出
    for f in files:
        im = Image.open(f).convert("RGB")
        im.resize((1920, 1080), Image.LANCZOS).save(os.path.join(OUT1080, os.path.basename(f)), optimize=True)
    print("exported 1920x1080:", len(files))

    # PPTX 组装（960x540 英寸制：10x5.625in）
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)
    for f in files:
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(f, 0, 0, width=Inches(10), height=Inches(5.625))
    prs.save(PPTX)
    print("saved:", PPTX, "slides:", len(prs.slides))

if __name__ == "__main__":
    main()
