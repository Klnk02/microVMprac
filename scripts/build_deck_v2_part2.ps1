#requires -Version 5.1
<#
  AgentENV 复习课件 v2 —— 第 2 部分：27 页内容与渲染
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'build_deck_v2_part1.ps1')

$pages = @()

# ============ 01 总览 ============
$pages += {
  param($g)
  ContentPage $g '01 总览' @(
    @{t = 'AgentENV 沙箱：'; c = $C.ink; bold = $false },
    @{t = '三个执行环境、六条链路、一个完成点判断'; c = $C.green; bold = $true }) `
    '28 讲压缩成 27 页：先建结构，再记机制，最后能自己复述' 1 `
    @(
      @('三个执行环境', '宿主用户态 3 个进程（server / firecracker / ublk-daemon）；宿主内核 KVM/ublk 驱动/cgroup 是功能，无 PID；Guest 自带内核与进程表。'),
      @('六条链路', '创建、执行、读文件、暂停、恢复、销毁。每条链有 3—4 个完成点，例如读文件链的四个完成点分属四层。'),
      @('一个判断句', '这一步的「完成」由谁判定、下一层知道了吗。ioctl 返回 ≠ Guest 执行完；发布 used ≠ Guest 已处理。'),
      @('证据规矩', '数字必须带口径（单位/范围/版本）；未实测写「量级」或「资料不足」。本讲不写具体毫秒。')
    ) `
    '把「28 课都讲过」当成「会讲」——学习记录里独立验收是 0/28。' `
    '说出三个执行环境里各有哪些进程，以及哪些对象没有 PID。' `
    '所有答案都落在「谁在哪一层、这一步算完成了吗」。' `
    { param($g, $x, $y, $w, $h) fig_map $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) fig_numcards $g $x ($y + 20) $w $h @(@('3', '个执行环境', '宿主 3 进程 + 内核功能 + Guest'), @('6', '条链路', '创建/执行/读/暂停/恢复/销毁'), @('4', '个完成点', '读路径：CQE→COMMIT→used→read'), @('0', '个实测数字', '性能数字全部标注未实测'), @('27', '页', '一页一个知识点')) } `
    1
}

$pages += {
  param($g)
  ContentPage $g '01 总览' @(
    @{t = '先建立结构，'; c = $C.ink; bold = $false },
    @{t = '再记细节'; c = $C.green; bold = $true }) `
    '六个模块有硬依赖：跳过位置与地址，后面只会变成名词记忆' 1 `
    @(
      @('依赖分三层', '地基：位置、地址。中间：执行（退出语义）、存储（virtio→ublk→层）。上层：状态（快照/恢复）、平台（资源/并发/度量）。'),
      @('一个具体依赖', 'process_vm_readv 四个参数：pid 选地址空间、local 是调用者缓冲、remote 放 Firecracker 的 HVA、count 是元素个数。'),
      @('三个易混区', '状态：暂停/快照/恢复本是三件事；平台：资源拥有 vs 引用消失；存储：逻辑偏移 vs 层内偏移 vs 后端位置。'),
      @('五个问题', '进程在谁那边？读到哪算完成？暂停等于快照吗？三件隔离工具各挡什么？恢复后旧连接为何可能不通？')
    ) `
    '跳过地址直接看快照，会把「按需缺页」「COW」「持久化」当成同一件事。' `
    '「恢复后首条命令慢」必须先懂哪个机制，为什么？' `
    '先建结构（谁在哪层），再记细节（那层的完成点）。' `
    { param($g, $x, $y, $w, $h) fig_map $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('位置', 0, '0'), @('地址', 0, '0'), @('执行', 2, '2'), @('存储', 2, '2'), @('状态', 3, '3'), @('平台', 5, '5')) 6 $C.green } `
    2
}

