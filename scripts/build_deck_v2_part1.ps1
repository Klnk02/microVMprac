#requires -Version 5.1
<#
  AgentENV 复习课件 v2（27 页）—— 内容按「课件-内容稿.md」排
  版式：左上章节胶囊 + 33px 结论标题 + 左侧模拟图/数据图 + 右侧 4 条知识点 + 底部易错/只记一件事
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'deck_core.ps1')

$TOTAL = 27
$LOG = New-Object System.Collections.Generic.List[string]
function Note($s) { $LOG.Add($s); Write-Host $s }

$ROOT = $PSScriptRoot
$OUT = Join-Path (Split-Path -Parent $ROOT) '04-AgentENV\图片-27页'
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

# ---------------- 版式骨架 ----------------
function ContentPage {
  param($g, [string]$section, $titleParts, [string]$subtitle, [int]$navIndex,
        $points, [string]$mistake, [string]$selftest, [string]$onlyone,
        [scriptblock]$drawFig, [scriptblock]$drawData, [int]$no)

  Header $g $section $titleParts $subtitle $navIndex

  # 左：图示面板
  $px = $M; $py = $CONTENT_TOP; $pw = 700; $ph = 560
  Rect $g $px $py $pw $ph '#FFFFFF' $C.line 1 12
  T $g '模拟图' ($px + 16) ($py + 12) 12 $C.dim $true 300 | Out-Null
  L $g ($px + 16) ($py + 28) ($px + 150) ($py + 28) $C.line 1
  & $drawFig $g ($px + 16) ($py + 40) ($pw - 32) 258
  L $g ($px + 16) ($py + 306) ($px + $pw - 16) ($py + 306) $C.line 1
  T $g '数据图' ($px + 16) ($py + 316) 12 $C.dim $true 300 | Out-Null
  & $drawData $g ($px + 16) ($py + 344) ($pw - 32) 200

  # 右：4 条知识点
  $cx = 776; $cw = 768; $cy = $CONTENT_TOP; $ch = 128; $gap = 13
  for ($i = 0; $i -lt $points.Count -and $i -lt 4; $i++) {
    $yy = $cy + $i * ($ch + $gap)
    Rect $g $cx $yy $cw $ch '#FFFFFF' $C.line 1 10
    Rect $g $cx $yy 5 $ch $C.green $null 0 2
    T $g ([string]($i + 1)) ($cx + 14) ($yy + 12) 20 $C.green $true 26 | Out-Null
    T $g $points[$i][0] ($cx + 44) ($yy + 14) 12.5 $C.ink $true ($cw - 60) | Out-Null
    T $g $points[$i][1] ($cx + 44) ($yy + 40) 11.5 $C.body $false ($cw - 62) | Out-Null
  }

  # 底部：易错 + 只记一件事
  $by = 782
  Rect $g $M $by 896 50 $C.redBg $C.red 1 10
  Rect $g $M $by 5 50 $C.red $null 0 2
  T $g '易错  ' ($M + 16) ($by + 15) 11.5 $C.red $true 60 | Out-Null
  T $g $mistake ($M + 62) ($by + 15) 11.5 $C.body $false 820 | Out-Null

  Rect $g 968 $by 576 50 $C.greenBg1 $C.green 1 10
  Rect $g 968 $by 5 50 $C.green $null 0 2
  T $g '只记一件事  ' (984) ($by + 15) 11.5 $C.green $true 90 | Out-Null
  T $g $onlyone (1078) ($by + 15) 11.5 $C.body $false 458 | Out-Null

  Footer $g ("自测：" + $selftest) $no $TOTAL
}

