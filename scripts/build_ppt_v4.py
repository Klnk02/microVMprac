# -*- coding: utf-8 -*-
"""AgentENV 图示版（简约风）：一页一图，覆盖 28 课 + 面试。
用法：python build_ppt_v4.py <输出路径>
"""
import sys, math
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

F = "Microsoft YaHei"
INK   = RGBColor(0x11, 0x11, 0x11)
GRAY  = RGBColor(0x6B, 0x72, 0x80)
LIGHT = RGBColor(0xE5, 0xE7, 0xEB)
PALE  = RGBColor(0xF7, 0xF8, 0xFA)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

BLUE   = RGBColor(0x25, 0x63, 0xEB)
PURPLE = RGBColor(0x6D, 0x28, 0xD9)
GREEN  = RGBColor(0x05, 0x96, 0x69)
ORANGE = RGBColor(0xC2, 0x41, 0x0C)
AMBER  = RGBColor(0xB4, 0x53, 0x09)
TEAL   = RGBColor(0x0F, 0x76, 0x6E)
SLATE  = RGBColor(0x33, 0x41, 0x55)
VIOLET = RGBColor(0x7E, 0x22, 0xCE)

def sf(run, size, bold=False, color=INK, name=F):
    run.font.size = Pt(size); run.font.bold = bold
    run.font.color.rgb = color; run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', name)

def T(s, x, y, w, h, text, size=9, bold=False, color=INK,
      align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, ls=1.25):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, seg in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = ls
        r = p.add_run(); r.text = seg
        sf(r, size, bold, color)
    return box

def line(s, x, y, w, h=0.008, color=LIGHT):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    sh.line.fill.background(); sh.shadow.inherit = False
    return sh

def node(s, x, y, w, h, text, accent=GRAY, size=9, bold=False, fill=WHITE,
         sub=None, dashed=False, lw=0.75):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = accent; sh.line.width = Pt(lw)
    if dashed: sh.line.dash_style = 4
    sh.shadow.inherit = False
    try: sh.adjustments[0] = 0.08
    except Exception: pass
    if sub:
        T(s, x + 0.06, y + h/2 - 0.26, w - 0.12, 0.24, text, size, bold, INK, PP_ALIGN.CENTER)
        T(s, x + 0.06, y + h/2 - 0.02, w - 0.12, 0.26, sub, size - 1.5, False, GRAY, PP_ALIGN.CENTER)
    else:
        T(s, x + 0.06, y + 0.02, w - 0.12, h - 0.04, text, size, bold, INK,
          PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    return sh

def tri(s, x, y, w=0.10, h=0.10, color=GRAY, rot=90):
    sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.rotation = rot
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    sh.line.fill.background(); sh.shadow.inherit = False

def arrow_h(s, x1, x2, y, color=LIGHT, w=0.010):
    line(s, x1, y, max(0.02, x2 - x1 - 0.08), w, color)
    tri(s, x2 - 0.09, y - 0.055, 0.10, 0.10, color, 90)

def arrow_v(s, y1, y2, x, color=LIGHT, w=0.010):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y1), Inches(w), Inches(max(0.02, y2 - y1 - 0.08)))
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    sh.line.fill.background(); sh.shadow.inherit = False
    tri(s, x - 0.045, y2 - 0.09, 0.10, 0.10, color, 180)

def vflow(s, x, y, w, items, accent=GRAY, bh=0.50, gap=0.26, size=9):
    yy = y
    for i, it in enumerate(items):
        txt, sub = (it if isinstance(it, tuple) else (it, None))
        node(s, x, yy, w, bh, txt, accent, size, True, sub=sub)
        if i < len(items) - 1:
            arrow_v(s, yy + bh, yy + bh + gap, x + w/2 - 0.005)
        yy += bh + gap
    return yy

def hflow(s, x, y, w, items, accent=GRAY, bh=0.52, gap=0.30, size=8.5):
    n = len(items); bw = (w - gap*(n-1)) / n; xx = x
    for i, it in enumerate(items):
        txt, sub = (it if isinstance(it, tuple) else (it, None))
        node(s, xx, y, bw, bh, txt, accent, size, True, sub=sub)
        if i < n-1: arrow_h(s, xx + bw, xx + bw + gap, y + bh/2)
        xx += bw + gap
    return bw

def page(prs, accent=GRAY):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background(); bg.shadow.inherit = False
    line(s, 0, 0, 13.333, 0.07, accent)
    return s

def head(s, kicker, title, pageno, note=None):
    T(s, 0.72, 0.42, 9.0, 0.22, kicker, 8, True, GRAY)
    T(s, 0.70, 0.66, 11.9, 0.50, title, 20, True, INK)
    line(s, 0.72, 1.22, 11.9, 0.008, LIGHT)
    if note:
        T(s, 0.72, 1.34, 11.9, 0.26, note, 8.5, False, GRAY)
    T(s, 12.30, 7.10, 0.55, 0.22, str(pageno), 8, False, RGBColor(0xB0, 0xB5, 0xBD), PP_ALIGN.RIGHT)

def foot(s, left, right):
    line(s, 0.72, 6.62, 11.9, 0.008, LIGHT)
    T(s, 0.72, 6.72, 5.6, 0.26, left, 8, False, GRAY)
    T(s, 6.9, 6.72, 5.7, 0.26, right, 8, False, RGBColor(0x9A, 0xA0, 0xA8))

def big(s, x, y, num, cap, accent=INK, size=34):
    T(s, x, y, 2.6, 0.62, num, size, True, accent)
    T(s, x, y + 0.60, 2.6, 0.5, cap, 8.5, False, GRAY, ls=1.3)

