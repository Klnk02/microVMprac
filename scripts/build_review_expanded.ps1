#requires -Version 5.1
param([switch]$Compact)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$base=Join-Path (Split-Path $PSScriptRoot -Parent) '04-AgentENV'
$out=Join-Path $base '图片-27页-机制详解版'
if($Compact){$out=Join-Path $base '图片-27页-紧凑图解版'}
New-Item -ItemType Directory -Force $out | Out-Null
# Load the content additions without running the previous package writer.
$add=[IO.File]::ReadAllText("$PSScriptRoot/enrich_27_review.ps1")
$start=$add.IndexOf('$supp=@(');$end=$add.IndexOf('if($supp.Count')
Invoke-Expression $add.Substring($start,$end-$start)
$core=[IO.File]::ReadAllText("$PSScriptRoot/deck_core.ps1")
$core=$core.Substring(0,$core.IndexOf('# ---------------- 内容 ----------------'))
# Original WrapText returned a nested collection, causing whole paragraphs to run off-canvas.
$core=$core.Replace('return ,$lines','return $lines.ToArray()')
$core=[regex]::Replace($core,'\$W\b','$script:W')
$core=[regex]::Replace($core,'\$H\b','$script:H')
$core=$core.Replace('$s = $size','$s = [Math]::Max(11.5,$size)')
$core=$core.Replace('T $g $points[$i][1]','T $g ($points[$i][1] + "`n" + $supp[$no-1][$i])')
$core=$core.Replace('T $g $notes[$i][1] ($cx + 14)', 'T $g ($notes[$i][1] + "`n" + $supp[$no-1][[Math]::Min(3,$i+1)]) ($cx + 14)')
Invoke-Expression $core
function WrapText {
 param($g,[string]$text,$font,[double]$maxW)
 $lines=New-Object 'System.Collections.Generic.List[string]'
 foreach($para in ($text -split "`n")){
  $cur=''
  foreach($match in [regex]::Matches($para,'[A-Za-z0-9_]+|.')){
   $token=$match.Value
   if($g.MeasureString($token,$font).Width -gt $maxW){$tokens=$token.ToCharArray()}else{$tokens=@($token)}
   foreach($piece in $tokens){
    $try=$cur+$piece
    if($cur -ne '' -and $g.MeasureString($try,$font).Width -gt $maxW){$lines.Add($cur.TrimEnd());$cur=([string]$piece).TrimStart()}else{$cur=$try}
   }
  }
  $lines.Add($cur)
 }
 return $lines.ToArray()
}
$part=[IO.File]::ReadAllText("$PSScriptRoot/build_deck_v2_part1.ps1")
$part=$part.Substring($part.IndexOf('$TOTAL = 27'))
$part=$part.Replace('$ROOT = $PSScriptRoot','$ROOT = "D:/learning/Learning/microVMprac/scripts"'); $part=$part.Replace('$OUT =','$unusedOut ='); Invoke-Expression $part
$OUT2=$out
function CoverPage {
 param($g,$titleParts,$subtitle,$goals,$keywords,$chain,[int]$no)
 Header $g '01 总览' @(@{t='AgentENV 机制复习：';c=$C.ink;bold=$false},@{t='沿着请求看清整台沙箱';c=$C.green;bold=$true}) '从进程、地址、设备到快照：每条链都标出执行者、数据位置与完成条件' 1
 Rect $g 56 222 580 540 $C.greenBg2 $C.line 1 10
 T $g '复习时持续回答三个问题' 78 242 21 $C.green $true 535|Out-Null
 $items=@(@('谁在执行？','server、VMM、daemon、Guest 应用分别由谁的内核调度？不要把内核机制画成一个服务进程。'),@('字节在哪里？','请求描述、通知、数据 buffer 是三种对象；每一根箭头都应说明发生复制、映射还是消息传递。'),@('何时算完成？','领取任务、读出字节、设备完成、应用返回各自成立；暂停、快照完成、持久化也要分别确认。'))
 for($i=0;$i -lt 3;$i++){$y=302+$i*131;T $g $items[$i][0] 78 $y 18 $C.green $true 525|Out-Null;T $g $items[$i][1] 78 ($y+36) 15 $C.body $false 525|Out-Null}
 T $g '知识结构：先建立位置与地址，再追踪执行、存储和状态' 660 230 17 $C.ink $true 865|Out-Null
 $nodes=@(@('01 位置','Host / Guest 与进程边界'),@('02 地址','GVA / GPA / HVA / HPA'),@('03 执行','KVM_RUN 与退出分流'),@('04 存储','VirtIO / ublk / OverlayBD'),@('05 状态','pause / 快照 / 按需恢复'),@('06 边界','隔离 / 回收 / 性能口径'))
 for($i=0;$i -lt 6;$i++){$x=660+($i%2)*449;$y=280+[math]::Floor($i/2)*128;Rect $g $x $y 430 108 $C.white $C.line 1 10;T $g $nodes[$i][0] ($x+16) ($y+16) 18 $C.green $true 397|Out-Null;T $g $nodes[$i][1] ($x+16) ($y+56) 14 $C.body $false 397|Out-Null}
 Rect $g 660 682 879 80 $C.orangeBg $C.orange 1 10
 T $g '使用方式：看图复述 → 解释机制 → 换条件验证 → 对照易错点' 678 700 15 $C.orangeDk $true 843|Out-Null
 T $g '示例地址与数字注明假设；源码配置以实际部署版本为准。' 678 729 12 $C.body $false 843|Out-Null
 Footer $g '学习目标：能把一条链路从头讲到完成，并说明失效边界。' 1 27
}
function AppendixPage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$cols,$mistake,$selftest,$onlyone,[int]$no)
 Header $g $section $titleParts '术语解释、易混辨析与参考答案分栏查询；先完成第 25 页再看答案' $nav
 $rows=@(
 @('GPA：Guest 物理地址；不是机器真实物理地址。','HVA：某个 Host 进程里的虚拟地址，必须注明进程。','HPA：Host 实际物理地址，由宿主内存管理维护。','memslot：GPA 区间与 VMM HVA 区间的软件登记。','EPT：CPU 二阶段页表，完成 GPA→HPA。','TLB：缓存地址翻译；组合项可避免重新走两级页表。','rootfs：Guest 看到的根文件系统，不包含完整运行现场。','ublk：内核块设备接口与用户态后端协作服务块请求。'),
 @('VM-Exit / KVM_RUN 返回：硬件退出不一定回用户态。','pause / 快照：停止 vCPU 不等于保存完整状态。','FETCH / READ：前者交付任务，后者交付数据字节。','mmap / RSS：虚拟映射范围不等于物理驻留量。','COW / 按需加载：分别控制写入隔离和取页时机。','Guest / Host 缓存：Host 命中仍可能经过 Guest 设备链。','namespace / 降权：可见范围与权限能力应分别说明。','CPU / wall：减少运行时间不保证总延迟下降。'),
 @('① 线程题：基础模型 N+2；N=2 时为 VMM、API 与两个 vCPU 线程。其他配置可有辅助线程。','Barrier 的 +1 是主线程。所有参与者到达后，初始化同步点才放行。','② 缓存题：命中 Guest 页缓存时，不必为这批数据发设备请求；仍可能有路径、元数据、预读 IO。','反例：只命中 Host 缓存时，Guest 仍可能先发 virtio 请求。','③ 快照题：先查全部 vCPU 是否确认停止，再查状态与内存层是否写完、父层引用是否完整。','若 pause 成功而磁盘写满，结果是“已暂停、快照保存失败”，不能把两步合为一个状态。','配置口径：白名单条数、超时值和映射标志必须按版本核对；示例数据不是实测。')
 )
 for($i=0;$i -lt 3;$i++){$x=56+$i*501;Rect $g $x 218 486 548 $C.white $C.line 1 10;T $g $(if($i -eq 0){'术语速查（8 条）'}else{$cols[$i][0]}) ($x+16) 234 17 $C.green $true 450|Out-Null;$y=280;foreach($r in $rows[$i]){$hh=T $g $r ($x+16) $y 14 $C.body $false 450;$y+=$hh+19;if($y -gt 765){throw "Appendix overflow column $i"}}}
 EndStrips $g $mistake $onlyone $selftest $no
}
# Correct schematic: hardware translation and Host virtual access are parallel paths.
function fig_dualpath {param($g,$x,$y,$w,$h)
 $labels=@(@('Guest 应用 GVA','Guest 页表 → GPA','EPT → 同一 HPA'),@('VMM 指针 HVA','宿主页表','→ 同一 HPA'))
 for($r=0;$r -lt 2;$r++){
  for($j=0;$j -lt 3;$j++){
   $xx=$x+$j*($w/3);$yy=$y+12+$r*85
   Rect $g $xx $yy ($w/3-12) 53 $C.greenBg2 $C.line 1 8
   T $g $labels[$r][$j] ($xx+10) ($yy+17) 12 $C.green $true ($w/3-30)|Out-Null
   if($j -lt 2){Arrow $g ($xx+$w/3-10) ($yy+26) ($xx+$w/3-2) ($yy+26) $C.arrow 1}
  }
 }
 T $g 'memslot 登记 GPA↔HVA；它不是 CPU 逐次访存的中间步骤。' $x ($y+192) 12 $C.body $false $w|Out-Null
}
# Replace empty formula-page lower half with an actual cross-process vector example.
$oldFormula=${function:FormulaPage}
function FormulaPage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$formula,$vars,$example,$notes,$mistake,$selftest,$onlyone,[int]$no)
 & $oldFormula @PSBoundParameters
 Rect $g 56 524 1488 236 $C.grayBg $C.line 1 10
 T $g '跨进程读取：一个 PID + 两组属于不同地址空间的 iovec' 74 540 14 $C.green $true 1400|Out-Null
 $items=@(@('远程源：Firecracker','PID=1234（假设）`nremote.iov_base = 0x70002000`nremote.iov_len = 4096'),@('内核执行 process_vm_readv','按 PID 找到远程地址空间`n检查权限与可访问范围`n复制远程字节至调用者本地缓冲'),@('本地目的：server','local.iov_base = server 的 buffer`nlocal.iov_len = 4096`n返回值 = 实际复制字节数'))
 for($i=0;$i -lt 3;$i++){
  $x=74+$i*492
  Rect $g $x 573 470 134 $C.white $C.line 1 8
  T $g $items[$i][0] ($x+12) 585 13 $C.ink $true 442|Out-Null
  T $g ($items[$i][1].Replace('`n',"`n")) ($x+12) 613 12 $C.body $false 442|Out-Null
  if($i -lt 2){Arrow $g ($x+472) 639 ($x+489) 639 $C.arrow 1}
 }
 T $g '短读必须处理：返回 2048 只完成半个 4 KiB 请求；HVA 合法不保证整段始终可读。' 74 724 12 $C.orangeDk $true 1430|Out-Null
}
$src=[IO.File]::ReadAllText("$PSScriptRoot/build_deck_v3_pages.ps1")
$src=$src.Substring($src.IndexOf('$pages = @()'))
$src=$src.Substring(0,$src.IndexOf('# ---------------- 渲染 ----------------'))
# Fix misleading or overly absolute statements while retaining the source's visual language.
$src=$src.Replace('设备按描述符把数据写进条 Guest RAM','设备按描述符把数据写进 Guest RAM')
$src=$src.Replace('模拟真实设备时每个寄存器访问都是一次 VM-Exit；VirtIO 把数据批量放共享内存，只在有活时敲一次门铃，把 N 次退出压成 1 次。','传统设备模拟可能因寄存器交互频繁退出；VirtIO 通过共享队列批量交付，降低通知成本。具体退出次数受 ioeventfd 和通知抑制影响，不能固定为 N→1。')
$src=$src.Replace('完成点：应用拿到字节','完成点：驱动可回收缓冲；应用返回仍有后续步骤')
$src=$src.Replace('server / firecracker / ublk-daemon','Host 三个用户态进程')
$src=$src.Replace('硬件把 Guest 寄存器写进 VMCS guest-state，写退出原因与 qualification，再载入宿主状态','硬件保存 VMCS 规定的 Guest 状态与退出信息并加载 Host 状态；通用寄存器等由 KVM 软件协同保存')
$src=$src.Replace('只有 MMIO/PIO 这类它办不了的才回用户态','需要用户态设备处理等情况才返回；部分 MMIO 可由内核处理')
$src=$src.Replace('命中未允许 syscall → SIGSYS 直接杀进程','TRAP 产生 SIGSYS，默认处置通常终止进程')
Invoke-Expression $src
if($Compact){. "$PSScriptRoot/compact_review_layouts.ps1"}
if($pages.Count -ne 27){throw 'Wrong page count'}
$LOG=New-Object 'System.Collections.Generic.List[string]'
$n=0
foreach($p in $pages){
 $n++;$pg=NewPage (Join-Path $out ('p{0:d2}.png' -f $n))
 try{& $p $pg.g}finally{SavePage $pg}
 Write-Host "Rendered $n"
}
$dest=Join-Path $base 'AgentENV-复习课件-27页-机制详解版.pptx'
if($Compact){$dest=Join-Path $base 'AgentENV-复习课件-27页-紧凑图解版.pptx'}
Copy-Item (Join-Path $base 'AgentENV-复习课件-27页.pptx') $dest -Force
$zip=[IO.Compression.ZipFile]::Open($dest,[IO.Compression.ZipArchiveMode]::Update)
try{for($n=1;$n -le 27;$n++){
 $rd=New-Object IO.StreamReader($zip.GetEntry("ppt/slides/_rels/slide$n.xml.rels").Open());[xml]$rx=$rd.ReadToEnd();$rd.Dispose()
 $target=($rx.Relationships.Relationship|Where-Object Type -like '*/image').Target
 $media='ppt/'+$target.Replace('../','');$zip.GetEntry($media).Delete()
 [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,(Join-Path $out ('p{0:d2}.png' -f $n)),$media)|Out-Null
}}finally{$zip.Dispose()}
foreach($group in 0..2){
 $bm=New-Object Drawing.Bitmap 2160,1215;$gg=[Drawing.Graphics]::FromImage($bm);$gg.Clear([Drawing.Color]::White)
 for($k=0;$k -lt 9;$k++){$n=$group*9+$k+1;$im=[Drawing.Image]::FromFile((Join-Path $out ('p{0:d2}.png' -f $n)));$gg.DrawImage($im,($k%3)*720,[math]::Floor($k/3)*405,720,405);$im.Dispose()}
 $gg.Dispose();$bm.Save((Join-Path $out "contact-$group.png"));$bm.Dispose()
}
Write-Host "OUTPUT $dest"