# ---------------- 图示库 ----------------
function fig_map { param($g, $x, $y, $w, $h)
  $names = @('位置', '地址', '执行', '存储', '状态', '平台')
  $tags = @('先学', '先学', '后学', '后学', '易混', '易混')
  $cols = @($C.green, $C.green, $C.orange, $C.orange, $C.red, $C.red)
  $bw = ($w - 2 * 12) / 3; $bh = 74
  for ($i = 0; $i -lt 6; $i++) {
    $bx = $x + ($i % 3) * ($bw + 12); $by = $y + [Math]::Floor($i / 3) * ($bh + 58)
    Rect $g $bx $by $bw $bh '#FFFFFF' $C.line 1 10
    Rect $g $bx $by 4 $bh $cols[$i] $null 0 2
    T $g $names[$i] ($bx + 14) ($by + 12) 15 $C.ink $true ($bw - 28) | Out-Null
    Chip $g ($bx + 14) ($by + 44) $tags[$i] $cols[$i] $C.grayBg 56 22 | Out-Null
    if ($i % 3 -lt 2) { Arrow $g ($bx + $bw + 2) ($by + 37) ($bx + $bw + 10) ($by + 37) $C.arrow 1.4 }
  }
  Arrow $g ($x + $bw / 2) ($y + $bh + 2) ($x + $bw / 2) ($y + $bh + 52) $C.arrow 1.4
  Arrow $g ($x + $bw / 2 + 4) ($y + $bh + 2) ($x + $bw + 12 + $bw / 2 - 4) ($y + $bh + 52) $C.arrow 1.4
  Arrow $g ($x + $bw * 2 + 24) ($y + $bh + 2) ($x + $bw * 2 + 24) ($y + $bh + 52) $C.arrow 1.4
}

function fig_layers3 { param($g, $x, $y, $w, $h)
  $rows = @(
    @('宿主用户态（3 个进程）', @('server', 'firecracker', 'ublk-daemon'), $C.green),
    @('宿主内核（功能，无 PID）', @('KVM', 'ublk 驱动', 'cgroup/seccomp'), $C.orange),
    @('Guest（独立内核）', @('Guest 内核', 'envd', '你的程序'), $C.red))
  $rh = 62; $gap = 26
  for ($i = 0; $i -lt 3; $i++) {
    $by = $y + $i * ($rh + $gap)
    T $g $rows[$i][0] $x ($by - 14) 11.5 $C.dim $true 300 | Out-Null
    $bw = ($w - 2 * 10) / 3
    for ($j = 0; $j -lt 3; $j++) {
      Rect $g ($x + $j * ($bw + 10)) $by $bw $rh '#FFFFFF' $rows[$i][2] 1 8
      T $g $rows[$i][1][$j] ($x + $j * ($bw + 10) + 8) ($by + 20) 12 $C.ink $false ($bw - 16) | Out-Null
    }
  }
}

function fig_dualpath { param($g, $x, $y, $w, $h)
  $bw = 108; $bh = 46
  Rect $g $x $y $bw $bh '#FFFFFF' $C.green 1.5 8
  T $g 'GVA' $x ($y + 14) 12.5 $C.green $true $bw 'center' | Out-Null
  Rect $g $x ($y + 74) $bw $bh '#FFFFFF' $C.green 1.5 8
  T $g 'GPA' $x ($y + 88) 12.5 $C.green $true $bw 'center' | Out-Null
  Rect $g ($x + $w / 2 - 70) ($y + 46) 140 $bh $C.greenBg1 $C.green 1.5 8
  T $g 'HPA' ($x + $w / 2 - 70) ($y + 60) 13 $C.green $true 140 'center' | Out-Null
  Rect $g ($x + $w - $bw) $y $bw $bh '#FFFFFF' $C.orange 1.5 8
  T $g 'HVA' ($x + $w - $bw) ($y + 14) 12.5 $C.orangeDk $true $bw 'center' | Out-Null
  Arrow $g ($x + $bw / 2) ($y + $bh) ($x + $bw / 2) ($y + 72) $C.arrow 1.4
  Arrow $g ($x + $bw) ($y + 96) ($x + $w / 2 - 74) ($y + 72) $C.arrow 1.4
  Arrow $g ($x + $w - $bw) ($y + $bh) ($x + $w / 2 + 74) ($y + 62) $C.arrow 1.4
  T $g 'Guest 页表' ($x + $bw + 8) ($y + 92) 11.5 $C.dim $false 90 | Out-Null
  T $g 'EPT' ($x + $bw + 8) ($y + 12) 11.5 $C.dim $false 60 | Out-Null
  T $g '宿主页表' ($x + $w - $bw - 90) ($y + 60) 11.5 $C.dim $false 90 | Out-Null
  T $g 'memslot：GPA 区间 - HVA 区间（登记，不复制）' $x ($y + 136) 11.5 $C.green $true ($w - 8) | Out-Null
  T $g '两条路径落在同一物理页 - 没有“两份内存”' $x ($y + 160) 11.5 $C.body $false ($w - 8) | Out-Null
}

