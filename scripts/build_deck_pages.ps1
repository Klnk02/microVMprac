#requires -Version 5.1
<#
  AgentENV 复习课件（30 页）—— 页面内容与绘制
  依赖 deck_core.ps1（画布、色板、T/Rect/L/Dot/Arrow/Seg/Nav/Header/Footer/Card）
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'deck_core.ps1')

$TOTAL = 30

# ---------- 通用小部件 ----------
function Chip {
  param($g, [double]$x, [double]$y, $text, [string]$fg, [string]$bg, [double]$w = 0, [double]$h = 24)
  $f = Font2 11.5 $true
  if ($w -le 0) { $w = $g.MeasureString($text, $f).Width + 22 }
  $f.Dispose()
  Rect $g $x $y $w $h $bg $fg 1 12
  $ff = Font2 11.5 $true; $b = Brush $fg
  $tw = $g.MeasureString($text, $ff).Width
  $g.DrawString($text, $ff, $b, [single]($x + ($w - $tw) / 2), [single]($y + 5))
  $ff.Dispose(); $b.Dispose()
  return $w
}

function StepCard {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h, [string]$num, [string]$title, [string]$detail, [string]$accent)
  Rect $g $x $y $w $h '#FFFFFF' $C.line 1 10
  Rect $g $x $y $w 5 $accent $null 0 2
  $f = Font2 20 $true; $b = Brush $accent
  $g.DrawString($num, $f, $b, [single]($x + 16), [single]($y + 14)); $f.Dispose(); $b.Dispose()
  T $g $title ($x + 16) ($y + 46) 12.5 $C.ink $true ($w - 30) | Out-Null
  T $g $detail ($x + 16) ($y + 74) 11.5 $C.body $false ($w - 30) | Out-Null
}

function KV {
  param($g, [double]$x, [double]$y, [double]$w, [string]$k, [string]$v, [string]$accent = '#047761')
  $kw = T $g $k $x $y 12 $accent $true 120
  T $g $v ($x + 132) $y 12 $C.body $false ($w - 132) | Out-Null
}

# ================= 页面 =================
$pages = @()

# ---- 01 封面 ----
$pages += {
  param($g)
  Header $g '01 总览' @(@{t='AgentENV 沙箱：';c=$C.ink;bold=$false}, @{t='一条链把它讲清';c=$C.green;bold=$true}) '28 讲压缩成 30 页：先结构、再机制、最后能自己复述' 1
  # 左：目标
  T $g '本讲目标' $M 232 12.5 $C.ink $true 300 | Out-Null
  $items = @('能画出三个执行环境与五条链路', '能说出每个动作的「完成点」在哪一层', '面试时用四段式讲清任意一个机制')
  $yy = 260
  foreach ($it in $items) { Dot $g $M ($yy + 6) 6 $C.green; T $g $it ($M + 16) $yy 12.5 $C.body $false 560 | Out-Null; $yy += 32 }
  # 浅绿结论横幅
  Rect $g $M 380 700 56 $C.greenBg1 $C.green 1 10
  T $g '一句话记住：所有问题的答案都落在「谁在哪一层、这一步算完成了吗」。' ($M + 18) 396 12.5 $C.green $true 664 | Out-Null
  # 右：一页看懂
  Rect $g 800 232 744 420 '#FFFFFF' $C.line 1 12
  T $g '一页看懂' 824 250 13 $C.ink $true 300 | Out-Null
  $kws = @('三个执行环境', '五条链路', '一个完成点思维')
  $yy = 282
  foreach ($k in $kws) { Chip $g 824 $yy $k $C.green $C.greenBg1 | Out-Null; $yy += 34 }
  # 迷你地图
  $mx = 824; $my = 400
  T $g '迷你知识地图' $mx $my 11.5 $C.dim $false 300 | Out-Null
  $blocks = @(@('位置',''), @('执行',''), @('存储',''), @('状态',''))
  $bx = $mx; $by = $my + 26
  for ($i = 0; $i -lt 4; $i++) {
    Rect $g $bx $by 110 42 '#FFFFFF' $C.line 1 8
    T $g $blocks[$i][0] $bx $by 12 $C.ink $true 110 'center' | Out-Null
    if ($i -lt 3) { Arrow $g ($bx + 112) ($by + 21) ($bx + 140) ($by + 21) $C.arrow 1.2 }
    $bx += 148
  }
  Arrow $g ($mx + 41) ($by + 46) ($mx + 41) ($by + 74) $C.arrow 1.2
  Rect $g $mx ($by + 78) 552 40 $C.greenBg2 $C.green 1 8
  T $g '平台层：资源回收 / 并发 / 失败恢复 / 度量 / 池化' ($mx + 12) ($by + 86) 11.5 $C.green $true 530 | Out-Null
  # 底部章节链
  $chain = @(@('01 总览','知道要学什么'), @('02 概念','讲得出机制'), @('03 例题','答得对追问'), @('04 总结','考前能自测'))
  $cx = $M; $cy = 700
  for ($i = 0; $i -lt 4; $i++) {
    Rect $g $cx $cy 340 74 '#FFFFFF' $C.line 1 10
    T $g $chain[$i][0] ($cx + 16) ($cy + 12) 12.5 $C.green $true 300 | Out-Null
    T $g $chain[$i][1] ($cx + 16) ($cy + 38) 11.5 $C.body $false 300 | Out-Null
    if ($i -lt 3) { Arrow $g ($cx + 344) ($cy + 37) ($cx + 386) ($cy + 37) $C.arrow 1.4 }
    $cx += 392
  }
  Footer $g '白底扁平 · 固定色板 · 所有结论都标注完成点' 1 $TOTAL
}

# ---- 02 知识地图 ----
$pages += {
  param($g)
  Header $g '01 总览' @(@{t='先建立结构，';c=$C.ink;bold=$false}, @{t='再记细节';c=$C.green;bold=$true}) '六个模块按依赖顺序排列：前一个不懂，后一个必错' 1
  $mods = @(
    @('位置', '三个执行环境是谁', '先学', $C.green),
    @('地址', 'GVA/GPA/HVA/HPA', '先学', $C.green),
    @('执行', 'KVM_RUN 与 VM-Exit', '后学', $C.orange),
    @('存储', '文件 → 块 → 层', '后学', $C.orange),
    @('状态', '快照与恢复', '易混', $C.red),
    @('平台', '资源 / 并发 / 度量', '易混', $C.red)
  )
  $x = $M; $y = 250; $bw = 226; $bh = 152
  for ($i = 0; $i -lt 6; $i++) {
    $mod = $mods[$i]
    Rect $g $x $y $bw $bh '#FFFFFF' $C.line 1 12
    Rect $g $x $y 5 $bh $mod[3] $null 0 2
    T $g $mod[0] ($x + 18) ($y + 16) 20 $C.ink $true 180 | Out-Null
    T $g $mod[1] ($x + 18) ($y + 60) 11.5 $C.body $false 190 | Out-Null
    Chip $g ($x + 18) ($y + 104) $mod[2] $mod[3] $C.grayBg 60 24 | Out-Null
    if ($i -lt 5) { Arrow $g ($x + $bw + 4) ($y + 76) ($x + $bw + 26) ($y + 76) $C.arrow 1.4 }
    $x += $bw + 30
  }
  Rect $g $M 430 1488 120 $C.greenBg1 $C.green 1 10
  T $g '学习顺序不是课本顺序：位置和地址是地基，跳过它们去看快照，只会看到一堆名词。' ($M + 20) 448 12.5 $C.green $true 1440 | Out-Null
  T $g '易混提示' $M 480 12.5 $C.red $true 200 | Out-Null
  T $g '「状态」与「平台」最容易被当成背记内容，其实它们的每个结论都要能落到一个完成点或一个数字上。' ($M + 110) 478 12 $C.body $false 1300 | Out-Null
  # 底部结论
  Rect $g $M 680 1488 96 $C.grayBg $null 0 10
  T $g '先建立结构，再记细节。' ($M + 20) 700 22 $C.ink $true 400 | Out-Null
  T $g '结构＝谁在哪一层；细节＝这一层的完成点是什么。' ($M + 20) 736 12 $C.body $false 900 | Out-Null
  Footer $g '顺序：位置 → 地址 → 执行 → 存储 → 状态 → 平台' 2 $TOTAL
}

# ---- 03 章节总览 ----
$pages += {
  param($g)
  Header $g '01 总览' @(@{t='本讲只回答';c=$C.ink;bold=$false}, @{t='5 个问题';c=$C.green;bold=$true}, @{t='，其中 3 个是高频考点';c=$C.ink;bold=$false}) '每个问题对应后面的一页，重要度按面试出现频率排' 1
  $qs = @(
    @('沙箱里的「进程」到底在谁那边？', '高频', $C.red),
    @('一个请求从哪进、到哪一层算完成？', '高频', $C.red),
    @('快照为什么要先暂停，暂停就等于快照吗？', '高频', $C.red),
    @('namespace / cgroup / seccomp 各挡什么？', '理解', $C.orange),
    @('恢复后为什么网络可能不通？', '了解', $C.dim)
  )
  $y = 236
  foreach ($q in $qs) {
    Rect $g $M $y 940 62 '#FFFFFF' $C.line 1 10
    Dot $g ($M + 16) ($y + 27) 8 $q[2]
    T $g $q[0] ($M + 36) ($y + 20) 12.5 $C.ink $false 700 | Out-Null
    Chip $g ($M + 800) ($y + 19) $q[1] $q[2] $C.grayBg 70 24 | Out-Null
    $y += 76
  }
  # 右侧：常见问法
  Rect $g 1040 232 504 400 '#FFFFFF' $C.line 1 12
  T $g '考试 / 面试常见问法' 1064 250 13 $C.ink $true 460 | Out-Null
  $asks = @(
    '「宿主 ps 能看到 Guest 里的 python 吗？」',
    '「这次 read 到哪一步算完成？」',
    '「暂停成功能不能说快照成功了？」',
    '「Guest 里的 root 会被 seccomp 拦住吗？」'
  )
  $yy = 286
  foreach ($a in $asks) { Dot $g 1064 ($yy + 7) 6 $C.green; T $g $a 1082 $yy 11.5 $C.body $false 440 | Out-Null; $yy += 62 }
  Footer $g '3 个高频点先过一遍，再回来看细节' 3 $TOTAL
}

