#requires -Version 5.1
<#
  AgentENV 复习课件 v3（27 页）—— 8 套版式轮换，每页约 800—1000 字
  版式：封面 / 图文 / 流程 / 表格 / 公式 / 例题 / 易错 / 卡片 / 练习 / 总结 / 附录
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'build_deck_v2_part1.ps1')

$OUT2 = Join-Path (Split-Path -Parent $PSScriptRoot) '04-AgentENV\图片-27页-v3'
New-Item -ItemType Directory -Force -Path $OUT2 | Out-Null

$pages = @()

# ===== P01 封面 =====
$pages += {
  param($g)
  CoverPage $g @(
    @{t = 'AgentENV 沙箱：'; c = $C.ink; bold = $false },
    @{t = '三个执行环境、六条链路、一个完成点判断'; c = $C.green; bold = $true }) `
    '28 讲压缩成 27 页；每页一张模拟图、一张数据图、四条机制，末尾带易错与自测' `
    @('能画出三个执行环境的位置图，说明谁有 PID、谁只是内核功能',
      '能说出读文件链的四个完成点，并解释为什么它们不能互相代替',
      '能用四段式（结论 → 机制 → 边界 → 证据）讲清任意一个机制') `
    @('三个执行环境', '六条链路', '完成点思维') `
    @(@('01 总览', '知道要学什么、按什么顺序学'), @('02 概念', '把每个机制的"完成"说清'), @('03 例题', '答得对追问，而不是背结论'), @('04 总结', '考前能自测、能对齐口径')) 1
}

# ===== P02 知识地图（图文）=====
$pages += {
  param($g)
  SplitPage $g '01 总览' @(
    @{t = '先建立结构，'; c = $C.ink; bold = $false },
    @{t = '再记细节'; c = $C.green; bold = $true }) `
    '六个模块有硬依赖：跳过位置与地址，后面只会变成名词记忆' 1 `
    @(
      @('依赖分三层，不是并列', '地基是位置（谁在哪层）与地址（GVA/GPA/HVA/HPA）；中间是执行（KVM_RUN 与 VM-Exit 的语义）与存储（virtio → ublk → 层）；上层是状态（快照/恢复）与平台（资源/并发/度量）。前一层没吃透，后一层只能背。'),
      @('一个具体的依赖例子', 'process_vm_readv(pid, local_iov, liovcnt, remote_iov, riovcnt, flags) 四个要点：pid 选地址空间、local 是调用者缓冲、remote 里放 Firecracker 的 HVA、count 是元素个数不是字节数；flags 必须 0。不懂四条地址线，这四个参数只能死记。'),
      @('三个易混区及成因', '状态区：暂停、快照、恢复有"停顿"这个共同表象；平台区：资源拥有（谁创建）与引用消失（谁还在用）是两回事；存储区：逻辑偏移、层内偏移、后端位置是三个坐标系。'),
      @('本讲回答的五个问题', '① Guest 里的进程在谁那边、宿主 ps 能看到吗 ② 一次 4 KiB 读到哪一步算完成 ③ 暂停能否说明快照成功 ④ namespace/cgroup/seccomp 各挡什么 ⑤ 恢复后旧 TCP 为何可能不通。前三个是高频。')
    ) `
    '跳过地址直接看快照，会把「按需缺页」「COW」「持久化」当成同一件事。' `
    '「恢复后首条命令慢」必须先懂哪个机制，为什么？' `
    '先建结构（谁在哪层），再记细节（那层的完成点）。' `
    { param($g, $x, $y, $w, $h) fig_map $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('位置', 0, '0'), @('地址', 0, '0'), @('执行', 2, '2'), @('存储', 2, '2'), @('状态', 3, '3'), @('平台', 5, '5')) 6 $C.green } `
    2
}

# ===== P03 三个执行环境（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '一台机器三个执行环境，'; c = $C.ink; bold = $false },
    @{t = '只有 Guest 有自己的内核'; c = $C.green; bold = $true }) `
    '进程、线程、内核功能三种对象混在一起，是所有位置题答错的总根源' 2 `
    @(
      @('Firecracker 是宿主进程（有代码证据）', 'instance.rs 里 Command::new 只准备参数；spawn_tokio_command_scoped 返回 child 才真正启动；随后 self.process = Some(child) 保存句柄，child.id() 拿到的是宿主 PID。三步要分开：准备 → 启动 → 保存，Command::new 前后系统里什么都没多。'),
      @('内核功能没有 PID', 'KVM 是 /dev/kvm 上的 ioctl 集合；ublk 驱动提供 /dev/ublkbN 请求队列；cgroup/seccomp 是内核子系统。它们不会出现在 ps 里，把它们画成"进程"，"谁在执行 Guest 指令"这个问题就永远讲不清。'),
      @('Guest 由 Guest 内核调度', 'Guest 里的程序是 Guest RAM 里的一段字节，靠 Guest 页表 + EPT 翻译访问；宿主 ps 只看到 firecracker 的若干线程。推论：宿主 PID 与 Guest PID 是两套编号空间，不能互相代入。'),
      @('两条跨层通道，载体完全不同', '控制面走宿主 Unix socket（--api-sock，REST：PATCH /vm、PUT /snapshot/load），不需要 Guest 配合；应用面走 TCP（经 tap0 + DNAT 到 envd，HTTP /health 与 gRPC 同址、带 token），需要 Guest 内核调度。')
    ) `
    '把 FirecrackerInstance 当进程；把宿主 PID 当 Guest PID；把 KVM 画成进程。' `
    '宿主 ps -eLf 能列出哪几个？列不出来的对象凭什么说它们「在」？' `
    '先问：这个对象有没有自己的 PID、由谁的内核调度。' `
    { param($g, $x, $y, $w, $h) fig_layers3 $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('对象', '宿主可见', '有 PID') @(@('server / firecracker / ublk-daemon', '是', '是'), @('KVM / ublk 驱动 / cgroup', '否', '否'), @('Guest 内核 / envd / 你的程序', '否', '是（Guest 内）')) 30 } `
    3
}

