# -*- coding: utf-8 -*-
"""AgentENV 图示讲解版 v5：左图右注，每页 5 条解释 + 数字 + 易错/追问。
用法：python build_ppt_v5.py <输出路径>
"""
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

F = "Microsoft YaHei"
INK, GRAY, FAINT = RGBColor(0x11,0x11,0x11), RGBColor(0x5B,0x63,0x6E), RGBColor(0x9A,0xA0,0xA8)
LIGHT, PALE, WHITE = RGBColor(0xE5,0xE7,0xEB), RGBColor(0xF7,0xF8,0xFA), RGBColor(0xFF,0xFF,0xFF)
BLUE, PURPLE, GREEN = RGBColor(0x25,0x63,0xEB), RGBColor(0x6D,0x28,0xD9), RGBColor(0x05,0x96,0x69)
ORANGE, AMBER, TEAL = RGBColor(0xC2,0x41,0x0C), RGBColor(0xB4,0x53,0x09), RGBColor(0x0F,0x76,0x6E)
VIOLET, SLATE = RGBColor(0x7E,0x22,0xCE), RGBColor(0x33,0x41,0x55)

def sf(run, size, bold=False, color=INK, name=F):
    run.font.size = Pt(size); run.font.bold = bold
    run.font.color.rgb = color; run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {}); rPr.append(ea)
    ea.set('typeface', name)

def T(s, x, y, w, h, text, size=9, bold=False, color=INK,
      align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, ls=1.30):
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

def node(s, x, y, w, h, text, accent=GRAY, size=8.5, bold=False, fill=WHITE, sub=None, lw=0.75):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = accent; sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    try: sh.adjustments[0] = 0.07
    except Exception: pass
    if sub:
        T(s, x + 0.05, y + h/2 - 0.245, w - 0.10, 0.22, text, size, bold, INK, PP_ALIGN.CENTER)
        T(s, x + 0.05, y + h/2 - 0.015, w - 0.10, 0.26, sub, size - 1.5, False, GRAY, PP_ALIGN.CENTER)
    else:
        T(s, x + 0.05, y + 0.02, w - 0.10, h - 0.04, text, size, bold, INK, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    return sh

def tri(s, x, y, w=0.09, h=0.09, color=GRAY, rot=90):
    sh = s.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.rotation = rot
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    sh.line.fill.background(); sh.shadow.inherit = False

def ah(s, x1, x2, y, color=LIGHT):
    line(s, x1, y, max(0.02, x2 - x1 - 0.07), 0.010, color)
    tri(s, x2 - 0.08, y - 0.045, 0.09, 0.09, color, 90)

def av(s, y1, y2, x, color=LIGHT):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y1), Inches(0.010), Inches(max(0.02, y2-y1-0.07)))
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    sh.line.fill.background(); sh.shadow.inherit = False
    tri(s, x - 0.040, y2 - 0.08, 0.09, 0.09, color, 180)

# ---------------- 页面骨架 ----------------
def page(prs, accent):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background(); bg.shadow.inherit = False
    line(s, 0, 0, 13.333, 0.06, accent)
    return s

EXTRA = {
 "一台机器，三个执行环境": ("为什么容易混", "同一个内核对上是“宿主”，对下是“Guest 的执行环境”；写排障记录时先标一句“我现在在哪一层”，后面就不会绕。"),
 "一个变量，四个地址": ("最短记法", "GVA/GPA 属于 Guest，HVA 属于某个宿主进程，HPA 只有一个——所以“同一份数据”永远只有一个落点。"),
 "三个动作，常常被混成一个": ("为什么值得单独画", "三个动作的“完成条件”不同：系统调用返回、退出原因被读到、线程真的被换下，混了就没法定位卡点。"),
 "一个进程，多个线程": ("怎么验证", "ps -eLf -p <pid> 看 LWP 列；线程数与 vCPU 数对应，另有 vmm/api 线程。名字不见了就说明代码里没设。"),
 "同一个数字，两块内存": ("一句话收口", "地址是“名字”，进程是“语境”；同一个名字在不同语境里指向不同东西，所以接口必须显式带上 pid。"),
 "两条路径，一块物理内存": ("为什么要有 memslot", "没有它，KVM 不知道某个 GPA 该去哪个进程的哪段 HVA 取；EPT 缺项时也就没法补。"),
 "本质是一个 ioctl 的循环": ("数字感", "一次 MMIO 退出是微秒量级；这就是 virtio 要批量、要门铃、要通知抑制的原因。"),
 "“没被调度”不是“已暂停”": ("为什么强调协议状态", "调度是随机的，协议是确定的；快照要的是确定，所以必须等到“全部确认”这个确定点。"),
 "队列在内存里，通知只提醒": ("一个容易忽略的代价", "队列在 Guest RAM 里意味着设备要读写 Guest 内存；所以后端必须做 GPA→HVA 校验，不能直接解引用。"),
 "控制面与数据面，两条通道": ("两条通道的故障表现不同", "控制面坏 → 不能暂停/快照但 Guest 照跑；数据面坏 → Guest 内部 IO 卡住但宿主仍可控制。"),
 "三层就绪，一层比一层强": ("排障顺序", "先 socket、再网络、最后应用层：跳层排查会把“网络不通”误诊成“服务没起来”。"),
 "exec 返回的是流，不是结果": ("为什么不合并成一个返回值", "输出是流式的、可能很长；一次性返回要么爆内存，要么丢输出。所以必须边收边处理。"),
 "一条数据，三个坐标系": ("为什么必须带单位", "LBA 在 512B 扇区和 4KiB 块下差 8 倍；报数不带单位，等于没报。"),
 "分层是覆盖映射": ("为什么不能拼字节", "拼接改变的是“相邻关系”，而覆盖需要的是“同一逻辑位置的替换关系”，两者语义不同。"),
 "内核给壳，用户态给内容": ("为什么要用户态", "分层、稀疏、远端拉取这些逻辑，内核里做不了也不该做；ublk 让内核只负责搬运。"),
 "映射了 ≠ 分配了 ≠ 复制了": ("最实用的一句", "看到 mmap 成功不要以为内存已占；看到 RSS 不涨也不要以为没生效——它还没被访问。"),
 "快照是四件套": ("常见误判", "vm_state 文件写成功不等于整套快照可用；恢复还需要内存层、磁盘层与配置索引同时到位。"),
 "增量必须有基线": ("为什么强调“不驻留”", "“页不在内存”不等于“内容为零”；把这两件事混起来，就会漏写覆盖记录，恢复时读回父层旧值。"),
 "每个参数都要能说出归属": ("最短记法", "pid 选空间、remote 指源、local 指目的、count 是个数——四个词各管一件事。"),
 "两条线：元数据与字节": ("为什么两条线要分开看", "元数据错 → 数据放错位置；字节错 → 内容不对。排障时先看哪条线断了，再查具体值。"),
 "恢复不是把内存读回来": ("量化口径", "恢复的“完成”是“能开始跑”，不是“所有页就绪”；要测的是首命令延迟与缺页数，不是恢复返回时间。"),
 "出站与入站，两条相反的路": ("为什么入站要 DNAT", "Guest 的 IP 在宿主主 netns 里不可路由；必须先落到 slot 地址，再在沙箱 netns 里改成 Guest IP。"),
 "tap 与 veth，DNAT 与 SNAT": ("一个判断技巧", "问“改的是源还是目的、发生在入口还是出口”，四个名字立刻能分清。"),
 "四类威胁，四道门": ("为什么先定威胁", "不定威胁就会堆控制点：堆了也不解释“防住谁”，面试官一追就露。"),
 "seccomp 是线程级的": ("为什么按线程分", "三类线程需要的 syscall 集合不同；用并集等于把白名单放大，用交集等于谁都跑不起来。"),
 "谁拥有，谁释放": ("为什么强调引用计数", "共享设备被多个沙箱用，谁都不能单方面销毁；靠引用计数把“最后一个用户”变成确定的释放点。"),
 "async 让出了什么": ("一句判断", "看“提交后是否立刻返回”与“buffer 是否被别人持有”；两条都满足才算真异步。"),
 "失败时状态不能乱跳": ("为什么状态机值得画", "状态机的价值不是在正常路径，而是在失败路径：它规定了“失败后允许停在哪”。"),
 "度量口径：先分类，再谈平均": ("为什么 p99 比均值重要", "用户体验由最差的那几次决定；均值把长尾抹平，正好抹掉要修的问题。"),
 "多节点与预热池": ("为什么要原子认领", "“先查空闲再写占用”中间有窗口；两个请求同时查都会看到空闲，于是双分配。"),
 "模板、快照、实例、缓存": ("一句话区分", "模板不可变、快照是历史、实例是可写分支、缓存是本地副本——四者的回收策略完全不同。"),
 "六条链，一条主线": ("为什么按链复习", "按课复习记的是名词；按链复习记的是“谁在等谁”，后者才是排障能力。"),
 "PVM 中转 vs 直接写出": ("怎么讲才不空", "先说省掉了哪一段、再说没省掉什么、最后给一个量级，三步说完比长篇设计更可信。"),
 "五个必深点": ("怎么用这张表", "每个深点后面那列是“证据”；缺证据的那行，就是你接下来要补的实验或数字。"),
 "四段式：缺第 4 段就是只背过": ("一句提醒", "面试官不要求你什么都深，但要求你说的每一句都能落到“我见过/我测过”。"),
 "把讲过变成做过": ("一句实话", "28 课覆盖完只代表“知道有这回事”；面试与上岗要的是“这件事我亲手做过一次”。"),
}