function fig_switches { param($g, $x, $y, $w, $h)
  $rows = @(@('KVM_RUN 系统调用', '换特权级，线程不变', $C.green), @('VM-Entry / VM-Exit', '硬件存/取现场，线程不变', $C.orange), @('宿主线程切换', '调度器换线程 = 真没拿到 CPU', $C.red))
  $rh = 54; $gap = 22
  for ($i = 0; $i -lt 3; $i++) {
    $by = $y + $i * ($rh + $gap)
    Rect $g $x $by ($w * 0.36) $rh '#FFFFFF' $rows[$i][2] 1.5 8
    T $g $rows[$i][0] ($x + 10) ($by + 18) 12 $C.ink $true ($w * 0.36 - 20) | Out-Null
    T $g $rows[$i][1] ($x + $w * 0.38 + 10) ($by + 18) 12 $C.body $false ($w * 0.6) | Out-Null
    if ($i -lt 2) { Arrow $g ($x + $w * 0.18) ($by + $rh) ($x + $w * 0.18) ($by + $rh + $gap - 2) $C.arrow 1.2 }
  }
}

function fig_threads { param($g, $x, $y, $w, $h)
  $bw = $w * 0.52
  Rect $g $x $y $bw $h '#FFFFFF' $C.green 1.5 10
  T $g 'firecracker（一个地址空间）' ($x + 12) ($y + 10) 11.5 $C.green $true ($bw - 24) | Out-Null
  $items = @(@('vmm 主线程', '协调 / 设备事件'), @('api 线程', 'Unix socket'), @('fc_vcpu 0', 'KVM_RUN'), @('fc_vcpu 1', 'KVM_RUN'))
  for ($i = 0; $i -lt 4; $i++) {
    $by = $y + 36 + $i * 54
    Rect $g ($x + 12) $by ($bw - 24) 46 $C.grayBg $null 0 6
    T $g $items[$i][0] ($x + 22) ($by + 8) 11.5 $C.ink $true 160 | Out-Null
    T $g $items[$i][1] ($x + 22) ($by + 26) 11 $C.dim $false 200 | Out-Null
  }
  $rx = $x + $bw + 24
  T $g 'Barrier::new(vcpu_count + 1)' $rx ($y + 10) 11.5 $C.green $true ($w - $bw - 30) | Out-Null
  T $g '主线程也 wait()：所有 vCPU 完成 TLS 初始化后才发启动' $rx ($y + 34) 11.5 $C.body $false ($w - $bw - 30) | Out-Null
  T $g '.name("fc_vcpu {i}") 写死，所以 ps -eLf 看得到' $rx ($y + 96) 11.5 $C.body $false ($w - $bw - 30) | Out-Null
  T $g '线程在 KVM_RUN 里 ≠ 空闲：CPU 可能正在跑 Guest' $rx ($y + 140) 11.5 $C.red $false ($w - $bw - 30) | Out-Null
}

function fig_channels { param($g, $x, $y, $w, $h)
  $bw = ($w - 20) / 2
  Rect $g $x $y $bw ($h * 0.62) '#FFFFFF' $C.green 1.5 10
  T $g '控制面' ($x + 14) ($y + 10) 15 $C.green $true 120 | Out-Null
  T $g '宿主 Unix socket（--api-sock）' ($x + 14) ($y + 36) 11.5 $C.ink $false ($bw - 28) | Out-Null
  T $g 'PATCH /vm · PUT /snapshot/load · GET dirty-ranges' ($x + 14) ($y + 60) 11 $C.body $false ($bw - 28) | Out-Null
  T $g '不需要 Guest 配合' ($x + 14) ($y + 88) 11.5 $C.green $true ($bw - 28) | Out-Null
  $x2 = $x + $bw + 20
  Rect $g $x2 $y $bw ($h * 0.62) '#FFFFFF' $C.orange 1.5 10
  T $g '数据面' ($x2 + 14) ($y + 10) 15 $C.orangeDk $true 120 | Out-Null
  T $g 'Guest RAM 里的 virtqueue' ($x2 + 14) ($y + 36) 11.5 $C.ink $false ($bw - 28) | Out-Null
  T $g '描述符 + avail + used + 门铃' ($x2 + 14) ($y + 60) 11 $C.body $false ($bw - 28) | Out-Null
  T $g '需要 Guest 驱动参与' ($x2 + 14) ($y + 88) 11.5 $C.orangeDk $true ($bw - 28) | Out-Null
  T $g '所以暂停绝不能走数据面：Guest 卡死时它就不动了' $x ($y + $h * 0.68) 11.5 $C.red $false ($w - 4) | Out-Null
}

