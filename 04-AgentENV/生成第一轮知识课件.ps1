param([string]$OutputRoot = 'D:\learning\Learning\microVMprac\04-AgentENV\第一轮知识课件')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$Outline = 'D:\learning\Learning\microVMprac\04-AgentENV\第一轮知识PPT-内容大纲.md'
$ImageDir = Join-Path $OutputRoot 'PNG源图'
$CheckDir = Join-Path $OutputRoot '验收图'
$DeckPath = Join-Path $OutputRoot 'AgentENV第一轮知识复习.pptx'
New-Item -ItemType Directory -Force -Path $OutputRoot,$ImageDir,$CheckDir | Out-Null
$C = @{ ink='#1D2125'; green='#047761'; green1='#E3F2EE'; green2='#ECF6F4'; orange='#DF962A'; deepOrange='#C97A12'; orange1='#FDF3E1'; red='#D9573B'; red1='#FBEDE8'; secondary='#7D848C'; gray='#5B626A'; gray1='#F6F7F8'; line='#E1E5E8'; arrow='#AAB6B2'; white='#FFFFFF' }
function Color([string]$hex) { [Drawing.ColorTranslator]::FromHtml($hex) }
function Font([single]$size,[bool]$bold=$false) { $style=if($bold){[Drawing.FontStyle]::Bold}else{[Drawing.FontStyle]::Regular}; New-Object Drawing.Font('Microsoft YaHei',$size,$style,[Drawing.GraphicsUnit]::Pixel) }
function T($g,[string]$s,[single]$x,[single]$y,[single]$w,[single]$h,[single]$size,[string]$color,[bool]$bold=$false,[string]$align='Near') {
 $font=Font $size $bold; $brush=New-Object Drawing.SolidBrush((Color $color)); $fmt=New-Object Drawing.StringFormat; $fmt.Alignment=[Drawing.StringAlignment]::$align; $fmt.LineAlignment=[Drawing.StringAlignment]::Center; $fmt.Trimming=[Drawing.StringTrimming]::None
 $rect=New-Object Drawing.RectangleF($x,$y,$w,$h); $g.DrawString($s,$font,$brush,$rect,$fmt)
 $font.Dispose();$brush.Dispose();$fmt.Dispose()
}
function Rect($g,[single]$x,[single]$y,[single]$w,[single]$h,[single]$r,[string]$fill,[string]$stroke='') {
 $path=New-Object Drawing.Drawing2D.GraphicsPath; if($r -gt 0){$d=2*$r;$path.AddArc($x,$y,$d,$d,180,90);$path.AddArc(($x+$w-$d),$y,$d,$d,270,90);$path.AddArc(($x+$w-$d),($y+$h-$d),$d,$d,0,90);$path.AddArc($x,($y+$h-$d),$d,$d,90,90);$path.CloseFigure()}else{$path.AddRectangle((New-Object Drawing.RectangleF($x,$y,$w,$h)))}
 if($fill){$b=New-Object Drawing.SolidBrush((Color $fill));$g.FillPath($b,$path);$b.Dispose()};if($stroke){$p=New-Object Drawing.Pen((Color $stroke),1);$g.DrawPath($p,$path);$p.Dispose()};$path.Dispose()
}
function L($g,[single]$x1,[single]$y1,[single]$x2,[single]$y2,[string]$color,[single]$width=1){$p=New-Object Drawing.Pen((Color $color),$width);$g.DrawLine($p,$x1,$y1,$x2,$y2);$p.Dispose()}
function Dot($g,[single]$x,[single]$y,[single]$d,[string]$color){$b=New-Object Drawing.SolidBrush((Color $color));$g.FillEllipse($b,$x,$y,$d,$d);$b.Dispose()}
function Arrow($g,[single]$x1,[single]$y1,[single]$x2,[single]$y2){$p=New-Object Drawing.Pen((Color $C.arrow),2);$p.EndCap=[Drawing.Drawing2D.LineCap]::ArrowAnchor;$g.DrawLine($p,$x1,$y1,$x2,$y2);$p.Dispose()}
function Seg($g,$segments,[single]$x,[single]$y,[single]$size){foreach($a in $segments){T $g $a.text $x $y $a.width 46 $size $a.color $a.bold;$x += $a.width}}
function Nav($g,[int]$active){$names=@('总览','概念','例题','总结');for($i=0;$i -lt 4;$i++){ $x=1090+$i*112; $num=('{0:00}' -f ($i+1)); if($i -eq ($active-1)){Rect $g $x 44 26 20 4 $C.green;T $g $num $x 44 26 20 12 $C.white $true 'Center';T $g $names[$i] ($x+32) 44 65 20 13 $C.green $true}else{T $g $num $x 44 26 20 12 $C.secondary;T $g $names[$i] ($x+32) 44 65 20 13 $C.secondary}}}
function Header($g,[int]$section,[string]$title,[string]$sub){$names=@('总览','概念','例题','总结');$name=$names[$section-1];Rect $g 56 45 88 26 13 $C.white $C.green;T $g (('{0:00} ' -f $section)+$name) 56 45 88 26 12 $C.green $true 'Center';Nav $g $section;$cut=[Math]::Min(6,[Math]::Floor($title.Length/2));$first=$title.Substring(0,$cut);$second=$title.Substring($cut);$ff=Font 33 $false;$measure=$g.MeasureString($first,$ff).Width+4;$ff.Dispose();T $g $first 56 91 $measure 46 33 $C.ink;T $g $second (56+$measure) 91 (1488-$measure) 46 33 $C.green $true;Rect $g 56 151 48 3 0 $C.green;T $g $sub 56 166 1488 28 15 $C.secondary}
function Footer($g,[int]$page,[int]$total,[string]$take){Rect $g 0 840 1600 60 0 $C.gray1;Rect $g 56 866 8 8 0 $C.green;T $g $take 76 850 1300 36 12 $C.gray;Rect $g 1444 858 100 24 10 $C.white $C.line;T $g ("$page / $total") 1444 858 100 24 12 $C.secondary $false 'Center'}
function Card($g,[single]$x,[single]$y,[single]$w,[single]$h,[string]$title,[string]$body,[string]$kind='green'){
 $bg=if($kind -eq 'red'){$C.red1}elseif($kind -eq 'orange'){$C.orange1}else{$C.green2};$accent=if($kind -eq 'red'){$C.red}elseif($kind -eq 'orange'){$C.deepOrange}else{$C.green};Rect $g $x $y $w $h 10 $bg $C.line;Rect $g $x ($y+10) 5 ($h-20) 0 $accent;T $g $title ($x+20) ($y+12) ($w-40) 28 13 $accent $true;T $g $body ($x+20) ($y+42) ($w-40) ($h-52) 14 $C.ink
}
$raw=[IO.File]::ReadAllText($Outline,[Text.Encoding]::UTF8)
$matches=[regex]::Matches($raw,'(?ms)^###\s+(\d{2})｜([^\r\n]+)\r?\n(.*?)(?=^###\s+\d{2}｜|^##\s+版式约束|\z)')
$pages=@();foreach($m in $matches){$b=$m.Groups[3].Value;function Field([string]$name){$v=[regex]::Match($b,('(?m)^- '+$name+'：([^\r\n]+)'));if(-not $v.Success){throw "missing $name at $($m.Groups[1].Value)"};$v.Groups[1].Value};$pages += [pscustomobject]@{number=[int]$m.Groups[1].Value;title=$m.Groups[2].Value;facts=(Field '知识');wrong=(Field '易错');question=(Field '自测');take=(Field '记忆');layout=(Field '版式')}}
if($pages.Count -ne 38){throw "Expected 38 pages, got $($pages.Count)"}
$exercises=@{31=@('基础：FC API socket 可连，能否断言 envd 已就绪？','进阶：FETCH、后端 READ、pread 各完成了什么？','易错：FC 后端写入 Guest RAM，需要覆盖计脏吗？');33=@('基础：增量快照缺少的页从哪里恢复？','进阶：总耗时 10 ms，其中 2 ms 完全消失，最少多少？','易错：A、B 同时对外部 counter 加 1，COW 能去重吗？')}
foreach($page in $pages){
 $bmp=New-Object Drawing.Bitmap(3200,1800);$g=[Drawing.Graphics]::FromImage($bmp);$g.ScaleTransform(2,2);$g.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias;$g.TextRenderingHint=[Drawing.Text.TextRenderingHint]::AntiAliasGridFit;$g.Clear((Color $C.white))
 $n=$page.number;$section=if($n -le 3){1}elseif($n -le 30){2}elseif($n -le 35){3}else{4}
 Header $g $section $page.title ('本页问题：'+$page.question)
 if($n -eq 1){
  T $g '目标：画清角色位置、解释数据流、判断操作完成条件' 56 220 850 54 20 $C.green $true
  Card $g 56 305 850 120 '01  先定位' '区分 Host 用户态、Host 内核与 Guest 内部的执行者。'
  Card $g 56 445 850 120 '02  再跟踪' '沿一次读文件与一次快照捕获，区分请求、字节、通知和结果。'
  Card $g 56 585 850 120 '03  最后判断' '结合失败、资源寿命和统计口径，分析系统表现与取舍。'
  Card $g 962 220 582 485 '一页看懂' "位置：server / Firecracker / KVM / Guest`n`n路径：创建、执行、读取、暂停、恢复、销毁`n`n方法：谁执行？数据在哪？何时完成？"
 }elseif($exercises.ContainsKey($n)){
  T $g '先独立思考，再翻到下一页核对思路' 56 220 1488 40 16 $C.gray $true
  $items=$exercises[$n];for($i=0;$i -lt 3;$i++){Card $g 56 (290+$i*150) 1488 120 (('0{0}  自测' -f ($i+1))) $items[$i] 'orange'}
 }else{
  $parts=@($page.facts -split '；' | Where-Object { $_.Trim() -ne '' });
  $count=$parts.Count;if($count -lt 3){throw "Page $n has fewer than 3 facts"}
  $mainX=56;$mainY=255;$mainW=980;$gap=if($count -ge 5){16}else{22};$bw=($mainW-$gap*($count-1))/$count
  T $g '机制图：按顺序或按对象阅读' 56 216 980 28 15 $C.green $true
  for($i=0;$i -lt $count;$i++){$x=$mainX+$i*($bw+$gap);$accent=if($i -eq 0){$C.green}elseif($i -eq ($count-1)){$C.deepOrange}else{$C.gray};Rect $g $x $mainY $bw 210 10 $C.white $accent;T $g ('0'+($i+1)) ($x+12) ($mainY+12) ($bw-24) 27 13 $accent $true;T $g $parts[$i].Trim() ($x+13) ($mainY+45) ($bw-26) 145 14 $C.ink $false 'Center';if($i -lt ($count-1) -and $page.layout.StartsWith('流程')){Arrow $g ($x+$bw+2) ($mainY+105) ($x+$bw+$gap-3) ($mainY+105)}}
  Card $g 1080 216 464 168 '这一页的判断题' $page.question 'orange'
  Card $g 1080 406 464 168 '常见误区' $page.wrong 'red'
  Card $g 56 506 980 110 '机制结论' $page.take 'green'
  Card $g 56 637 980 120 '继续推理' ('结合图中的角色、数据位置与完成条件，回答：'+$page.question) 'orange'
  Card $g 1080 596 464 161 '阅读边界' '图为教学模型。地址、数值和场景如无实测标记，均为假设。具体行为以源码版本和配置为准。' 'green'
 }
 Footer $g $n $pages.Count $page.take
 $path=Join-Path $ImageDir ('slide-{0:00}.png' -f $n);$bmp.Save($path,[Drawing.Imaging.ImageFormat]::Png);$g.Dispose();$bmp.Dispose();Write-Output ("RENDER {0}/{1}" -f $n,$pages.Count)
}
Copy-Item -LiteralPath (Join-Path $ImageDir 'slide-36.png') -Destination (Join-Path $OutputRoot '知识地图与三件事.png') -Force
$app=$null;$pres=$null
try {
 $app=New-Object -ComObject PowerPoint.Application
 $pres=$app.Presentations.Add();$pres.PageSetup.SlideWidth=960;$pres.PageSetup.SlideHeight=540
 foreach($page in $pages){$slide=$pres.Slides.Add($page.number,12);$img=Join-Path $ImageDir ('slide-{0:00}.png' -f $page.number);$null=$slide.Shapes.AddPicture($img,0,-1,0,0,960,540)}
 $pres.SaveAs($DeckPath);$pres.Close();$pres=$null
 $pres=$app.Presentations.Open($DeckPath,$true,$false,$false);if($pres.Slides.Count -ne $pages.Count){throw 'Slide count mismatch'}
 foreach($slide in $pres.Slides){$path=Join-Path $CheckDir ('slide-{0:00}.png' -f $slide.SlideIndex);$slide.Export($path,'PNG',1920,1080)}
 Write-Output "PPTX $DeckPath";Write-Output "SLIDES $($pres.Slides.Count)"
} finally {if($pres){$pres.Close()};if($app){$app.Quit();[Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)|Out-Null}}
