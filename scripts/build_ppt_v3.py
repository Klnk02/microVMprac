# -*- coding: utf-8 -*-
"""AgentENV 全课讲解型 PPT：每课两页（机制页 + 边界页），左图右文，展开讲。
用法：python build_ppt_v3.py <输出路径>
"""
import sys, math
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

FONT = "Microsoft YaHei"
INK   = RGBColor(0x19, 0x1E, 0x23)
DIM   = RGBColor(0x55, 0x63, 0x72)
FAINT = RGBColor(0x88, 0x96, 0xA5)
LINE  = RGBColor(0xD5, 0xDD, 0xE5)
PAPER = RGBColor(0xFC, 0xFD, 0xFE)
SOFT  = RGBColor(0xF1, 0xF4, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

BLUE   = RGBColor(0x1F, 0x6F, 0xEB)
PURPLE = RGBColor(0x6F, 0x42, 0xCC)
GREEN  = RGBColor(0x1B, 0x7F, 0x3B)
ORANGE = RGBColor(0xB5, 0x53, 0x16)
VIOLET = RGBColor(0x86, 0x4C, 0xCE)
AMBER  = RGBColor(0xA5, 0x74, 0x0C)
TEAL   = RGBColor(0x0D, 0x63, 0x80)

def tint(c, k=0.90):
    return RGBColor(int(c[0] + (255 - c[0]) * k),
                    int(c[1] + (255 - c[1]) * k),
                    int(c[2] + (255 - c[2]) * k))

def set_font(run, size, bold=False, color=INK, name=FONT):
    run.font.size = Pt(size); run.font.bold = bold
    run.font.color.rgb = color; run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', name)

def tb(s, x, y, w, h, text, size=12, bold=False, color=INK,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, ls=1.35):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, seg in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = ls
        r = p.add_run(); r.text = seg
        set_font(r, size, bold, color)
    return box

def rr(s, x, y, w, h, fill=None, line=None, r=0.06, lw=1.1, dash=False):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line if line else (fill if fill else LINE)
    sh.line.width = Pt(lw)
    if line is None and fill is not None: sh.line.fill.background()
    if dash: sh.line.dash_style = 4
    sh.shadow.inherit = False
    try: sh.adjustments[0] = r
    except Exception: pass
    return sh

def box(s, x, y, w, h, text, c, size=10, bold=False, fill=WHITE, sub=None, dash=False):
    rr(s, x, y, w, h, fill=fill, line=c, dash=dash)
    if sub:
        tb(s, x + 0.08, y + h/2 - 0.31, w - 0.16, 0.26, text, size, bold, INK, PP_ALIGN.CENTER)
        tb(s, x + 0.08, y + h/2 - 0.02, w - 0.16, 0.30, sub, size - 2, False, DIM, PP_ALIGN.CENTER, ls=1.1)
    else:
        tb(s, x + 0.08, y + 0.03, w - 0.16, h - 0.06, text, size, bold, INK,
           PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, 1.15)

def arr_r(s, x, y, w=0.26, h=0.2, c=None):
    sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.rotation = 90; sh.fill.solid(); sh.fill.fore_color.rgb = c or LINE
    sh.line.fill.background(); sh.shadow.inherit = False

def arr_d(s, x, y, w=0.2, h=0.22, c=None):
    sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.rotation = 180; sh.fill.solid(); sh.fill.fore_color.rgb = c or LINE
    sh.line.fill.background(); sh.shadow.inherit = False

# ---------------------------------------------------------------- 页面骨架
def new_page(prs, c):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = PAPER
    bg.line.fill.background(); bg.shadow.inherit = False
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.15), Inches(7.5))
    bar.fill.solid(); bar.fill.fore_color.rgb = c
    bar.line.fill.background(); bar.shadow.inherit = False
    return s

def head(s, kicker, title, c, sub=None):
    tb(s, 0.58, 0.40, 8.2, 0.26, kicker, 10, True, c)
    tb(s, 0.56, 0.70, 12.0, 0.62, title, 22, True, INK, ls=1.05)
    y = 1.30
    if sub:
        tb(s, 0.58, 1.30, 11.95, 0.30, sub, 11, False, DIM)
        y = 1.66
    rr(s, 0.56, y, 12.18, 0.010, fill=LINE, r=0)
    return y + 0.12

def pfoot(s, note, ask, c, pageno):
    y = 6.46
    rr(s, 0.56, y, 6.30, 0.62, fill=tint(c, 0.94), line=tint(c, 0.74), r=0.12)
    tb(s, 0.72, y + 0.07, 5.98, 0.48, note, 10, False, INK, ls=1.15)
    rr(s, 6.92, y, 5.82, 0.62, fill=RGBColor(0xF7, 0xF9, 0xFC), line=LINE, r=0.12)
    tb(s, 7.08, y + 0.07, 5.50, 0.48, ask, 10, False, DIM, ls=1.15)
    tb(s, 12.42, 7.16, 0.50, 0.22, str(pageno), 8.5, False, FAINT, PP_ALIGN.RIGHT)

def divider(prs, num, t, sub, c, pageno):
    s = new_page(prs, c)
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = c
    bg.line.fill.background(); bg.shadow.inherit = False
    tb(s, 1.00, 2.20, 2.4, 1.3, num, 72, True, WHITE)
    tb(s, 3.35, 2.52, 8.8, 0.8, t, 30, True, WHITE)
    tb(s, 3.42, 3.40, 8.4, 0.9, sub, 13, False, RGBColor(0xEC, 0xF3, 0xF9), ls=1.35)
    tb(s, 12.42, 7.16, 0.50, 0.22, str(pageno), 8.5, False, RGBColor(0xEC, 0xF3, 0xF9), PP_ALIGN.RIGHT)

# ---------------------------------------------------------------- 通用图元
def diagram_panel(s, x, y, w, h, caption, c):
    rr(s, x, y, w, h, fill=WHITE, line=LINE, r=0.03)
    if caption:
        tb(s, x + 0.16, y + 0.10, w - 0.32, 0.24, caption, 9.5, True, FAINT)

def chain_v(s, x, y, w, items, c, gap=0.30, bh=0.60, size=10):
    yy = y
    for i, it in enumerate(items):
        label, sub = it[0], it[1]
        col = it[2] if len(it) > 2 and it[2] else c
        box(s, x, yy, w, bh, label, col, size, True, sub=sub)
        if i < len(items) - 1:
            arr_d(s, x + w/2 - 0.10, yy + bh + 0.03, 0.2, gap - 0.06, LINE)
        yy += bh + gap
    return yy

def chain_h(s, x, y, w, items, c, bh=0.62, size=9.5, gap=0.18):
    n = len(items)
    bw = (w - gap * (n - 1)) / n
    xx = x
    for i, it in enumerate(items):
        label, sub = it[0], it[1]
        col = it[2] if len(it) > 2 and it[2] else c
        box(s, xx, y, bw, bh, label, col, size, True, sub=sub)
        if i < n - 1:
            arr_r(s, xx + bw + 0.02, y + bh/2 - 0.10, gap - 0.04, 0.2, LINE)
        xx += bw + gap
    return bw

def compare2(s, x, y, w, h, left, right, c):
    """left/right = (title, [lines], color)"""
    half = (w - 0.22) / 2
    for i, (t, lines, col) in enumerate((left, right)):
        xx = x + i * (half + 0.22)
        rr(s, xx, y, half, h, fill=tint(col, 0.95), line=tint(col, 0.72), r=0.05)
        tb(s, xx + 0.16, y + 0.10, half - 0.32, 0.26, t, 10.5, True, col)
        tb(s, xx + 0.16, y + 0.40, half - 0.32, h - 0.50, "\n".join(lines), 9.5, False, INK, ls=1.35)