# ---- 04 三层执行环境 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='一台机器三个执行环境：';c=$C.ink;bold=$false}, @{t='只有 Guest 有独立内核';c=$C.green;bold=$true}) '分清这三层，后面每个问题的位置就都不会答错' 2
  $rows = @(
    @('宿主用户态', @('AgentENV server  生命周期 / 快照 / 控制', 'Firecracker  VMM：vCPU 线程 + 设备模型', 'ublk-daemon  块设备服务（集中式）'), $C.green),
    @('宿主内核', @('KVM  运行 vCPU、维护 EPT', 'ublk 驱动  /dev/ublkbN 请求队列', 'cgroup / seccomp  约束 VMM'), $C.orange),
    @('Guest', @('Guest 内核  自己的页表与进程表', 'envd  执行命令、回传输出', '你的程序  PID 由 Guest 内核分配'), $C.red)
  )
  $y = 240
  foreach ($r in $rows) {
    Rect $g $M $y 1488 150 '#FFFFFF' $C.line 1 12
    Rect $g $M $y 5 150 $r[2] $null 0 2
    T $g $r[0] ($M + 20) ($y + 20) 20 $C.ink $true 200 | Out-Null
    $col = @($C.green, $C.orange, $C.red)
    for ($i = 0; $i -lt 3; $i++) {
      $bx = $M + 200 + $i * 428
      Rect $g $bx ($y + 26) 400 98 $C.grayBg $null 0 8
      T $g $r[1][$i] ($bx + 14) ($y + 46) 11.5 $C.body $false 372 | Out-Null
    }
    $y += 164
  }
  T $g '关键：Guest 里的程序不是 firecracker 的子进程，宿主 ps 看不到它；KVM / ublk 驱动是内核功能，没有自己的 PID。' $M 740 12.5 $C.green $true 1488 | Out-Null
  Footer $g '位置题答错，后面全错——先问「这个对象在哪一层」' 4 $TOTAL
}

# ---- 05 四把尺子 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='一个变量四个地址：';c=$C.ink;bold=$false}, @{t='GVA/GPA 属 Guest，HVA 属某个进程';c=$C.green;bold=$true}) '同一个数字在不同地址空间里指向不同物理页' 2
  # 左：定义
  $defs = @(
    @('GVA  客户机虚拟地址', 'Guest 程序用的地址，经 Guest 页表翻译'),
    @('GPA  客户机物理地址', 'Guest 以为的物理地址，经 EPT 再翻一次'),
    @('HVA  宿主机虚拟地址', '必须说明属于哪个进程，如 firecracker'),
    @('HPA  宿主物理地址', '真正的内存条位置，只有一个')
  )
  $y = 240
  foreach ($d in $defs) {
    Rect $g $M $y 700 66 '#FFFFFF' $C.line 1 10
    T $g $d[0] ($M + 16) ($y + 12) 12.5 $C.ink $true 660 | Out-Null
    T $g $d[1] ($M + 16) ($y + 36) 11.5 $C.body $false 660 | Out-Null
    $y += 78
  }
  # 右：双路径
  $rx = 800; $ry = 250
  Rect $g $rx $ry 744 316 '#FFFFFF' $C.line 1 12
  T $g '两条访存路径，落到同一块物理页' ($rx + 20) ($ry + 16) 12.5 $C.ink $true 700 | Out-Null
  Rect $g ($rx + 40) ($ry + 60) 120 44 '#FFFFFF' $C.green 1.5 8
  T $g 'GVA' ($rx + 40) ($ry + 70) 12.5 $C.green $true 120 'center' | Out-Null
  Rect $g ($rx + 40) ($ry + 132) 120 44 '#FFFFFF' $C.green 1.5 8
  T $g 'GPA' ($rx + 40) ($ry + 142) 12.5 $C.green $true 120 'center' | Out-Null
  Rect $g ($rx + 300) ($ry + 96) 140 48 $C.greenBg1 $C.green 1.5 8
  T $g 'HPA' ($rx + 300) ($ry + 108) 13 $C.green $true 140 'center' | Out-Null
  Arrow $g ($rx + 162) ($ry + 82) ($rx + 162) ($ry + 130) $C.arrow 1.4
  Arrow $g ($rx + 162) ($ry + 154) ($rx + 296) ($ry + 120) $C.arrow 1.4
  T $g '页表 + EPT' ($rx + 176) ($ry + 120) 11.5 $C.dim $false 120 | Out-Null
  Rect $g ($rx + 560) ($ry + 60) 120 44 '#FFFFFF' $C.orange 1.5 8
  T $g 'HVA' ($rx + 560) ($ry + 70) 12.5 $C.orangeDk $true 120 'center' | Out-Null
  Arrow $g ($rx + 556) ($ry + 84) ($rx + 442) ($ry + 116) $C.arrow 1.4
  T $g '宿主页表' ($rx + 450) ($ry + 60) 11.5 $C.dim $false 110 | Out-Null
  # 记忆句
  Rect $g $M 592 1488 168 $C.greenBg1 $C.green 1 12
  T $g '一句话记忆' ($M + 22) 610 12.5 $C.green $true 300 | Out-Null
  T $g '地址是名字，进程是语境：同一个名字在不同语境里指向不同东西，所以接口必须显式带上 pid。' ($M + 22) 636 12.5 $C.body $false 1440 | Out-Null
  T $g '反例：server 拿到 Firecracker 的 0x400000 直接 pwrite，写进去的是 server 自己的页，不是 Guest 的内存。' ($M + 22) 676 12 $C.red $false 1440 | Out-Null
  Footer $g '看到地址先问「谁的地址空间」，看到 HVA 先问「哪个进程的」' 5 $TOTAL
}

# ---- 06 三个切换 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='三个「切换」不是一回事：';c=$C.ink;bold=$false}, @{t='只有线程切换才是没拿到 CPU';c=$C.green;bold=$true}) 'KVM_RUN、VM-Exit、线程切换，混了就解释不了性能' 2
  $cols = @(300, 460, 300, 428)
  $hdr = @('动作', '发生了什么', '是否切宿主线程', '典型误判')
  $rows = @(
    @('KVM_RUN 系统调用', '用户态 → 内核，换特权级', '否', '以为这是「进入 Guest 了」'),
    @('VM-Entry / VM-Exit', 'Guest ↔ 宿主执行环境切换', '否', '以为每次都回到用户态'),
    @('宿主线程切换', '调度器把 CPU 给别的线程', '是', '把调度延迟算成虚拟化开销')
  )
  $x = $M; $y = 246
  for ($i = 0; $i -lt 4; $i++) { Rect $g $x $y $cols[$i] 46 $C.grayBg $C.line 1 8; T $g $hdr[$i] ($x + 12) ($y + 13) 12.5 $C.ink $true ($cols[$i] - 24) | Out-Null; $x += $cols[$i] }
  $y += 46
  for ($r = 0; $r -lt 3; $r++) {
    $x = $M
    $bg = if ($r % 2 -eq 0) { '#FFFFFF' } else { $C.greenBg2 }
    for ($i = 0; $i -lt 4; $i++) {
      Rect $g $x $y $cols[$i] 58 $bg $C.line 1 0
      $col = if ($i -eq 2) { if ($rows[$r][2] -eq '是') { $C.red } else { $C.green } } elseif ($i -eq 3) { $C.body } else { $C.ink }
      $bold = ($i -eq 2)
      T $g $rows[$r][$i] ($x + 12) ($y + 18) 12 $col $bold ($cols[$i] - 24) | Out-Null
      $x += $cols[$i]
    }
    $y += 58
  }
  # 结论卡
  Rect $g $M 470 1488 92 $C.orangeBg $C.orange 1 12
  T $g '最容易错的一步：把 VM-Exit 当成「KVM_RUN 已返回」。' ($M + 20) 486 12.5 $C.orangeDk $true 1400 | Out-Null
  T $g 'KVM 能处理的退出（例如补一条 EPT 映射）会处理完直接重入 Guest，整个 ioctl 从头到尾没返回过。' ($M + 20) 516 12 $C.body $false 1400 | Out-Null
  Rect $g $M 590 1488 148 '#FFFFFF' $C.line 1 12
  T $g '为什么重要' ($M + 20) 606 12.5 $C.ink $true 300 | Out-Null
  T $g '「虚拟机慢」要分三件事：退出次数太多（设备模型重）、线程被抢（超订）、IO 等待（缺页/后端慢）。' ($M + 20) 632 12 $C.body $false 1440 | Out-Null
  T $g '把三者混成一个「虚拟化开销」，就没法定位，也做不了优化。' ($M + 20) 664 12 $C.body $false 1440 | Out-Null
  Footer $g '看到「慢」先分类：退出 / 调度 / IO' 6 $TOTAL
}

# ---- 07 vCPU 与线程 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='一个 vCPU 就是一个线程：';c=$C.ink;bold=$false}, @{t='多线程是为了能接住控制请求';c=$C.green;bold=$true}) '不是性能优化，而是避免 Guest 卡住时宿主无从下手' 2
  # 左：进程框
  Rect $g $M 240 740 380 '#FFFFFF' $C.green 1.5 12
  T $g 'firecracker（宿主进程，一个地址空间）' ($M + 20) 258 12.5 $C.green $true 700 | Out-Null
  $th = @(@('vmm 主线程', '协调状态 / 处理设备事件'), @('api 线程', 'Unix socket 收控制请求'),
          @('fc_vcpu 0', 'ioctl(KVM_RUN) 跑 Guest'), @('fc_vcpu 1', 'ioctl(KVM_RUN) 跑 Guest'))
  $yy = 294
  foreach ($t in $th) {
    Rect $g ($M + 20) $yy 700 66 '#FFFFFF' $C.line 1 8
    T $g $t[0] ($M + 36) ($yy + 12) 12.5 $C.ink $true 300 | Out-Null
    T $g $t[1] ($M + 36) ($yy + 36) 11.5 $C.body $false 640 | Out-Null
    $yy += 76
  }
  # 右：解释
  $rx = 840
  Card $g $rx 240 704 120 $C.green '为什么不是一个线程' 'vCPU 卡在 KVM_RUN 里跑 Guest 时，同一线程无法同时处理「请暂停」的请求，单线程 VMM 会死锁。'
  Card $g $rx 376 704 120 $C.orange '线程名是代码写死的' '.name("fc_vcpu {i}")，所以宿主 ps -eLf 才能看到这个名字；不写就只有默认名。' $null $C.orangeDk
  Card $g $rx 512 704 108 $C.red '常见误判' '以为 vCPU 线程在 KVM_RUN 里就是「睡着了」：物理 CPU 可能正在它上面执行 Guest，占用率照样高。'
  T $g '代价：线程数 = 1（vmm）+ 1（api）+ N（vCPU），seccomp 白名单与 cgroup 记账都按这个粒度生效。' $M 660 12 $C.body $false 1488 | Out-Null
  Footer $g '配 4 个 vCPU，宿主就多 4 个线程，外加 vmm 与 api' 7 $TOTAL
}

