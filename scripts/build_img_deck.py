# -*- coding: utf-8 -*-
"""生成 24 张 16:9 全页图示，并组装成 PPT。
用法：python build_img_deck.py <输出pptx> [图片目录]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib16 import *          # noqa
import figlib16 as F
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches

IMGDIR = None
PAGES = []

def page(n, kicker, title, accent, draw, callouts, pitfall, ask):
    fig, ax = canvas()
    head(ax, kicker, title, accent)
    draw(ax)
    calls(ax, callouts, 13.4, accent)
    foot(ax, pitfall, ask)
    pageno(ax, n)
    name = os.path.join(IMGDIR, "p%02d.png" % n)
    save(fig, name)
    PAGES.append(name)
    print("  fig", n, os.path.basename(name))

# ---------------- 各页绘图 ----------------
def d_layers(ax):
    rows = [("宿主用户态", ["server", "firecracker", "ublk-daemon"], BLUE, 40.0),
            ("宿主内核", ["KVM", "ublk 驱动", "cgroup / seccomp"], PURPLE, 28.0),
            ("Guest", ["Guest 内核", "envd", "你的程序"], GREEN, 16.0)]
    for name, items, c, y in rows:
        txt(ax, 5.0, y + 4.0, name, 6.4, c, bold=True)
        bw = (108.0 - 8.0) / 3
        for i, it in enumerate(items):
            box(ax, 30.0 + i * (bw + 4.0), y, bw, 9.0, it, c, 7.4, True)
        ax.plot([5.0, 128.0], [y - 2.6, y - 2.6], color=LINE, lw=0.8)
    arrow(ax, (79.0, 26.0), (79.0, 25.2), LINE)
    arrow(ax, (79.0, 38.0), (79.0, 37.2), LINE)
    txt(ax, 82.0, 23.6, "Guest 不是 firecracker 的子进程", 5.4, GRAY)

def d_addr(ax):
    box(ax, 6.0, 40.0, 24.0, 8.0, "GVA", BLUE, 7.6, True, sub="Guest 程序")
    box(ax, 6.0, 28.0, 24.0, 8.0, "GPA", BLUE, 7.6, True, sub="Guest 内核")
    box(ax, 50.0, 32.0, 26.0, 9.0, "HPA", PURPLE, 8.0, True, sub="物理页")
    box(ax, 96.0, 40.0, 26.0, 8.0, "HVA", PURPLE, 7.6, True, sub="Firecracker")
    arrow(ax, (18.0, 39.6), (18.0, 36.4), BLUE)
    arrow(ax, (30.4, 32.0), (49.6, 35.0), BLUE)
    arrow(ax, (95.6, 44.0), (76.4, 38.0), PURPLE)
    txt(ax, 33.0, 31.0, "Guest 页表 + EPT", 5.2, GRAY)
    txt(ax, 78.0, 43.6, "宿主页表", 5.2, GRAY)
    box(ax, 26.0, 18.0, 76.0, 8.0, "memslot：GPA 区间 — HVA 区间（软件登记，不复制数据）", BLUE, 6.6, False)
    txt(ax, 6.0, 46.0, "两条路径落在同一块物理页，所以没有“两份内存”", 5.4, GRAY)

def d_bound(ax):
    rows = [("KVM_RUN 系统调用", "用户态 → 内核", "不切线程", GREEN),
            ("VM-Entry / VM-Exit", "Guest — 宿主执行环境", "不切线程", GREEN),
            ("宿主线程切换", "调度器换线程执行", "切了", ORANGE)]
    y = 42.0
    for i, (a, b, c, col) in enumerate(rows):
        box(ax, 8.0, y, 34.0, 8.0, a, PURPLE, 7.0, True)
        txt(ax, 46.0, y + 4.0, b, 5.8, GRAY)
        txt(ax, 96.0, y + 4.0, c, 6.0, col, bold=True)
        if i < 2:
            arrow(ax, (25.0, y - 0.4), (25.0, y - 4.0), LINE)
        y -= 11.0
    txt(ax, 8.0, 17.0, "只有最后一种才是「没拿到 CPU」；前两种都在同一个线程内完成", 5.6, GRAY)

def d_threads(ax):
    box(ax, 6.0, 16.0, 56.0, 36.0, "", BLUE, 7.0, fill=PALE)
    txt(ax, 9.0, 49.0, "firecracker（宿主进程，一个地址空间）", 5.8, BLUE, bold=True)
    items = [("vmm 主线程", "协调状态 / 设备事件"), ("api 线程", "Unix socket 收请求"),
             ("fc_vcpu 0", "ioctl(KVM_RUN)"), ("fc_vcpu 1", "ioctl(KVM_RUN)")]
    for i, (t, s) in enumerate(items):
        box(ax, 9.0, 41.0 - i * 6.6, 50.0, 5.8, t, BLUE, 6.4, True, sub=s)
    txt(ax, 68.0, 44.0, "线程名来自代码：", 5.8, GRAY, bold=True)
    txt(ax, 68.0, 40.0, ".name(\"fc_vcpu {i}\")\n所以 ps -eLf 看得到", 5.8, GRAY)
    txt(ax, 68.0, 30.0, "为什么必须多线程：\n单线程时 vCPU 卡在 KVM_RUN，\n没人接「请暂停」的请求", 5.8, GRAY)
    txt(ax, 68.0, 20.0, "代价：线程数 = 1 + 1 + N，\nseccomp/cgroup 都按这粒度记账", 5.6, GRAY)

def d_spaces(ax):
    box(ax, 6.0, 40.0, 26.0, 8.0, "server", ORANGE, 7.2, True, sub="0x400000")
    box(ax, 6.0, 28.0, 26.0, 8.0, "firecracker", PURPLE, 7.2, True, sub="0x400000")
    box(ax, 52.0, 40.0, 26.0, 8.0, "物理页 P_A", ORANGE, 7.2, True, sub="SERVER")
    box(ax, 52.0, 28.0, 26.0, 8.0, "物理页 P_B", PURPLE, 7.2, True, sub="GUEST")
    arrow(ax, (32.4, 44.0), (51.6, 44.0), ORANGE)
    arrow(ax, (32.4, 32.0), (51.6, 32.0), PURPLE)
    box(ax, 84.0, 40.0, 42.0, 8.0, "pwrite(fd, buf…)", ORANGE, 6.4, True, sub="buf 只能是自己的内存")
    box(ax, 84.0, 28.0, 42.0, 8.0, "process_vm_readv(pid…)", PURPLE, 6.4, True, sub="pid 决定用谁的空间")
    txt(ax, 6.0, 20.0, "所以读 Guest 内存时，remote 地址填 Firecracker 的 HVA；liovcnt 是元素个数，不是字节数", 5.6, GRAY)

def d_paths(ax):
    box(ax, 8.0, 40.0, 22.0, 7.6, "GVA", BLUE, 7.2)
    box(ax, 8.0, 29.0, 22.0, 7.6, "GPA", BLUE, 7.2)
    box(ax, 52.0, 34.0, 24.0, 8.0, "HPA", PURPLE, 7.6, True)
    box(ax, 100.0, 40.0, 22.0, 7.6, "HVA", PURPLE, 7.2)
    arrow(ax, (19.0, 39.6), (19.0, 36.8), BLUE)
    arrow(ax, (30.4, 32.8), (51.6, 37.0), BLUE)
    arrow(ax, (99.6, 43.8), (76.4, 39.0), PURPLE)
    txt(ax, 34.0, 30.6, "Guest 页表 + EPT", 5.2, GRAY)
    txt(ax, 80.0, 45.0, "宿主页表", 5.2, GRAY)
    box(ax, 8.0, 17.0, 116.0, 9.0, "", BLUE, 6.0, fill=PALE)
    txt(ax, 11.0, 23.0, "登记：KVM_SET_USER_MEMORY_REGION(guest_phys_addr, userspace_addr, size)", 5.4, INK)
    txt(ax, 11.0, 19.6, "只登记范围，不复制 RAM；缺 EPT 项时才按 memslot 算 HVA、取页、建项", 5.2, GRAY)

def d_kvm(ax):
    box(ax, 6.0, 38.0, 30.0, 9.0, "ioctl(KVM_RUN)", PURPLE, 7.4, True, sub="阻塞直到一次退出")
    box(ax, 44.0, 38.0, 34.0, 9.0, "硬件执行 Guest", PURPLE, 7.4, True, sub="非根模式")
    box(ax, 86.0, 38.0, 28.0, 9.0, "VM-Exit", PURPLE, 7.4, True, sub="写 exit_reason")
    arrow(ax, (36.4, 42.5), (43.6, 42.5), PURPLE)
    arrow(ax, (78.4, 42.5), (85.6, 42.5), PURPLE)
    arrow(ax, (100.0, 37.6), (100.0, 32.4), PURPLE)
    box(ax, 76.0, 24.0, 48.0, 8.0, "KVM 处理完直接重入", GREEN, 6.8, True, sub="ioctl 从头到尾没返回过")
    box(ax, 12.0, 24.0, 56.0, 8.0, "需要用户态模拟（MMIO / PIO）", ORANGE, 6.8, True, sub="KVM_RUN 返回 Firecracker")
    arrow(ax, (68.4, 28.0), (75.6, 28.0), LINE)
    txt(ax, 12.0, 18.0, "退出次数（硬件）≠ 被唤醒次数（用户态）：EPT 缺页这类 KVM 自己就办完了", 5.6, GRAY)

def d_pause(ax):
    ev = [("t1", "API 收到请求", GREEN), ("t2", "置暂停意图", GREEN), ("t3", "vCPU0 确认", GREEN),
          ("t4", "vCPU1 没被调度", ORANGE), ("t5", "vCPU1 确认", GREEN), ("t6", "暂停完成", BLUE)]
    n = 6; gap = 2.4; bw = (118.0 - gap*(n-1)) / n
    for i, (t, d, c) in enumerate(ev):
        x = 7.0 + i*(bw+gap)
        box(ax, x, 36.0, bw, 10.0, t, c, 6.6, True, sub=d)
        if i < n-1:
            arrow(ax, (x + bw + 0.4, 41.0), (x + bw + gap - 0.4, 41.0), LINE)
    txt(ax, 7.0, 31.0, "t4 是关键：只是“没拿到 CPU”，调度器再给时间片它就会继续写 Guest RAM", 5.8, ORANGE, bold=True)
    hchain(ax, 7.0, 18.0, 118.0, [("请求发出", "写进 socket"), ("FC 接收", "API 解析"),
                                  ("全部确认", "没有 vCPU 能跑"), ("快照完成", "另一件事")], PURPLE, 9.0)

def d_virtio(ax):
    box(ax, 6.0, 38.0, 40.0, 9.0, "描述符表", PURPLE, 7.0, True, sub="addr / len / flags / next")
    box(ax, 6.0, 24.0, 40.0, 8.0, "avail 环", GREEN, 7.0, True, sub="Guest 发布链头")
    box(ax, 60.0, 24.0, 40.0, 8.0, "used 环", ORANGE, 7.0, True, sub="设备发布完成")
    arrow(ax, (46.4, 28.0), (59.6, 28.0), LINE)
    box(ax, 60.0, 38.0, 40.0, 9.0, "设备后端", PURPLE, 7.0, True, sub="从 Guest RAM 取描述符")
    arrow(ax, (86.0, 37.6), (86.0, 32.4), LINE)
    arrow(ax, (26.0, 37.6), (26.0, 32.4), LINE)
    box(ax, 106.0, 24.0, 21.0, 23.0, "", GRAY, 5.4, fill=PALE)
    txt(ax, 108.0, 44.0, "通知\n只提醒\n不带数据", 5.4, GRAY)
    txt(ax, 6.0, 18.0, "通知次数 ≠ 请求数；设备发布 used ≠ Guest 驱动已处理；未处理完就交回缓冲，设备可能覆盖", 5.6, GRAY)

def d_channels(ax):
    box(ax, 6.0, 36.0, 56.0, 14.0, "控制面", GREEN, 7.6, True,
        sub="宿主 Unix socket\nPATCH /vm · 不需要 Guest 配合")
    box(ax, 68.0, 36.0, 59.0, 14.0, "数据面", ORANGE, 7.6, True,
        sub="Guest RAM 里的 virtqueue\n需要 Guest 驱动发布")
    hchain(ax, 6.0, 18.0, 121.0, [("请求发出", "写 socket"), ("FC 接收", "API 解析"),
                                  ("全部 vCPU 确认", "协议状态"), ("快照持久化", "另一件事")], GREEN, 9.0)

def d_tiers(ax):
    tiers = [("① API socket 可用", "能配 VM、能 pause", GREEN, 78.0),
             ("② 网络可达", "tap0 能到 Guest", GREEN, 62.0),
             ("③ envd /health 通过", "应用层能应答", BLUE, 46.0)]
    for i, (t, d, c, w) in enumerate(tiers):
        box(ax, 6.0, 42.0 - i * 11.0, w, 8.6, t, c, 7.0, True, sub=d)
    txt(ax, 6.0, 20.0, "强度递进：进程存在 → 端口能连 → 应用能应答；health 不校验 body，单次上限 1 秒", 5.6, GRAY)
    txt(ax, 6.0, 32.0, "start_nowait 只等 socket；wait_for_ready 才等 envd", 5.6, GRAY)

def d_stream(ax):
    hchain(ax, 6.0, 38.0, 121.0, [("start 请求", "cmd + args + env"), ("Start{pid}", "进程已创建"),
                                  ("Data", "stdout / stderr"), ("End{code}", "进程已退出")], GREEN, 10.0)
    box(ax, 6.0, 22.0, 56.0, 9.0, "判断一：事件收齐？", GREEN, 6.8, True, sub="收到 End = Ok，否则 Err")
    box(ax, 68.0, 22.0, 59.0, 9.0, "判断二：exit_code？", BLUE, 6.8, True, sub="0 / 非零")
    txt(ax, 6.0, 17.0, "成功要三样：wait 返回 Ok + 收到 End + exit_code 符合预期", 5.8, GRAY)

def d_offsets(ax):
    hchain(ax, 6.0, 40.0, 121.0, [("read()", "文件偏移 8 MiB"), ("ext4", "extent → LBA"),
                                  ("块层", "合并 / 排队"), ("virtio-blk", "描述符"), ("后端", "层文件")], ORANGE, 8.6, 2.6, 6.2, 5.0)
    txt(ax, 6.0, 34.0, "文件偏移 ≠ LBA ≠ 后端位置；文件内连续的数据，在磁盘上可以完全不连续", 5.6, GRAY)
    hchain(ax, 6.0, 20.0, 121.0, [("write 进页缓存", ""), ("回写交 virtio", ""),
                                  ("后端写层", ""), ("fsync 持久化", "")], GRAY, 8.0, 3.0)
    txt(ax, 6.0, 16.0, "write 返回 ≠ 持久化；快照前要不要预同步，是个真问题", 5.6, GRAY)

def d_overlay(ax):
    layers = [("upper（可写）", "位置1 → 新值", GREEN, 40.0),
              ("增量层（只读）", "位置3 → 显式零", ORANGE, 30.0),
              ("基层（只读）", "位置0/1/2 有数据", PURPLE, 20.0)]
    for t, d, c, y in layers:
        box(ax, 6.0, y, 56.0, 8.0, t, c, 6.6, True, sub=d)
    cells = [("P0", "基层 A", PURPLE), ("P1", "upper 新值", GREEN), ("P2", "显式零", ORANGE), ("P3", "显式零", ORANGE)]
    cw = (56.0 - 3*2.0) / 4
    for i, (t, d, c) in enumerate(cells):
        box(ax, 70.0 + i*(cw+2.0), 24.0, cw, 12.0, t, c, 6.2, True, sub=d)
    txt(ax, 70.0, 40.0, "最终视图（从上往下第一个命中）", 5.6, GRAY, bold=True)
    txt(ax, 70.0, 18.0, "「无记录」要回落；「显式零」必须终止\n拼接字节表达不了「X 替换位置 1」", 5.4, GRAY)

def d_ublk(ax):
    hchain(ax, 6.0, 40.0, 121.0, [("ublk-control", "创建 / 删除"), ("ublkcN", "命令交接"),
                                  ("ublkbN", "数据读写（FC 挂这个）")], ORANGE, 9.0, 3.0)
    hchain(ax, 6.0, 22.0, 121.0, [("① 等待", "io_uring"), ("② 领取", "CQE 到"),
                                  ("③ 解析", "OverlayBD 查索引"), ("④ 提交", "COMMIT")], ORANGE, 9.0, 3.0)
    txt(ax, 6.0, 17.0, "「领取」的 CQE 只表示请求送到 daemon，不表示数据读完", 5.8, ORANGE, bold=True)

def d_mmap(ax):
    hchain(ax, 6.0, 38.0, 121.0, [("mmap 之后", "只有 VMA，无物理页"), ("第一次读", "缺页：取页或分配"),
                                  ("第一次写", "COW：复制私有页")], PURPLE, 10.0, 3.0)
    txt(ax, 6.0, 30.0, "缺页三类：minor（页已在内存）／major（要读盘）／非法访问（SIGSEGV）；写保护缺页不算非法", 5.4, GRAY)
    txt(ax, 6.0, 25.0, "两种写语义：MAP_SHARED 写回共享缓存；MAP_PRIVATE 只影响私有副本", 5.4, GRAY)
    box(ax, 6.0, 16.0, 121.0, 7.6, "microVM 恢复：只读后端 + MAP_PRIVATE → 读共享页缓存，写才 COW（FC 1.12.1 已核）", PURPLE, 6.0, True, fill=PALE)

def d_snapshot(ax):
    quad(ax, 6.0, 50.0, 121.0, 18.0, [("① VM 状态", "寄存器 / 设备", BLUE), ("② 内存镜像", "RAM 字节 + 父层", PURPLE),
                                      ("③ 磁盘视图", "层 + 引用", ORANGE), ("④ 恢复配置", "层顺序 / 设备", GREEN)])
    hchain(ax, 6.0, 20.0, 121.0, [("暂停", "vCPU 全停"), ("捕获", "读内存 / 写层"),
                                  ("持久化", "fsync / 上传"), ("释放", "回收运行时")], PURPLE, 9.0, 3.0)

def d_resume(ax):
    hchain(ax, 6.0, 40.0, 121.0, [("准备", "ublk/盘/网"), ("加载状态", "resume_vm=false"),
                                  ("映射内存", "只读设备"), ("补配置", "卷 / MMDS"), ("resume", "vCPU 执行")], PURPLE, 9.0, 2.4)
    txt(ax, 6.0, 32.0, "一页怎么变得可访问：Guest 访问 GPA → 宿主缺项 → 向只读设备发块读 → daemon 查 OverlayBD → 填页", 5.4, GRAY)
    txt(ax, 6.0, 26.0, "写这一页：COW 到私有层。多沙箱共享同一只读设备与页缓存（agentenv device.rs:573-582）", 5.4, GRAY)
    txt(ax, 6.0, 19.0, "推论：恢复成功 ≠ 所有页已在宿主 RAM；首条命令慢、内存指标不高，是正常的按需加载", 5.6, PURPLE, bold=True)

def d_net(ax):
    txt(ax, 6.0, 48.0, "出站", 6.2, ORANGE, bold=True)
    hchain(ax, 6.0, 36.0, 121.0, [("eth0", "virtio"), ("tap0", "沙箱 netns"), ("SNAT", "改源"),
                                  ("veth", "主 netns"), ("MASQ", "出口地址")], ORANGE, 8.6, 2.4)
    txt(ax, 6.0, 30.0, "入站", 6.2, BLUE, bold=True)
    hchain(ax, 6.0, 18.0, 121.0, [("server", "slot 地址"), ("veth", "进 netns"), ("DNAT", "改目的"),
                                  ("tap0 → FC", "VirtIO RX"), ("envd", "处理")], BLUE, 8.6, 2.4)

def d_nat(ax):
    box(ax, 6.0, 40.0, 56.0, 10.0, "tap", AMBER, 7.4, True, sub="用户态进程 — 内核网络栈（二层帧）")
    box(ax, 68.0, 40.0, 59.0, 10.0, "veth", AMBER, 7.4, True, sub="内核栈 — 内核栈（两个 netns）")
    hchain(ax, 6.0, 26.0, 121.0, [("DNAT", "改目的（入口）"), ("SNAT", "改源（出口）"),
                                  ("MASQUERADE", "取出口地址"), ("REDIRECT", "改到本机")], BLUE, 8.6, 2.6)
    txt(ax, 6.0, 18.0, "DNAT 靠 conntrack 记住原值、回包再改回来——状态丢了旧连接就断", 5.6, GRAY)

def d_doors(ax):
    quad(ax, 6.0, 50.0, 121.0, 18.0, [("A. Guest 内作恶", "Guest 自己的内核挡", BLUE),
                                      ("B. VMM 被攻破", "seccomp / 降权 / chroot / caps", ORANGE),
                                      ("C. 资源超用", "cgroup 限值 / vCPU / balloon", GREEN),
                                      ("D. 网络外连", "netns / iptables / 代理", PURPLE)])
    hchain(ax, 6.0, 20.0, 121.0, [("seccomp", "vmm 60 / api 35 / vcpu 43 条"), ("默认动作", "trap → SIGSYS"),
                                  ("作用对象", "线程，不是进程"), ("拦不到", "Guest 内部 syscall")], ORANGE, 9.0, 3.0)

def d_metrics(ax):
    hchain(ax, 6.0, 40.0, 121.0, [("拉镜像", ""), ("建盘", ""), ("起 VMM", ""), ("等 envd", ""), ("首命令", "")], TEAL, 9.0, 2.6)
    base, x0 = 18.0, 8.0
    bars = [("p50", 4.0), ("p90", 7.0), ("p99", 11.0), ("max", 15.0)]
    for i, (t, h) in enumerate(bars):
        c = TEAL if t != "max" else ORANGE
        ax.add_patch(plt.Rectangle((x0 + i*8.0, base), 5.0, h, facecolor=c, alpha=0.18, edgecolor=c, lw=0.9, zorder=3))
        txt(ax, x0 + i*8.0 + 2.5, base - 3.4, t, 5.4, c, ha="center", bold=True)
    txt(ax, 44.0, 30.0, "冷启动要分段计时：每段都给 wall 与 CPU\n均值相同、分布不同的两个系统，体验完全不同", 5.4, GRAY)
    txt(ax, 44.0, 20.0, "「资源就绪」与「首命令完成」是两个指标\n同一操作按路径分类统计，否则 p99 无法解释", 5.4, GRAY)

def d_chains(ax):
    quad(ax, 6.0, 50.0, 121.0, 18.0, [("创建", "spawn → 配置 → 启动 → 就绪", TEAL),
                                      ("执行", "envd → 进程 → 事件流", TEAL),
                                      ("读文件", "VFS → virtio → ublk → 层", TEAL),
                                      ("暂停 / 恢复 / 销毁", "确认 → 装载 → 回收", TEAL)])
    txt(ax, 6.0, 18.0, "共同主线：一个请求怎么落到硬件，再带着结果回到调用者", 5.8, TEAL, bold=True)

def d_interview(ax):
    hchain(ax, 6.0, 40.0, 121.0, [("结论", "一句话判断"), ("机制", "谁在哪层做什么"),
                                  ("边界", "挡不住什么"), ("证据", "数字 / 实测 / 故障")], INK, 10.0, 3.0)
    box(ax, 6.0, 16.0, 121.0, 20.0, "", GRAY, 5.6, fill=PALE)
    txt(ax, 10.0, 31.0, "示范（怎么隔离）：结论＝两类威胁；机制＝虚拟化 + seccomp/namespace/cgroup；", 5.4, INK)
    txt(ax, 10.0, 26.0, "边界＝namespace 不改权限、seccomp 看不到 Guest syscall；", 5.4, INK)
    txt(ax, 10.0, 21.0, "证据＝一份真实实现里 VMM 用 unshare -m 启动、没有 jailer、cgroup 只记账", 5.4, INK)

# ---------------- 组装 ----------------
def main(out, imgdir):
    global IMGDIR
    IMGDIR = imgdir
    os.makedirs(imgdir, exist_ok=True)
    pages = [
        ("全景", "一台机器，三个执行环境", BLUE, d_layers,
         [("①", "三层共用一个宿主内核，只有 Guest 有自己的内核"),
          ("②", "server / firecracker / ublk-daemon 是三个独立宿主进程"),
          ("③", "Guest 里的程序不是 firecracker 的子进程，宿主 ps 看不到")],
         "易错：把 server 里的 FirecrackerInstance 对象当成进程",
         "会被问：宿主 ps 能看到哪些？"),
        ("全景", "一个变量，四个地址", BLUE, d_addr,
         [("①", "GVA/GPA 属于 Guest；HVA 属于某个宿主进程；HPA 只有一个"),
          ("②", "Guest 访存 GVA→GPA→HPA；Firecracker 访存 HVA→HPA"),
          ("③", "memslot 只登记 GPA—HVA，不复制 RAM，也不要求填 HPA")],
         "易错：以为 Guest 正常访存会经过 HVA",
         "会被问：为什么 ioctl 里没有 HPA 参数？"),
        ("全景", "三个动作，常常被混成一个", PURPLE, d_bound,
         [("①", "KVM_RUN 是系统调用；VM-Exit 是执行环境切换；两者都不切线程"),
          ("②", "只有调度器换线程，才是真的「没拿到 CPU」"),
          ("③", "所以 VM-Exit 次数 ≠ VMM 被唤醒次数")],
         "易错：把 VM-Exit 当成 KVM_RUN 返回用户态",
         "会被问：一次 EPT 缺页会让 FC 从 ioctl 返回吗？"),
        ("第 1 课", "一个进程，多个线程", BLUE, d_threads,
         [("①", "1 个 vCPU = 1 个宿主线程；线程名是代码 .name() 写死的"),
          ("②", "多线程不是为了性能，是为了「Guest 卡住时宿主还能下指令」"),
          ("③", "线程在 KVM_RUN 里不等于睡着，CPU 可能正在跑 Guest")],
         "易错：以为 vCPU 线程在 KVM_RUN 里就是睡着了",
         "会被问：配 4 个 vCPU，宿主多几个线程？"),
        ("第 2 课", "同一个数字，两块内存", BLUE, d_spaces,
         [("①", "地址离开地址空间没有意义：两套页表翻出不同物理页"),
          ("②", "pwrite 没有远程参数；PVM 才用 pid 指定目标地址空间"),
          ("③", "两个 iovec 数组都在调用者内存里，只有元素里的地址指向目标")],
         "易错：以为内核会自动按被读进程解释地址",
         "会被问：remote_iov 里填 GVA、GPA 还是 HVA？"),
        ("第 3 课", "两条路径，一块物理内存", BLUE, d_paths,
         [("①", "登记范围不等于复制内存；128 MiB 始终只有一份"),
          ("②", "EPT 按需建立：缺项时才取页、建项"),
          ("③", "偏移公式：HVA = userspace_addr + (GPA − guest_phys_addr)")],
         "易错：以为 memslot 就是 EPT 表本身",
         "会被问：memslot 在哪、EPT 在哪？"),
        ("第 4 课", "本质是一个 ioctl 的循环", PURPLE, d_kvm,
         [("①", "退出由硬件完成：存现场、写 exit reason、载入宿主状态"),
          ("②", "KVM 能处理的直接重入；办不了的才回用户态"),
          ("③", "退出原因不止设备：外部中断、EPT 缺页、I/O 指令都会退出")],
         "易错：把退出次数当成 VMM 开销",
         "会被问：哪些退出必须回用户态？"),
        ("第 5 课", "「没被调度」不是「已暂停」", PURPLE, d_pause,
         [("①", "三个完成点：请求发出 / FC 接收 / 全部 vCPU 确认"),
          ("②", "只停一个 vCPU 不算暂停，另一个还在写同一块 RAM"),
          ("③", "暂停完成还要：捕获内存、写层、fsync、改 manifest")],
         "易错：把「请求发出」当「VM 已停」",
         "会被问：只暂停一个 vCPU 能叫暂停吗？"),
        ("第 6 课", "队列在内存里，通知只提醒", PURPLE, d_virtio,
         [("①", "描述符 16 字节，只描述缓冲区，不复制字节"),
          ("②", "avail 由 Guest 写、used 由设备写，都在 Guest RAM"),
          ("③", "doorbell 只提醒「去检查队列」，一次通知可对应多项工作")],
         "易错：把设备发布 used 当成 Guest 已处理",
         "会被问：通知里到底传了什么？"),
        ("第 7 课", "控制面与数据面，两条通道", GREEN, d_channels,
         [("①", "控制面走宿主 Unix socket，HTTP 只是格式，不走 TCP"),
          ("②", "数据面走 virtqueue，需要 Guest 驱动配合"),
          ("③", "暂停不能走数据面：它要能在 Guest 不配合时生效")],
         "易错：把 socket 当网络；把超时当失败",
         "会被问：超时有哪三种可能？"),
        ("第 8 课", "三层就绪，一层比一层强", GREEN, d_tiers,
         [("①", "进程存在只证明配置就绪；端口能连只证明监听在工作"),
          ("②", "health 通过才证明应用能应答（非 4xx/5xx，单次 1 秒）"),
          ("③", "start_nowait 与 wait_for_ready 是两个不同的等待")],
         "易错：把 health 通过当成鉴权通过",
         "会被问：端口能连、命令不能执行，卡在哪层？"),
        ("第 9 课", "exec 返回的是流，不是结果", GREEN, d_stream,
         [("①", "Start 只说明进程被创建；Data 是输出；End 带退出码"),
          ("②", "两个独立判断：事件是否收齐、exit_code 是多少"),
          ("③", "成功要三样同时满足，缺一个都不能说成功")],
         "易错：看到 Start 就当成功",
         "会被问：超时后终止失败，能断言进程退出吗？"),
        ("第 10 课", "一条数据，三个坐标系", ORANGE, d_offsets,
         [("①", "文件偏移 / LBA / 后端位置，三者不能混"),
          ("②", "LBA 必须带块或扇区大小，否则差 8 倍"),
          ("③", "写路径四个节点，只有 fsync 才算持久化")],
         "易错：以为文件偏移 0 就是磁盘偏移 0",
         "会被问：一次 4 KiB 读可能读多少字节？"),
        ("第 11 课", "分层是覆盖映射", ORANGE, d_overlay,
         [("①", "从新到旧查，第一个有记录的就赢"),
          ("②", "「无记录」不是零，要继续回落"),
          ("③", "「显式零」必须终止，否则暴露父层旧数据")],
         "易错：以为「没记录」读出来是零",
         "会被问：父层有旧值、新状态应为零，能省略吗？"),
        ("第 12 课", "内核给壳，用户态给内容", ORANGE, d_ublk,
         [("①", "三个节点：control 管创建、ublkcN 管交接、ublkbN 管数据"),
          ("②", "创建要等节点「真正可打开」，不只是文件存在"),
          ("③", "daemon 是集中式的：不是每沙箱一个进程")],
         "易错：把 FETCH 的完成当数据读完",
         "会被问：daemon 挂了，这个节点会怎样？"),
        ("第 13 课", "映射了 ≠ 分配了 ≠ 复制了", PURPLE, d_mmap,
         [("①", "mmap 只建 VMA，不占物理内存"),
          ("②", "首次访问缺页，首次写才 COW 复制"),
          ("③", "三层缺页：Guest 页表 / EPT / 宿主页表")],
         "易错：以为 mmap 就占满物理内存",
         "会被问：恢复后首次读与首次写分别发生什么？"),
        ("第 14 课", "快照是四件套", PURPLE, d_snapshot,
         [("①", "VM 状态 + 内存镜像 + 磁盘视图 + 恢复配置，缺一不可"),
          ("②", "四个完成点：暂停 / 捕获 / 持久化 / 释放"),
          ("③", "暂停只冻 Guest CPU 写入，设备侧仍可能写 RAM")],
         "易错：pause 成功就当快照成功",
         "会被问：哪一步失败会造成「有文件但恢复不了」？"),
        ("第 18 课", "恢复不是把内存读回来", PURPLE, d_resume,
         [("①", "先 resume_vm=false 装好一切，最后才让 vCPU 跑"),
          ("②", "内存按需缺页取，不是一次性全读"),
          ("③", "共享只读设备 + MAP_PRIVATE：读共享、写才 COW")],
         "易错：以为恢复会把全部内存读回宿主",
         "会被问：首条命令慢，是故障还是正常？"),
        ("第 19 课", "出站与入站，两条相反的路", AMBER, d_net,
         [("①", "出站：SNAT 改源，再 MASQUERADE 适配出口"),
          ("②", "入站：DNAT 改目的，包才进得了 Guest"),
          ("③", "TX 的 used 只表示缓冲可回收，不代表对端收到")],
         "易错：以为同名 tap0 会冲突",
         "会被问：恢复后旧 TCP 连接为什么可能不通？"),
        ("第 19 课 · 细节", "tap 与 veth，DNAT 与 SNAT", AMBER, d_nat,
         [("①", "tap 连「进程 — 内核」，veth 连「内核 — 内核」"),
          ("②", "DNAT 改目的（入口），SNAT 改源（出口）"),
          ("③", "REDIRECT 是 DNAT 特例：把流量导给本机代理")],
         "易错：把 DNAT 当成转发",
         "会被问：REDIRECT 与 DNAT 差在哪？"),
        ("第 20 课", "四类威胁，四道门", AMBER, d_doors,
         [("①", "先定威胁（谁、越没越过门），再选控制点"),
          ("②", "namespace 改视野、cgroup 改用量、seccomp 改能力"),
          ("③", "seccomp 是线程级白名单，拦不到 Guest 内部 syscall")],
         "易错：把 namespace 当成降权",
         "会被问：Guest 里的 root 会被 seccomp 拦吗？"),
        ("第 24 课", "度量口径：先分类，再谈平均", TEAL, d_metrics,
         [("①", "wall / CPU / 分位数，三个口径缺一不可"),
          ("②", "冷启动按阶段分段，别只报一个总时间"),
          ("③", "抖动来自路径不同与超订，不是「设备慢」")],
         "易错：只报平均值",
         "会被问：wall 高而 CPU 低，说明什么？"),
        ("第 27 课", "六条链，一条主线", TEAL, d_chains,
         [("①", "创建 / 执行 / 读文件 / 暂停 / 恢复 / 销毁"),
          ("②", "每条链的完成点都不一样，排障先定位卡在哪一段"),
          ("③", "最容易混：暂停完成 vs 快照完成")],
         "易错：把「某层完成」当「整件事完成」",
         "会被问：读一个文件，中间有几次「完成」？"),
        ("面试", "四段式：缺第 4 段就是只背过", INK, d_interview,
         [("①", "结论先给判断，别铺垫"),
          ("②", "机制两句：谁在哪层做什么"),
          ("③", "边界与证据：挡不住什么 + 一个数字或一次实测")],
         "易错：只报均值不报分位；只讲名词不讲边界",
         "会被问：90 秒讲完「VM-Exit」，能吗？"),
    ]
    for i, (k, t, c, fn, callouts, p1, p2) in enumerate(pages, 1):
        page(i, k, t, c, fn, callouts, p1, p2)

    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    for path in PAGES:
        s = prs.slides.add_slide(prs.slide_layouts[6])
        s.shapes.add_picture(path, 0, 0, width=Inches(13.333), height=Inches(7.5))
    prs.save(out)
    print("saved:", out, "slides:", len(PAGES))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "img_deck.pptx"
    imgdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(out), "图片")
    main(out, imgdir)