# ===== P04 四把尺子（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '一个变量四个地址：'; c = $C.ink; bold = $false },
    @{t = 'HVA 只属于某一条访问路径'; c = $C.green; bold = $true }) `
    '同一块物理页有两条访问路径，HVA 只属于其中一条' 2 `
    @(
      @('两条翻译链，各用各的表', 'Guest 访存：GVA →（Guest 页表）→ GPA →（EPT）→ HPA。Firecracker 访存：HVA →（宿主页表）→ HPA。两条链落在同一物理页，所以不存在"两份内存要同步"，存在的是"两份页表指向同一页"。'),
      @('登记接口的字段解释了为什么没有 HPA', 'KVM_SET_USER_MEMORY_REGION{slot, flags, guest_phys_addr, memory_size, userspace_addr}。用户态拿不到物理地址，只能交 HVA 起点；是宿主内核查宿主页表把 HVA 翻成 HPA 再填 EPT——所以参数里没有 HPA 不是省略，而是不可能。'),
      @('偏移公式与代入', 'HVA = userspace_addr + (目标 GPA − guest_phys_addr)。例：0x70000000 + 0x2000 = 0x70002000，该值直接作为 PVM 的 remote 地址。remote_iov 里放的是 Firecracker 的 HVA，不是 GVA，也不是 GPA。'),
      @('memslot 的两个硬约束', '数量上限来自 KVM_CAP_NR_MEMSLOTS（Firecracker 用 max_nr_memslots() 校验，超了报 NotEnoughMemorySlots）；每条 memslot 可带 dirty log，快照的"哪些页要存"就按这个位图拿。')
    ) `
    '以为 Guest 正常访存会经过 HVA；以为 memslot 就是 EPT 表；以为登记时复制了一份 RAM。' `
    'guest_phys_addr=0、userspace_addr=0x70000000，访问 GPA 0x2000 时 remote 填什么？' `
    '地址是名字，进程是语境。' `
    { param($g, $x, $y, $w, $h) fig_dualpath $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('Guest 访存', 2, '2 次'), @('FC 访存', 1, '1 次')) 2 $C.orange } `
    4
}

# ===== P05 三个切换（表格）=====
$pages += {
  param($g)
  TablePage $g '02 概念' @(
    @{t = '三个「切换」不是一回事：'; c = $C.ink; bold = $false },
    @{t = '只有线程切换才是真没拿到 CPU'; c = $C.green; bold = $true }) `
    '把三种边界混成一个，就没法把「慢」拆开' 2 `
    @('边界', '发生了什么', '是否切宿主线程', '典型误判') `
    @(
      @('KVM_RUN 系统调用', '用户态 → 内核，换特权级，线程不变；返回时带 kvm_run->exit_reason', '否', '以为"调了 ioctl 就进 Guest 了"'),
      @('VM-Entry / VM-Exit', '硬件把 Guest 寄存器写进 VMCS guest-state，写退出原因与 qualification，再载入宿主状态', '否', '以为每次都回到用户态'),
      @('宿主线程切换', '调度器把 CPU 给另一个线程；此时 KVM_RUN 可能还没返回', '是', '把调度延迟算成虚拟化开销')
    ) `
    @(300, 620, 240, 328) `
    @(
      @('一个容易漏的命名层次', '硬件层的退出原因叫 EXIT_REASON_EPT_VIOLATION，KVM 对用户态暴露的叫 KVM_EXIT_MMIO——同一个事件在两层的名字不同，混用会答错"谁处理的"。'),
      @('KVM 处理完直接重入', '普通 RAM 的 EPT 缺项：KVM 按 memslot 取页、建项、重入 Guest，ioctl 从头到尾没返回用户态；只有 MMIO/PIO 这类它办不了的才回用户态。'),
      @('三个指标分开报', '退出次数（硬件，看 exit_mmio_* 计数）、被唤醒次数（用户态）、上下文切换（调度器）。互为因果但不可相加。')
    ) `
    '把 VM-Exit 当 KVM_RUN 返回；把补 EPT 映射的开销算到设备模型头上。' `
    '一次 EPT 缺页退出会让 FC 从 ioctl 返回吗？判据是什么？' `
    '看到「慢」先分三类：退出 / 调度 / IO。' `
    5
}

# ===== P06 vCPU 与线程（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '一个 vCPU 就是一个线程：'; c = $C.ink; bold = $false },
    @{t = '多线程是为了能接住控制请求'; c = $C.green; bold = $true }) `
    '不是为了性能：单线程时 Guest 卡在 KVM_RUN 里，宿主连暂停都下不了' 2 `
    @(
      @('线程创建的真实路径', 'lib.rs:397 对每个 vCPU 调 start_threaded(vcpu_seccomp_filter.clone(), barrier.clone())；vcpu.rs:246 用 thread::Builder::new().name(format!("fc_vcpu {index}")).spawn(...) 起线程。'),
      @('Barrier 的 +1 是主线程', 'lib.rs:372 Barrier::new(vcpu_count + 1)，lib.rs:401 主线程也 wait()。语义：所有 vCPU 线程完成 TLS 初始化后，主线程才继续去发启动；去掉它，Guest 可能在某个 vCPU 未就绪时被唤醒。'),
      @('线程名写死才好排障', '.name() 决定 ps -eLf 看到的名字；内核 comm 字段上限 16 字节（含结尾 0），所以最长 15 字符。不写 name() 就只有默认名，排障时根本分不清哪个是 vCPU 线程。'),
      @('"在 KVM_RUN 里"≠"线程空闲"', 'CPU 可能正在该线程上下文中执行 Guest 指令，所以 CPU 占用率包含"跑 Guest"的时间；只有 Guest 执行 HLT、等中断这类情况，线程才真正阻塞。')
    ) `
    '以为 vCPU 线程闲置；以为线程名会自动继承；用 CPU 占用率判断 VMM 忙不忙。' `
    '配 2 个 vCPU，宿主至少几个线程？Barrier 为什么是 vcpu_count+1？' `
    '线程数 = 1（vmm）+ 1（api）+ N（vcpu）。' `
    { param($g, $x, $y, $w, $h) fig_threads $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('1 vCPU', 3, '3'), @('2 vCPU', 4, '4'), @('4 vCPU', 6, '6'), @('8 vCPU', 10, '10')) 10 $C.green } `
    6
}

# ===== P07 控制面与数据面（表格）=====
$pages += {
  param($g)
  TablePage $g '02 概念' @(
    @{t = '控制面走 socket，数据面走队列：'; c = $C.ink; bold = $false },
    @{t = 'HTTP 只是消息格式'; c = $C.green; bold = $true }) `
    '两条通道的故障表现完全不同，混了就没法排障' 2 `
    @('维度', '控制面', '数据面', '后果差异') `
    @(
      @('载体', '宿主 Unix socket（--api-sock）', 'Guest RAM 里的 virtqueue', 'socket 坏：宿主失控；队列坏：Guest 内 IO 停'),
      @('消息', 'Firecracker REST：PATCH /vm、PUT /snapshot/load、GET dirty-ranges', '描述符 + avail + used + 门铃', 'REST 不带数据；队列带的是缓冲描述'),
      @('依赖 Guest', '不需要，Guest 卡死也能停', '需要 Guest 驱动参与', '这是"Guest 卡住还能暂停"的原因'),
      @('超时含义', '没送到 / 响应丢了 / 还在做', '不适用（无请求-响应语义）', '超时不能推出"VM 还在跑"')
    ) `
    @(240, 620, 400, 428) `
    @(
      @('为什么暂停不能走数据面', '暂停的用途之一正是"Guest 不配合时也能停住它"。若停机依赖 Guest 处理队列，就变成"要停下它得先让它运行"的循环论证。'),
      @('排障先问哪一面坏了', '控制面坏：不能暂停/快照/销毁，但 Guest 照跑；数据面坏：Guest 内部 IO 卡住，但宿主仍能控制与捕获。这一句能省一半排障时间。'),
      @('超时后重试要幂等', '三种可能里"做成了但响应丢了"意味着重放会重复执行；所以终止/恢复这类操作要有幂等键或状态查询。')
    ) `
    '把 socket 当网络；把超时当失败；以为 HTTP 就要走 TCP。' `
    '超时后补发一次 resume 有什么风险？举一个坏结果。' `
    'socket 是宿主之间，virtqueue 是 Guest 参与。' `
    7
}