function fig_virtio { param($g, $x, $y, $w, $h)
  $bw = ($w - 24) / 3
  $items = @(@('描述符表', '16 字节：addr/len/flags/next', $C.green), @('avail 环', 'Guest 发布链头', $C.green), @('used 环', '设备发布完成', $C.orange))
  for ($i = 0; $i -lt 3; $i++) {
    $bx = $x + $i * ($bw + 12)
    Rect $g $bx $y $bw 82 '#FFFFFF' $items[$i][2] 1.5 10
    T $g $items[$i][0] ($bx + 10) ($y + 12) 12.5 $C.ink $true ($bw - 20) | Out-Null
    T $g $items[$i][1] ($bx + 10) ($y + 40) 11 $C.body $false ($bw - 20) | Out-Null
    if ($i -lt 2) { Arrow $g ($bx + $bw + 1) ($y + 41) ($bx + $bw + 10) ($y + 41) $C.arrow 1.2 }
  }
  T $g '门铃只提醒「去检查队列」：不带数据，一次通知可对应多项工作' $x ($y + 100) 11.5 $C.green $true ($w - 4) | Out-Null
  T $g '设备发布 used ≠ Guest 驱动已处理（还差中断注入与调度）' $x ($y + 126) 11.5 $C.red $false ($w - 4) | Out-Null
}

function fig_ladder { param($g, $x, $y, $w, $h)
  $tiers = @(@('① API socket 可用', '能配 VM、能 pause', 0.78, $C.green), @('② 网络可达', 'tap0 能到 Guest', 0.58, $C.green), @('③ /health 通过', '应用层能应答', 0.40, $C.orange))
  for ($i = 0; $i -lt 3; $i++) {
    $by = $y + $i * 72
    $bw = $w * $tiers[$i][2]
    Rect $g $x $by $bw 58 '#FFFFFF' $tiers[$i][3] 1.5 10
    T $g $tiers[$i][0] ($x + 12) ($by + 10) 12 $C.ink $true ($bw - 24) | Out-Null
    T $g $tiers[$i][1] ($x + 12) ($by + 32) 11 $C.body $false ($bw - 24) | Out-Null
    T $g ('能证明：' + $(if ($i -eq 0) { 'VMM 起来' } elseif ($i -eq 1) { 'netns/端口' } else { '服务能应答' })) ($x + $bw + 8) ($by + 20) 11 $C.dim $false 180 | Out-Null
  }
}

function fig_timeline { param($g, $x, $y, $w, $h)
  $ev = @(@('t1', 'API 收到请求', $C.green), @('t2', '置暂停意图', $C.green), @('t3', 'vCPU0 确认', $C.green),
          @('t4', 'vCPU1 没被调度', $C.red), @('t5', 'vCPU1 确认', $C.green), @('t6', '暂停完成', $C.green))
  $gap = 8; $bw = ($w - $gap * 5) / 6
  for ($i = 0; $i -lt 6; $i++) {
    $bx = $x + $i * ($bw + $gap)
    Rect $g $bx $y $bw 76 '#FFFFFF' $ev[$i][2] 1.5 8
    T $g $ev[$i][0] ($bx + 8) ($y + 8) 11.5 $ev[$i][2] $true 40 | Out-Null
    T $g $ev[$i][1] ($bx + 8) ($y + 30) 11 $C.body $false ($bw - 16) | Out-Null
    if ($i -lt 5) { Arrow $g ($bx + $bw + 1) ($y + 38) ($bx + $bw + $gap - 1) ($y + 38) $C.arrow 1.2 }
  }
  T $g 't4 是关键：只是没拿到 CPU，调度器再给时间片它就会继续写 RAM' $x ($y + 92) 11.5 $C.red $true ($w - 4) | Out-Null
}

