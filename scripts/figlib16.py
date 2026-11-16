# -*- coding: utf-8 -*-
"""16:9 全页图示渲染库（matplotlib）——图即页面，文字自动收缩防溢出。"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.font_manager as fm

INK, GRAY, FAINT = "#15181C", "#5F6B7A", "#9AA3AE"
LINE, PALE, WHITE = "#DFE4EA", "#F6F8FA", "#FFFFFF"
BLUE, PURPLE, GREEN = "#2F6FEB", "#7C3AED", "#0E9F6E"
ORANGE, TEAL, VIOLET, RED = "#D97706", "#0E7490", "#9333EA", "#B42318"
AMBER = "#B45309"

for _n in ["Microsoft YaHei", "Microsoft YaHei UI", "SimHei"]:
    if any(f.name == _n for f in fm.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_n]
        plt.rcParams["font.family"] = "sans-serif"
        break
plt.rcParams["axes.unicode_minus"] = False

W, H = 13.333, 7.5
UX, UY = 133.33, 75.0          # 画布坐标：1 单位 = 0.1 英寸 = 7.2pt
PT = 7.2                       # 1 单位对应的点数

BOXES = []

def canvas():
    fig = plt.figure(figsize=(W, H), dpi=160)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, UX); ax.set_ylim(0, UY); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), UX, UY, facecolor=WHITE, edgecolor="none", zorder=0))
    BOXES.clear()
    return fig, ax

def _wlen(s):
    """加权字宽：CJK 1.0 em，ASCII 0.55 em。"""
    n = 0.0
    for ch in s:
        n += 0.55 if ord(ch) < 128 else 1.0
    return n

def _wrap(s, max_em):
    lines, cur, curlen = [], "", 0.0
    for ch in s:
        wl = 0.55 if ord(ch) < 128 else 1.0
        if curlen + wl > max_em and cur:
            lines.append(cur); cur, curlen = ch, wl
        else:
            cur += ch; curlen += wl
    if cur:
        lines.append(cur)
    return lines

def fit(text, w, h, size, min_size=4.6, pad=0.90):
    """把 text 塞进 w×h 区域内：先缩字号，再折行。返回 (text, size)。"""
    s = size
    while s >= min_size:
        em = s / PT
        max_em = max(1.0, (w * pad) / em)
        lines = _wrap(text, max_em)
        lh = s * 1.42 / PT
        if len(lines) * lh <= h * pad:
            return "\n".join(lines), s
        s -= 0.25
    em = min_size / PT
    return "\n".join(_wrap(text, max(1.0, (w * pad) / em))), min_size

def box(ax, x, y, w, h, text="", color=GRAY, size=7.4, bold=False, fill=WHITE,
        sub=None, lw=0.9, dashed=False, rad=1.2, z=3, align="center"):
    BOXES.append((x, y, w, h, text or "", sub or ""))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rad}",
                                linewidth=lw, edgecolor=color, facecolor=fill, zorder=z,
                                linestyle=(0, (3, 2)) if dashed else "solid"))
    if text and sub:
        t, s1 = fit(text, w, h * 0.46, size, 4.6)
        st, s2 = fit(sub, w, h * 0.40, size - 1.4, 4.2)
        ax.text(x + w/2, y + h*0.68, t, ha="center", va="center", fontsize=s1,
                color=INK, fontweight="bold" if bold else "normal", zorder=z+1, linespacing=1.3)
        ax.text(x + w/2, y + h*0.26, st, ha="center", va="center", fontsize=s2,
                color=GRAY, zorder=z+1, linespacing=1.35)
    elif text:
        t, s1 = fit(text, w, h, size, 4.6)
        ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=s1,
                color=INK, fontweight="bold" if bold else "normal", zorder=z+1, linespacing=1.35)

def txt(ax, x, y, s, size=5.6, color=GRAY, ha="left", va="center", bold=False, w=None):
    if w:
        s, size = fit(s, w, size * 3.2, size, 4.2)
        ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color,
                fontweight="bold" if bold else "normal", zorder=6, linespacing=1.4)
    else:
        ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color,
                fontweight="bold" if bold else "normal", zorder=6, linespacing=1.4)

def arrow(ax, p1, p2, color=LINE, lw=0.9, style="-|>", ms=7, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms, lw=lw,
                                 color=color, zorder=2, shrinkA=1.2, shrinkB=1.2,
                                 connectionstyle=f"arc3,rad={rad}"))

def hchain(ax, x, y, w, items, color=GRAY, bh=9.0, gap=2.4, size=6.8, sub_size=5.4):
    n = len(items); bw = (w - gap * (n - 1)) / n
    for i, it in enumerate(items):
        t, sub = it if isinstance(it, tuple) else (it, None)
        bx = x + i * (bw + gap)
        box(ax, bx, y, bw, bh, t, color, size, True, sub=sub)
        if i < n - 1:
            arrow(ax, (bx + bw + 0.4, y + bh/2), (bx + bw + gap - 0.4, y + bh/2), color)
    return bw

def vchain(ax, x, ytop, w, items, color=GRAY, bh=8.4, gap=3.2, size=6.8):
    yy = ytop
    for i, it in enumerate(items):
        t, sub = it if isinstance(it, tuple) else (it, None)
        box(ax, x, yy - bh, w, bh, t, color, size, True, sub=sub)
        if i < len(items) - 1:
            arrow(ax, (x + w/2, yy - bh - 0.4), (x + w/2, yy - bh - gap + 0.4), color)
        yy -= (bh + gap)

def quad(ax, x, ytop, w, h, items, size=7.0, pad=2.6):
    cw = (w - pad) / 2; ch = (h - pad) / 2
    for i, (t, sub, c) in enumerate(items[:4]):
        bx = x + (i % 2) * (cw + pad)
        by = ytop - (i // 2) * (ch + pad)
        box(ax, bx, by - ch, cw, ch, t, c, size, True, sub=sub)

def table(ax, x, ytop, w, header, rows, color=GRAY, rh=5.6, fs=5.6):
    n = len(header); cw = w / n
    for j, hd in enumerate(header):
        box(ax, x + j*cw, ytop - rh, cw, rh, hd, color, fs, True, fill=PALE)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            box(ax, x + j*cw, ytop - (i+2)*rh, cw, rh, v, LINE, fs, j == 0)

def head(ax, kicker, title, accent=INK, note=None):
    ax.add_patch(Rectangle((0, UY - 1.2), UX, 1.2, facecolor=accent, edgecolor="none", zorder=5))
    txt(ax, 5.0, 66.4, kicker, 6.0, accent, bold=True)
    ax.text(5.0, 60.0, title, ha="left", va="center", fontsize=15.5, color=INK,
            fontweight="bold", zorder=6)
    ax.plot([5.0, UX - 5.0], [55.6, 55.6], color=LINE, lw=0.9, zorder=1)
    if note:
        txt(ax, 5.0, 52.4, note, 6.0, GRAY)

def calls(ax, items, y=15.0, color=GRAY):
    """底部 3 条带编号的注释。"""
    n = len(items); w = (UX - 10.0 - (n-1)*3.0) / n
    for i, (mark, body) in enumerate(items):
        x = 5.0 + i * (w + 3.0)
        ax.text(x, y, mark, ha="left", va="center", fontsize=7.2, color=color, fontweight="bold", zorder=6)
        s, sz = fit(body, w - 4.0, 10.0, 5.6, 4.4)
        ax.text(x + 4.2, y, s, ha="left", va="center", fontsize=sz, color=GRAY, zorder=6, linespacing=1.4)

def foot(ax, left, right, color=GRAY):
    ax.plot([5.0, UX - 5.0], [6.2, 6.2], color=LINE, lw=0.8, zorder=1)
    s, sz = fit(left, 56.0, 4.0, 5.2, 4.2)
    ax.text(5.0, 3.2, s, ha="left", va="center", fontsize=sz, color=color, zorder=6)
    s2, sz2 = fit(right, 56.0, 4.0, 5.2, 4.2)
    ax.text(UX - 5.0, 3.2, s2, ha="right", va="center", fontsize=sz2, color=FAINT, zorder=6)

def pageno(ax, n):
    ax.text(UX - 3.0, UY - 3.0, str(n), ha="right", va="center", fontsize=5.6, color="#C4CAD2", zorder=7)

def save(fig, path):
    fig.savefig(path, dpi=160, facecolor=WHITE)
    plt.close(fig)
    return path
