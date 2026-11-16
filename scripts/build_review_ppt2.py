# -*- coding: utf-8 -*-
"""AgentENV 全课复习 PPT（图文版）：左图右文 + 真解释，不堆提纲。
用法：python build_review_ppt2.py <输出路径>
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

FONT = "Microsoft YaHei"
INK = RGBColor(0x1A, 0x1F, 0x24)
DIM = RGBColor(0x5C, 0x6B, 0x7A)
FAINT = RGBColor(0x8A, 0x99, 0xA8)
LINE = RGBColor(0xD8, 0xDF, 0xE6)
PAPER = RGBColor(0xFB, 0xFC, 0xFD)
SOFT = RGBColor(0xF2, 0xF5, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

BLUE = RGBColor(0x1F, 0x6F, 0xEB)
PURPLE = RGBColor(0x7C, 0x4D, 0xD8)
GREEN = RGBColor(0x1F, 0x8B, 0x3D)
ORANGE = RGBColor(0xC2, 0x5D, 0x1C)
VIOLET = RGBColor(0x8E, 0x4E, 0xD6)
AMBER = RGBColor(0xB0, 0x7D, 0x0E)
TEAL = RGBColor(0x0F, 0x6E, 0x8C)

def tint(c, k=0.90):
    """把颜色调浅，用作底色。"""
    r, g, b = c[0], c[1], c[2]
    return RGBColor(int(r + (255 - r) * k), int(g + (255 - g) * k), int(b + (255 - b) * k))

def set_font(run, size, bold=False, color=INK, name=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', name)

def tbox(s, x, y, w, h, text, size=12, bold=False, color=INK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.15):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run(); r.text = ln
        set_font(r, size, bold, color)
    return tb

def rect(s, x, y, w, h, fill=None, line=None, radius=0.06, lw=1.0):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                            Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    if radius:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    return sh

def chip(s, x, y, w, text, color, size=10.5, h=0.30):
    rect(s, x, y, w, h, fill=tint(color, 0.88), line=tint(color, 0.55), radius=0.5)
    tbox(s, x + 0.10, y + 0.035, w - 0.2, h - 0.06, text, size, True, color, PP_ALIGN.CENTER)

def arrow_right(s, x, y, w=0.30, h=0.24, color=None):
    sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.rotation = 90
    sh.fill.solid(); sh.fill.fore_color.rgb = color or LINE
    sh.line.fill.background(); sh.shadow.inherit = False
    return sh

def arrow_down(s, x, y, w=0.24, h=0.26, color=None):
    sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.rotation = 180
    sh.fill.solid(); sh.fill.fore_color.rgb = color or LINE
    sh.line.fill.background(); sh.shadow.inherit = False
    return sh

def box(s, x, y, w, h, text, color=None, size=10.5, bold=False, fill=None, dashed=False):
    c = color or LINE
    b = rect(s, x, y, w, h, fill=fill if fill else WHITE, line=c, radius=0.08, lw=1.2)
    if dashed:
        b.line.dash_style = 4
    tbox(s, x + 0.06, y, w - 0.12, h, text, size, bold, INK, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE, 1.05)
    return b

def bullet_block(s, x, y, w, items, size=12, gap=0.40, color=INK, marker_color=None, w_gap=None):
    yy = y
    for it in items:
        rect(s, x, yy + 0.11, 0.075, 0.075, fill=marker_color or DIM, radius=0.5)
        tbox(s, x + 0.20, yy - 0.02, w - 0.2, gap, it, size, False, color, spacing=1.2)
        yy += gap
    return yy

# ---------------------------------------------------------------- 页框架
def page(prs, color):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, 13.333, 7.5, fill=PAPER, radius=0)
    return s

def header(s, kicker, title, color, sub=None):
    rect(s, 0, 0, 0.16, 7.5, fill=color, radius=0)
    tbox(s, 0.62, 0.42, 8.0, 0.28, kicker, 10.5, True, color)
    tbox(s, 0.60, 0.74, 11.9, 0.66, title, 23, True, INK, spacing=1.05)
    if sub:
        tbox(s, 0.62, 1.38, 11.9, 0.34, sub, 11.5, False, DIM)
    rect(s, 0.60, 1.80 if sub else 1.52, 12.13, 0.012, fill=LINE, radius=0)

def foot(s, note, question, color, pageno):
    y = 6.42
    rect(s, 0.60, y, 6.35, 0.66, fill=tint(color, 0.94), line=tint(color, 0.72), radius=0.10)
    tbox(s, 0.76, y + 0.07, 6.03, 0.52, note, 11, False, INK, spacing=1.1)
    rect(s, 6.95, y, 5.78, 0.66, fill=RGBColor(0xF7, 0xF9, 0xFC), line=LINE, radius=0.10)
    tbox(s, 7.11, y + 0.07, 5.46, 0.52, question, 11, False, DIM, spacing=1.1)
    tbox(s, 12.30, 7.14, 0.55, 0.24, str(pageno), 9, False, FAINT, PP_ALIGN.RIGHT)

def divider(prs, num, title, sub, color, pageno):
    s = page(prs, color)
    rect(s, 0, 0, 13.333, 7.5, fill=color, radius=0)
    tbox(s, 1.05, 2.15, 2.6, 1.4, num, 76, True, RGBColor(0xFF, 0xFF, 0xFF))
    tbox(s, 3.45, 2.55, 8.6, 0.8, title, 32, True, RGBColor(0xFF, 0xFF, 0xFF))
    tbox(s, 3.52, 3.48, 8.2, 0.8, sub, 14, False, RGBColor(0xEE, 0xF4, 0xFA), spacing=1.3)
    tbox(s, 12.30, 7.14, 0.55, 0.24, str(pageno), 9, False, RGBColor(0xEE, 0xF4, 0xFA), PP_ALIGN.RIGHT)

def cover(prs):
    s = page(prs, BLUE)
    rect(s, 0, 0, 13.333, 7.5, fill=RGBColor(0x0E, 0x13, 0x1A), radius=0)
    rect(s, 0.95, 2.05, 0.10, 2.0, fill=BLUE, radius=0)
    tbox(s, 1.30, 1.98, 10.4, 0.9, "AgentENV 沙箱全课复习", 40, True, RGBColor(0xED, 0xF2, 0xF8))
    tbox(s, 1.34, 2.92, 10.4, 0.5, "20 讲 · 三个执行环境 · 一条完整链路", 17, False, RGBColor(0x9F, 0xAE, 0xBE))
    tbox(s, 1.34, 3.86, 10.4, 0.9,
         "每一页 = 一张图 + 一段解释 + 一个易错点 + 一个面试问法\n读完应该能自己把这张图画出来，而不是背句子",
         12.5, False, RGBColor(0x76, 0x87, 0x99), spacing=1.5)
    tbox(s, 1.34, 6.35, 11.0, 0.4,
         "基线 9f62cbe07cebfecf416dc9bdcf497e2a97687644   ·   整理 2026-11-13   ·   未实测处已标注", 10.5, False, RGBColor(0x60, 0x70, 0x82))

def build(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    pn = [0]
    def nxt():
        pn[0] += 1
        return pn[0]

    cover(prs); nxt()

    # ---------- 0. 用法 ----------
    s = page(prs, TEAL); header(s, "怎么用", "三种复习法，按你要花的时间选", TEAL,
                              "这份 PPT 的目标不是让你读完，而是让你合上之后能自己画出来。")
    cards = [
        ("20 分钟 · 扫", "只看每页的大标题和左侧那张图。标题就是结论，图就是机制的骨架。适合考前一晚。"),
        ("1 小时 · 讲", "每页只看「会被问」，口头答一遍。答不出来的地方翻回对应课程笔记，不要凭印象补。"),
        ("半天 · 画", "白纸画三张图：系统全景、一次 4 KiB 读的全链路、快照四件套。画不出的位置就是你的缺口。"),
    ]
    x = 0.60
    for t, d in cards:
        rect(s, x, 2.05, 3.95, 3.15, fill=WHITE, line=LINE, radius=0.05)
        rect(s, x, 2.05, 3.95, 0.06, fill=TEAL, radius=0)
        tbox(s, x + 0.26, 2.30, 3.4, 0.4, t, 15, True, INK)
        tbox(s, x + 0.26, 2.82, 3.42, 2.1, d, 11.5, False, DIM, spacing=1.55)
        x += 4.13
    tbox(s, 0.62, 5.52, 12.1, 0.7,
         "共同的判断标准：不是「我记得这个名词」，而是「换一个条件我还能预测结果」。",
         12.5, True, TEAL)
    foot(s, "把「讲过」当「掌握」是复习里最大的浪费。材料齐不等于你会。",
         "合上这份 PPT，你能默画出几张图？", TEAL, nxt())

    # ---------- 1. 全景 ----------
    s = page(prs, BLUE); header(s, "全景 · 第 0 课", "三个执行环境：所有内容都挂在这三层上", BLUE,
                               "同一个内核、三个视角。分不清这三层，后面每一个问题都会答错位置。")
    # 三个横向大带
    bands = [
        ("宿主用户态（3 个独立进程）", 2.02, [
            ("AgentENV server", "生命周期 / 快照 / 控制"),
            ("Firecracker", "VMM：vCPU 线程 + 设备模型"),
            ("ublk-daemon", "块设备服务（集中式）"),
        ]),
        ("宿主内核（同一台机器的内核）", 3.62, [
            ("KVM", "跑 vCPU、维护 EPT"),
            ("ublk 驱动", "/dev/ublkbN 请求队列"),
            ("cgroup · seccomp", "约束 VMM 的用量与 syscall"),
        ]),
        ("Guest（一台虚拟机内部）", 5.22, [
            ("Guest 内核", "自己的页表与进程表"),
            ("envd", "执行命令、回传结果"),
            ("你的程序", "PID 由 Guest 内核分配"),
        ]),
    ]
    for name, y, items in bands:
        tbox(s, 0.62, y - 0.30, 6.0, 0.26, name, 10.5, True, DIM)
        xx = 0.62
        for t, d in items:
            rect(s, xx, y, 3.95, 0.84, fill=WHITE, line=LINE, radius=0.06)
            rect(s, xx, y, 0.05, 0.84, fill=BLUE, radius=0)
            tbox(s, xx + 0.18, y + 0.13, 3.6, 0.3, t, 12, True, INK)
            tbox(s, xx + 0.18, y + 0.44, 3.65, 0.32, d, 10.5, False, DIM)
            xx += 4.13
    tbox(s, 0.62, 6.06, 6.4, 0.3, "关键：Guest 程序不是 Firecracker 的子进程，宿主 ps 看不到。", 11.5, True, BLUE)
    foot(s, "把 server 里的 Rust 对象当成进程；把宿主 PID 当成 Guest PID。",
         "宿主上执行 ps -eLf，能看到哪些？看不到哪些？", BLUE, nxt())

    # ---------- 2. 四把尺子 ----------
    s = page(prs, BLUE); header(s, "全景 · 第 0 课", "一个变量有四个地址：取决于谁在看", BLUE,
                               "同一个 4 KiB 物理页，Guest 和 Firecracker 各用自己的一套地址去碰它。")
    # 中央物理页
    rect(s, 5.35, 3.10, 2.6, 1.0, fill=tint(BLUE, 0.86), line=BLUE, radius=0.06)
    tbox(s, 5.42, 3.28, 2.46, 0.66, "宿主物理页 HPA\n这里是真正的内存条", 10.5, True, BLUE, PP_ALIGN.CENTER)
    # 左路径
    box(s, 0.62, 2.05, 2.2, 0.62, "Guest 程序用 GVA", BLUE)
    box(s, 0.62, 3.25, 2.2, 0.62, "Guest 内核认 GPA", BLUE)
    arrow_down(s, 1.58, 2.72, 0.22, 0.40, BLUE)
    arrow_down(s, 1.58, 3.92, 0.22, 0.40, BLUE)
    tbox(s, 0.50, 3.96, 1.0, 0.3, "Guest 页表", 9, False, DIM)
    # 右路径
    box(s, 10.55, 2.05, 2.2, 0.62, "Firecracker HVA", PURPLE)
    box(s, 10.55, 3.25, 2.2, 0.62, "宿主页表翻译", PURPLE)
    arrow_down(s, 11.50, 2.72, 0.22, 0.40, PURPLE)
    arrow_down(s, 11.50, 3.92, 0.22, 0.40, PURPLE)
    # 汇合标注
    tbox(s, 3.05, 3.36, 2.1, 0.7, "经 EPT 二级翻译\n（GPA → HPA）", 9.5, False, DIM, PP_ALIGN.RIGHT, spacing=1.2)
    tbox(s, 8.35, 3.36, 2.0, 0.7, "一步翻译\n（HVA → HPA）", 9.5, False, DIM, PP_ALIGN.LEFT, spacing=1.2)
    tbox(s, 0.62, 4.62, 5.6, 0.3, "Guest 访存：GVA → GPA → HPA（硬件直接完成）", 11.5, True, BLUE)
    tbox(s, 7.3, 4.62, 5.5, 0.3, "Firecracker 访存：HVA → HPA（宿主页表）", 11.5, True, PURPLE)
    tbox(s, 0.62, 5.10, 12.1, 1.1,
         "memslot 就是这两条路径的接线处：VMM 用 KVM_SET_USER_MEMORY_REGION 登记「某段 GPA 对应我这段 HVA」。\n"
         "所以调用者只填 GPA 起点、HVA 起点、长度——不需要也不应该填 HPA，物理页由宿主内核按需准备。",
         11.5, False, INK, spacing=1.35)
    foot(s, "以为 Guest 访存会经过 HVA；以为 ioctl 登记时把整份 RAM 复制了一遍。",
         "为什么登记 128 MiB 不需要提供 HPA？页面还没驻留时谁负责？", BLUE, nxt())

    # ---------- 3. 三条边界 ----------
    s = page(prs, BLUE); header(s, "全景 · 第 0 课", "三个动作经常被混成一个", BLUE,
                               "调 ioctl、VM-Exit、宿主线程切换——发生的位置和后果都不同。")
    rows = [
        ("KVM_RUN 系统调用", "Firecracker 用户态 → 宿主内核", "否", "线程还在跑，只是换了特权级"),
        ("VM-Entry / VM-Exit", "Guest 与宿主执行环境切换", "否", "仍在同一个宿主线程内，由 KVM 处理"),
        ("宿主线程切换", "调度器让 CPU 去跑别的线程", "是", "这才叫「没拿到 CPU」"),
    ]
    y = 2.02
    for i, (a, b, c, d) in enumerate(rows):
        fill = WHITE if i % 2 == 0 else SOFT
        rect(s, 0.60, y, 12.13, 0.92, fill=fill, line=LINE, radius=0.05)
        tbox(s, 0.82, y + 0.12, 3.3, 0.3, a, 12.5, True, INK)
        tbox(s, 0.82, y + 0.48, 4.4, 0.3, b, 10.5, False, DIM)
        tbox(s, 5.55, y + 0.14, 1.6, 0.3, "必切线程：" + c, 11, True, ORANGE if c == "是" else GREEN)
        tbox(s, 7.35, y + 0.14, 5.2, 0.6, d, 10.5, False, DIM, spacing=1.2)
        y += 1.00
    tbox(s, 0.62, 5.10, 12.1, 1.2,
         "最实用的一条推论：VM-Exit 回到宿主内核，不等于 KVM_RUN 已经返回用户态。\n"
         "KVM 能自己处理的退出（例如补一条 EPT 映射）会处理完直接重入 Guest，整个 ioctl 从头到尾没返回过。\n"
         "只有它处理不了、需要用户态模拟的事（比如 MMIO），才会让 KVM_RUN 返回，Firecracker 才被唤醒。",
         11.5, False, INK, spacing=1.4)
    foot(s, "把 VM-Exit 当成 KVM_RUN 返回；把「两个 vCPU」当成「永久独占两个物理核」。",
         "一次 EPT 缺页退出，一定会让 Firecracker 从 ioctl 返回吗？", BLUE, nxt())

    # ---------- 章节 01 ----------
    divider(prs, "01", "位置与地址", "第 1—3 课：谁在哪里跑，指针属于谁，两条访存路径怎么汇合", BLUE, nxt())

    # 第 1 课
    s = page(prs, BLUE); header(s, "第 1 课", "一个 Firecracker 进程，内部有多个线程", BLUE,
                               "「进程」和「线程」在这里不是细节，它直接决定你怎么读 ps 的输出。")
    # 左图：进程与线程
    rect(s, 0.60, 2.00, 6.10, 3.95, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 0.80, 2.14, 5.4, 0.3, "宿主进程：firecracker（PID 由宿主内核分配）", 10.5, True, DIM)
    box(s, 0.82, 2.55, 2.55, 0.62, "vmm 主线程", BLUE)
    box(s, 0.82, 3.32, 2.55, 0.62, "api 线程（Unix socket）", BLUE)
    box(s, 0.82, 4.09, 2.55, 0.62, "fc_vcpu 0（KVM_RUN）", BLUE)
    box(s, 0.82, 4.86, 2.55, 0.62, "fc_vcpu 1（KVM_RUN）", BLUE)
    tbox(s, 3.60, 2.55, 2.9, 2.9,
         "线程名不是自动来的：\n代码里 .name(\"fc_vcpu {index}\")\n写死了，所以 ps -eLf\n才看得到这个名字。",
         10.5, False, DIM, spacing=1.35)
    bullet_block(s, 6.95, 2.05, 5.75, [
        "Firecracker 是宿主用户态进程；它借 KVM 运行 Guest，本身不在 Guest 里。",
        "一个 vCPU 对应一个宿主线程：配 2 个 vCPU，宿主就多两个线程。",
        "Guest 里的程序由 Guest 内核调度，不占宿主的进程表。",
        "server 里的 FirecrackerInstance 只是句柄对象，不是第二个进程。",
    ], 11.5, 0.78)
    foot(s, "把宿主看到的 Firecracker PID 当成 Guest 里 python 的 PID；把 Rust 结构体当成进程。",
         "宿主 ps 能看到 Guest 里的 python 吗？它的 PID 由谁分配？", BLUE, nxt())

    # 第 2 课
    s = page(prs, BLUE); header(s, "第 2 课", "地址离开地址空间就没有意义", BLUE,
                               "同一个数字 0x400000，在 server 里和 Firecracker 里指向两块不同的物理页。")
    rect(s, 0.60, 2.00, 6.10, 2.55, fill=WHITE, line=LINE, radius=0.05)
    box(s, 0.85, 2.22, 2.5, 0.58, "server 的 0x400000", ORANGE)
    box(s, 0.85, 3.10, 2.5, 0.58, "Firecracker 的 0x400000", PURPLE)
    box(s, 3.95, 2.22, 2.4, 0.58, "物理页 P_A：SERVER", ORANGE)
    box(s, 3.95, 3.10, 2.4, 0.58, "物理页 P_B：GUEST", PURPLE)
    arrow_right(s, 3.55, 2.39, 0.30, 0.24, ORANGE)
    arrow_right(s, 3.55, 3.27, 0.30, 0.24, PURPLE)
    tbox(s, 0.85, 3.95, 5.5, 0.4, "两个进程各自的页表，把同一个数字翻译到不同物理页", 10.5, False, DIM)
    # 右侧对比
    rect(s, 6.95, 2.00, 5.75, 1.30, fill=tint(ORANGE, 0.93), line=tint(ORANGE, 0.7), radius=0.05)
    tbox(s, 7.15, 2.12, 5.4, 0.9,
         "pwrite(fd, buf, len, off)\n只有调用者地址空间：buf 永远是「我自己的」内存",
         11, False, INK, spacing=1.35)
    rect(s, 6.95, 3.42, 5.75, 1.60, fill=tint(PURPLE, 0.93), line=tint(PURPLE, 0.7), radius=0.05)
    tbox(s, 7.15, 3.54, 5.4, 1.3,
         "process_vm_readv(pid, local_iov, remote_iov)\npid 决定用谁的地址空间；remote 说从哪取，local 说放哪",
         11, False, INK, spacing=1.35)
    tbox(s, 0.62, 5.05, 12.1, 1.25,
         "三个动作必须分开看：① 创建 iovec 描述（不复制数据）② 跨进程读取（内核复制一次）③ 写文件（pwrite 或 writer）。\n"
         "很多人把「描述」当成「复制」，于是以为 process_vm_readv 之前就已经把 Guest 内存搬到 server 了。\n"
         "还有一个细节：两个 iovec 数组本身都在调用者内存里，只有 remote_iov 里的地址指向目标进程。",
         11.5, False, INK, spacing=1.4)
    foot(s, "以为内核会自动按被读进程解释地址；把 remote_iov 的参数指针误填成目标进程地址。",
         "读 Guest 内存时，remote address 填 GVA、GPA 还是 HVA？", BLUE, nxt())

    # 第 3 课
    s = page(prs, BLUE); header(s, "第 3 课", "memslot 是这两条路径的接线处", BLUE,
                               "登记的是「范围对应关系」，不是把 128 MiB 复制一份。")
    # 流程
    steps = [
        ("Firecracker mmap 匿名内存", "得到 HVA 0x70000000"),
        ("ioctl 登记内存区域", "KVM_SET_USER_MEMORY_REGION"),
        ("KVM 记录 memslot", "软件关系：GPA → HVA"),
        ("Guest 访存触发缺项", "KVM 算出 HVA，取到真实页"),
        ("建立 EPT 项", "GPA → HPA，硬件翻译"),
    ]
    y = 2.05
    for i, (t, d) in enumerate(steps):
        rect(s, 0.62, y, 4.35, 0.66, fill=WHITE, line=BLUE if i >= 3 else LINE, radius=0.06)
        tbox(s, 0.78, y + 0.06, 4.05, 0.26, t, 10.5, True, INK)
        tbox(s, 0.78, y + 0.36, 4.05, 0.24, d, 8.5, False, DIM)
        if i < 4:
            arrow_down(s, 2.68, y + 0.68, 0.20, 0.22, LINE)
        y += 0.90
    # 右侧解释
    rect(s, 5.35, 2.05, 7.35, 3.55, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 5.62, 2.18, 6.9, 3.3,
         "为什么不需要填 HPA\n"
         "用户态进程碰不到物理地址，只能交出自己的 HVA；是宿主内核查宿主页表，\n"
         "把 HVA 翻成 HPA，再去填 EPT。所以 ioctl 的参数里根本没有 HPA 这一项。\n\n"
         "为什么不是一次性建完 EPT\n"
         "登记时只记录范围；真正用到某页时缺项，才由 KVM 现取页、现建项。\n"
         "这也是「登记不等于复制」的原因：那 128 MiB 的内容一直只有一份。\n\n"
         "算一个偏移（面试常考）\n"
         "HVA = userspace_addr + (目标 GPA − guest_phys_addr)\n"
         "= 0x70000000 + (0x2000 − 0) = 0x70002000",
         11, False, INK, spacing=1.35)
    foot(s, "以为 Guest 正常访存会经过 HVA；以为 memslot 就是 EPT 表本身。",
         "memslot 与 EPT 分别是什么、各自存在哪里？", BLUE, nxt())

    # ---------- 章节 02 ----------
    divider(prs, "02", "执行与设备", "第 4—6 课：谁在跑指令，暂停怎么确认，请求怎么传", PURPLE, nxt())

    # 第 4 课
    s = page(prs, PURPLE); header(s, "第 4 课", "本质是一个 ioctl(KVM_RUN) 的循环", PURPLE,
                               "vCPU 线程进去，硬件跑 Guest；撞到退出条件回来，处理完再进去。")
    # 循环图
    box(s, 0.62, 2.10, 3.0, 0.72, "vCPU 线程调用\nioctl(KVM_RUN)", PURPLE)
    box(s, 4.35, 2.10, 3.0, 0.72, "硬件进非根模式\n执行 Guest 指令", PURPLE)
    box(s, 8.08, 2.10, 3.0, 0.72, "撞到退出条件\nVM-Exit 回到 KVM", PURPLE)
    arrow_right(s, 3.70, 2.34, 0.34, 0.26, PURPLE)
    arrow_right(s, 7.43, 2.34, 0.34, 0.26, PURPLE)
    # 分叉
    box(s, 8.08, 3.30, 3.0, 0.72, "KVM 自己能处理\n→ 直接重入，ioctl 未返回", GREEN)
    box(s, 4.35, 3.30, 3.0, 0.72, "需要用户态模拟\n→ KVM_RUN 返回 Firecracker", ORANGE)
    arrow_down(s, 9.46, 2.88, 0.22, 0.36, GREEN)
    arrow_down(s, 5.68, 2.88, 0.22, 0.36, ORANGE)
    box(s, 0.62, 3.30, 3.0, 0.72, "MMIO / PIO 退出\n交给设备模型", ORANGE)
    arrow_right(s, 3.70, 3.54, 0.34, 0.26, ORANGE)
    tbox(s, 0.62, 4.22, 12.1, 1.9,
         "三条容易混的边界：KVM_RUN 系统调用（用户态→内核）、VM-Exit（Guest→宿主执行环境）、宿主线程切换（调度器换线程）。\n"
         "只有第三种才是「这个线程没拿到 CPU」。前两种都在同一个线程里完成。\n\n"
         "所以「VM-Exit 频繁」不等于「Firecracker 被唤醒频繁」：补一条 EPT 映射这类退出，KVM 自己就办完了，\n"
         "用户态完全无感。真正把控制权交回用户态的，是它办不了的事——比如 MMIO。",
         11.5, False, INK, spacing=1.4)
    foot(s, "把「VM-Exit 回到宿主内核」当成「KVM_RUN 已返回」；以为每条指令或每次系统调用都要退出。",
         "哪些退出 KVM 自己处理，哪些必须回到用户态？", PURPLE, nxt())

    # 第 5 课
    s = page(prs, PURPLE); header(s, "第 5 课", "「没被调度」不是「已暂停」", PURPLE,
                               "这是暂停这一课唯一真正难的点，也是面试最爱追的点。")
    # 时间线
    tbox(s, 0.62, 2.02, 1.2, 0.3, "时间 →", 10, False, DIM)
    events = [
        ("t1", "API 线程收到 PATCH /vm\nstate=Paused", GREEN),
        ("t2", "VMM 线程置暂停意图\n请求各 vCPU 退出", GREEN),
        ("t3", "vCPU0 从 KVM_RUN 返回\n进入等待：已暂停", GREEN),
        ("t4", "vCPU1 没被调度\n注意：这不是暂停", ORANGE),
        ("t5", "vCPU1 被调度后才\n处理退出要求", GREEN),
        ("t6", "两个都确认\n暂停才完成", BLUE),
    ]
    x = 0.62
    for i, (t, d, c) in enumerate(events):
        rect(s, x, 2.34, 1.92, 1.22, fill=WHITE, line=c, radius=0.06)
        tbox(s, x + 0.10, 2.42, 1.72, 0.26, t, 10.5, True, c)
        tbox(s, x + 0.10, 2.70, 1.74, 0.8, d, 9.5, False, INK, spacing=1.15)
        x += 2.04
    tbox(s, 0.62, 3.72, 12.1, 0.4,
         "t4 是关键：vCPU1 只是「没有拿到 CPU」，只要调度器再给它时间片，它会继续执行 Guest 指令。",
         11.5, True, ORANGE)
    bullet_block(s, 0.62, 4.28, 5.9, [
        "暂停一个 vCPU ≠ VM 已暂停：另一个还在写同一块 Guest RAM。",
        "暂停请求发出 ≠ Firecracker 收到 ≠ 全部 vCPU 确认，三段各自检查。",
        "暂停完成 ≠ 快照完成：后面还要读内存、写层、落盘。",
    ], 11.5, 0.62, INK, PURPLE)
    rect(s, 6.95, 4.24, 5.78, 1.85, fill=tint(PURPLE, 0.94), line=tint(PURPLE, 0.72), radius=0.06)
    tbox(s, 7.15, 4.36, 5.4, 1.6,
         "顺带一个高频结论\n"
         "宿主设备写 Guest RAM 不需要 vCPU 执行（两个线程写同一块物理页）；\n"
         "但 Guest 驱动要处理这批数据，仍然需要 vCPU 运行。",
         10.5, False, INK, spacing=1.35)
    foot(s, "把「暂停请求发出」当成「VM 已停」；把暂停完成当成快照已保存。",
         "为什么暂停控制不能走 virtqueue，必须走宿主 socket？", PURPLE, nxt())

    # 第 6 课
    s = page(prs, PURPLE); header(s, "第 6 课", "VirtIO：队列在内存里，通知只负责提醒", PURPLE,
                               "设备不是「收到一个包」，而是「去共享队列里取一条描述」——这是它快的根本原因。")
    # 三件套
    rect(s, 0.62, 2.02, 4.0, 3.5, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 0.82, 2.14, 3.6, 0.3, "① 描述符表（16 字节/项）", 10.5, True, PURPLE)
    tbox(s, 0.82, 2.50, 3.6, 2.9,
         "addr  缓冲区在哪（GPA）\nlen   多长\nflags WRITE / NEXT\nnext  下一个描述符下标\n\n"
         "可以串成链，描述多块不连续缓冲区；\n描述符本身不复制任何字节。",
         10.5, False, INK, spacing=1.45)
    rect(s, 4.78, 2.02, 3.8, 1.66, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 4.98, 2.14, 3.4, 0.3, "② 可用环 avail（Guest 写）", 10.5, True, GREEN)
    tbox(s, 4.98, 2.50, 3.45, 1.1, "把「链头编号」发布出去，\n表示这批缓冲区可以给设备用了。", 10.5, False, INK, spacing=1.3)
    rect(s, 4.78, 3.84, 3.8, 1.68, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 4.98, 3.96, 3.4, 0.3, "③ 已用环 used（设备写）", 10.5, True, ORANGE)
    tbox(s, 4.98, 4.32, 3.45, 1.1, "发布完成项与写入长度，\nGuest 驱动处理完才会再次发布。", 10.5, False, INK, spacing=1.3)
    rect(s, 8.78, 2.02, 3.95, 3.5, fill=tint(PURPLE, 0.94), line=tint(PURPLE, 0.72), radius=0.05)
    tbox(s, 8.98, 2.14, 3.6, 3.2,
         "通知（doorbell）\n"
         "只是「去检查队列」的提醒：\n"
         "· 不携带包内容\n"
         "· 一次通知可以对应多项工作\n"
         "· Guest 未处理完就交回缓冲区，设备可能覆盖\n\n"
         "所以：通知次数 ≠ 请求数。\n"
         "多包一批时，只有一次门铃。",
         10.5, False, INK, spacing=1.4)
    tbox(s, 0.62, 5.68, 12.1, 0.6,
         "为什么快：模拟真实设备时，每个寄存器访问都是一次 VM-Exit；VirtIO 把数据放在共享内存里批量搬，只在「有活」时敲一次门铃。",
         11.5, True, PURPLE)
    foot(s, "把「设备发布 used」当成「Guest 驱动已处理」；把通知次数当成请求数。",
         "VirtIO 相比模拟真实设备，省掉的到底是什么？", PURPLE, nxt())

    # ---------- 章节 03 ----------
    divider(prs, "03", "控制与命令", "第 7—9 课：请求从哪进，就绪怎么判，命令结果怎么回来", GREEN, nxt())

    # 第 7 课
    s = page(prs, GREEN); header(s, "第 7 课", "两条完全不同的通道", GREEN,
                               "控制面走宿主 Unix socket，数据面走 Guest 内存里的队列。混了就会把暂停讲成设备请求。")
    rect(s, 0.62, 2.02, 5.95, 1.42, fill=tint(GREEN, 0.93), line=tint(GREEN, 0.7), radius=0.06)
    tbox(s, 0.82, 2.14, 5.5, 1.2,
         "控制面\n载体：宿主 Unix socket（--api-sock）\n格式：Firecracker REST（PATCH /vm, state=Paused）",
         10.5, False, INK, spacing=1.35)
    rect(s, 6.80, 2.02, 5.93, 1.42, fill=tint(ORANGE, 0.93), line=tint(ORANGE, 0.7), radius=0.06)
    tbox(s, 7.00, 2.14, 5.5, 1.2,
         "数据面\n载体：Guest RAM 里的 virtqueue + 通知\n格式：描述符 / avail / used 环",
         10.5, False, INK, spacing=1.35)
    tbox(s, 0.62, 3.62, 12.1, 2.2,
         "为什么暂停不能走数据面：暂停的用途之一，就是「Guest 不配合时也能把 VM 停住」。\n"
         "如果停机依赖 Guest 驱动去处理队列，那么 Guest 内核或驱动卡住时，宿主就永远停不下来。\n\n"
         "HTTP 只是消息格式：它跑在 Unix socket 上，不走 TCP、不经过 Guest 网卡。\n"
         "最常见的误读是把 socket 当成网络，然后推理出「暂停要经过 Guest 网络栈」。\n\n"
         "请求之后的三个结果要分开：已发出 / 收到成功响应 / 全部 vCPU 确认。超时也有三种可能：\n"
         "没送到、送成了但响应丢了、还在做。所以「超时」不能直接推出「VM 还在正常跑」。",
         11.5, False, INK, spacing=1.45)
    foot(s, "把 pause() 这个函数名当成「进入 Guest 执行」；把 socket 当成网络连接。",
         "一条暂停请求超时了，你能得出什么结论、不能得出什么？", GREEN, nxt())

    # 第 8 课
    s = page(prs, GREEN); header(s, "第 8 课", "三层就绪，逐层收紧", GREEN,
                               "「进程在」→「网络通」→「应用能应答」，每层只能证明自己那一层。")
    steps = [
        ("① API socket 可用", "能配 VM、能 pause", "VMM 起来了、socket 路径对", GREEN),
        ("② 网络可达", "宿主经 tap0 能到 Guest", "netns、网卡、IP、端口都对", GREEN),
        ("③ envd 应用层", "GET /health 返回非 4xx/5xx", "服务真能应答，不只是监听", BLUE),
    ]
    y = 2.02
    for i, (t, d, e, c) in enumerate(steps):
        w = 7.4 + i * 0.0
        rect(s, 0.62, y, w, 0.86, fill=WHITE, line=c, radius=0.06)
        tbox(s, 0.82, y + 0.10, 3.1, 0.3, t, 12, True, INK)
        tbox(s, 0.82, y + 0.46, 3.4, 0.3, d, 10, False, DIM)
        tbox(s, 4.35, y + 0.24, 3.5, 0.4, "能证明：" + e, 9.5, False, DIM)
        y += 0.98
    rect(s, 8.30, 2.02, 4.43, 2.72, fill=tint(GREEN, 0.94), line=tint(GREEN, 0.72), radius=0.06)
    tbox(s, 8.50, 2.14, 4.05, 2.5,
         "健康检查的实际行为\n"
         "· GET {base}/health\n"
         "· 判定：状态码不是 4xx/5xx 即通过\n"
         "  （不校验响应体，204 也算过）\n"
         "· 单次上限 1 秒，失败继续重试\n"
         "· 整体期限耗尽才报超时",
         10, False, INK, spacing=1.35)
    tbox(s, 0.62, 4.95, 12.1, 1.2,
         "start_nowait() 只等 API socket；wait_for_ready() 才等 envd。这就是为什么它被拆成两个接口：\n"
         "调用方可以先把别的事做完（比如准备磁盘），最后再统一等 envd 就绪。\n"
         "另一个坑：对象创建、端口能连、health 通过，是三件强度完全不同的事。",
         11.5, False, INK, spacing=1.4)
    foot(s, "把「envd 客户端对象创建成功」当成「Guest 服务就绪」；把 health 通过当成鉴权通过。",
         "端口能连却不能执行命令，问题可能在哪一层？", GREEN, nxt())

    # 第 9 课
    s = page(prs, GREEN); header(s, "第 9 课", "Start 不代表成功，wait 返回 Ok 也不代表", GREEN,
                               "一次 exec 只有三类事件，但「成功」需要同时满足三个条件。")
    # 事件流
    xs = [0.62, 3.35, 6.08, 8.81]
    labels = [("start 请求", "cmd + args + env + cwd", GREEN),
              ("Start{pid}", "进程已创建", GREEN),
              ("Data{...}", "stdout / stderr 分段", GREEN),
              ("End{code}", "进程已退出", BLUE)]
    for i, (t, d, c) in enumerate(labels):
        rect(s, xs[i], 2.05, 2.5, 0.82, fill=WHITE, line=c, radius=0.06)
        tbox(s, xs[i] + 0.12, 2.13, 2.26, 0.3, t, 11, True, INK)
        tbox(s, xs[i] + 0.12, 2.46, 2.26, 0.3, d, 9.5, False, DIM)
        if i < 3:
            arrow_right(s, xs[i] + 2.55, 2.30, 0.22, 0.22, LINE)
    rect(s, 8.50, 1.98, 1.40, 0.24, fill=tint(BLUE, 0.8), line=None, radius=0.5)
    tbox(s, 8.60, 2.00, 1.2, 0.22, "可选项", 9, True, BLUE, PP_ALIGN.CENTER)
    # 右侧判断
    rect(s, 0.62, 3.15, 6.0, 1.6, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 0.82, 3.27, 5.6, 1.35,
         "两个独立判断\n"
         "① 事件收齐了吗？→ 协议层 Ok / Err（没收到 End 就是错误）\n"
         "② exit_code 是多少？→ 程序层 0 / 非零",
         10.5, False, INK, spacing=1.35)
    rect(s, 6.85, 3.15, 5.88, 1.6, fill=tint(GREEN, 0.94), line=tint(GREEN, 0.72), radius=0.05)
    tbox(s, 7.05, 3.27, 5.5, 1.35,
         "所以判断成功要三样同时满足\n"
         "wait 返回 Ok + 收到 End + exit_code 符合预期\n"
         "只有 Start，说明「进程被创建出来了」而已。",
         10.5, False, INK, spacing=1.35)
    tbox(s, 0.62, 4.98, 12.1, 1.2,
         "还有两个边界：命令与参数分开传，不假设有 shell（没有管道、通配符、重定向语义）；\n"
         "以及可执行文件都起不来时，可能直接返回启动错误——不一定先有 Start 再有 End。",
         11.5, False, INK, spacing=1.4)
    foot(s, "看到 Start 就当命令成功；只看 exit_code 不看流是否收齐。",
         "超时后发终止请求失败，能不能断言进程已退出？为什么？", GREEN, nxt())

    # ---------- 章节 04 ----------
    divider(prs, "04", "存储", "第 10—12 课：文件怎么变成块读写，分层怎么查，谁来回答「这块是什么」", ORANGE, nxt())

    # 第 10 课
    s = page(prs, ORANGE); header(s, "第 10 课", "一条数据在三个坐标系里换名", ORANGE,
                               "文件偏移、逻辑块号、后端实际位置——面试里只写一个数字会被追着问单位。")
    # 三段换算
    box(s, 0.62, 2.05, 3.35, 0.86, "Guest 应用\nread(fd, buf, 4096)\n文件偏移 8 MiB", ORANGE)
    box(s, 4.60, 2.05, 3.35, 0.86, "Guest ext4\n偏移 → extent → LBA\nLBA = 0x4000（假设）", ORANGE)
    box(s, 8.58, 2.05, 4.15, 0.86, "宿主后端\n层文件里的某段字节\n或远端对象", ORANGE)
    arrow_right(s, 4.06, 2.34, 0.36, 0.26, ORANGE)
    arrow_right(s, 8.04, 2.34, 0.36, 0.26, ORANGE)
    tbox(s, 0.62, 3.05, 3.35, 0.3, "文件偏移：文件系统语义", 9.5, False, DIM, PP_ALIGN.CENTER)
    tbox(s, 4.60, 3.05, 3.35, 0.3, "LBA：块设备语义（要带单位）", 9.5, False, DIM, PP_ALIGN.CENTER)
    tbox(s, 8.58, 3.05, 4.15, 0.3, "后端位置：宿主才知道", 9.5, False, DIM, PP_ALIGN.CENTER)
    tbox(s, 0.62, 3.55, 12.1, 2.55,
         "三个不能省的前提：\n"
         "· 页缓存命中时，这次 read 可能根本不产生设备 IO；但路径解析、元数据仍可能产生 IO。\n"
         "· 块设备不认文件名：a.txt 只存在于 Guest 文件系统的语义里，到块层只剩「第几块、多长」。\n"
         "· 文件内连续的数据，在磁盘上可以是不连续的：ext4 的 extent 允许映射到任意 LBA。\n\n"
         "写路径的结论更实用：write 返回只代表数据进了页缓存，不等于落盘；要持久化得靠 fsync / flush / 预同步。\n"
         "这也是为什么「快照前要不要同步文件系统」本身就是一个真实的设计问题。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为文件偏移 0 就是磁盘偏移 0；以为 write 返回＝数据已经持久化。",
         "一次 4 KiB 读，实际可能从盘上读多少字节？为什么可能更少或更多？", ORANGE, nxt())

    # 第 11 课
    s = page(prs, ORANGE); header(s, "第 11 课", "分层是覆盖映射，不是把文件拼起来", ORANGE,
                               "每层一张「逻辑位置 → 本层偏移」的索引；读的时候从新到旧查，第一个命中就停。")
    # 层叠
    layers = [("upper（可写）", "位置1 → 0x0100", GREEN),
              ("增量层（只读）", "位置3 → 显式零", ORANGE),
              ("基层（只读）", "位置0/1/2/3 都有数据", PURPLE)]
    y = 2.05
    for name, d, c in layers:
        rect(s, 0.62, y, 6.4, 0.78, fill=WHITE, line=c, radius=0.05)
        rect(s, 0.62, y, 0.05, 0.78, fill=c, radius=0)
        tbox(s, 0.82, y + 0.10, 2.5, 0.3, name, 11, True, INK)
        tbox(s, 0.82, y + 0.44, 5.9, 0.3, d, 10, False, DIM)
        y += 0.90
    # 视图结果
    tbox(s, 7.35, 2.02, 5.37, 0.3, "最终逻辑视图（从上往下第一个命中）", 10.5, True, DIM)
    cells = [("位置0", "基层 A", PURPLE), ("位置1", "upper 新数据", GREEN),
             ("位置2", "显式零", ORANGE), ("位置3", "显式零", ORANGE)]
    xx = 7.35
    for t, d, c in cells:
        rect(s, xx, 2.36, 1.30, 0.92, fill=tint(c, 0.9), line=c, radius=0.05)
        tbox(s, xx + 0.08, 2.44, 1.14, 0.26, t, 9.5, True, DIM, PP_ALIGN.CENTER)
        tbox(s, xx + 0.08, 2.72, 1.16, 0.5, d, 9.5, True, INK, PP_ALIGN.CENTER, spacing=1.1)
        xx += 1.35
    tbox(s, 0.62, 4.90, 12.1, 1.25,
         "两个语义必须分清：\n"
         "· 「无记录」不是零——它表示「这层没管这段」，要继续往下一层找（回落）。\n"
         "· 「显式零」必须终止查找——它表示「我明确写过这里全是 0」，若当成无记录，就会把下层的旧数据暴露出来。\n"
         "所以叠加只能在索引层做；把层文件首尾拼接，只会得到 A/B/C/D/X/Y，表达不了「X 替换位置 1」。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为「没记录」等于读出为零；以为 OverlayBD 是数据库或 OverlayFS。",
         "新层某位置没有记录，读出来是什么？为什么？", ORANGE, nxt())

    # 第 12 课
    s = page(prs, ORANGE); header(s, "第 12 课", "内核给壳，用户态给内容", ORANGE,
                               "ublk 把「块设备」这个外形交给内核，把「这块里是什么」留给用户态 daemon。")
    # 三个节点
    rect(s, 0.62, 2.02, 6.2, 3.3, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 0.82, 2.14, 5.8, 0.3, "三个设备节点，别混", 10.5, True, ORANGE)
    nodes = [("/dev/ublk-control", "全局管理：创建 / 删除 / 设参数"),
             ("/dev/ublkcN", "该设备的命令交接通道（daemon 用它拿请求）"),
             ("/dev/ublkbN", "对外读写的块设备（Firecracker 挂的是这个）")]
    yy = 2.52
    for n, d in nodes:
        tbox(s, 0.82, yy, 2.7, 0.3, n, 10.5, True, INK)
        tbox(s, 3.55, yy, 3.1, 0.5, d, 9.5, False, DIM, spacing=1.15)
        yy += 0.62
    tbox(s, 0.82, 4.48, 5.8, 0.7,
         "创建流程：server 发 Create → 内核分配 N → daemon 等节点\n真正可打开（不只是文件存在）→ 回 (dev_id, path)",
         9.5, False, INK, spacing=1.25)
    # 右侧四步
    rect(s, 7.02, 2.02, 5.71, 3.3, fill=tint(ORANGE, 0.94), line=tint(ORANGE, 0.72), radius=0.05)
    tbox(s, 7.22, 2.14, 5.3, 3.05,
         "daemon 处理一次 4 KiB 读的四步\n\n"
         "① 等待：在 io_uring 上提交「有活给我」\n"
         "② 领取：CQE 带回请求描述（queue、tag、偏移、长度）\n"
         "   —— 这一步只代表「请求送到了」\n"
         "③ 解析：调 OverlayBD 查索引，定层、定偏移、取字节\n"
         "④ 提交：报告完成，原块请求才算完成",
         10.5, False, INK, spacing=1.4)
    tbox(s, 0.62, 5.50, 12.1, 0.7,
         "它不是什么：不是内核模块、不是每沙箱一个进程、不是 OverlayBD 本身（后者是它链接的库）。集中式的好处是密度，代价是单点。",
         11.5, True, ORANGE)
    foot(s, "把 FETCH_REQ 的 CQE 当成「数据已读出」；以为设备编号固定不变。",
         "daemon 挂了，这个节点上的沙箱会发生什么？", ORANGE, nxt())

    # ---------- 章节 05 ----------
    divider(prs, "05", "内存与快照", "第 13—18 课：映射、缺页、COW、捕获、封存、恢复", VIOLET, nxt())

    # 第 13 课
    s = page(prs, VIOLET); header(s, "第 13 课", "映射了 ≠ 分配了 ≠ 复制了", VIOLET,
                               "这是整门课最值钱的一句话，也是面试里最容易露馅的一句。")
    # 三态
    states = [("① mmap 之后", "只有虚拟范围（VMA）\n没有任何物理页\n128 MiB 一分没占", GREEN),
              ("② 第一次读", "缺页（minor/major）\n有页就映射，没页就去取\n取完填 PTE", ORANGE),
              ("③ 第一次写", "COW：复制一份私有副本\n之后各写各的\n共享页不再变", PURPLE)]
    x = 0.62
    for t, d, c in states:
        rect(s, x, 2.05, 3.95, 1.75, fill=WHITE, line=c, radius=0.06)
        tbox(s, x + 0.18, 2.16, 3.6, 0.3, t, 11.5, True, c)
        tbox(s, x + 0.18, 2.52, 3.6, 1.15, d, 10.5, False, INK, spacing=1.4)
        x += 4.13
    tbox(s, 0.62, 4.02, 12.1, 2.05,
         "缺页的三种情况要分开：minor（页已在内存，比如零页、page cache）、major（页不在，要读文件/换入）、\n"
         "以及非法访问（地址没有映射或权限不符，通常 SIGSEGV）。写保护缺页不属于非法访问，那是 COW 的正常处理。\n\n"
         "两种写语义：MAP_SHARED 写会进共享缓存、按规则写回；MAP_PRIVATE 的写只影响自己的私有副本。\n"
         "fork 之后父子共享物理页、PTE 都设成只读，任一方写才复制——这就是 COW，不是「fork 时复制」也不是「mmap 时复制」。\n\n"
         "接到 microVM：恢复时 Guest RAM 是「只读层 + 私有可写」，Guest 第一次读某页会去后端取，第一次写才复制。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为 mmap 128 MiB 就占 128 MiB 物理内存；以为 COW 在映射或 fork 时就发生。",
         "恢复后第一次「读」一页和第一次「写」一页，分别发生什么？", VIOLET, nxt())

    # 第 14 课
    s = page(prs, VIOLET); header(s, "第 14 课", "快照是四件套，不是「存个内存」", VIOLET,
                               "缺任何一件都恢复不出一台能跑的同款机器；而四件事还各在不同的时间点完成。")
    parts = [("VM 状态", "寄存器、指令位置、设备状态", BLUE),
             ("内存镜像", "Guest RAM 的内容，可增量 + 父层", VIOLET),
             ("磁盘视图", "rootfs 层 + 额外盘 + 父层引用", ORANGE),
             ("恢复配置/索引", "层顺序、设备关联、兼容参数", GREEN)]
    x = 0.62
    for t, d, c in parts:
        rect(s, x, 2.02, 2.95, 1.35, fill=WHITE, line=c, radius=0.06)
        tbox(s, x + 0.16, 2.12, 2.6, 0.3, t, 11.5, True, c)
        tbox(s, x + 0.16, 2.46, 2.62, 0.8, d, 10, False, INK, spacing=1.3)
        x += 3.07
    # 四件事分开
    tbox(s, 0.62, 3.58, 12.1, 0.3, "顺序与四个不同的「完成」", 10.5, True, DIM)
    seq = [("pause", "停止执行 Guest"), ("捕获", "读内存、写层、生成状态文件"),
           ("持久化", "fsync / 上传，抗断电"), ("释放运行时", "关实例、回收资源")]
    xx = 0.62
    for i, (t, d) in enumerate(seq):
        rect(s, xx, 3.92, 2.85, 0.86, fill=WHITE, line=LINE, radius=0.05)
        tbox(s, xx + 0.14, 3.98, 2.5, 0.28, t, 10.5, True, INK)
        tbox(s, xx + 0.14, 4.28, 2.6, 0.42, d, 9, False, DIM, spacing=1.1)
        if i < 3:
            arrow_right(s, xx + 2.88, 4.22, 0.18, 0.2, LINE)
        xx += 3.08
    tbox(s, 0.62, 4.98, 12.1, 1.15,
         "为什么必须先暂停全部 vCPU：抓取期间页还在变，会拼出「从未同时存在」的状态（真实是 x=90,y=110，采到 x=100,y=110）。\n"
         "但暂停只停 Guest 的 CPU 写入；宿主设备侧仍可能在写同一块 RAM，所以还要协调设备和在途 IO。\n"
         "最后一个区分：VM 内部一致 ≠ 应用事务已提交。快照回滚不了外部支付系统已经完成的交易。",
         11.5, False, INK, spacing=1.42)
    foot(s, "pause 成功就当快照成功；把 VM 一致性当成业务一致性。",
         "快照写失败了一半，重试要注意什么？", VIOLET, nxt())

    # 第 15 课
    s = page(prs, VIOLET); header(s, "第 15 课", "增量必须有基线，范围不冻结内容", VIOLET,
                               "只存脏页是省空间的前提，但前提是「你能从父层把没存的页补回来」。")
    # 表格化展示
    tbox(s, 0.62, 2.02, 3.0, 0.3, "页号", 10, True, DIM)
    for i in range(6):
        tbox(s, 2.35 + i * 1.05, 2.02, 1.0, 0.3, str(i), 10, True, DIM, PP_ALIGN.CENTER)
    rows = [("S0 基线", ["A", "B", "C", "D", "E", "F"], PURPLE),
            ("S1 增量", ["—", "B1", "—", "—", "E1", "—"], ORANGE),
            ("S2 增量", ["—", "—", "—", "—", "E2", "F2"], ORANGE),
            ("S2 视图", ["A", "B1", "C", "D", "E2", "F2"], GREEN)]
    y = 2.34
    for name, vals, c in rows:
        tbox(s, 0.62, y + 0.10, 1.7, 0.3, name, 10.5, True, c)
        for i, v in enumerate(vals):
            fill = tint(c, 0.92) if v != "—" else WHITE
            rect(s, 2.35 + i * 1.05, y, 0.92, 0.5, fill=fill, line=tint(c, 0.6) if v != "—" else LINE, radius=0.05)
            tbox(s, 2.35 + i * 1.05, y + 0.10, 0.92, 0.3, v, 10, v != "—", INK, PP_ALIGN.CENTER)
        y += 0.62
    tbox(s, 0.62, 5.10, 12.1, 1.05,
         "三个概念严格区分：dirty（被记录为写过，改回原值仍是脏）、present（页在不在）、内容为零（值本身）。\n"
         "范围列表只描述「从哪取、存到逻辑哪里」，它不会冻结内容——一致性靠的是暂停与协调，不是这份列表。\n"
         "所以恢复时的读请求数、实际读盘量、镜像逻辑大小，是三个不同的指标，不能互相代入。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为 dirty 列表能保证一致快照；以为「页不驻留」就等于「内容为零」。",
         "父层有旧数据、新状态应为全零，能不能省略这条覆盖？", VIOLET, nxt())

    # 第 16 课
    s = page(prs, VIOLET); header(s, "第 16 课", "跨进程读：每个参数都要能说出归属", VIOLET,
                               "读 Guest RAM 的四个参数，面试里逐个问都有人答错。")
    call = ("process_vm_readv(\n"
            "    pid,          // ← Firecracker 的宿主 PID\n"
            "    local_iov,    // ← server 自己的缓冲区\n"
            "    remote_iov,   // ← 地址是 Firecracker 的 HVA\n"
            "    ...)")
    rect(s, 0.62, 2.02, 5.65, 1.95, fill=WHITE, line=VIOLET, radius=0.05)
    tbox(s, 0.82, 2.14, 5.3, 1.75, call, 10.5, False, INK, spacing=1.5)
    rect(s, 6.55, 2.02, 6.18, 1.95, fill=tint(VIOLET, 0.94), line=tint(VIOLET, 0.72), radius=0.05)
    tbox(s, 6.75, 2.14, 5.8, 1.72,
         "两个 iovec 数组本身都在调用者内存里\n"
         "只有 remote_iov 元素里的地址指向目标进程；\n"
         "liovcnt / riovcnt 是元素个数，不是字节数",
         10.5, False, INK, spacing=1.4)
    tbox(s, 0.62, 4.12, 12.1, 2.0,
         "读循环里最容易忽略的三件事：\n"
         "· 短读：请求 8192 只回来 4096 → 源地址和目的地址同时前进 4096 再继续，不是从头重读。\n"
         "· EINTR：被信号打断要重试；零进展或长度异常必须报错，不能当成功。\n"
         "· async 外壳：read_at 标了 async，但内部仍是同步的 process_vm_readv，不会自动让出 Tokio worker。\n\n"
         "边界：整段读完只说明「目的 buffer 拿到了字节」，不代表已封装成层、写进文件、或形成完整快照。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为 async 方法就是异步 IO；以为读成功＝已持久化。",
         "请求 8192 只回 4096，下一次从哪继续？函数的 off 在这个实现里是什么？", VIOLET, nxt())

    # 第 17 课
    s = page(prs, VIOLET); header(s, "第 17 课", "chunk 是任务批次，buffer 才是字节", VIOLET,
                               "两条线并行：元数据线决定「存到哪」，字节线决定「搬什么」。")
    rect(s, 0.62, 2.02, 5.95, 1.15, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 0.82, 2.12, 5.6, 0.28, "元数据线", 10.5, True, BLUE)
    tbox(s, 0.82, 2.44, 5.6, 0.65, "范围映射 → entry(tag/src_offset/len/logical_offset) → 输出索引", 10, False, INK, spacing=1.25)
    rect(s, 6.78, 2.02, 5.95, 1.15, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 6.98, 2.12, 5.6, 0.28, "字节线", 10.5, True, ORANGE)
    tbox(s, 6.98, 2.44, 5.6, 0.65, "Firecracker HVA → ProcessVmReader → server buffer → writer", 10, False, INK, spacing=1.25)
    # 层格式
    tbox(s, 0.62, 3.42, 12.1, 0.3, "层文件的概念布局（顺序不重要，索引才是关键）", 10, True, DIM)
    segs = [("header", 1.6, LINE), ("payload（紧凑存放）", 4.0, tint(ORANGE, 0.75)),
            ("index（逻辑范围 → 层内位置）", 3.6, tint(BLUE, 0.75)), ("trailer", 1.5, LINE)]
    xx = 0.62
    for name, w, c in segs:
        rect(s, xx, 3.74, w, 0.56, fill=c, line=LINE, radius=0.04)
        tbox(s, xx + 0.06, 3.82, w - 0.12, 0.4, name, 9.5, True, INK, PP_ALIGN.CENTER, spacing=1.1)
        xx += w + 0.1
    tbox(s, 0.62, 4.55, 12.1, 1.6,
         "为什么一个 chunk 不等于一次 syscall：chunk 只是把若干 entry 组织在一起；source 是 ProcessVmReader 时，\n"
         "每个 entry 各自走一遍跨进程读，短读还要在内部循环。chunk 大小、并发度、syscall 次数、真实磁盘 IO 次数是四个不同指标。\n\n"
         "两个「完成」的边界：writer.finalize 只表示格式处理完成；临时文件 rename 成功只表示名字切换。\n"
         "两者都不等于断电持久化，也不代替 VM 状态、父层引用与 manifest 的整体发布。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为 chunk 已经把多次读合并成一次 syscall；以为 finalize + rename 就等于持久化。",
         "一个 chunk 有两个 entry，是几次跨进程读？为什么？", VIOLET, nxt())

    # 第 18 课
    s = page(prs, VIOLET); header(s, "第 18 课", "恢复不是「把内存读回来」", VIOLET,
                               "主路径是：Firecracker 映射只读内存设备，按需缺页，写时 COW。")
    steps = [("准备运行环境", "检查 ublk 可用、备盘、备网", BLUE),
             ("加载 VM 状态", "load_snapshot_file(resume_vm=false)", BLUE),
             ("映射内存后端", "内存镜像 → 只读块设备 → 私有映射", VIOLET),
             ("补充配置", "新挂载卷、MMDS、限流", BLUE),
             ("resume", "vCPU 继续执行，缺页按需取", GREEN)]
    y = 2.02
    for i, (t, d, c) in enumerate(steps):
        rect(s, 0.62, y, 6.3, 0.70, fill=WHITE, line=c, radius=0.05)
        tbox(s, 0.80, y + 0.07, 2.5, 0.26, t, 10.5, True, INK)
        tbox(s, 0.80, y + 0.36, 5.9, 0.28, d, 9.5, False, DIM)
        if i < 4:
            arrow_down(s, 3.68, y + 0.72, 0.18, 0.16, LINE)
        y += 0.80
    rect(s, 7.15, 2.02, 5.58, 3.55, fill=tint(VIOLET, 0.94), line=tint(VIOLET, 0.72), radius=0.05)
    tbox(s, 7.35, 2.14, 5.2, 3.3,
         "一页 RAM 怎么变得可访问\n\n"
         "Guest 访问某个 GPA → 宿主页表缺项\n"
         "→ 向只读内存设备发块读\n"
         "→ daemon 查 OverlayBD 找这一块\n"
         "→ 取到数据、填进宿主页\n"
         "→ Guest 继续执行\n\n"
         "写这一页：COW 到私有层，共享镜像不动。\n"
         "所以「恢复成功」只代表可以开始跑。",
         10.5, False, INK, spacing=1.4)
    tbox(s, 0.62, 6.02, 12.1, 0.34,
         "推论：恢复后首条命令慢、内存指标却不高，是正常的——那是在缺页；而不是「恢复没生效」。",
         11.5, True, VIOLET)
    foot(s, "以为恢复会把全部内存读回来；以为恢复 VM 就等于恢复了外部连接与状态。",
         "恢复后一条旧 TCP 连接为什么可能不通？举一个没被恢复的状态。", VIOLET, nxt())

    # ---------- 章节 06 ----------
    divider(prs, "06", "网络与隔离", "第 19—20 课：包怎么出去，四道门各关什么", AMBER, nxt())

    # 第 19 课
    s = page(prs, AMBER); header(s, "第 19 课", "两条路径：出站转发，和宿主进 Guest", AMBER,
                               "同一个内核里的不同 netns，接口可以同名；靠 slot 地址区分实例。")
    # 出站链路
    tbox(s, 0.62, 2.02, 6.0, 0.28, "① Guest 出站（普通路由 + 两层源 NAT）", 10.5, True, AMBER)
    chain = [("Guest eth0", "VirtIO-net"), ("TAP", "沙箱 netns"), ("SNAT", "改为 slot 地址"),
             ("veth", "到主 netns"), ("MASQUERADE", "适配出口")]
    x = 0.62
    for i, (t, d) in enumerate(chain):
        rect(s, x, 2.34, 2.22, 0.78, fill=WHITE, line=AMBER, radius=0.05)
        tbox(s, x + 0.10, 2.40, 2.02, 0.26, t, 10, True, INK)
        tbox(s, x + 0.10, 2.66, 2.02, 0.4, d, 8.5, False, DIM, spacing=1.1)
        if i < 4:
            arrow_right(s, x + 2.24, 2.60, 0.16, 0.2, AMBER)
        x += 2.44
    # 入站
    tbox(s, 0.62, 3.42, 6.0, 0.28, "② 宿主访问 envd（DNAT 进沙箱 netns）", 10.5, True, BLUE)
    inbound = [("server", "发到 slot 地址"), ("veth", "进沙箱 netns"), ("DNAT", "改成 Guest IP"),
               ("tap0 → Firecracker", "VirtIO RX")]
    x = 0.62
    for i, (t, d) in enumerate(inbound):
        rect(s, x, 3.74, 2.80, 0.78, fill=WHITE, line=BLUE, radius=0.05)
        tbox(s, x + 0.10, 3.80, 2.60, 0.26, t, 10, True, INK)
        tbox(s, x + 0.10, 4.06, 2.60, 0.4, d, 8.5, False, DIM, spacing=1.1)
        if i < 3:
            arrow_right(s, x + 2.82, 4.00, 0.16, 0.2, BLUE)
        x += 3.05
    tbox(s, 0.62, 4.78, 12.1, 1.35,
         "三个必须说准的点：\n"
         "· 每个 netns 都可以有名叫 tap0 的接口：先由 netns 分隔，再用 slot 专属地址区分实例，所以同名不冲突。\n"
         "· TX 的 used 只表示「这个发送缓冲区可以回收」，不表示远端收到、更不表示业务成功。\n"
         "· 80/443 可被 REDIRECT 到出口代理（按 Host/SNI 判断），但代理不终止 TLS、不改写 HTTP，也不是通用域名防火墙。",
         11.5, False, INK, spacing=1.42)
    foot(s, "以为同名 tap0 会冲突；以为 TX 完成＝对端收到；以为策略更新会切断已有连接。",
         "恢复 Guest 内存里的 socket，能否保证外部连接继续可用？", AMBER, nxt())

    # 第 20 课
    s = page(prs, AMBER); header(s, "第 20 课", "四类威胁，四道不同的门", AMBER,
                               "先问「防谁、防什么」，再问「用什么挡」。顺序错了，答案一定是错的。")
    # 2x2
    quads = [
        ("A. Guest 内作恶（含 root）", "没越过任何门\nGuest root 本来就能任意 syscall", "Guest 自己的内核\n（RLIMIT / pid_max）", BLUE),
        ("B. VMM 被攻破（逃逸）", "已越过虚拟化边界", "seccomp / 降权 / chroot\ncaps / LSM / namespace", ORANGE),
        ("C. 资源超用", "没越界，走正常消耗", "cgroup 限值 / vCPU 数\nballoon", GREEN),
        ("D. 网络外连", "没越界，走虚拟网卡", "netns + veth + iptables\n+ 出口代理", PURPLE),
    ]
    x, y = 0.62, 2.02
    for i, (t, d, c, col) in enumerate(quads):
        px = x + (i % 2) * 6.22
        py = y + (i // 2) * 1.62
        rect(s, px, py, 5.90, 1.42, fill=WHITE, line=col, radius=0.05)
        tbox(s, px + 0.16, py + 0.10, 5.6, 0.3, t, 11, True, col)
        tbox(s, px + 0.16, py + 0.44, 2.9, 0.85, d, 9, False, DIM, spacing=1.2)
        tbox(s, px + 3.15, py + 0.44, 2.65, 0.85, "控制点：\n" + c, 9, False, INK, spacing=1.2)
    tbox(s, 0.62, 5.32, 12.1, 0.95,
         "一句话分家：namespace 改「看见什么」，cgroup 改「能用多少」，seccomp/caps/LSM 改「能对内核做什么」，虚拟化改「有几台机器」。\n"
         "最容易错的一条：seccomp 是线程级白名单，拦的是 VMM 自己发出的宿主 syscall——Guest 内部的 syscall 它根本看不到。",
         11.5, False, INK, spacing=1.4)
    foot(s, "以为 pids.max 能挡 Guest 内 fork bomb（它只数宿主 task）；以为 namespace 等于降权。",
         "Guest 里的 root 执行任意 syscall，会被 Firecracker 的 seccomp 拦住吗？", AMBER, nxt())

    # ---------- 章节 07 ----------
    divider(prs, "07", "面试", "五个必深点 · 四段式 · 追问链 · 已纠正的说法", TEAL, nxt())

    # 五个必深点
    s = page(prs, TEAL); header(s, "面试", "五个必深点：每个都要能讲 5 分钟", TEAL,
                               "其余课程只要 15 秒能答。深度集中在能决定面试结果的地方。")
    pts = [("① 地址空间", "GVA/GPA/HVA/HPA 四条线 + PVM 参数归属", "一次跨进程读的字节数与耗时", BLUE),
           ("② VM-Exit 分流", "MMIO 靠 EPT 缺映射、PIO 靠敏感指令；exit_reason 怎么分流", "一次压测里的退出次数", PURPLE),
           ("③ 快照与恢复", "四件套、一致性、只读层 + COW + 按需加载", "冷/热恢复延迟对比", VIOLET),
           ("④ 隔离各层", "namespace/cgroup/seccomp/降权 各挡什么、漏什么", "真实进程的线程数、Seccomp 值、限额", AMBER),
           ("⑤ 性能口径", "wall 与 CPU、p50/p99、资源就绪 vs 首命令完成", "一段分段耗时表", TEAL)]
    y = 1.95
    for i, (t, d, e, c) in enumerate(pts):
        rect(s, 0.62, y, 12.13, 0.74, fill=WHITE if i % 2 == 0 else SOFT, line=LINE, radius=0.05)
        tbox(s, 0.82, y + 0.08, 2.2, 0.3, t, 11.5, True, c)
        tbox(s, 0.82, y + 0.40, 6.6, 0.3, d, 9.5, False, DIM)
        tbox(s, 7.65, y + 0.20, 4.9, 0.36, "证据：" + e, 9.5, False, ORANGE)
        y += 0.80
    tbox(s, 0.62, 5.98, 12.1, 0.32, "橙色那一列是「做过」的证据；缺哪行，就从那行开始补数字。", 10.5, True, ORANGE)
    foot(s, "把「读过文档」当成「有证据」。面试里问「你测过吗」，答不出数字就掉一档。",
         "这五个点里，你现在能立刻拿出证据的是哪几个？", TEAL, nxt())

    # 四段式 + 示范
    s = page(prs, TEAL); header(s, "面试", "四段式：缺第 4 段就是只背过", TEAL,
                               "以「你们沙箱怎么隔离」为例，给一份可以直接照着说的答案。")
    rect(s, 0.62, 2.02, 3.6, 3.6, fill=WHITE, line=LINE, radius=0.05)
    tbox(s, 0.82, 2.14, 3.2, 3.3,
         "模板\n\n① 结论\n一句话给判断\n\n② 机制\n两句讲谁在哪层做了什么\n\n③ 边界\n一句半讲清挡不住什么、代价\n\n④ 证据\n一个数字 / 一次实测 / 一次故障",
         10.5, False, INK, spacing=1.35)
    rect(s, 4.42, 2.02, 8.31, 3.6, fill=tint(TEAL, 0.95), line=tint(TEAL, 0.7), radius=0.05)
    tbox(s, 4.62, 2.12, 7.95, 3.4,
         "示范答案\n\n"
         "结论：分两类——一类防 Guest 越界，一类防 VMM 被攻破后的破坏力。\n"
         "机制：Guest 与宿主之间靠硬件虚拟化（VT-x + EPT）；VMM 自己只是宿主上的普通进程，\n"
         "　　　靠 seccomp 白名单限制它能发的 syscall，namespace 给它独立的挂载与网络视图，cgroup 管用量。\n"
         "边界：namespace 只改视图不改权限；cgroup 只记账不设限就等于没有；seccomp 是线程级，拦不到 Guest 内 syscall。\n"
         "证据：我读过的一份实现里，VMM 用 unshare -m + ip netns exec 启动、没有 jailer、cgroup 只读不设限，\n"
         "　　　VMM 逃逸后只剩 seccomp 一道——这个结论是从真实配置里看出来的，不是推测。",
         10, False, INK, spacing=1.4)
    tbox(s, 0.62, 5.78, 12.1, 0.5,
         "第 4 段是分水岭：前三段背得出来的人很多，能说出「我在哪看到的 / 我测出多少」的人很少。",
         11.5, True, TEAL)
    foot(s, "只报平均值不报分位数；只讲名词不讲「什么情况下会变坏」。",
         "现在给你 90 秒，用四段式讲「VM-Exit」，你能讲完吗？", TEAL, nxt())

    # 追问表
    s = page(prs, TEAL); header(s, "面试", "八个高频追问：能接住三层就够", TEAL,
                               "答案都压成一句半，重点是别在第二层就断掉。")
    qa = [("Guest 里的 root 会被 seccomp 拦吗？", "不会。seccomp 只约束 VMM 发出的宿主 syscall"),
          ("为什么不能边跑边抓快照？", "页在变，会拼出从未同时存在的状态"),
          ("恢复后网络为什么可能不通？", "对端状态、宿主 conntrack/NAT、超时计时器都没回滚"),
          ("冷启动 3 秒先查哪段？", "分段计时：拉镜像/建盘/起 VMM/等 envd/首命令"),
          ("fork 的两个实例共享什么？", "共享只读底座，各自 COW 私有层；需重随机化 PID/RNG/时钟"),
          ("daemon 挂了会怎样？", "该节点块 IO 全停；快照恢复直接失败"),
          ("升级 VMM 为什么会被 seccomp 杀掉？", "默认动作是 trap，新 syscall 不在白名单就 SIGSYS"),
          ("为什么按沙箱开 SQPOLL 是错的？", "一 ring 一轮询线程占满一核，密度场景直接超订")]
    y = 2.00
    for i, (q, a) in enumerate(qa):
        fill = WHITE if i % 2 == 0 else SOFT
        rect(s, 0.62, y, 12.13, 0.46, fill=fill, line=LINE, radius=0.04)
        tbox(s, 0.80, y + 0.10, 5.2, 0.28, q, 9.5, True, INK)
        tbox(s, 6.15, y + 0.10, 6.4, 0.28, a, 9.5, False, DIM)
        y += 0.50
    foot(s, "第二层就答不下去——面试官会认为第一层也是背的。",
         "这八条里，哪三条你现在讲不出机制？", TEAL, nxt())

    # 已纠正
    s = page(prs, TEAL); header(s, "面试", "已经纠正过的说法：别再讲错", TEAL,
                               "这些是我在带你的过程里实际纠出来的，也是最容易被追问戳穿的地方。")
    wrong = [("pids.max 能挡 Guest 内 fork bomb", "不能：它只数宿主 cgroup 里的 task"),
             ("多实例共享同一批 page cache 页", "已核验成立：共享设备与页缓存，MAP_PRIVATE 写时 COW"),
             ("VM-Exit 就等于 KVM_RUN 返回用户态", "不等：KVM 可处理完直接重入"),
             ("namespace 隔离等于降权", "namespace 只改视图，ns 里的 root 仍是 root"),
             ("finalize + rename 等于已持久化", "只保证格式完成与名字切换"),
             ("health 通过等于鉴权通过", "health 不带 token；受保护命令另有鉴权")]
    y = 2.02
    tbox(s, 0.62, y - 0.02, 5.9, 0.26, "✗ 错误说法", 10, True, ORANGE)
    tbox(s, 6.75, y - 0.02, 5.9, 0.26, "✓ 正确说法", 10, True, GREEN)
    y += 0.30
    for i, (a, b) in enumerate(wrong):
        fill = WHITE if i % 2 == 0 else SOFT
        rect(s, 0.62, y, 12.13, 0.56, fill=fill, line=LINE, radius=0.04)
        tbox(s, 0.80, y + 0.14, 5.6, 0.3, a, 9.5, False, RGBColor(0x99, 0x3C, 0x0C))
        tbox(s, 6.75, y + 0.14, 5.85, 0.3, b, 9.5, False, RGBColor(0x16, 0x6B, 0x30))
        y += 0.62
    tbox(s, 0.62, 6.02, 12.1, 0.3,
         "这六条的共同点：都把「某一层的完成」当成了「整件事完成」，或者把「看见什么」当成了「能用多少」。",
         10.5, True, DIM)
    foot(s, "同一句错话在不同面试里会被追问到不同深度，但第一句错就结束了。",
         "这六条你能用自己的话重新讲一遍吗？", TEAL, nxt())

    # 结束页
    s = page(prs, BLUE); header(s, "下一步", "把「讲过」变成「做过」", BLUE,
                               "剩下的缺口很具体：几个数字，和两个还没演练的深点。")
    todo = [("还没演练的深点", "地址空间（PVM 参数与短读）、性能度量（冷启动怎么查）", BLUE),
            ("还没跑的实验", "/dev/kvm 通路、ns 创建耗时、cgroup 限额是否生效", ORANGE),
            ("还没有的数字", "冷/热恢复延迟、一次跨进程读耗时、退出次数", VIOLET),
            ("还没写的", "第 21—28 课改成面试格式；三篇项目故事", GREEN)]
    y = 2.02
    for t, d, c in todo:
        rect(s, 0.62, y, 12.13, 0.86, fill=WHITE, line=LINE, radius=0.05)
        rect(s, 0.62, y, 0.05, 0.86, fill=c, radius=0)
        tbox(s, 0.84, y + 0.12, 3.4, 0.3, t, 11, True, c)
        tbox(s, 4.35, y + 0.12, 8.2, 0.6, d, 10, False, INK, spacing=1.2)
        y += 0.96
    tbox(s, 0.62, 6.02, 12.1, 0.4, "下一步动作只有一个：先在 WSL 里跑 ls -l /dev/kvm，把实验的路打通。", 11.5, True, BLUE)
    foot(s, "只看不测：面试问「你测过吗」，答不出数字，前面讲得再好也会掉档。",
         "下一周你打算补哪个数字？基线怎么定？", BLUE, nxt())

    prs.save(path)
    print("saved:", path, "slides:", len(prs.slides))

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "review.pptx")