BOUND = {'一台机器，三个执行环境': '边界：这三层里只有 Guest 有“自己的内核”；宿主那两层共用一个内核，所以隔离强度完全不同。', '一个变量，四个地址': '边界：HVA 只在所属进程内有效；换了进程，同一个数字可能指向别的物理页。', '三个动作，常常被混成一个': '边界：三者的“完成”由不同主体判定——系统调用返回看内核，退出看硬件，切线程看调度器。', '一个进程，多个线程': '边界：线程数增长会让宿主的 seccomp 白名单、cgroup 记账、调度都按线程粒度生效。', '同一个数字，两块内存': '边界：PVM 需要 ptrace 级权限检查（PTRACE_MODE_ATTACH_REALCREDS），不是谁都能读另一个进程。', '两条路径，一块物理内存': '边界：memslot 有数量上限（KVM 上报的 max_nr_memslots），碎片化登记会先撞这个上限。', '本质是一个 ioctl 的循环': '边界：退回用户态的代价包含上下文切换与设备模型模拟，量级在微秒；这就是批量化能省的东西。', '“没被调度”不是“已暂停”': '边界：即使全部 vCPU 确认，设备侧仍可能有在途 IO；完整冻结要单独协调。', '队列在内存里，通知只提醒': '边界：描述符里的地址是 Guest 物理地址，后端必须先做 GPA→HVA 换算与范围校验再访问。', '控制面与数据面，两条通道': '边界：控制面依赖宿主 fd，不受 Guest 影响；但宿主资源耗尽或 FC 进程故障仍会让它失败。', '三层就绪，一层比一层强': '边界：health 通过只代表“能应答”，不代表工具盘下载完、也不代表鉴权通过。', 'exec 返回的是流，不是结果': '边界：流式输出有背压，消费慢了会堆在缓冲里；必要时要做输出上限与丢弃策略。', '一条数据，三个坐标系': '边界：一次逻辑读可能被拆成多段，也可能被合并；不能从逻辑长度推断真实 IO 次数。', '分层是覆盖映射': '边界：层数越多查询路径越长；缓存命中可以缩短，但“命中哪里”要按层看。', '内核给壳，用户态给内容': '边界：daemon 挂了会让整节点块 IO 停摆；它不是一个可以随意重启的旁路组件。', '映射了 ≠ 分配了 ≠ 复制了': '边界：RSS 不涨不代表没映射；反过来，RSS 涨也可能只是文件页缓存被算进去了。', '快照是四件套': '边界：磁盘只读层可共享，但所有引用都必须存在；缺一个父层就整套恢复失败。', '增量必须有基线': '边界：dirty 位图只覆盖“被跟踪的写入源”，宿主设备写入必须一起纳入，否则会漏页。', '每个参数都要能说出归属': '边界：PVM 不提供快照级原子性；多段读取之间源内容仍可能变化。', '两条线：元数据与字节': '边界：异步提交后不能立刻复用 buffer；完成顺序可能与提交顺序不同。', '恢复不是把内存读回来': '边界：恢复后旧 PID/HVA 不再有效；网络要重连，不依赖旧连接。', '出站与入站，两条相反的路': '边界：两层 NAT 都依赖 conntrack；状态丢了旧连接就断，这是恢复后网络异常的常见原因。', 'tap 与 veth，DNAT 与 SNAT': '边界：DNAT 只改地址，不解析内容；要按域名判断必须由代理进程看 Host/SNI。', '四类威胁，四道门': '边界：每道门都有它管不到的维度；堆控制点不等于安全感，要能说清“防住谁”。', 'seccomp 是线程级的': '边界：白名单只能加严不能放松；过滤器与 VMM 版本必须一起升级。', '谁拥有，谁释放': '边界：引用计数只解决“何时释放”，不解决“释放失败怎么办”，后者要靠兜底扫描。', 'async 让出了什么': '边界：async 提高并发度，不提高单次 IO 速度；尾延迟仍由最慢的那次决定。', '失败时状态不能乱跳': '边界：重试要幂等，否则“补偿”本身会制造重复副作用。', '度量口径：先分类，再谈平均': '边界：把不同路径的样本混在一起算 p99，得到的数无法解释、也无法优化。', '多节点与预热池': '边界：预热池有内存与端口成本；池太大反而挤占运行中的沙箱。', '模板、快照、实例、缓存': '边界：跨机器通常是“各自取得副本”，不是两台机器共享同一物理页。', '六条链，一条主线': '边界：每条链的失败点不同，排障不能只看一个指标。', 'PVM 中转 vs 直接写出': '边界：省掉中转不代表省掉约束——一致性、在途 IO 寿命、格式完整性都还在。', '五个必深点': '边界：五点是“深度指纹”，不是全部知识；广度靠一页速答兜底。', '四段式：缺第 4 段就是只背过': '边界：没有实测就诚实说“这是从源码读出来的”，别编数字。', '把讲过变成做过': '边界：材料齐全 ≠ 会；判断标准是换条件后还能预测结果。'}

CHAIN = {'一台机器，三个执行环境': '链路：客户端 → server → firecracker → KVM → Guest 内核 → 你的程序', '一个变量，四个地址': '链路：Guest 访存 GVA→GPA→HPA；宿主访问 HVA→HPA；两者落在同一物理页', '三个动作，常常被混成一个': '链路：ioctl(KVM_RUN) → （硬件）VM-Exit → KVM 处理 → 重入 或 返回用户态', '一个进程，多个线程': '链路：spawn → api 线程监听 → vmm 协调 → N 个 fc_vcpu 线程各自阻塞在 KVM_RUN', '同一个数字，两块内存': '链路：server 构造 iovec → PVM(pid, local, remote) → 内核复制 → server buffer', '两条路径，一块物理内存': '链路：mmap 匿名内存(HVA) → ioctl 登记(GPA↔HVA) → 缺页 → 取页 → 建 EPT 项', '本质是一个 ioctl 的循环': '链路：KVM_RUN → Guest 执行 → VM-Exit → 读 exit_reason → 处理 → 再 KVM_RUN', '“没被调度”不是“已暂停”': '链路：PATCH /vm → 置暂停意图 → 各 vCPU 退出确认 → 全部确认才叫暂停', '队列在内存里，通知只提醒': '链路：Guest 发布 avail → doorbell → 设备取描述符 → 写数据 → 发布 used → Guest 处理', '控制面与数据面，两条通道': '链路：server --api-sock→ FC（控制）；server --TCP→ envd（应用）', '三层就绪，一层比一层强': '链路：start_nowait（等 socket）→ 配 VM → wait_for_ready（等 envd /health）', 'exec 返回的是流，不是结果': '链路：start → Start(pid) → Data… → End(code) → wait 归一成 ProcessOutput', '一条数据，三个坐标系': '链路：read → 页缓存(miss) → ext4 extent → LBA → virtio → ublk → 层文件', '分层是覆盖映射': '链路：查 upper → 命中即停 → 未命中回落 → 全无则空洞(零)', '内核给壳，用户态给内容': '链路：Create → 内核分配 N → 等节点可打开 → FC add_drive → Guest /dev/vdX', '映射了 ≠ 分配了 ≠ 复制了': '链路：mmap 建 VMA → 首次访问缺页 → 有页映射/无页取页 → 首次写 COW', '快照是四件套': '链路：pause → 捕获（状态/内存/磁盘）→ 持久化 → 发布 manifest', '增量必须有基线': '链路：S0 全量 → S1 增量 → S2 增量 → 视图 = 逐层回落组合', '每个参数都要能说出归属': '链路：构造 iovec → process_vm_readv → server buffer → writer 写层', '两条线：元数据与字节': '链路：范围 → entry → chunk → buffer → writer → finalize → rename', '恢复不是把内存读回来': '链路：备环境 → load(resume_vm=false) → 映射内存 → 补配置 → resume → 缺页按需取', '出站与入站，两条相反的路': '链路：eth0→tap0→SNAT→veth→MASQ ｜ server→veth→DNAT→tap0→envd', 'tap 与 veth，DNAT 与 SNAT': '链路：tap 接进程，veth 接 netns；DNAT 改目的，SNAT 改源，REDIRECT 改到本机', '四类威胁，四道门': '链路：定威胁（谁/越没越界）→ 选控制点（虚拟化/ns/cgroup/seccomp）→ 验证', 'seccomp 是线程级的': '链路：线程创建 → 各自 apply_filter → 命中白名单放行 → 命中未允许 SIGSYS', '谁拥有，谁释放': '链路：创建（网络/磁盘/进程）→ 运行 → 失败或销毁 → 按拥有者回收', 'async 让出了什么': '链路：调用 async 方法 → 内部同步 syscall → worker 阻塞 → 完成后恢复', '失败时状态不能乱跳': '链路：Running → Pausing → Paused → 捕获 → Resuming → Running', '度量口径：先分类，再谈平均': '链路：分段计时 → 分类（路径）→ 报 p50/p99 → 单变量优化 → 复测', '多节点与预热池': '链路：请求 → scheduler 选节点 → 池中认领 → 装载/就绪 → 返回', '模板、快照、实例、缓存': '链路：模板（只读）→ 快照（历史）→ 实例（可写分支）→ 缓存（本地副本）', '六条链，一条主线': '链路：创建 → 执行 → 读文件 → 暂停 → 恢复 → 销毁', 'PVM 中转 vs 直接写出': '链路：现状 FC→PVM→server→writer；候选 FC→writer（格式/一致性仍需处理）', '五个必深点': '链路：地址 → 执行 → 存储 → 快照 → 隔离 → 度量（五个点各一段）', '四段式：缺第 4 段就是只背过': '链路：结论 → 机制 → 边界 → 证据（缺最后一段＝只背过）', '把讲过变成做过': '链路：跑通环境 → 测一个数 → 讲成故事 → 面试复盘'}

def teach(prs, kicker, title, accent, notes, nums, pitfall, ask, pageno, dg, wide=False):
    if len(notes) == 5 and title in EXTRA:
        notes = notes + [EXTRA[title]]
    """wide=True：图占满宽度、注释在下方三栏；否则图左（0.7..7.55）、注右（7.9..12.65）。"""
    s = page(prs, accent)
    T(s, 0.70, 0.36, 9.0, 0.20, kicker, 7.5, True, accent)
    T(s, 0.68, 0.58, 11.9, 0.46, title, 18, True, INK)
    line(s, 0.68, 1.08, 11.95, 0.006, LIGHT)

    if wide:
        dg(s, 0.68, 1.18, 11.95, 2.55)
        # 三栏注释
        cols = 3
        cw = (11.95 - 0.30 * (cols - 1)) / cols
        for i, (h, body) in enumerate(notes[:6]):
            col = i % cols; row = i // cols
            x = 0.68 + col * (cw + 0.30)
            y = 3.80 + row * 0.92
            T(s, x, y, cw, 0.20, h, 8.5, True, INK)
            T(s, x, y + 0.20, cw, 0.66, body, 7.6, False, GRAY, ls=1.28)
        ch = CHAIN.get(title)
        if ch:
            T(s, 0.68, 5.64, 11.95, 0.24, ch, 7.2, False, accent, ls=1.2)
        bd = BOUND.get(title)
        if bd:
            T(s, 0.68, 5.88, 11.95, 0.24, bd, 7.2, False, GRAY, ls=1.2)
        xx = 0.68
        for num, cap in nums[:3]:
            T(s, xx, 6.02, 0.55, 0.24, num, 11, True, accent)
            T(s, xx + 0.62, 6.06, 2.4, 0.24, cap, 6.8, False, GRAY)
            xx += 3.30
    else:
        dg(s, 0.68, 1.18, 6.85, 4.25)
        x = 7.85
        y = 1.10
        for h, body in notes[:6]:
            T(s, x, y, 4.75, 0.20, h, 8.5, True, accent)
            T(s, x, y + 0.19, 4.75, 0.58, body, 7.6, False, GRAY, ls=1.30)
            y += 0.80
        ch = CHAIN.get(title)
        if ch:
            T(s, 0.68, 5.34, 6.85, 0.30, ch, 7.2, False, accent, ls=1.25)
        bd = BOUND.get(title)
        if bd:
            T(s, 0.68, 5.66, 6.85, 0.40, bd, 7.2, False, GRAY, ls=1.25)
        # 数字条
        yy = 5.96
        line(s, x, yy - 0.08, 4.75, 0.006, LIGHT)
        xx = x
        for num, cap in nums[:3]:
            T(s, xx, yy, 1.5, 0.26, num, 13, True, accent)
            T(s, xx, yy + 0.27, 1.55, 0.34, cap, 6.8, False, GRAY, ls=1.2)
            xx += 1.60

    line(s, 0.68, 6.52, 11.95, 0.006, LIGHT)
    T(s, 0.68, 6.60, 5.9, 0.42, pitfall, 7.8, False, RGBColor(0x8A, 0x3F, 0x0E), ls=1.3)
    T(s, 6.75, 6.60, 5.9, 0.42, ask, 7.8, False, GRAY, ls=1.3)
    T(s, 12.35, 7.14, 0.50, 0.20, str(pageno), 7.5, False, RGBColor(0xB8, 0xBD, 0xC4), PP_ALIGN.RIGHT)
    return s

# ---------------- 图形库 ----------------
def dg_three_layers(s, X, Y, W, H):
    rows = [("宿主用户态", ["server", "firecracker", "ublk-daemon"], BLUE),
            ("宿主内核", ["KVM", "ublk 驱动", "cgroup/seccomp"], PURPLE),
            ("Guest", ["Guest 内核", "envd", "你的程序"], GREEN)]
    bh = 0.62; gap = (H - bh*3) / 2
    for i, (name, items, c) in enumerate(rows):
        y = Y + i * (bh + gap)
        T(s, X, y - 0.02, 1.4, 0.20, name, 7, True, c)
        n = 3; bw = (W - 1.45 - 0.18*2) / 3
        for j, it in enumerate(items):
            node(s, X + 1.45 + j*(bw+0.18), y, bw, bh, it, c, 8)
    av(s, Y + bh + 0.06, Y + bh + gap - 0.06, X + 1.45 + (W-1.45)/2, LIGHT)

