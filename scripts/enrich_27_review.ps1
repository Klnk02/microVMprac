#requires -Version 5.1
# Preserve the original PPTX package and add explanations inside existing card whitespace.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
. "$PSScriptRoot/deck_core.ps1"
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$base=Join-Path (Split-Path $PSScriptRoot -Parent) '04-AgentENV'
$dest=Join-Path $base 'AgentENV-复习课件-27页-内容补充版.pptx'
$out=Join-Path $base '图片-27页-内容补充版'
New-Item -ItemType Directory -Force -Path $out | Out-Null
# Four additions per page, corresponding to the four existing mechanism cards.
$supp=@(
@('定位例：server 发暂停请求；Firecracker 停 vCPU；envd 在 Guest 内执行命令。三者各自有职责。','创建要等就绪，执行要取退出结果，读文件要等字节交付；销毁还要等引用与在途操作结束。','追问模板：谁提交 → 谁执行 → 谁确认？例如设备写 used 后，Guest 驱动仍需消费结果。','纸面例子必须标“假设”；性能比较至少记录负载大小、并发数、缓存状态和计时范围。'),
@('复习顺序：先画进程边界，再标地址属于谁，最后把 syscall、通知和数据复制分别连线。','补充：实际接口还包含 flags（须为 0）；local/remote 是 iovec 数组，返回值才是已复制字节数。','遇到“恢复很慢”先区分：建立映射慢、首触缺页慢、后端取块慢，三者对应不同观测。','每个答案都补一个反例：health 成功但 token 无效；pause 成功但磁盘满导致快照写失败。'),
@('管理对象 FirecrackerInstance 位于 server 内；它保存 Child 句柄与 API socket 路径，本身没有独立 PID。','“无 PID”指这些机制不是独立服务进程；内核仍可能有相关工作线程，不能据此说它们不可观测。','Host 调度 vCPU 线程；Guest 内核再调度 envd/应用。Host 的线程数不会随每次 Guest fork 增加。','API socket 操作机器状态；envd 处理命令与文件请求。API 可连不证明 Guest 网络或 envd 已就绪。'),
@('普通 load/store 由 CPU 完成翻译；命中组合 TLB 时可直接使用 GVA→HPA 的缓存结果。','接口登记 GPA 区间及其 HVA 后备；HPA 由宿主内存管理与 KVM 取得，无须 VMM 逐页填入。','此处地址是假设值。即使数值相同，server 的 HVA 与 Firecracker 的 HVA 也不代表同一个对象。','每段必须检查起点、长度与边界。memslot 登记成功不保证所有物理页已驻留，也不等于完成复制。'),
@('准确说法是 ioctl(vcpu_fd, KVM_RUN)：KVM_RUN 是 ioctl 命令号；返回原因决定后续处理。','VMCS 只自动保存特定体系结构状态；通用寄存器等还需 KVM 软件保存，不能理解为保存整份 VM 快照。','普通 RAM 缺项可在 KVM 内解决；设备 MMIO 若需要用户态模拟，才可能把退出原因交给 VMM。','线程睡眠通常不累计自身 CPU 时间；忙轮询会累计。wall 时间还包括等待、排队与被抢占。'),
@('按本页基础模型，N 个 vCPU 加 VMM/API 线程为 N+2；其他版本、配置或辅助功能可能增加线程。','N=2 时有 3 个参与者：vCPU0、vCPU1、主线程。Barrier 是启动同步，不是快照持久化屏障。','排障可同时看 PID/TID、线程名、运行状态及栈；只看一个进程的总 CPU 无法定位哪个线程在忙。','阻塞是否发生取决于退出与等待路径；Guest 正在计算时，vCPU 线程虽停留在 ioctl 中仍消耗 CPU。'),
@('Unix socket 是本机传输端点；REST/HTTP 表示请求格式。二者分别回答“从哪传”和“怎么表达”。','分清三条路：VMM 控制、Guest 应用通信、设备数据路径；envd 的 TCP/gRPC 属于应用通信。','暂停由宿主控制路径推进；已经停下的 Guest 也不需要再执行一条 envd 命令来确认自己暂停。','重试前查询实例实际状态与操作结果；创建、执行命令这类有副作用的操作需防止重复执行。'),
@('例如一次块读可组成头部→数据 buffer→状态字节的描述符链；WRITE 标志表示设备可写该段。','发布描述符与 avail 内容后再更新 idx，并遵守内存顺序；通知只催促设备检查，不承载数据。','设备完成后写 used{id,len}；Guest 消费 used 才可回收链及 buffer。avail 被取走不等于任务结束。','split ring 的槽位通常按 idx % 队列长度定位；idx 是累计索引，不能简单当作当前请求数量。'),
@('排障先看子进程存活及 socket 是否响应，再查启动配置；创建客户端对象只准备通信能力。','检查接口、路由、NAT 和端口；TCP 握手成功只表示传输层可建立连接，不保证应用请求成功。','探测成功说明当时能处理该健康请求；并不保证下一次 exec 的权限、路径和资源都满足。','可用同一 base 地址发健康与业务请求；两种请求的认证要求不同，失败应分别报告。'),
@('例如 cmd=/bin/echo，args=[hello]；不要默认字符串中的管道、重定向符会被 shell 解释。','Start 后收到 Data="hello"，最后 End{0}，才获得本次执行的完整结果；没有输出也可成功。','End{2} 可以是完整、正常交付的执行结果，但业务命令失败；流中断则连最终退出结果都不完整。','超时表示调用方不再继续等待；远端进程可能仍活着。重试写文件或扣款命令前尤其要核对状态。'),
@('ublk 在 Host 内核侧；Guest 内核先走自己的文件系统与 virtio-blk，Firecracker 再访问 Host 后端。','字节经后端读取缓冲、块请求缓冲和 Guest 页面到应用缓冲；具体复制次数取决于实现与缓存路径。','假设扇区为 512 B：4 KiB 请求是 8 个扇区。文件 offset 必须经文件系统映射，不能直接充当 LBA。','Guest 页缓存命中可跳过该数据块的 virtio；Host 缓存命中只省后端磁盘读取，不省 Guest 设备交互。'),
@('索引查找回答“这个逻辑范围由哪层提供”；真正读文件还需要把逻辑偏移换成本层数据偏移。','例如逻辑块 2 在新层显式置零，旧层即使有 C 也不可返回 C；新层记录是覆盖规则的一部分。','增量层只记录修改范围；删除仍被引用的父层，会使没有被覆盖的范围失去数据来源。','一个请求跨两个映射区间时应拆分处理，不能把首个命中层的物理偏移套给整个请求。'),
@('ublkbN 是块设备，不是每个请求对应一个文件；queue_id 与 tag 标识当前队列内的在途请求槽。','“节点存在”与“服务可用”分开：注册成功后还要检查能打开、队列已准备、daemon 能接请求。','FETCH 的 CQE 交付任务；若后端另用 io_uring READ，其 CQE 才报告读字节结果；再 COMMIT 交还。','请求未结束不能提前复用 tag/buffer；daemon 退出时需要让等待者获得错误，并协调设备清理。'),
@('VMA 描述范围和权限；RSS 反映实际驻留。映射 128 MiB 后 RSS 可远小于 128 MiB，首触时才增长。','minor/major 是宿主缺页统计口径，不等于 EPT 退出次数；major 也不直接等价于一次设备请求。','例：A/B 私有映射初读同一页；A 写后读到 11，B 仍读到旧值 10，父层内容不被这次写修改。','MAP_PRIVATE 是写入可见性语义；按需加载是何时取页。两者可以一起出现，但不是同一个机制。'),
@('内存文件只保留字节，无法单独恢复 CPU 指令位置与设备状态；rootfs 也不是完整运行时快照。','脏范围描述“读哪些页”；ProcessVmReader 按 Firecracker HVA 取字节，随后才进入层格式写入。','格式 finalize、原子 rename、持久化与索引发布是不同步骤；父层引用也必须与快照对应。','暂停 vCPU 后仍需处理在途设备 IO；应用事务或外部服务的一致性，还需要更高层协议保证。'),
@('某线程当前未运行，只是调度现象；调度器下一刻可能再次让它执行，不能当暂停确认。','成功响应的含义要与实现约定对应；仅请求入队、收到 HTTP 响应片段，都不足以证明全部确认。','一致性要求“读出快照期间没有未协调写入”；不能先读半段，再停剩余 vCPU 后读另一半。','若暂停成功而内存层写入失败，应报告“已暂停、快照失败”，保留现场与可重试所需资源。'),
@('这里“只读”指后备块设备；Firecracker 可建立私有可写映射，Guest 后续写入由 COW 隔离。','启动顺序影响正确性：先接好资源再运行 vCPU；resume 返回也不证明 envd 已能处理命令。','恢复 RAM 的缺页由 Host 后备映射取页；不会为了补 RAM 而让 Guest 发一条 virtio-blk 请求。','网络重连与身份重置需按实现处理；不能仅靠还原 RAM 就保证外部连接、租约与随机状态安全。'),
@('SNAT 改源地址便于回包；conntrack 记录连接的转换关系，返回流量按已有状态反向转换。','目的地址转换完成后仍需路由与 virtio-net 交付；Guest 网络栈最后依据端口找到 envd socket。','两个实例都叫 tap0 不冲突，但实例自己的路由与 NAT 规则仍要正确，单靠名字隔离不能通信。','envd 未监听时，包到 Guest 也无法完成应用通信；域名解析、TCP、TLS、RPC 可分别失败。'),
@('namespace 组织可见范围，cgroup 限资源，uid/capability 约束权限，seccomp 限宿主 syscall。','过滤器按线程生效；新线程的继承或同步安装策略要查实现。把规则给 API 线程不自动约束所有对象。','TRAP 产生 SIGSYS，默认处置通常终止进程；条数与允许参数依版本变化，不作为跨版本固定常量。','no_new_privs 阻止 exec 获得新权限；它并不自动清除已有 capability，也不能代替降权。'),
@('先判定 guest_phys_addr ≤ GPA < guest_phys_addr+size，再做减法与加法，检查溢出和区间边界。','假设 PID=1234：remote 指向该进程的 0x70002000，local 指向 server 自己的 buffer，二者不可互换。','第二段起点 0x4000000：0x80000000+(0x4010000−0x4000000)=0x80010000。','process_vm_readv 返回实际字节数，可能短读；检查权限和错误后按已完成范围推进，不能直接当满长成功。'),
@('先明确“读到”是 daemon 的 buffer，还是 Guest 应用 buffer；同样叫 read，完成点可能隔了几层。','CQE 是完成条目，含义由对应的 SQE 决定；user_data 可用于把完成结果关联回提交的操作。','若 READ 的 res=4096，只说明该次读取交付了 4096 字节；res<0 是负错误码，短读也要处理。','最后还需设备完成及 Guest 驱动消费；本页 pread 的主体是 daemon，不能套用 Guest 应用返回语义。'),
@('先画两条 syscall 路：Guest 应用→Guest 内核；Firecracker 线程→Host 内核。过滤对象不同。','Guest root 仍受虚拟机硬件隔离与设备接口约束；“不经 Host seccomp”不等于能任意访问 Host。','若设备请求诱发 VMM 调用 Host syscall，该调用会受 VMM 线程的过滤器约束，属于间接影响。','宿主 pids.max 仍能限制 VMM/daemon 新建宿主任务；内存超限是否杀整组由 cgroup 配置决定。'),
@('反例：Guest 创建 100 个进程，不要求 Host 创建 100 个线程；限制应放在能看到这些对象的一层。','补充边界：ioeventfd 可让部分设备通知留在内核处理；MMIO 也不能一概推断必返用户态。','用户命名空间能改变 UID 映射；“隔离视图”与“权限能力”应结合具体 namespace 类型分别判断。','文件数据与目录项的持久化都应纳入协议；rename 只给出命名切换的原子性，不自动保证断电恢复。'),
@('记字段用途比死记大小重要：addr 指范围、len 限长度、flags 表访问方向/链、next 指下一项。','1 秒是这份材料所述版本的单次探测口径；总等待时间还包括重试、间隔和总体期限。','假设 60 MiB/4 KiB=15360 页；这是页数，不等于任务数、chunk 数或实际 IO 次数。','性能公式：加速比=旧 wall/新 wall；CPU 节省率=(旧 CPU−新 CPU)/旧 CPU，必须统一统计范围。'),
@('作答提示：先写线程角色，再说明启动同步参与者。线程数按本课模型回答，并注明可有额外线程。','作答提示：分别讨论“这 4 KiB 数据本身”和“整个系统调用附带的元数据等 IO”，避免绝对化。','作答提示：至少分别提出暂停确认、快照输出或持久化的观测；不要只凭一条总失败日志归因。','可用反例检验答案：增加一个 vCPU、改成 Host 缓存命中、把磁盘写满，原结论会如何改变？'),
@('必须会的第五条是隔离与度量：能区分 namespace/cgroup/seccomp，并区分 wall、CPU 与 perf 样本。','地址例：memslot 换算得到远程 HVA；PVM 的 PID 决定读哪个进程，local buffer 属于调用者。','若 perf 中 memcpy 占 10%，先确认是 CPU 采样占比；不能直接说它贡献了 10% 的 wall 时间。','只记三件事：画清执行主体；对齐完成点；把可见性、生命周期和计时口径写进结论。'),
@('补充术语：TLB 缓存地址翻译；EPT 做二阶段翻译；chunk 描述数据范围，buffer 才承载实际字节。','再加两对：async 接口≠内部不阻塞；减少 CPU≠减少延迟。阻塞可释放 CPU，但仍占住当前工作线程。','参考思路：① 基础模型 2+2=4，主线程也等 Barrier；② 数据命中可免读块；③ pause 与保存逐段查证。','本材料是机制复习；源码行号、白名单数与配置项随版本变化，排障时用实际部署版本复核。')
)
if($supp.Count -ne 27){throw 'Expected 27 pages'}
Copy-Item -LiteralPath (Join-Path $base 'AgentENV-复习课件-27页.pptx') -Destination $dest -Force
$zip=[IO.Compression.ZipFile]::Open($dest,[IO.Compression.ZipArchiveMode]::Update)
try {
 for($n=1;$n -le 27;$n++){
  $rel=$zip.GetEntry("ppt/slides/_rels/slide$n.xml.rels")
  $rd=New-Object IO.StreamReader($rel.Open()); [xml]$rx=$rd.ReadToEnd(); $rd.Dispose()
  $target=($rx.Relationships.Relationship | Where-Object Type -like '*/image').Target
  $media='ppt/'+$target.Replace('../','')
  $entry=$zip.GetEntry($media); $ms=New-Object IO.MemoryStream
  $stream=$entry.Open(); $stream.CopyTo($ms); $stream.Dispose(); $ms.Position=0
  $img=[Drawing.Image]::FromStream($ms)
  $path=Join-Path $out ('p{0:d2}.png' -f $n)
  $pg=NewPage $path
  $pg.g.DrawImage($img,0,0,1600,900)
  for($j=0;$j -lt 4;$j++){
   $y=210+$j*141+78
   # Original body occupies y+40..74; the new paragraph uses the remaining card area.
   L $pg.g 820 ($y-3) 1528 ($y-3) $C.line 0.7
   $height=T $pg.g $supp[$n-1][$j] 820 $y 12 $C.body $false 705
   if($height -gt 45){throw "Supplement overflow page $n card $j height=$height"}
  }
  # Small concrete traces in existing left-panel whitespace; no original diagram is removed.
  $trace=$null
  switch($n){
   8 {$trace=@('链头 3 → avail','设备处理数据','used.id = 3','驱动回收 buffer')}
   10 {$trace=@('Start{42}','Data: hello','End{0}','核对退出结果')}
   13 {$trace=@('FETCH：领任务','OverlayBD 定层','READ：取字节','COMMIT：交结果')}
   17 {$trace=@('Host 后备缺页','Host 块请求','daemon 取页','映射后继续执行')}
   20 {$trace=@('GPA: 0x2000','段内偏移 0x2000','HVA: 0x70002000','PVM 远程源地址')}
  }
  if($null -ne $trace){
   for($k=0;$k -lt 4;$k++){
    $tx=72+$k*171
    Rect $pg.g $tx 439 155 43 $C.greenBg2 $C.line 1 8
    T $pg.g $trace[$k] ($tx+7) 452 11.5 $C.green $true 141 | Out-Null
    if($k -lt 3){Arrow $pg.g ($tx+157) 460 ($tx+168) 460 $C.arrow 1}
   }
  }
  SavePage $pg
  $img.Dispose();$ms.Dispose()
  $entry.Delete(); [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$path,$media,[IO.Compression.CompressionLevel]::Optimal)|Out-Null
  Write-Host "Enriched page $n"
 }
} finally {$zip.Dispose()}
# Contact sheets for complete source/output comparison.
foreach($group in 0..2){
 $bm=New-Object Drawing.Bitmap 2160,1215
 $g=[Drawing.Graphics]::FromImage($bm);$g.Clear([Drawing.Color]::White)
 for($k=0;$k -lt 9;$k++){
  $n=$group*9+$k+1
  $im=[Drawing.Image]::FromFile((Join-Path $out ('p{0:d2}.png' -f $n)))
  $g.DrawImage($im,($k%3)*720,[math]::Floor($k/3)*405,720,405);$im.Dispose()
 }
 $g.Dispose();$bm.Save((Join-Path $out ("contact-$group.png")));$bm.Dispose()
}
Write-Host "OUTPUT $dest"