# ===== P08 VirtIO（流程）=====
$pages += {
  param($g)
  FlowPage $g '02 概念' @(
    @{t = '队列在内存里，通知只提醒：'; c = $C.ink; bold = $false },
    @{t = '描述符不搬字节'; c = $C.green; bold = $true }) `
    '设备不是「收到包」，而是「去共享队列取一条描述」' 2 `
    @(
      @('准备缓冲', 'Guest 在 RAM 里准备接收缓冲，写描述符：addr(GPA 8B) + len(4B) + flags(NEXT/WRITE 2B) + next(2B)，共 16 字节，可串成链描述多块不连续内存。', '完成点：描述符可被设备读取'),
      @('发布 avail', '把链头编号写入 avail 环（Guest 侧），必要时敲门铃。门铃只表示"去检查队列"，不带数据，可被抑制；一次通知可对应多项工作。', '完成点：设备可看到新链头'),
      @('设备写数据并发布 used', '设备按描述符把数据写进条 Guest RAM（GPA→HVA 换算并校验范围），再把完成项与实际长度写入 used 环。', '完成点：设备侧交差，Guest 尚未处理'),
      @('Guest 处理并复用', 'Guest 驱动处理 used 里的数据，之后才能把同一链头再次发布；未处理完就复用，设备可能覆盖仍需读的内容。', '完成点：应用拿到字节')
    ) `
    @(
      @('通知的边界', '通知次数 ≠ 请求数：avail 里有链头 3、7、9 时只敲一次门铃。把通知当"每包一次"会错估 VM-Exit 次数，也会错估性能。'),
      @('「设备完成」与「Guest 完成」', '设备发布 used 只表示设备侧写完；Guest 驱动还要被中断唤醒、处理队列、把数据交给上层。这两步之间可能隔着一次调度。'),
      @('为什么快', '模拟真实设备时每个寄存器访问都是一次 VM-Exit；VirtIO 把数据批量放共享内存，只在有活时敲一次门铃，把 N 次退出压成 1 次。')
    ) `
    '把「设备发布 used」当成「Guest 已处理」；把通知次数当请求数。' `
    'Guest 未处理完就把缓冲再次发布，会发生什么？为什么难复现？' `
    '队列在内存、通知只提醒、数据在 buffer。' `
    { param($g, $x, $y, $w, $h) data_stack $g $x $y $w $h } `
    8
}

# ===== P09 三层就绪（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '三层就绪，一层比一层强：'; c = $C.ink; bold = $false },
    @{t = '最后一层才代表能干活'; c = $C.green; bold = $true }) `
    '「进程在」「端口通」「服务能应答」是三件强度不同的事' 2 `
    @(
      @('第一层：API socket 可用', '能配 VM、能 pause，证明 VMM 起来了、--api-sock 路径对；start_nowait() 的注释写明"只等 API socket 可用"。此时 VM 可能还没配置、更没启动。'),
      @('第二层：网络可达', '宿主经 tap0 能到 Guest，证明 netns、网卡、IP、端口都对。这一层的失败最常被误诊成"服务没起来"，因为现象都是"连不上"。'),
      @('第三层：/health 通过', 'GET {base}/health，判定是状态码非 4xx/5xx（不校验 body，204 也算过）；单次上限 1 秒（HEALTH_PROBE_TIMEOUT），失败继续重试，整体期限耗尽才报超时。'),
      @('health 不带 token', 'envd 客户端把 base_path 与 grpc_address 设为同一地址，access_token 单独保存并用于受保护请求；health 请求未带 token——所以"健康通过"不等于"鉴权通过"。')
    ) `
    '把 health 通过当完整可用；把"对象创建成功"当"服务就绪"。' `
    '端口能连、命令返回 UNAUTHENTICATED，问题在哪层？health 为什么排除不了？' `
    '就绪答三层，比"服务起来了"多拿一分。' `
    { param($g, $x, $y, $w, $h) fig_ladder $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('期限 5s', 10, '10 次'), @('期限 10s', 20, '20 次')) 20 $C.orange } `
    9
}

# ===== P10 exec 事件流（流程）=====
$pages += {
  param($g)
  FlowPage $g '02 概念' @(
    @{t = 'exec 返回的是流：'; c = $C.ink; bold = $false },
    @{t = 'Start 说明不了成功'; c = $C.green; bold = $true }) `
    '两个独立判断：事件是否收齐、退出码是多少' 2 `
    @(
      @('发起请求', 'start_process_inner(cmd, args, envs, cwd) 打包成 StartRequest，经 envd 的 gRPC ProcessClient.start 发送；命令与参数分开传，不假设经 shell 解析。', '完成点：envd 收到请求'),
      @('Start{pid}', '进程已在 Guest 内被创建，pid 是 Guest 内的编号。它只证明"创建出来了"，之后仍可能立刻失败、崩溃、或被执行策略杀掉。', '完成点：进程存在'),
      @('Data 分段', 'stdout/stderr 各自分段到达，可能 0 条也可能很多条；两个通道都可能写。看到 Data 既不证明成功也不证明失败。', '完成点：有输出'),
      @('End{code}', '进程退出并带回退出码；wait 消费到 End 后归一成 ProcessOutput。若流结束却没收到 End，属协议层错误。', '完成点：进程已退出')
    ) `
    @(
      @('成功三件套', 'wait 返回 Ok + 收到 End + exit_code 符合预期。只看到 Start 就宣布成功，是最常见的错答；只看到 exit_code=0 而不检查流是否收齐，同样会漏掉协议层失败。'),
      @('没有 shell 的后果', '命令与参数分开传：没有管道、通配符、重定向语义；要用这些必须显式 sh -c。把 shell 特性当默认行为，会写出一堆"本地能跑、沙箱里失败"的脚本。'),
      @('超时与幂等', '超时后发终止请求可能失败，所以不能断言进程已退出；结果未知时重试可能重复执行，业务侧要幂等或先查询状态。')
    ) `
    '看到 Start 就当成功；只看 exit_code 不看流是否收齐；把超时当已退出。' `
    '可执行文件起不来时一定会先收到 Start 吗？这如何影响判错逻辑？' `
    'Start 之后追两件事：End 到了吗、退出码是多少。' `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('事件', '携带', '只说明', '不能推出') @(@('Start', 'Guest PID', '进程被创建', '命令会成功'), @('Data', 'stdout/stderr', '有输出', '成功或失败'), @('End', 'exit_code', '进程已退出', '业务正确')) 26 } `
    10
}

# ===== P11 六层读路径（流程）=====
$pages += {
  param($g)
  FlowPage $g '02 概念' @(
    @{t = '一次 4 KiB 读跨六层：'; c = $C.ink; bold = $false },
    @{t = '每层「完成」含义都不同'; c = $C.green; bold = $true }) `
    '排障就是把「卡在哪一层、哪个完成点」定位出来' 2 `
    @(
      @('Guest 侧：read → LBA', 'read() 查页缓存未命中 → ext4 用 extent 把文件偏移换成逻辑块 LBA（文件偏移 ≠ 磁盘偏移）。页缓存命中时这批数据可能完全不产生设备 IO。', '完成点：算出 LBA'),
      @('virtio → Firecracker', '驱动构造描述符链、发布 avail、敲门铃（MMIO 写触发 EPT 缺页 → VM-Exit）；FC 的后端从 Guest RAM 取描述符，把请求打到 /dev/ublkbN。', '完成点：请求进入宿主块层'),
      @('ublk → daemon', 'ublk 组织请求（queue id + tag）入队；daemon 的 FETCH 命令 CQE 到达——只表示请求送到 daemon，不表示数据读完。', '完成点：请求交付 daemon'),
      @('取字节并返回', 'daemon 查 OverlayBD 定层取字节、提交 COMMIT；内核完成原块请求 → FC 填 Guest 页并发布 used → Guest 驱动处理 → read() 返回 4096。', '完成点：应用拿到字节')
    ) `
    @(
      @('四个完成点不能互相代入', '① FETCH 的 CQE 到（交付）② daemon 提交 COMMIT（它交差）③ 发布 used（设备交差）④ read() 返回（应用拿到）。把 ① 当成 ④ 是最常见的错。'),
      @('三个偏移与 8 倍单位差', '文件偏移（字节）、LBA（块号）、后端位置（层内偏移/远端）。同一 8 MiB：按 512 B 扇区编号 16384，按 4 KiB 块编号 2048——报 LBA 不带单位等于没报。'),
      @('缓存改变的不只是速度', '页缓存命中可免设备 IO，但路径解析、元数据、并发预读仍可能产生 IO；所以"缓存命中"不能推出"整次零设备请求"。')
    ) `
    '把 FETCH 的 CQE 当数据读完；把缓存命中当零 IO。' `
    'FETCH CQE 到了但后端读失败，哪些层还能报成功？read() 返回什么？' `
    '问「完成了吗」必须先说清是哪一层。' `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('512 B 扇区', 16384, '16384'), @('4 KiB 块', 2048, '2048')) 16384 $C.orange } `
    11
}

# ===== P12 分层覆盖（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '分层是覆盖映射，'; c = $C.ink; bold = $false },
    @{t = '不是拼字节'; c = $C.green; bold = $true }) `
    '无记录要回落，显式零要终止：两种都为 0，语义完全不同' 2 `
    @(
      @('读取规则', '每层一张索引：逻辑区间 → 本层内位置（tag + moffset）。读取时从最新层往下查，第一个有记录的就赢，命中即停；都没有命中则是空洞，按只读镜像语义返回零。'),
      @('四情形要能手算', '父层 A/B/C/无、上层 无/X/显式零/无：位置0 → A（回落）；位置1 → X（覆盖，父层 B 仍在但被遮住）；位置2 → 全零（显式零遮蔽 C）；位置3 → 零（空洞）。'),
      @('"无记录"与"显式零"', '无记录 = 这层没管这段，继续往下找；显式零 = 明确写过全零，必须终止。把后者当前者，会读回父层旧数据——不报错，属静默损坏。'),
      @('单位与校验', '基础对齐 512 B（lsmt types 的 ALIGNMENT），页与逻辑块常用 4 KiB；转换时校验 page_size=4096、image_offset+length 不溢出、排序后拒绝目的范围重叠。')
    ) `
    '把"显式零"当"无记录"；把后端读失败当零返回；以为一个逻辑读只对应一段层内数据。' `
    '父层有旧值、新状态应为全零，能省略覆盖记录吗？不加会读到什么？' `
    '拼接字节只能得到 A/B/C/D/X/Y，表达不了「X 替换位置 1」。' `
    { param($g, $x, $y, $w, $h) fig_overlay $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('位置0', 2, '2 层'), @('位置1', 1, '1 层'), @('位置2', 2, '2 层'), @('位置3', 3, '3 层')) 3 $C.red } `
    12
}