def build(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    P = [0]
    def np_():
        P[0] += 1; return P[0]

    # ============ 封面 ============
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background(); bg.shadow.inherit = False
    line(s, 1.0, 1.55, 0.9, 0.035, INK)
    T(s, 1.0, 1.85, 11.0, 0.9, "AgentENV 沙箱：图示全课", 40, True, INK)
    T(s, 1.02, 2.82, 11.0, 0.4, "28 讲 · 一页一图 · 看图就能讲出机制", 14, False, GRAY)
    T(s, 1.02, 4.10, 10.6, 1.2,
      "读法：先看图形怎么动，再看下面那行灰字；合上讲义，你能把这张图画出来，才算会。\n"
      "所有数字标注「量级」；没有实测的地方不写数字。", 10, False, GRAY, ls=1.6)
    T(s, 1.02, 6.55, 11.0, 0.3, "基线 9f62cbe   ·   2026-11-16   ·   简约图示版", 9, False, RGBColor(0x9A, 0xA0, 0xA8))
    np_()

    # ============ 读图说明 ============
    s = page(prs, SLATE); head(s, "读法", "三种图，对应三种问题", np_())
    xs = [0.72, 4.85, 8.98]
    data = [("结构图", "谁在哪里、谁拥有谁", "位置", BLUE),
            ("流程图", "一次请求经过哪些完成点", "顺序", GREEN),
            ("对照图", "两个东西差在哪个维度", "区别", ORANGE)]
    for (t, d, n, c), x in zip(data, xs):
        node(s, x, 1.72, 3.60, 0.62, t, c, 11, True)
        T(s, x, 2.52, 3.60, 0.5, d, 9, False, GRAY, ls=1.4)
        big(s, x, 3.30, n, "看图时先问这一个", c, 30)
    T(s, 0.72, 5.30, 11.9, 0.6, "每页底部两行灰字：左边是「易错」，右边是「会被问」。其余留白是故意的。", 9, False, GRAY)
    np_()

    # ============ 全景：三层 ============
    s = page(prs, BLUE); head(s, "全景", "一台机器，三个执行环境", np_())
    rows = [("宿主用户态", ["server", "firecracker", "ublk-daemon"], BLUE, 1.72),
            ("宿主内核", ["KVM", "ublk 驱动", "cgroup / seccomp"], PURPLE, 2.96),
            ("Guest", ["Guest 内核", "envd", "你的程序"], GREEN, 4.20)]
    for name, items, c, y in rows:
        T(s, 0.72, y + 0.16, 1.5, 0.24, name, 8, True, c)
        xx = 2.25
        for it in items:
            node(s, xx, y, 3.05, 0.56, it, c, 9.5, True)
            xx += 3.25
        line(s, 2.25, y + 1.02, 10.55, 0.008, LIGHT)
    arrow_v(s, 4.05, 4.10, 7.0, LIGHT); arrow_v(s, 5.30, 5.32, 7.0, LIGHT)
    T(s, 7.15, 3.86, 3.2, 0.24, "Guest 不是子进程", 8, False, GRAY)
    T(s, 7.15, 5.10, 3.2, 0.24, "宿主看不见 Guest 的 PID", 8, False, GRAY)
    foot(s, "把 server 里的 Rust 对象当进程。", "宿主 ps 能看到哪些？")
    np_()

    # ============ 四把尺子 ============
    s = page(prs, BLUE); head(s, "全景", "一个变量，四个地址", np_())
    node(s, 5.55, 2.95, 2.2, 0.9, "宿主物理页", PURPLE, 10, True, sub="HPA")
    node(s, 0.90, 1.80, 2.5, 0.56, "Guest 程序", BLUE, 9.5, sub="GVA")
    node(s, 0.90, 2.55, 2.5, 0.56, "Guest 内核", BLUE, 9.5, sub="GPA")
    node(s, 10.0, 1.80, 2.4, 0.56, "Firecracker", PURPLE, 9.5, sub="HVA")
    arrow_v(s, 2.36, 2.55, 2.15, BLUE); arrow_v(s, 3.11, 2.95, 2.15, BLUE)
    arrow_v(s, 2.36, 2.95, 11.1, PURPLE)
    T(s, 0.90, 4.30, 11.9, 0.9,
      "Guest 访存：GVA → GPA → HPA（硬件完成，不经过 HVA）\n"
      "Firecracker 访存：HVA → HPA（宿主页表）——两条路可以落到同一块物理页", 9, False, GRAY, ls=1.6)
    node(s, 3.55, 5.35, 6.2, 0.52, "memslot：GPA 区间 ↔ HVA 区间（软件登记）", BLUE, 9)
    foot(s, "以为 Guest 访存会经过 HVA。", "登记 memslot 时为什么不填 HPA？")
    np_()

    # ============ 三条边界 ============
    s = page(prs, PURPLE); head(s, "全景", "三个动作，常常被混成一个", np_())
    items = [("KVM_RUN", "用户态 → 内核", "不切线程"), ("VM-Exit", "Guest ↔ 宿主执行环境", "不切线程"),
             ("线程切换", "调度器换线程", "切了")]
    y = 1.90
    for i, (t, d, r) in enumerate(items):
        node(s, 0.90, y, 2.4, 0.60, t, PURPLE, 10, True)
        T(s, 3.55, y + 0.18, 4.4, 0.26, d, 9, False, GRAY)
        T(s, 8.30, y + 0.18, 2.2, 0.26, r, 9, True, ORANGE if r == "切了" else GREEN)
        if i < 2: arrow_v(s, y + 0.60, y + 0.86, 2.10)
        y += 0.86
    T(s, 0.90, 4.55, 11.7, 0.9,
      "最实用的一句：VM-Exit 回到宿主内核 ≠ KVM_RUN 已返回用户态。\n"
      "KVM 能处理的退出会直接重入 Guest，整个 ioctl 从没返回过。", 9, False, GRAY, ls=1.6)
    foot(s, "把「VM-Exit」当「返回用户态」。", "哪些退出必须回用户态？")
    np_()

    # ================= 01 =================
    s = page(prs, BLUE); head(s, "01 / 位置与地址", "谁在跑、指针属于谁", np_(), "第 1—3 课")
    T(s, 0.72, 2.6, 8, 0.6, "第 1 课 进程与线程　·　第 2 课 地址空间　·　第 3 课 两条访存路径", 11, False, GRAY)
    np_()

    # 第1课 进程与线程
    s = page(prs, BLUE); head(s, "第 1 课", "一个进程，多个线程", np_(), "vCPU 就是线程；线程名是代码写死的")
    node(s, 0.90, 1.75, 4.6, 3.9, "", BLUE, 9, fill=PALE)
    T(s, 1.10, 1.88, 4.2, 0.24, "firecracker（宿主进程）", 8, True, BLUE)
    for i, (t, d) in enumerate([("vmm", "状态与设备"), ("api", "Unix socket"),
                                ("fc_vcpu 0", "KVM_RUN"), ("fc_vcpu 1", "KVM_RUN")]):
        node(s, 1.10, 2.22 + i*0.82, 4.2, 0.62, t, BLUE, 9.5, True, sub=d)
    T(s, 6.10, 1.80, 6.5, 3.6,
      "为什么不是一个线程\n"
      "vCPU 线程卡在 KVM_RUN 里跑 Guest 时，没人能接「请暂停」的请求。\n\n"
      "于是拆成三类：\n"
      "  vcpu —— 负责「Guest 在跑」的时间\n"
      "  api  —— 负责「随时能接请求」\n"
      "  vmm  —— 把请求翻译成协调动作\n\n"
      "名字来自代码：.name(\"fc_vcpu {i}\")，所以 ps -eLf 看得到。", 9, False, GRAY, ls=1.6)
    foot(s, "以为 vCPU 线程在 KVM_RUN 里就是睡着了。", "配 4 个 vCPU，宿主多几个线程？")
    np_()

    # 第2课 两个地址空间
    s = page(prs, BLUE); head(s, "第 2 课", "同一个数字，两块内存", np_(), "地址离开地址空间，没有意义")
    node(s, 0.95, 1.85, 2.3, 0.56, "server", ORANGE, 9.5, sub="0x400000")
    node(s, 0.95, 2.70, 2.3, 0.56, "firecracker", PURPLE, 9.5, sub="0x400000")
    node(s, 5.05, 1.85, 2.2, 0.56, "物理页 P_A", ORANGE, 9.5, sub="SERVER")
    node(s, 5.05, 2.70, 2.2, 0.56, "物理页 P_B", PURPLE, 9.5, sub="GUEST")
    arrow_h(s, 3.30, 5.00, 2.13, ORANGE); arrow_h(s, 3.30, 5.00, 2.98, PURPLE)
    T(s, 0.95, 3.55, 6.3, 0.3, "两个进程各有自己的页表：同一数字 → 不同物理页", 8.5, False, GRAY)
    node(s, 8.10, 1.80, 4.35, 1.05, "pwrite(fd, buf, len, off)", ORANGE, 9, sub="buf 只能是自己的内存")
    node(s, 8.10, 3.05, 4.35, 1.05, "process_vm_readv(pid, …)", PURPLE, 9, sub="pid 指定用谁的空间")
    T(s, 8.10, 4.35, 4.35, 1.2, "所以读 Guest 内存，remote 地址填的是\nFirecracker 的 HVA，不是 GVA/GPA。", 9, False, GRAY, ls=1.6)
    foot(s, "以为内核会自动按被读进程解释地址。", "remote_iov 里的地址属于谁？")
    np_()

    # 第2课 PVM 细节
    s = page(prs, BLUE); head(s, "第 2 课 · 细节", "四个参数，三个动作", np_(), "两个 iovec 数组都在调用者内存里")
    node(s, 0.90, 1.72, 5.4, 1.55, "", PURPLE, 9, fill=PALE)
    T(s, 1.06, 1.84, 5.0, 1.35,
      "process_vm_readv(\n"
      "    pid,        ← firecracker 的 PID\n"
      "    local_iov,  ← server 的缓冲区\n"
      "    remote_iov, ← 地址属于 firecracker\n"
      "    flags)      ← 0", 8.5, False, INK, ls=1.45)
    node(s, 6.70, 1.72, 5.75, 1.55, "", BLUE, 9, fill=PALE)
    T(s, 6.86, 2.02, 5.45, 1.1,
      "① 描述（构造 iovec，不复制）\n② 读取（内核复制一次）\n③ 写文件（writer）", 9, False, INK, ls=1.45)
    hflow(s, 0.90, 3.65, 11.55, [("正常", "填满"), ("短读", "源和目的同时前进"),
                                 ("EINTR", "重试"), ("零进展", "报错")], BLUE, 0.60, 0.26)
    T(s, 0.90, 4.70, 11.55, 1.3,
      "async 外壳不改变实现：方法标了 async，内部仍是同步的 process_vm_readv，不会自动让出 worker。\n"
      "边界：读成功只说明 buffer 拿到字节，不代表已封层、写文件或形成完整快照。", 9, False, GRAY, ls=1.6)
    foot(s, "把 async 方法当异步 IO。", "8192 只回 4096，下一次从哪继续？")
    np_()

    # 第3课 两条路径
    s = page(prs, BLUE); head(s, "第 3 课", "两条路径，一块物理内存", np_(), "memslot 是这两条路径的接线处")
    node(s, 1.30, 1.80, 1.9, 0.52, "GVA", BLUE, 9); node(s, 1.30, 2.55, 1.9, 0.52, "GPA", BLUE, 9)
    node(s, 5.55, 2.15, 2.2, 0.60, "HPA", PURPLE, 9.5, True)
    node(s, 9.30, 1.80, 1.9, 0.52, "HVA", PURPLE, 9)
    arrow_v(s, 2.25, 2.55, 2.25, BLUE); arrow_h(s, 3.25, 5.50, 2.81, BLUE)
    arrow_h(s, 9.25, 7.80, 2.06, PURPLE); arrow_v(s, 2.36, 2.15, 7.75, PURPLE)
    T(s, 2.40, 2.34, 1.1, 0.22, "页表", 7.5, False, GRAY)
    T(s, 3.05, 2.60, 1.1, 0.22, "EPT", 7.5, False, GRAY)
    T(s, 8.65, 2.34, 1.2, 0.22, "宿主页表", 7.5, False, GRAY)
    T(s, 0.90, 3.45, 11.5, 1.5,
      "登记：KVM_SET_USER_MEMORY_REGION(guest_phys_addr, userspace_addr, size)\n"
      "  → memslot 只是「GPA 区间 ↔ HVA 区间」的软件登记，不复制 RAM\n"
      "  → 访问到缺 EPT 项的页时，KVM 才按 memslot 算 HVA、取真实页、建 EPT 项", 9, False, GRAY, ls=1.7)
    node(s, 3.20, 5.15, 7.0, 0.50, "HVA = userspace_addr + (目标 GPA − guest_phys_addr)", BLUE, 9)
    foot(s, "以为登记时会复制一份 128 MiB。", "为什么 ioctl 里没有 HPA 参数？")
    np_()

    # ================= 02 =================
    s = page(prs, PURPLE); head(s, "02 / 执行与设备", "谁在跑指令，请求怎么传", np_(), "第 4—6 课")
    np_()

    # 第4课 KVM_RUN 循环
    s = page(prs, PURPLE); head(s, "第 4 课", "本质是一个 ioctl 的循环", np_(), "进去跑 Guest，撞到退出条件回来，处理完再进去")
    node(s, 1.10, 1.95, 2.5, 0.65, "ioctl(KVM_RUN)", PURPLE, 9, sub="阻塞")
    node(s, 4.30, 1.95, 2.6, 0.65, "硬件跑 Guest", PURPLE, 9, sub="非根模式")
    node(s, 7.60, 1.95, 2.2, 0.65, "VM-Exit", PURPLE, 9, sub="exit_reason")
    arrow_h(s, 3.65, 4.25, 2.27, PURPLE); arrow_h(s, 6.95, 7.55, 2.27, PURPLE)
    arrow_v(s, 2.60, 3.15, 8.70, PURPLE)
    node(s, 6.60, 3.15, 2.0, 0.62, "KVM 处理", GREEN, 9, sub="直接重入")
    node(s, 3.10, 3.15, 2.6, 0.62, "要用户态处理", ORANGE, 9, sub="KVM_RUN 返回")
    arrow_h(s, 4.35, 6.55, 3.46, LIGHT)
    T(s, 0.90, 4.15, 11.6, 1.7,
      "绿色那条：整个 ioctl 从头到尾没返回过——补一条 EPT 映射这类事，KVM 自己办完就重入。\n"
      "橙色那条：MMIO/PIO 这类它办不了的，才把控制权交回 Firecracker。\n"
      "所以「退出次数」和「被唤醒次数」不是一个数：前者看硬件，后者看是否必须回用户态。", 9, False, GRAY, ls=1.7)
    foot(s, "把 VM-Exit 次数当成 VMM 开销。", "EPT 缺页退出会让 FC 从 ioctl 返回吗？")
    np_()

    # 第5课 线程分工 + 暂停
    s = page(prs, PURPLE); head(s, "第 5 课", "「没被调度」不是「已暂停」", np_(), "单线程 VMM 的死结，与暂停的三个完成点")
    xs = [0.90, 2.95, 5.00, 7.05, 9.10, 11.15]
    ev = [("t1", "API 收到请求"), ("t2", "置暂停意图"), ("t3", "vCPU0 确认"),
          ("t4", "vCPU1 没被调度"), ("t5", "vCPU1 确认"), ("t6", "暂停完成")]
    for i, (t, d) in enumerate(ev):
        c = ORANGE if i == 3 else (GREEN if i < 3 or i == 4 else BLUE)
        node(s, xs[i], 1.85, 1.85, 0.70, t, c, 9, True, sub=d, lw=1.0 if i == 3 else 0.75)
        if i < 5: arrow_h(s, xs[i] + 1.85, xs[i+1], 2.20)
    T(s, 0.90, 3.00, 11.6, 1.2,
      "t4 是唯一难点：vCPU1 只是「没拿到 CPU」，调度器再给它时间片它就会继续写 Guest RAM。\n"
      "所以暂停必须等「全部 vCPU 确认」，而不是「请求发出」或「API 返回成功」。", 9, False, GRAY, ls=1.7)
    hflow(s, 0.90, 4.40, 11.55, [("请求发出", "写进 socket"), ("FC 接收", "API 线程解析"),
                                 ("全部确认", "没有 vCPU 能跑"), ("快照完成", "另一步")], PURPLE, 0.62, 0.28)
    foot(s, "把「暂停请求发出」当「VM 已停」。", "只暂停一个 vCPU 能叫 VM 暂停吗？")
    np_()

    # 第6课 VirtIO
    s = page(prs, PURPLE); head(s, "第 6 课", "队列在内存里，通知只提醒", np_(), "描述符 16 字节；avail 由 Guest 写，used 由设备写")
    node(s, 0.90, 1.80, 3.6, 1.35, "描述符表", PURPLE, 9.5, True,
         sub="addr / len / flags / next")
    node(s, 0.90, 3.45, 3.6, 1.05, "avail 环", GREEN, 9.5, True, sub="Guest 发布链头")
    node(s, 4.85, 3.45, 3.6, 1.05, "used 环", ORANGE, 9.5, True, sub="设备发布完成")
    arrow_h(s, 4.52, 4.80, 3.97, LIGHT)
    node(s, 8.85, 1.80, 3.55, 1.35, "设备后端", PURPLE, 9.5, True, sub="从 Guest RAM 取描述符")
    arrow_v(s, 2.70, 3.40, 2.70, LIGHT); arrow_v(s, 2.70, 3.40, 10.60, LIGHT)
    T(s, 0.90, 4.75, 11.5, 1.3,
      "通知（doorbell）只是「去检查队列」：不带包内容，一次通知可对应多项工作。\n"
      "所以：通知次数 ≠ 请求数；设备发布 used ≠ Guest 驱动已处理。", 9, False, GRAY, ls=1.7)
    foot(s, "把通知次数当请求数。", "VirtIO 相比模拟设备省掉了什么？")
    np_()

    # ================= 03 =================
    s = page(prs, GREEN); head(s, "03 / 控制与命令", "请求从哪进，结果怎么回", np_(), "第 7—9 课")
    np_()

    # 第7课 两通道
    s = page(prs, GREEN); head(s, "第 7 课", "控制面与数据面，两条通道", np_(), "HTTP 只是消息格式，它跑在 Unix socket 上")
    node(s, 0.90, 1.80, 5.5, 1.5, "控制面", GREEN, 10, True,
         sub="Unix socket · PATCH /vm\n不需要 Guest 配合")
    node(s, 6.80, 1.80, 5.55, 1.5, "数据面", ORANGE, 10, True,
         sub="virtqueue · 描述符/avail/used\n需要 Guest 驱动")
    T(s, 0.90, 3.55, 11.5, 1.3,
      "为什么暂停不能走数据面：暂停的用途之一，就是「Guest 不配合时也能停住它」。\n"
      "如果停机依赖 Guest 处理队列，那么 Guest 内核卡死时，宿主就永远停不下来。", 9, False, GRAY, ls=1.7)
    hflow(s, 0.90, 4.90, 11.55, [("发出", "写 socket"), ("接收", "API 解析"),
                                 ("执行", "vCPU 全停"), ("持久化", "另一件事")], GREEN, 0.58, 0.30)
    foot(s, "把 socket 当网络；把超时当失败。", "超时有哪三种可能？")
    np_()

    # 第8课 三层就绪
    s = page(prs, GREEN); head(s, "第 8 课", "三层就绪，一层比一层强", np_(), "进程在 → 网络通 → 应用能应答")
    tiers = [("API socket 可用", "能配 VM、能 pause", GREEN, 0.90),
             ("网络可达", "tap0 能到 Guest", GREEN, 4.75),
             ("envd /health", "应用层能应答", BLUE, 8.60)]
    for t, d, c, x in tiers:
        node(s, x, 1.80, 3.60, 1.05, t, c, 9.5, True, sub=d)
    T(s, 0.90, 3.30, 11.5, 1.0,
      "强度递进：进程存在只证明配置就绪；端口能连只证明监听在工作；health 通过才证明服务能处理请求。\n"
      "health 细节：状态码非 4xx/5xx 即通过，单次上限 1 秒，失败重试。", 9, False, GRAY, ls=1.7)
    node(s, 0.90, 4.75, 5.5, 0.55, "start_nowait()：只等 API socket", GREEN, 9)
    node(s, 6.80, 4.75, 5.55, 0.55, "wait_for_ready()：等 envd", BLUE, 9)
    foot(s, "把 health 通过当鉴权通过。", "端口能连、命令不能执行，卡在哪层？")
    np_()

    # 第9课 事件流
    s = page(prs, GREEN); head(s, "第 9 课", "exec 返回的是流，不是结果", np_(), "两个独立判断：事件是否收齐、退出码是多少")
    hflow(s, 0.90, 1.85, 11.55, [("start", "cmd+args+env"), ("Start", "pid"),
                                 ("Data", "stdout/stderr"), ("End", "exit_code")], GREEN, 0.72, 0.24)
    node(s, 0.90, 3.05, 5.5, 1.25, "判断一：事件收齐？", GREEN, 9.5, True,
         sub="Ok：收到 End / Err：流断了")
    node(s, 6.80, 3.05, 5.55, 1.25, "判断二：exit_code？", BLUE, 9.5, True,
         sub="0 / 非零")
    T(s, 0.90, 4.55, 11.5, 1.3,
      "成功要三样同时满足：wait 返回 Ok + 收到 End + exit_code 符合预期。\n"
      "只有 Start，说明进程被创建出来了——之后仍可能立刻失败、崩溃、被超时杀掉。", 9, False, GRAY, ls=1.7)
    foot(s, "看到 Start 就当成功。", "超时后终止失败，能断言进程退出吗？")
    np_()

    # ================= 04 =================
    s = page(prs, ORANGE); head(s, "04 / 存储", "文件怎么变成块读写", np_(), "第 10—12 课")
    np_()

    # 第10课 三个偏移
    s = page(prs, ORANGE); head(s, "第 10 课", "一条数据，三个坐标系", np_(), "文件偏移 ≠ 逻辑块号 ≠ 后端位置")
    hflow(s, 0.90, 1.85, 11.55, [("read()", "文件偏移 8 MiB"), ("ext4", "extent → LBA"),
                                 ("块层", "合并/排队"), ("virtio-blk", "描述符"), ("后端", "层文件")], ORANGE, 0.66, 0.22, 8)
    T(s, 0.90, 2.85, 11.5, 1.2,
      "页缓存命中时这次 read 可能不产生设备 IO；但路径解析、元数据仍可能产生 IO。\n"
      "块设备不认文件名：a.txt 只存在于 Guest 文件系统语义里。", 9, False, GRAY, ls=1.7)
    hflow(s, 0.90, 4.15, 11.55, [("写入", "进页缓存"), ("回写", "交给 virtio"),
                                 ("后端", "写层文件"), ("持久化", "fsync")], ORANGE, 0.60, 0.34)
    foot(s, "把 write 返回当持久化。", "一次 4 KiB 读可能读多少字节？")
    np_()

    # 第11课 分层
    s = page(prs, ORANGE); head(s, "第 11 课", "分层是覆盖映射", np_(), "从新到旧查，第一个有记录的就赢")
    layers = [("upper（可写）", "位置1 → 新值", GREEN, 1.80), ("增量（只读）", "位置3 → 显式零", ORANGE, 2.55),
              ("基层（只读）", "位置0/1/2 有数据", PURPLE, 3.30)]
    for t, d, c, y in layers:
        node(s, 0.90, y, 4.9, 0.56, t, c, 9, True, sub=d)
    T(s, 6.20, 1.78, 6.2, 0.26, "最终视图", 8, True, GRAY)
    cells = [("P0", "基层", PURPLE), ("P1", "upper", GREEN), ("P2", "显式零", ORANGE), ("P3", "显式零", ORANGE)]
    xx = 6.20
    for t, d, c in cells:
        node(s, xx, 2.10, 1.42, 0.72, t, c, 9, True, sub=d)
        xx += 1.52
    T(s, 6.20, 3.05, 6.2, 1.0,
      "「无记录」不是零 → 继续往下找（回落）\n"
      "「显式零」必须终止 → 否则暴露父层旧数据", 9, False, GRAY, ls=1.7)
    T(s, 0.90, 4.35, 11.5, 1.2,
      "叠加只能在索引层做：把层文件首尾拼接，只会得到 A/B/C/D/X/Y，表达不了「X 替换位置 1」。\n"
      "代价：一个逻辑读可能跨多段层内数据；后端读失败必须报错，不能当零。", 9, False, GRAY, ls=1.7)
    foot(s, "把「没记录」当零。", "父层有旧值、新状态应为零，能省略吗？")
    np_()

    # 第12课 ublk
    s = page(prs, ORANGE); head(s, "第 12 课", "内核给壳，用户态给内容", np_(), "三个节点：control / ublkcN / ublkbN")
    node(s, 0.90, 1.80, 3.2, 0.56, "/dev/ublk-control", ORANGE, 8.5, True, sub="创建/删除")
    node(s, 4.30, 1.80, 3.2, 0.56, "/dev/ublkcN", ORANGE, 8.5, True, sub="命令交接")
    node(s, 7.70, 1.80, 3.2, 0.56, "/dev/ublkbN", ORANGE, 8.5, True, sub="数据读写")
    hflow(s, 0.90, 3.10, 11.55, [("等待", "io_uring"), ("领取", "CQE 到"),
                                 ("解析", "OverlayBD"), ("提交", "COMMIT")], ORANGE, 0.62, 0.30)
    T(s, 0.90, 4.20, 11.5, 1.3,
      "「领取」的 CQE 只表示请求送到了 daemon，不表示数据读完——这是第 12 课最容易错的一步。\n"
      "daemon 是集中式的：不是每沙箱一个进程；OverlayBD 是它链接的库。", 9, False, GRAY, ls=1.7)
    foot(s, "把 FETCH 的完成当数据读完。", "daemon 挂了，这个节点会怎样？")
    np_()

    # ================= 05 =================
    s = page(prs, PURPLE); head(s, "05 / 内存与快照", "映射、COW、捕获、恢复", np_(), "第 13—18 课")
    np_()

    # 第13课 三态
    s = page(prs, PURPLE); head(s, "第 13 课", "映射了 ≠ 分配了 ≠ 复制了", np_(), "整门课最值钱的一句话")
    trio = [("mmap 之后", "只有 VMA，没有物理页", GREEN, 0.90),
            ("第一次读", "缺页：有页就映射，没页就取", ORANGE, 4.35),
            ("第一次写", "COW：复制私有副本", PURPLE, 7.80)]
    for t, d, c, x in trio:
        node(s, x, 1.80, 3.15, 1.15, t, c, 9.5, True, sub=d)
    T(s, 0.90, 3.20, 11.5, 1.5,
      "缺页三类：minor（页已在内存）、major（要读盘/换入）、非法访问（SIGSEGV）。写保护缺页不是非法访问。\n"
      "两种写语义：MAP_SHARED 写回共享缓存；MAP_PRIVATE 只影响自己的私有副本。", 9, False, GRAY, ls=1.7)
    node(s, 0.90, 4.85, 11.55, 0.55, "microVM 恢复：只读后端 + MAP_PRIVATE → 读共享页缓存，写才 COW", PURPLE, 9)
    foot(s, "以为 mmap 就占满物理内存。", "恢复后首次读与首次写分别发生什么？")
    np_()

    # 第13课 三层缺页
    s = page(prs, PURPLE); head(s, "第 13 课 · 细节", "三层缺页，三个处理者", np_(), "混在一起就解释不了延迟")
    hflow(s, 0.90, 1.85, 11.55, [("Guest 页表", "Guest 内核 · GVA→GPA"),
                                 ("EPT", "KVM · GPA→HPA"),
                                 ("宿主页表", "宿主内核 · HVA→HPA")], PURPLE, 0.85, 0.30, 8.5)
    T(s, 0.90, 3.00, 11.5, 1.4,
      "第一层缺页发生在 Guest 内部，宿主完全不知道（不需要 VM-Exit）。\n"
      "第二层是 EPT 缺项 → VM-Exit，但 KVM 常能自己补完（不返回用户态）。\n"
      "第三层是宿主自己的页缺失 → 可能是匿名页分配，也可能是文件页读入。", 9, False, GRAY, ls=1.7)
    node(s, 0.90, 4.70, 11.55, 0.55, "所以「恢复后很慢」要说是哪一层缺页，不能笼统说「缺页」", PURPLE, 9)
    foot(s, "把三层缺页算成一个缺页率。", "首条命令慢，你先查哪一层？")
    np_()

    # 第14课 四件套
    s = page(prs, PURPLE); head(s, "第 14 课", "快照是四件套", np_(), "缺一件就恢复不出一台能跑的机器")
    quad = [("VM 状态", "寄存器/设备", BLUE, 0.90, 1.80), ("内存镜像", "RAM 字节", PURPLE, 3.95, 1.80),
            ("磁盘视图", "层 + 父层引用", ORANGE, 7.00, 1.80), ("恢复配置", "层顺序/设备", GREEN, 10.05, 1.80)]
    for t, d, c, x, y in quad:
        node(s, x, y, 2.85, 0.95, t, c, 9.5, True, sub=d)
    T(s, 0.90, 3.05, 11.5, 0.32, "四件事还各在不同的时间点完成：", 9, False, GRAY)
    hflow(s, 0.90, 3.62, 11.55, [("暂停", "vCPU 全停"), ("捕获", "读内存/写层"),
                                 ("持久化", "fsync/上传"), ("释放", "回收运行时")], PURPLE, 0.58, 0.30)
    T(s, 0.90, 4.75, 11.5, 1.1,
      "为什么必须先暂停：抓取期间页在变，会拼出「从未同时存在」的状态。\n"
      "但暂停只停 Guest 的 CPU 写入；宿主设备侧仍可能在写同一块 RAM。", 9, False, GRAY, ls=1.7)
    foot(s, "把 pause 成功当快照成功。", "哪一步失败会导致「有文件但恢复不了」？")
    np_()

    # 第15课 增量
    s = page(prs, PURPLE); head(s, "第 15 课", "增量必须有基线", np_(), "「—」表示本层没管，要回落，不是零")
    x0, y0, cw, rh = 2.55, 1.85, 1.30, 0.50
    for i in range(6):
        T(s, x0 + i*cw, y0 - 0.30, cw, 0.24, "页%d" % i, 8, True, GRAY, PP_ALIGN.CENTER)
    rows = [("S0", ["A", "B", "C", "D", "E", "F"], PURPLE),
            ("S1", ["—", "B1", "—", "—", "E1", "—"], ORANGE),
            ("S2", ["—", "—", "—", "—", "E2", "F2"], ORANGE),
            ("视图", ["A", "B1", "C", "D", "E2", "F2"], GREEN)]
    for r, (name, vals, c) in enumerate(rows):
        T(s, 0.95, y0 + r*rh + 0.10, 1.4, 0.24, name, 9, True, c)
        for i, v in enumerate(vals):
            fill = PALE if v == "—" else WHITE
            node(s, x0 + i*cw, y0 + r*rh, cw - 0.10, rh - 0.10, v, c, 9, v != "—", fill=fill)
    T(s, 0.90, 4.50, 11.5, 1.4,
      "dirty（写过）、present（在不在）、内容为零 —— 三个不同概念。\n"
      "范围列表只说明「从哪取、存到哪」，它不冻结内容；一致性靠暂停与协调。", 9, False, GRAY, ls=1.7)
    foot(s, "以为 dirty 列表能保证一致快照。", "改回原值，dirty 会消失吗？")
    np_()

    # 第16课 PVM 参数
    s = page(prs, PURPLE); head(s, "第 16 课", "每个参数都要能说出归属", np_(), "两个数组都在调用者内存里")
    node(s, 0.90, 1.80, 5.6, 1.45, "", PURPLE, 9, fill=PALE)
    T(s, 1.06, 1.92, 5.2, 1.25,
      "pid        → firecracker\nlocal_iov  → server 的 buffer\n"
      "remote_iov → firecracker 的 HVA\nliovcnt    → 元素个数，不是字节", 8.5, False, INK, ls=1.5)
    hflow(s, 7.00, 1.80, 5.45, [("源", "Guest RAM 映射"), ("宿主", "内核复制"), ("目的", "server buffer")], PURPLE, 0.85, 0.24, 8)
    T(s, 7.00, 3.05, 5.45, 1.2, "之后才由 writer 写成层\n→ 「先读到 server 再写文件」是本实现的路径", 8.5, False, GRAY, ls=1.6)
    T(s, 0.90, 4.35, 11.5, 1.3,
      "边界：整段读完只说明 buffer 拿到字节，不代表已封层、写文件或形成完整快照。\n"
      "失败时 buffer 可能已有部分字节，但函数返回错误就不能当整段有效。", 9, False, GRAY, ls=1.7)
    foot(s, "把 remote 地址填成 GVA/GPA。", "短读时源和目的怎么前进？")
    np_()

    # 第17课 chunk
    s = page(prs, PURPLE); head(s, "第 17 课", "两条线：元数据与字节", np_(), "chunk 是任务批次，buffer 才是数据")
    node(s, 0.90, 1.80, 11.55, 0.52, "元数据：范围 → entry → 输出索引（逻辑范围 → 层内位置）", BLUE, 9)
    node(s, 0.90, 2.55, 11.55, 0.52, "字节：源 HVA → buffer → writer（buffer 寿命要覆盖写入）", ORANGE, 9)
    segs = [("header", 1.55, LIGHT), ("payload", 3.85, PALE), ("index", 2.30, PALE), ("trailer", 1.35, LIGHT)]
    xx = 0.90
    for name, w, c in segs:
        node(s, xx, 3.60, w, 0.50, name, GRAY, 9, True, fill=c)
        xx += w + 0.12
    T(s, 0.90, 4.35, 11.5, 1.3,
      "一个 chunk 不等于一次 syscall：源是 PVM 时，每个 entry 各走一遍读取。\n"
      "finalize 只保证格式完成；rename 只是换名字——都不等于断电持久化。", 9, False, GRAY, ls=1.7)
    foot(s, "把 finalize+rename 当持久化。", "两个 entry 是几次跨进程读？")
    np_()

    # 第18课 恢复
    s = page(prs, PURPLE); head(s, "第 18 课", "恢复不是把内存读回来", np_(), "共享只读设备 + MAP_PRIVATE + 按需缺页")
    vflow(s, 0.90, 1.72, 3.9, [("准备环境", "ublk/盘/网"), ("加载状态", "resume_vm=false"),
                               ("映射内存", "只读设备"), ("补配置", "卷/MMDS"), ("resume", "vCPU 继续")], PURPLE, 0.44, 0.18, 8.5)
    node(s, 5.30, 1.72, 7.15, 4.10, "", PURPLE, 9, fill=PALE)
    T(s, 5.50, 1.86, 6.75, 3.8,
      "冷恢复时，一页 RAM 怎么变得可访问\n\n"
      "Guest 访问 GPA → 宿主缺项\n"
      "　→ 向只读块设备发块读\n"
      "　→ daemon 查 OverlayBD 取这一块\n"
      "　→ 填进宿主页 → Guest 继续\n\n"
      "写这一页：COW 到私有层，共享镜像不动\n\n"
      "为什么先 resume_vm=false：\n"
      "把状态、设备、网络、额外盘都装好，\n"
      "最后才让 vCPU 跑起来。", 8.5, False, INK, ls=1.55)
    foot(s, "以为恢复会把全部内存读回宿主。", "首条命令慢，是故障还是正常？")
    np_()

    # ================= 06 =================
    s = page(prs, AMBER); head(s, "06 / 网络与隔离", "包怎么出去，门怎么关", np_(), "第 19—20 课")
    np_()

    # 第19课 出站
    s = page(prs, AMBER); head(s, "第 19 课", "出站：两层源 NAT", np_(), "每个 netns 都可以有自己的 tap0")
    hflow(s, 0.90, 1.85, 11.55, [("Guest eth0", "VirtIO"), ("tap0", "沙箱 netns"),
                                 ("SNAT", "改成 slot"), ("veth", "主 netns"), ("MASQ", "出口地址")], AMBER, 0.68, 0.24, 8)
    T(s, 0.90, 2.90, 11.5, 1.2,
      "TX 的 used 只表示发送缓冲可回收，不代表远端收到、更不代表业务成功。\n"
      "返回包靠 conntrack 逆变换，不是 server 每次读包再转发。", 9, False, GRAY, ls=1.7)
    hflow(s, 0.90, 4.20, 11.55, [("server", "slot 地址"), ("veth", "进 netns"),
                                 ("DNAT", "改 Guest IP"), ("tap0→FC", "VirtIO RX"), ("envd", "处理")], BLUE, 0.68, 0.24, 8)
    T(s, 0.90, 5.25, 11.5, 1.0, "入站这条：宿主访问 envd 走 DNAT，和出站的方向与规则都相反。", 9, False, GRAY, ls=1.7)
    foot(s, "以为同名 tap0 会冲突。", "恢复后旧 TCP 连接为什么可能不通？")
    np_()

    # 第19课 tap/veth + NAT 家族
    s = page(prs, AMBER); head(s, "第 19 课 · 细节", "tap 与 veth，DNAT 与 SNAT", np_(), "两组概念，四个名字")
    node(s, 0.90, 1.80, 5.4, 1.25, "tap", AMBER, 9.5, True, sub="用户态进程 ↔ 内核网络栈（二层帧）")
    node(s, 6.75, 1.80, 5.7, 1.25, "veth", AMBER, 9.5, True, sub="内核栈 ↔ 内核栈（两个 netns 之间）")
    node(s, 0.90, 3.35, 3.6, 1.05, "DNAT", BLUE, 9.5, True, sub="改目的（入口）")
    node(s, 4.75, 3.35, 3.6, 1.05, "SNAT", BLUE, 9.5, True, sub="改源（出口）")
    node(s, 8.60, 3.35, 3.85, 1.05, "REDIRECT", BLUE, 9.5, True, sub="DNAT 特例：改到本机")
    T(s, 0.90, 4.75, 11.5, 1.2,
      "DNAT 改完靠 conntrack 记住原值，回包再改回来——所以状态丢了，旧连接就断。\n"
      "MASQUERADE 是 SNAT 的特例：源地址取出口网卡当前地址。", 9, False, GRAY, ls=1.7)
    foot(s, "把 DNAT 当成转发。", "REDIRECT 与 DNAT 差在哪？")
    np_()

    # 第20课 四道门
    s = page(prs, AMBER); head(s, "第 20 课", "四类威胁，四道门", np_(), "先问防谁，再问用什么挡")
    quad = [("Guest 内作恶", "Guest 自己的内核挡", BLUE, 0.90, 1.80),
            ("VMM 被攻破", "seccomp/降权/chroot/caps", ORANGE, 6.80, 1.80),
            ("资源超用", "cgroup 限值/vCPU/balloon", GREEN, 0.90, 3.05),
            ("网络外连", "netns/veth/iptables/代理", PURPLE, 6.80, 3.05)]
    for t, d, c, x, y in quad:
        node(s, x, y, 5.6, 1.00, t, c, 9.5, True, sub=d)
    T(s, 0.90, 4.35, 11.5, 1.4,
      "namespace 改「看见什么」；cgroup 改「能用多少」；seccomp/caps/LSM 改「能对内核做什么」。\n"
      "三者互不替代：只做 namespace 等于什么都没锁；只做 seccomp 等于资源随便吃。", 9, False, GRAY, ls=1.7)
    foot(s, "把 namespace 当成降权。", "Guest 里的 root 会被 seccomp 拦吗？")
    np_()

    # 第20课 seccomp
    s = page(prs, AMBER); head(s, "第 20 课 · 细节", "seccomp 是线程级的", np_(), "它拦的是 VMM 发出的宿主 syscall")
    node(s, 0.90, 1.80, 5.5, 2.6, "", AMBER, 9, fill=PALE)
    T(s, 1.08, 1.94, 5.2, 2.3,
      "每个线程各装一份白名单\n\n"
      "vmm 线程　60 条\n"
      "api 线程　35 条\n"
      "vcpu 线程 43 条\n\n"
      "默认动作 trap：命中未允许 → SIGSYS", 9, False, INK, ls=1.6)
    node(s, 6.80, 1.80, 5.65, 2.6, "", ORANGE, 9, fill=PALE)
    T(s, 6.98, 1.94, 5.35, 2.3,
      "三个后果\n\n"
      "· Guest 内部 syscall 完全不受约束\n"
      "· 升级 VMM 引入新 syscall → 当场被杀\n"
      "· pids.max 挡不住 Guest 内 fork（只数宿主 task）", 9, False, INK, ls=1.6)
    T(s, 0.90, 4.65, 11.5, 1.0, "VMM 逃逸后还剩什么：seccomp 限 syscall、drop 降权、chroot 限视野、caps 去能力、netns 限网络。", 9, False, GRAY, ls=1.7)
    foot(s, "以为 seccomp 能约束 Guest。", "升级 FC 为什么可能直接崩？")
    np_()

    # ================= 07 =================
    s = page(prs, TEAL); head(s, "07 / 平台层", "资源、并发、失败、度量、池、取舍", np_(), "第 21—28 课")
    np_()

    # 第21课 资源
    s = page(prs, TEAL); head(s, "第 21 课", "谁拥有，谁释放", np_(), "创建与销毁要对得上")
    rows = [("netns / veth", "创建它的流程", "删除设备与 netns"),
            ("ublk 设备", "daemon（引用计数）", "最后一个句柄释放"),
            ("共享快照层", "模板/快照管理", "无引用后才可回收"),
            ("FC 进程", "server", "wait 回收，避免僵尸")]
    xx, yy = 0.90, 1.85
    for name, owner, rel in rows:
        node(s, xx, yy, 3.5, 0.52, name, TEAL, 8.5, True)
        node(s, xx + 3.75, yy, 3.6, 0.52, owner, GRAY, 8.5)
        node(s, xx + 7.60, yy, 3.85, 0.52, rel, GRAY, 8.5)
        yy += 0.66
    T(s, xx, 1.52, 3.5, 0.24, "对象", 7.5, True, GRAY)
    T(s, xx + 3.75, 1.52, 3.6, 0.24, "拥有者", 7.5, True, GRAY)
    T(s, xx + 7.60, 1.52, 3.85, 0.24, "释放条件", 7.5, True, GRAY)
    T(s, 0.90, 4.65, 11.5, 1.1, "中途失败最容易漏：创建到一半挂掉，网络设备和 cgroup 可能没人回收 → 泄漏成“幽灵沙箱”。", 9, False, GRAY, ls=1.7)
    foot(s, "以为引用消失＝资源已回收。", "envd 超时能说明 FC 退出了吗？")
    np_()

    # 第22课 async
    s = page(prs, TEAL); head(s, "第 22 课", "async 让出了什么", np_(), "只是让出线程，不改变底层是不是阻塞")
    node(s, 0.90, 1.80, 5.6, 1.6, "", ORANGE, 9, fill=PALE)
    T(s, 1.08, 2.05, 5.2, 1.2, "worker 线程被阻塞住\n其它任务排不上 → 不是并行", 9, False, INK, ls=1.6)
    node(s, 6.90, 1.80, 5.55, 1.6, "", GREEN, 9, fill=PALE)
    T(s, 7.08, 2.05, 5.2, 1.2, "提交后立即返回\n完成时唤醒 → worker 可干别的", 9, False, INK, ls=1.6)
    T(s, 0.90, 3.65, 11.5, 1.4,
      "buffer 寿命：提交出去的内存必须活到 IO 完成；否则可能写到别人的数据上。\n"
      "取消：取消不等于底层停止，仍要等完成或明确丢弃。", 9, False, GRAY, ls=1.7)
    foot(s, "把 async 当多线程。", "单 worker 下两个任务能交替吗？")
    np_()

    # 第23课 失败与恢复
    s = page(prs, TEAL); head(s, "第 23 课", "失败时状态不能乱跳", np_(), "Pausing / Paused / Resuming 各有前置条件")
    hflow(s, 0.90, 1.85, 11.55, [("Running", "正常执行"), ("Pausing", "等全部确认"),
                                 ("Paused", "可捕获"), ("Resuming", "重新加载")], TEAL, 0.72, 0.30)
    T(s, 0.90, 3.00, 11.5, 1.5,
      "跳步的后果：没确认就捕获 → 不一致；捕获失败就宣布 Paused → 状态与磁盘不符。\n"
      "重试要幂等：同一请求重放不能产生两份产物或两次副作用。", 9, False, GRAY, ls=1.7)
    node(s, 0.90, 4.55, 11.55, 0.55, "失败后要回答三个问题：现在是什么状态、残留了什么、下一步怎么安全推进", TEAL, 9)
    foot(s, "把「请求失败」当「状态未变」。", "捕获写了一半失败，回滚到哪一步？")
    np_()

    # 第24课 度量
    s = page(prs, TEAL); head(s, "第 24 课", "度量口径：先分类，再平均", np_(), "平均延迟相同的系统，体验可能完全不同")
    node(s, 0.90, 1.80, 3.6, 1.0, "wall", TEAL, 9.5, True, sub="墙上时间")
    node(s, 4.75, 1.80, 3.6, 1.0, "CPU", TEAL, 9.5, True, sub="谁在烧")
    node(s, 8.60, 1.80, 3.85, 1.0, "p50 / p99", TEAL, 9.5, True, sub="分布，不是均值")
    T(s, 0.90, 3.05, 11.5, 0.9,
      "冷启动要分段：拉镜像 / 建盘 / 起 VMM / 等 envd / 首条命令——每段都给 wall 与 CPU。\n"
      "「资源就绪」与「首条命令完成」是两个指标，不能混。", 9, False, GRAY, ls=1.7)
    x = 0.90
    for label, h in [("p50", 0.35), ("p90", 0.60), ("p99", 0.95), ("max", 1.25)]:
        node(s, x, 6.05 - h, 1.6, h, label, TEAL if label != "max" else ORANGE, 8, True, fill=PALE)
        x += 1.85
    T(s, 8.75, 4.95, 3.7, 0.7, "同一操作按「路径」分类统计，\n否则 p99 无法解释。", 8.5, False, GRAY, ls=1.6)
    foot(s, "只报平均值。", "wall 高而 CPU 低，说明什么？")
    np_()

    # 第25课 多节点 + 池
    s = page(prs, TEAL); head(s, "第 25 课", "多节点与预热池", np_(), "预热不等于就绪；路由元数据不等于实际状态")
    node(s, 0.90, 1.80, 2.6, 0.55, "gateway", TEAL, 9)
    node(s, 4.10, 1.80, 2.6, 0.55, "scheduler", TEAL, 9)
    node(s, 7.30, 1.80, 2.6, 0.55, "node A", TEAL, 9)
    node(s, 10.10, 1.80, 2.35, 0.55, "node B", TEAL, 9)
    arrow_h(s, 3.50, 4.05, 2.07); arrow_h(s, 6.70, 7.25, 2.07); arrow_h(s, 9.90, 10.05, 2.07)
    hflow(s, 0.90, 3.05, 11.55, [("池：FC 进程", "已起"), ("池：网络槽位", "已建"),
                                 ("池：磁盘设备", "已备"), ("就绪", "envd 探活")], TEAL, 0.60, 0.26)
    T(s, 0.90, 4.20, 11.5, 1.3,
      "预热省掉的是「创建」那几段，不免除「恢复装载」与「首命令」的代价。\n"
      "并发分配要靠原子认领：两个请求抢同一实例，只能有一个成功。", 9, False, GRAY, ls=1.7)
    foot(s, "以为查不到归属就说明沙箱退出了。", "预热完成后还缺哪几步？")
    np_()

    # 第26课 模板/fork
    s = page(prs, TEAL); head(s, "第 26 课", "模板、快照、实例、缓存", np_(), "同一个底座，四层含义")
    hflow(s, 0.90, 1.85, 11.55, [("模板", "只读底座"), ("快照", "某刻状态"),
                                 ("实例", "私有可变"), ("缓存", "本地副本")], TEAL, 0.66, 0.26)
    T(s, 0.90, 2.95, 11.5, 1.5,
      "从同一模板起 A、B：私有 RAM 与根盘改动互不影响；只有外部共享可写盘会互相看见。\n"
      "父层不能随意删：增量里「没记录」的范围要靠父层补回来。", 9, False, GRAY, ls=1.7)
    node(s, 0.90, 4.50, 11.55, 0.55, "克隆体要重随机化：PID、RNG、时钟、序列号、主机名/IP", TEAL, 9)
    foot(s, "以为 COW 能保证外部副作用只发生一次。", "A 改了文件，B 已读的字节会变吗？")
    np_()

    # 第27课 六条链
    s = page(prs, TEAL); head(s, "第 27 课", "六条链，一条主线", np_(), "每条的完成点都不一样")
    chains = [("创建", "spawn → 配置 → 启动", TEAL), ("执行", "envd → 进程 → 事件流", TEAL),
              ("读文件", "VFS → virtio → ublk → 层", TEAL), ("暂停", "请求 → 全确认", TEAL),
              ("恢复", "装载 → 映射 → resume", TEAL), ("销毁", "停进程 → 回收设备", TEAL)]
    x, y = 0.90, 1.85
    for i, (t, d, c) in enumerate(chains):
        node(s, x + (i % 3) * 3.95, y + (i // 3) * 1.25, 3.6, 0.95, t, c, 10, True, sub=d)
    T(s, 0.90, 4.55, 11.5, 1.2,
      "共同的主线：一个请求怎么落到硬件，再带着结果回到调用者。\n"
      "排障时先问：卡在哪一条链、哪一个完成点上？", 9, False, GRAY, ls=1.7)
    foot(s, "把「某层完成」当「整件事完成」。", "任选两条链，能说出全部完成点吗？")
    np_()

    # 第28课 取舍
    s = page(prs, TEAL); head(s, "第 28 课", "PVM 中转 vs 直接写出", np_(), "省一次搬运，不等于省一半时间")
    node(s, 0.90, 1.80, 5.6, 1.05, "现状：FC → PVM → server → writer", TEAL, 8.5, True)
    node(s, 6.90, 1.80, 5.55, 1.05, "候选：FC 直接用 HVA 写", ORANGE, 8.5, True)
    T(s, 0.90, 3.05, 11.5, 1.5,
      "省的是「server 侧中转」，不是零拷贝：普通缓冲写仍有复制，且格式/索引/稀疏仍要有人做。\n"
      "方案 A「先导出原始 RAM 再转换」会新增中间文件与二次读取，可能抵消收益。", 9, False, GRAY, ls=1.7)
    node(s, 0.90, 4.55, 11.55, 0.75, "假设总 10 ms、PVM 2 ms：最乐观也只到 8 ms（-20%），不是减半", TEAL, 9.5, True)
    foot(s, "把组件间搬 CPU 当成减少总量。", "怎么设计 A/B 才算公平？")
    np_()

    # ================= 08 面试 =================
    s = page(prs, INK); head(s, "08 / 面试", "五个必深点", np_(), "其余只需 15 秒速答")
    pts = [("地址空间", "四条线 + PVM 参数", "一次读取的字节与耗时", BLUE),
           ("VM-Exit", "MMIO/PIO + exit_reason", "一次压测的退出次数", PURPLE),
           ("快照恢复", "四件套 + 共享/COW/按需", "冷热恢复延迟", VIOLET),
           ("隔离", "四道门 + 线程级 seccomp", "线程数与 Seccomp 值", AMBER),
           ("度量", "wall/CPU/p50/p99", "分段耗时表", TEAL)]
    y = 1.85
    for t, d, e, c in pts:
        node(s, 0.90, y, 2.6, 0.58, t, c, 9.5, True)
        T(s, 3.70, y + 0.18, 4.6, 0.26, d, 8.5, False, GRAY)
        T(s, 8.50, y + 0.18, 3.9, 0.26, "证据：" + e, 8.5, False, ORANGE)
        y += 0.70
    foot(s, "只讲机制，没有证据。", "哪几点你能立刻拿出数字？")
    np_()

    # 四段式
    s = page(prs, INK); head(s, "08 / 面试", "四段式：缺第 4 段就是只背过", np_())
    seg = [("结论", "一句话判断", 1.85), ("机制", "谁在哪层做什么", 2.85),
           ("边界", "挡不住什么、代价", 3.85), ("证据", "数字/实测/故障", 4.85)]
    for t, d, y in seg:
        node(s, 0.90, y, 2.4, 0.58, t, INK, 9.5, True)
        T(s, 3.55, y + 0.16, 3.4, 0.26, d, 8.5, False, GRAY)
    node(s, 7.60, 1.85, 4.85, 3.58, "", GRAY, 9, fill=PALE)
    T(s, 7.80, 2.00, 4.5, 3.3,
      "示范：你们沙箱怎么隔离？\n\n"
      "结论：两类——防 Guest 越界、\n防 VMM 被攻破后的破坏力。\n\n"
      "机制：Guest↔宿主靠硬件虚拟化；\nVMM 靠 seccomp/namespace/cgroup。\n\n"
      "边界：namespace 不改权限；\nseccomp 拦不到 Guest 内 syscall。\n\n"
      "证据：一份真实实现里 VMM 用\nunshare -m + ip netns exec 启动，\n没有 jailer、cgroup 只记账。", 8, False, INK, ls=1.5)
    foot(s, "只报平均值不报分位数。", "90 秒讲完「VM-Exit」，能吗？")
    np_()

    # 收尾
    s = page(prs, INK); head(s, "下一步", "把「讲过」变成「做过」", np_())
    todo = [("还没演练", "地址空间、性能度量", BLUE),
            ("还没跑", "/dev/kvm、namespace 耗时、cgroup 限额", ORANGE),
            ("还没有", "冷/热恢复延迟、PVM 耗时、退出次数", VIOLET),
            ("还没写", "第 21—28 课面试格式、三篇项目故事", GREEN)]
    y = 1.90
    for t, d, c in todo:
        node(s, 0.90, y, 2.4, 0.56, t, c, 9, True)
        T(s, 3.55, y + 0.16, 8.9, 0.26, d, 9, False, GRAY)
        y += 0.72
    T(s, 0.90, 4.95, 11.5, 0.6, "下一个动作：在 WSL 里跑 ls -l /dev/kvm。", 10, True, INK)
    foot(s, "只看不测。", "下周补哪个数字？")
    np_()

    prs.save(path)
    print("saved:", path, "slides:", len(prs.slides))

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "review_v4.pptx")