# ============ 02 概念 ============
$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '一台机器三个执行环境，'; c = $C.ink; bold = $false },
    @{t = '只有 Guest 有自己的内核'; c = $C.green; bold = $true }) `
    '进程、线程、内核功能三种对象混在一起，是所有位置题答错的总根源' 2 `
    @(
      @('Firecracker 是宿主进程', 'Command::new 只准备参数；spawn_tokio_command_scoped 返回 child 才真正启动；self.process 保存句柄，child.id() 是宿主 PID。'),
      @('内核功能没有 PID', 'KVM 是 /dev/kvm 上的 ioctl 集合，ublk 驱动是块设备子系统，cgroup/seccomp 是内核机制；把它们画成进程，位置题必错。'),
      @('Guest 由 Guest 内核调度', '它的程序是 Guest RAM 里的一段字节，靠 Guest 页表 + EPT 访问；宿主 ps 只看到 firecracker 的若干线程。'),
      @('两条跨层通道', '控制面：宿主 Unix socket（--api-sock，REST）。应用面：TCP 经 tap0+DNAT 到 envd（HTTP /health 与 gRPC 同址、带 token）。')
    ) `
    '把 FirecrackerInstance 当进程；把宿主 PID 当 Guest PID。' `
    '宿主 ps -eLf 能列出哪几个？列不出来的对象凭什么说它们「在」？' `
    '先问：这个对象有没有自己的 PID、由谁的内核调度。' `
    { param($g, $x, $y, $w, $h) fig_layers3 $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('对象', '宿主可见', '有 PID') @(@('server / firecracker / ublk-daemon', '是', '是'), @('KVM / ublk 驱动 / cgroup', '否', '否'), @('Guest 内核 / envd / 你的程序', '否（Guest 侧可见）', '是（Guest 内）')) 28 } `
    3
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '一个变量四个地址：'; c = $C.ink; bold = $false },
    @{t = 'HVA 只属于某一条访问路径'; c = $C.green; bold = $true }) `
    '同一块物理页有两条访问路径，HVA 只属于其中一条' 2 `
    @(
      @('两条翻译链', 'Guest：GVA→GPA（Guest 页表）→HPA（EPT）。Firecracker：HVA→HPA（宿主页表）。两条链落在同一页，不存在两份内存。'),
      @('登记接口的实际字段', 'KVM_SET_USER_MEMORY_REGION{slot, flags, guest_phys_addr, memory_size, userspace_addr}：没有 HPA 字段，因为用户态拿不到物理地址。'),
      @('偏移公式与代入', 'HVA = userspace_addr + (目标 GPA - guest_phys_addr)；0x70000000 + 0x2000 = 0x70002000，直接当 PVM 的 remote。'),
      @('memslot 的两个约束', '数量上限来自 KVM_CAP_NR_MEMSLOTS（超了报 NotEnoughMemorySlots）；每条可带 dirty log，快照的「哪些页要存」按它拿。')
    ) `
    '以为 Guest 正常访存会经过 HVA；以为 memslot 就是 EPT 表。' `
    'guest_phys_addr=0、userspace_addr=0x70000000，访问 GPA 0x2000 时 remote 填什么？' `
    '地址是名字，进程是语境。' `
    { param($g, $x, $y, $w, $h) fig_dualpath $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('Guest 访存', 2, '2 次'), @('FC 访存', 1, '1 次')) 2 $C.orange } `
    4
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '三个「切换」不是一回事：'; c = $C.ink; bold = $false },
    @{t = '只有线程切换才是真没拿到 CPU'; c = $C.green; bold = $true }) `
    '把三种边界混成一个，就没法把「慢」拆开' 2 `
    @(
      @('KVM_RUN 是系统调用', '进内核、换特权级、线程不变。返回时带 kvm_run->exit_reason；注意硬件层叫 EPT_VIOLATION，暴露给用户态叫 KVM_EXIT_MMIO。'),
      @('VM-Exit 是硬件行为', 'CPU 把 Guest 寄存器写进 VMCS 的 guest-state，把退出原因与 qualification 写进 VM-exit 信息区，再载入宿主状态。'),
      @('KVM 处理完直接重入', '典型是普通 RAM 的 EPT 缺项：KVM 按 memslot 取页建项后重入，ioctl 从头到尾没返回用户态。'),
      @('三个指标分开报', '退出次数（硬件）、被唤醒次数（用户态）、上下文切换（调度器）。互为因果但不可相加。')
    ) `
    '把 VM-Exit 当 KVM_RUN 返回；把补 EPT 映射的开销算到设备模型头上。' `
    '一次 EPT 缺页退出会让 FC 从 ioctl 返回吗？判据是什么？' `
    '看到「慢」先分三类：退出 / 调度 / IO。' `
    { param($g, $x, $y, $w, $h) fig_switches $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('边界', '切宿主线程', '典型误判') @(@('KVM_RUN 系统调用', '否', '以为进了 Guest'), @('VM-Entry / VM-Exit', '否', '以为每次回用户态'), @('宿主线程切换', '是', '把调度延迟算虚拟化开销')) 28 } `
    5
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '一个 vCPU 就是一个线程：'; c = $C.ink; bold = $false },
    @{t = '多线程是为了能接住控制请求'; c = $C.green; bold = $true }) `
    '不是为了性能：单线程时 Guest 卡在 KVM_RUN 里，宿主连暂停都下不了' 2 `
    @(
      @('线程创建的真实路径', 'lib.rs:397 对每个 vCPU 调 start_threaded(filter.clone(), barrier.clone())；vcpu.rs:246 用 thread::Builder.name("fc_vcpu {i}").spawn。'),
      @('Barrier 的 +1 是主线程', 'lib.rs:372 Barrier::new(vcpu_count+1)，lib.rs:401 主线程也 wait()：所有 vCPU 完成 TLS 初始化后才发启动。'),
      @('线程名写死才好排障', '.name() 决定 ps -eLf 看到的名字；内核 comm 上限 16 字节含结尾 0，所以最长 15 字符。'),
      @('「在 KVM_RUN 里」≠ 空闲', 'CPU 可能正在该线程上下文跑 Guest，占用率包含跑 Guest 的时间；只有 HLT/等事件时才真阻塞。')
    ) `
    '以为 vCPU 线程闲置；以为线程名会自动继承。' `
    '配 2 个 vCPU，宿主至少几个线程？Barrier 为什么是 vcpu_count+1？' `
    '线程数 = 1（vmm）+ 1（api）+ N（vcpu）。' `
    { param($g, $x, $y, $w, $h) fig_threads $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('1 vCPU', 3, '3'), @('2 vCPU', 4, '4'), @('4 vCPU', 6, '6'), @('8 vCPU', 10, '10')) 10 $C.green } `
    6
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '控制面走 socket，数据面走队列：'; c = $C.ink; bold = $false },
    @{t = 'HTTP 只是消息格式'; c = $C.green; bold = $true }) `
    '两条通道的故障表现完全不同，混了就没法排障' 2 `
    @(
      @('控制面的载体与调用', '宿主 Unix socket：PATCH /vm、PUT /snapshot/load、GET /vm/dirty-memory-ranges；由 FC 的 API 线程解析，不需要 Guest 调度。'),
      @('数据面的依赖', 'Guest RAM 里的 virtqueue：描述符 + avail + used + 门铃；设备与驱动必须协作推进，Guest 内核卡死时队列不动。'),
      @('为什么暂停不能走数据面', '暂停的用途之一正是「Guest 不配合时也能停住它」；依赖 Guest 处理队列就是循环论证。'),
      @('超时的三种可能', '没送到 / 做成了但响应丢了 / 还在做。所以超时既不能推出「VM 还在跑」，也不能推出「操作失败」。')
    ) `
    '把 socket 当网络；把超时当失败。' `
    '超时后补发一次 resume 有什么风险？举一个坏结果。' `
    'socket 是宿主之间，virtqueue 是 Guest 参与。' `
    { param($g, $x, $y, $w, $h) fig_channels $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('场景', '控制面', '数据面') @(@('Guest 正常运行', '可用', '可用'), @('Guest 内核卡死', '仍可用', '停住')) 30 } `
    7
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '队列在内存里，通知只提醒：'; c = $C.ink; bold = $false },
    @{t = '描述符不搬字节'; c = $C.green; bold = $true }) `
    '设备不是「收到包」，而是「去共享队列取一条描述」' 2 `
    @(
      @('三件套与 16 字节字段', '描述符 addr(8B, GPA) + len(4B) + flags(2B: NEXT/WRITE) + next(2B)；avail 环 Guest 写；used 环设备写。'),
      @('通知的语义边界', '门铃只表示「去检查队列」：不带数据、可被抑制、一次通知可对应多项工作（avail 有 3/7/9 只敲一次）。'),
      @('复用风险', '同一链头发布两次 = 两次使用机会；未处理完 used 就再次发布，设备可能覆盖仍需读的内容。'),
      @('为什么快', '模拟真实设备时每个寄存器访问都是一次 VM-Exit；VirtIO 把数据批量放共享内存，只在有活时敲一次门铃。')
    ) `
    '把「设备发布 used」当成「Guest 已处理」；把通知次数当请求数。' `
    'Guest 未处理完就把缓冲再次发布，会发生什么？为什么难复现？' `
    '队列在内存、通知只提醒、数据在 buffer。' `
    { param($g, $x, $y, $w, $h) fig_virtio $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_stack $g $x $y $w $h } `
    8
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '三层就绪，一层比一层强：'; c = $C.ink; bold = $false },
    @{t = '最后一层才代表能干活'; c = $C.green; bold = $true }) `
    '「进程在」「端口通」「服务能应答」是三件强度不同的事' 2 `
    @(
      @('第一层：API socket', '能配 VM、能 pause，证明 VMM 起来了、--api-sock 路径对；start_nowait() 就停在这一层。'),
      @('第二层：网络可达', '宿主经 tap0 能到 Guest，证明 netns/网卡/IP/端口都对；这一层的失败最常被误诊成「服务没起来」。'),
      @('第三层：/health 通过', '状态码非 4xx/5xx 即通过（不校验 body，204 也算过）；单次上限 1 秒，失败重试，期限耗尽才报超时。'),
      @('health 不带 token', 'envd 客户端把 base 与 gRPC 地址设为同一地址，token 单独保存并用于受保护请求；所以健康通过 ≠ 鉴权通过。')
    ) `
    '把 health 通过当完整可用；把「对象创建成功」当「服务就绪」。' `
    '端口能连、命令返回 UNAUTHENTICATED，问题在哪层？health 为什么排除不了？' `
    '就绪答三层，比「服务起来了」多拿一分。' `
    { param($g, $x, $y, $w, $h) fig_ladder $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('期限 5s', 10, '10 次'), @('期限 10s', 20, '20 次')) 20 $C.orange } `
    9
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = 'exec 返回的是流：'; c = $C.ink; bold = $false },
    @{t = 'Start 说明不了成功'; c = $C.green; bold = $true }) `
    '两个独立判断：事件是否收齐、退出码是多少' 2 `
    @(
      @('接口形状', 'start_process_inner(cmd, args, envs, cwd) → 打包 StartRequest → envd 的 gRPC ProcessClient.start → 返回流，必须消费到结束。'),
      @('三类事件', 'Start{pid} 进程已创建；Data stdout/stderr 分段（可能 0 条）；End{exit_code} 进程已退出。Data 既不证明成功也不证明失败。'),
      @('两个独立判断', '① 事件是否收齐（收到 End=Ok，流断=Err，协议层）② exit_code 是否 0（程序层）；wait 返回 Ok 只代表取得结果。'),
      @('没有 shell 与超时', '命令与参数分开传，不假设经 shell 解析；超时后发终止请求可能失败，不能断言进程已退出，重试可能重复执行。')
    ) `
    '看到 Start 就当成功；只看 exit_code 不看流是否收齐。' `
    '可执行文件起不来时一定会先收到 Start 吗？这如何影响判错逻辑？' `
    'Start 之后追两件事：End 到了吗、退出码是多少。' `
    { param($g, $x, $y, $w, $h) fig_eventstream $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('事件', '携带', '只说明') @(@('Start', 'Guest PID', '进程被创建'), @('Data', 'stdout/stderr', '有输出'), @('End', 'exit_code', '进程已退出')) 30 } `
    10
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '一次 4 KiB 读跨六层：'; c = $C.ink; bold = $false },
    @{t = '每层「完成」含义都不同'; c = $C.green; bold = $true }) `
    '排障就是把「卡在哪一层、哪个完成点」定位出来' 2 `
    @(
      @('六步链', 'read() → ext4 算 LBA → virtio 描述符+门铃（MMIO→VM-Exit）→ ublk 入队（queue/tag）→ daemon 查 OverlayBD → 返回填页。'),
      @('四个完成点', 'FETCH 的 CQE 到=请求送到；COMMIT=daemon 交差；used=设备交差；read() 返回=应用拿到字节。'),
      @('三个偏移与 8 倍差', '文件偏移（字节）、LBA（块号）、后端位置。同一 8 MiB：512 B 编号 16384，4 KiB 编号 2048。'),
      @('缓存改变的不只是速度', '页缓存命中可免设备 IO，但路径解析、元数据、并发预读仍可能产生 IO；不能断言整次零设备请求。')
    ) `
    '把 FETCH 的 CQE 当数据读完；报 LBA 不带单位。' `
    'FETCH CQE 到了但后端读失败，哪些层还能报成功？read() 返回什么？' `
    '问「完成了吗」必须先说清是哪一层。' `
    { param($g, $x, $y, $w, $h) fig_sixstep $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('512 B 扇区', 16384, '16384'), @('4 KiB 块', 2048, '2048')) 16384 $C.orange } `
    11
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '分层是覆盖映射，'; c = $C.ink; bold = $false },
    @{t = '不是拼字节'; c = $C.green; bold = $true }) `
    '无记录要回落，显式零要终止：两种都为 0，语义完全不同' 2 `
    @(
      @('读取规则', '每层一张索引（逻辑区间→本层位置）；从最新层往下查，第一个有记录的就赢，命中即停，都没有是空洞。'),
      @('四情形手算', '父层 A/B/C/无、上层 无/X/显式零/无：→ A（回落）、X（覆盖）、全零（遮蔽）、零（空洞）。'),
      @('「无记录」与「显式零」', '前者=这层没管，继续往下找；后者=明确写过全零，必须终止。混淆会静默读回父层旧数据。'),
      @('单位与校验', '基础对齐 512 B，页与块常用 4 KiB；转换时 image_offset+length 不得溢出，排序后拒绝目的范围重叠。')
    ) `
    '把「显式零」当「无记录」；把后端读失败当零返回。' `
    '父层有旧值、新状态应为全零，能省略覆盖记录吗？不加会读到什么？' `
    '拼接字节只能得到 A/B/C/D/X/Y，表达不了「X 替换位置 1」。' `
    { param($g, $x, $y, $w, $h) fig_overlay $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('位置0', 2, '2 层'), @('位置1', 1, '1 层'), @('位置2', 2, '2 层'), @('位置3', 3, '3 层')) 3 $C.red } `
    12
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '内核给壳，用户态给内容：'; c = $C.ink; bold = $false },
    @{t = 'daemon 是这条链的单点'; c = $C.red; bold = $true }) `
    '内核只负责「第几块、多长」，格式与远端都在用户态' 2 `
    @(
      @('三个设备节点', 'ublk-control 管创建删除；ublkcN 是命令交接通道；ublkbN 是对外读写块设备，Firecracker add_drive 挂的是它。'),
      @('创建流程与竞态', 'server 发 Create → 注册设备 → 内核分配 N → daemon 等节点「真正可打开」（udev 可能还没改权限）→ 回 (dev_id, path)。'),
      @('四步处理', '等待 io_uring → 领取 CQE（只表示请求送到）→ 查 OverlayBD 定层取字节 → 提交 COMMIT 完成原块请求。'),
      @('集中式的代价', 'daemon 无响应则该节点全部块 IO 停滞或失败；快照恢复前 sandbox.rs 会检查 ublk client 可用。')
    ) `
    '把 FETCH 的 CQE 当数据读完；把 daemon 当内核模块或每沙箱一个进程。' `
    'FC 挂盘用哪个节点、daemon 收请求用哪个？两者为什么不能混？' `
    '内核搬「第几块、多长」，其余全在用户态。' `
    { param($g, $x, $y, $w, $h) fig_ublk $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('角色', '用的节点', '做什么') @(@('server', 'ublk-control', '创建/删除设备'), @('daemon', 'ublkcN', '领取请求、提交完成'), @('Firecracker', 'ublkbN', '发起块读写')) 30 } `
    13
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '映射了 ≠ 分配了 ≠ 复制了：'; c = $C.ink; bold = $false },
    @{t = '写才复制'; c = $C.green; bold = $true }) `
    'mmap 只建 VMA；分配在缺页；复制在首次写' 2 `
    @(
      @('mmap 只建 VMA', 'mmap(NULL,128MiB,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0) 成功只建虚拟范围；prot 决定能不能，不决定有没有页。'),
      @('缺页三类', 'minor（页已在内存）、major（要读盘/换入）、非法访问（SIGSEGV/SIGBUS）；写保护缺页不算非法，那是 COW 正常处理。'),
      @('两种写语义', 'MAP_SHARED 写进共享缓存并回写；MAP_PRIVATE 只影响私有副本。fork 后共享页、PTE 只读，任一方写才复制。'),
      @('三层缺页同在', 'Guest 页表（Guest 内核处理）、EPT（KVM 处理常能重入）、宿主页表（匿名页分配或文件页读入），不能混成一个缺页率。')
    ) `
    '以为 mmap 就占内存；以为 COW 在 fork/mmap 时发生。' `
    '恢复后「第一次读一页」和「第一次写一页」分别发生什么？哪步碰后端？' `
    'RSS 不涨不代表没映射，只是还没被访问。' `
    { param($g, $x, $y, $w, $h) fig_trio $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('VMA 建立', 1, '0 页'), @('缺页', 2, '按需'), @('首次写', 3, 'COW')) 3 $C.orange } `
    14
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '快照是四件套：'; c = $C.ink; bold = $false },
    @{t = '缺一件就恢复不出同款机器'; c = $C.green; bold = $true }) `
    '状态、内存、磁盘、配置各有独立完成点，pause 只是第一件' 2 `
    @(
      @('四件套逐项', 'VM 状态（寄存器/设备）、内存镜像（RAM 字节，可增量+父层）、磁盘视图（rootfs 层+引用）、恢复配置与索引。'),
      @('捕获主线', 'pause → snapshot_to_dir → create_state_only_snapshot(Diff) + get_dirty_memory_ranges → 转 OverlayBD → 组合父层 → 写 manifest。'),
      @('四个完成点', '暂停（vCPU 全确认）、捕获（读内存/写层）、持久化（fsync/上传）、释放运行时；每段失败残留不同。'),
      @('一致性反例', '真实 x=100→90、y=100→110；采到 x=100 与 y=110 就拼出从未同时存在的状态。暂停挡不住宿主设备写。')
    ) `
    'pause 成功就当快照成功；把 fsync 当业务事务提交。' `
    '哪一步失败会造成「文件存在但恢复不了」？说出两个候选点。' `
    '四件套 + 四完成点，缺一不可。' `
    { param($g, $x, $y, $w, $h) fig_quad4 $g $x $y $w $h @(@('① VM 状态', '寄存器/指令位置/设备', $C.green), @('② 内存镜像', 'RAM 字节 + 父层', $C.green), @('③ 磁盘视图', 'rootfs 层 + 引用', $C.orange), @('④ 恢复配置', '层顺序/设备关联', $C.orange)) } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('完成点', '等待什么', '失败残留') @(@('暂停', '全部 vCPU 确认', '半停状态'), @('捕获', '读内存/写层', '临时文件'), @('持久化', 'fsync/上传', '半写层'), @('释放', '回收运行时', '占用设备')) 26 } `
    15
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '暂停不等于快照：'; c = $C.ink; bold = $false },
    @{t = '「没被调度」不是「已暂停」'; c = $C.red; bold = $true }) `
    '调度状态是随机的，协议状态是确定的；快照只能要后者' 2 `
    @(
      @('时间线 t1—t6', 't1 收到请求 → t2 置意图 → t3 vCPU0 确认 → t4 vCPU1 没被调度（≠暂停）→ t5 才确认 → t6 完成。'),
      @('三个完成点', '请求已发出（写进 socket）、FC 已接收（API 解析成功）、全部 vCPU 确认（没有 vCPU 还能跑 Guest）。'),
      @('为什么必须等确认', '只标 Paused 而某 vCPU 还在写 RAM，之后读到的内容可能不一致；这与「只暂停一个 vCPU」是同一条道理。'),
      @('暂停的边界', '只停 Guest CPU 写入；宿主设备侧仍可能写同一块 RAM，设备 drain 与在途 IO 要单独协调。')
    ) `
    '把「请求发出」或「API 返回成功」当「VM 已停」；把暂停完成当快照已保存。' `
    '只暂停两个 vCPU 里的一个，能叫 VM 已暂停吗？为什么？' `
    '暂停 ≠ 快照；确认 ≠ 持久化。' `
    { param($g, $x, $y, $w, $h) fig_timeline $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('完成点', '由谁判定', '不能推出') @(@('请求已发出', '本地 socket 写成功', '对方收到'), @('FC 已接收', 'API 线程解析', 'vCPU 全停'), @('全部确认', '各 vCPU 退出确认', '快照已保存')) 30 } `
    16
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '恢复不是把内存读回来：'; c = $C.ink; bold = $false },
    @{t = '只读设备 + 按需缺页 + COW'; c = $C.green; bold = $true }) `
    '恢复成功只代表「能开始跑」，不代表所有页已在宿主 RAM' 2 `
    @(
      @('五步链', '检查 ublk → load_snapshot(BackendType::File, mem_backend=/dev/ublkbN, resume_vm=false) → 映射只读内存 → 补卷/MMDS → resume。'),
      @('resume_vm=false 的理由', '先把状态、设备关联、网络、额外盘装好，最后才让 vCPU 跑；否则 Guest 会在配置不全时开始执行。'),
      @('一页怎么变可访问', 'GPA 缺项 → 向只读设备发块读 → daemon 查 OverlayBD 取块 → 填宿主页 → Guest 继续；写则 COW 到私有层。'),
      @('三样不恢复的东西', '外部对端状态、宿主 conntrack/NAT、超时与租约计时器；克隆体还要重随机化 PID/RNG/时钟/序列号。')
    ) `
    '以为恢复会预读全部内存；以为恢复 VM 就恢复了业务状态。' `
    '恢复后首条命令慢、内存指标不高，是故障还是正常？用什么指标证明？' `
    '恢复 = 重建机器 + 装载状态，不是「重新开机」。' `
    { param($g, $x, $y, $w, $h) fig_fivestep $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('对象', '随快照恢复', '需要额外处理') @(@('Guest RAM', '是（按需）', '缺页取页'), @('TCP 对端', '否', '重连/幂等'), @('conntrack', '否', '重建或等待超时')) 30 } `
    17
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '出站靠 SNAT，入站靠 DNAT：'; c = $C.ink; bold = $false },
    @{t = '两条方向相反的路'; c = $C.green; bold = $true }) `
    '每个 netns 都能有 tap0，靠 slot 地址区分实例' 2 `
    @(
      @('出站链路', 'eth0 → VirtIO → tap0 → 沙箱 netns 路由 → SNAT（改源为 slot 地址）→ veth → 主 netns → MASQUERADE（适配出口）。'),
      @('入站链路', 'server 连 slot 地址 → veth → PREROUTING DNAT（改目的为 Guest IP）→ tap0 → FC → VirtIO RX → envd。'),
      @('同名 tap0 为何不冲突', '每个 netns 有独立接口命名空间；先由 netns 隔开，再用 slot 专属地址区分实例。'),
      @('策略分支与边界', 'TCP 80/443 可 REDIRECT 到出口代理（看 Host/SNI），不终止 TLS、不改写 HTTP；只覆盖 TCP，非通用域名防火墙。')
    ) `
    'TX 的 used 只表示缓冲可回收；conntrack 不回滚，恢复后旧连接可能不通。' `
    '两个沙箱 Guest 用同一段 IP 为什么不冲突？改策略会断旧连接吗？' `
    '网络不通先分方向：出站看 SNAT/路由，入站看 DNAT/端口。' `
    { param($g, $x, $y, $w, $h) fig_twochains $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('50 沙箱', 150, '~150 条'), @('100 沙箱', 300, '~300 条')) 300 $C.orange } `
    18
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '四类威胁四道门：'; c = $C.ink; bold = $false },
    @{t = 'seccomp 只约束宿主 syscall'; c = $C.red; bold = $true }) `
    '先问「防谁、越没越过门」，再问「用什么挡」' 2 `
    @(
      @('四类威胁', 'A Guest 内作恶（Guest 内核限）、B VMM 被攻破（seccomp/降权/chroot/caps/LSM）、C 资源超用（cgroup/vCPU）、D 网络外连（netns/iptables）。'),
      @('seccomp 的装载位置', 'vcpu.rs:276 run() 第一件事就是 apply_filter，失败 panic!；Arc<BpfProgram> 每线程 clone 后各自安装。'),
      @('白名单与失败动作', 'FC 1.12.1 默认 vmm 60 / api 35 / vcpu 43 条，default_action=trap；命中未允许 → SIGSYS 杀进程；BPF_MAX_LEN=4096。'),
      @('安装前置条件', 'seccomp.rs:99 先 prctl(PR_SET_NO_NEW_PRIVS,1)，再 syscall(SYS_seccomp,…)；顺序反且无 CAP_SYS_ADMIN 会 EACCES。')
    ) `
    '以为 seccomp 能约束 Guest；以为 namespace 里 root 无特权；以为 pids.max 能挡 Guest fork。' `
    'Guest root 执行任意 syscall 会被 seccomp 拦吗？fork bomb 靠什么限制？' `
    'namespace 改视野、cgroup 改用量、seccomp 改能力。' `
    { param($g, $x, $y, $w, $h) fig_quad4 $g $x $y $w $h @(@('A Guest 内作恶', 'Guest 内核挡', $C.green), @('B VMM 被攻破', 'seccomp/降权/caps', $C.red), @('C 资源超用', 'cgroup/vCPU/balloon', $C.orange), @('D 网络外连', 'netns/iptables/代理', $C.orange)) } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('vmm', 60, '60'), @('api', 35, '35'), @('vcpu', 43, '43')) 60 $C.red } `
    19
}

$pages += {
  param($g)
  ContentPage $g '02 概念' @(
    @{t = '登记不复制：'; c = $C.ink; bold = $false },
    @{t = 'HVA 由 GPA 偏移算出来'; c = $C.green; bold = $true }) `
    '算出的是 Firecracker 的 HVA：不是 GVA，也不是 HPA' 2 `
    @(
      @('公式与变量', 'HVA = userspace_addr + (目标 GPA - guest_phys_addr)；userspace_addr 是 HVA 起点，目标必须落在同一条 memslot 内。'),
      @('代入一个数', 'GPA 起点 0、HVA 起点 0x70000000；访问 GPA 0x2000 → 0x70002000，直接作为 PVM 的 remote 地址。'),
      @('跨 memslot 会算错', '两条 memslot（0..64MiB→0x70000000；64MiB..128MiB→0x80000000）时，访问 0x4010000 必须用第二条公式。'),
      @('公式给的是软件关系', 'EPT 项是否已建立要另看：缺项时 KVM 才取页建项；页面未驻留还可能触发缺页，公式不保证已驻留。')
    ) `
    '把 HVA 当 GVA 传给 Guest；跨 memslot 直接套公式。' `
    '两条 memslot 如上，访问 GPA 0x4010000 时 HVA 是多少？' `
    '公式只在「同一条 memslot 内」成立。' `
    { param($g, $x, $y, $w, $h) fig_formula $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('目标 GPA', '计算式', 'HVA') @(@('0x0', '0x70000000 + 0', '0x70000000'), @('0x2000', '0x70000000 + 0x2000', '0x70002000'), @('0x100000', '0x70000000 + 0x100000', '0x70100000')) 30 } `
    20
}