# ===== P13 ublk 与 daemon（流程）=====
$pages += {
  param($g)
  FlowPage $g '02 概念' @(
    @{t = '内核给壳，用户态给内容：'; c = $C.ink; bold = $false },
    @{t = 'daemon 是这条链的单点'; c = $C.red; bold = $true }) `
    '内核只负责「第几块、多长」，格式与远端都在用户态' 2 `
    @(
      @('等待（io_uring）', 'daemon 在 io_uring 上提交"有活给我"的命令；此时并没有要求 OverlayBD 读某个文件，只是建立接收等待。', '完成点：等待已登记'),
      @('领取（CQE 到）', '内核交付请求描述：queue id、tag、逻辑偏移、长度、缓冲信息。这条 CQE 只表示请求送到了 daemon，不表示数据读完。', '完成点：请求已交付'),
      @('解析（OverlayBD）', 'daemon 查索引：这段逻辑区间由哪一层提供、层内位置在哪；命中缓存可能完全不碰盘，未命中才发起后端读取。', '完成点：字节进入 buffer'),
      @('提交（COMMIT）', 'COMMIT_AND_FETCH_REQ 可合并"报告完成 + 挂下次等待"，但不表示下一项已处理完；内核据此完成原始块请求。', '完成点：原块请求完成')
    ) `
    @(
      @('三个节点别混', '/dev/ublk-control 管创建删除；/dev/ublkcN 是命令交接通道；/dev/ublkbN 是对外读写块设备——Firecracker add_drive 挂的是最后这个。'),
      @('创建时的竞态', 'server 发 Create → 注册设备 → 内核分配 N → daemon 等节点"真正可打开"（不只文件存在：udev 可能还没改好组与权限）→ 回 (dev_id, path)。设备号不固定。'),
      @('集中式的代价', 'daemon 无响应则该节点全部块 IO 停滞或失败；快照恢复前 sandbox.rs 会检查 ublk client 可用。所以它是单点，不是可随意重启的旁路。')
    ) `
    '把 FETCH 的 CQE 当数据读完；把 daemon 当内核模块或每沙箱一个进程。' `
    'FC 挂盘用哪个节点、daemon 收请求用哪个？两者为什么不能混？' `
    '内核搬「第几块、多长」，其余全在用户态。' `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('角色', '用的节点', '做什么', '失败表现') @(@('server', 'ublk-control', '创建/删除设备', '设备建不出来'), @('daemon', 'ublkcN', '领取请求、提交完成', 'IO 停滞'), @('Firecracker', 'ublkbN', '发起块读写', 'Guest IO 超时')) 26 } `
    13
}