def dg_four_addr(s, X, Y, W, H):
    cy = Y + 0.62
    node(s, X + W*0.40, cy, W*0.22, 0.52, "HPA", PURPLE, 9, True, sub="物理页")
    node(s, X, cy - 0.75, W*0.20, 0.48, "GVA", BLUE, 8.5, True, sub="Guest 程序")
    node(s, X, cy - 0.10, W*0.20, 0.48, "GPA", BLUE, 8.5, True, sub="Guest 内核")
    node(s, X + W - W*0.20, cy - 0.75, W*0.20, 0.48, "HVA", PURPLE, 8.5, True, sub="Firecracker")
    av(s, cy - 0.27, cy - 0.10, X + W*0.10, BLUE)
    ah(s, X + W*0.20, X + W*0.40, cy + 0.26, BLUE)
    av(s, cy - 0.27, cy + 0.10, X + W - W*0.10, PURPLE)
    ah(s, X + W*0.60, X + W - W*0.20, cy, PURPLE)
    node(s, X + W*0.18, cy + 0.78, W*0.64, 0.46, "memslot：GPA 区间 ↔ HVA 区间（软件登记，不复制数据）", BLUE, 7.5)

def dg_bound3(s, X, Y, W, H):
    rows = [("KVM_RUN", "用户态 → 内核", "不切线程", GREEN),
            ("VM-Exit", "Guest ↔ 宿主执行环境", "不切线程", GREEN),
            ("线程切换", "调度器换线程", "切了", ORANGE)]
    bh = 0.52; gap = 0.28
    for i, (t, d, r, c) in enumerate(rows):
        y = Y + i*(bh+gap)
        node(s, X, y, 1.9, bh, t, PURPLE, 8.5, True)
        T(s, X + 2.10, y + 0.16, 2.6, 0.22, d, 7.5, False, GRAY)
        T(s, X + 4.75, y + 0.16, 1.6, 0.22, r, 7.5, True, c)
        if i < 2: av(s, y + bh, y + bh + gap, X + 0.95)
    T(s, X, Y + 3*0.80 + 0.05, W, 0.60,
      "只有第三种才是「没拿到 CPU」。前两种都在同一个线程内完成，\n所以 VM-Exit 频率 ≠ VMM 被唤醒的频率。", 7.5, False, GRAY, ls=1.4)

def dg_proc_threads(s, X, Y, W, H):
    node(s, X, Y, W, H, "", BLUE, 8, fill=PALE)
    T(s, X + 0.12, Y + 0.10, W - 0.24, 0.20, "firecracker（宿主进程，一个地址空间）", 7, True, BLUE)
    for i, (t, d) in enumerate([("vmm 主线程", "协调状态、处理设备事件"), ("api 线程", "Unix socket 收控制请求"),
                                ("fc_vcpu 0", "ioctl(KVM_RUN) 跑 Guest"), ("fc_vcpu 1", "ioctl(KVM_RUN) 跑 Guest")]):
        node(s, X + 0.12, Y + 0.36 + i*((H-0.5)/4), W - 0.24, (H-0.55)/4 - 0.08, t, BLUE, 8, True, sub=d)

def dg_two_spaces(s, X, Y, W, H):
    node(s, X + 0.05, Y + 0.15, W*0.30, 0.46, "server", ORANGE, 8.5, True, sub="0x400000")
    node(s, X + 0.05, Y + 0.75, W*0.30, 0.46, "firecracker", PURPLE, 8.5, True, sub="0x400000")
    node(s, X + W*0.55, Y + 0.15, W*0.32, 0.46, "物理页 P_A", ORANGE, 8.5, True, sub="SERVER")
    node(s, X + W*0.55, Y + 0.75, W*0.32, 0.46, "物理页 P_B", PURPLE, 8.5, True, sub="GUEST")
    ah(s, X + W*0.36, X + W*0.54, Y + 0.38, ORANGE); ah(s, X + W*0.36, X + W*0.54, Y + 0.98, PURPLE)
    T(s, X + 0.05, Y + 1.35, W, 0.28, "两张页表把同一数字翻到不同物理页", 7.2, False, GRAY)
    node(s, X + 0.05, Y + 1.72, W*0.46, 0.50, "pwrite(buf)", ORANGE, 7.5, True, sub="buf 只能是自己的")
    node(s, X + W*0.52, Y + 1.72, W*0.46, 0.50, "PVM(pid,…)", PURPLE, 7.5, True, sub="pid 决定地址空间")
    T(s, X + 0.05, Y + 2.32, W, 0.52, "所以读 Guest 内存时，remote 地址填 Firecracker 的 HVA；\nliovcnt/riovcnt 是元素个数，不是字节数。", 7.2, False, GRAY, ls=1.35)

def dg_two_paths(s, X, Y, W, H):
    node(s, X + 0.10, Y + 0.05, W*0.26, 0.44, "GVA", BLUE, 8.5)
    node(s, X + 0.10, Y + 0.72, W*0.26, 0.44, "GPA", BLUE, 8.5)
    node(s, X + W*0.46, Y + 0.38, W*0.26, 0.50, "HPA", PURPLE, 9, True)
    node(s, X + W - 0.10 - W*0.26, Y + 0.05, W*0.26, 0.44, "HVA", PURPLE, 8.5)
    av(s, Y + 0.49, Y + 0.72, X + W*0.23, BLUE); ah(s, X + W*0.36, X + W*0.46, Y + 0.94, BLUE)
    ah(s, X + W*0.62, X + W - 0.10 - W*0.26, Y + 0.63, PURPLE); av(s, Y + 0.49, Y + 0.63, X + W*0.87, PURPLE)
    T(s, X + 0.10, Y + 1.28, W, 0.30, "Guest：GVA→GPA→HPA（页表 + EPT）；Firecracker：HVA→HPA（宿主页表）", 7.2, False, GRAY)
    node(s, X + 0.10, Y + 1.72, W - 0.20, 1.10, "", BLUE, 7.5, fill=PALE)
    T(s, X + 0.24, Y + 1.84, W - 0.48, 0.92,
      "KVM_SET_USER_MEMORY_REGION(guest_phys_addr, userspace_addr, size)\n"
      "→ 只登记范围：不复制 128 MiB，也不要求你填 HPA\n"
      "→ 访问缺 EPT 项时，KVM 按 memslot 算 HVA、取真实页、再建 EPT\n"
      "→ 偏移：HVA = userspace_addr + (GPA − guest_phys_addr)", 7, False, INK, ls=1.45)

def dg_kvm_loop(s, X, Y, W, H):
    node(s, X + 0.05, Y + 0.10, W*0.30, 0.52, "ioctl(KVM_RUN)", PURPLE, 8, True, sub="阻塞直到退出")
    node(s, X + W*0.40, Y + 0.10, W*0.30, 0.52, "硬件跑 Guest", PURPLE, 8, True, sub="非根模式")
    node(s, X + W*0.75, Y + 0.10, W*0.22, 0.52, "VM-Exit", PURPLE, 8, True, sub="exit_reason")
    ah(s, X + W*0.35, X + W*0.40, Y + 0.36, PURPLE); ah(s, X + W*0.70, X + W*0.75, Y + 0.36, PURPLE)
    av(s, Y + 0.62, Y + 0.92, X + W*0.86, PURPLE)
    node(s, X + W*0.64, Y + 0.92, W*0.34, 0.50, "KVM 处理完", GREEN, 7.5, True, sub="直接重入，ioctl 未返回")
    node(s, X + W*0.18, Y + 0.92, W*0.40, 0.50, "需要用户态模拟", ORANGE, 7.5, True, sub="KVM_RUN 返回 FC")
    ah(s, X + W*0.58, X + W*0.64, Y + 1.17, LIGHT)
    ah(s, X + W*0.04, X + 0.05, Y + 1.17, LIGHT)
    T(s, X + 0.05, Y + 1.58, W, 1.35,
      "退出原因不是只有「Guest 要设备」：外部中断、EPT 缺页、I/O 指令都会退出。\n"
      "KVM 能处理的（补 EPT 映射）处理完直接重入；它办不了的（MMIO/PIO 模拟）才回用户态。\n"
      "所以：退出次数看硬件，唤醒次数看是否必须回用户态——两个数不一样。\n"
      "常见误判：把「VM-Exit 频繁」直接当成「VMM 开销大」。", 7, False, GRAY, ls=1.5)

def dg_pause(s, X, Y, W, H):
    ev = [("t1", "API 收到 PATCH", GREEN), ("t2", "置暂停意图", GREEN), ("t3", "vCPU0 确认", GREEN),
          ("t4", "vCPU1 没被调度", ORANGE), ("t5", "vCPU1 确认", GREEN), ("t6", "暂停完成", BLUE)]
    bw = (W - 0.14*5) / 6
    for i, (t, d, c) in enumerate(ev):
        x = X + i*(bw+0.14)
        node(s, x, Y + 0.10, bw, 0.62, t, c, 7.5, True, sub=d)
        if i < 5: ah(s, x + bw, x + bw + 0.14, Y + 0.41)
    T(s, X, Y + 0.88, W, 0.60,
      "t4 是唯一难点：vCPU1 只是「没拿到 CPU」，调度器再给它时间片，它会继续写 Guest RAM。\n"
      "所以「请求发出」「API 返回成功」「全部 vCPU 确认」是三个不同的完成点。", 7.2, False, GRAY, ls=1.4)
    node(s, X, Y + 1.62, W, 0.46, "暂停只停 Guest 的 CPU 写入；宿主设备侧仍可能在写同一块 RAM", PURPLE, 7.5)
    node(s, X, Y + 2.16, W, 0.46, "暂停完成后还有：捕获内存、写层、fsync、改 manifest —— 各自独立", PURPLE, 7.5)

def dg_virtio(s, X, Y, W, H):
    node(s, X + 0.05, Y + 0.08, W*0.36, 0.62, "描述符表", PURPLE, 8.5, True, sub="addr/len/flags/next")
    node(s, X + 0.05, Y + 0.90, W*0.36, 0.50, "avail 环", GREEN, 8.5, True, sub="Guest 发布链头")
    node(s, X + W*0.55, Y + 0.90, W*0.40, 0.50, "used 环", ORANGE, 8.5, True, sub="设备发布完成")
    ah(s, X + W*0.42, X + W*0.54, Y + 1.15)
    node(s, X + W*0.55, Y + 0.08, W*0.40, 0.62, "设备后端", PURPLE, 8.5, True, sub="从 Guest RAM 取描述符")
    av(s, Y + 0.70, Y + 0.90, X + W*0.23, LIGHT); av(s, Y + 0.70, Y + 0.90, X + W*0.75, LIGHT)
    T(s, X + 0.05, Y + 1.55, W, 1.30,
      "描述符 16 字节；描述符不复制字节，只描述「缓冲区在哪、多长」。\n"
      "通知（doorbell）只提醒「去检查队列」：不带包内容，一次通知可对应多项工作。\n"
      "复用：同一链头发布两次＝两次使用机会；未处理完就交回，设备可能覆盖。\n"
      "范围：VirtIO 只用于设备 IO，普通内存赋值不走它。", 7, False, GRAY, ls=1.5)

def dg_two_channels(s, X, Y, W, H):
    node(s, X + 0.05, Y + 0.10, W*0.46, 0.90, "控制面", GREEN, 8.5, True,
         sub="Unix socket · PATCH /vm\n不需要 Guest 配合")
    node(s, X + W*0.51, Y + 0.10, W*0.46, 0.90, "数据面", ORANGE, 8.5, True,
         sub="virtqueue · 需要 Guest 驱动")
    T(s, X + 0.05, Y + 1.10, W, 0.60,
      "为什么暂停不能走数据面：暂停的用途之一，就是「Guest 不配合时也能停住它」。", 7.2, False, GRAY, ls=1.4)
    node(s, X + 0.05, Y + 1.75, W, 0.50, "", GREEN, 7.5, fill=PALE)
    T(s, X + 0.18, Y + 1.84, W - 0.36, 0.34,
      "超时的三种可能：① 没送到 ② 做成了但响应丢了 ③ 还在做 —— 不能只凭超时下结论", 7, False, INK)