function fig_sixstep { param($g, $x, $y, $w, $h)
  $steps = @('read()', 'ext4 → LBA', 'virtio + 门铃', 'ublk 入队', 'daemon 取字节', '原路返回')
  $bw = ($w - 2 * 10) / 3; $bh = 62
  for ($i = 0; $i -lt 6; $i++) {
    $bx = $x + ($i % 3) * ($bw + 10); $by = $y + [Math]::Floor($i / 3) * ($bh + 44)
    Rect $g $bx $by $bw $bh '#FFFFFF' $(if ($i -lt 3) { $C.green } else { $C.orange }) 1.5 8
    T $g ([string]($i + 1)) ($bx + 8) ($by + 8) 14 $(if ($i -lt 3) { $C.green } else { $C.orange }) $true 20 | Out-Null
    T $g $steps[$i] ($bx + 32) ($by + 20) 12 $C.ink $true ($bw - 40) | Out-Null
    if ($i % 3 -lt 2) { Arrow $g ($bx + $bw + 1) ($by + 31) ($bx + $bw + 9) ($by + 31) $C.arrow 1.2 }
  }
  T $g '四个完成点：FETCH CQE 到 / COMMIT / used / read 返回' $x ($y + 172) 11.5 $C.green $true ($w - 4) | Out-Null
}

function fig_overlay { param($g, $x, $y, $w, $h)
  $layers = @(@('upper（可写）', '位置1 → 新值', $C.green), @('增量层（只读）', '位置3 → 显式零', $C.orange), @('基层（只读）', '位置0/1/2 有数据', $C.red))
  for ($i = 0; $i -lt 3; $i++) {
    $by = $y + $i * 56
    Rect $g $x $by ($w * 0.46) 46 '#FFFFFF' $layers[$i][2] 1.5 8
    T $g $layers[$i][0] ($x + 10) ($by + 6) 11.5 $C.ink $true ($w * 0.46 - 20) | Out-Null
    T $g $layers[$i][1] ($x + 10) ($by + 26) 11 $C.body $false ($w * 0.46 - 20) | Out-Null
  }
  $cx = $x + $w * 0.5
  $cw = ($w * 0.5 - 3 * 8) / 4
  $cells = @(@('位置0', '基层 A', $C.green), @('位置1', 'upper 新值', $C.green), @('位置2', '全零', $C.orange), @('位置3', '全零', $C.orange))
  for ($i = 0; $i -lt 4; $i++) {
    $bx = $cx + $i * ($cw + 8)
    Rect $g $bx $y $cw 76 '#FFFFFF' $cells[$i][2] 1.5 8
    T $g $cells[$i][0] ($bx + 6) ($y + 8) 11 $C.dim $false ($cw - 12) | Out-Null
    T $g $cells[$i][1] ($bx + 6) ($y + 32) 11.5 $C.ink $true ($cw - 12) | Out-Null
  }
  T $g '无记录 → 回落；显式零 → 终止（否则读回父层旧数据）' $x ($y + 190) 11.5 $C.red $false ($w - 4) | Out-Null
}

function fig_ublk { param($g, $x, $y, $w, $h)
  $nodes = @(@('/dev/ublk-control', '创建/删除'), @('/dev/ublkcN', '命令交接'), @('/dev/ublkbN', '数据读写（FC 挂这个）'))
  $bw = ($w - 2 * 10) / 3
  for ($i = 0; $i -lt 3; $i++) {
    $bx = $x + $i * ($bw + 10)
    Rect $g $bx $y $bw 58 '#FFFFFF' $C.orange 1.5 8
    T $g $nodes[$i][0] ($bx + 8) ($y + 8) 11.5 $C.ink $true ($bw - 16) | Out-Null
    T $g $nodes[$i][1] ($bx + 8) ($y + 30) 11 $C.body $false ($bw - 16) | Out-Null
  }
  $steps = @('等待 io_uring', '领取 CQE', '解析 OverlayBD', '提交 COMMIT')
  $bh = 50
  for ($i = 0; $i -lt 4; $i++) {
    $bx = $x + $i * ($bw + 10)
    Rect $g $bx ($y + 84) $bw $bh '#FFFFFF' $C.green 1.5 8
    T $g ([string]($i + 1)) ($bx + 8) ($y + 92) 13 $C.green $true 18 | Out-Null
    T $g $steps[$i] ($bx + 28) ($y + 100) 11.5 $C.ink $true ($bw - 36) | Out-Null
    if ($i -lt 3) { Arrow $g ($bx + $bw + 1) ($y + 109) ($bx + $bw + 9) ($y + 109) $C.arrow 1.2 }
  }
  T $g '「领取」的 CQE 只表示请求送到 daemon，不表示数据读完' $x ($y + 152) 11.5 $C.red $true ($w - 4) | Out-Null
}