# ===== P14 mmap/COW（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '映射了 ≠ 分配了 ≠ 复制了：'; c = $C.ink; bold = $false },
    @{t = '写才复制'; c = $C.green; bold = $true }) `
    'mmap 只建 VMA；分配在缺页；复制在首次写' 2 `
    @(
      @('mmap 只建 VMA', 'mmap(NULL, 128 MiB, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) 成功只建立虚拟范围与属性；不预填充时不会立刻分配 128 MiB 物理页。prot 决定"能不能"，不决定"有没有页"。'),
      @('缺页三类，处理路径不同', 'minor：页已在内存（零页、page cache），映射即可。major：页不在，要读文件或换入，产生真实 IO。非法访问：无映射或权限不符 → SIGSEGV（文件映射也可能 SIGBUS）。写保护缺页不属于非法访问。'),
      @('两种写语义与 COW 时机', 'MAP_SHARED 写进共享缓存并按规则写回；MAP_PRIVATE 只影响私有副本。fork 后父子共享物理页、PTE 都设只读，任一方写才复制——COW 不在 fork 或 mmap 时发生。'),
      @('microVM 里同时有三层缺页', 'Guest 页表（Guest 内核处理，宿主不知情）、EPT（KVM 处理，常能补完直接重入）、宿主页表（匿名页分配或文件页读入）。所以"恢复后很慢"要指出是哪一层缺页。')
    ) `
    '以为 mmap 就占内存；以为 COW 在 fork/mmap 时发生；把三层缺页混成一个缺页率。' `
    '恢复后「第一次读一页」和「第一次写一页」分别发生什么？哪步碰后端？' `
    'RSS 不涨不代表没映射，只是还没被访问。' `
    { param($g, $x, $y, $w, $h) fig_trio $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('VMA 建立', 1, '0 页'), @('缺页', 2, '按需'), @('首次写', 3, 'COW')) 3 $C.orange } `
    14
}

# ===== P15 快照四件套（图文）=====
$pages += {
  param($g)
  SplitPage $g '02 概念' @(
    @{t = '快照是四件套：'; c = $C.ink; bold = $false },
    @{t = '缺一件就恢复不出同款机器'; c = $C.green; bold = $true }) `
    '状态、内存、磁盘、配置各有独立完成点，pause 只是第一件' 2 `
    @(
      @('四件套逐项', 'VM 状态（vCPU 寄存器、指令位置、设备状态）决定"从哪继续执行"；内存镜像（RAM 字节，可增量+父层）决定"变量是什么值"；磁盘视图（rootfs 层+引用）决定"文件长什么样"；恢复配置决定"怎么拼回去"。'),
      @('捕获主线（已核对的调用）', 'pause_to_dir →（有可写持久卷时先经 envd 同步其文件系统）→ fc_instance.pause() → snapshot_to_dir → create_state_only_snapshot(Diff) + get_dirty_memory_ranges() → 转 OverlayBD → 组合父层 → 写 manifest。'),
      @('四个完成点', '暂停（vCPU 全确认）、捕获（读内存/写层/出状态文件）、持久化（fsync/上传）、释放运行时。每段失败留下的残留不同：半停状态、临时文件、半写层、占用设备。'),
      @('一致性反例', '真实顺序 x=100→90、y=100→110；采集到 x=100 与 y=110 就拼出"从未同时存在"的状态。暂停能挡 Guest CPU 写入，但宿主设备侧仍可能写同一块 RAM。')
    ) `
    'pause 成功就当快照成功；单个文件写成功就当整套可用；把 fsync 当业务事务提交。' `
    '哪一步失败会造成「文件存在但恢复不了」？说出两个候选点。' `
    '四件套 + 四完成点，缺一不可。' `
    { param($g, $x, $y, $w, $h) fig_quad4 $g $x $y $w $h @(@('① VM 状态', '寄存器/指令位置/设备', $C.green), @('② 内存镜像', 'RAM 字节 + 父层', $C.green), @('③ 磁盘视图', 'rootfs 层 + 引用', $C.orange), @('④ 恢复配置', '层顺序/设备关联', $C.orange)) } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('完成点', '等待什么', '失败残留') @(@('暂停', '全部 vCPU 确认', '半停状态'), @('捕获', '读内存/写层', '临时文件'), @('持久化', 'fsync/上传', '半写层'), @('释放', '回收运行时', '占用设备')) 26 } `
    15
}

# ===== P16 暂停三完成点（流程）=====
$pages += {
  param($g)
  FlowPage $g '02 概念' @(
    @{t = '暂停不等于快照：'; c = $C.ink; bold = $false },
    @{t = '「没被调度」不是「已暂停」'; c = $C.red; bold = $true }) `
    '调度状态是随机的，协议状态是确定的；快照只能要后者' 2 `
    @(
      @('t1 收到请求', 'API 线程收到 PATCH /vm {state: Paused}，解析成功只说明"请求到了"，不代表任何 vCPU 停下。', '完成点：请求已接收'),
      @('t2 置暂停意图', 'VMM 线程把意图置位，并向各 vCPU 发放"退出"请求（通过 eventfd/信号等手段，具体实现按版本）。', '完成点：退出请求已发出'),
      @('t3—t5 逐个确认', 'vCPU0 从 KVM_RUN 返回并确认；vCPU1 此刻"没被调度"——只是没拿到 CPU，不是暂停；等它被调度、处理退出要求后才确认。', '完成点：全部 vCPU 确认'),
      @('t6 暂停完成', '所有 vCPU 确认后才叫暂停完成；此时 Guest 不再执行，但内存捕获、写层、fsync、manifest 都还没做。', '完成点：VM 已停，快照未成')
    ) `
    @(
      @('为什么必须等确认', '只把状态标成 Paused 而某 vCPU 还在写 Guest RAM，之后读到或保存的内容就可能不一致；这与"只暂停一个 vCPU 不算 VM 暂停"是同一条道理的两种说法。'),
      @('暂停只冻 Guest CPU', '宿主设备侧仍可能在写同一块 RAM，设备 drain 与在途 IO 要单独协调；"全部 vCPU 确认"是必要条件，不是"所有写入源静止"的充分条件。'),
      @('暂停之后还有四步', '捕获内存 → 写层 → fsync/上传 → 改 manifest；任一步失败都可能留下半成品，源码里有临时文件清理与上层恢复逻辑。')
    ) `
    '把「请求发出」或「API 返回成功」当「VM 已停」；把暂停完成当快照已保存。' `
    '只暂停两个 vCPU 里的一个，能叫 VM 已暂停吗？为什么？' `
    '暂停 ≠ 快照；确认 ≠ 持久化。' `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('完成点', '由谁判定', '不能推出') @(@('请求已发出', '本地 socket 写成功', '对方收到'), @('FC 已接收', 'API 线程解析', 'vCPU 全停'), @('全部确认', '各 vCPU 退出确认', '快照已保存')) 30 } `
    16
}