def dg_tiers(s, X, Y, W, H):
    tiers = [("① API socket 可用", "能配 VM、能 pause", GREEN, 0.70),
             ("② 网络可达", "tap0 能到 Guest", GREEN, 0.62),
             ("③ envd /health 通过", "应用层能应答", BLUE, 0.54)]
    y = Y + 0.10
    for t, d, c, wf in tiers:
        node(s, X, y, W*wf, 0.56, t, c, 8, True, sub=d)
        y += 0.74
    T(s, X, Y + 2.20, W, 1.10,
      "强度递进：进程存在 → 端口能连 → 应用能应答。\n"
      "health 细节：GET /health，状态码非 4xx/5xx 即通过（不校验 body），\n"
      "单次上限 1 秒，失败继续重试，整体期限耗尽才报超时。\n"
      "拆两段：start_nowait 只等 socket；wait_for_ready 才等 envd。", 7, False, GRAY, ls=1.5)

def dg_stream(s, X, Y, W, H):
    items = [("start 请求", "cmd+args+env+cwd"), ("Start{pid}", "进程已创建"),
             ("Data{...}", "stdout/stderr"), ("End{code}", "进程已退出")]
    bw = (W - 0.20*3) / 4
    for i, (t, d) in enumerate(items):
        x = X + i*(bw+0.20)
        node(s, x, Y + 0.10, bw, 0.62, t, GREEN if i < 3 else BLUE, 7.5, True, sub=d)
        if i < 3: ah(s, x + bw, x + bw + 0.20, Y + 0.41)
    node(s, X + 0.05, Y + 1.00, W*0.46, 0.62, "判断一：事件收齐？", GREEN, 7.5, True, sub="收到 End = Ok")
    node(s, X + W*0.51, Y + 1.00, W*0.46, 0.62, "判断二：exit_code？", BLUE, 7.5, True, sub="0 / 非零")
    T(s, X + 0.05, Y + 1.78, W, 1.05,
      "成功要三样同时满足：wait 返回 Ok + 收到 End + exit_code 符合预期。\n"
      "只有 Start 只说明进程被创建——之后可能立刻失败、崩溃、被超时杀。\n"
      "命令与参数分开传，不假设过 shell：没有管道/通配符/重定向语义。", 7, False, GRAY, ls=1.5)

def dg_offsets(s, X, Y, W, H):
    items = [("read()", "文件偏移 8 MiB"), ("ext4", "extent → LBA"), ("块层", "合并/排队"),
             ("virtio-blk", "描述符 + 通知"), ("后端", "层文件/块设备")]
    bw = (W - 0.16*4) / 5
    for i, (t, d) in enumerate(items):
        x = X + i*(bw+0.16)
        node(s, x, Y + 0.10, bw, 0.58, t, ORANGE, 7.2, True, sub=d)
        if i < 4: ah(s, x + bw, x + bw + 0.16, Y + 0.39)
    T(s, X + 0.05, Y + 0.82, W, 0.60,
      "三个坐标系：文件偏移（文件系统）→ LBA（块设备，必须带块/扇区大小）→ 后端位置（宿主）。\n"
      "文件内连续的数据，在磁盘上可以完全不连续。", 7, False, GRAY, ls=1.4)
    items2 = [("写入", "进页缓存"), ("回写", "交 virtio"), ("后端", "写层文件"), ("持久化", "fsync")]
    bw2 = (W - 0.16*3) / 4
    for i, (t, d) in enumerate(items2):
        x = X + i*(bw2+0.16)
        node(s, x, Y + 1.78, bw2, 0.56, t, GRAY, 7.2, True, sub=d)
        if i < 3: ah(s, x + bw2, x + bw2 + 0.16, Y + 2.06)
    T(s, X + 0.05, Y + 2.42, W, 0.42, "write 返回 ≠ 持久化；要持久化得 fsync/flush。", 7.2, True, ORANGE)

def dg_overlay(s, X, Y, W, H):
    layers = [("upper（可写）", "位置1 → 新值", GREEN, 0.10),
              ("增量（只读）", "位置3 → 显式零", ORANGE, 0.86),
              ("基层（只读）", "位置0/1/2 有数据", PURPLE, 1.62)]
    for t, d, c, dy in layers:
        node(s, X, Y + dy, W*0.52, 0.60, t, c, 7.5, True, sub=d)
    cells = [("P0", "基层 A", PURPLE), ("P1", "upper", GREEN), ("P2", "显式零", ORANGE), ("P3", "显式零", ORANGE)]
    cw = (W*0.44 - 0.10*3) / 4
    for i, (t, d, c) in enumerate(cells):
        node(s, X + W*0.56 + i*(cw+0.10), Y + 0.86, cw, 0.86, t, c, 7, True, sub=d)
    T(s, X + W*0.56, Y + 0.10, W*0.44, 0.60, "最终视图（从上往下第一个命中）", 7, True, GRAY)
    T(s, X, Y + 2.35, W, 1.10,
      "「无记录」不是零 → 继续往下找（回落）；「显式零」必须终止 → 否则暴露父层旧数据。\n"
      "叠加只能在索引层做：拼字节只会得到 A/B/C/D/X/Y，表达不了「X 替换位置 1」。\n"
      "代价：一个逻辑读可能跨多段；后端读失败必须报错，不能当零。", 7, False, GRAY, ls=1.5)

def dg_ublk(s, X, Y, W, H):
    nodes = [("ublk-control", "创建/删除"), ("ublkcN", "命令交接"), ("ublkbN", "数据读写")]
    bw = (W - 0.16*2) / 3
    for i, (t, d) in enumerate(nodes):
        node(s, X + i*(bw+0.16), Y + 0.10, bw, 0.56, t, ORANGE, 7.2, True, sub=d)
    steps = [("① 等待", "io_uring"), ("② 领取", "CQE 到"), ("③ 解析", "OverlayBD"), ("④ 提交", "COMMIT")]
    bw2 = (W - 0.16*3) / 4
    for i, (t, d) in enumerate(steps):
        node(s, X + i*(bw2+0.16), Y + 0.86, bw2, 0.56, t, ORANGE, 7.2, True, sub=d)
        if i < 3: ah(s, X + i*(bw2+0.16) + bw2, X + (i+1)*(bw2+0.16), Y + 1.14)
    T(s, X, Y + 1.58, W, 1.20,
      "「领取」的 CQE 只表示请求送到 daemon，不表示数据读完。\n"
      "daemon 是集中式的：不是每沙箱一个进程；OverlayBD 是它链接的库。\n"
      "创建流程：server 发 Create → 内核分配 N → daemon 等节点真正可打开 → 回 (dev_id, path)。", 7, False, GRAY, ls=1.5)

def dg_mmap(s, X, Y, W, H):
    trio = [("mmap 之后", "只有 VMA，无物理页", GREEN), ("第一次读", "缺页：取页或分配", ORANGE),
            ("第一次写", "COW：复制私有页", PURPLE)]
    bw = (W - 0.16*2) / 3
    for i, (t, d, c) in enumerate(trio):
        node(s, X + i*(bw+0.16), Y + 0.10, bw, 0.76, t, c, 7.2, True, sub=d)
        if i < 2: ah(s, X + i*(bw+0.16) + bw, X + (i+1)*(bw+0.16), Y + 0.48)
    T(s, X, Y + 1.02, W, 1.70,
      "缺页三类：minor（页已在内存）、major（要读盘/换入）、非法访问（SIGSEGV，写保护缺页不属于它）。\n"
      "两种写语义：MAP_SHARED 写回共享缓存；MAP_PRIVATE 只影响私有副本。\n"
      "microVM：只读后端 + MAP_PRIVATE → 读共享页缓存，写才 COW（已核验 FC 1.12.1 memory.rs:136）。\n"
      "三层缺页：Guest 页表（Guest 内核）／EPT（KVM）／宿主页表（宿主内核）。", 7, False, GRAY, ls=1.5)