# ---- 08 控制面与数据面 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='控制面走 socket，数据面走队列：';c=$C.ink;bold=$false}, @{t='HTTP 只是消息格式';c=$C.green;bold=$true}) '两条通道的故障表现完全不同，混了就排不了障' 2
  $x1 = $M; $x2 = 820
  Rect $g $x1 240 680 200 '#FFFFFF' $C.green 1.5 12
  T $g '控制面' ($x1 + 20) 258 20 $C.green $true 200 | Out-Null
  T $g 'server ↔ firecracker（--api-sock，宿主 Unix socket）' ($x1 + 20) 294 12.5 $C.ink $false 640 | Out-Null
  T $g '消息：PATCH /vm { state: Paused }、PUT /snapshot/load' ($x1 + 20) 324 12 $C.body $false 640 | Out-Null
  T $g '特点：不需要 Guest 配合；Guest 卡死也能停' ($x1 + 20) 356 12 $C.green $false 640 | Out-Null
  Rect $g $x2 240 680 200 '#FFFFFF' $C.orange 1.5 12
  T $g '数据面' ($x2 + 20) 258 20 $C.orangeDk $true 200 | Out-Null
  T $g 'Guest 驱动 ↔ 设备后端（Guest RAM 里的 virtqueue）' ($x2 + 20) 294 12.5 $C.ink $false 640 | Out-Null
  T $g '消息：描述符 + avail 环 + used 环 + 通知' ($x2 + 20) 324 12 $C.body $false 640 | Out-Null
  T $g '特点：需要 Guest 驱动参与；Guest 卡死就停不了' ($x2 + 20) 356 12 $C.orangeDk $false 640 | Out-Null
  # 故障对照
  $cols = @(300, 620, 568)
  $x = $M; $y = 470
  $hdr = @('如果坏的是', '现象', '你该先查')
  for ($i = 0; $i -lt 3; $i++) { Rect $g $x $y $cols[$i] 44 $C.grayBg $C.line 1 8; T $g $hdr[$i] ($x + 12) ($y + 12) 12.5 $C.ink $true ($cols[$i] - 24) | Out-Null; $x += $cols[$i] }
  $y += 44
  $rows = @(@('控制面', 'Host 不能暂停 / 快照，但 Guest 照常跑', 'socket 路径、FC 进程是否在'),
            @('数据面', 'Guest 内部 IO 卡住，Host 仍能控制', 'virtqueue、后端设备、daemon'))
  for ($r = 0; $r -lt 2; $r++) {
    $x = $M
    for ($i = 0; $i -lt 3; $i++) {
      Rect $g $x $y $cols[$i] 54 $(if ($r % 2 -eq 0) { '#FFFFFF' } else { $C.greenBg2 }) $C.line 1 0
      T $g $rows[$r][$i] ($x + 12) ($y + 16) 12 $(if ($i -eq 0) { $C.ink } else { $C.body }) ($i -eq 0) ($cols[$i] - 24) | Out-Null
      $x += $cols[$i]
    }
    $y += 54
  }
  Rect $g $M 600 1488 140 $C.greenBg1 $C.green 1 12
  T $g '超时有三种可能' ($M + 20) 616 12.5 $C.green $true 300 | Out-Null
  T $g '① 请求根本没送到　② 已经执行成功但响应丢了　③ 还在执行中' ($M + 20) 644 12.5 $C.ink $false 1400 | Out-Null
  T $g '所以「超时」不能直接推出「VM 还在跑」，也不能推出「操作失败」。' ($M + 20) 676 12 $C.body $false 1400 | Out-Null
  Footer $g '看到 socket 先想「宿主之间」，看到 virtqueue 先想「Guest 参与」' 8 $TOTAL
}

# ---- 09 VirtIO ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='队列在内存里，通知只提醒：';c=$C.ink;bold=$false}, @{t='描述符不搬字节';c=$C.green;bold=$true}) '设备不是「收到包」，而是「去共享队列取一条描述」' 2
  # 三件套
  Rect $g $M 240 470 180 '#FFFFFF' $C.green 1.5 12
  T $g '① 描述符表' ($M + 18) 258 12.5 $C.green $true 300 | Out-Null
  T $g '16 字节/项：addr / len / flags / next。可串成链，描述多块不连续缓冲区。' ($M + 18) 288 11.5 $C.body $false 430 | Out-Null
  Rect $g $M 436 470 180 '#FFFFFF' $C.green 1.5 12
  T $g '② 可用环 avail' ($M + 18) 454 12.5 $C.green $true 300 | Out-Null
  T $g 'Guest 把「链头编号」发布出去，表示这批缓冲区可以给设备用。' ($M + 18) 484 11.5 $C.body $false 430 | Out-Null
  Rect $g 560 240 470 180 '#FFFFFF' $C.orange 1.5 12
  T $g '③ 已用环 used' (578) 258 12.5 $C.orangeDk $true 300 | Out-Null
  T $g '设备发布完成项与实际写入长度；Guest 处理完后才会再次发布缓冲。' (578) 288 11.5 $C.body $false 430 | Out-Null
  Arrow $g 532 330 554 330 $C.arrow 1.4
  # 右侧说明
  Rect $g 1060 240 484 180 $C.greenBg1 $C.green 1 12
  T $g '通知（doorbell）' 1080 258 12.5 $C.green $true 300 | Out-Null
  T $g '只提醒「去检查队列」：不带包内容；一次通知可对应多项工作。所以通知次数 ≠ 请求数。' 1080 288 11.5 $C.body $false 444 | Out-Null
  # 流程
  T $g '一次收包的四个动作' $M 452 12.5 $C.ink $true 400 | Out-Null
  $steps = @(@('准备缓冲', '描述符指向 Guest RAM'), @('发布 avail', '写链头编号'), @('设备写数据', '发布 used'), @('Guest 处理', '交回缓冲'))
  $x = $M; $y = 482
  for ($i = 0; $i -lt 4; $i++) {
    StepCard $g $x $y 340 110 ([string]($i + 1)) $steps[$i][0] $steps[$i][1] $C.green
    if ($i -lt 3) { Arrow $g ($x + 344) ($y + 55) ($x + 384) ($y + 55) $C.arrow 1.4 }
    $x += 388
  }
  Rect $g $M 620 1488 120 $C.redBg $C.red 1 12
  T $g '最容易错的一步：把「设备发布 used」当成「Guest 已处理」。' ($M + 20) 636 12.5 $C.red $true 1400 | Out-Null
  T $g '中间还差一次中断注入与线程调度；Guest 未处理完就把缓冲再发布，设备可能覆盖你还要读的内容。' ($M + 20) 666 12 $C.body $false 1400 | Out-Null
  Footer $g 'VirtIO 省掉的是「每个寄存器一次 VM-Exit」，不是数据本身' 9 $TOTAL
}

# ---- 10 三层就绪 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='三层就绪，一层比一层强：';c=$C.ink;bold=$false}, @{t='最后一层才代表能干活';c=$C.green;bold=$true}) '「进程在」「端口通」「服务能应答」是三件不同强度的事' 2
  $tiers = @(@('①  API socket 可用', '能配 VM、能暂停', '证明 VMM 起来了、socket 路径对', 1030),
             @('②  网络可达', '宿主经 tap0 能到 Guest', '证明 netns、网卡、IP、端口都对', 880),
             @('③  envd /health 通过', '应用层能应答', '证明服务真能处理请求', 730))
  $y = 244
  foreach ($t in $tiers) {
    Rect $g $M $y $t[3] 86 '#FFFFFF' $C.green 1.5 10
    T $g $t[0] ($M + 18) ($y + 12) 13 $C.green $true 400 | Out-Null
    T $g $t[1] ($M + 18) ($y + 38) 12 $C.ink $false 420 | Out-Null
    T $g $t[2] ($M + 18) ($y + 60) 11.5 $C.body $false ($t[3] - 36) | Out-Null
    $y += 100
  }
  # 右侧 health 细节
  Rect $g 1090 244 454 300 '#FFFFFF' $C.line 1 12
  T $g 'health 的实际行为' 1110 262 12.5 $C.ink $true 420 | Out-Null
  $hs = @('GET {base}/health', '状态码非 4xx/5xx 即通过（不校验 body）', '单次上限 1 秒，失败继续重试', '整体期限耗尽才报超时', '返回时不带 access token')
  $yy = 294
  foreach ($h in $hs) { Dot $g 1110 ($yy + 6) 6 $C.green; T $g $h 1126 $yy 11.5 $C.body $false 400 | Out-Null; $yy += 40 }
  Rect $g $M 560 1488 150 $C.orangeBg $C.orange 1 12
  T $g '两个接口分开，是有意的' ($M + 20) 576 12.5 $C.orangeDk $true 400 | Out-Null
  T $g 'start_nowait() 只等 API socket 可用；wait_for_ready() 才等 envd。调用方可以先把磁盘、网络准备做完，最后再统一等 Guest 服务。' ($M + 20) 604 12 $C.body $false 1440 | Out-Null
  T $g '所以「端口能连」不能证明「能执行命令」——中间还差应用层这一跳。' ($M + 20) 646 12 $C.body $false 1440 | Out-Null
  Footer $g '就绪题答「三层」，比答「服务起来了」多拿一分' 10 $TOTAL
}