# ===== P17 恢复路径（流程）=====
$pages += {
  param($g)
  FlowPage $g '02 概念' @(
    @{t = '恢复不是把内存读回来：'; c = $C.ink; bold = $false },
    @{t = '只读设备 + 按需缺页 + COW'; c = $C.green; bold = $true }) `
    '恢复成功只代表「能开始跑」，不代表所有页已在宿主 RAM' 2 `
    @(
      @('准备运行环境', '检查 ublk 可用、备盘、备网；这一步失败通常表现为"恢复直接报错"，与内存无关。', '完成点：依赖就绪'),
      @('加载 VM 状态', 'load_snapshot_file(..., BackendType::File, mem_backend_path=/dev/ublkbN, resume_vm=false)：只装状态，不让 vCPU 跑。', '完成点：状态已装载'),
      @('映射内存后端', '内存镜像以只读块设备暴露，FC 用 MAP_PRIVATE 映射；此刻只有映射，没有任何页被预读。', '完成点：映射建立'),
      @('补配置并 resume', '补新挂载卷/MMDS/限流，最后 fc_instance.resume()；vCPU 开始执行，缺页按需从后端取。', '完成点：vCPU 可执行')
    ) `
    @(
      @('为什么 resume_vm=false', '先把状态、设备关联、网络、额外盘都装好，最后才让 vCPU 执行；否则 Guest 会在配置不全时开始跑，表现为"随机的初始化失败"。'),
      @('共享与私有（已核验）', '同一模板的沙箱共享同一只读 ublk 设备，因而共享同一页缓存（device.rs:573-582 注释原文）；FC 以 MAP_PRIVATE 映射（memory.rs:136），写时才 COW。'),
      @('三样不恢复的东西', '外部对端状态、宿主 conntrack/NAT、超时与租约计时器；克隆体还要重随机化 PID/RNG/时钟/序列号。所以恢复后按"重连"设计。')
    ) `
    '以为恢复会预读全部内存；以为恢复 VM 就恢复了业务状态；用旧连接续用的默认假设。' `
    '恢复后首条命令慢、内存指标不高，是故障还是正常？用什么指标证明？' `
    '恢复 = 重建机器 + 装载状态，不是「重新开机」。' `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('对象', '随快照恢复', '需要额外处理') @(@('Guest RAM', '是（按需）', '缺页取页'), @('TCP 对端', '否', '重连 / 幂等'), @('conntrack', '否', '重建或等超时')) 30 } `
    17
}

# ===== P18 网络两方向（表格）=====
$pages += {
  param($g)
  TablePage $g '02 概念' @(
    @{t = '出站靠 SNAT，入站靠 DNAT：'; c = $C.ink; bold = $false },
    @{t = '两条方向相反的路'; c = $C.green; bold = $true }) `
    '每个 netns 都能有 tap0，靠 slot 地址区分实例' 2 `
    @('维度', '出站（Guest → 外网）', '入站（宿主 → envd）', '差异点') `
    @(
      @('链路', 'eth0 → VirtIO → tap0 → netns 路由 → SNAT → veth → 主 netns → MASQUERADE', 'server → veth → PREROUTING DNAT → tap0 → FC → VirtIO RX → envd', '方向相反，NAT 类型相反'),
      @('改的是什么', '源地址改成 slot 的 host_interaction_ip，再由 MASQUERADE 适配出口', '目的地址改成 Guest vm_ip', 'SNAT 改源 / DNAT 改目的'),
      @('依赖的状态', 'conntrack 记录 NAT 映射，回包逆向还原', '同样依赖 conntrack + 放行规则', '状态丢失 → 旧连接断'),
      @('策略分支', 'TCP 80/443 可 REDIRECT 到出口代理（看 Host/SNI）', '通常直连，不经代理', '代理只覆盖 TCP，不终止 TLS')
    ) `
    @(200, 640, 500, 308) `
    @(
      @('同名 tap0 为何不冲突', '每个 netns 有独立的接口命名空间；先由 netns 隔开，再用 slot 专属地址区分实例。所以"200 个沙箱各有 tap0"完全合法。'),
      @('返回包不靠"读包再转发"', 'conntrack 记录 NAT 映射并逆向还原，配合 ESTABLISHED/RELATED 放行；恢复快照不会把 conntrack 一起带回，所以"Guest 里 socket 还在却连不通"很常见。'),
      @('两处性能/兼容边界', 'TX 的 used 只表示发送缓冲可回收，不代表远端收到；MTU 与 offload 不一致会让"小包通、大包挂"，排障时要先对齐 MTU。')
    ) `
    'TX 的 used 只表示缓冲可回收；把 TCP 重定向当全协议域名白名单。' `
    '两个沙箱 Guest 用同一段 IP 为什么不冲突？改策略会断旧连接吗？' `
    '网络不通先分方向：出站看 SNAT/路由，入站看 DNAT/端口。' `
    18
}

# ===== P19 四道门 + seccomp（表格）=====
$pages += {
  param($g)
  TablePage $g '02 概念' @(
    @{t = '四类威胁四道门：'; c = $C.ink; bold = $false },
    @{t = 'seccomp 只约束宿主 syscall'; c = $C.red; bold = $true }) `
    '先问「防谁、越没越过门」，再问「用什么挡」' 2 `
    @('威胁', '谁在作恶', '控制点', '它管不到什么') `
    @(
      @('A Guest 内作恶', 'Guest 内的 root', 'Guest 内核：pid_max、RLIMIT_NPROC', '宿主侧资源与 IO'),
      @('B VMM 被攻破', '逃出 Guest 的宿主进程', 'seccomp（白名单）、降权、chroot、caps、LSM', '白名单内的 syscall 滥用'),
      @('C 资源超用', 'Guest 内任意程序', 'cgroup：memory.max / cpu.max、vCPU 数、balloon', 'Guest 内部分配语义'),
      @('D 网络外连', 'Guest 内任意程序', 'netns + veth + iptables + 出口代理', 'UDP/非 80/443 的协议')
    ) `
    @(220, 320, 600, 348) `
    @(
      @('seccomp 是线程级的', 'vcpu.rs:276 run() 第一件事就是 apply_filter，失败 panic!；Arc<BpfProgram> 每个线程 clone 后各自安装。同进程不同线程可有不同白名单：vmm 60 / api 35 / vcpu 43 条。'),
      @('失败动作是 trap 不是 EPERM', '命中未允许 syscall → SIGSYS 直接杀进程；所以升级 VMM 引入新 syscall 会当场崩。BPF_MAX_LEN=4096，超长直接报错。'),
      @('安装前置条件与两条边界', 'seccomp.rs:99 先 prctl(PR_SET_NO_NEW_PRIVS,1) 再 SYS_seccomp；顺序反且无 CAP_SYS_ADMIN 会 EACCES。另：pids.max 只数宿主 task，挡不住 Guest fork bomb。')
    ) `
    '以为 seccomp 能约束 Guest；以为 namespace 里 root 无特权；以为 pids.max 能挡 Guest fork。' `
    'Guest root 执行任意 syscall 会被 seccomp 拦吗？fork bomb 靠什么限制？' `
    'namespace 改视野、cgroup 改用量、seccomp 改能力。' `
    19
}