def dg_quad(s, X, Y, W, H, items):
    cw = (W - 0.18) / 2; ch = (H - 0.18) / 2
    for i, (t, d, c) in enumerate(items[:4]):
        x = X + (i % 2) * (cw + 0.18); y = Y + (i // 2) * (ch + 0.18)
        node(s, x, y, cw, ch, t, c, 7.5, True, sub=d)

def dg_hflow(s, X, Y, W, H, items, accent=GRAY, bh=0.60, size=7):
    n = len(items); gap = 0.16; bw = (W - gap*(n-1)) / n
    for i, it in enumerate(items):
        t, d = it
        x = X + i*(bw+gap)
        node(s, x, Y, bw, bh, t, accent, size, True, sub=d)
        if i < n-1: ah(s, x + bw, x + bw + gap, Y + bh/2)

def dg_table(s, X, Y, W, H, header, rows, accent=GRAY, rh=0.34, fs=6.8):
    n = len(header); cw = W / n
    for j, hd in enumerate(header):
        node(s, X + j*cw, Y, cw, rh, hd, accent, fs, True, fill=PALE)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            node(s, X + j*cw, Y + (i+1)*rh, cw, rh, v, LIGHT, fs, j == 0)

# ================= 内容 =================
def build(path):
    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    P = [0]
    def pn():
        P[0] += 1; return P[0]

    # 封面
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE; bg.line.fill.background(); bg.shadow.inherit = False
    line(s, 1.0, 1.45, 0.9, 0.03, INK)
    T(s, 1.0, 1.72, 11.0, 0.8, "AgentENV 沙箱：图解全课", 36, True, INK)
    T(s, 1.02, 2.58, 11.0, 0.4, "28 讲 · 左图右注 · 每页 5 条机制 + 数字 + 易错/追问", 12, False, GRAY)
    T(s, 1.02, 3.30, 10.8, 2.2,
      "怎么读：左边一张图，是这一课的骨架；右边五条，是这张图每一处「为什么」。\n"
      "数字只在核验过的地方给；没测过的写「量级」或标注待实测。\n"
      "目标不是读完，是合上讲义能把这张图画出来。", 10, False, GRAY, ls=1.7)
    T(s, 1.02, 6.55, 11.0, 0.3, "基线 9f62cbe   ·   2026-11-16   ·   图示讲解版 v5", 8.5, False, FAINT)
    pn()

    # 全景
    teach(prs, "全景", "一台机器，三个执行环境", BLUE,
          [("为什么先讲位置", "同一个内核的三个视角：宿主用户态、宿主内核、Guest。分不清层，后面每个问题都会答错位置。"),
           ("三个进程", "server 管生命周期、firecracker 是 VMM、ublk-daemon 管块设备——三个独立宿主进程，不是线程。"),
           ("Guest 不是子进程", "Guest 里的程序由 Guest 内核调度，宿主 ps 看不到；它对应的宿主对象只是 firecracker 进程的内存。"),
           ("内核功能不是进程", "KVM、ublk 驱动、cgroup/seccomp 都是宿主内核里的功能，没有自己的 PID，不能当进程画。"),
           ("跨层通信只有两条", "控制走 Unix socket（server↔FC），应用走 TCP（server↔envd，经 Guest 网络）。")],
          [("3", "个宿主进程"), ("2", "条跨层通道"), ("1", "个宿主内核")],
          "易错：把 server 里的 FirecrackerInstance 对象当成一个进程。",
          "会被问：宿主 ps -eLf 能看到哪些？看不到哪些？", pn(), dg_three_layers)

    teach(prs, "全景", "一个变量，四个地址", BLUE,
          [("GPA 是 guest 眼里的物理地址", "它只对 Guest 有意义；对宿主来说只是一个数字，还要经 EPT 再翻一次。"),
           ("HVA 属于某个宿主进程", "说 HVA 必须带“谁的”：Firecracker 的 HVA 和 server 的 HVA 是两套地址空间。"),
           ("两条路径汇合在 HPA", "Guest 访存 GVA→GPA→HPA；Firecracker 访存 HVA→HPA。落在同一物理页，所以没有“两份内存”。"),
           ("memslot 是接线处", "登记 GPA↔HVA 只是软件关系；EPT 是硬件表，缺项时才按 memslot 算 HVA、取页、建项。"),
           ("为什么不用填 HPA", "用户态看不到物理地址，只能交 HVA；由宿主内核查宿主页表翻成 HPA。")],
          [("4", "种地址空间"), ("2", "次翻译"), ("0", "次数据复制")],
          "易错：以为 Guest 正常访存会经过 HVA。",
          "会被问：为什么 ioctl 里没有 HPA 参数？", pn(), dg_four_addr)

    teach(prs, "全景", "三个动作，常常被混成一个", PURPLE,
          [("KVM_RUN", "用户态进内核的一条系统调用；线程没换，只是特权级变了。"),
           ("VM-Exit", "Guest 与宿主执行环境的切换；仍然发生在同一个宿主线程内，由 KVM 处理。"),
           ("线程切换", "调度器把 CPU 给另一个线程——只有这一种才是“没拿到 CPU”。"),
           ("由此得到一条推论", "KVM 能处理的退出（补 EPT 映射）处理完直接重入，ioctl 从头到尾没返回过。"),
           ("诊断价值", "“虚拟机慢”要分三件事：退出太多（设备模型重）、线程被抢（超订）、IO 等待（缺页/后端慢）。")],
          [("3", "种边界"), ("1", "个会切线程"), ("0", "次必然返回")],
          "易错：把 VM-Exit 当成 KVM_RUN 返回用户态。",
          "会被问：一次 EPT 缺页，一定会让 FC 从 ioctl 返回吗？", pn(), dg_bound3)

    # 01
    teach(prs, "第 1 课", "一个进程，多个线程", BLUE,
          [("为什么不是一个线程", "vCPU 线程卡在 KVM_RUN 里跑 Guest 时，没人能接“请暂停”的请求，单线程 VMM 会死锁。"),
           ("三类线程各管一段", "vcpu 管“Guest 在跑”的时间；api 管“随时能接请求”；vmm 把请求翻译成协调动作。"),
           ("线程名是代码写死的", "源码 .name(\"fc_vcpu {i}\")，所以宿主 ps -eLf 才看得到；不写就只有默认名。"),
           ("一个 vCPU 一个线程", "配 2 个 vCPU，宿主就多两个线程；它们不永久独占物理核，会被调度。"),
           ("它不是“睡眠”", "线程在 KVM_RUN 里时，物理 CPU 可能正在它上面执行 Guest，CPU 占用率照样高。")],
          [("1", "进程"), ("N", "vCPU 线程"), ("16", "字节线程名上限")],
          "易错：以为 vCPU 线程在 KVM_RUN 里就是睡着了。",
          "会被问：配 4 个 vCPU，宿主会多几个线程？", pn(), dg_proc_threads)

    teach(prs, "第 2 课", "同一个数字，两块内存", BLUE,
          [("地址离开空间没有意义", "0x400000 在 server 里指向 P_A，在 firecracker 里指向 P_B；两张页表各自翻译。"),
           ("pwrite 没有远程参数", "buf 永远按调用者自己的地址空间解释，接口里没有“去哪个进程取”这个参数。"),
           ("PVM 补上了这一点", "pid 决定用谁的地址空间，remote_iov 说从哪取，local_iov 说放到自己哪。"),
           ("两个数组都在调用者内存", "remote_iov 元素里的地址才指向目标进程；把参数指针本身填成远程地址是常见错误。"),
           ("三个动作分开", "① 构造 iovec（不复制）② 内核复制一次 ③ writer 写文件——很多人把①当成②。")],
          [("2", "套页表"), ("1", "次复制"), ("0", "个全局地址")],
          "易错：以为内核会自动按被读进程解释地址。",
          "会被问：remote_iov 里应该填 GVA、GPA 还是 HVA？", pn(), dg_two_spaces)

    teach(prs, "第 3 课", "两条路径，一块物理内存", BLUE,
          [("翻译链", "GVA→GPA 由 Guest 页表；GPA→HPA 由 EPT；HVA→HPA 由宿主页表。"),
           ("登记不复制", "KVM_SET_USER_MEMORY_REGION 只记录范围，128 MiB 的内容始终只有一份。"),
           ("EPT 按需建立", "访问到缺项才由 KVM 现取页、现建项——这也是“登记完不等于内存已占”的原因。"),
           ("偏移公式要会算", "HVA = userspace_addr + (目标 GPA − guest_phys_addr)；算错一位就全错。"),
           ("memslot 还管脏页", "每条 memslot 可带 dirty log，快照的“哪些页要存”就是按它拿的。")],
          [("128", "MiB 一次登记"), ("4", "KiB 页粒度"), ("1", "份数据")],
          "易错：以为 memslot 就是 EPT 表本身。",
          "会被问：memslot 在哪、EPT 在哪、谁读谁？", pn(), dg_two_paths)

    # 02
    teach(prs, "第 4 课", "本质是一个 ioctl 的循环", PURPLE,
          [("谁在执行", "物理 CPU 执行 vCPU 线程的代码；调 ioctl 后在同一线程内切到内核、再切到 Guest。"),
           ("退出是硬件做的", "撞到 VMCS 配置的条件，硬件自动存现场、写 exit reason，再载入宿主状态。"),
           ("两条分支", "KVM 能处理的（补 EPT 映射）直接重入；办不了的（MMIO/PIO）才回到用户态。"),
           ("退出原因很多", "不只是设备：外部中断、EPT 缺页、I/O 指令都会退出；频率取决于负载与配置。"),
           ("两个不同的数", "退出次数（硬件）与唤醒次数（用户态）不是一回事，混起来会误判开销。")],
          [("2", "条分支"), ("1", "个循环"), ("0", "次必然返回")],
          "易错：把 VM-Exit 次数当成 VMM 开销。",
          "会被问：哪些退出会回到用户态？", pn(), dg_kvm_loop)

    teach(prs, "第 5 课", "“没被调度”不是“已暂停”", PURPLE,
          [("t4 是唯一难点", "vCPU1 只是没拿到 CPU；调度器再给它时间片，它会继续写 Guest RAM。"),
           ("三个完成点", "请求发出 → Firecracker 接收 → 全部 vCPU 确认；三段各自检查，不能互相代替。"),
           ("为什么必须确认", "只把状态标成 Paused 而某个 vCPU 还在写，之后读到的内存就可能不一致。"),
           ("暂停 ≠ 冻结全部", "它只停 Guest 的 CPU 写入；宿主设备侧仍可能写同一块 RAM，还要协调在途 IO。"),
           ("暂停 ≠ 快照", "后面还有捕获内存、写层、fsync、改 manifest，每一步都可能失败。")],
          [("3", "个完成点"), ("N+1", "方 barrier"), ("0", "次可省确认")],
          "易错：把“请求发出”或“API 返回”当成 VM 已停。",
          "会被问：只暂停一个 vCPU，能说 VM 已暂停吗？", pn(), dg_pause)

    teach(prs, "第 6 课", "队列在内存里，通知只提醒", PURPLE,
          [("描述符只描述", "16 字节：addr/len/flags/next；它不复制字节，只说明缓冲区在哪、多长。"),
           ("两个环分工", "avail 由 Guest 写（我有活给你），used 由设备写（我做完了）；都在 Guest RAM 里。"),
           ("通知不携带数据", "doorbell 只是“去检查队列”，一次通知可对应多项工作，所以通知次数 ≠ 请求数。"),
           ("复用的风险", "同一链头发布两次＝两次使用机会；Guest 没处理完就交回，设备可能覆盖你还要读的内容。"),
           ("为什么快", "模拟真实设备时每个寄存器访问都是一次 VM-Exit；VirtIO 把数据批量放共享内存里搬。")],
          [("16", "字节/描述符"), ("2", "个环"), ("1", "次通知 = 多项")],
          "易错：把“设备发布 used”当成“Guest 已处理”。",
          "会被问：通知里到底传了什么？", pn(), dg_virtio)

    # 03
    teach(prs, "第 7 课", "控制面与数据面，两条通道", GREEN,
          [("控制面走宿主 socket", "server ↔ firecracker（--api-sock），HTTP 只是消息格式，不走 TCP、不经过 Guest。"),
           ("数据面走共享队列", "Guest 驱动 ↔ 设备，需要 Guest 配合发布描述符；暂停显然不能依赖它。"),
           ("为什么不能依赖 Guest", "暂停的用途之一就是“Guest 不配合时也能停住它”——依赖它就是循环论证。"),
           ("超时有三种可能", "没送到 / 做成了响应丢了 / 还在做；所以超时不能直接推出“VM 还在跑”。"),
           ("函数名不等于位置", "pause() 是 server 调自己的对象，由它发请求；调用者并没有进入 Guest。")],
          [("1", "条 socket"), ("3", "种超时"), ("0", "次进 Guest")],
          "易错：把 socket 当网络；把超时当失败。",
          "会被问：超时后你发 resume 有什么风险？", pn(), dg_two_channels)

    teach(prs, "第 8 课", "三层就绪，一层比一层强", GREEN,
          [("第一层：进程与 socket", "能连上 API socket 只证明 VMM 起来了、路径对；VM 还没配好。"),
           ("第二层：网络可达", "宿主经 tap0 能到 Guest；证明 netns、网卡、IP、端口都对。"),
           ("第三层：应用能应答", "GET /health 非 4xx/5xx；能发现“进程在、端口开、服务却卡住”。"),
           ("health 的具体行为", "不校验 body（204 也算过），单次上限 1 秒，失败重试，整体期限耗尽才报超时。"),
           ("两个接口分开", "start_nowait 只等 socket；wait_for_ready 才等 envd——所以可以先干别的再等。")],
          [("3", "层就绪"), ("1", "秒/次探测"), ("0", "次校验 body")],
          "易错：把 health 通过当成鉴权通过（它不带 token）。",
          "会被问：端口能连、命令不能执行，卡在哪层？", pn(), dg_tiers)

    teach(prs, "第 9 课", "exec 返回的是流，不是结果", GREEN,
          [("一次 exec 三类事件", "Start{pid} 表示进程已创建；Data 是 stdout/stderr 分段；End{code} 表示已退出。"),
           ("两个独立判断", "① 事件收齐了吗（协议层 Ok/Err）② exit_code 是多少（程序层）——不能互相代替。"),
           ("成功要三样", "wait 返回 Ok + 收到 End + exit_code 符合预期；只有 Start 说明不了任何事。"),
           ("没有 shell", "命令与参数分开传：没有管道、通配符、重定向语义；要这些就显式调 sh -c。"),
           ("超时与终止", "超时后发终止请求可能失败，所以不能断言进程已退出；重试还可能重复执行。")],
          [("3", "类事件"), ("2", "个判断"), ("1", "个退出码")],
          "易错：看到 Start 就当成功；只看 exit_code 不看流是否收齐。",
          "会被问：进程没有任何输出时，Data 会出现吗？", pn(), dg_stream)

    # 04
    teach(prs, "第 10 课", "一条数据，三个坐标系", ORANGE,
          [("文件偏移", "属于 Guest 文件系统；ext4 的 extent 决定它映射到哪个逻辑块。"),
           ("LBA", "块设备的语言；必须是“第几块 + 块大小”，只说数字会被追问单位。"),
           ("后端位置", "层文件里的某段字节，只有宿主知道；逻辑偏移与它没有固定对应。"),
           ("页缓存的影响", "命中时这次 read 可能不产生设备 IO；但路径解析、元数据仍可能产生 IO。"),
           ("写路径四个节点", "write 进页缓存 → 回写交 virtio → 后端写层 → fsync 才算持久化。")],
          [("3", "个偏移"), ("4", "个写节点"), ("0", "次必读盘")],
          "易错：以为文件偏移 0 就是磁盘偏移 0。",
          "会被问：一次 4 KiB 读，实际可能读多少字节？", pn(), dg_offsets)

    teach(prs, "第 11 课", "分层是覆盖映射", ORANGE,
          [("读取规则只有一条", "从最新层往下查，第一个有记录的就赢，命中即停；都没有才是空洞。"),
           ("“无记录”不是零", "它表示这层没管这段，要继续往下找——把回落当零会读错数据。"),
           ("“显式零”必须终止", "表示“我明确写过这里是 0”；当成无记录就会把父层旧数据暴露出来。"),
           ("叠加不是拼字节", "拼接只会得到 A/B/C/D/X/Y，表达不了“X 替换位置 1”。"),
           ("边界", "一个逻辑读可能跨多段层内数据；后端读失败必须报错，不能静默当零。")],
          [("4", "种情形"), ("2", "个语义坑"), ("1", "条规则")],
          "易错：以为“没记录”读出来是零。",
          "会被问：父层有旧值、新状态应为零，能省略吗？", pn(), dg_overlay)

    teach(prs, "第 12 课", "内核给壳，用户态给内容", ORANGE,
          [("三个节点", "ublk-control 管创建删除；ublkcN 是命令交接；ublkbN 是对外读写（FC 挂的是它）。"),
           ("创建流程", "server 发 Create → 内核分配 N → daemon 等节点真正可打开 → 回 (dev_id, path)。"),
           ("四步处理", "等待（io_uring）→ 领取（CQE 到）→ 解析（OverlayBD 查索引）→ 提交（COMMIT）。"),
           ("第一步最容易错", "领取的 CQE 只表示请求送到了 daemon，不表示数据读完。"),
           ("集中式的取舍", "一个进程管全节点设备：密度高、缓存集中；代价是单点，挂了该节点块 IO 全停。")],
          [("3", "个设备节点"), ("4", "步处理"), ("1", "个单点")],
          "易错：把 FETCH 的完成当成数据读完。",
          "会被问：daemon 挂了，这个节点的沙箱会怎样？", pn(), dg_ublk)

    # 05
    teach(prs, "第 13 课", "映射了 ≠ 分配了 ≠ 复制了", PURPLE,
          [("mmap 只建 VMA", "登记虚拟范围与属性；128 MiB 不是立刻占 128 MiB 物理内存。"),
           ("缺页三类", "minor（页已在内存）、major（要读盘）、非法访问（SIGSEGV）；写保护缺页不算非法。"),
           ("两种写语义", "MAP_SHARED 写回共享缓存；MAP_PRIVATE 只影响自己的私有副本。"),
           ("COW 的时机", "fork 后共享、PTE 只读；任一方写才复制——不是 fork 时复制，也不是 mmap 时复制。"),
           ("microVM 的对应", "只读后端 + MAP_PRIVATE：读共享页缓存，写才 COW（FC 1.12.1 memory.rs:136 已核）。")],
          [("3", "类缺页"), ("4", "KiB 页"), ("1", "次复制/首次写")],
          "易错：以为 mmap 就占满物理内存；以为 COW 在映射时发生。",
          "会被问：恢复后首次读和首次写分别发生什么？", pn(), dg_mmap)

    teach(prs, "第 14 课", "快照是四件套", PURPLE,
          [("四件套", "VM 状态（寄存器/设备）+ 内存镜像 + 磁盘视图 + 恢复配置；缺一件恢复不出同款机器。"),
           ("四个完成点", "暂停 → 捕获 → 持久化 → 释放运行时；顺序固定，含义各不相同。"),
           ("为什么必须暂停", "抓取期间页在变，会拼出“从未同时存在”的状态（x=100,y=110）。"),
           ("暂停只冻 Guest CPU", "宿主设备侧仍可能写 Guest RAM，完整方案还要协调设备与在途 IO。"),
           ("一致性 vs 业务一致性", "VM 内部一致 ≠ 应用事务已提交；外部支付/数据库不随快照回滚。")],
          [("4", "件套"), ("4", "个完成点"), ("1", "个必要前提")],
          "易错：pause 成功就当快照成功。",
          "会被问：哪一步失败会造成“有文件但恢复不了”？", pn(),
          lambda s, X, Y, W, H: (
              dg_quad(s, X, Y, W, H*0.55, [("① VM 状态", "寄存器/设备", BLUE), ("② 内存镜像", "RAM 字节", PURPLE),
                                           ("③ 磁盘视图", "层+父层引用", ORANGE), ("④ 恢复配置", "层顺序/设备", GREEN)]),
              dg_hflow(s, X, Y + H*0.62, W, 0.62, [("暂停", "vCPU 全停"), ("捕获", "读内存/写层"),
                                                   ("持久化", "fsync/上传"), ("释放", "回收运行时")], PURPLE)),
          wide=True)

    teach(prs, "第 15 课", "增量必须有基线", PURPLE,
          [("基线不可省", "S1/S2 只记覆盖，完整视图靠回落；丢弃父层就会读出错误内容。"),
           ("dirty 的含义", "在跟踪区间内被记录为写过；改回原值仍可能脏，不保证与父层不同。"),
           ("present 是另一维度", "描述页在不在，不是修改历史；不能和 dirty 混。"),
           ("内容为零是第三件事", "父层有旧值、新状态应为零时，必须写显式零或零字节，不能靠“不驻留”。"),
           ("四个不同指标", "镜像逻辑大小、新层数据量、读请求数、恢复时实际读盘量——不能互相代入。")],
          [("3", "个维度"), ("4", "KiB/页"), ("0", "次可省基线")],
          "易错：以为 dirty 列表能保证一致快照。",
          "会被问：改回原值，dirty 标记会消失吗？", pn(),
          lambda s, X, Y, W, H: dg_table(s, X, Y + 0.10, W, H,
                                          ["", "页0", "页1", "页2", "页3", "页4", "页5"],
                                          [["S0", "A", "B", "C", "D", "E", "F"],
                                           ["S1", "—", "B1", "—", "—", "E1", "—"],
                                           ["S2", "—", "—", "—", "—", "E2", "F2"],
                                           ["视图", "A", "B1", "C", "D", "E2", "F2"]], PURPLE, rh=0.46, fs=7.2),
          wide=True)

    teach(prs, "第 16 课", "每个参数都要能说出归属", PURPLE,
          [("四个参数", "pid=firecracker；local_iov=server 的 buffer；remote_iov=firecracker 的 HVA；flags=0。"),
           ("两个数组都在本地", "只有 remote_iov 元素里的地址指向目标进程；liovcnt 是元素个数不是字节。"),
           ("短读要前进", "返回 n < 请求长度时，源与目的同时前进 n，不是从头重读。"),
           ("零进展必须报错", "返回 0、超长、地址加法溢出不当作成功；EINTR 才重试。"),
           ("async 外壳不改实现", "标了 async 也仍是同步 process_vm_readv，不会自动让出 worker。")],
          [("2", "个 iovec 数组"), ("1", "次复制"), ("0", "次自动异步")],
          "易错：把 async 当异步 IO；把读成功当已持久化。",
          "会被问：8192 只回 4096，下一次从哪继续？", pn(),
          lambda s, X, Y, W, H: (
              node(s, X, Y + 0.05, W*0.52, 1.30, "", PURPLE, 7, fill=PALE),
              T(s, X + 0.12, Y + 0.14, W*0.48, 1.14,
                "pid        → firecracker\nlocal_iov  → server buffer\nremote_iov → FC 的 HVA\n"
                "liovcnt    → 元素个数\nflags      → 必须 0", 7, False, INK, ls=1.45),
              dg_hflow(s, X + W*0.56, Y + 0.05, W*0.44, 0.60, [("源", "Guest RAM"), ("复制", "内核一次")], PURPLE),
              T(s, X + W*0.56, Y + 0.75, W*0.44, 0.70, "之后 writer 写成层\n→ 先读到 server 再写文件", 7, False, GRAY, ls=1.4),
              dg_hflow(s, X, Y + 1.55, W, 0.62, [("正常", "填满"), ("短读", "前进 n"), ("EINTR", "重试"), ("零进展", "报错")], PURPLE)),
          wide=True)

    teach(prs, "第 17 课", "两条线：元数据与字节", PURPLE,
          [("元数据线", "范围 → entry(tag/src_offset/len/logical_offset) → chunk → 输出索引。"),
           ("字节线", "源 HVA → buffer → writer；buffer 生命周期必须覆盖实际写入。"),
           ("chunk ≠ 一次 syscall", "源是 PVM 时每个 entry 各走一遍读取，短读还要循环。"),
           ("四个不同指标", "chunk 大小、并发度、syscall 次数、真实磁盘 IO 次数不能混。"),
           ("两层完成", "finalize 只保证格式完成；rename 只换名字——都不等于断电持久化。")],
          [("2", "条线"), ("1", "个 buffer"), ("0", "次自动持久化")],
          "易错：把 finalize+rename 当持久化。",
          "会被问：一个 chunk 两个 entry，是几次跨进程读？", pn(),
          lambda s, X, Y, W, H: (
              node(s, X, Y + 0.05, W, 0.44, "元数据：范围 → entry → 输出索引（逻辑范围 → 层内位置）", BLUE, 7),
              node(s, X, Y + 0.58, W, 0.44, "字节：源 HVA → buffer → writer（寿命覆盖写入）", ORANGE, 7),
              dg_hflow(s, X, Y + 1.16, W, 0.46, [("header", ""), ("payload", "紧凑"), ("index", "映射"), ("trailer", "")], GRAY, 0.46),
              T(s, X, Y + 1.78, W, 0.60, "finalize 完成格式 / rename 换名字 / fsync 才抗断电", 7.2, True, GRAY)),
          wide=True)

    teach(prs, "第 18 课", "恢复不是把内存读回来", PURPLE,
          [("五步准备", "检查 ublk → 加载 VM 状态（resume_vm=false）→ 映射只读内存 → 补卷/MMDS/限流 → resume。"),
           ("为什么先不跑", "先把状态、设备、网络、额外盘装好，最后才让 vCPU 执行，否则 Guest 会在配置不全时开跑。"),
           ("一页怎么变可访问", "GPA 缺项 → 向只读设备发块读 → daemon 查 OverlayBD → 取块填页 → 继续。"),
           ("共享与私有（已核验）", "多沙箱共享同一只读 ublk 设备与页缓存；FC 用 MAP_PRIVATE，写才 COW。"),
           ("推论", "恢复成功 ≠ 所有页在宿主 RAM；首条命令慢、内存指标不高是正常的。")],
          [("5", "步"), ("1", "次缺页/页"), ("0", "次全量预读")],
          "易错：以为恢复会把全部内存读回宿主。",
          "会被问：恢复后首条命令慢，是故障还是正常？", pn(),
          lambda s, X, Y, W, H: (
              dg_hflow(s, X, Y + 0.05, W, 0.62, [("准备", "ublk/盘/网"), ("加载状态", "resume_vm=false"),
                                                 ("映射内存", "只读设备"), ("补配置", "卷/MMDS"), ("resume", "vCPU 执行")], PURPLE),
              T(s, X, Y + 0.80, W, 0.86,
                "写这一页：COW 到私有层，共享镜像不动。\n"
                "依据：agentenv device.rs:573-582（共享设备与页缓存）+ FC 1.12.1 memory.rs:136（MAP_PRIVATE）。", 7, False, GRAY, ls=1.4)),
          wide=True)

    # 06
    teach(prs, "第 19 课", "出站与入站，两条相反的路", AMBER,
          [("出站", "eth0 → virtio → tap0 → 沙箱 netns 路由 → SNAT 改源 → veth → 主 netns → MASQUERADE。"),
           ("入站", "server 连 slot 地址 → veth → netns PREROUTING DNAT 改目的 → tap0 → FC → Guest envd。"),
           ("两层 NAT 的目的", "第一层让宿主区分实例；第二层让流量适配出口地址。"),
           ("同名接口不冲突", "每个 netns 都能有 tap0，先由 netns 隔开，再用 slot 地址区分实例。"),
           ("完成点", "TX 的 used 只表示缓冲可回收，不代表远端收到、更不代表业务成功。")],
          [("2", "层 NAT"), ("2", "条方向"), ("1", "对 veth/沙箱")],
          "易错：以为同名 tap0 会冲突；以为 TX 完成＝对端收到。",
          "会被问：两个沙箱 Guest 用同一段 IP，为什么不冲突？", pn(),
          lambda s, X, Y, W, H: (
              T(s, X, Y + 0.02, W, 0.20, "出站", 7, True, AMBER),
              dg_hflow(s, X, Y + 0.24, W, 0.56, [("eth0", "virtio"), ("tap0", "沙箱 netns"), ("SNAT", "改源"),
                                                 ("veth", "主 netns"), ("MASQ", "出口")], AMBER),
              T(s, X, Y + 0.90, W, 0.20, "入站", 7, True, BLUE),
              dg_hflow(s, X, Y + 1.12, W, 0.56, [("server", "slot 地址"), ("veth", "进 netns"), ("DNAT", "改目的"),
                                                 ("tap0→FC", "VirtIO RX"), ("envd", "处理")], BLUE),
              T(s, X, Y + 1.78, W, 0.62, "返回包靠 conntrack 逆变换，不是 server 每次读包再转发。", 7, False, GRAY)),
          wide=True)

    teach(prs, "第 19 课 · 细节", "tap 与 veth，DNAT 与 SNAT", AMBER,
          [("tap 连“进程 ↔ 内核”", "内核侧是网络接口，用户态侧是 fd；Firecracker 读写 fd 就是收发以太网帧。"),
           ("veth 连“内核 ↔ 内核”", "一对虚拟接口分处两个 netns，是 host 与沙箱之间的那段链路。"),
           ("DNAT 改目的", "入口用：外部访问落到里面；常连带端口一起改。"),
           ("SNAT/MASQUERADE 改源", "出口用：让里面访问外面时看起来是宿主；MASQ 取出口网卡地址。"),
           ("REDIRECT 是 DNAT 特例", "目的改成本机，把流量导给本机代理进程（第 19 课的 80/443 分支）。")],
          [("2", "组概念"), ("4", "个名字"), ("1", "张 conntrack")],
          "易错：把 DNAT 当成转发（转发由路由决定）。",
          "会被问：REDIRECT 与 DNAT 差在哪？", pn(),
          lambda s, X, Y, W, H: (
              node(s, X, Y + 0.05, W*0.48, 0.62, "tap", AMBER, 8, True, sub="进程 ↔ 内核栈（二层帧）"),
              node(s, X + W*0.52, Y + 0.05, W*0.48, 0.62, "veth", AMBER, 8, True, sub="内核栈 ↔ 内核栈（两 netns）"),
              dg_hflow(s, X, Y + 0.80, W, 0.56, [("DNAT", "改目的"), ("SNAT", "改源"),
                                                 ("MASQ", "取出口地址"), ("REDIRECT", "改到本机")], BLUE),
              T(s, X, Y + 1.50, W, 0.80,
                "DNAT 改完靠 conntrack 记住原值，回包再改回来——状态丢了，旧连接就断。\n"
                "所以快照恢复后“Guest 里 socket 还在、但连不通”是常见现象。", 7, False, GRAY, ls=1.45)),
          wide=True)

    teach(prs, "第 20 课", "四类威胁，四道门", AMBER,
          [("A. Guest 内作恶", "没越过任何门：Guest root 本来就能任意 syscall；挡它的是 Guest 自己的内核。"),
           ("B. VMM 被攻破", "已越过虚拟化边界；挡它的是 seccomp、降权、chroot、caps、LSM。"),
           ("C. 资源超用", "没越界，走正常消耗；挡它的是 cgroup 限值、vCPU 数、balloon。"),
           ("D. 网络外连", "没越界，走虚拟网卡；挡它的是 netns + veth + iptables + 出口代理。"),
           ("一句话分家", "namespace 改看见什么；cgroup 改能用多少；seccomp/caps/LSM 改能对内核做什么。")],
          [("4", "类威胁"), ("4", "道门"), ("0", "层可替代")],
          "易错：把 namespace 当成降权。",
          "会被问：Guest 里的 root 会被 seccomp 拦吗？", pn(),
          lambda s, X, Y, W, H: (
              dg_quad(s, X, Y + 0.05, W, H*0.62, [("A. Guest 内作恶", "Guest 内核挡", BLUE),
                                                  ("B. VMM 被攻破", "seccomp/降权/caps", ORANGE),
                                                  ("C. 资源超用", "cgroup/vCPU/balloon", GREEN),
                                                  ("D. 网络外连", "netns/iptables/代理", PURPLE)]),
              T(s, X, Y + H*0.72, W, 0.44, "只做 namespace ＝ 什么都没锁；只做 seccomp ＝ 资源随便吃。", 7.2, True, GRAY)),
          wide=True)

    teach(prs, "第 20 课 · 细节", "seccomp 是线程级的", AMBER,
          [("作用对象是线程", "filter 装在每个线程上，同进程不同线程可有不同白名单（vmm 60 / api 35 / vcpu 43 条）。"),
           ("拦的是宿主 syscall", "Guest 内部的 syscall 由 Guest 内核处理，seccomp 完全看不到。"),
           ("默认动作是 trap", "命中未允许的 syscall 直接 SIGSYS 杀进程，不是返回 EPERM。"),
           ("升级会踩坑", "新版本引入新 syscall，旧过滤器当场 trap；所以过滤器必须跟版本走。"),
           ("pids.max 挡不住 Guest", "它只数宿主 cgroup 里的 task；Guest 进程不是宿主 task。")],
          [("3", "组白名单"), ("60/35/43", "条数"), ("1", "次 SIGSYS")],
          "易错：以为 seccomp 能约束 Guest 内的程序。",
          "会被问：升级 FC 版本为什么可能直接崩？", pn(),
          lambda s, X, Y, W, H: (
              node(s, X, Y + 0.05, W*0.46, 1.10, "", AMBER, 7, fill=PALE),
              T(s, X + 0.12, Y + 0.14, W*0.42, 0.95,
                "vmm 线程   60 条\napi 线程   35 条\nvcpu 线程  43 条\ntrap → SIGSYS", 7, False, INK, ls=1.5),
              node(s, X + W*0.50, Y + 0.05, W*0.50, 1.10, "", ORANGE, 7, fill=PALE),
              T(s, X + W*0.50 + 0.12, Y + 0.14, W*0.44, 0.95,
                "Guest 内 syscall 不受约束\n新 syscall 不在白名单 → 崩\npids.max 只数宿主 task", 7, False, INK, ls=1.5),
              T(s, X, Y + 1.28, W, 0.60, "逃逸后还剩什么：seccomp 限 syscall / 降权 / chroot / caps / netns", 7.2, True, GRAY)),
          wide=True)

    # 07
    teach(prs, "第 21 课", "谁拥有，谁释放", TEAL,
          [("对象与拥有者要对上", "netns/veth 由创建流程拥有；ublk 设备由 daemon 引用计数；共享层由快照管理。"),
           ("释放条件不同", "设备靠最后一个句柄释放；层靠无引用；进程靠 wait 回收，避免僵尸。"),
           ("中途失败最危险", "创建到一半失败，网络设备与 cgroup 可能没人回收，泄漏成“幽灵沙箱”。"),
           ("超时 ≠ 退出", "envd 超时只说明没收到响应，不等于 FC 进程已退出。"),
           ("共享资源要等 IO", "设备在途 IO 完成后才能复用或销毁，否则会写坏别人。")],
          [("4", "类资源"), ("1", "套引用计数"), ("0", "次可提前释放")],
          "易错：以为引用消失＝资源已回收。",
          "会被问：envd 超时能说明 FC 退出了吗？", pn(),
          lambda s, X, Y, W, H: dg_table(s, X, Y + 0.05, W, H,
                                          ["对象", "拥有者", "释放条件"],
                                          [["netns / veth", "创建流程", "删设备与 netns"],
                                           ["ublk 设备", "daemon（引用计数）", "最后句柄释放"],
                                           ["共享快照层", "快照管理", "无引用后回收"],
                                           ["FC 进程", "server", "wait 回收防僵尸"]], TEAL, rh=0.42, fs=6.8),
          wide=True)

    teach(prs, "第 22 课", "async 让出了什么", TEAL,
          [("async 只换调度", "它让出线程，不改变底层是不是阻塞；同步 syscall 照样占住 worker。"),
           ("所以要看“谁在等”", "提交即返回才是真异步；方法体里直接调用同步 IO 就不是。"),
           ("buffer 寿命", "提交出去的内存要活到 IO 完成，否则可能写到别人的数据上。"),
           ("取消不等于停止", "取消只表示不再关心结果，底层操作可能仍在跑，仍要等完成或明确丢弃。"),
           ("测量口径", "区分 wall 与 CPU、等待与执行；别用 async 掩盖真实的阻塞成本。")],
          [("1", "个 worker"), ("0", "次自动异步"), ("1", "条 buffer 寿命")],
          "易错：把 async 当多线程/并行。",
          "会被问：单 worker 下两个任务能交替吗？", pn(),
          lambda s, X, Y, W, H: (
              node(s, X, Y + 0.05, W*0.46, 1.05, "", ORANGE, 7, fill=PALE),
              T(s, X + 0.12, Y + 0.14, W*0.42, 0.92, "async 里调同步 IO\nworker 被阻塞\n其它任务排不上", 7, False, INK, ls=1.5),
              node(s, X + W*0.50, Y + 0.05, W*0.50, 1.05, "", GREEN, 7, fill=PALE),
              T(s, X + W*0.50 + 0.12, Y + 0.14, W*0.44, 0.92, "真异步 IO\n提交即返回\n完成时唤醒", 7, False, INK, ls=1.5),
              T(s, X, Y + 1.25, W, 0.60, "同样的吞吐下，被阻塞的 worker 会拖高尾延迟（p99）", 7.2, False, GRAY)),
          wide=True)

    teach(prs, "第 23 课", "失败时状态不能乱跳", TEAL,
          [("状态有前置条件", "Running → Pausing → Paused → Resuming，每一步都有“什么时候算到了”。"),
           ("跳步的后果", "没确认就捕获 → 不一致；捕获失败就宣布 Paused → 状态与磁盘不符。"),
           ("重试要幂等", "同一请求重放不能产生两份产物或两次副作用。"),
           ("失败三问", "现在是什么状态、残留了什么、下一步怎么安全推进。"),
           ("残留清理", "临时文件、半写层、占用的设备都要有明确清理路径。")],
          [("4", "个状态"), ("3", "个问题"), ("1", "条幂等要求")],
          "易错：把“请求失败”当成“状态未变”。",
          "会被问：捕获写了一半失败，回滚到哪一步？", pn(),
          lambda s, X, Y, W, H: (
              dg_hflow(s, X, Y + 0.10, W, 0.66, [("Running", "正常"), ("Pausing", "等确认"),
                                                 ("Paused", "可捕获"), ("Resuming", "重加载")], TEAL),
              T(s, X, Y + 0.95, W, 1.0,
                "失败时最危险的是「状态已改、产物未成」：\n"
                "例如标成 Paused 但内存层只写了一半，后续恢复会读到不完整镜像。", 7.2, False, GRAY, ls=1.45)),
          wide=True)

    teach(prs, "第 24 课", "度量口径：先分类，再谈平均", TEAL,
          [("三个口径", "wall（墙上时间）、CPU（谁在烧）、分布（p50/p99）——只说均值等于没说。"),
           ("冷启动要分段", "拉镜像 / 建盘 / 起 VMM / 等 envd / 首条命令，每段给 wall 与 CPU。"),
           ("两个“就绪”", "资源就绪（设备/网络可用）与首命令完成（服务能跑）是两个指标。"),
           ("抖动来源", "调度、超订、路径不同（缓存命中 vs 缺页）、单点排队、内存回收。"),
           ("A/B 要公平", "固定 Guest 状态、脏页集合、快照链、并发；把 server 与 FC 纳入同一计量。")],
          [("3", "个口径"), ("5", "个阶段"), ("1", "条基线")],
          "易错：只报平均值；把组件间搬 CPU 当减少总量。",
          "会被问：wall 高而 CPU 低，说明什么？", pn(),
          lambda s, X, Y, W, H: (
              dg_hflow(s, X, Y + 0.05, W, 0.56, [("拉镜像", ""), ("建盘", ""), ("起 VMM", ""),
                                                 ("等 envd", ""), ("首命令", "")], TEAL),
              T(s, X, Y + 0.75, W, 0.24, "p50 / p90 / p99 / max（同一操作按路径分类）", 7, True, GRAY),
              dg_hflow(s, X, Y + 1.02, W, 0.30, [("p50", ""), ("p90", ""), ("p99", ""), ("max", "")], ORANGE, 0.30),
              T(s, X, Y + 1.45, W, 0.50, "均值相同、分布不同的两个系统，体验完全不同。", 7.2, False, GRAY)),
          wide=True)

    teach(prs, "第 25 课", "多节点与预热池", TEAL,
          [("三层角色", "gateway 接入、scheduler 选节点、node 落地——选节点与落地是两次决策。"),
           ("池的三层", "FC 进程池、网络槽位池、磁盘设备池；预热省的是“创建”那几段。"),
           ("预热不等于就绪", "进程在、网络通、盘在，仍要装载快照、关联设备、等 envd。"),
           ("并发要原子认领", "两个请求抢同一实例，只能有一个成功；靠 CAS/租约，不靠“先查再写”。"),
           ("归属丢了怎么办", "心跳/绑定丢失不等于 VM 消失，要能重建视图或直接核对节点。")],
          [("3", "层池"), ("2", "次决策"), ("1", "次原子认领")],
          "易错：以为查不到归属就说明沙箱退出了。",
          "会被问：预热完成后还缺哪几步？", pn(),
          lambda s, X, Y, W, H: (
              dg_hflow(s, X, Y + 0.05, W, 0.56, [("gateway", "接入"), ("scheduler", "选节点"),
                                                 ("node A", "落地"), ("node B", "落地")], TEAL),
              dg_hflow(s, X, Y + 0.80, W, 0.56, [("FC 池", "已起"), ("网络池", "已建"),
                                                 ("磁盘池", "已备"), ("就绪", "envd 探活")], TEAL),
              T(s, X, Y + 1.55, W, 0.60, "预热只砍掉「创建」；「恢复装载」与「首命令」的代价照付。", 7.2, False, GRAY)),
          wide=True)

    teach(prs, "第 26 课", "模板、快照、实例、缓存", TEAL,
          [("四层含义", "模板是只读底座；快照是某刻状态；实例是私有可变；缓存是本地副本。"),
           ("共享与私有", "同模板起的 A/B：私有 RAM 与根盘改动互不影响；外部共享可写盘会互相看见。"),
           ("父层不能乱删", "增量里“没记录”的范围要靠父层补；删了就恢复不出来。"),
           ("克隆要重随机化", "PID、RNG、时钟、序列号、主机名/IP 都需要在恢复时处理。"),
           ("外部副作用", "COW 保证内存隔离，不保证外部系统只被调用一次——要幂等键。")],
          [("4", "层含义"), ("1", "个只读底座"), ("N", "个私有层")],
          "易错：以为 COW 能保证外部副作用只发生一次。",
          "会被问：A 改了文件，B 已读的字节会变吗？", pn(),
          lambda s, X, Y, W, H: (
              dg_hflow(s, X, Y + 0.05, W, 0.62, [("模板", "只读底座"), ("快照", "某刻状态"),
                                                 ("实例", "私有可变"), ("缓存", "本地副本")], TEAL),
              T(s, X, Y + 0.85, W, 0.85,
                "父层依赖：S2 的视图 = S2 ∪ S1 ∪ S0；删父层 → 未覆盖范围读不出来。\n"
                "已读进 buffer 的旧字节不会因为文件被改而变；再读能否看见取决于缓存与同步。", 7, False, GRAY, ls=1.45)),
          wide=True)

    teach(prs, "第 27 课", "六条链，一条主线", TEAL,
          [("六条链", "创建、执行、读文件、暂停、恢复、销毁——每条的完成点都不一样。"),
           ("共同主线", "一个请求怎么落到硬件，再带着结果回到调用者。"),
           ("排障用法", "先定位：卡在哪条链、哪个完成点；再看那一层的证据（日志/指标）。"),
           ("最容易混的两次", "「暂停完成」vs「快照完成」；「进程在跑」vs「服务就绪」。"),
           ("验收方式", "任选两条链，能不看笔记说全完成点，才算真的走通。")],
          [("6", "条链"), ("2", "次易混"), ("1", "条主线")],
          "易错：把“某层完成”当“整件事完成”。",
          "会被问：读一个文件，中间有几次“完成”？", pn(),
          lambda s, X, Y, W, H: dg_quad(s, X, Y + 0.05, W, H*0.80,
                                        [("创建", "spawn→配置→启动→就绪", TEAL), ("执行", "envd→进程→事件流", TEAL),
                                         ("读文件", "VFS→virtio→ublk→层", TEAL), ("暂停/恢复/销毁", "确认→装载→回收", TEAL)]),
          wide=True)

    teach(prs, "第 28 课", "PVM 中转 vs 直接写出", TEAL,
          [("现状路径", "FC 的 Guest RAM 映射 → PVM 跨进程读 → server buffer → writer → 层文件。"),
           ("候选路径", "FC 用自己的 HVA 直接写文件；能省掉 server 侧中转，但不是零拷贝。"),
           ("省的是什么", "普通缓冲写仍有复制；格式、索引、稀疏、压缩仍需有人做。"),
           ("方案 A 的坑", "先导出原始 RAM 再转换，会新增中间文件与二次读取，可能抵消收益。"),
           ("必须保留的约束", "稳定 RAM 视图、覆盖设备写入、在途 IO 的生命周期、失败回滚。")],
          [("1", "次中转"), ("-20%", "最乐观降幅"), ("0", "次省掉约束")],
          "易错：以为省一次搬运就能减半时间。",
          "会被问：怎么设计 A/B 才算公平？", pn(),
          lambda s, X, Y, W, H: (
              node(s, X, Y + 0.05, W*0.46, 0.62, "现状：FC→PVM→server→writer", TEAL, 7.5, True),
              node(s, X + W*0.50, Y + 0.05, W*0.50, 0.62, "候选：FC 直接用 HVA 写", ORANGE, 7.5, True),
              T(s, X, Y + 0.85, W, 0.95,
                "假设总 wall 10 ms、其中 PVM 2 ms：即使这 2 ms 完全消失且没有新增成本，\n"
                "总时间也只到 8 ms（-20%）。真实并行阶段要看关键路径，不能把 wall 任意相加。", 7, False, GRAY, ls=1.45)),
          wide=True)

    # 08 面试
    teach(prs, "面试", "五个必深点", INK,
          [("① 地址空间", "GVA/GPA/HVA/HPA、PVM 参数归属、短读处理；证据：一次跨进程读的字节与耗时。"),
           ("② VM-Exit 分流", "MMIO 靠 EPT 缺映射、PIO 靠敏感指令；证据：一次压测的退出次数。"),
           ("③ 快照与恢复", "四件套、一致性、只读层+COW+按需；证据：冷/热恢复延迟对比。"),
           ("④ 隔离各层", "四道门、seccomp 线程级；证据：真实线程数与 Seccomp 值。"),
           ("⑤ 度量口径", "wall/CPU、p50/p99、资源就绪 vs 首命令；证据：分段耗时表。")],
          [("5", "个深点"), ("3", "层追问"), ("1", "个数字/点")],
          "易错：只讲机制，拿不出证据。",
          "会被问：哪几点你能立刻给出数字？", pn(),
          lambda s, X, Y, W, H: dg_table(s, X, Y + 0.05, W, H,
                                          ["深点", "要能说清", "证据"],
                                          [["地址空间", "四条线 + PVM 参数", "一次读取的字节/耗时"],
                                           ["VM-Exit", "MMIO/PIO + 分流", "退出次数"],
                                           ["快照恢复", "四件套 + COW/按需", "冷热恢复延迟"],
                                           ["隔离", "四道门 + 线程级 seccomp", "线程数与 Seccomp 值"],
                                           ["度量", "wall/CPU/p50/p99", "分段耗时表"]], INK, rh=0.36, fs=6.4),
          wide=True)

    teach(prs, "面试", "四段式：缺第 4 段就是只背过", INK,
          [("结论", "一句话给判断——面试官先听到的是答案，不是铺垫。"),
           ("机制", "两句讲清谁在哪一层做什么，点名进程/内核/硬件。"),
           ("边界", "一句半说清挡不住什么、代价是什么。"),
           ("证据", "一个数字、一次实测、或一次真实故障；这段才区分做过与看过。"),
           ("示范要点", "以“怎么隔离”为例：两类威胁、三个控制点、一条真实配置差异。")],
          [("4", "段"), ("90", "秒/题"), ("1", "个数字")],
          "易错：只报均值不报分位；只讲名词不讲边界。",
          "会被问：用 90 秒讲完「VM-Exit」，能吗？", pn(),
          lambda s, X, Y, W, H: (
              dg_hflow(s, X, Y + 0.05, W, 0.56, [("结论", "判断"), ("机制", "谁在哪层"),
                                                 ("边界", "挡不住什么"), ("证据", "数字/故障")], INK),
              node(s, X, Y + 0.80, W, 1.10, "", GRAY, 7, fill=PALE),
              T(s, X + 0.14, Y + 0.90, W - 0.28, 0.95,
                "示范：结论＝两类威胁；机制＝虚拟化 + seccomp/namespace/cgroup；\n"
                "边界＝namespace 不改权限、seccomp 看不到 Guest syscall；\n"
                "证据＝一份真实实现里 VMM 用 unshare -m 启动、没有 jailer。", 7, False, INK, ls=1.45)),
          wide=True)

    teach(prs, "下一步", "把讲过变成做过", INK,
          [("还没演练", "地址空间（PVM 参数与短读）、性能度量（冷启动怎么查）。"),
           ("还没跑", "/dev/kvm 通路、namespace 创建耗时、cgroup 限额是否生效。"),
           ("还没有数字", "冷/热恢复延迟、一次跨进程读耗时、一次压测的退出次数。"),
           ("还没写", "第 21—28 课面试格式版本；三篇项目故事。"),
           ("下一个动作", "在 WSL 里跑 ls -l /dev/kvm；通了就跑一次最小测量。")],
          [("3", "类缺口"), ("1", "个动作"), ("0", "次实测")],
          "易错：只看不测。",
          "会被问：下周补哪个数字？基线怎么定？", pn(),
          lambda s, X, Y, W, H: dg_quad(s, X, Y + 0.05, W, H*0.80,
                                        [("演练", "两个深点", BLUE), ("跑通", "/dev/kvm", ORANGE),
                                         ("数字", "延迟/耗时/次数", VIOLET), ("写作", "面试格式 + 故事", GREEN)]),
          wide=True)

    prs.save(path)
    print("saved:", path, "slides:", len(prs.slides))

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "review_v5.pptx")