# ---- 11 exec 事件流 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='exec 返回的是流：';c=$C.ink;bold=$false}, @{t='Start 说明不了成功';c=$C.green;bold=$true}) '两个独立判断：事件是否收齐、退出码是多少' 2
  $ev = @(@('start 请求', 'cmd + args + env + cwd'), @('Start{pid}', '进程已创建'), @('Data', 'stdout / stderr 分段'), @('End{code}', '进程已退出'))
  $x = $M; $y = 248
  for ($i = 0; $i -lt 4; $i++) {
    StepCard $g $x $y 340 110 ([string]($i + 1)) $ev[$i][0] $ev[$i][1] $(if ($i -lt 3) { $C.green } else { $C.red })
    if ($i -lt 3) { Arrow $g ($x + 344) ($y + 55) ($x + 384) ($y + 55) $C.arrow 1.4 }
    $x += 388
  }
  Rect $g $M 400 720 130 '#FFFFFF' $C.green 1.5 12
  T $g '判断一：事件收齐了吗' ($M + 18) 418 12.5 $C.green $true 400 | Out-Null
  T $g 'Ok：一路收到 End；Err：流结束但没等到 End（传输/协议层）。' ($M + 18) 448 11.5 $C.body $false 680 | Out-Null
  Rect $g 800 400 744 130 '#FFFFFF' $C.green 1.5 12
  T $g '判断二：exit_code 是多少' 818 418 12.5 $C.green $true 400 | Out-Null
  T $g '0：程序自己认为成功；非零：失败或被杀（程序层）。' 818 448 11.5 $C.body $false 700 | Out-Null
  Rect $g $M 552 1488 96 $C.greenBg1 $C.green 1 12
  T $g '成功要三样同时满足：wait 返回 Ok + 收到 End + exit_code 符合预期。' ($M + 20) 570 12.5 $C.green $true 1440 | Out-Null
  T $g '只有 Start，说明「进程被创建出来了」——之后它仍可能立刻失败、崩溃、被超时杀掉。' ($M + 20) 600 12 $C.body $false 1440 | Out-Null
  T $g '另外：命令与参数分开传，不假设过 shell（没有管道、通配符、重定向语义）。' $M 668 12 $C.body $false 1488 | Out-Null
  Footer $g '看到 Start 就追问：End 到了吗、exit_code 是多少' 11 $TOTAL
}

# ---- 12 一次读六层 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='一次 4 KiB 读要跨六层：';c=$C.ink;bold=$false}, @{t='每层的「完成」含义都不同';c=$C.green;bold=$true}) '排障就是找出卡在哪一层的哪个完成点上' 2
  $steps = @(
    @('Guest 应用 read()', '文件偏移 → 页缓存未命中'),
    @('Guest 内核 ext4', 'extent → 逻辑块 LBA'),
    @('VirtIO → Firecracker', '描述符 + 门铃 → VM-Exit'),
    @('宿主 ublk 驱动', '请求入队：queue / tag'),
    @('daemon + OverlayBD', '查索引 → 定层 → 取字节'),
    @('原路返回', '填 buffer → used → 唤醒')
  )
  $x = $M; $y = 244
  for ($i = 0; $i -lt 3; $i++) {
    $s = $steps[$i]
    StepCard $g $x $y 460 120 ([string]($i + 1)) $s[0] $s[1] $C.green
    if ($i -lt 2) { Arrow $g ($x + 464) ($y + 60) ($x + 500) ($y + 60) $C.arrow 1.4 }
    $x += 508
  }
  $x = $M; $y = 386
  for ($i = 3; $i -lt 6; $i++) {
    $s = $steps[$i]
    StepCard $g $x $y 460 120 ([string]($i + 1)) $s[0] $s[1] $C.orange
    if ($i -lt 5) { Arrow $g ($x + 464) ($y + 60) ($x + 500) ($y + 60) $C.arrow 1.4 }
    $x += 508
  }
  Rect $g $M 528 1488 118 $C.redBg $C.red 1 12
  T $g '四个「完成」，不是一件事' ($M + 20) 544 12.5 $C.red $true 400 | Out-Null
  T $g '① FETCH 的 CQE 到＝请求送到 daemon　② daemon 提交 COMMIT＝它交差　③ 发布 used＝设备侧交差　④ read() 返回＝应用拿到字节' ($M + 20) 572 12 $C.body $false 1440 | Out-Null
  T $g '最容易错的是第 ①：CQE 只说明「请求送到了」，不说明数据已经从层里取出来。' ($M + 20) 610 12 $C.red $false 1440 | Out-Null
  T $g '一句话：每一层只对「自己那一段」负责，问「完成了吗」必须先说清是哪一层。' $M 664 12.5 $C.green $true 1488 | Out-Null
  Footer $g '把这条链背下来，等于把第 9—12 课串成一条线' 12 $TOTAL
}

# ---- 13 三个偏移 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='三个偏移不能混：';c=$C.ink;bold=$false}, @{t='少一个单位就差 8 倍';c=$C.green;bold=$true}) '文件偏移、LBA、后端位置，分属三个坐标系' 2
  $cols = @(340, 300, 340, 508)
  $hdr = @('偏移', '属于谁', '单位与换算', '常见错')
  $rows = @(@('文件偏移', 'Guest 文件系统', '字节；read 用当前位置，pread 显式指定', '以为文件偏移 0 就是磁盘偏移 0'),
            @('逻辑块 LBA', 'Guest 块设备', '块号；512 B 扇区与 4 KiB 块差 8 倍', '只写数字不写单位'),
            @('后端位置', '宿主存储', '层文件内的字节偏移或远端对象位置', '以为逻辑连续＝物理连续'))
  $x = $M; $y = 246
  for ($i = 0; $i -lt 4; $i++) { Rect $g $x $y $cols[$i] 46 $C.grayBg $C.line 1 8; T $g $hdr[$i] ($x + 12) ($y + 13) 12.5 $C.ink $true ($cols[$i] - 24) | Out-Null; $x += $cols[$i] }
  $y += 46
  for ($r = 0; $r -lt 3; $r++) {
    $x = $M
    for ($i = 0; $i -lt 4; $i++) {
      $bg = if ($r % 2 -eq 0) { '#FFFFFF' } else { $C.greenBg2 }
      Rect $g $x $y $cols[$i] 62 $bg $C.line 1 0
      $col = if ($i -eq 3) { $C.red } else { if ($i -eq 0) { $C.ink } else { $C.body } }
      T $g $rows[$r][$i] ($x + 12) ($y + 20) 12 $col ($i -eq 0) ($cols[$i] - 24) | Out-Null
      $x += $cols[$i]
    }
    $y += 62
  }
  Rect $g $M 492 1488 110 $C.orangeBg $C.orange 1 12
  T $g '最小例子（课堂假设）' ($M + 20) 508 12.5 $C.orangeDk $true 400 | Out-Null
  T $g '文件 8 KiB 在偏移 0 处，ext4 把它映射到磁盘字节偏移 8 MiB：按 512 B 扇区编号是 16384，按 4 KiB 块编号是 2048。' ($M + 20) 536 12 $C.body $false 1440 | Out-Null
  Rect $g $M 622 1488 118 '#FFFFFF' $C.line 1 12
  T $g '写路径的四个节点' ($M + 20) 638 12.5 $C.ink $true 400 | Out-Null
  T $g 'write 进页缓存 → 回写交 virtio → 后端写层文件 → fsync 才算持久化。write 返回只代表进了页缓存。' ($M + 20) 666 12 $C.body $false 1440 | Out-Null
  Footer $g '报偏移必须带单位；写返回不等于落盘' 13 $TOTAL
}

# ---- 14 分层覆盖 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='分层是覆盖映射，不是拼字节：';c=$C.ink;bold=$false}, @{t='无记录要回落，显式零要终止';c=$C.green;bold=$true}) '同一逻辑位置只认「第一个有记录的层」' 2
  # 左：三层
  $layers = @(@('upper（可写）', '位置1 → 新值', $C.green), @('增量层（只读）', '位置3 → 显式零', $C.orange), @('基层（只读）', '位置0/1/2 有数据', $C.red))
  $y = 240
  foreach ($l in $layers) {
    Rect $g $M $y 700 96 '#FFFFFF' $l[2] 1.5 10
    Rect $g $M $y 5 96 $l[2] $null 0 2
    T $g $l[0] ($M + 20) ($y + 16) 12.5 $C.ink $true 400 | Out-Null
    T $g $l[1] ($M + 20) ($y + 44) 11.5 $C.body $false 640 | Out-Null
    $y += 112
  }
  # 右：四情形
  T $g '最终视图：从上往下第一个命中' 800 240 12.5 $C.ink $true 700 | Out-Null
  $cells = @(@('位置 0', '基层 A', '回落', $C.green), @('位置 1', 'upper 新值', '覆盖', $C.green),
             @('位置 2', '全零', '遮蔽父层', $C.orange), @('位置 3', '全零', '空洞', $C.orange))
  for ($i = 0; $i -lt 4; $i++) {
    $cx = 800 + ($i % 2) * 372; $cy = 274 + [Math]::Floor($i / 2) * 132
    Rect $g $cx $cy 352 116 '#FFFFFF' $cells[$i][3] 1.5 10
    T $g $cells[$i][0] ($cx + 16) ($cy + 12) 11.5 $C.dim $false 200 | Out-Null
    T $g $cells[$i][1] ($cx + 16) ($cy + 36) 12.5 $C.ink $true 300 | Out-Null
    T $g $cells[$i][2] ($cx + 16) ($cy + 66) 11.5 $cells[$i][3] $false 300 | Out-Null
  }
  Rect $g $M 594 1488 150 $C.greenBg1 $C.green 1 12
  T $g '一句话记忆' ($M + 20) 610 12.5 $C.green $true 300 | Out-Null
  T $g '「没记录」不是零，它表示这层没管这段，要继续往下找；「显式零」表示我明确写过全是 0，必须在这里停。' ($M + 20) 636 12 $C.body $false 1440 | Out-Null
  T $g '反例：把「显式零」当成「没记录」，读出来就是父层的旧数据——这不是零，是数据错。' ($M + 20) 676 12 $C.red $false 1440 | Out-Null
  Footer $g '看到「覆盖」先问：这一层的记录是数据、是无记录、还是显式零' 14 $TOTAL
}