# ============ 03 例题 ============
$pages += {
  param($g)
  ContentPage $g '03 例题' @(
    @{t = '这题考「完成点」：'; c = $C.ink; bold = $false },
    @{t = 'FETCH 的 CQE 到了，数据到了吗'; c = $C.green; bold = $true }) `
    'CQE 的语义由它对应的命令决定，不由「它到了」决定' 3 `
    @(
      @('题面与已知', 'daemon 收到 UBLK_IO_FETCH_REQ 的 CQE（带回 queue/tag/偏移/长度）；后端是只读层 + OverlayBD。问能否断言「已读到」。'),
      @('步骤1：定位语义', '这条 CQE 对应「领取请求」命令，只说明请求已交付给 daemon；它不含数据，也不代表后端读过盘。'),
      @('步骤2：列还差的动作', '查 OverlayBD 索引 → 定层 → 取字节（命中缓存可能不碰盘）→ 填 daemon buffer → 提交 COMMIT。'),
      @('步骤3：给判据', 'COMMIT 完成、内核完成原块请求后数据才算到；pread 返回 4096 时字节仍在 daemon buffer，还要写进 Guest 页。')
    ) `
    '把「领取完成」当「IO 完成」；把 FETCH 与普通 READ 的 CQE 混为一谈。' `
    '缓存命中时，这条链上有哪几步可以完全跳过？' `
    '凡是 CQE/回调/事件，先问它对应哪条命令。' `
    { param($g, $x, $y, $w, $h) fig_example $g $x $y $w $h '题目' 'FETCH 的 CQE 到了，能否说 4 KiB 已从盘上读到？给出判据。' } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('阶段', '已取字节', '在哪') @(@('FETCH CQE 到', '否', '—'), @('daemon COMMIT', '是', 'daemon buffer'), @('used 发布', '是', 'Guest 页'), @('read() 返回', '是', '用户 buffer')) 30 } `
    21
}

$pages += {
  param($g)
  ContentPage $g '03 例题' @(
    @{t = '这题考「作用对象」：'; c = $C.ink; bold = $false },
    @{t = 'Guest 里的 root 会被 seccomp 拦住吗'; c = $C.green; bold = $true }) `
    '机制作用在谁身上，决定了它能不能回答这道题' 3 `
    @(
      @('题面与已知', 'seccomp 白名单装在 firecracker 的线程上（vmm 60 / api 35 / vcpu 43）；Guest 有独立内核。'),
      @('步骤1：syscall 由谁处理', 'Guest 内 syscall 进入 Guest 内核，由 Guest 内核服务例程处理；它根本没发出宿主 syscall，seccomp 无从拦截。'),
      @('步骤2：seccomp 拦的是谁', '它拦的是 firecracker 自己发出的宿主 syscall（open/mmap/ioctl）；防的是「VMM 被攻破之后」的破坏力。'),
      @('步骤3：那 fork bomb 靠什么', 'Guest 内核的 pid_max/RLIMIT_NPROC；宿主侧 memory.max（OOM 杀整台 VM）、cpu.max、vCPU 数。pids.max 无效。')
    ) `
    '把 seccomp 当「给 Guest 用的沙箱」；把 namespace 里的 root 当已无特权。' `
    '谁能拦住 Guest 里的 fork bomb？两个控制点各说一个管不到的维度。' `
    '每题先问：这个机制作用在哪个对象上。' `
    { param($g, $x, $y, $w, $h) fig_example $g $x $y $w $h '题目' 'Guest root 执行任意 syscall，会被 FC 的 seccomp 拦住吗？' } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('对象', '谁在限制', '失效场景') @(@('Guest 进程', 'Guest 内核', 'Guest 内核漏洞'), @('FC 线程', 'seccomp/caps', '白名单内滥用'), @('整台 VM', 'cgroup/balloon', '配额未配置')) 30 } `
    22
}