function fig_trio { param($g, $x, $y, $w, $h)
  $trio = @(@('mmap 之后', '只有 VMA，无物理页', $C.green), @('第一次读', '缺页：给页或取页', $C.orange), @('第一次写', 'COW：复制私有页', $C.red))
  $bw = ($w - 2 * 12) / 3
  for ($i = 0; $i -lt 3; $i++) {
    $bx = $x + $i * ($bw + 12)
    Rect $g $bx $y $bw 86 '#FFFFFF' $trio[$i][2] 1.5 10
    T $g $trio[$i][0] ($bx + 10) ($y + 12) 12.5 $trio[$i][2] $true ($bw - 20) | Out-Null
    T $g $trio[$i][1] ($bx + 10) ($y + 40) 11 $C.body $false ($bw - 20) | Out-Null
    if ($i -lt 2) { Arrow $g ($bx + $bw + 2) ($y + 43) ($bx + $bw + 10) ($y + 43) $C.arrow 1.2 }
  }
  T $g '三层缺页：Guest 页表（Guest 内核）/ EPT（KVM）/ 宿主页表（宿主内核）' $x ($y + 104) 11.5 $C.ink $false ($w - 4) | Out-Null
  T $g '已核验：FC 1.12.1 memory.rs:136 用 MAP_PRIVATE → 读共享页缓存、写才 COW' $x ($y + 132) 11.5 $C.green $true ($w - 4) | Out-Null
}

function fig_quad4 { param($g, $x, $y, $w, $h, $items)
  $bw = ($w - 12) / 2; $bh = 76
  for ($i = 0; $i -lt 4; $i++) {
    $bx = $x + ($i % 2) * ($bw + 12); $by = $y + [Math]::Floor($i / 2) * ($bh + 14)
    Rect $g $bx $by $bw $bh '#FFFFFF' $items[$i][2] 1.5 8
    Rect $g $bx $by 4 $bh $items[$i][2] $null 0 2
    T $g $items[$i][0] ($bx + 12) ($by + 8) 12 $items[$i][2] $true ($bw - 24) | Out-Null
    T $g $items[$i][1] ($bx + 12) ($by + 32) 11 $C.body $false ($bw - 24) | Out-Null
  }
}

function fig_fivestep { param($g, $x, $y, $w, $h)
  $steps = @('检查 ublk', 'load_snapshot', '映射只读内存', '补配置', 'resume')
  $bw = ($w - 4 * 8) / 5
  for ($i = 0; $i -lt 5; $i++) {
    $bx = $x + $i * ($bw + 8)
    Rect $g $bx $y $bw 66 '#FFFFFF' $C.green 1.5 8
    T $g ([string]($i + 1)) ($bx + 8) ($y + 8) 13 $C.green $true 18 | Out-Null
    T $g $steps[$i] ($bx + 26) ($y + 16) 11.5 $C.ink $true ($bw - 34) | Out-Null
    if ($i -lt 4) { Arrow $g ($bx + $bw + 1) ($y + 33) ($bx + $bw + 7) ($y + 33) $C.arrow 1 }
  }
  T $g 'resume_vm=false：先把状态/设备/网络/额外盘装好，最后才让 vCPU 跑' $x ($y + 84) 11.5 $C.orangeDk $true ($w - 4) | Out-Null
  T $g '一页可访问 = GPA 缺项 → 只读设备块读 → daemon 查层 → 填页' $x ($y + 110) 11.5 $C.body $false ($w - 4) | Out-Null
}

function fig_formula { param($g, $x, $y, $w, $h)
  Rect $g $x $y $w 82 $C.greenBg1 $C.green 1.5 10
  $f = Font2 20 $true; $b = Brush $C.green
  $eq = 'HVA = userspace_addr + (目标 GPA - guest_phys_addr)'
  $ew = $g.MeasureString($eq, $f).Width
  $g.DrawString($eq, $f, $b, [single]($x + ($w - $ew) / 2), [single]($y + 30))
  $f.Dispose(); $b.Dispose()
  T $g '例：0x70000000 + (0x2000 - 0) = 0x70002000 → 直接当 PVM 的 remote' $x ($y + 96) 12 $C.ink $true ($w - 4) | Out-Null
  T $g '算出的是 Firecracker 的 HVA：不是 GVA，也不是 HPA' $x ($y + 124) 11.5 $C.red $false ($w - 4) | Out-Null
  T $g '只在同一条 memslot 内成立；跨段要先定位属于哪一段' $x ($y + 150) 11.5 $C.body $false ($w - 4) | Out-Null
}