# ---- 15 ublk 与 daemon ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='内核给壳，用户态给内容：';c=$C.ink;bold=$false}, @{t='daemon 是这条链的单点';c=$C.red;bold=$true}) 'ublk 只搬运「第几块、多长」，格式与远端在用户态' 2
  $nodes = @(@('/dev/ublk-control', '创建 / 删除 / 设参数'), @('/dev/ublkcN', '命令交接（daemon 拿请求）'), @('/dev/ublkbN', '数据读写（FC 挂这个）'))
  $x = $M; $y = 240
  for ($i = 0; $i -lt 3; $i++) {
    Rect $g $x $y 480 96 '#FFFFFF' $C.green 1.5 10
    T $g $nodes[$i][0] ($x + 18) ($y + 16) 12.5 $C.ink $true 440 | Out-Null
    T $g $nodes[$i][1] ($x + 18) ($y + 46) 11.5 $C.body $false 440 | Out-Null
    $x += 508
  }
  $steps = @(@('等待', '在 io_uring 提交「有活给我」'), @('领取', 'CQE 带回请求描述'),
             @('解析', 'OverlayBD 查索引定层'), @('提交', 'COMMIT 报告完成'))
  $x = $M; $y = 372
  for ($i = 0; $i -lt 4; $i++) {
    StepCard $g $x $y 340 116 ([string]($i + 1)) $steps[$i][0] $steps[$i][1] $C.orange
    if ($i -lt 3) { Arrow $g ($x + 344) ($y + 58) ($x + 384) ($y + 58) $C.arrow 1.4 }
    $x += 388
  }
  Rect $g $M 520 1488 96 $C.redBg $C.red 1 12
  T $g '最容易错：把「领取」的 CQE 当成「数据读完」。' ($M + 20) 536 12.5 $C.red $true 1400 | Out-Null
  T $g '它只说明请求送到了 daemon；真正的字节要在第 ③ 步之后才有。' ($M + 20) 566 12 $C.body $false 1400 | Out-Null
  Rect $g $M 636 1488 108 '#FFFFFF' $C.line 1 12
  T $g '它不是什么' ($M + 20) 652 12.5 $C.ink $true 300 | Out-Null
  T $g '不是内核模块；不是每沙箱一个进程（集中式，一个进程管全节点设备）；OverlayBD 是它链接的库，不是另一个服务。' ($M + 20) 680 12 $C.body $false 1440 | Out-Null
  Footer $g 'daemon 挂了 → 该节点块 IO 全停，快照恢复也直接失败' 15 $TOTAL
}

# ---- 16 mmap / 缺页 / COW ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='映射了 ≠ 分配了 ≠ 复制了：';c=$C.ink;bold=$false}, @{t='写才复制';c=$C.green;bold=$true}) 'mmap 只建 VMA，物理页在缺页时才准备' 2
  $trio = @(@('mmap 之后', '只有虚拟范围（VMA），一个物理页都没占', $C.green), @('第一次读', '缺页：页在就映射，不在就去取（major）', $C.orange), @('第一次写', 'COW：复制出私有副本，之后各写各的', $C.red))
  $x = $M; $y = 240
  for ($i = 0; $i -lt 3; $i++) {
    Rect $g $x $y 480 120 '#FFFFFF' $trio[$i][2] 1.5 10
    T $g $trio[$i][0] ($x + 18) ($y + 16) 13 $trio[$i][2] $true 400 | Out-Null
    T $g $trio[$i][1] ($x + 18) ($y + 46) 11.5 $C.body $false 440 | Out-Null
    if ($i -lt 2) { Arrow $g ($x + 484) ($y + 60) ($x + 520) ($y + 60) $C.arrow 1.4 }
    $x += 528
  }
  # 三层缺页
  T $g '三层缺页，三个处理者' $M 392 12.5 $C.ink $true 400 | Out-Null
  $rows = @(@('Guest 页表', 'GVA → GPA', 'Guest 内核处理，宿主不知道'), @('EPT', 'GPA → HPA', 'KVM 处理，常能补完直接重入'),
            @('宿主页表', 'HVA → HPA', '宿主内核：匿名页分配或文件页读入'))
  $y = 422
  for ($r = 0; $r -lt 3; $r++) {
    Rect $g $M $y 1488 54 $(if ($r % 2 -eq 0) { '#FFFFFF' } else { $C.grayBg }) $C.line 1 8
    T $g $rows[$r][0] ($M + 16) ($y + 16) 12 $C.ink $true 260 | Out-Null
    T $g $rows[$r][1] ($M + 300) ($y + 16) 12 $C.body $false 300 | Out-Null
    T $g $rows[$r][2] ($M + 640) ($y + 16) 12 $C.body $false 820 | Out-Null
    $y += 54
  }
  Rect $g $M 602 1488 140 $C.greenBg1 $C.green 1 12
  T $g '一句话记忆' ($M + 20) 618 12.5 $C.green $true 300 | Out-Null
  T $g '看到 mmap 成功不要以为内存已占；看到 RSS 不涨也不要以为没生效——它还没被访问。' ($M + 20) 644 12 $C.body $false 1440 | Out-Null
  T $g 'microVM 恢复：只读后端 + MAP_PRIVATE → 读共享页缓存，写才 COW（Firecracker 1.12.1 memory.rs:136 已核）。' ($M + 20) 674 12 $C.orangeDk $false 1440 | Out-Null
  Footer $g '问到「恢复后第一次读/第一次写」，答案分别是缺页与 COW' 16 $TOTAL
}

# ---- 17 快照四件套 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='快照是四件套：';c=$C.ink;bold=$false}, @{t='缺一件就恢复不出同款机器';c=$C.green;bold=$true}) '状态、内存、磁盘、配置，各自有不同的完成点' 2
  $quad = @(@('① VM 状态', '寄存器、指令位置、设备状态', $C.green), @('② 内存镜像', 'Guest RAM 字节，可增量 + 父层', $C.green),
            @('③ 磁盘视图', 'rootfs 层 + 额外盘 + 父层引用', $C.orange), @('④ 恢复配置', '层顺序、设备关联、兼容参数', $C.orange))
  for ($i = 0; $i -lt 4; $i++) {
    $cx = $M + ($i % 2) * 760; $cy = 240 + [Math]::Floor($i / 2) * 136
    Rect $g $cx $cy 728 124 '#FFFFFF' $quad[$i][2] 1.5 10
    Rect $g $cx $cy 5 124 $quad[$i][2] $null 0 2
    T $g $quad[$i][0] ($cx + 20) ($cy + 16) 13 $quad[$i][2] $true 300 | Out-Null
    T $g $quad[$i][1] ($cx + 20) ($cy + 46) 11.5 $C.body $false 680 | Out-Null
  }
  # 四完成点
  T $g '四个完成点，顺序固定' $M 520 12.5 $C.ink $true 400 | Out-Null
  $st = @(@('暂停', 'vCPU 全部确认'), @('捕获', '读内存 / 写层'), @('持久化', 'fsync / 上传'), @('释放', '回收运行时'))
  $x = $M; $y = 550
  for ($i = 0; $i -lt 4; $i++) {
    StepCard $g $x $y 340 108 ([string]($i + 1)) $st[$i][0] $st[$i][1] $C.green
    if ($i -lt 3) { Arrow $g ($x + 344) ($y + 54) ($x + 384) ($y + 54) $C.arrow 1.4 }
    $x += 388
  }
  T $g '最容易错：pause 成功就当快照成功。暂停只保证「现在不跑了」，捕获、写层、落盘都可能失败。' $M 700 12.5 $C.red $true 1488 | Out-Null
  Footer $g '四件套 + 四完成点，是快照两页的全部内容' 17 $TOTAL
}

# ---- 18 暂停三完成点 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='暂停不等于快照：';c=$C.ink;bold=$false}, @{t='「没被调度」不是「已暂停」';c=$C.red;bold=$true}) '三个完成点，缺一个就会抓到不一致的状态' 2
  $ev = @(@('t1', 'API 收到请求', $C.green), @('t2', '置暂停意图', $C.green), @('t3', 'vCPU0 确认', $C.green),
          @('t4', 'vCPU1 没被调度', $C.red), @('t5', 'vCPU1 确认', $C.green), @('t6', '暂停完成', $C.green))
  $x = $M; $y = 244; $bw = 226
  for ($i = 0; $i -lt 6; $i++) {
    Rect $g $x $y $bw 96 '#FFFFFF' $ev[$i][2] 1.5 10
    T $g $ev[$i][0] ($x + 14) ($y + 12) 11.5 $ev[$i][2] $true 100 | Out-Null
    T $g $ev[$i][1] ($x + 14) ($y + 38) 11.5 $C.body $false ($bw - 28) | Out-Null
    if ($i -lt 5) { Arrow $g ($x + $bw + 4) ($y + 48) ($x + $bw + 26) ($y + 48) $C.arrow 1.2 }
    $x += $bw + 30
  }
  Rect $g $M 366 1488 116 $C.redBg $C.red 1 12
  T $g 't4 是唯一难点' ($M + 20) 382 12.5 $C.red $true 300 | Out-Null
  T $g 'vCPU1 只是「没拿到 CPU」：调度器再给它时间片，它会继续执行 Guest 指令、继续写 Guest RAM。' ($M + 20) 410 12 $C.body $false 1440 | Out-Null
  T $g '「没被调度」是调度状态，「已暂停」是协议状态；前者随时可能变，后者要等恢复指令。' ($M + 20) 442 12 $C.body $false 1440 | Out-Null
  # 三个完成点
  $c3 = @(@('请求已发出', '本地把字节写进 socket'), @('Firecracker 已接收', 'API 线程解析成功'), @('全部 vCPU 确认', '没有 vCPU 还能执行 Guest'))
  $x = $M; $y = 512
  for ($i = 0; $i -lt 3; $i++) {
    Rect $g $x $y 480 120 '#FFFFFF' $C.green 1.5 10
    T $g $c3[$i][0] ($x + 18) ($y + 16) 12.5 $C.green $true 400 | Out-Null
    T $g $c3[$i][1] ($x + 18) ($y + 46) 11.5 $C.body $false 440 | Out-Null
    $x += 528
  }
  T $g '暂停完成之后还有：捕获内存、写层、fsync、改 manifest —— 每一步都可能失败，都算独立的完成点。' $M 664 12.5 $C.green $true 1488 | Out-Null
  Footer $g '看到「暂停成功」就追问：全部 vCPU 确认了吗、快照写完了吗' 18 $TOTAL
}

