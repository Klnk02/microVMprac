# -*- coding: utf-8 -*-
"""生成 AgentENV 全课复习 PPT。用法：python build_review_ppt.py <输出路径>"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

FONT = "Microsoft YaHei"
C_BG = RGBColor(0xFF, 0xFF, 0xFF)
C_INK = RGBColor(0x1F, 0x23, 0x28)
C_DIM = RGBColor(0x6B, 0x77, 0x85)
C_LINE = RGBColor(0xDD, 0xE2, 0xE8)
C_SOFT = RGBColor(0xF5, 0xF7, 0xFA)

def set_font(run, size, bold=False, color=C_INK, name=FONT):
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

def textbox(slide, x, y, w, h, text, size, bold=False, color=C_INK, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run(); r.text = text
    set_font(r, size, bold, color)
    return tb

def rect(slide, x, y, w, h, fill=None, line=None, radius=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line; sh.line.width = Pt(1)
    sh.shadow.inherit = False
    if radius:
        try:
            sh.adjustments[0] = 0.08
        except Exception:
            pass
    return sh

def slide_blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def add_page_no(slide, n):
    textbox(slide, 12.1, 7.05, 0.9, 0.3, str(n), 10, False, C_DIM, PP_ALIGN.RIGHT)

def cover(prs, title, sub, meta):
    s = slide_blank(prs)
    rect(s, 0, 0, 13.333, 7.5, fill=RGBColor(0x0F, 0x12, 0x16))
    rect(s, 0.9, 2.3, 0.09, 1.5, fill=RGBColor(0x58, 0xA6, 0xFF))
    textbox(s, 1.2, 2.25, 10.5, 0.9, title, 40, True, RGBColor(0xE6, 0xED, 0xF3))
    textbox(s, 1.2, 3.2, 10.5, 0.6, sub, 18, False, RGBColor(0x9A, 0xA7, 0xB4))
    textbox(s, 1.2, 4.05, 10.5, 0.5, meta, 12, False, RGBColor(0x6B, 0x77, 0x85))
    return s

def section(prs, num, title, sub, color, page):
    s = slide_blank(prs)
    rect(s, 0, 0, 13.333, 7.5, fill=color)
    textbox(s, 1.0, 2.35, 3.0, 1.2, num, 64, True, RGBColor(0xFF, 0xFF, 0xFF))
    textbox(s, 3.4, 2.62, 8.5, 0.9, title, 34, True, RGBColor(0xFF, 0xFF, 0xFF))
    textbox(s, 3.45, 3.62, 8.5, 0.6, sub, 15, False, RGBColor(0xF2, 0xF6, 0xFA))
    textbox(s, 12.1, 7.05, 0.9, 0.3, str(page), 10, False, RGBColor(0xF2, 0xF6, 0xFA), PP_ALIGN.RIGHT)
    return s

def content(prs, kicker, title, points, pitfall, question, color, page):
    s = slide_blank(prs)
    rect(s, 0, 0, 13.333, 0.16, fill=color)
    textbox(s, 0.85, 0.55, 11.6, 0.35, kicker, 12, True, color)
    textbox(s, 0.85, 0.92, 11.6, 0.95, title, 27, True, C_INK)
    rect(s, 0.85, 1.98, 11.63, 0.012, fill=C_LINE)

    y = 2.25
    for p in points:
        rect(s, 0.9, y + 0.14, 0.09, 0.09, fill=color)
        tb = s.shapes.add_textbox(Inches(1.18), Inches(y), Inches(11.1), Inches(0.9))
        tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = 0; tf.margin_top = 0
        r = tf.paragraphs[0].add_run(); r.text = p
        n = len(p)
        size = 15.5 if n <= 42 else (14.0 if n <= 54 else 12.5)
        set_font(r, size, False, C_INK)
        y += 0.72 if n > 54 else 0.64

    # 易错
    base = 5.28
    rect(s, 0.85, base, 5.72, 1.42, fill=RGBColor(0xFF, 0xF6, 0xEE), line=RGBColor(0xF0, 0x88, 0x3E), radius=True)
    textbox(s, 1.05, base + 0.12, 5.3, 0.3, "易错", 12, True, RGBColor(0xB5, 0x54, 0x09))
    tb = s.shapes.add_textbox(Inches(1.05), Inches(base + 0.44), Inches(5.3), Inches(0.9))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = pitfall
    set_font(r, 12.5, False, RGBColor(0x4A, 0x3A, 0x2E))

    # 会被问
    rect(s, 6.76, base, 5.72, 1.42, fill=RGBColor(0xEF, 0xF6, 0xFF), line=RGBColor(0x58, 0xA6, 0xFF), radius=True)
    textbox(s, 6.96, base + 0.12, 5.3, 0.3, "会被问", 12, True, RGBColor(0x0B, 0x5C, 0xAD))
    tb = s.shapes.add_textbox(Inches(6.96), Inches(base + 0.44), Inches(5.3), Inches(0.9))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = question
    set_font(r, 12.5, False, RGBColor(0x24, 0x3B, 0x53))
    add_page_no(s, page)
    return s

def table_slide(prs, kicker, title, header, rows, color, page, widths=None, note=None):
    s = slide_blank(prs)
    rect(s, 0, 0, 13.333, 0.16, fill=color)
    textbox(s, 0.85, 0.55, 11.6, 0.35, kicker, 12, True, color)
    textbox(s, 0.85, 0.92, 11.6, 0.6, title, 26, True, C_INK)

    nrows = len(rows) + 1
    ncols = len(header)
    top = 1.85
    height = min(0.52, (5.4 - (0.55 if note else 0)) / nrows)
    shape = s.shapes.add_table(nrows, ncols, Inches(0.85), Inches(top), Inches(11.63), Inches(height * nrows))
    tbl = shape.table
    if widths:
        for i, w in enumerate(widths):
            tbl.columns[i].width = Inches(w)
    for j, h in enumerate(header):
        cell = tbl.cell(0, j)
        cell.fill.solid(); cell.fill.fore_color.rgb = color
        cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.03); cell.margin_bottom = Inches(0.03)
        tf = cell.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run(); r.text = h
        set_font(r, 12.5, True, RGBColor(0xFF, 0xFF, 0xFF))
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if i % 2 else C_SOFT
            cell.margin_left = Inches(0.08); cell.margin_top = Inches(0.02); cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run(); r.text = val
            set_font(r, 11.5, j == 0, C_INK if j == 0 else RGBColor(0x30, 0x3A, 0x45))
    if note:
        textbox(s, 0.85, 6.62, 11.6, 0.4, note, 11, False, C_DIM)
    add_page_no(s, page)
    return s

def build(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    BLUE = RGBColor(0x1F, 0x6F, 0xEB)
    PURPLE = RGBColor(0x89, 0x57, 0xE5)
    GREEN = RGBColor(0x2E, 0xA0, 0x43)
    ORANGE = RGBColor(0xDB, 0x6D, 0x28)
    VIOLET = RGBColor(0xA3, 0x71, 0xF7)
    AMBER = RGBColor(0xD2, 0x99, 0x22)
    CYAN = RGBColor(0x58, 0xA6, 0xFF)

    p = 0
    def nxt():
        nonlocal p
        p += 1
        return p

    cover(prs, "AgentENV 沙箱全课复习",
          "20 讲 · 一条链路 · 五个必深点",
          "基线 9f62cbe07cebfecf416dc9bdcf497e2a97687644   |   整理于 2026-11-13   |   用途：面试复盘")

    nxt()
    content(prs, "使用说明", "怎么用这份复习", [
        "每页固定四块：一句话结论 / 机制要点 / 易错 / 会被问——照着这个顺序自问自答",
        "第一轮按节通读；第二轮只看「易错」；第三轮只看「会被问」，答不出的回头查",
        "全课一条主线：一个请求怎么落到硬件，再带着结果回到调用者",
        "所有「完成」都要问一句：这是哪一层完成了？下一层知道吗？",
    ], "把「讲过」当「掌握」。这份 PPT 只覆盖已核对的内容，未实测的地方都标了边界。",
       "你能否用四段式（结论→机制→边界→证据）讲完任意一页？", CYAN, nxt())

    nxt()
    table_slide(prs, "全景", "系统地图：谁在哪里", ["对象", "位置", "一句话职责"], [
        ["AgentENV server", "宿主用户态进程", "生命周期、快照、控制面"],
        ["Firecracker", "宿主用户态进程", "VMM：vCPU 线程 + 设备模型 + API socket"],
        ["ublk-daemon", "宿主用户态进程（集中式）", "块设备服务；OverlayBD 是它链接的库"],
        ["Guest envd", "Guest 内服务", "执行命令、回传 stdout 与退出码"],
        ["Guest 应用", "Guest 内进程", "真正干活的程序，PID 由 Guest 内核分配"],
        ["KVM", "宿主内核", "运行 vCPU、维护 EPT"],
        ["ublk 驱动", "宿主内核", "提供 /dev/ublkbN 的请求队列"],
    ], BLUE, nxt(), widths=[2.9, 3.4, 5.3], note="关键：Guest 里的程序不是 Firecracker 的原生子进程；宿主 ps 看不到。")

    nxt()
    table_slide(prs, "全景", "四把尺子：地址到底属于谁", ["名称", "谁观察", "含义与用途"], [
        ["GVA", "Guest 程序", "Guest 虚拟地址；经 Guest 页表翻译"],
        ["GPA", "Guest 内核", "Guest 以为的物理地址；经 EPT 翻译"],
        ["HVA", "某个宿主进程", "必须说明属于哪个进程，如 Firecracker 的 mmap 区"],
        ["HPA", "物理机器", "真正的内存条位置"],
    ], BLUE, nxt(), widths=[1.9, 3.2, 6.5], note="Guest 访存：GVA→GPA→HPA。Firecracker 访存：HVA→HPA。两条路可落在同一物理页。")

    nxt()
    table_slide(prs, "全景", "三条容易混的边界", ["边界", "发生了什么", "必然切换宿主线程？"], [
        ["KVM_RUN 系统调用", "Firecracker 用户态 → 宿主内核", "否"],
        ["VM-Entry / VM-Exit", "Guest 与宿主执行环境切换", "否"],
        ["宿主线程切换", "调度器换另一个线程执行", "是"],
    ], BLUE, nxt(), widths=[3.2, 5.6, 2.8], note="VM-Exit 回到宿主内核 ≠ KVM_RUN 已返回用户态。KVM 可以处理完再直接重入 Guest。")

    section(prs, "01", "位置与地址", "第 1—3 课：谁在哪里，指针属于谁", BLUE, nxt())

    nxt()
    content(prs, "第 1 课", "谁在哪里", [
        "Firecracker 是宿主用户态进程；它借 KVM 运行 Guest，不是 Guest 的一部分",
        "一个 Firecracker 进程内有多种线程：vmm 主线程、api 线程、fc_vcpu 0..N-1",
        "线程名来自代码里的 .name(\"fc_vcpu {index}\")，所以 ps -eLf 能看到",
        "Guest 里的进程由 Guest 内核分配 PID，宿主进程表里没有它们",
    ], "把 server 里的 FirecrackerInstance 对象当成进程；把宿主 PID 当成 Guest PID。",
       "宿主 ps 能看到 Guest 里的 python 吗？它的 PID 谁分配？", BLUE, nxt())

    nxt()
    content(prs, "第 2 课", "指针属于谁", [
        "同一个数字地址在两个进程里可以指向不同物理页——地址离开地址空间没有意义",
        "pwrite(fd, buf, ...) 的 buf 永远按调用者自己的地址空间解释，没有远程进程参数",
        "process_vm_readv(pid, local_iov, remote_iov, ...) 才把「去哪个进程取」说清楚",
        "两个 iovec 数组本身都在调用者内存；只有 remote_iov 里的地址指向目标进程",
    ], "以为内核会自动按被读进程解释地址；把 remote_iov 参数指针误填成目标进程地址。",
       "读 Guest 内存时，remote address 应该填 GVA、GPA 还是 HVA？", BLUE, nxt())

    nxt()
    content(prs, "第 3 课", "Guest 内存与宿主映射", [
        "KVM_SET_USER_MEMORY_REGION 登记的是「GPA 范围 ↔ 某进程 HVA」的对应，不搬字节",
        "memslot 是软件登记；EPT 是硬件表，缺项时按需建立",
        "所以调用者只填 GPA 起点、HVA 起点、长度——不需要也不该填 HPA",
        "Guest 正常访存不经过 HVA；HVA 只属于 Firecracker 自己的那条路径",
    ], "以为登记时把 128 MiB 复制了一份；以为 Guest 访存会经过 HVA。",
       "为什么 ioctl 不需要你填 HPA？页面还没驻留时谁负责准备？", BLUE, nxt())

    section(prs, "02", "执行与设备", "第 4—6 课：谁在跑指令，请求怎么传", PURPLE, nxt())

    nxt()
    content(prs, "第 4 课", "谁在执行 Guest 指令", [
        "vCPU 线程调 ioctl(vcpu_fd, KVM_RUN)，硬件进入非根模式执行 Guest",
        "撞到退出条件 → VM-Exit → 硬件把现场存进 VMCS，KVM 在根模式处理",
        "KVM 能自己处理就处理完直接重入；需要用户态才让 KVM_RUN 返回",
        "退出原因不只看「Guest 是否主动请求设备」，还有中断、EPT 缺页等",
    ], "把 VM-Exit 等同于 KVM_RUN 返回；以为两个 vCPU 永久独占两个物理核。",
       "KVM_RUN 的返回值与 kvm_run->exit_reason 是什么关系？", PURPLE, nxt())

    nxt()
    content(prs, "第 5 课", "Firecracker 线程与暂停", [
        "单线程 VMM 会死锁：vCPU 线程卡在 KVM_RUN 时没人接控制请求",
        "所以拆成 api / vmm / vcpu 三类线程，各自职责不同",
        "「未获调度」是调度状态，「已暂停」是协议状态——两者不同",
        "暂停一个 vCPU 不等于 VM 已暂停：另一个 vCPU 还在写同一块 Guest RAM",
    ], "把暂停请求发出、Firecracker 接收、全部 vCPU 确认混为一件事。",
       "为什么暂停控制不能走 virtqueue？", PURPLE, nxt())

    nxt()
    content(prs, "第 6 课", "VirtIO：描述符、双环、通知", [
        "描述符 16 字节：addr(GPA) / len / flags / next，可串成链描述不连续缓冲区",
        "两个环：avail 由 Guest 发布，used 由设备发布，都在 Guest RAM 里",
        "通知只是提醒对方「去检查队列」，不携带数据，也不代表一次只处理一项",
        "同一链头发布两次＝两次使用机会，不是同一个包发两次",
    ], "把通知次数当请求数；把「设备发布了 used」当成「Guest 驱动已处理」。",
       "VirtIO 为什么比模拟真实设备快？批量体现在哪？", PURPLE, nxt())

    section(prs, "03", "控制与命令", "第 7—9 课：一条请求从哪里进，结果怎么回来", GREEN, nxt())

    nxt()
    content(prs, "第 7 课", "请求控制路径", [
        "控制面：宿主 Unix socket + Firecracker REST（PATCH /vm, state=Paused）",
        "数据面：Guest 内存里的 virtqueue + 通知",
        "HTTP 只是消息格式，它跑在 Unix socket 上，不走 TCP、不经过 Guest 网卡",
        "超时有三种可能：没送到 / 送成了响应没回来 / 还没做完",
    ], "把 FirecrackerInstance.pause() 当成「进入 Guest 执行」；把 socket 当网络。",
       "控制面为什么不能依赖 Guest 配合？", GREEN, nxt())

    nxt()
    content(prs, "第 8 课", "启动与就绪：三层收紧", [
        "第一层：进程与 API socket 可用 → 能配 VM、能 pause",
        "第二层：网络可达 → 宿主经 tap0 能到 Guest",
        "第三层：envd GET /health 返回非 4xx/5xx（不校验响应体，单次最多 1 秒）",
        "start_nowait 只等 API socket；wait_for_ready 才等 envd",
    ], "以为对象创建＝服务就绪；以为 health 通过＝受保护命令的鉴权也通过。",
       "「端口能连」和「服务就绪」差在哪？", GREEN, nxt())

    nxt()
    content(prs, "第 9 课", "命令执行与事件流", [
        "请求走 envd gRPC，返回的是流：Start(pid) / Data / End(exit_code)",
        "命令与参数分开传，不假设过 shell（没有管道、通配符、重定向）",
        "wait 有两个独立判断：事件是否收齐（协议层）、退出码是多少（程序层）",
        "wait 返回 Ok 只说明「取得了结果」，不代表程序成功",
    ], "把 Start 事件当成功；把「超时后终止失败」当成「进程一定还在」。",
       "判断一次 exec 成功，至少要同时看哪三样？", GREEN, nxt())

    section(prs, "04", "存储", "第 10—12 课：文件怎么变成块设备", ORANGE, nxt())

    nxt()
    content(prs, "第 10 课", "文件、文件系统与块设备", [
        "三个偏移不能混：文件偏移（文件系统）、LBA（块设备）、后端实际位置（宿主）",
        "块设备只认逻辑地址和长度，不认文件名；a.txt 只存在于 Guest 文件系统",
        "页缓存命中可以免掉设备 IO，但路径解析、元数据仍可能产生 IO",
        "write 返回只代表数据进了页缓存，不等于落到介质",
    ], "以为文件偏移 0 就是磁盘偏移 0；以为 write 返回＝持久化。",
       "一次 4 KiB 读，实际可能从盘上读多少字节？", ORANGE, nxt())

    nxt()
    content(prs, "第 11 课", "OverlayBD：分层与索引", [
        "每层有一张索引：逻辑位置 → 本层偏移。读取时自上而下，第一个有记录的就赢",
        "「无记录」不是零，它表示继续往下一层找（回落）",
        "「显式零」必须终止查找，否则会把下层的旧数据暴露出来",
        "叠加是覆盖映射；把层文件首尾拼接表达不了「新层替换某个位置」",
    ], "以为 OverlayBD 是数据库或 OverlayFS；以为逻辑偏移等于层内偏移。",
       "新层某位置「没记录」，读出来是零吗？为什么？", ORANGE, nxt())

    nxt()
    content(prs, "第 12 课", "ublk 与存储 daemon", [
        "分工：内核给壳（/dev/ublkbN + 请求队列），用户态给内容",
        "三个节点：ublk-control（管理）、ublkcN（命令交接）、ublkbN（数据）",
        "创建流程：server 发 Create → 内核分配 N → 等节点「真正可打开」→ 回 (dev_id, path)",
        "FETCH_REQ 的 CQE 只代表「请求送到」，不代表数据已读出",
    ], "以为每个沙箱一个 daemon；以为设备号固定；把 daemon 和 OverlayBD 当两个服务。",
       "daemon 挂了，这个节点上所有沙箱会怎样？", ORANGE, nxt())

    section(prs, "05", "内存与快照", "第 13—18 课：映射、COW、捕获、恢复", VIOLET, nxt())

    nxt()
    content(prs, "第 13 课", "mmap、缺页与 COW", [
        "mmap 只建立虚拟范围（VMA）；分配物理页是缺页时才发生",
        "缺页分 minor（页已在内存）与 major（要读盘/换入）；写保护缺页是正常的 COW 处理",
        "MAP_SHARED 写回共享缓存；MAP_PRIVATE 的写只影响自己的私有副本",
        "核心结论：映射了 ≠ 分配了 ≠ 复制了",
    ], "以为 mmap 128 MiB 就占 128 MiB 物理内存；以为 COW 一定发生复制。",
       "恢复后 Guest 第一次读某页 vs 第一次写某页，分别发生什么？", VIOLET, nxt())

    nxt()
    content(prs, "第 14 课", "快照要保存什么", [
        "四件套：VM 状态（寄存器/设备）+ 内存镜像 + 磁盘视图 + 恢复配置与索引",
        "顺序：pause → snapshot_to_dir → state-only 状态 + 脏内存范围 → 组合父层 → 写 manifest",
        "四件事必须分开：暂停、捕获、持久化、释放运行时",
        "VM 内部一致 ≠ 应用事务已提交（外部支付/数据库不随快照回滚）",
    ], "pause 成功就当快照成功；单个文件写成功就当整套产物可用。",
       "为什么必须先暂停全部 vCPU 再捕获内存？", VIOLET, nxt())

    nxt()
    content(prs, "第 15 课", "保存范围、脏页与父层", [
        "增量必须有基线：S0 全量，S1/S2 只记覆盖，完整视图靠回落组合",
        "dirty 表示「被记录为写过」，不保证内容与父层不同；改回原值可能仍是脏",
        "范围描述只说明「从哪取、存到逻辑哪里」，不冻结内容",
        "image_offset 是完整镜像里的逻辑位置，不是层文件最终存放位置",
    ], "以为 dirty 列表能保证一致快照；以为页粒度等于读取请求粒度。",
       "父层有旧内容、新状态应为零时，能不能省略这条覆盖记录？", VIOLET, nxt())

    nxt()
    content(prs, "第 16 课", "pause 时的跨进程读取", [
        "调用者 server；remote PID = Firecracker；remote address = Firecracker HVA",
        "read_exact_remote 循环：EINTR 重试、短读时源和目的同时前进、零进展报错",
        "两个 iovec 数组都在调用者内存；liovcnt/riovcnt 是元素个数，不是字节数",
        "方法虽标 async，内部仍直接调同步 process_vm_readv，不会自动让出 worker",
    ], "以为 async 方法就是异步 IO；以为读成功＝已持久化。",
       "请求 8192 字节只返回 4096，下一次从哪里继续？", VIOLET, nxt())

    nxt()
    content(prs, "第 17 课", "chunk 写出与快照封存", [
        "三个对象分清：entry（一段范围描述）、chunk（一批 entry）、buffer（实际字节）",
        "两条线：元数据（范围→entry→输出索引）与 payload（源 HVA→buffer→writer）",
        "compact_to 写 header/payload/index/trailer；finalize 只保证格式完成",
        "publish 用临时路径 → rename；rename 不等于断电持久化",
    ], "以为一个 chunk 等于一次 process_vm_readv；以为 finalize 成功＝快照已持久化。",
       "一个 chunk 有两个 entry，是几次跨进程读？为什么？", VIOLET, nxt())

    nxt()
    content(prs, "第 18 课", "从快照恢复", [
        "两种恢复：原地 resume（运行时还在）vs 从快照重建（重新准备运行环境）",
        "重建链：检查 ublk → 备盘/网 → load_snapshot_file(resume_vm=false) → resume",
        "内存不是「先读回 server 再写进 Firecracker」；主路径是映射只读内存设备 + 私有映射 COW",
        "按需加载：恢复成功 ≠ 所有页已在宿主 RAM",
    ], "以为恢复＝把所有内存读回来；以为恢复 VM 就恢复了外部连接。",
       "恢复后首条命令很慢、内存指标却不高，怎么解释？", VIOLET, nxt())

    section(prs, "06", "网络与隔离", "第 19—20 课：包怎么出去，门怎么关", AMBER, nxt())

    nxt()
    content(prs, "第 19 课", "网络包怎样出去", [
        "路径：Guest eth0 → VirtIO → TAP → 沙箱 netns → SNAT → veth → 主 netns → MASQUERADE",
        "宿主到 envd 是另一条：veth → PREROUTING DNAT → tap0 → VirtIO RX → envd",
        "80/443 可被 REDIRECT 到出口代理，按 Host/SNI 判断；不终止 TLS、不改写 HTTP",
        "TX 的 used 只说明发送缓冲可回收，不代表远端收到或业务成功",
    ], "以为同名 tap0 会冲突（不同 netns 各有一套）；以为恢复 Guest socket 就能续上旧连接。",
       "快照恢复后，一条旧 TCP 连接为什么可能不通？", AMBER, nxt())

    nxt()
    content(prs, "第 20 课", "各种隔离分别限制什么", [
        "四类威胁对四道门：Guest 内部 / VMM 被攻破 / 资源超用 / 网络外连",
        "namespace 改「看见什么」，cgroup 改「能用多少」，seccomp/caps/LSM 改「能对内核做什么」",
        "seccomp 是线程级白名单，拦的是 VMM 发出的宿主 syscall，拦不到 Guest 内部 syscall",
        "cgroup 只记账不设 memory.max/cpu.max 时，资源超用一道门等于没有",
    ], "以为 pids.max 能挡 Guest 内 fork bomb（它只数宿主 task）；以为 namespace 等于降权。",
       "Guest 里的 root 执行任意 syscall，会被 Firecracker 的 seccomp 拦住吗？", AMBER, nxt())

    section(prs, "07", "面试", "五个必深点 · 四段式 · 追问链", CYAN, nxt())

    nxt()
    table_slide(prs, "面试", "五个必深点：能讲 5 分钟才算过", ["深点", "你要能说清", "必备证据"], [
        ["地址空间", "GVA/GPA/HVA/HPA 四条线 + PVM 参数归属", "一次跨进程读的字节数与耗时"],
        ["VM-Exit 分流", "MMIO 靠 EPT 缺映射、PIO 靠敏感指令；exit_reason 怎么分流", "一次压测里的退出次数"],
        ["快照与恢复", "四件套、一致性、只读层 + COW + 按需加载", "冷/热恢复延迟对比"],
        ["隔离各层", "namespace/cgroup/seccomp/降权 各挡什么、漏什么", "真实进程的线程数、Seccomp 值、限额"],
        ["性能口径", "wall 与 CPU、p50/p99、资源 Ready vs 首命令完成", "一段分段耗时表"],
    ], CYAN, nxt(), widths=[2.4, 6.0, 3.2], note="五点是「深度指纹」；其余课程只需 15 秒速答，不必深挖。")

    nxt()
    content(prs, "面试", "四段式：缺第 4 段就是只背过", [
        "结论：先给判断，一句话（面官先听到的是答案，不是铺垫）",
        "机制：两句讲清谁在哪一层做了什么",
        "边界/代价：一句半说清挡不住什么、付出什么",
        "证据：一个数字、一次实测或一次真实故障——这段才区分「做过」与「看过」",
    ], "只报平均值不报分位数；只讲名词不讲「在什么条件下会变坏」。",
       "以「你们沙箱怎么隔离」为例，你能一口气讲完四段吗？", CYAN, nxt())

    nxt()
    table_slide(prs, "面试", "高频追问：能接住三层的答案方向", ["追问", "答题方向"], [
        ["Guest 里的 root 会被 seccomp 拦吗？", "不会。seccomp 只作用于 VMM 自己发出的宿主 syscall"],
        ["为什么不能边跑边抓快照？", "抓的过程中页在变，会拼出从未同时存在的状态"],
        ["恢复后为什么网络可能不通？", "对端状态、宿主 conntrack/NAT、超时计时器都没回滚"],
        ["冷启动 3 秒先查哪一段？", "分段：拉镜像/建盘/起 VMM/等 envd/首命令，各给 wall 与 CPU"],
        ["fork 出的两实例共享什么？", "共享只读底座；各自私有 COW 层；需重随机化 PID/RNG/时钟"],
        ["daemon 挂了会怎样？", "该节点全部块 IO 停；快照恢复直接失败（依赖 ublk client）"],
    ], CYAN, nxt(), widths=[4.6, 7.0])

    nxt()
    table_slide(prs, "面试", "已经纠正过的错误：别再讲错", ["错误说法", "正确说法"], [
        ["pids.max 能挡 Guest 内 fork bomb", "不能。它只数宿主 cgroup 里的 task；靠 memory.max/cpu.max 兜底"],
        ["多实例共享同一批 page cache 页", "已核验成立：共享同一 ublk 设备与页缓存，FC 用 MAP_PRIVATE，写才 COW"],
        ["VM-Exit 就等于 KVM_RUN 返回用户态", "不等。KVM 可处理完直接重入 Guest"],
        ["namespace 隔离等于降权", "namespace 只改视图；ns 里的 root 仍是 root"],
        ["finalize + rename 等于已持久化", "只保证格式完成与名字切换，不等于断电安全"],
        ["health 通过等于鉴权通过", "health_get 未带 token；受保护命令另有鉴权"],
    ], CYAN, nxt(), widths=[5.3, 6.3])

    nxt()
    content(prs, "自测", "看见标题，先自问三句", [
        "第一句：这一步谁在执行？（进程 / 线程 / 内核 / 硬件，第几层）",
        "第二句：数据现在在哪？（GVA/GPA/HVA/HPA、层文件、buffer、page cache）",
        "第三句：这一步的「完成」意味着什么？下一层知道了吗？",
        "答不出来的页，回到对应课程的动画或笔记，不要只看结论",
    ], "把「我记得这个名词」当成「我能解释机制」。判断标准是：能不能预测换条件后的结果。",
       "任选三页，你能不看笔记讲完机制 + 一个数字吗？", CYAN, nxt())

    nxt()
    content(prs, "下一步", "进度与接下来的重点", [
        "已深挖：VM-Exit 分流 ✔  快照恢复 ✔  隔离控制点 ✔（地址空间与性能度量待演练）",
        "已有素材：MMIO 链路、内存镜像、全栈结构、OverlayBD 分层、全链路走查（5 份动画）",
        "接下来：A5 性能度量（冷启动怎么查、报什么口径）+ 第 21—28 课按面试格式推进",
        "要补的真数字：/dev/kvm 通路、冷/热恢复延迟、一次跨进程读耗时、cgroup 实际限额",
    ], "只看不测。面试里问「你测过吗」，答不出数字，前面讲得再好也会掉档。",
       "下一周你打算补哪个数字？怎么测、基线是什么？", CYAN, nxt())

    prs.save(path)
    print("saved:", path, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "review.pptx")