# ===== P20 公式页 =====
$pages += {
  param($g)
  FormulaPage $g '02 概念' @(
    @{t = '登记不复制：'; c = $C.ink; bold = $false },
    @{t = 'HVA 由 GPA 偏移算出来'; c = $C.green; bold = $true }) `
    '算出的是 Firecracker 的 HVA：不是 GVA，也不是 HPA' 2 `
    'HVA = userspace_addr + (目标 GPA − guest_phys_addr)' `
    'userspace_addr：登记时给的 HVA 起点；guest_phys_addr：这段 GPA 的起点；目标必须落在同一条 memslot 内；长度由 memory_size 界定。' `
    '登记 GPA 起点 0、HVA 起点 0x70000000；访问 GPA 0x2000 → 0x70000000 + 0x2000 = 0x70002000。该值直接作为 process_vm_readv 的 remote 地址；0x100000 → 0x70100000。' `
    '跨 memslot 要换公式：若第二条是 GPA 64MiB..128MiB → HVA 0x80000000，访问 GPA 0x4010000 时算 0x80000000 + 0x10000。公式只给软件关系：EPT 项是否已建立要另看，页面未驻留还可能触发缺页。' `
    '把 HVA 当 GVA 传给 Guest；跨 memslot 直接套公式。' `
    '两条 memslot 如上，访问 GPA 0x4010000 时 HVA 是多少？' `
    '公式只在「同一条 memslot 内」成立。' `
    20
}

# ===== P21 例题1 =====
$pages += {
  param($g)
  ExamplePage $g '03 例题' @(
    @{t = '这题考「完成点」：'; c = $C.ink; bold = $false },
    @{t = 'FETCH 的 CQE 到了，数据到了吗'; c = $C.green; bold = $true }) `
    'CQE 的语义由它对应的命令决定，不由「它到了」决定' 3 `
    'daemon 收到 UBLK_IO_FETCH_REQ 对应的 CQE。此时能不能说"这个 4 KiB 已经从盘上读到了"？为什么？给出你判断所依据的完成点。' `
    'CQE 已到，携带 queue id、tag、逻辑偏移、长度；后端是只读层 + OverlayBD；未假设缓存命中。' `
    @(
      @('先定位这条 CQE 的语义', '它对应"领取请求"这条命令：内核把队列里的请求交付给 daemon。它不含数据，也不代表后端读过盘。'),
      @('再列还差的动作', 'daemon 查 OverlayBD 索引 → 定层 → 取字节（命中缓存则可能不碰盘）→ 填 daemon buffer → 提交 COMMIT。数据此时在 daemon 侧，不在 Guest 侧。'),
      @('最后给判据', 'COMMIT 完成、内核完成原块请求，数据才算到宿主侧；pread 返回 4096 时字节仍在 daemon buffer，还要经 FC 写进 Guest 页、发布 used、read() 才返回。')
    ) `
    '不能。CQE 只证明"请求已交付"；数据要等 daemon 取到字节并提交完成。若后端 READ 失败，COMMIT 应带错误返回，FC 不应发布成功的 used，Guest 应看到 IO 错误而不是 4 KiB 数据。' `
    '把"领取完成"当"IO 完成"；把 FETCH 的完成与普通 READ 的完成混为一谈（两者 CQE 的 user_data 含义不同）。' `
    '缓存命中时，这条链上有哪几步可以完全跳过？' `
    '凡是 CQE/回调/事件，先问它对应哪条命令。' `
    21
}

# ===== P22 例题2 =====
$pages += {
  param($g)
  ExamplePage $g '03 例题' @(
    @{t = '这题考「作用对象」：'; c = $C.ink; bold = $false },
    @{t = 'Guest 里的 root 会被 seccomp 拦住吗'; c = $C.green; bold = $true }) `
    '机制作用在谁身上，决定了它能不能回答这道题' 3 `
    'Guest 里的 root 用户执行任意 syscall，会被 Firecracker 的 seccomp 拦住吗？说明 seccomp 实际约束的是谁。' `
    'seccomp 白名单装在 firecracker 的线程上（vmm 60 / api 35 / vcpu 43）；Guest 有独立内核；默认动作 trap。' `
    @(
      @('syscall 由谁处理', 'Guest 内 syscall 进入 Guest 内核，由 Guest 内核的服务例程处理；它根本没有发出宿主 syscall，宿主 seccomp 无从拦截。'),
      @('seccomp 拦的是谁', '它拦的是 firecracker 自己发出的宿主 syscall（open/mmap/ioctl 等），防的是"VMM 被攻破之后"的破坏力：提权、加载模块、开新设备。'),
      @('那 Guest 内 fork bomb 靠什么', 'Guest 内核的 pid_max、RLIMIT_NPROC；宿主侧兜底是 memory.max（OOM 杀整台 VM）、cpu.max、vCPU 数。pids.max 只数宿主 task，无效。')
    ) `
    '不会。seccomp 是线程级白名单，只约束 firecracker 发出的宿主 syscall；Guest 内的 root 由 Guest 内核限制。若 Guest 内核本身有提权漏洞，seccomp 也挡不住——那要靠 Guest 内核补丁与最小化攻击面。' `
    '把 seccomp 当"给 Guest 用的沙箱"；把 namespace 里的 root 当已无特权。' `
    '谁能拦住 Guest 里的 fork bomb？两个控制点各说一个管不到的维度。' `
    '每题先问：这个机制作用在哪个对象上。' `
    22
}

# ===== P23 易错点 =====
$pages += {
  param($g)
  MistakesPage $g '03 例题' @(
    @{t = '六个高频错答：'; c = $C.ink; bold = $false },
    @{t = '错在哪一句，正确怎么说'; c = $C.red; bold = $true }) `
    '六条错答共同病根：把「某层完成」当「整件事完成」' 3 `
    @(
      @('pids.max 能挡 Guest 内 fork bomb', '错在对象：pids 控制器数的是宿主 cgroup 里的 task；Guest 进程不是 task。兜底是 memory.max（OOM 杀整台 VM）、cpu.max、vCPU 数。'),
      @('VM-Exit 就等于 KVM_RUN 返回用户态', '错在边界：KVM 能处理的退出直接重入，ioctl 从未返回；只有 MMIO/PIO 这类才把控制权交回 Firecracker。'),
      @('namespace 隔离等于降权', '错在语义：namespace 只改"看见什么"；ns 里的 root 仍是 root。要降权得 uid/gid 切换 + drop capabilities。'),
      @('finalize + rename 等于已持久化', '错在完成点：finalize 只保证格式完成，rename 只换名字；断电安全要 fsync，完整快照还要 manifest 与父层引用一起发布。'),
      @('health 通过等于鉴权通过', '错在请求内容：/health 不加 access token；受保护命令另有鉴权，两者是不同强度。'),
      @('只读块设备 = 各实例各自匿名页', '错在映射模型：同一模板共享同一只读 ublk 设备与页缓存（device.rs:573-582），FC 用 MAP_PRIVATE（memory.rs:136），写才 COW。')
    ) `
    '这六条都能"听起来很顺"，因为都省略了"哪一层/哪一步"。' `
    '用自己的话重讲第 1、2、6 条，各加一个数字或 file:line。' `
    '看到「等于/挡住」先问它管的是哪一层。' `
    23
}

# ===== P24 记忆卡 =====
$pages += {
  param($g)
  CardsPage $g '04 总结' @(
    @{t = '记住 5 个数字'; c = $C.ink; bold = $false },
    @{t = '＋一条主线'; c = $C.green; bold = $true }) `
    '面试里数字比形容词可信，但数字必须带口径' 4 `
    @(@('16', '字节', '一个 VirtIO 描述符'), @('1', '秒', 'health 单次探测上限'), @('4', 'KiB', '页与逻辑块粒度'), @('60/35/43', '条', 'seccomp 三组白名单'), @('3', '个', '暂停的完成点')) `
    @(@('16 字节', 'addr 8B + len 4B + flags 2B + next 2B', 'virtio split virtqueue 规范'),
      @('1 秒', '单次探测上限；判定非 4xx/5xx，不校验 body', 'envd.rs:27 HEALTH_PROBE_TIMEOUT'),
      @('4 KiB', '页/块粒度；与 512 B 扇区差 8 倍', 'overlaybd_snapshot 校验 page_size=4096'),
      @('60/35/43', 'vmm/api/vcpu 三组条数，default trap', 'Firecracker 1.12.1 默认过滤器'),
      @('3 个', '请求发出 / FC 接收 / 全部确认', '本讲第 16 页'),
      @('一条主线', '请求落到硬件，再带结果回到调用者', '读路径六步 + 四个完成点')) `
    '数字不给口径；把上游默认值当部署值。' `
    '这 5 个数字分别落在哪一层？哪个最容易被追问"你的版本是多少"？' `
    '只记三件事：三个执行环境、每层完成点、暂停≠快照≠恢复。' `
    24
}

