# -*- coding: utf-8 -*-
"""验收 v2：
- 色板检查（允许抗锯齿混合：颜色须落在两个色板色的连线附近）
- PPTX 完整性检查（页数、每页是否有整页图片）
"""
import os, glob
from collections import Counter
from PIL import Image
from pptx import Presentation

ROOT = r"D:\learning\Learning\microVMprac"
SRC = os.path.join(ROOT, "04-AgentENV", "图片-30页")
PPTX = os.path.join(ROOT, "04-AgentENV", "AgentENV-复习课件-30页.pptx")

PAL = [(0x1D,0x21,0x25),(0x04,0x77,0x61),(0xE3,0xF2,0xEE),(0xEC,0xF6,0xF4),
       (0xDF,0x96,0x2A),(0xC9,0x7A,0x12),(0xFD,0xF3,0xE1),(0xD9,0x57,0x3B),
       (0xFB,0xED,0xE8),(0x7D,0x84,0x8C),(0x5B,0x62,0x6A),(0xF6,0xF7,0xF8),
       (0xE1,0xE5,0xE8),(0xFF,0xFF,0xFF),(0xF0,0xF2,0xF1),(0xAA,0xB6,0xB2)]

def near_palette(c, tol=4):
    return min(max(abs(c[0]-p[0]), abs(c[1]-p[1]), abs(c[2]-p[2])) for p in PAL) <= tol

def is_blend(c, tol=7):
    """判断 c 是否落在两个色板色的连线附近（抗锯齿混合）。"""
    for i in range(len(PAL)):
        for j in range(i, len(PAL)):
            a, b = PAL[i], PAL[j]
            # 投影到线段
            ab = [b[k]-a[k] for k in range(3)]
            denom = sum(v*v for v in ab)
            if denom == 0:
                continue
            t = sum((c[k]-a[k])*ab[k] for k in range(3)) / denom
            t = max(0.0, min(1.0, t))
            proj = [a[k] + t*ab[k] for k in range(3)]
            if max(abs(c[k]-proj[k]) for k in range(3)) <= tol:
                return True
    return False

def check(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((900, 900))
    cnt = Counter(im.getdata())
    total = sum(cnt.values())
    bad = []
    for color, n in cnt.most_common(80):
        if n / total < 0.002:
            continue
        if near_palette(color) or is_blend(color):
            continue
        bad.append((color, round(n/total*100, 2)))
    return bad

def main():
    files = sorted(glob.glob(os.path.join(SRC, "p*.png")))
    bad_pages = 0
    for f in files:
        b = check(f)
        if b:
            bad_pages += 1
            print("  越界色", os.path.basename(f), b[:3])
    print("pages:", len(files), "palette-bad pages:", bad_pages)

    prs = Presentation(PPTX)
    print("pptx slides:", len(prs.slides))
    missing = 0
    for i, s in enumerate(prs.slides, 1):
        pics = [sh for sh in s.shapes if sh.shape_type == 13]
        if len(pics) != 1:
            missing += 1
            print("  slide", i, "pictures:", len(pics))
    print("slides without exactly one picture:", missing)
    sizes = {(round(s.shapes[0].width/914400, 2), round(s.shapes[0].height/914400, 2))
             for s in prs.slides if s.shapes}
    print("picture sizes (in):", sizes)
    print("pptx size MB:", round(os.path.getsize(PPTX)/1048576, 2))

if __name__ == "__main__":
    main()