$pages += {
  param($g)
  ContentPage $g '03 例题' @(
    @{t = '六个高频错答：'; c = $C.ink; bold = $false },
    @{t = '错在哪一句，正确怎么说'; c = $C.red; bold = $true }) `
    '六条错答共同病根：把「某层完成」当「整件事完成」' 3 `
    @(
      @('pids.max 挡 Guest fork', '错在对象：pids 控制器数宿主 task；Guest 进程不是 task。兜底是 memory.max（OOM 杀整台 VM）、cpu.max、vCPU 数。'),
      @('VM-Exit = KVM_RUN 返回', '错在边界：KVM 能处理的退出直接重入，ioctl 从未返回；只有 MMIO/PIO 这类才回用户态。'),
      @('namespace = 降权', '错在语义：namespace 只改「看见什么」；ns 里的 root 仍是 root，要降权得 uid/gid + drop caps。'),
      @('finalize+rename = 持久化', '错在完成点：finalize 只保证格式完成，rename 只换名字；断电安全要 fsync，还要 manifest 与父层引用一起发布。')
    ) `
    '这六条都能「听起来很顺」，因为都省略了「哪一层/哪一步」。' `
    '用自己的话重讲第 1、2 条，各加一个数字或 file:line。' `
    '看到「等于/挡住」先问它管的是哪一层。' `
    { param($g, $x, $y, $w, $h) fig_mistakes $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('层完成当整体', 3, '3 条'), @('视野当权限', 2, '2 条'), @('其他', 1, '1 条')) 3 $C.red } `
    23
}

# ============ 04 总结 ============
$pages += {
  param($g)
  ContentPage $g '04 总结' @(
    @{t = '记住 5 个数字'; c = $C.ink; bold = $false },
    @{t = '＋一条主线'; c = $C.green; bold = $true }) `
    '面试里数字比形容词可信，但数字必须带口径' 4 `
    @(
      @('16 字节', '一个 VirtIO 描述符：addr 8B + len 4B + flags 2B + next 2B。口径：split virtqueue 规范。'),
      @('1 秒', 'health 单次探测上限；判定是「非 4xx/5xx」，不校验 body。'),
      @('4 KiB / 512 B', '页与块常用 4 KiB；与 512 B 扇区差 8 倍（8 MiB → 16384 vs 2048）；转换函数校验 page_size=4096。'),
      @('60 / 35 / 43', 'seccomp 三组白名单条数（vmm/api/vcpu），default_action=trap，BPF_MAX_LEN=4096。口径：FC 1.12.1 默认值。')
    ) `
    '数字不给口径；把上游默认值当部署值。' `
    '这 5 个数字分别落在哪一层？哪个最容易被追问「你的版本是多少」？' `
    '只记三件事：三个执行环境、每层完成点、暂停≠快照≠恢复。' `
    { param($g, $x, $y, $w, $h) fig_numcards $g $x $y $w $h @(@('16', '字节', 'VirtIO 描述符'), @('1', '秒', 'health 单次上限'), @('4', 'KiB', '页与块粒度'), @('60/35/43', '条', 'seccomp 白名单'), @('3', '个', '暂停完成点')) } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('数字', '口径', '出处') @(@('16 字节', 'split virtqueue 描述符', 'virtio 规范'), @('1 秒', 'health 单次探测', 'envd.rs:27'), @('60/35/43', '上游默认过滤器', 'FC 1.12.1 seccomp json'), @('3 个', '暂停完成点', '本讲第 16 页')) 26 } `
    24
}