# ---- 19 恢复路径 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='恢复不是把内存读回来：';c=$C.ink;bold=$false}, @{t='只读设备 + 按需缺页 + 写时 COW';c=$C.green;bold=$true}) '恢复成功只代表「能开始跑」' 2
  $steps = @(@('准备环境', '检查 ublk、备盘、备网'), @('加载 VM 状态', 'resume_vm = false'), @('映射内存', '只读块设备 + MAP_PRIVATE'),
             @('补配置', '新挂载卷 / MMDS / 限流'), @('resume', 'vCPU 执行，缺页按需取'))
  $x = $M; $y = 244
  for ($i = 0; $i -lt 5; $i++) {
    StepCard $g $x $y 280 124 ([string]($i + 1)) $steps[$i][0] $steps[$i][1] $C.green
    if ($i -lt 4) { Arrow $g ($x + 284) ($y + 62) ($x + 316) ($y + 62) $C.arrow 1.2 }
    $x += 316
  }
  # 一页说明
  Rect $g $M 400 1488 120 $C.greenBg1 $C.green 1 12
  T $g '一页 RAM 怎么变得可访问' ($M + 20) 416 12.5 $C.green $true 400 | Out-Null
  T $g 'Guest 访问 GPA → 宿主页表缺项 → 向只读块设备发块读 → daemon 查 OverlayBD 取这一块 → 填进宿主页 → Guest 继续。' ($M + 20) 444 12 $C.body $false 1440 | Out-Null
  # 为什么先不跑
  Rect $g $M 540 728 150 '#FFFFFF' $C.line 1 12
  T $g '为什么要 resume_vm = false' ($M + 20) 556 12.5 $C.ink $true 400 | Out-Null
  T $g '先把状态、设备、网络、额外盘都装好，最后才让 vCPU 跑；否则 Guest 会在配置不全时就开始执行。' ($M + 20) 584 12 $C.body $false 690 | Out-Null
  Rect $g 816 540 728 150 '#FFFFFF' $C.line 1 12
  T $g '共享与私有（已核验）' (836) 556 12.5 $C.ink $true 400 | Out-Null
  T $g '同一模板的沙箱共享同一只读 ublk 设备与页缓存；Firecracker 用 MAP_PRIVATE 映射，写时才 COW 出私有页。' (836) 584 12 $C.body $false 690 | Out-Null
  T $g '推论：恢复成功 ≠ 所有页已在宿主 RAM。首条命令慢、内存指标却不高，是正常的按需加载。' $M 716 12.5 $C.green $true 1488 | Out-Null
  Footer $g '恢复 = 重建机器 + 装载状态，不是「重新开机」' 19 $TOTAL
}

# ---- 20 网络两方向 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='出站靠 SNAT，入站靠 DNAT：';c=$C.ink;bold=$false}, @{t='两条方向相反的路';c=$C.green;bold=$true}) '每个 netns 都能有 tap0，靠 slot 地址区分实例' 2
  T $g '出站（Guest 主动连外面）' $M 236 12.5 $C.orangeDk $true 500 | Out-Null
  $out = @(@('eth0', 'VirtIO 发出'), @('tap0', '沙箱 netns'), @('SNAT', '源改成 slot 地址'), @('veth', '进主 netns'), @('MASQUERADE', '适配出口'))
  $x = $M; $y = 264
  for ($i = 0; $i -lt 5; $i++) {
    Rect $g $x $y 270 100 '#FFFFFF' $C.orange 1.5 10
    T $g $out[$i][0] ($x + 14) ($y + 16) 12 $C.ink $true 240 | Out-Null
    T $g $out[$i][1] ($x + 14) ($y + 46) 11 $C.body $false 240 | Out-Null
    if ($i -lt 4) { Arrow $g ($x + 274) ($y + 50) ($x + 306) ($y + 50) $C.arrow 1.2 }
    $x += 306
  }
  T $g '入站（宿主访问 Guest 的 envd）' $M 392 12.5 $C.green $true 500 | Out-Null
  $inn = @(@('server', '连 slot 地址'), @('veth', '进沙箱 netns'), @('DNAT', '目的改成 Guest IP'), @('tap0 → FC', 'VirtIO RX'), @('envd', '处理请求'))
  $x = $M; $y = 420
  for ($i = 0; $i -lt 5; $i++) {
    Rect $g $x $y 270 100 '#FFFFFF' $C.green 1.5 10
    T $g $inn[$i][0] ($x + 14) ($y + 16) 12 $C.ink $true 240 | Out-Null
    T $g $inn[$i][1] ($x + 14) ($y + 46) 11 $C.body $false 240 | Out-Null
    if ($i -lt 4) { Arrow $g ($x + 274) ($y + 50) ($x + 306) ($y + 50) $C.arrow 1.2 }
    $x += 306
  }
  Rect $g $M 548 1488 150 $C.orangeBg $C.orange 1 12
  T $g '三个必须说准的点' ($M + 20) 564 12.5 $C.orangeDk $true 400 | Out-Null
  T $g '① 同名 tap0 不冲突：先由 netns 隔开，再用 slot 专属地址区分实例。' ($M + 20) 592 12 $C.body $false 1440 | Out-Null
  T $g '② TX 的 used 只表示发送缓冲可回收，不代表远端收到、更不代表业务成功。' ($M + 20) 620 12 $C.body $false 1440 | Out-Null
  T $g '③ 返回流量靠 conntrack 逆变换；快照恢复后 conntrack 不回滚，所以旧连接可能不通。' ($M + 20) 648 12 $C.body $false 1440 | Out-Null
  Footer $g '看到「网络不通」先分方向：出站看 SNAT/路由，入站看 DNAT/端口' 20 $TOTAL
}

# ---- 21 四道门 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='四类威胁，四道门：';c=$C.ink;bold=$false}, @{t='seccomp 只约束宿主 syscall';c=$C.red;bold=$true}) '先问「防谁、越没越过门」，再问「用什么挡」' 2
  $quad = @(@('A. Guest 内作恶', '没越过任何门：Guest root 本来就能任意 syscall', $C.green),
            @('B. VMM 被攻破', '已越过虚拟化边界：seccomp / 降权 / chroot / caps', $C.red),
            @('C. 资源超用', '没越界，走正常消耗：cgroup 限值 / vCPU / balloon', $C.orange),
            @('D. 网络外连', '没越界，走虚拟网卡：netns / iptables / 代理', $C.orange))
  for ($i = 0; $i -lt 4; $i++) {
    $cx = $M + ($i % 2) * 760; $cy = 240 + [Math]::Floor($i / 2) * 136
    Rect $g $cx $cy 728 124 '#FFFFFF' $quad[$i][2] 1.5 10
    Rect $g $cx $cy 5 124 $quad[$i][2] $null 0 2
    T $g $quad[$i][0] ($cx + 20) ($cy + 16) 13 $quad[$i][2] $true 300 | Out-Null
    T $g $quad[$i][1] ($cx + 20) ($cy + 46) 11.5 $C.body $false 680 | Out-Null
  }
  # seccomp 三行
  T $g 'seccomp 的三个关键事实' $M 520 12.5 $C.ink $true 500 | Out-Null
  $rows = @(@('作用对象', '线程，不是进程（vmm 60 / api 35 / vcpu 43 条）'), @('默认动作', 'trap：命中未允许的 syscall 直接 SIGSYS'), @('拦不到', 'Guest 内部的 syscall 由 Guest 内核处理'))
  $y = 550
  for ($r = 0; $r -lt 3; $r++) {
    Rect $g $M $y 1488 50 $(if ($r % 2 -eq 0) { '#FFFFFF' } else { $C.grayBg }) $C.line 1 8
    T $g $rows[$r][0] ($M + 16) ($y + 14) 12 $C.red $true 200 | Out-Null
    T $g $rows[$r][1] ($M + 240) ($y + 14) 12 $C.body $false 1200 | Out-Null
    $y += 50
  }
  T $g '一句话分家：namespace 改「看见什么」，cgroup 改「能用多少」，seccomp/caps/LSM 改「能对内核做什么」。' $M 712 12.5 $C.green $true 1488 | Out-Null
  Footer $g '看到「隔离」先分威胁类型，再谈控制点' 21 $TOTAL
}

# ---- 22 公式 ----
$pages += {
  param($g)
  Header $g '02 概念' @(@{t='登记不复制：';c=$C.ink;bold=$false}, @{t='HVA 由 GPA 偏移算出来';c=$C.green;bold=$true}) 'memslot 只记录对应关系，物理页在缺页时才准备' 2
  # 公式框
  Rect $g $M 244 980 132 $C.greenBg1 $C.green 1.5 12
  $f = Font2 26 $true; $b = Brush $C.green
  $eq = 'HVA = userspace_addr + (目标 GPA - guest_phys_addr)'
  $ew = $g.MeasureString($eq, $f).Width
  $g.DrawString($eq, $f, $b, [single]($M + (980 - $ew) / 2), [single]282)
  $f.Dispose(); $b.Dispose()
  # 变量解释
  Rect $g 1060 244 484 132 '#FFFFFF' $C.line 1 12
  T $g '变量含义' 1080 258 11.5 $C.ink $true 300 | Out-Null
  T $g 'userspace_addr：登记时给的 HVA 起点' 1080 282 11 $C.body $false 444 | Out-Null
  T $g 'guest_phys_addr：这段 GPA 的起点' 1080 306 11 $C.body $false 444 | Out-Null
  T $g '目标 GPA：要访问的那一页' 1080 330 11 $C.body $false 444 | Out-Null
  # 最小例子
  Rect $g $M 404 1488 150 '#FFFFFF' $C.line 1 12
  T $g '最小例子（代入数字）' ($M + 20) 420 12.5 $C.ink $true 400 | Out-Null
  T $g '登记：GPA 起点 0，HVA 起点 0x70000000，长度 128 MiB。问：GPA 0x2000 这一页在 Firecracker 里的地址？' ($M + 20) 448 12 $C.body $false 1440 | Out-Null
  T $g '代入：HVA = 0x70000000 + (0x2000 - 0) = 0x70002000。这个地址可直接交给 process_vm_readv 当 remote。' ($M + 20) 480 12 $C.green $true 1440 | Out-Null
  T $g '注意：这是 Firecracker 的 HVA，不是 Guest 的 GVA，也不是 HPA。' ($M + 20) 512 11.5 $C.dim $false 1440 | Out-Null
  # 适用条件 / 变形
  Rect $g $M 582 728 148 $C.orangeBg $C.orange 1 12
  T $g '适用条件' ($M + 20) 598 12.5 $C.orangeDk $true 300 | Out-Null
  T $g '目标地址必须落在同一条 memslot 内；跨 region 要先定位属于哪一段。' ($M + 20) 626 12 $C.body $false 690 | Out-Null
  T $g '公式给的是软件关系，EPT 项是否已建立要另看。' ($M + 20) 660 11.5 $C.dim $false 690 | Out-Null
  Rect $g 816 582 728 148 '#FFFFFF' $C.line 1 12
  T $g '常见变形' (836) 598 12.5 $C.ink $true 300 | Out-Null
  T $g '反算 GPA：GPA = guest_phys_addr + (HVA - userspace_addr)' (836) 626 12 $C.body $false 690 | Out-Null
  T $g '页面还没驻留时，KVM 要取页、可能触发缺页，再填 EPT。' (836) 658 11.5 $C.dim $false 690 | Out-Null
  Footer $g '公式只在「同一条 memslot 内」成立；跨段先定位' 22 $TOTAL
}