function fig_example { param($g, $x, $y, $w, $h, $title, $sub)
  Rect $g $x $y ($w * 0.44) 130 '#FFFFFF' $C.line 1 10
  T $g $title ($x + 12) ($y + 10) 12 $C.dim $true 220 | Out-Null
  T $g $sub ($x + 12) ($y + 34) 11.5 $C.ink $false ($w * 0.44 - 24) | Out-Null
  $steps = @('定位语义', '列出还差的动作', '给出判据')
  for ($i = 0; $i -lt 3; $i++) {
    $bx = $x + $w * 0.48; $by = $y + $i * 46
    Rect $g $bx $by ($w * 0.52) 38 '#FFFFFF' $C.green 1 6
    T $g ([string]($i + 1)) ($bx + 8) ($by + 9) 13 $C.green $true 18 | Out-Null
    T $g $steps[$i] ($bx + 28) ($by + 10) 11.5 $C.body $false ($w * 0.52 - 36) | Out-Null
  }
}

function fig_mistakes { param($g, $x, $y, $w, $h)
  $rows = @('pids.max 挡 Guest fork', 'VM-Exit = KVM_RUN 返回', 'namespace = 降权', 'finalize+rename = 持久化', 'health = 鉴权', '只读设备 = 各自匿名页')
  $rh = 30
  for ($i = 0; $i -lt 6; $i++) {
    $by = $y + $i * $rh
    T $g '错' ($x + 2) ($by + 8) 12 $C.red $true 16 | Out-Null
    T $g $rows[$i] ($x + 20) ($by + 8) 11 $C.red $false ($w - 24) | Out-Null
  }
}

function fig_numcards { param($g, $x, $y, $w, $h, $nums)
  $bw = ($w - 4 * 8) / 5
  for ($i = 0; $i -lt 5; $i++) {
    $bx = $x + $i * ($bw + 8)
    Rect $g $bx $y $bw 96 '#FFFFFF' $C.line 1 10
    T $g $nums[$i][0] ($bx + 8) ($y + 10) 22 $C.green $true ($bw - 16) | Out-Null
    T $g $nums[$i][1] ($bx + 8) ($y + 42) 11 $C.green $false ($bw - 16) | Out-Null
    T $g $nums[$i][2] ($bx + 8) ($y + 62) 10.5 $C.body $false ($bw - 16) | Out-Null
  }
}

function fig_threeq { param($g, $x, $y, $w, $h)
  $qs = @(@('基础', '线程数与 Barrier', $C.green), @('进阶', '缓存命中还会不会发队列请求', $C.orange), @('易错', '如何判断快照失败原因', $C.red))
  for ($i = 0; $i -lt 3; $i++) {
    $by = $y + $i * 78
    Rect $g $x $by $w 66 '#FFFFFF' $C.line 1 10
    Chip $g ($x + 12) ($by + 10) $qs[$i][0] $qs[$i][2] $C.grayBg 62 22 | Out-Null
    T $g $qs[$i][1] ($x + 88) ($by + 12) 11.5 $C.ink $false ($w - 100) | Out-Null
    T $g '（作答区：留白）' ($x + 88) ($by + 36) 10.5 $C.dim $false 200 | Out-Null
  }
}


function fig_eventstream { param($g, $x, $y, $w, $h)
  $ev = @(@('start 请求', 'cmd + args + env + cwd'), @('Start{pid}', '进程已创建'), @('Data', 'stdout / stderr'), @('End{code}', '进程已退出'))
  $gap = 8; $bw = ($w - $gap * 3) / 4
  for ($i = 0; $i -lt 4; $i++) {
    $bx = $x + $i * ($bw + $gap)
    Rect $g $bx $y $bw 72 '#FFFFFF' $(if ($i -lt 3) { $C.green } else { $C.red }) 1.5 8
    T $g $ev[$i][0] ($bx + 8) ($y + 8) 11.5 $C.ink $true ($bw - 16) | Out-Null
    T $g $ev[$i][1] ($bx + 8) ($y + 32) 10.5 $C.body $false ($bw - 16) | Out-Null
    if ($i -lt 3) { Arrow $g ($bx + $bw + 1) ($y + 36) ($bx + $bw + $gap - 1) ($y + 36) $C.arrow 1.2 }
  }
  T $g '判断一：事件收齐了吗（收到 End = Ok）' $x ($y + 90) 11.5 $C.green $true ($w * 0.48) | Out-Null
  T $g '判断二：exit_code 是否为 0' ($x + $w * 0.52) ($y + 90) 11.5 $C.green $true ($w * 0.48) | Out-Null
  T $g '成功 = wait 返回 Ok + 收到 End + 退出码符合预期' $x ($y + 118) 11.5 $C.ink $false ($w - 4) | Out-Null
}