$pages += {
  param($g)
  ContentPage $g '04 总结' @(
    @{t = '3 道练习题：'; c = $C.ink; bold = $false },
    @{t = '答案在第 27 页'; c = $C.green; bold = $true }) `
    '先自己写，再翻答案；每题写三行也算完成' 4 `
    @(
      @('基础', '配 2 个 vCPU 的 VM，宿主上这台 firecracker 至少几个线程、分别负责什么？Barrier 为什么是 vcpu_count+1？'),
      @('进阶', '一次 4 KiB 读，Guest 页缓存命中。还会发生 virtio 队列请求吗？如果发生，最可能来自哪几个动作？'),
      @('易错', '同事说「快照失败是因为 pause 没成功」。你怎么判断？指出两个必须分别检查的完成点与观测手段。'),
      @('作答要求', '每题三行：结论 / 机制 / 一个可验证的观测。写不出来就说明对应那页没吃透。')
    ) `
    '直接翻答案；答案是「知道」，自己写才算「会」。' `
    '三题各写三行，能否 10 分钟内写完？' `
    '写不出来的地方，就是你下一轮要复的页。' `
    { param($g, $x, $y, $w, $h) fig_threeq $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('题', '考查点', '对应页') @(@('基础', '线程数 / barrier', 'P06'), @('进阶', '缓存命中与 IO', 'P11'), @('易错', '完成点定位', 'P16/P15')) 30 } `
    25
}

$pages += {
  param($g)
  ContentPage $g '04 总结' @(
    @{t = '必须会 5 条'; c = $C.ink; bold = $false },
    @{t = '＋如果只记三件事'; c = $C.green; bold = $true }) `
    '能讲、能画、能量：三样齐了才算会' 4 `
    @(
      @('① 三个执行环境', '宿主 3 进程 + 内核功能 + Guest；宿主 ps 看不到 Guest 进程。'),
      @('② 四条地址线', 'GVA/GPA/HVA/HPA + process_vm_readv 四参数归属 + HVA 偏移公式。'),
      @('③ KVM_RUN 循环', '退出 ≠ 返回；退出次数/唤醒次数/线程切换三个指标不可混。'),
      @('④ 快照与恢复', '四件套 + 暂停三完成点 + 按需缺页（共享只读设备 + MAP_PRIVATE COW）。')
    ) `
    '把「背下 5 条」当「会讲」——每条都要能配一个数字或一次实测。' `
    '这 5 条里你现在能立刻给出证据的是哪几条？缺的怎么补？' `
    '能讲、能画、能量。' `
    { param($g, $x, $y, $w, $h) fig_numcards $g $x $y $w $h @(@('28', '课', '已覆盖'), @('0', '验收', '独立验收 0/28'), @('3', '件事', '如果只记三件'), @('5', '条', '必须会'), @('2', '点', '待补证据')) } `
    { param($g, $x, $y, $w, $h) data_bars $g $x $y $w $h @(@('课程覆盖', 28, '28/28'), @('独立验收', 0, '0/28')) 28 $C.green } `
    26
}

$pages += {
  param($g)
  ContentPage $g '04 总结' @(
    @{t = '考前 10 分钟看这一页：'; c = $C.ink; bold = $false },
    @{t = '术语 + 易混 + 答案'; c = $C.green; bold = $true }) `
    '附录只对齐口径，不解释原理' 4 `
    @(
      @('术语 7 条', 'GPA（Guest 物理）、HVA（某进程虚拟）、memslot（GPA↔HVA 登记）、VM-Exit、vCPU、rootfs、ublk。'),
      @('易混 8 对', 'VM-Exit≠返回 / 暂停≠快照 / 领取≠读完 / 文件偏移≠磁盘偏移 / 映射≠分配 / 只读≠不共享页缓存 / ns≠降权 / health≠鉴权。'),
      @('练习答案', '① 至少 4 线程；Barrier 的 +1 是主线程。② 通常不发 virtio 请求，但路径/元数据/预读仍可能产生 IO。③ 查全部 vCPU 确认 + 内存层/状态文件 fsync。'),
      @('口径声明', '60/35/43、BPF_MAX_LEN=4096、16 字节描述符来自 FC 1.12.1 与 virtio 规范；性能数字未实测，不写毫秒。')
    ) `
    '把「以教材/老师口径为准」当废话——版本不同，白名单条数与映射标志都可能变。' `
    '这 8 对易混你能各说一句区别吗？说不出的那对回哪一页？' `
    '附录只对齐口径，不解释原理。' `
    { param($g, $x, $y, $w, $h) fig_threecols $g $x $y $w $h } `
    { param($g, $x, $y, $w, $h) data_table $g $x $y $w $h @('易混 A', '易混 B', '一句话区别') @(@('VM-Exit', 'KVM_RUN 返回', '硬件退出 vs ioctl 返回'), @('暂停完成', '快照完成', '停止 vs 落盘'), @('领取完成', '数据读完', '交付 vs 取字节'), @('只读设备', '不共享页缓存', '只读讲可写性，映射讲共享')) 26 } `
    27
}

# ---------------- 渲染 ----------------
$i = 0
foreach ($p in $pages) {
  $i++
  $name = 'p{0:d2}.png' -f $i
  $path = Join-Path $OUT $name
  $pg = NewPage $path
  try { & $p $pg.g } catch { Note ("PAGE {0} 失败: {1}`n{2}" -f $i, $_.Exception.Message, $_.ScriptStackTrace) }
  SavePage $pg
  Note ("saved {0}" -f $name)
}
Note ("total: {0} pages, out: {1}" -f $i, $OUT)