# ---- 23 例题1 完成点 ----
$pages += {
  param($g)
  Header $g '03 例题' @(@{t='这题考的是';c=$C.ink;bold=$false}, @{t='「完成点」';c=$C.green;bold=$true}, @{t='，不是流程记忆';c=$C.ink;bold=$false}) '答对的关键是把「谁完成了什么」一格一格说清' 3
  # 左：题目
  Rect $g $M 240 700 380 '#FFFFFF' $C.line 1 12
  T $g '题目' ($M + 20) 256 12.5 $C.ink $true 200 | Out-Null
  T $g 'daemon 收到 UBLK_IO_FETCH_REQ 对应的 CQE。此时能不能说「这个 4 KiB 已经从盘上读到了」？为什么？' ($M + 20) 284 12.5 $C.body $false 660 | Out-Null
  T $g '已知' ($M + 20) 388 11.5 $C.green $true 200 | Out-Null
  T $g '· CQE 已到，携带 queue / tag / 偏移 / 长度' ($M + 20) 412 11.5 $C.body $false 660 | Out-Null
  T $g '· 后端是只读层 + OverlayBD' ($M + 20) 436 11.5 $C.body $false 660 | Out-Null
  T $g '求' ($M + 20) 470 11.5 $C.green $true 200 | Out-Null
  T $g '· 判断能否断言「数据已读出」，并说明还差哪几步' ($M + 20) 494 11.5 $C.body $false 660 | Out-Null
  # 右：步骤
  $steps = @(@('1', '先定位 CQE 的语义', '它对应的是「领取请求」这条命令，不是后端读。所以只能说明请求送到了 daemon。'),
             @('2', '再列出还差的动作', 'daemon 查 OverlayBD 索引 → 定层 → 取字节 → 填 buffer → 提交 COMMIT。'),
             @('3', '最后给判据', '只有 COMMIT 完成、内核完成原块请求，数据才算到。'))
  $x = 812; $y = 240
  foreach ($s in $steps) {
    Rect $g $x $y 732 112 '#FFFFFF' $C.line 1 10
    Rect $g $x $y 5 112 $C.green $null 0 2
    T $g $s[0] ($x + 18) ($y + 14) 20 $C.green $true 40 | Out-Null
    T $g $s[1] ($x + 56) ($y + 14) 12.5 $C.ink $true 640 | Out-Null
    T $g $s[2] ($x + 56) ($y + 42) 11.5 $C.body $false 650 | Out-Null
    $y += 124
  }
  Rect $g $M 644 1488 92 $C.greenBg1 $C.green 1 12
  T $g '答案：不能。CQE 只证明「请求已交付」，数据还在后端；要等 daemon 取到字节并提交完成。' ($M + 20) 660 12.5 $C.green $true 1440 | Out-Null
  T $g '易错：把「领取完成」当成「IO 完成」——这是第 12 课里最常错的一步。' ($M + 20) 692 11.5 $C.red $false 1440 | Out-Null
  Footer $g '凡是 CQE / 回调 / 事件，先问它对应的是哪条命令' 23 $TOTAL
}

# ---- 24 例题2 作用对象 ----
$pages += {
  param($g)
  Header $g '03 例题' @(@{t='这题考的是';c=$C.ink;bold=$false}, @{t='「作用对象」';c=$C.green;bold=$true}, @{t='，也就是这层管的是谁';c=$C.ink;bold=$false}) '答错的人几乎都是把「进程」和「Guest」混了' 3
  Rect $g $M 240 700 380 '#FFFFFF' $C.line 1 12
  T $g '题目' ($M + 20) 256 12.5 $C.ink $true 200 | Out-Null
  T $g 'Guest 里的 root 用户执行任意 syscall，会被 Firecracker 的 seccomp 拦住吗？' ($M + 20) 284 12.5 $C.body $false 660 | Out-Null
  T $g '已知' ($M + 20) 360 11.5 $C.green $true 200 | Out-Null
  T $g '· seccomp 白名单装在 firecracker 进程的线程上' ($M + 20) 384 11.5 $C.body $false 660 | Out-Null
  T $g '· Guest 有独立的 Guest 内核' ($M + 20) 408 11.5 $C.body $false 660 | Out-Null
  T $g '求' ($M + 20) 442 11.5 $C.green $true 200 | Out-Null
  T $g '· 判断会不会被拦，并说明 seccomp 实际约束的是谁' ($M + 20) 466 11.5 $C.body $false 660 | Out-Null
  $steps = @(@('1', '先问：syscall 由谁处理', 'Guest 里的 syscall 由 Guest 内核处理，根本不经过宿主 seccomp。'),
             @('2', '再问：seccomp 装在谁身上', '装在 firecracker 的线程上，拦的是它自己发出的宿主 syscall。'),
             @('3', '最后说清边界', '所以 seccomp 防的是「VMM 被攻破后」的破坏力，不是 Guest 内行为。'))
  $x = 812; $y = 240
  foreach ($s in $steps) {
    Rect $g $x $y 732 112 '#FFFFFF' $C.line 1 10
    Rect $g $x $y 5 112 $C.green $null 0 2
    T $g $s[0] ($x + 18) ($y + 14) 20 $C.green $true 40 | Out-Null
    T $g $s[1] ($x + 56) ($y + 14) 12.5 $C.ink $true 640 | Out-Null
    T $g $s[2] ($x + 56) ($y + 42) 11.5 $C.body $false 650 | Out-Null
    $y += 124
  }
  Rect $g $M 546 1488 96 $C.greenBg1 $C.green 1 12
  T $g '答案：不会。seccomp 是线程级白名单，只约束 firecracker 发出的宿主 syscall。' ($M + 20) 562 12.5 $C.green $true 1440 | Out-Null
  T $g 'Guest 内的 root 由 Guest 内核限制（pid_max、RLIMIT_NPROC），它逃不到宿主层面。' ($M + 20) 594 12 $C.body $false 1440 | Out-Null
  T $g '易错：以为 seccomp 是「给 Guest 用的」；以为 namespace 里的 root 已经没有特权。' $M 656 11.5 $C.red $false 1488 | Out-Null
  Footer $g '每题先问一句：这个机制作用在哪个对象上（进程/线程/内核/Guest）' 24 $TOTAL
}

# ---- 25 例题3 判门 ----
$pages += {
  param($g)
  Header $g '03 例题' @(@{t='这题考的是';c=$C.ink;bold=$false}, @{t='「判门」';c=$C.green;bold=$true}, @{t='：先定威胁，再找漏点';c=$C.ink;bold=$false}) '工单题的正确姿势：分层定位，而不是背名词' 3
  Rect $g $M 240 700 380 '#FFFFFF' $C.line 1 12
  T $g '题目' ($M + 20) 256 12.5 $C.ink $true 200 | Out-Null
  T $g '工单说「Guest 里跑了个 fork bomb，把宿主机搞卡了」。这句话对不对？该查哪一层？' ($M + 20) 284 12.5 $C.body $false 660 | Out-Null
  T $g '已知' ($M + 20) 360 11.5 $C.green $true 200 | Out-Null
  T $g '· Guest 进程不是宿主 task' ($M + 20) 384 11.5 $C.body $false 660 | Out-Null
  T $g '· 宿主 cgroup 只对 VMM 记账' ($M + 20) 408 11.5 $C.body $false 660 | Out-Null
  T $g '求' ($M + 20) 442 11.5 $C.green $true 200 | Out-Null
  T $g '· 判断这句话对不对，并给出两个可查的指标' ($M + 20) 466 11.5 $C.body $false 660 | Out-Null
  $steps = @(@('1', '拆半句：卡是真，原因要精确', '宿主机确实会卡，但不会因为「多出进程」，而是被这台 VM 的资源消耗拖慢。'),
             @('2', '定位门：谁该挡它', 'Guest 内的 fork 由 Guest 内核限制；宿主侧只靠 cgroup 的 memory.max / cpu.max。'),
             @('3', '给指标', '宿主看 memory.current、cpu.stat 与线程数；Guest 内看进程数。'))
  $x = 812; $y = 240
  foreach ($s in $steps) {
    Rect $g $x $y 732 112 '#FFFFFF' $C.line 1 10
    Rect $g $x $y 5 112 $C.green $null 0 2
    T $g $s[0] ($x + 18) ($y + 14) 20 $C.green $true 40 | Out-Null
    T $g $s[1] ($x + 56) ($y + 14) 12.5 $C.ink $true 640 | Out-Null
    T $g $s[2] ($x + 56) ($y + 42) 11.5 $C.body $false 650 | Out-Null
    $y += 124
  }
  Rect $g $M 546 1488 96 $C.redBg $C.red 1 12
  T $g '答案：半对。宿主「卡」成立，「原因」说不准；ps 看不到 Guest 进程这件事才是关键。' ($M + 20) 562 12.5 $C.red $true 1440 | Out-Null
  T $g '易错：以为 pids.max 能挡住 Guest 内的 fork——pids 控制器只数宿主 cgroup 里的 task。' ($M + 20) 594 12 $C.body $false 1440 | Out-Null
  T $g '正确兜底：memory.max（OOM 杀整台 VM）、cpu.max、vCPU 数、balloon。' $M 640 12.5 $C.green $true 1488 | Out-Null
  Footer $g '判门三步：定威胁类型 → 找控制点 → 说清它管不到什么' 25 $TOTAL
}

# ---- 26 易错点 ----
$pages += {
  param($g)
  Header $g '03 易错点' @(@{t='6 个高频错答：';c=$C.ink;bold=$false}, @{t='错在哪一句，正确怎么说';c=$C.red;bold=$true}) '这些是面试与工单里最容易被戳穿的说法' 3
  $rows = @(
    @('pids.max 能挡 Guest 内 fork bomb', '它只数宿主 cgroup 里的 task；Guest 进程不是宿主 task'),
    @('多实例共享同一批 page cache 页（用只读块设备时）', '只读设备被共享、页缓存共享，但要写清是 MAP_PRIVATE + COW'),
    @('VM-Exit 就等于 KVM_RUN 返回用户态', 'KVM 能处理的退出会直接重入，ioctl 从未返回'),
    @('namespace 隔离等于降权', '只改视图；ns 里的 root 仍是 root'),
    @('finalize + rename 等于已持久化', '只保证格式完成与名字切换，不等于断电安全'),
    @('health 通过等于鉴权通过', 'health 不带 token；受保护命令另有鉴权')
  )
  $y = 240
  for ($i = 0; $i -lt 6; $i++) {
    Rect $g $M $y 1488 76 '#FFFFFF' $C.line 1 10
    Rect $g $M $y 5 76 $C.red $null 0 2
    T $g '错' ($M + 16) ($y + 24) 13 $C.red $true 26 | Out-Null
    T $g $rows[$i][0] ($M + 48) ($y + 16) 12 $C.red $false 620 | Out-Null
    T $g '对' ($M + 700) ($y + 24) 13 $C.green $true 26 | Out-Null
    T $g $rows[$i][1] ($M + 732) ($y + 16) 12 $C.green $false 730 | Out-Null
    $y += 84
  }
  T $g '看到「挡住/不影响/等于」这类绝对化说法，就要想到「它管的是哪一层、哪一步」。' $M 754 12.5 $C.green $true 1488 | Out-Null
  Footer $g '错答的共同病根：把「某层完成」当「整件事完成」' 26 $TOTAL
}