# ===== P25 练习 =====
$pages += {
  param($g)
  PracticePage $g '04 总结' @(
    @{t = '3 道练习题：'; c = $C.ink; bold = $false },
    @{t = '答案在第 27 页'; c = $C.green; bold = $true }) `
    '先自己写，再翻答案；每题写三行也算完成' 4 `
    @(@('基础', '一台 VM 配 2 个 vCPU，宿主上这台 firecracker 至少几个线程？分别负责什么？Barrier 为什么是 vcpu_count + 1？'),
      @('进阶', '一次 4 KiB 读，Guest 页缓存命中。还会发生 virtio 队列请求吗？如果发生，最可能来自哪几个动作（路径解析 / 元数据 / 预读）？'),
      @('易错', '同事说"快照失败是因为 pause 没成功"。你怎么判断？请指出两个必须分别检查的完成点，以及各自的观测手段。')) `
    '直接翻答案；答案是"知道"，自己写才算"会"。' `
    '三题各写三行，能否 10 分钟内写完？' `
    '写不出来的地方，就是你下一轮要复的页。' `
    25
}

# ===== P26 总结 =====
$pages += {
  param($g)
  SummaryPage $g '04 总结' @(
    @{t = '必须会 5 条'; c = $C.ink; bold = $false },
    @{t = '＋如果只记三件事'; c = $C.green; bold = $true }) `
    '能讲、能画、能量：三样齐了才算会' 4 `
    @('① 三个执行环境与各自的内核视图：宿主 3 个进程、内核功能无 PID、Guest 自带内核与进程表；宿主 ps 看不到 Guest 进程。',
      '② 四条地址线 + process_vm_readv 四参数归属 + HVA 偏移公式；memslot 只登记范围、不复制 RAM。',
      '③ KVM_RUN 循环与"退出 ≠ 返回"；退出次数 / 唤醒次数 / 线程切换是三个不同指标，不可相加。',
      '④ 快照四件套 + 暂停三完成点 + 恢复按需缺页（共享只读设备 + MAP_PRIVATE COW）。',
      '⑤ 四道门：namespace 改视野、cgroup 改用量、seccomp 改能力、降权改身份；seccomp 是线程级、默认 trap。') `
    @('三个执行环境：只有 Guest 有独立内核，宿主 ps 看不到 Guest 进程。',
      '每一层都有自己的完成点：问"完成了吗"必须先说清哪一层。',
      '暂停、快照、恢复是三件事：确认 ≠ 落盘 ≠ 可服务。') `
    '先把第 25 页三题写完；再把「一次 4 KiB 读跨六层」自己画一遍；最后补一个真数字（一次 PVM 读耗时或一次冷/热恢复延迟）。' `
    '把"背下 5 条"当"会讲"——每条都要能配一个数字或一次实测。' `
    '这 5 条里你现在能立刻给出证据的是哪几条？缺的怎么补？' `
    '能讲、能画、能量。' `
    26
}

# ===== P27 附录 =====
$pages += {
  param($g)
  AppendixPage $g '04 总结' @(
    @{t = '考前 10 分钟：'; c = $C.ink; bold = $false },
    @{t = '术语 + 易混 + 答案'; c = $C.green; bold = $true }) `
    '附录只对齐口径，不解释原理' 4 `
    @(
      @('术语速查（7 条）', 'GPA：Guest 以为的物理地址。HVA：某个宿主进程的虚拟地址，必须说明是谁。memslot：KVM 里 GPA 区间与 HVA 区间的登记关系。VM-Exit：Guest 到宿主执行环境的切换，由硬件完成。vCPU：一个宿主线程 + 一个 KVM vCPU。rootfs：Guest 里 / 的整棵目录树。ublk：内核出壳、用户态给内容的块设备。'),
      @('易混 8 对', 'VM-Exit ≠ KVM_RUN 返回｜暂停完成 ≠ 快照完成｜领取完成 ≠ 数据读完｜文件偏移 ≠ 磁盘偏移｜映射了 ≠ 分配了｜只读设备 ≠ 不共享页缓存｜namespace ≠ 降权｜health 通过 ≠ 鉴权通过。'),
      @('练习答案（第 25 页）', '① 至少 4 个线程：vmm 主线程、api 线程、fc_vcpu 0/1；Barrier 的 +1 是主线程，确保所有 vCPU 完成 TLS 初始化后才发启动。② 通常不为这批数据发 virtio 请求，但路径解析、元数据、并发预读仍可能产生 IO。③ 先查"全部 vCPU 是否确认"与"内存层/状态文件是否写完并 fsync"；pause 成功而捕获失败同样表现为快照失败。口径声明：60/35/43、BPF_MAX_LEN=4096、16 字节描述符来自 FC 1.12.1 与 virtio 规范；性能数字未实测，不写毫秒。')
    ) `
    '把"以教材/老师口径为准"当废话——版本不同，白名单条数与映射标志都可能变。' `
    '这 8 对易混你能各说一句区别吗？说不出的那对回哪一页？' `
    '附录只对齐口径，不解释原理。' `
    27
}

# ---------------- 渲染 ----------------
$i = 0
foreach ($p in $pages) {
  $i++
  $name = 'p{0:d2}.png' -f $i
  $path = Join-Path $OUT2 $name
  $pg = NewPage $path
  try { & $p $pg.g } catch { Note ("PAGE {0} 失败: {1}`n{2}" -f $i, $_.Exception.Message, $_.ScriptStackTrace) }
  SavePage $pg
}
Note ("total: {0} pages -> {1}" -f $i, $OUT2)