def quad(s, x, y, w, h, items, c):
    """items = [(title, body, color)] ×4"""
    cw = (w - 0.18) / 2; ch = (h - 0.18) / 2
    for i, (t, d, col) in enumerate(items[:4]):
        xx = x + (i % 2) * (cw + 0.18)
        yy = y + (i // 2) * (ch + 0.18)
        rr(s, xx, yy, cw, ch, fill=WHITE, line=col, r=0.05)
        tb(s, xx + 0.14, yy + 0.09, cw - 0.28, 0.26, t, 10, True, col)
        tb(s, xx + 0.14, yy + 0.38, cw - 0.28, ch - 0.46, d, 9, False, INK, ls=1.3)

def table(s, x, y, w, header, rows, c, colw=None, rh=0.40, size=9, hsize=9.5):
    n = len(header)
    if colw is None:
        colw = [w / n] * n
    xx = x
    for j, hd in enumerate(header):
        rr(s, xx, y, colw[j], rh, fill=c, line=c, r=0.03)
        tb(s, xx + 0.08, y + 0.04, colw[j] - 0.16, rh - 0.08, hd, hsize, True, WHITE, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
        xx += colw[j]
    yy = y + rh
    for i, row in enumerate(rows):
        xx = x
        for j, val in enumerate(row):
            fill = WHITE if i % 2 == 0 else SOFT
            rr(s, xx, yy, colw[j], rh, fill=fill, line=LINE, r=0.02)
            tb(s, xx + 0.08, yy + 0.03, colw[j] - 0.16, rh - 0.06, val, size,
               j == 0, INK if j == 0 else DIM, PP_ALIGN.LEFT, MSO_ANCHOR.MIDDLE, 1.15)
            xx += colw[j]
        yy += rh
    return yy

def _lines(text, w, size):
    cpl = max(8, int(w * 72 / (size * 0.95)))
    n = 0
    for seg in text.split("\n"):
        n += max(1, math.ceil(len(seg) / cpl))
    return n

def paragraphs(s, x, y, w, items, size=11, ls=1.5, gap=0.16, color=DIM):
    """items: (头, 正文) 或 整段字符串。按估算行高逐段排版，避免重叠。"""
    yy = y
    sz = size - 0.5
    for it in items:
        if isinstance(it, tuple):
            head_t, body = it
            tb(s, x, yy, w, 0.26, head_t, sz, True, INK)
            h = _lines(body, w, sz) * sz * ls / 72
            tb(s, x, yy + 0.27, w, h + 0.06, body, sz, False, color, ls=ls)
            yy += 0.27 + h + gap
        else:
            h = _lines(it, w, sz) * sz * ls / 72
            tb(s, x, yy, w, h + 0.06, it, sz, False, color, ls=ls)
            yy += h + gap
    return yy

# ---------------------------------------------------------------- 主构建
def build(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    P = [0]
    def np_():
        P[0] += 1; return P[0]

    # ============ 封面 ============
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = RGBColor(0x0D, 0x12, 0x19); bg.line.fill.background()
    bg.shadow.inherit = False
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(1.95), Inches(0.10), Inches(2.05))
    bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background(); bar.shadow.inherit = False
    tb(s, 1.28, 1.88, 10.6, 0.86, "AgentENV 沙箱全课讲解", 38, True, RGBColor(0xEC, 0xF1, 0xF7))
    tb(s, 1.32, 2.74, 10.6, 0.44, "20 讲逐课展开：机制 → 边界 → 面试问法", 16, False, RGBColor(0x9B, 0xAA, 0xBA))
    tb(s, 1.32, 3.70, 10.6, 1.0,
       "每课两页：第一页讲清「它怎么工作」，第二页讲清「它在哪会坏、面试怎么被追」。\n"
       "图为示意，不是真实 trace；没有实测的地方都标了「待实测」。",
       11.5, False, RGBColor(0x74, 0x85, 0x96), ls=1.55)
    tb(s, 1.32, 6.45, 11.2, 0.34,
       "基线 9f62cbe07cebfecf416dc9bdcf497e2a97687644   ·   2026-11-13", 10, False, RGBColor(0x5D, 0x6D, 0x7E))
    np_()

    # ============ 用法 ============
    s = new_page(prs, TEAL); head(s, "怎么用", "两页一课，按「图 → 话 → 问」看", TEAL)
    items = [
        ("第一页 · 机制页", "左边一张图，右边一段解释。先看图能不能自己讲出来，再看文字补细节。", BLUE),
        ("第二页 · 边界页", "这一课在哪会出错、哪些「完成」不是一回事、面试会怎么追问。", ORANGE),
        ("一层层追问自己", "谁在执行？数据在哪？这一步的完成意味着什么？下一层知道了吗？", TEAL),
    ]
    y = 2.00
    for t, d, c in items:
        rr(s, 0.58, y, 12.15, 0.98, fill=WHITE, line=LINE, r=0.05)
        rr(s, 0.58, y, 0.05, 0.98, fill=c, r=0)
        tb(s, 0.82, y + 0.13, 3.2, 0.28, t, 11, True, c)
        tb(s, 4.15, y + 0.13, 8.3, 0.66, d, 10.5, False, INK, ls=1.3)
        y += 1.10
    tb(s, 0.58, 5.80, 12.15, 0.55,
       "全课只有一个主线：一次请求怎么落到硬件，再带着结果回到调用者。所有课都在补这条线的某一段。",
       11.5, True, TEAL)
    pfoot(s, "读完不等于会。判断标准是：换一个条件，你还能预测结果。",
          "你打算用哪种方式复习：扫图、口答、还是白纸重画？", TEAL, np_())

    # ============ 全景 1 ============
    s = new_page(prs, BLUE); head(s, "全景 · 第 0 课", "三个执行环境，一台机器", BLUE,
                                 "所有课程内容都挂在这三层上；分不清层，后面每一个问题都会答错位置。")
    bands = [("宿主用户态", ["AgentENV server ｜ 生命周期与控制", "Firecracker ｜ VMM：vCPU 线程 + 设备模型", "ublk-daemon ｜ 块设备服务（集中式）"], BLUE, 2.05),
             ("宿主内核", ["KVM ｜ 运行 vCPU、维护 EPT", "ublk 驱动 ｜ /dev/ublkbN 请求队列", "cgroup / seccomp ｜ 约束 VMM 的用量与 syscall"], PURPLE, 3.28),
             ("Guest 虚拟机", ["Guest 内核 ｜ 自己的页表与进程表", "envd ｜ 执行命令、回传 stdout 与退出码", "你的程序 ｜ PID 由 Guest 内核分配"], GREEN, 4.51)]
    for name, lines, c, y in bands:
        rr(s, 0.58, y, 12.15, 1.02, fill=WHITE, line=LINE, r=0.04)
        rr(s, 0.58, y, 0.05, 1.02, fill=c, r=0)
        tb(s, 0.78, y + 0.10, 1.5, 0.26, name, 9.5, True, c)
        tb(s, 2.20, y + 0.08, 10.3, 0.88, "\n".join(lines), 9.5, False, INK, ls=1.35)
    for y in (3.13, 4.36):
        tb(s, 0.58, y, 12.15, 0.18, "▼", 8, False, FAINT, PP_ALIGN.CENTER)
    tb(s, 0.58, 5.68, 12.15, 0.62,
       "关键一句：Guest 里的程序不是 Firecracker 的子进程，它由 Guest 内核调度，宿主 ps 看不到。\n"
       "所以「宿主上有个 python 进程」和「Guest 里有个 python 进程」是两句完全不同的话。",
       11, False, INK, ls=1.4)
    pfoot(s, "把 server 里的 Rust 对象当成进程；把宿主 PID 当成 Guest PID。",
          "宿主 ps -eLf 能看到哪些？看不到哪些？", BLUE, np_())

    # ============ 全景 2 ============
    s = new_page(prs, BLUE); head(s, "全景 · 第 0 课", "四把尺子与三条边界", BLUE,
                                 "地址属于谁、动作发生在哪一层——这两件事答错，后面全错。")
    table(s, 0.58, 1.95, 6.10, ["名称", "谁在看", "含义"], [
        ["GVA", "Guest 程序", "Guest 虚拟地址"],
        ["GPA", "Guest 内核", "Guest 眼里的物理地址"],
        ["HVA", "某个宿主进程", "必须说明属于谁"],
        ["HPA", "物理机器", "真正的内存条位置"],
    ], BLUE, colw=[1.05, 1.55, 3.50], rh=0.44)
    tb(s, 0.58, 4.22, 6.10, 0.9,
       "Guest 访存：GVA → GPA → HPA（Guest 页表 + EPT）\n"
       "Firecracker 访存：HVA → HPA（宿主页表）\n两条路径可以落在同一张物理页上。",
       9.5, False, INK, ls=1.4)
    table(s, 6.95, 1.95, 5.80, ["边界", "是否切宿主线程"], [
        ["KVM_RUN 系统调用", "否（只换特权级）"],
        ["VM-Entry / VM-Exit", "否（同一线程内切换）"],
        ["宿主线程切换", "是（真没拿到 CPU）"],
    ], PURPLE, colw=[3.10, 2.70], rh=0.46)
    tb(s, 6.95, 3.72, 5.80, 1.2,
       "最实用的一条推论：VM-Exit 回到宿主内核，不等于 KVM_RUN 已经返回用户态。\n"
       "KVM 能处理的退出会处理完直接重入 Guest，整个 ioctl 从头到尾没返回。",
       9.5, False, INK, ls=1.4)
    tb(s, 0.58, 5.28, 12.15, 0.95,
       "把这两张表合起来看：地址决定「数据在哪」，边界决定「谁在动它」。\n"
       "后面每一课，本质都是在给这两张表补一行。",
       11, True, BLUE, ls=1.4)
    pfoot(s, "把「VM-Exit」当成「KVM_RUN 返回」；把「guest 物理地址」当成「宿主物理地址」。",
          "GPA 与 HPA 之间还差了哪一层翻译？由谁维护？", BLUE, np_())

    # ============ 章节 01 ============
    divider(prs, "01", "位置与地址", "第 1—3 课：谁在跑，指针属于谁，两条访问路径怎么汇合", BLUE, np_())

    # --- 第 1 课 机制页 ---
    s = new_page(prs, BLUE); head(s, "第 1 课 · 机制", "Firecracker 是宿主进程，Guest 是另一台机器", BLUE,
                                 "先解决最基础的位置问题：谁是谁的子进程，谁由谁的内核管理。")
    diagram_panel(s, 0.58, 1.95, 5.55, 4.20, "位置关系（示意）", BLUE)
    chain_v(s, 1.05, 2.35, 2.05, [
        ("AgentENV server", "宿主用户态进程", BLUE),
        ("Firecracker", "宿主用户态进程", PURPLE),
        ("KVM", "宿主内核功能", PURPLE),
        ("Guest 内核 + 程序", "由 Guest 内核管理", GREEN),
    ], BLUE, gap=0.34, bh=0.66)
    tb(s, 3.35, 2.45, 2.55, 3.3,
       "server 通过 tokio 的\nCommand 启动 firecracker，\n保存的是子进程句柄。\n\n"
       "Firecracker 借 KVM\n让 CPU 进非根模式，\n执行 Guest 的代码。\n\n"
       "Guest 不是子进程：\n宿主 ps 看不到它里面的\npython。",
       9.5, False, DIM, ls=1.4)
    paragraphs(s, 6.45, 1.95, 6.25, [
        ("这是什么关系", "server 与 Firecracker 都是宿主内核管理的普通进程，是父子关系；Guest 是 CPU 在非根模式下执行的另一套内核，不是进程树里的节点。"),
        ("为什么重要", "这条区别决定了你读 ps、读日志、读 PID 时的解释方式：宿主的 PID 与 Guest 的 PID 是两套编号空间，互不通用。"),
        ("三个容易混的名字", "FirecrackerInstance 是 server 里的结构体（存 socket 路径与子进程句柄），不是进程；envd 是 Guest 内服务；OverlayBD 是被 daemon 链接的库。"),
    ], 10.5)
    pfoot(s, "把宿主 PID 当成 Guest PID；把 Rust 结构体当进程。",
          "宿主能看到几个进程？Guest 里的 python 由谁分配 PID？", BLUE, np_())

    # --- 第 1 课 边界页 ---
    s = new_page(prs, BLUE); head(s, "第 1 课 · 边界", "一个进程，内部有多个线程", BLUE,
                                 "进程是「一个地址空间」，线程是「执行流」。vCPU 就是一个线程。")
    diagram_panel(s, 0.58, 1.95, 6.05, 3.95, "Firecracker 进程内部的线程（示意）", BLUE)
    rr(s, 0.85, 2.30, 5.50, 3.35, fill=tint(BLUE, 0.96), line=tint(BLUE, 0.75), r=0.04)
    tb(s, 1.02, 2.42, 5.1, 0.26, "宿主进程 firecracker（PID 由宿主内核分配）", 9, True, DIM)
    for i, (t, d) in enumerate([("vmm 主线程", "协调状态、处理设备事件"),
                                ("api 线程", "Unix socket 上收控制请求"),
                                ("fc_vcpu 0", "ioctl(KVM_RUN) 跑 Guest"),
                                ("fc_vcpu 1", "ioctl(KVM_RUN) 跑 Guest")]):
        box(s, 1.05, 2.72 + i * 0.66, 5.05, 0.54, t, BLUE, 9.5, True, sub=d)
    tb(s, 6.90, 1.98, 5.80, 3.85,
       "为什么必须多线程\n"
       "单线程 VMM 会卡死：vCPU 线程卡在 ioctl(KVM_RUN) 里跑 Guest 时，没人接「请暂停」的请求。\n\n"
       "于是拆成三类：vcpu 线程负责「Guest 在跑」的时间，api 线程负责「随时能接请求」，vmm 线程负责把请求翻译成协调动作。\n\n"
       "线程名是代码写死的\n"
       "源码里 .name(\"fc_vcpu {index}\")，所以宿主 ps -eLf 才看得到这个名字——不写就没有。",
       10, False, INK, ls=1.5)
    tb(s, 0.58, 5.98, 12.15, 0.32,
       "观测方法：ps -eLf -p <firecracker_pid> ｜ 或 ls /proc/<pid>/task ｜ 线程数应与 vCPU 数对应（另有 vmm/api 线程）。",
       9.5, True, BLUE)
    pfoot(s, "以为 vCPU 线程在 KVM_RUN 里就是「睡着了」：物理 CPU 可能正在它上面跑 Guest。",
          "配 4 个 vCPU，宿主会多出几个线程？为什么？", BLUE, np_())

    # --- 第 2 课 机制页 ---
    s = new_page(prs, BLUE); head(s, "第 2 课 · 机制", "同一个数字地址，在两个进程里指向不同内存", BLUE,
                                 "地址不是一个全局编号，它只在某个地址空间里有意义。")
    diagram_panel(s, 0.58, 1.95, 5.85, 3.55, "两个进程地址空间（课堂假设）", BLUE)
    box(s, 0.90, 2.40, 2.30, 0.58, "server 的 0x400000", ORANGE, 9)
    box(s, 0.90, 3.30, 2.30, 0.58, "Firecracker 的 0x400000", PURPLE, 9)
    box(s, 3.90, 2.40, 2.25, 0.58, "物理页 P_A：SERVER", ORANGE, 9)
    box(s, 3.90, 3.30, 2.25, 0.58, "物理页 P_B：GUEST-DATA", PURPLE, 9)
    arr_r(s, 3.28, 2.58, 0.55, 0.20, ORANGE)
    arr_r(s, 3.28, 3.48, 0.55, 0.20, PURPLE)
    tb(s, 0.90, 4.08, 5.2, 0.5, "两个进程各有自己的一张页表：同一数字 → 不同物理页", 9.5, False, DIM, ls=1.3)
    tb(s, 0.90, 4.72, 5.30, 0.8,
       "推论：server 手里的 0x400000 是它自己的地址；用它去读 Firecracker 的数据，读到的只会是 server 自己的页。",
       9.5, True, BLUE, ls=1.35)
    tb(s, 6.75, 1.95, 5.95, 3.5,
       "普通 pwrite 的问题\n"
       "pwrite(fd, buf, len, off) 里 buf 永远按调用者自己的地址空间解释，接口里根本没有「去哪个进程取」这个参数。\n\n"
       "所以 server 想保存 Guest 内存，不能直接把 Firecracker 的地址交给 pwrite。\n\n"
       "process_vm_readv 补上了这一点\n"
       "process_vm_readv(pid, local_iov, remote_iov, ...)：pid 决定用谁的地址空间，remote 说从哪取，local 说放到我自己哪。",
       10, False, INK, ls=1.55)
    pfoot(s, "以为内核会自动按被读进程解释地址；以为「同一个数字」就是「同一块内存」。",
          "server 想读 Guest 内存，buf 该填谁的地址？", BLUE, np_())

    # --- 第 2 课 边界页 ---
    s = new_page(prs, BLUE); head(s, "第 2 课 · 边界", "四个参数、三个动作、两个数组", BLUE,
                                 "PVM 这题面试常问，问到第二层就会暴露「有没有真读过」。")
    rr(s, 0.58, 1.95, 6.10, 1.95, fill=WHITE, line=BLUE, r=0.04)
    tb(s, 0.76, 2.06, 5.7, 1.75,
       "process_vm_readv(\n"
       "    pid,         // Firecracker 的宿主 PID\n"
       "    local_iov,   // server 自己的缓冲区\n"
       "    remote_iov,  // 地址属于 Firecracker（HVA）\n"
       "    flags)       // 必须为 0",
       9.5, False, INK, ls=1.5)
    rr(s, 6.92, 1.95, 5.82, 1.95, fill=tint(BLUE, 0.95), line=tint(BLUE, 0.72), r=0.04)
    tb(s, 7.10, 2.06, 5.5, 1.75,
       "两个 iovec 数组本身都在调用者内存里\n"
       "只有 remote_iov 元素里的地址指向目标进程；\n"
       "liovcnt / riovcnt 是元素个数，不是字节数。",
       9.5, False, INK, ls=1.5)
    chain_h(s, 0.58, 4.10, 12.15, [("① 描述", "构造 iovec（不复制）"), ("② 读取", "内核复制一次"),
                                   ("③ 写文件", "pwrite / writer")], BLUE, bh=0.66)
    tb(s, 0.58, 5.00, 12.15, 1.25,
       "读循环里的三件事：短读要「源和目的同时前进」（不是从头重读）；EINTR 要重试；零进展或长度异常必须报错。\n"
       "还有一个常被问的点：read_at 虽然标了 async，内部仍是同步的 process_vm_readv，不会自动让出 worker。\n"
       "边界：整段读完只说明「目的 buffer 拿到了字节」，不代表已封层、写文件、或形成完整快照。",
       10, False, INK, ls=1.45)
    pfoot(s, "以为 async 就等于异步 IO；以为读成功＝已持久化。",
          "请求 8192 只回 4096，下一次源和目的各前进多少？", BLUE, np_())

    # --- 第 3 课 机制页 ---
    s = new_page(prs, BLUE); head(s, "第 3 课 · 机制", "两条访存路径，最后落到同一块物理内存", BLUE,
                                 "Guest 用页表 + EPT；Firecracker 用宿主页表。中间靠 memslot 接线。")
    diagram_panel(s, 0.58, 1.95, 6.05, 3.60, "一块数据，两种看法（示意）", BLUE)
    box(s, 0.85, 2.35, 1.95, 0.56, "Guest 程序 GVA", BLUE, 9)
    box(s, 0.85, 3.15, 1.95, 0.56, "Guest 内核 GPA", BLUE, 9)
    box(s, 2.95, 3.95, 2.30, 0.60, "宿主物理页 HPA", PURPLE, 9)
    box(s, 5.10, 2.35, 1.30, 0.56, "HVA", PURPLE, 9)
    arr_d(s, 1.72, 2.93, 0.2, 0.20, BLUE)
    arr_d(s, 1.72, 3.73, 0.2, 0.20, BLUE)
    arr_d(s, 3.95, 3.33, 0.2, 0.22, PURPLE)
    tb(s, 0.70, 3.00, 0.95, 0.2, "页表", 8, False, FAINT)
    tb(s, 1.80, 3.70, 0.95, 0.2, "EPT", 8, False, FAINT)
    tb(s, 5.05, 3.02, 1.45, 0.2, "宿主页表", 8, False, FAINT)
    tb(s, 0.85, 4.72, 5.5, 0.7, "HVA 不属于 Guest 的硬件访存路径；它是 Firecracker 进程自己的一条路。", 9.5, True, BLUE, ls=1.35)
    paragraphs(s, 6.85, 1.95, 5.85, [
        ("翻译链", "Guest 程序给出 GVA，Guest 页表翻成 GPA，硬件再用 EPT 翻成 HPA。Firecracker 另外用宿主页表，把自己进程里的 HVA 翻到同一个 HPA。"),
        ("为什么不是两份数据", "同一块物理页被两张表同时指向，所以没有「同步两份内存」这回事；两份是同一份。"),
        ("memslot 的角色", "KVM 用 KVM_SET_USER_MEMORY_REGION 记录「这段 GPA 对应我这段 HVA」；缺 EPT 项时，它靠这条关系算出 HVA，再取真实页。"),
    ], 10.5)
    pfoot(s, "以为 Guest 访存会经过 HVA；以为登记 memslot 时复制了一份 RAM。",
          "GPA 0x2000、HVA 起点 0x70000000，对应 HVA 是多少？", BLUE, np_())

    # --- 第 3 课 边界页 ---
    s = new_page(prs, BLUE); head(s, "第 3 课 · 边界", "登记的是范围，建立的是映射", BLUE,
                                 "这两步分开，是理解「登记不等于复制」的关键。")
    diagram_panel(s, 0.58, 1.95, 6.05, 3.95, "从 mmap 到 EPT（五步）", BLUE)
    chain_v(s, 0.90, 2.30, 3.55, [
        ("mmap 匿名内存", "得到 HVA 区间", BLUE),
        ("ioctl 登记", "GPA 范围 ↔ HVA", BLUE),
        ("KVM 记 memslot", "软件关系 GPA→HVA", PURPLE),
        ("Guest 访存缺项", "KVM 算 HVA，取真实页", PURPLE),
        ("建 EPT 项", "GPA→HPA，硬件翻译", GREEN),
    ], BLUE, gap=0.22, bh=0.50, size=9)
    tb(s, 4.70, 2.30, 1.75, 3.2,
       "注意\n\n登记时\n不填 HPA\n\n物理页\n可能此刻\n才分配\n\nEPT 项\n按需建立",
       8.5, False, DIM, ls=1.5)
    tb(s, 6.85, 1.95, 5.85, 4.1,
       "为什么不能填 HPA\n"
       "用户态进程根本看不到物理地址，它能交出的只有自己的 HVA；是宿主内核查宿主页表把 HVA 翻成 HPA，再去填 EPT。\n\n"
       "为什么不是一次性建完\n"
       "登记的只是范围。真到访问某一页发现 EPT 缺项，KVM 才现取页、现建项——所以那 128 MiB 的内容始终只有一份。\n\n"
       "算一个偏移（面试常考）\n"
       "HVA = userspace_addr + (目标 GPA − guest_phys_addr)\n"
       "例：0x70000000 + (0x2000 − 0) = 0x70002000\n\n"
       "另一条边界\n"
       "memslot 是软件登记，EPT 是硬件表；把两者当同一个东西，就解释不清「为什么缺项时才建」。",
       10, False, INK, ls=1.5)
    pfoot(s, "以为 memslot 就是 EPT；以为登记之后页面一定已驻留。",
          "memslot 存在哪？EPT 存在哪？谁读谁？", BLUE, np_())

    # ============ 章节 02 ============
    divider(prs, "02", "执行与设备", "第 4—6 课：谁在跑指令、暂停怎么确认、请求怎么传", PURPLE, np_())

    # --- 第 4 课 机制 ---
    s = new_page(prs, PURPLE); head(s, "第 4 课 · 机制", "本质是一个 ioctl(KVM_RUN) 的循环", PURPLE,
                                 "进去跑 Guest，撞到退出条件回来；处理完再进去。")
    diagram_panel(s, 0.58, 1.95, 6.05, 3.90, "vCPU 线程的一生", PURPLE)
    box(s, 0.85, 2.30, 2.40, 0.66, "ioctl(KVM_RUN)", PURPLE, 9, True, sub="阻塞在这里")
    arr_r(s, 3.30, 2.53, 0.30, 0.20, PURPLE)
    box(s, 3.70, 2.30, 2.55, 0.66, "硬件跑 Guest 指令", PURPLE, 9, True, sub="非根模式")
    arr_d(s, 4.85, 3.02, 0.2, 0.24, PURPLE)
    box(s, 3.70, 3.32, 2.55, 0.66, "VM-Exit", PURPLE, 9, True, sub="exit_reason")
    arr_d(s, 4.85, 4.04, 0.2, 0.24, LINE)
    box(s, 2.30, 4.34, 1.85, 0.62, "KVM 自己处理", GREEN, 9, True, sub="直接重入")
    box(s, 4.35, 4.34, 2.05, 0.62, "要用户态处理", ORANGE, 9, True, sub="KVM_RUN 返回")
    tb(s, 0.85, 5.10, 5.5, 0.6, "绿色：整个 ioctl 没返回过。橙色：Firecracker 被唤醒。", 9.5, False, INK, ls=1.3)
    paragraphs(s, 6.85, 1.95, 5.85, [
        ("谁在执行", "物理 CPU 执行的是 Firecracker 那个 vCPU 线程的代码；它调 ioctl 后，CPU 在同一个线程里切换到内核、再切到 Guest 执行环境。"),
        ("退出是硬件做的", "撞到 VMCS 里配置的退出条件，硬件自动保存 Guest 现场、写入退出原因，再载入宿主状态——不是软件主动去「检查」。"),
        ("用户态只在必要时被唤醒", "KVM 能处理的退出（比如补一条 EPT 映射）会处理完直接重入；只有它办不了的事，才把控制权交回 Firecracker。"),
    ], 10.5)
    pfoot(s, "把「VM-Exit 回到宿主内核」当成「KVM_RUN 返回」；以为每条指令都要退出。",
          "一次 EPT 缺页，一定会让 Firecracker 从 ioctl 返回吗？", PURPLE, np_())

    # --- 第 4 课 边界 ---
    s = new_page(prs, PURPLE); head(s, "第 4 课 · 边界", "三种边界，三种「没拿到 CPU」", PURPLE,
                                 "分不清这三层，就会把「调度延迟」误诊成「虚拟化开销」。")
    table(s, 0.58, 1.95, 12.15, ["边界", "发生了什么", "需要切宿主线程吗", "典型误判"], [
        ["KVM_RUN 系统调用", "Firecracker 用户态 → 宿主内核", "否", "以为这是「进 Guest 了」"],
        ["VM-Entry / VM-Exit", "Guest ↔ 宿主执行环境", "否", "以为每次都回到用户态"],
        ["宿主线程切换", "调度器换另一个线程跑", "是", "把调度延迟算成虚拟化开销"],
    ], PURPLE, colw=[2.55, 3.55, 2.45, 3.60], rh=0.52)
    paragraphs(s, 0.58, 4.10, 12.15, [
        ("退出原因不止「Guest 要设备」", "还有外部中断、EPT 缺页、I/O 指令等；具体频率取决于负载与配置，不是每条指令都退出。"),
        ("最容易被追的一句", "「虚拟机为什么慢」不能统一回答——要先分类：是退出次数多（设备模型重）、还是线程拿不到 CPU（超订）、还是缺页/IO 等待。"),
    ], 10.5)
    pfoot(s, "把所有「慢」都归因于虚拟化；把 VM-Exit 频率当成负载指标。",
          "VM-Exit 次数多，一定说明 VMM 有问题吗？", PURPLE, np_())

    # --- 第 5 课 机制 ---
    s = new_page(prs, PURPLE); head(s, "第 5 课 · 机制", "为什么必须把 VMM 拆成多条线程", PURPLE,
                                 "不是为了性能，是为了「Guest 卡住时，宿主还能下指令」。")
    compare2(s, 0.58, 1.95, 12.15, 2.35,
             ("单线程 VMM 的死结", ["Guest 正在跑时，vCPU 线程卡在 ioctl(KVM_RUN) 里",
                                    "同一线程无法同时处理「请暂停」的控制请求",
                                    "结果：Guest 不配合时，宿主下不了手"], ORANGE),
             ("拆成三类线程之后", ["vcpu 线程只管「Guest 在跑」的时间",
                                    "api 线程保证随时能接控制请求",
                                    "vmm 线程把请求翻译成对 vCPU/设备的协调"], GREEN), PURPLE)
    tb(s, 0.58, 4.48, 12.15, 0.28, "顺带纠正一个常见误解", 10, True, DIM)
    tb(s, 0.58, 4.78, 12.15, 1.3,
       "「线程在 KVM_RUN 里」不等于「线程睡着了」：物理 CPU 可能正在这个线程的执行上下文中运行 Guest。\n"
       "只有 Guest 执行 HLT、等事件这类情况，线程才可能真的阻塞。\n"
       "所以用 CPU 占用率看 VMM 忙不忙，要注意它包含「在跑 Guest」的那部分时间。",
       10.5, False, INK, ls=1.5)
    pfoot(s, "以为 KVM_RUN 期间线程在睡眠；以为多线程是所有 VMM 的唯一做法。",
          "如果只有一个线程，Guest 死循环时还能 pause 吗？", PURPLE, np_())

    # --- 第 5 课 边界 ---
    s = new_page(prs, PURPLE); head(s, "第 5 课 · 边界", "「没被调度」不是「已暂停」", PURPLE,
                                 "这一课唯一的难点，也是面试最爱追的地方。")
    diagram_panel(s, 0.58, 1.95, 12.15, 1.75, "两个 vCPU 的暂停时间线（课堂假设）", PURPLE)
    ev = [("t1", "API 收到\nPATCH /vm", GREEN), ("t2", "VMM 置暂停意图\n请求各 vCPU 退出", GREEN),
          ("t3", "vCPU0 返回\n确认暂停", GREEN), ("t4", "vCPU1 没被调度\n≠ 已暂停", ORANGE),
          ("t5", "vCPU1 被调度\n才处理退出", GREEN), ("t6", "两个都确认\n暂停完成", BLUE)]
    xx = 0.85
    for t, d, c in ev:
        rr(s, xx, 2.30, 1.85, 1.10, fill=WHITE, line=c, r=0.05)
        tb(s, xx + 0.10, 2.36, 1.65, 0.24, t, 9.5, True, c)
        tb(s, xx + 0.10, 2.62, 1.68, 0.72, d, 8.5, False, INK, ls=1.2)
        xx += 1.94
    paragraphs(s, 0.58, 3.95, 12.15, [
        ("为什么这是关键", "「没拿到 CPU」是调度状态，随时可能被重新调度并继续执行 Guest；「已暂停」是协议状态，要等恢复指令才继续。把两者混同，就会在 vCPU1 还在写内存时去抓快照。"),
        ("三个完成点", "请求已发出（写进 socket）→ Firecracker 已接收（API 线程解析成功）→ 全部 vCPU 确认（没有 vCPU 还能执行 Guest）。三段各自检查，不能互相代替。"),
        ("还有一层", "暂停所有 vCPU 只停了 Guest 的 CPU 写入；宿主设备侧仍可能在写同一块 RAM，完整方案还要协调设备与在途 IO。"),
    ], 10)
    pfoot(s, "把「请求发出」当成「VM 已停」；把暂停完成当成快照已保存。",
          "只暂停两个 vCPU 里的一个，能说 VM 已暂停吗？", PURPLE, np_())

    # --- 第 6 课 机制 ---
    s = new_page(prs, PURPLE); head(s, "第 6 课 · 机制", "三个部件：描述符、可用环、已用环", PURPLE,
                                 "设备不是「收到一个包」，而是「去共享队列里取一条描述」。")
    diagram_panel(s, 0.58, 1.95, 6.10, 4.05, "split virtqueue（示意）", PURPLE)
    rr(s, 0.85, 2.30, 5.55, 1.05, fill=WHITE, line=PURPLE, r=0.04)
    tb(s, 1.00, 2.38, 5.2, 0.24, "描述符表（16 字节/项）", 9, True, PURPLE)
    tb(s, 1.00, 2.64, 5.3, 0.66, "addr（GPA）· len · flags(WRITE/NEXT) · next", 8.5, False, INK, ls=1.3)
    rr(s, 0.85, 3.48, 5.55, 0.85, fill=tint(GREEN, 0.94), line=GREEN, r=0.04)
    tb(s, 1.00, 3.55, 5.2, 0.24, "可用环 avail（Guest 写）", 9, True, GREEN)
    tb(s, 1.00, 3.80, 5.3, 0.48, "发布「链头编号」，表示这批缓冲区可以给设备用", 8.5, False, INK, ls=1.25)
    rr(s, 0.85, 4.45, 5.55, 0.85, fill=tint(ORANGE, 0.94), line=ORANGE, r=0.04)
    tb(s, 1.00, 4.52, 5.2, 0.24, "已用环 used（设备写）", 9, True, ORANGE)
    tb(s, 1.00, 4.77, 5.3, 0.48, "发布完成项与实际写入长度；Guest 处理完才会再次发布", 8.5, False, INK, ls=1.25)
    tb(s, 0.85, 5.40, 5.5, 0.5, "描述符不复制字节，它只描述「缓冲区在哪、多长」。", 9, True, PURPLE, ls=1.3)
    tb(s, 6.90, 1.95, 5.80, 4.0,
       "为什么这样设计\n"
       "模拟真实设备时，每个寄存器访问都是一次 VM-Exit；VirtIO 把数据放在共享内存里批量搬，只在「有活」时敲一次门铃。\n\n"
       "通知到底做什么\n"
       "只是提醒对方「去检查队列」：不携带包内容，一次通知可以对应多项工作。所以「通知次数 ≠ 请求数」。\n\n"
       "两个经常被混的完成\n"
       "设备把结果写进 used，表示「设备侧做完了」；Guest 驱动处理完这批数据，才是「Guest 侧做完了」。中间还差一次中断注入与调度。",
       10, False, INK, ls=1.55)
    pfoot(s, "把「设备发布 used」当成「Guest 已处理」；把通知次数当请求数。",
          "Guest 未处理完就把缓冲区再次发布，会发生什么？", PURPLE, np_())

    # --- 第 6 课 边界 ---
    s = new_page(prs, PURPLE); head(s, "第 6 课 · 边界", "一次完整的收发要经过几次「发布」", PURPLE,
                                 "缓冲区生命周期，比「发一个包」复杂。")
    chain_h(s, 0.58, 2.00, 12.15, [
        ("Guest 准备缓冲", "描述符 + 缓冲区"), ("发布 avail", "写链头编号"),
        ("设备写入并发布 used", "带实际长度"), ("Guest 驱动处理", "读数据、交还缓冲"),
        ("再次发布 avail", "复用同一缓冲区"),
    ], PURPLE, bh=0.78, size=9)
    paragraphs(s, 0.58, 3.10, 12.15, [
        ("「发布两次」不是发两个包", "同一个链头发布两次代表两次使用机会；Guest 没处理完就交回，设备可能覆盖你还要读的内容。"),
        ("内存顺序与通知抑制", "真实实现需要正确的内存屏障与通知抑制策略；本课只讲交接语义，不把这些简化成「发个信号就行」。"),
        ("适用范围", "VirtIO 是 Guest 驱动与虚拟设备之间的标准接口；普通内存赋值、内核改数据结构都不走它，加载内核时也不需要 Guest 先提供队列。"),
    ], 10)
    pfoot(s, "以为所有设备访问都走 VirtIO；以为队列是「设备里的一块内存」。",
          "队列内存属于谁？设备怎么知道去哪读描述符？", PURPLE, np_())

    # ============ 章节 03 ============
    divider(prs, "03", "控制与命令", "第 7—9 课：请求从哪进、就绪怎么判、命令结果怎么回来", GREEN, np_())

    # --- 第 7 课 机制 ---
    s = new_page(prs, GREEN); head(s, "第 7 课 · 机制", "控制面与数据面是两条通道", GREEN,
                                 "搞混这两条，就会把「暂停」讲成「设备请求」。")
    rr(s, 0.58, 1.95, 6.05, 1.55, fill=tint(GREEN, 0.94), line=tint(GREEN, 0.72), r=0.04)
    tb(s, 0.76, 2.04, 5.7, 0.26, "控制面", 10, True, GREEN)
    tb(s, 0.76, 2.32, 5.7, 1.1,
       "载体：宿主 Unix socket（--api-sock）\n格式：Firecracker REST，例如 PATCH /vm\n不需要 Guest 配合，也不需要 vCPU 执行",
       9.5, False, INK, ls=1.45)
    rr(s, 6.90, 1.95, 5.85, 1.55, fill=tint(ORANGE, 0.94), line=tint(ORANGE, 0.72), r=0.04)
    tb(s, 7.08, 2.04, 5.5, 0.26, "数据面", 10, True, ORANGE)
    tb(s, 7.08, 2.32, 5.5, 1.1,
       "载体：Guest RAM 里的 virtqueue\n格式：描述符 / avail / used 环\n需要 Guest 驱动发布队列",
       9.5, False, INK, ls=1.45)
    paragraphs(s, 0.58, 3.72, 12.15, [
        ("为什么暂停不能走数据面", "暂停的用途之一正是「Guest 不配合时也能停住它」。如果停机依赖 Guest 驱动处理队列，Guest 内核或驱动卡住时宿主就永远停不下来。"),
        ("HTTP 只是格式", "它跑在 Unix socket 上，不走 TCP、不经过 Guest 网卡——「socket」不等于「网络」。"),
        ("函数名不等于位置", "FirecrackerInstance.pause() 是 server 调自己的对象，由该对象经 socket 发请求；调用者并没有进入 Guest。"),
    ], 10)
    pfoot(s, "把 socket 当网络；把 pause() 当「进入 Guest 执行」。",
          "如果控制面走 virtqueue，Guest 死循环时还能暂停吗？", GREEN, np_())

    # --- 第 7 课 边界 ---
    s = new_page(prs, GREEN); head(s, "第 7 课 · 边界", "一个请求，三种结果，三种超时", GREEN,
                                 "「超时」这个词本身不含信息，必须拆开。")
    chain_h(s, 0.58, 1.98, 12.15, [("① 请求已发出", "本地把字节写进 socket"),
                                   ("② 收到成功响应", "接口层报告暂停成功"),
                                   ("③ 全部 vCPU 确认", "没有任何 vCPU 还在跑 Guest")], GREEN, bh=0.76)
    tb(s, 0.58, 2.95, 12.15, 0.28, "超时的三种可能（不能只凭超时下结论）", 10, True, DIM)
    quad(s, 0.58, 3.28, 12.15, 1.95, [
        ("完全没送到", "连接断了、Firecracker 刚起还没监听", ORANGE),
        ("送到了、做成了，响应丢了", "VM 其实已暂停，但你不知道", ORANGE),
        ("还在做", "vCPU 没被调度、设备 IO 卡住", ORANGE),
        ("所以正确做法", "查状态 + 重试要幂等，不能假设「没响应＝没执行」", GREEN),
    ], GREEN)
    tb(s, 0.58, 5.45, 12.15, 0.75,
       "延伸一句：这也是为什么快照流程要「先 pause、再确认、再读内存」——每一步都要有可验证的完成条件，而不是靠一次请求的返回值。",
       10, True, GREEN, ls=1.4)
    pfoot(s, "把「请求超时」直接等同于「操作失败」或「VM 还在跑」。",
          "超时后你发了一次 resume，会有什么风险？", GREEN, np_())

    # --- 第 8 课 机制 ---
    s = new_page(prs, GREEN); head(s, "第 8 课 · 机制", "三层就绪，一层比一层强", GREEN,
                                 "「进程在」「网络通」「应用能应答」是三件不同强度的事。")
    ladder = [("① API socket 可用", "能配 VM、能 pause", "证明 VMM 起来了、socket 路径对", GREEN),
              ("② 网络可达", "宿主经 tap0 能到 Guest", "证明 netns、网卡、IP、端口都对", GREEN),
              ("③ envd /health 通过", "状态码非 4xx/5xx", "证明服务真能应答，不只是监听", BLUE)]
    y = 1.98
    for i, (t, d, e, c) in enumerate(ladder):
        w = 8.2
        rr(s, 0.58, y, w, 0.92, fill=WHITE, line=c, r=0.04)
        rr(s, 0.58, y, 0.05, 0.92, fill=c, r=0)
        tb(s, 0.80, y + 0.10, 3.0, 0.26, t, 10, True, c)
        tb(s, 0.80, y + 0.42, 3.2, 0.28, d, 9, False, INK)
        tb(s, 3.95, y + 0.24, 4.5, 0.5, e, 8.5, False, DIM, ls=1.2)
        y += 1.02
    rr(s, 8.98, 1.98, 3.75, 2.96, fill=tint(GREEN, 0.95), line=tint(GREEN, 0.72), r=0.04)
    tb(s, 9.16, 2.08, 3.42, 2.8,
       "为什么需要第三层\n\n"
       "「端口能连」只证明\n监听套接字在工作；\n\n"
       "「health 通过」证明\n应用层能处理请求，\n"
       "能发现「进程在、端口开、\n服务却卡住」的情况。",
       9.5, False, INK, ls=1.5)
    tb(s, 0.58, 5.20, 12.15, 0.95,
       "调用链的形状：start() = start_nowait() + wait_for_ready()。前者只等 API socket 可用，后者才等 envd。\n"
       "拆成两个接口的意义：调用方可以先把磁盘、网络等准备做完，最后再统一等 Guest 服务。",
       10.5, False, INK, ls=1.45)
    pfoot(s, "把「envd 客户端对象创建成功」当成「Guest 服务就绪」。",
          "端口能连、命令却执行失败，问题可能在哪一层？", GREEN, np_())

    # --- 第 8 课 边界 ---
    s = new_page(prs, GREEN); head(s, "第 8 课 · 边界", "健康检查的实现细节（已核对固定版本）", GREEN,
                                 "这些细节决定了你对「就绪」的判断到底有多可靠。")
    table(s, 0.58, 1.95, 12.15, ["项目", "实际行为", "容易被误读成"], [
        ["请求", "GET {base_path}/health", "以为还要带鉴权头"],
        ["判定", "请求成功且状态码不是 4xx/5xx，不校验响应体", "以为必须等于 200"],
        ["单次上限", "min(1 秒, 剩余总时长)，失败继续重试", "以为一次失败就整体失败"],
        ["整体期限", "耗尽才返回超时错误", "以为没有重试"],
        ["成功后", "尽力通知 ublk daemon（放行后台下载），失败不影响就绪返回", "以为就绪＝一切就绪"],
    ], GREEN, colw=[2.0, 6.9, 3.25], rh=0.50)
    tb(s, 0.58, 5.05, 12.15, 1.1,
       "两个结论：① health 通过只说明「应用能应答」，不代表每个功能都可用；② 它不带 access token，\n"
       "所以「健康检查通过」不能当作「受保护命令的鉴权也通过」。",
       10.5, False, INK, ls=1.45)
    pfoot(s, "把 200 当唯一成功码；把 health 通过当成完整功能验证。",
          "envd 起来了但工具盘还没下载完，就绪该怎么判？", GREEN, np_())

    # --- 第 9 课 机制 ---
    s = new_page(prs, GREEN); head(s, "第 9 课 · 机制", "exec 返回的是一个流，不是一次结果", GREEN,
                                 "三类事件，两个独立判断——这是这一课的全部。")
    diagram_panel(s, 0.58, 1.95, 12.15, 1.60, "事件流（时间 →）", GREEN)
    evs = [("start 请求", "cmd + args + env + cwd"), ("Start{pid}", "进程已创建"),
           ("Data{...}", "stdout / stderr 分段"), ("End{code}", "进程已退出")]
    xx = 0.85
    for i, (t, d) in enumerate(evs):
        rr(s, xx, 2.28, 2.55, 0.92, fill=WHITE, line=GREEN if i < 3 else BLUE, r=0.04)
        tb(s, xx + 0.14, 2.36, 2.3, 0.26, t, 9.5, True, INK)
        tb(s, xx + 0.14, 2.64, 2.3, 0.48, d, 8.5, False, DIM, ls=1.2)
        if i < 3:
            arr_r(s, xx + 2.58, 2.62, 0.22, 0.20, LINE)
        xx += 2.92
    compare2(s, 0.58, 3.70, 12.15, 1.55,
             ("判断一：事件收齐了吗", ["Ok：一路收到 End", "Err：流结束但没等到 End"], GREEN),
             ("判断二：exit_code 是多少", ["0：程序自己认为成功", "非零：程序失败或被杀"], BLUE), GREEN)
    tb(s, 0.58, 5.42, 12.15, 0.8,
       "所以「exec 成功」要三样同时满足：wait 返回 Ok、收到 End、exit_code 符合预期。只有 Start，说明进程被创建出来了而已。",
       10.5, True, GREEN, ls=1.4)
    pfoot(s, "看到 Start 就当成功；只看 exit_code 不看流是否收齐。",
          "进程没有任何输出时，Data 事件会出现吗？", GREEN, np_())

    # --- 第 9 课 边界 ---
    s = new_page(prs, GREEN); head(s, "第 9 课 · 边界", "失败模式的四种样子", GREEN,
                                 "排障时先分类，再决定要不要重试。")
    quad(s, 0.58, 1.95, 12.15, 2.55, [
        ("起不来", "可执行文件不存在 / 权限不足：可能直接返回启动错误，不一定有 Start", ORANGE),
        ("起来了但立刻失败", "有 Start，随后 End 带非零码（脚本报错、依赖缺失）", ORANGE),
        ("跑着崩了", "有 Start 与部分 Data，然后流异常结束", ORANGE),
        ("超时被终止", "wait 超时；终止请求可能失败，所以不能断言进程已退出", ORANGE),
    ], GREEN)
    tb(s, 0.58, 4.72, 12.15, 1.45,
       "三个必须说清的边界：\n"
       "· 命令与参数分开传，不假设过 shell——没有 shell 就没有管道、通配符、重定向语义。\n"
       "· 结果未知时重试可能重复执行，所以业务侧要幂等；这不是 SDK 能替你解决的。\n"
       "· 宿主看到的 PID 与 Guest 内的 PID 是两套编号，不能直接互相当证据。",
       10, False, INK, ls=1.5)
    pfoot(s, "超时后终止失败，就断言进程已退出；把 stdout 当成唯一证据。",
          "一次 exec 超时了，你怎么判断它到底还在不在跑？", GREEN, np_())

    # ============ 章节 04 ============
    divider(prs, "04", "存储", "第 10—12 课：文件怎么变成块读写、分层怎么查、谁回答「这块是什么」", ORANGE, np_())

    # --- 第 10 课 机制 ---
    s = new_page(prs, ORANGE); head(s, "第 10 课 · 机制", "一条数据在三个坐标系里换名字", ORANGE,
                                 "文件偏移、逻辑块号、后端位置——报数时少一个单位就会被追。")
    chain_h(s, 0.58, 2.00, 12.15, [
        ("应用 read(fd,...)", "文件偏移 8 MiB"), ("Guest ext4", "extent → LBA"),
        ("Guest 块层", "合并 / 排队 / 调度"), ("virtio-blk", "描述符 + 通知"),
        ("Firecracker", "虚拟设备后端"), ("宿主后端", "层文件 / 块设备"),
    ], ORANGE, bh=0.86, size=9)
    paragraphs(s, 0.58, 3.20, 12.15, [
        ("三个偏移别混", "文件偏移属于文件系统；LBA 属于块设备（要带块/扇区大小）；后端实际位置只有宿主知道。文件内连续的数据，在磁盘上可以完全不连续。"),
        ("页缓存的作用", "命中时这次 read 可能根本不产生设备 IO；但路径解析、元数据、并发预读仍可能产生 IO，所以不能断言「整次调用零设备请求」。"),
        ("write 返回说明什么", "只说明数据进了页缓存，不代表落盘。要持久化靠 fsync/flush；这也解释了为什么「快照前要不要同步文件系统」是个真问题。"),
    ], 10)
    pfoot(s, "以为文件偏移 0 就是磁盘偏移 0；以为 write 返回＝持久化。",
          "一次 4 KiB 读，盘上可能读多少字节？为什么可能更多？", ORANGE, np_())

    # --- 第 10 课 边界 ---
    s = new_page(prs, ORANGE); head(s, "第 10 课 · 边界", "写路径的四个节点，只有最后一个算数", ORANGE,
                                 "「写成功」在存储栈里有四种不同含义。")
    chain_v(s, 0.58, 1.98, 4.20, [
        ("write() 返回", "数据进了 Guest 页缓存", ORANGE),
        ("脏页回写", "块层把脏页交给 virtio", ORANGE),
        ("后端写入", "Firecracker 写宿主后端（可能是层）", ORANGE),
        ("真正持久化", "fsync / flush / 远端确认", GREEN),
    ], ORANGE, gap=0.22, bh=0.58, size=9.5)
    tb(s, 5.10, 1.98, 7.60, 3.9,
       "为什么这件事对沙箱特别重要\n\n"
       "快照恢复会把「过去某一刻」的磁盘视图拿回来。如果快照前没有把应用数据真正刷下去，\n"
       "恢复后你会得到「文件存在、内容不对」的现场，而这种 bug 极难复现。\n\n"
       "所以真实的快照流程里有「预同步」这一步：\n"
       "有可写持久卷时，先让 Guest 内的文件系统把数据刷下去，再 pause。\n\n"
       "但它也有边界：文件系统同步 ≠ 用户程序私有缓冲已 flush，≠ 外部数据库事务已提交。\n"
       "这三层各有各的保证，不能互相替代。",
       10, False, INK, ls=1.55)
    pfoot(s, "把 fsync 当成「业务事务已提交」；把 write 返回当成「数据在盘上」。",
          "快照前为什么要先同步文件系统？它能保证业务一致性吗？", ORANGE, np_())

    # --- 第 11 课 机制 ---
    s = new_page(prs, ORANGE); head(s, "第 11 课 · 机制", "分层是覆盖映射，不是把文件拼起来", ORANGE,
                                 "每层一张索引：逻辑位置 → 本层偏移。读的时候从新到旧，第一个命中就停。")
    diagram_panel(s, 0.58, 1.95, 6.05, 3.85, "三层叠加与最终视图", ORANGE)
    layers = [("upper（可写）", "位置1 → 0x0100", GREEN), ("增量层（只读）", "位置3 → 显式零", ORANGE),
              ("基层（只读）", "位置0/1/2 → 各有数据", PURPLE)]
    yy = 2.30
    for t, d, c in layers:
        rr(s, 0.85, yy, 5.5, 0.80, fill=WHITE, line=c, r=0.04)
        rr(s, 0.85, yy, 0.05, 0.80, fill=c, r=0)
        tb(s, 1.02, yy + 0.09, 2.6, 0.26, t, 9.5, True, c)
        tb(s, 1.02, yy + 0.40, 5.1, 0.28, d, 8.5, False, DIM)
        yy += 0.92
    tb(s, 0.85, 5.05, 5.5, 0.55, "拼接字节只会得到 A/B/C/D/X/Y，表达不了「X 替换位置 1」。", 9, True, ORANGE, ls=1.3)
    tb(s, 6.90, 1.98, 5.80, 3.7,
       "读取规则只有一条\n"
       "从最新的一层往下查，哪一层有这段的记录就用它，命中即停；都没有才是空洞。\n\n"
       "两个语义必须分清\n"
       "· 「无记录」不是零，它表示「这层没管这段」，要继续往下找。\n"
       "· 「显式零」必须终止查找，否则会把下层旧数据暴露出来。\n\n"
       "为什么需要显式零\n"
       "父层有旧内容、新状态应为全零时，如果只写「无记录」，读数的人就会回落到父层，\n"
       "把早就该被抹掉的数据又读出来。",
       10, False, INK, ls=1.55)
    pfoot(s, "以为「没记录」等于读出为零；以为 OverlayBD 是数据库或 OverlayFS。",
          "某位置上层无记录、下层有数据，读出来是什么？", ORANGE, np_())

    # --- 第 11 课 边界 ---
    s = new_page(prs, ORANGE); head(s, "第 11 课 · 边界", "四种情形手算一遍就再也不会错", ORANGE,
                                 "同样读出 0，索引语义可能完全不同。")
    table(s, 0.58, 1.95, 12.15, ["逻辑位置", "父层", "新层", "读出的结果", "语义"], [
        ["位置 0", "A", "无记录", "A", "回落：本层没管，用父层"],
        ["位置 1", "B", "X", "X", "覆盖：新层赢，旧数据仍在但被遮住"],
        ["位置 2", "C", "显式零", "全零", "遮蔽：明确写过零，必须终止查找"],
        ["位置 3", "无映射", "无记录", "全零", "空洞：所有层都没写过"],
    ], ORANGE, colw=[1.55, 1.55, 1.55, 2.10, 5.40], rh=0.56)
    tb(s, 0.58, 4.85, 12.15, 1.4,
       "两个实现细节：① 索引项在概念上要能表达「起点、长度、来源层、层内位置、是否显式零」；\n"
       "② 后端读取失败必须作为错误返回，不能静默当成空洞——否则就是数据损坏而不是零。\n"
       "另外，一个读取范围可以跨多段映射，所以「一次逻辑读」不等于「一次层内读」。",
       10, False, INK, ls=1.5)
    pfoot(s, "把「后端读失败」当零返回；以为一个逻辑读范围只对应一段层内数据。",
          "读取跨了两个层的数据，谁负责拼？在读的哪一步发生？", ORANGE, np_())

    # --- 第 12 课 机制 ---
    s = new_page(prs, ORANGE); head(s, "第 12 课 · 机制", "内核给壳，用户态给内容", ORANGE,
                                 "ublk 把「块设备」的外形交给内核，把「这块里是什么」留给 daemon。")
    table(s, 0.58, 1.95, 6.10, ["设备节点", "用途"], [
        ["/dev/ublk-control", "全局管理：创建 / 删除 / 设参数"],
        ["/dev/ublkcN", "该设备的命令交接通道"],
        ["/dev/ublkbN", "对外读写的块设备"],
    ], ORANGE, colw=[2.25, 3.85], rh=0.46)
    tb(s, 0.58, 3.90, 6.10, 1.45,
       "创建流程：server 发 Create → 内核分配 N → daemon 等节点「真正可打开」（不只是文件存在）\n"
       "→ 回 (dev_id, device_path) → Firecracker 把它挂成 Guest 的 /dev/vdX。\n"
       "设备编号由内核分配，不能当固定 ID。",
       9.5, False, INK, ls=1.45)
    rr(s, 6.92, 1.95, 5.82, 3.40, fill=tint(ORANGE, 0.95), line=tint(ORANGE, 0.72), r=0.04)
    tb(s, 7.10, 2.05, 5.5, 3.2,
       "daemon 处理一次 4 KiB 读\n\n"
       "① 等待：在 io_uring 上提交「有活给我」\n"
       "② 领取：CQE 带回请求（queue、tag、偏移、长度）\n"
       "    —— 只代表「请求送到了」\n"
       "③ 解析：OverlayBD 查索引，定层、定偏移、取字节\n"
       "④ 提交：报告完成，原块请求才算完成",
       9.5, False, INK, ls=1.6)
    tb(s, 0.58, 5.55, 12.15, 0.65,
       "分工的本质：内核不认识你的文件格式，它只负责「第几块、多长」的搬运；格式与远端拉取都在用户态。",
       10.5, True, ORANGE, ls=1.4)
    pfoot(s, "把 FETCH_REQ 的完成当成「数据读完」；以为设备编号固定。",
          "Firecracker 挂盘用的是哪个节点？daemon 收请求用哪个？", ORANGE, np_())

    # --- 第 12 课 边界 ---
    s = new_page(prs, ORANGE); head(s, "第 12 课 · 边界", "daemon 的位置、代价与失败模式", ORANGE,
                                 "它不是一个可有可无的中间层，而是这条存储链的单点。")
    compare2(s, 0.58, 1.95, 12.15, 2.10,
             ("它是什么", ["宿主上一个常驻用户态进程", "集中式：一个进程管理该节点所有 ublk 设备",
                            "OverlayBD 是它链接的库，不是另一个服务"], GREEN),
             ("它不是什么", ["不是内核模块（挂了就是普通进程挂）", "不是每沙箱一个进程",
                             "不是 server 的线程"], ORANGE), ORANGE)
    quad(s, 0.58, 4.20, 12.15, 2.05, [
        ("好处：密度", "设备创建成本低、缓存集中，不用每沙箱 fork 一个服务", GREEN),
        ("代价：单点", "daemon 无响应 → 该节点全部块 IO 停滞或失败", ORANGE),
        ("隐藏依赖", "快照恢复前会检查 ublk 可用：内存镜像也走这条链路", VIOLET),
        ("错误语义", "后端读失败必须向上传播，不能当零返回，否则是静默损坏", ORANGE),
    ], ORANGE)
    pfoot(s, "以为 daemon 可以随时重启而不影响运行中的沙箱。",
          "daemon 升级要怎么做才能不打断沙箱？", ORANGE, np_())

    # ============ 章节 05 ============
    divider(prs, "05", "内存与快照", "第 13—18 课：映射、缺页、COW、捕获、封存、恢复", VIOLET, np_())

    # --- 第 13 课 机制 ---
    s = new_page(prs, VIOLET); head(s, "第 13 课 · 机制", "映射了 ≠ 分配了 ≠ 复制了", VIOLET,
                                 "整门课最值钱的一句话，也是面试最容易露馅的一句。")
    trio = [("① mmap 之后", "只有虚拟范围（VMA）\n没有任何物理页\n128 MiB 一个字节没占", GREEN),
            ("② 第一次读", "缺页：页在就映射，不在就去取\n取完填 PTE，指令重试", ORANGE),
            ("③ 第一次写", "COW：复制一份私有副本\n之后各写各的，共享页不变", PURPLE)]
    xx = 0.58
    for t, d, c in trio:
        rr(s, xx, 1.98, 3.95, 1.65, fill=WHITE, line=c, r=0.04)
        tb(s, xx + 0.16, 2.08, 3.6, 0.26, t, 10, True, c)
        tb(s, xx + 0.16, 2.38, 3.62, 1.15, d, 9, False, INK, ls=1.4)
        xx += 4.12
    paragraphs(s, 0.58, 3.85, 12.15, [
        ("缺页要分三类", "minor（页已在内存：零页、page cache）、major（页不在，要读文件/换入）、非法访问（无映射或权限不符，通常 SIGSEGV）。写保护缺页不属于非法访问，那是 COW 的正常处理。"),
        ("两种写语义", "MAP_SHARED 的写进共享缓存、按规则写回；MAP_PRIVATE 的写只影响自己的私有副本。fork 之后父子共享物理页、PTE 都设只读，任一方写才复制。"),
        ("接回 microVM", "恢复时 Guest RAM 是「只读层 + 私有可写」：第一次读某页会去后端取，第一次写才复制。所以「恢复」与「首次写」是两个不同的事件。"),
    ], 10)
    pfoot(s, "以为 mmap 128 MiB 就占 128 MiB 物理内存；以为 COW 在映射或 fork 时就发生。",
          "恢复后第一次读一页、第一次写一页，分别发生什么？", VIOLET, np_())

    # --- 第 13 课 边界 ---
    s = new_page(prs, VIOLET); head(s, "第 13 课 · 边界", "一层缺页，三层世界", VIOLET,
                                 "microVM 里同时存在三种缺页，混起来就解释不了延迟。")
    table(s, 0.58, 1.95, 12.15, ["哪一层", "谁处理", "缺什么", "典型后果"], [
        ["Guest 页表", "Guest 内核", "GVA→GPA 的 PTE", "Guest 内 minor/major fault"],
        ["EPT", "KVM（宿主内核）", "GPA→HPA 的 EPT 项", "VM-Exit，KVM 补完可直接重入"],
        ["宿主页表", "宿主内核", "HVA→HPA 的 PTE", "匿名页分配或文件页读入"],
    ], VIOLET, colw=[2.25, 3.30, 3.30, 3.30], rh=0.56)
    tb(s, 0.58, 4.20, 12.15, 1.15,
       "为什么这很重要：恢复后「首条命令很慢」可能来自任意一层——Guest 内的缺页、EPT 缺项、或宿主侧去只读层取页。\n"
       "只说「缺页慢」等于没说，要指出是哪一层、缺的是什么。",
       10.5, False, INK, ls=1.45)
    rr(s, 0.58, 5.42, 12.15, 0.80, fill=tint(VIOLET, 0.95), line=tint(VIOLET, 0.72), r=0.04)
    tb(s, 0.76, 5.52, 11.8, 0.62,
       "量化的正确口径：minor/major 分开统计；EPT 缺项看退出计数；后端取页看实际读盘量。三个指标不能相加。",
       9.5, False, INK, ls=1.35)
    pfoot(s, "把三层缺页混成一个「缺页率」；用缺页数代替延迟。",
          "恢复后首条命令慢，你会先查哪一层？为什么？", VIOLET, np_())

    # --- 第 14 课 机制 ---
    s = new_page(prs, VIOLET); head(s, "第 14 课 · 机制", "快照是四件套，缺一件就恢复不出来", VIOLET,
                                 "「存个内存」只是其中一件事。")
    quad(s, 0.58, 1.95, 12.15, 2.45, [
        ("① VM 状态", "vCPU 寄存器、指令位置、虚拟设备状态：决定「从哪继续执行」", BLUE),
        ("② 内存镜像", "Guest RAM 内容，可增量 + 父层组合：决定「变量是什么值」", VIOLET),
        ("③ 磁盘视图", "rootfs 层 + 额外盘 + 父层引用：决定「文件长什么样」", ORANGE),
        ("④ 恢复配置/索引", "层顺序、设备关联、兼容参数：决定「怎么拼回去」", GREEN),
    ], VIOLET)
    chain_h(s, 0.58, 4.55, 12.15, [("pause", "停止执行 Guest"), ("捕获", "读内存、写层、出状态文件"),
                                   ("持久化", "fsync / 上传"), ("释放运行时", "关实例、回收资源")], VIOLET, bh=0.70)
    tb(s, 0.58, 5.42, 12.15, 0.75,
       "这四步是四个不同的完成点：暂停成功不代表捕获成功，捕获成功不代表已落盘，落盘也不代表运行时已释放。",
       10.5, True, VIOLET, ls=1.4)
    pfoot(s, "把 pause 成功当快照成功；把「已写出文件」当成「已持久化」。",
          "哪一步失败会导致「快照看起来存在但恢复不了」？", VIOLET, np_())

    # --- 第 14 课 边界 ---
    s = new_page(prs, VIOLET); head(s, "第 14 课 · 边界", "为什么一致性和业务一致性是两件事", VIOLET,
                                 "抓取期间数据在变，这是第一层；外部世界不回滚，是第二层。")
    rr(s, 0.58, 1.95, 6.05, 1.85, fill=WHITE, line=VIOLET, r=0.04)
    tb(s, 0.76, 2.05, 5.7, 1.65,
       "机器状态的一致性\n"
       "真实顺序：x=100 → x=90 → y=110\n"
       "采集顺序：读到旧 x=100，之后读到新 y=110\n"
       "→ 拼出「从未同时存在」的 x=100,y=110\n\n"
       "解法：先暂停全部 vCPU，再捕获。",
       9.5, False, INK, ls=1.45)
    rr(s, 6.90, 1.95, 5.85, 1.85, fill=tint(ORANGE, 0.95), line=tint(ORANGE, 0.72), r=0.04)
    tb(s, 7.08, 2.05, 5.5, 1.65,
       "但它不解决业务一致性\n"
       "快照里写着「付款请求已发出，等待响应」，\n"
       "而外部支付系统那边可能已经扣款成功。\n\n"
       "恢复 + 重试 → 可能重复支付。所以要幂等与对账。",
       9.5, False, INK, ls=1.45)
    tb(s, 0.58, 4.05, 12.15, 1.9,
       "还有两个容易被忽略的边界：\n"
       "· 暂停只停 Guest 的 CPU 写入，宿主设备侧仍可能写 Guest RAM，完整方案要协调设备与在途 IO。\n"
       "· 暂停若恰好落在真实的中间时刻（x=90,y=100），那是一个合法快照——只是它不在业务事务边界上，恢复后应用继续跑完剩下的步骤。\n"
       "  所以「机器一致」是必要条件，不是「业务一致」的充分条件。",
       10, False, INK, ls=1.5)
    pfoot(s, "把 VM 一致性当成业务一致性；以为恢复能撤回外部系统的操作。",
          "恢复后应用会从哪继续执行？业务侧要注意什么？", VIOLET, np_())

    # --- 第 15 课 机制 ---
    s = new_page(prs, VIOLET); head(s, "第 15 课 · 机制", "增量必须有基线，范围描述不是字节", VIOLET,
                                 "只存脏页省空间，但前提是「没存的能从父层补回来」。")
    table(s, 0.58, 1.95, 7.30, ["", "页0", "页1", "页2", "页3", "页4", "页5"], [
        ["S0 基线", "A", "B", "C", "D", "E", "F"],
        ["S1 增量", "—", "B1", "—", "—", "E1", "—"],
        ["S2 增量", "—", "—", "—", "—", "E2", "F2"],
        ["S2 视图", "A", "B1", "C", "D", "E2", "F2"],
    ], VIOLET, colw=[1.60, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95], rh=0.50)
    tb(s, 0.58, 4.55, 7.30, 0.95,
       "「—」表示本层没有覆盖记录，要回落，不是零。\n"
       "所以 S2 依赖 S1 与 S0；丢弃父层就会读出错误内容。",
       9.5, False, INK, ls=1.45)
    tb(s, 8.15, 1.95, 4.60, 3.55,
       "范围描述里都有什么\n"
       "· 源地址：Firecracker 的 HVA\n"
       "· 目的位置：完整镜像里的逻辑偏移\n"
       "· 长度：按 4 KiB 页对齐\n\n"
       "它只说明「从哪取、存到逻辑哪里」，\n"
       "创建范围、记录 dirty 位这两件事，\n"
       "都不复制数据、也不冻结内容。\n\n"
       "一致性靠的是第 14 课的暂停与协调。",
       9.5, False, INK, ls=1.5)
    pfoot(s, "以为 dirty 列表能保证一致快照；以为范围描述里带着数据。",
          "S2 的页 1 和页 4 分别来自哪一层？", VIOLET, np_())

    # --- 第 15 课 边界 ---
    s = new_page(prs, VIOLET); head(s, "第 15 课 · 边界", "dirty / present / 内容为零 是三件事", VIOLET,
                                 "这三个词答混，快照恢复就会读出不该出现的数据。")
    table(s, 0.58, 1.95, 12.15, ["概念", "含义", "常见误解"], [
        ["dirty", "在跟踪区间内被记录为写过", "以为「改回原值就不脏」——可能仍是脏"],
        ["present / resident", "页是否驻留（存在）", "以为这是修改历史，或以为它等价于 PTE/位图状态"],
        ["内容为零", "值本身是 0", "以为「不驻留」就等于「为零」，于是省略覆盖记录"],
    ], VIOLET, colw=[2.30, 5.30, 4.55], rh=0.56)
    tb(s, 0.58, 4.10, 12.15, 1.75,
       "推论一：父层有旧内容、新状态应为全零时，不能因为「页面不驻留」就省略覆盖记录，否则会读回父层旧数据。\n"
       "推论二：完整逻辑大小、新层实际数据量、读取请求数、恢复时真实物理 IO 量，是四个不同指标，不能互相代入。\n"
       "推论三：页粒度（4 KiB）描述「存什么」，请求粒度可能更大或更小，两者不能混。",
       10, False, INK, ls=1.5)
    pfoot(s, "把页不驻留当成内容为零；把新层数据量当成恢复时的读盘量。",
          "一页写了新值又改回原值，dirty 标记会消失吗？", VIOLET, np_())

    # --- 第 16 课 机制 ---
    s = new_page(prs, VIOLET); head(s, "第 16 课 · 机制", "四个参数，每一个都有归属", VIOLET,
                                 "这题面试常问，问到第二层就会暴露「有没有真读过源码」。")
    rr(s, 0.58, 1.95, 6.20, 2.05, fill=WHITE, line=VIOLET, r=0.04)
    tb(s, 0.76, 2.06, 5.85, 1.85,
       "process_vm_readv(\n"
       "    pid,          // Firecracker 的宿主 PID\n"
       "    local_iov,    // server 自己的缓冲区\n"
       "    remote_iov,   // 地址属于 Firecracker（HVA）\n"
       "    flags)        // 必须为 0",
       9.5, False, INK, ls=1.55)
    rr(s, 6.95, 1.95, 5.80, 2.05, fill=tint(VIOLET, 0.94), line=tint(VIOLET, 0.72), r=0.04)
    tb(s, 7.13, 2.06, 5.45, 1.85,
       "两个 iovec 数组本身都在调用者内存里\n\n"
       "只有 remote_iov 元素里的地址指向目标进程；\n"
       "liovcnt / riovcnt 是元素个数，不是字节数。",
       9.5, False, INK, ls=1.55)
    tb(s, 0.58, 4.20, 12.15, 1.6,
       "数据流：Firecracker 的 Guest RAM 映射 → 内核复制一次 → server 的目的缓冲区 → 之后才由 writer 写成层。\n"
       "所以「先读到 server 内存、再写文件」是这个实现的路径；原理上不是唯一做法（比如让 Firecracker 自己写共享映射），\n"
       "但那要另外处理格式、接口与一致性。",
       10, False, INK, ls=1.5)
    pfoot(s, "以为 remote 地址可以是 GVA 或 GPA；以为 iovec 数量是字节数。",
          "remote_iov 里的地址到底是什么？为什么不是 GPA？", VIOLET, np_())

    # --- 第 16 课 边界 ---
    s = new_page(prs, VIOLET); head(s, "第 16 课 · 边界", "读循环的四种情形", VIOLET,
                                 "写不好循环，就会出现「少读了一半还以为成功」。")
    quad(s, 0.58, 1.95, 12.15, 2.35, [
        ("正常", "返回 n = 请求长度：目的正好填满", GREEN),
        ("短读", "n < 请求长度：源和目的同时前进 n，再继续（不是从头重读）", ORANGE),
        ("被信号打断", "EINTR：重试，不算失败", ORANGE),
        ("零进展或异常", "返回 0、超过请求长度、地址加法溢出：必须报错", ORANGE),
    ], VIOLET)
    tb(s, 0.58, 4.55, 12.15, 1.35,
       "三个边界：\n"
       "· 失败时 buffer 可能已有部分字节，但函数返回错误就不能当整段有效。\n"
       "· 多段读取之间源内容仍可能变化，PVM 不提供整份快照的原子性。\n"
       "· 权限不足、目标进程退出、源映射消失，都会让读取失败——这些是真实的错误路径，不是理论情况。",
       10, False, INK, ls=1.5)
    pfoot(s, "把短读当成失败，或把部分填充的 buffer 当有效数据。",
          "异步外壳会不会让这段同步读变成非阻塞？为什么？", VIOLET, np_())

    # --- 第 17 课 机制 ---
    s = new_page(prs, VIOLET); head(s, "第 17 课 · 机制", "chunk 是任务批次，buffer 才是字节", VIOLET,
                                 "元数据线与字节线并行：一条决定「存到哪」，一条决定「搬什么」。")
    rr(s, 0.58, 1.95, 12.15, 0.95, fill=tint(BLUE, 0.95), line=tint(BLUE, 0.72), r=0.04)
    tb(s, 0.76, 2.04, 11.8, 0.26, "元数据线", 9.5, True, BLUE)
    tb(s, 0.76, 2.30, 11.8, 0.5, "范围映射 → entry(tag / src_offset / len / logical_offset) → chunk → 输出索引（逻辑范围 → 层内位置）",
       9, False, INK, ls=1.3)
    rr(s, 0.58, 3.02, 12.15, 0.95, fill=tint(ORANGE, 0.95), line=tint(ORANGE, 0.72), r=0.04)
    tb(s, 0.76, 3.11, 11.8, 0.26, "字节线", 9.5, True, ORANGE)
    tb(s, 0.76, 3.37, 11.8, 0.5, "Firecracker 源 HVA → ProcessVmReader → server buffer → writer（buffer 生命周期必须覆盖实际写入）",
       9, False, INK, ls=1.3)
    segs = [("header", 1.55, LINE), ("payload（紧凑）", 3.85, tint(ORANGE, 0.78)),
            ("index", 2.00, tint(BLUE, 0.78)), ("trailer", 1.35, LINE)]
    xx = 0.58
    for name, w, c in segs:
        rr(s, xx, 4.20, w, 0.56, fill=c, line=LINE, r=0.03)
        tb(s, xx + 0.06, 4.28, w - 0.12, 0.4, name, 9, True, INK, PP_ALIGN.CENTER, MSO_ALIGN_TOP if False else MSO_ANCHOR.MIDDLE)
        xx += w + 0.10
    tb(s, 0.58, 4.95, 12.15, 1.3,
       "为什么一个 chunk 不等于一次 syscall：chunk 只是把若干 entry 组织在一起；源是 ProcessVmReader 时，\n"
       "每个 entry 各自走一遍跨进程读，短读还要在内部循环。\n"
       "所以 chunk 大小、并发度、syscall 次数、真实磁盘 IO 次数，是四个不同指标。",
       10, False, INK, ls=1.5)
    pfoot(s, "以为 chunk 已经把多次读合并成一次 syscall；以为 buffer 可以提交后立刻复用。",
          "一个 chunk 有两个 entry，是几次跨进程读？为什么？", VIOLET, np_())

    # --- 第 17 课 边界 ---
    s = new_page(prs, VIOLET); head(s, "第 17 课 · 边界", "封存的六个完成点", VIOLET,
                                 "越往后越接近「真的存住了」，但大多数代码只检查前几个。")
    chain_h(s, 0.58, 2.00, 12.15, [
        ("源读取完成", "buffer 有数据"), ("chunk 写入完成", "writer 收下"),
        ("格式写全", "header/payload/index/trailer"), ("finalize", "格式处理结束"),
        ("rename", "切换名字"), ("发布/持久化", "fsync 或上传确认"),
    ], VIOLET, bh=0.86, size=8.5)
    tb(s, 0.58, 3.25, 12.15, 1.9,
       "三个必须说清的边界：\n"
       "· finalize 只表示 writer 完成格式处理，不保证已同步到稳定存储。\n"
       "· rename 只是切换名字：不自动保证断电持久化，也不代替 VM 状态、父层引用、磁盘与 manifest 的整体发布。\n"
       "· 任一步失败都返回错误；「buffer 填满」或「最后一次 write 成功」都不等于整层成功（源码里有临时文件清理与上层恢复）。",
       10, False, INK, ls=1.5)
    rr(s, 0.58, 5.30, 12.15, 0.85, fill=tint(VIOLET, 0.95), line=tint(VIOLET, 0.72), r=0.04)
    tb(s, 0.76, 5.40, 11.8, 0.65,
       "一个能加分的说法：写出顺序不等于恢复访问顺序——恢复时是按逻辑视图按需加载的。",
       9.5, False, INK, ls=1.35)
    pfoot(s, "把 finalize + rename 当成「已持久化」；以为写完就能立刻删父层。",
          "写层成功但 manifest 没写，这套快照能恢复吗？", VIOLET, np_())

    # --- 第 18 课 机制 ---
    s = new_page(prs, VIOLET); head(s, "第 18 课 · 机制", "恢复不是「把内存读回来」", VIOLET,
                                 "主路径是：映射只读内存设备，按需缺页，写时 COW。")
    chain_v(s, 0.58, 1.95, 4.35, [
        ("准备运行环境", "检查 ublk、备盘、备网", BLUE),
        ("加载 VM 状态", "load_snapshot_file(resume_vm=false)", BLUE),
        ("映射内存后端", "只读块设备 + 私有映射", VIOLET),
        ("补充配置", "新挂载卷、MMDS、限流", BLUE),
        ("resume", "vCPU 继续，缺页按需取", GREEN),
    ], VIOLET, gap=0.20, bh=0.56, size=9)
    tb(s, 5.25, 1.95, 7.45, 4.0,
       "冷恢复时一页 RAM 怎么变得可访问\n\n"
       "Guest 访问某个 GPA → 宿主页表缺项\n"
       "→ 向只读内存设备发块读 → daemon 查 OverlayBD 找这一块\n"
       "→ 取到数据、填进宿主页 → Guest 继续执行\n\n"
       "写这一页：COW 到私有层，共享镜像不动。\n"       "（已核验：同一模板的沙箱共享同一只读 ublk 设备与页缓存；FC 用 MAP_PRIVATE 映射，写时才 COW）\n\n"
       "为什么先 resume_vm=false：先把状态与设备关联都装好、把网络与额外盘补上，\n"
       "最后再让 vCPU 真的跑起来——否则 Guest 会在配置还没齐时就开始执行。",
       10, False, INK, ls=1.55)
    tb(s, 0.58, 6.02, 12.15, 0.34,
       "推论：恢复成功 ≠ 所有页已在宿主 RAM。首条命令慢、内存指标却不高，是正常的按需加载。",
       10.5, True, VIOLET, ls=1.4)
    pfoot(s, "以为恢复会把全部内存读回宿主；以为恢复返回就代表随时都能快速执行。",
          "恢复后首条命令很慢，是故障还是正常？怎么验证？", VIOLET, np_())

    # --- 第 18 课 边界 ---
    s = new_page(prs, VIOLET); head(s, "第 18 课 · 边界", "恢复不回来的东西", VIOLET,
                                 "VM 内部能回滚，外部世界不会。这条边界决定了「恢复能不能用」。")
    quad(s, 0.58, 1.95, 12.15, 2.40, [
        ("对端状态", "TCP 对端可能已超时、重传、关闭连接", ORANGE),
        ("宿主 conntrack / NAT", "快照时建立的映射可能已过期或被回收", ORANGE),
        ("计时器与时钟", "超时、退避、租约都按「现在」算，不随快照回滚", ORANGE),
        ("文件与外部事务", "外部数据库/对象存储不随 VM 一起回滚", ORANGE),
    ], VIOLET)
    tb(s, 0.58, 4.60, 12.15, 1.35,
       "所以「恢复后网络不通」不是玄学：Guest 里的 socket 结构还在，但它对应的四元组在对端和宿主侧可能都已失效。\n"
       "工程上的做法是重连而不是续连，并且要幂等——这也是为什么真实的 Agent 恢复流程里常带「重新握手」这一步。",
       10, False, INK, ls=1.5)
    pfoot(s, "以为恢复 Guest 内存就等于恢复业务状态；用「继续用旧连接」当作默认假设。",
          "恢复后为什么建议重连而不是续连？", VIOLET, np_())

    # ============ 章节 06 ============
    divider(prs, "06", "网络与隔离", "第 19—20 课：包怎么出去，四道门各关什么", AMBER, np_())

    # --- 第 19 课 机制 ---
    s = new_page(prs, AMBER); head(s, "第 19 课 · 机制", "同一个内核，不同的网络视图", AMBER,
                                 "每个 netns 都可以有名叫 tap0 的接口；靠 slot 地址区分实例。")
    chain_h(s, 0.58, 1.98, 12.15, [
        ("Guest eth0", "VirtIO-net"), ("TAP", "沙箱 netns"), ("SNAT", "改为 slot 地址"),
        ("veth", "进主 netns"), ("MASQUERADE", "适配出口"),
    ], AMBER, bh=0.80, size=9)
    tb(s, 0.58, 3.00, 12.15, 0.28, "反方向：宿主访问 envd（DNAT 进沙箱）", 9.5, True, BLUE)
    chain_h(s, 0.58, 3.30, 12.15, [
        ("server", "发到 slot 地址"), ("veth", "进沙箱 netns"), ("DNAT", "改成 Guest IP"),
        ("tap0 → Firecracker", "VirtIO RX"), ("envd", "处理请求"),
    ], BLUE, bh=0.80, size=9)
    tb(s, 0.58, 4.30, 12.15, 1.55,
       "三个必须说准的点：\n"
       "· TX 的 used 只表示「这个发送缓冲可以回收」，不表示远端收到，更不表示业务成功。\n"
       "· 返回流量依赖连接跟踪的 NAT 状态逆向还原，不是「server 每次读包再决定转发给谁」。\n"
       "· 有路由不代表允许：内部地址池禁止规则、用户策略、代理分支都可能拦下。",
       10, False, INK, ls=1.5)
    pfoot(s, "以为同名 tap0 会冲突；以为 TX 完成＝对端收到。",
          "两个沙箱的 Guest 都用同一段 IP，为什么不冲突？", AMBER, np_())

    # --- 第 19 课 边界 ---
    s = new_page(prs, AMBER); head(s, "第 19 课 · 边界", "代理分支与快照的边界", AMBER,
                                 "这条路不是「所有协议都能按域名拦」，也不是「恢复后连接自动续上」。")
    rr(s, 0.58, 1.95, 6.05, 1.95, fill=WHITE, line=AMBER, r=0.04)
    tb(s, 0.76, 2.05, 5.7, 1.75,
       "代理分支\n"
       "TCP 80/443 可被 REDIRECT 到出口代理；\n"
       "代理看 HTTP Host 或 TLS ClientHello 的 SNI\n"
       "再决定是否放行。\n"
       "基线声明：不终止 TLS、不改写 HTTP。",
       9.5, False, INK, ls=1.45)
    rr(s, 6.90, 1.95, 5.85, 1.95, fill=tint(ORANGE, 0.95), line=tint(ORANGE, 0.72), r=0.04)
    tb(s, 7.08, 2.05, 5.5, 1.75,
       "它不是万能的\n"
       "· 只覆盖 TCP，UDP/443 不在内\n"
       "· 不是通用域名防火墙\n"
       "· 已有连接的策略效果与新连接不同：\n"
       "  改 deny 不一定断开已建立的转发",
       9.5, False, INK, ls=1.45)
    tb(s, 0.58, 4.10, 12.15, 1.85,
       "与快照的交界：恢复会替换宿主 tap0 绑定、重新准备网络环境，但恢复 Guest RAM 与 socket 状态，\n"
       "不会把对端状态、宿主 conntrack/NAT、网络超时一起带回过去。\n"
       "所以「恢复后旧 TCP 连接还能不能用」的正确答案是：不保证，应按重连设计。",
       10, False, INK, ls=1.5)
    pfoot(s, "把 TCP 重定向当成「全协议域名白名单」；以为策略更新会立即切断现有连接。",
          "策略从 allow 改成 deny，已建立的连接会立刻断吗？", AMBER, np_())

    # --- 第 20 课 机制 ---
    s = new_page(prs, AMBER); head(s, "第 20 课 · 机制", "四类威胁，四道不同的门", AMBER,
                                 "先问「防谁、防什么」，再问「用什么挡」。顺序错了，答案一定错。")
    quad(s, 0.58, 1.95, 12.15, 2.50, [
        ("A. Guest 内作恶（含 root）", "没越过任何门：Guest root 本来就能任意 syscall\n挡它的是 Guest 自己的内核（RLIMIT / pid_max）", BLUE),
        ("B. VMM 被攻破（逃逸）", "已越过虚拟化边界\n挡它的是 seccomp / 降权 / chroot / caps / LSM", ORANGE),
        ("C. 资源超用", "没越界，走正常消耗\n挡它的是 cgroup 限值、vCPU 数、balloon", GREEN),
        ("D. 网络外连", "没越界，走虚拟网卡\n挡它的是 netns + veth + iptables + 出口代理", PURPLE),
    ], AMBER)
    tb(s, 0.58, 4.68, 12.15, 1.35,
       "一句话分家：namespace 改「看见什么」，cgroup 改「能用多少」，seccomp/caps/LSM 改「能对内核做什么」，虚拟化改「有几台机器」。\n"
       "四者互不替代——只做 namespace 就等于「什么都看得见但都没锁」，只做 seccomp 就等于「锁了 syscall 但资源随便吃」。",
       10, False, INK, ls=1.5)
    pfoot(s, "把 namespace 当成权限隔离；以为有虚拟化就不用管 cgroup。",
          "Guest 里的 root 和宿主里的 root，能力差在哪？", AMBER, np_())

    # --- 第 20 课 边界 ---
    s = new_page(prs, AMBER); head(s, "第 20 课 · 边界", "seccomp 拦不住 Guest，只用线程级", AMBER,
                                 "这一页是整门课最容易被追问穿的地方。")
    table(s, 0.58, 1.95, 12.15, ["事实", "说明"], [
        ["作用对象是线程", "filter 装在每个线程上；同一进程里不同线程可以有不同白名单"],
        ["拦的是宿主 syscall", "只约束 VMM 自己发出的系统调用；Guest 内部的 syscall 由 Guest 内核处理，看不到"],
        ["默认动作是 trap", "命中未允许的 syscall → SIGSYS 直接杀进程，不是返回 EPERM"],
        ["升级会踩坑", "新版本引入新 syscall，旧过滤器会当场 trap，所以过滤器要跟着版本走"],
        ["pids.max 挡不住 Guest fork", "pids 控制器只数宿主 cgroup 里的 task；Guest 进程不是宿主 task"],
    ], AMBER, colw=[3.35, 8.80], rh=0.52)
    tb(s, 0.58, 4.95, 12.15, 1.1,
       "所以「VMM 被攻破后还剩什么」要能一条条数：seccomp 限制 syscall 面、降权限制 uid、chroot 限制文件视野、\n"
       "caps 去掉危险能力、LSM 按路径再收一层、netns 限制网络视野。少哪一条，就是逃逸后的活动空间。",
       10, False, INK, ls=1.5)
    pfoot(s, "以为 seccomp 能限制 Guest 里的程序；以为 namespace 里的 root 已经没有特权。",
          "VMM 逃逸成功后，攻击者第一件事会做什么？哪一层挡它？", AMBER, np_())

    # ============ 章节 07 ============
    divider(prs, "07", "面试", "五个必深点 · 四段式 · 追问与纠错", TEAL, np_())

    s = new_page(prs, TEAL); head(s, "面试", "五个必深点：每个都要能讲 5 分钟", TEAL,
                                 "其余课程 15 秒能答就够；深度集中在能决定结果的地方。")
    table(s, 0.58, 1.95, 12.15, ["深点", "要能说清", "必备证据"], [
        ["① 地址空间", "四条地址线 + PVM 参数归属 + 短读处理", "一次跨进程读的字节数与耗时"],
        ["② VM-Exit 分流", "MMIO 靠 EPT 缺映射、PIO 靠敏感指令；exit_reason 怎么分流", "一次压测里的退出次数"],
        ["③ 快照与恢复", "四件套、一致性、只读层 + COW + 按需加载", "冷/热恢复延迟对比"],
        ["④ 隔离各层", "四道门各挡什么、漏什么；seccomp 是线程级", "真实进程的线程数与 Seccomp 值"],
        ["⑤ 性能口径", "wall 与 CPU、p50/p99、资源就绪 vs 首命令完成", "一段分段耗时表"],
    ], TEAL, colw=[2.30, 6.55, 3.30], rh=0.62)
    tb(s, 0.58, 5.80, 12.15, 0.55,
       "右列是「做过」的证据。缺哪一行，就从那一行开始补数字——讲得再顺，没有证据也只在第一层。",
       10.5, True, ORANGE, ls=1.4)
    pfoot(s, "把「读过文档」当成「有证据」。",
          "这五点里，你现在能立刻拿出证据的是哪几个？", TEAL, np_())

    s = new_page(prs, TEAL); head(s, "面试", "四段式与一段示范", TEAL,
                                 "以「你们沙箱怎么隔离」为例，给一份可以直接照着说的答案。")
    rr(s, 0.58, 1.95, 3.55, 3.85, fill=WHITE, line=LINE, r=0.04)
    tb(s, 0.76, 2.05, 3.2, 3.6,
       "模板\n\n① 结论\n一句话给判断\n\n② 机制\n两句：谁在哪层做什么\n\n③ 边界\n一句半：挡不住什么、代价\n\n④ 证据\n一个数字 / 一次实测 / 一次故障",
       9.5, False, INK, ls=1.45)
    rr(s, 4.30, 1.95, 8.42, 3.85, fill=tint(TEAL, 0.95), line=tint(TEAL, 0.72), r=0.04)
    tb(s, 4.50, 2.05, 8.05, 3.6,
       "示范\n\n"
       "结论：分两类——一类防 Guest 越界，一类防 VMM 被攻破后的破坏力。\n"
       "机制：Guest 与宿主之间靠硬件虚拟化；VMM 自己只是宿主上的普通进程，靠 seccomp 白名单限 syscall、\n"
       "　　　namespace 给它独立的挂载与网络视图、cgroup 管用量。\n"
       "边界：namespace 只改视图不改权限；cgroup 只记账不设限等于没有；seccomp 是线程级，拦不到 Guest 内 syscall。\n"
       "证据：我读过的一份实现里，VMM 用 unshare -m + ip netns exec 启动、没有 jailer、cgroup 只读不设限，\n"
       "　　　所以逃逸后只剩 seccomp 一道——这条结论来自真实配置，不是推测。",
       9.5, False, INK, ls=1.5)
    tb(s, 0.58, 5.95, 12.15, 0.4,
       "第 4 段是分水岭：前三段背得出的人很多，能说出「我在哪看到 / 我测出多少」的人很少。",
       10.5, True, TEAL)
    pfoot(s, "只报平均值不报分位数；只讲名词不讲「什么条件下会变坏」。",
          "用 90 秒讲完「VM-Exit」，你能讲完吗？", TEAL, np_())

    s = new_page(prs, TEAL); head(s, "面试", "追问速答与已纠正的说法", TEAL,
                                 "左半是被追问的三层，右半是别再讲错的六条。")
    table(s, 0.58, 1.95, 6.05, ["追问", "答题方向"], [
        ["Guest root 会被 seccomp 拦吗", "不会，只约束 VMM 的宿主 syscall"],
        ["为什么不能边跑边抓", "页在变，会拼出从未存在的状态"],
        ["恢复后网络为什么不通", "对端、conntrack、计时器都没回滚"],
        ["冷启动 3 秒先查哪段", "分段计时，各给 wall 与 CPU"],
        ["fork 两实例共享什么", "共享只读底座，各自 COW"],
        ["daemon 挂了会怎样", "该节点块 IO 停；恢复直接失败"],
    ], TEAL, colw=[2.55, 3.50], rh=0.50, size=9)
    table(s, 6.92, 1.95, 5.82, ["✗ 错误", "✓ 正确"], [
        ["pids.max 挡 guest fork", "只数宿主 task，挡不住"],
        ["多实例共享 page cache", "只在文件 mmap 模型成立"],
        ["VM-Exit＝KVM_RUN 返回", "KVM 可处理完直接重入"],
        ["namespace＝降权", "只改视图，root 仍是 root"],
        ["finalize+rename＝持久化", "只保证格式与名字"],
        ["health 通过＝鉴权通过", "health 不带 token"],
    ], ORANGE, colw=[2.60, 3.22], rh=0.50, size=9, hsize=9)
    tb(s, 0.58, 5.55, 12.15, 0.65,
       "这六条的共同病根：把「某一层的完成」当成「整件事完成」，或者把「看见什么」当成「能用多少」。",
       10.5, True, INK, ls=1.4)
    pfoot(s, "同一句错话会被追问到不同深度，但第一句错就结束了。",
          "这六条你能用自己的话重讲一遍吗？", TEAL, np_())

    # ============ 收尾 ============
    s = new_page(prs, BLUE); head(s, "下一步", "把「讲过」变成「做过」", BLUE,
                                 "剩下的缺口很具体：几个数字，和两个还没演练的深点。")
    todo = [("还没演练的深点", "地址空间（PVM 参数与短读）、性能度量（冷启动怎么查）", BLUE),
            ("还没跑的实验", "/dev/kvm 通路、namespace 创建耗时、cgroup 限额是否生效", ORANGE),
            ("还没有的数字", "冷/热恢复延迟、一次跨进程读耗时、一次压测的退出次数", VIOLET),
            ("还没改的课", "第 21—28 课改成面试格式；三篇项目故事", GREEN)]
    y = 2.00
    for t, d, c in todo:
        rr(s, 0.58, y, 12.15, 0.86, fill=WHITE, line=LINE, r=0.04)
        rr(s, 0.58, y, 0.05, 0.86, fill=c, r=0)
        tb(s, 0.82, y + 0.10, 3.3, 0.28, t, 10.5, True, c)
        tb(s, 4.20, y + 0.10, 8.35, 0.66, d, 9.5, False, INK, ls=1.25)
        y += 0.98
    tb(s, 0.58, 6.02, 12.15, 0.4,
       "下一个动作只有一个：在 WSL 里跑 ls -l /dev/kvm，把实验的路打通。", 10.5, True, BLUE)
    pfoot(s, "只看不测：面试问「你测过吗」，答不出数字，前面讲得再好也会掉档。",
          "下一周你打算补哪个数字？基线怎么定？", BLUE, np_())

    prs.save(path)
    print("saved:", path, "slides:", len(prs.slides))

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "review_v3.pptx")
