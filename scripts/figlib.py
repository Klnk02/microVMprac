# -*- coding: utf-8 -*-
"""图示渲染库：matplotlib 画图，输出 PNG 供 PPT 使用。"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.font_manager as fm

INK    = "#15181C"
GRAY   = "#5F6B7A"
FAINT  = "#9AA3AE"
LINE   = "#DFE4EA"
PALE   = "#F6F8FA"
WHITE  = "#FFFFFF"
BLUE   = "#2F6FEB"
PURPLE = "#7C3AED"
GREEN  = "#0E9F6E"
ORANGE = "#D97706"
TEAL   = "#0E7490"
VIOLET = "#9333EA"

def _setup_font():
    for name in ["Microsoft YaHei", "Microsoft YaHei UI", "SimHei", "Noto Sans CJK SC"]:
        if any(f.name == name for f in fm.fontManager.ttflist):
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["font.family"] = "sans-serif"
            break
    plt.rcParams["axes.unicode_minus"] = False

_setup_font()

W, H = 12.4, 5.2   # inches

def canvas():
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 124); ax.set_ylim(0, 52)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 124, 52, facecolor=WHITE, edgecolor="none", zorder=0))
    return fig, ax

def _wrap(text, n):
    if len(text) <= n:
        return text
    out, cur = [], ""
    for ch in text:
        cur += ch
        if len(cur) >= n:
            out.append(cur); cur = ""
    if cur:
        out.append(cur)
    return "\n".join(out)

def box(ax, x, y, w, h, text="", color=GRAY, size=8.2, bold=False, fill=WHITE,
        sub=None, lw=0.9, dashed=False, sub_size=6.6, zorder=3):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                       linewidth=lw, edgecolor=color, facecolor=fill, zorder=zorder,
                       linestyle=(0, (3, 2)) if dashed else "solid")
    ax.add_patch(p)
    if text:
        if sub:
            ax.text(x + w/2, y + h*0.62, text, ha="center", va="center",
                    fontsize=size, color=INK, fontweight="bold" if bold else "normal", zorder=zorder+1)
            ax.text(x + w/2, y + h*0.30, sub, ha="center", va="center",
                    fontsize=sub_size, color=GRAY, zorder=zorder+1, linespacing=1.35)
        else:
            ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                    fontsize=size, color=INK, fontweight="bold" if bold else "normal",
                    zorder=zorder+1, linespacing=1.35)
    return p

def label(ax, x, y, text, size=6.6, color=GRAY, ha="left", va="center", bold=False, ls=1.35):
    ax.text(x, y, text, ha=ha, va=va, fontsize=size, color=color,
            fontweight="bold" if bold else "normal", zorder=6, linespacing=ls)

def arrow(ax, p1, p2, color=LINE, lw=0.9, style="-|>", ms=8, rad=0.0, zorder=2):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms, lw=lw,
                        color=color, zorder=zorder, shrinkA=1, shrinkB=1,
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)

def hchain(ax, x, y, w, items, color=GRAY, bh=8.0, gap=2.2, size=7.6, sub_size=6.0):
    n = len(items); bw = (w - gap * (n - 1)) / n
    for i, it in enumerate(items):
        t, sub = it if isinstance(it, tuple) else (it, None)
        bx = x + i * (bw + gap)
        box(ax, bx, y, bw, bh, t, color, size, True, sub=sub, sub_size=sub_size)
        if i < n - 1:
            arrow(ax, (bx + bw + 0.3, y + bh/2), (bx + bw + gap - 0.3, y + bh/2), color)
    return bw

def vchain(ax, x, y, w, items, color=GRAY, bh=7.6, gap=3.0, size=7.6, sub_size=6.0):
    yy = y
    for i, it in enumerate(items):
        t, sub = it if isinstance(it, tuple) else (it, None)
        box(ax, x, yy, w, bh, t, color, size, True, sub=sub, sub_size=sub_size)
        if i < len(items) - 1:
            arrow(ax, (x + w/2, yy + bh + 0.3), (x + w/2, yy + bh + gap - 0.3), color)
        yy -= (bh + gap)
    return yy

def quad(ax, x, y, w, h, items, size=7.8, sub_size=6.2, pad=2.4):
    cw = (w - pad) / 2; ch = (h - pad) / 2
    for i, (t, sub, c) in enumerate(items[:4]):
        bx = x + (i % 2) * (cw + pad)
        by = y - (i // 2) * (ch + pad)
        box(ax, bx, by - ch, cw, ch, t, c, size, True, sub=sub, sub_size=sub_size)

def table(ax, x, y, w, header, rows, color=GRAY, rh=5.0, fs=6.4, hfs=6.6):
    n = len(header); cw = w / n
    for j, hd in enumerate(header):
        box(ax, x + j*cw, y - rh, cw, rh, hd, color, hfs, True, fill=PALE)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            box(ax, x + j*cw, y - (i+2)*rh, cw, rh, v, LINE, fs, j == 0)

def chip(ax, x, y, text, color=GRAY, size=6.6):
    box(ax, x, y, 16, 4.2, text, color, size, True)

def titles(ax, kicker, title, accent=INK):
    label(ax, 4, 48.2, kicker, 7.2, accent, bold=True)
    ax.text(4, 43.4, title, ha="left", va="center", fontsize=14.5, color=INK, fontweight="bold", zorder=6)

def footer(ax, left, right):
    ax.plot([4, 120], [6.4, 6.4], color=LINE, lw=0.8, zorder=1)
    label(ax, 4, 3.6, left, 6.4, GRAY)
    label(ax, 68, 3.6, right, 6.4, FAINT)

def save(fig, path):
    fig.savefig(path, dpi=200, facecolor=WHITE)
    plt.close(fig)
    return path