function fig_twochains { param($g, $x, $y, $w, $h)
  T $g '出站（Guest 主动连外面）' $x $y 11.5 $C.orangeDk $true 320 | Out-Null
  $out = @('eth0', 'tap0', 'SNAT', 'veth', 'MASQ')
  $bw = ($w - 4 * 8) / 5
  for ($i = 0; $i -lt 5; $i++) {
    $bx = $x + $i * ($bw + 8)
    Rect $g $bx ($y + 22) $bw 44 '#FFFFFF' $C.orange 1.5 8
    T $g $out[$i] ($bx + 6) ($y + 32) 11.5 $C.ink $true ($bw - 12) | Out-Null
    if ($i -lt 4) { Arrow $g ($bx + $bw + 1) ($y + 43) ($bx + $bw + 7) ($y + 43) $C.arrow 1 }
  }
  T $g '入站（宿主访问 envd）' $x ($y + 82) 11.5 $C.green $true 320 | Out-Null
  $inn = @('server', 'veth', 'DNAT', 'tap0→FC', 'envd')
  for ($i = 0; $i -lt 5; $i++) {
    $bx = $x + $i * ($bw + 8)
    Rect $g $bx ($y + 104) $bw 44 '#FFFFFF' $C.green 1.5 8
    T $g $inn[$i] ($bx + 6) ($y + 114) 11.5 $C.ink $true ($bw - 12) | Out-Null
    if ($i -lt 4) { Arrow $g ($bx + $bw + 1) ($y + 125) ($bx + $bw + 7) ($y + 125) $C.arrow 1 }
  }
  T $g '同名 tap0 不冲突：netns 先隔开，slot 地址再区分实例' $x ($y + 168) 11.5 $C.red $false ($w - 4) | Out-Null
}

function fig_threecols { param($g, $x, $y, $w, $h)
  $cols = @(@('术语 7 条', 'GPA / HVA / memslot / VM-Exit / vCPU / rootfs / ublk', $C.green), @('易混 8 对', '返回≠退出 / 暂停≠快照 / 领取≠读完 / 映射≠分配', $C.red), @('练习答案', '4 线程 / 不发请求但仍有 IO / 两个完成点', $C.orange))
  $bw = ($w - 2 * 12) / 3
  for ($i = 0; $i -lt 3; $i++) {
    $bx = $x + $i * ($bw + 12)
    Rect $g $bx $y $bw 110 '#FFFFFF' $cols[$i][2] 1.5 10
    T $g $cols[$i][0] ($bx + 10) ($y + 10) 12.5 $cols[$i][2] $true ($bw - 20) | Out-Null
    T $g $cols[$i][1] ($bx + 10) ($y + 38) 11 $C.body $false ($bw - 20) | Out-Null
  }
  T $g '考前只看这三栏：术语对齐、易混分清、答案复核' $x ($y + 128) 11.5 $C.dim $false ($w - 4) | Out-Null
}

# ---------------- 数据图 ----------------
function data_bars { param($g, $x, $y, $w, $h, $items, $maxV, $accent)
  BarsV $g $x ($y + 10) $w ($h - 20) $items $maxV $accent
}
function data_table { param($g, $x, $y, $w, $h, $header, $rows, $rh)
  MiniTable $g $x $y $w $header $rows $rh
}
function data_stack { param($g, $x, $y, $w, $h)
  StackBar $g $x ($y + 20) $w 34 @(@('addr 8 B', (8.0 / 16), $C.green), @('len 4 B', (4.0 / 16), $C.orange), @('flags 2 B', (2.0 / 16), $C.red), @('next 2 B', (2.0 / 16), $C.dim))
  T $g '一个 VirtIO 描述符 = 16 字节' ($x) ($y + 82) 11.5 $C.ink $true 300 | Out-Null
}