# ---- 27 记忆卡 ----
$pages += {
  param($g)
  Header $g '04 总结' @(@{t='记住 5 个数字';c=$C.ink;bold=$false}, @{t='＋一条主线';c=$C.green;bold=$true}) '考试与面试里，数字比形容词可信' 4
  $nums = @(@('16', '字节', '一个 VirtIO 描述符的大小'),
            @('1', '秒', 'health 单次探测上限'),
            @('4', 'KiB', '页与逻辑块的常用粒度（与 512 B 扇区差 8 倍）'),
            @('60/35/43', '条', 'seccomp 三组白名单：vmm / api / vcpu'),
            @('3', '个', '暂停的完成点：发出 / 接收 / 全部确认'))
  $x = $M; $y = 240
  for ($i = 0; $i -lt 5; $i++) {
    $cx = $M + ($i % 3) * 500; $cy = 240 + [Math]::Floor($i / 3) * 150
    Rect $g $cx $cy 480 134 '#FFFFFF' $C.line 1 12
    T $g $nums[$i][0] ($cx + 20) ($cy + 16) 34 $C.green $true 300 | Out-Null
    T $g $nums[$i][1] ($cx + 240) ($cy + 30) 12 $C.green $true 60 | Out-Null
    T $g $nums[$i][2] ($cx + 20) ($cy + 74) 11.5 $C.body $false 440 | Out-Null
  }
  Rect $g $M 552 1488 128 $C.greenBg1 $C.green 1 12
  T $g '一条主线' ($M + 20) 568 12.5 $C.green $true 300 | Out-Null
  T $g '一个请求怎么落到硬件（Guest → virtio → FC → ublk → 层），再带着结果回到调用者（used → 唤醒 → read 返回）。' ($M + 20) 596 12 $C.body $false 1440 | Out-Null
  T $g '如果只记三件事：① 三个执行环境 ② 每层的完成点 ③ 暂停/快照/恢复不是同一件事。' ($M + 20) 632 12 $C.ink $true 1440 | Out-Null
  Footer $g '数字要给口径：单位、范围、版本' 27 $TOTAL
}

# ---- 28 练习 ----
$pages += {
  param($g)
  Header $g '04 总结' @(@{t='3 道练习题：';c=$C.ink;bold=$false}, @{t='答案在第 30 页';c=$C.green;bold=$true}) '先自己写，再翻答案；每题只写三行也算完成' 4
  $qs = @(@('基础', $C.green, '一台 VM 配了 2 个 vCPU。宿主上这台 firecracker 至少有几个线程？分别负责什么？'),
          @('进阶', $C.orange, '一次 4 KiB 读，Guest 页缓存命中。还会发生 virtio 队列请求吗？为什么？'),
          @('易错', $C.red, '同事说「快照失败是因为 pause 没成功」。你怎么判断他说的对不对？要查哪两个点？'))
  $y = 244
  foreach ($q in $qs) {
    Rect $g $M $y 1488 150 '#FFFFFF' $C.line 1 12
    Rect $g $M $y 5 150 $q[1] $null 0 2
    Chip $g ($M + 20) ($y + 18) $q[0] $q[1] $C.grayBg 76 26 | Out-Null
    T $g $q[2] ($M + 20) ($y + 58) 13 $C.ink $false 1420 | Out-Null
    T $g '（在下面留白处作答）' ($M + 20) ($y + 110) 11.5 $C.dim $false 400 | Out-Null
    $y += 166
  }
  T $g '提示：第 1 题数线程；第 2 题分清「缓存命中」与「路径解析」；第 3 题看完成点而不是看结论。' $M 742 12 $C.body $false 1488 | Out-Null
  Footer $g '练习页不给答案：写下来才知道哪里断' 28 $TOTAL
}

# ---- 29 总结 ----
$pages += {
  param($g)
  Header $g '04 总结' @(@{t='必须会 5 条';c=$C.ink;bold=$false}, @{t='＋如果只记三件事';c=$C.green;bold=$true}) '这一讲的目标：能讲、能画、能量' 4
  $must = @('三个执行环境与它们各自的内核视图', 'GVA/GPA/HVA/HPA 四条线与 PVM 参数归属',
            'KVM_RUN 循环与「退出 ≠ 返回」', '快照四件套 + 暂停三完成点 + 恢复按需加载',
            '四道门：namespace / cgroup / seccomp / 降权')
  $y = 240
  T $g '必须会' $M 240 12.5 $C.ink $true 200 | Out-Null
  $y = 270
  for ($i = 0; $i -lt 5; $i++) {
    Rect $g $M $y 820 62 '#FFFFFF' $C.line 1 10
    T $g ([string]($i + 1)) ($M + 16) ($y + 18) 14 $C.green $true 26 | Out-Null
    T $g $must[$i] ($M + 52) ($y + 20) 12.5 $C.body $false 750 | Out-Null
    $y += 72
  }
  Rect $g 920 240 624 356 '#FFFFFF' $C.line 1 12
  T $g '如果只记三件事' 940 258 13 $C.ink $true 400 | Out-Null
  $three = @('三个执行环境：只有 Guest 有独立内核', '每层都有自己的完成点，问「完成了吗」先问哪一层', '暂停、快照、恢复是三件事，各有完成点')
  $yy = 292
  foreach ($t in $three) {
    Rect $g 940 $yy 584 88 $C.greenBg2 $C.green 1 10
    T $g $t (956) ($yy + 16) 12 $C.green $false 552 | Out-Null
    $yy += 100
  }
  Rect $g $M 636 1488 96 $C.grayBg $null 0 10
  T $g '下一步复习建议' ($M + 20) 652 12.5 $C.ink $true 300 | Out-Null
  T $g '① 先用第 27 页数字自测；② 再答第 28 页三题；③ 最后把「一次读六层」画一遍。' ($M + 20) 680 12 $C.body $false 1440 | Out-Null
  Footer $g '能讲、能画、能量：三样齐了才算会' 29 $TOTAL
}

# ---- 30 附录 ----
$pages += {
  param($g)
  Header $g '04 总结' @(@{t='考前 10 分钟看这一页：';c=$C.ink;bold=$false}, @{t='术语 + 易混 + 答案';c=$C.green;bold=$true}) '三栏速查，不解释原理，只对齐口径' 4
  # 术语
  Rect $g $M 240 486 470 '#FFFFFF' $C.line 1 12
  T $g '术语速查' ($M + 18) 256 12.5 $C.green $true 300 | Out-Null
  $terms = @(@('GPA', 'Guest 认为的物理地址'), @('HVA', '宿主某进程的虚拟地址'), @('memslot', 'GPA 区间与 HVA 区间的登记'),
             @('VM-Exit', 'Guest → 宿主执行环境'), @('vCPU', '一个宿主线程 + 一个 KVM vCPU'), @('rootfs', 'Guest 里 / 的整棵目录树'),
             @('ublk', '内核出壳、用户态给内容的块设备'))
  $yy = 286
  foreach ($t in $terms) { T $g $t[0] ($M + 18) $yy 11.5 $C.ink $true 90 | Out-Null; T $g $t[1] ($M + 118) $yy 11.5 $C.body $false 350 | Out-Null; $yy += 34 }
  # 易混
  Rect $g 560 240 486 470 '#FFFFFF' $C.line 1 12
  T $g '易混清单' (578) 256 12.5 $C.red $true 300 | Out-Null
  $pairs = @(@('VM-Exit', 'KVM_RUN 返回'), @('暂停完成', '快照完成'), @('领取完成', '数据读完'), @('文件偏移', '磁盘偏移'),
             @('映射了', '分配了'), @('只读设备', '不共享页缓存'), @('namespace', '降权'), @('health 通过', '鉴权通过'))
  $yy = 286
  foreach ($p in $pairs) {
    T $g $p[0] (578) $yy 11 $C.red $false 230 | Out-Null
    T $g '≠' (816) $yy 11 $C.dim $false 20 | Out-Null
    T $g $p[1] (838) $yy 11 $C.green $false 190 | Out-Null
    $yy += 34
  }
  # 答案
  Rect $g 1060 240 484 470 '#FFFFFF' $C.line 1 12
  T $g '第 28 页练习答案' 1078 256 12.5 $C.green $true 400 | Out-Null
  T $g '1. 至少 4 个线程：vmm 主线程、api 线程、fc_vcpu 0/1。' 1078 286 11.5 $C.body $false 450 | Out-Null
  T $g '2. 通常不会为这批数据发 virtio 请求；但路径解析、元数据、并发预读仍可能产生 IO，所以不能断言整次零设备请求。' 1078 318 11.5 $C.body $false 450 | Out-Null
  T $g '3. 先查两点：全部 vCPU 是否确认（暂停是否完成）、内存层与状态文件是否写完并 fsync。pause 成功而捕获失败，也会表现为「快照失败」。' 1078 384 11.5 $C.body $false 450 | Out-Null
  T $g '口径说明：数字单位为常用值；不同内核/版本可能变化，以教材与老师口径为准。' $M 730 11.5 $C.dim $false 1488 | Out-Null
  Footer $g '考前只看这一页：术语对齐、易混点、三道题答案' 30 $TOTAL
}

# ---------------- 渲染 ----------------
$i = 0
foreach ($p in $pages) {
  $i++
  $name = 'p{0:d2}.png' -f $i
  $path = Join-Path $OUT $name
  $pg = NewPage $path
  try { & $p $pg.g } catch { Note ("PAGE {0} 绘制失败: {1}`n{2}" -f $i, $_.Exception.Message, $_.ScriptStackTrace) }
  SavePage $pg
  Note ("saved {0}" -f $name)
}
Note ("total pages: {0}" -f $i)
Note ("output: {0}" -f $OUT)
