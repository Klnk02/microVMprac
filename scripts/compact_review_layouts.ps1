function TextHeight($g,$text,$fs,$width,$bold=$false){
 $f=Font2 $fs $bold
 try{$lines=@(WrapText $g $text $f $width);return $lines.Count*$fs*1.45}finally{$f.Dispose()}
}
function PanelHeight($g,$title,$body,$width,$fs=13){
 return 24+(TextHeight $g $title 14 ($width-28) $true)+8+(TextHeight $g $body $fs ($width-28))
}
function TightPanel($g,$x,$y,$width,$height,$title,$body,$accent,$fs=13){
 $need=PanelHeight $g $title $body $width $fs
 if($need -gt $height+1){throw "Panel overflow page=$script:pageNo title=$title need=$need available=$height"}
 Rect $g $x $y $width $height $C.white $C.line 1 8
 Rect $g $x $y 4 $height $accent $null 0 2
 $th=T $g $title ($x+14) ($y+12) 14 $accent $true ($width-28)
 T $g $body ($x+14) ($y+20+$th) $fs $C.body $false ($width-28)|Out-Null
}
function SplitPage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$points,$mistake,$selftest,$onlyone,$drawFig,$drawData,[int]$no)
 $script:pageNo=$no
 Header $g $section $titleParts $subtitle $nav
 T $g '结构与位置' 56 218 14 $C.green $true 500|Out-Null
 & $drawFig $g 60 252 600 246
 L $g 56 518 662 518 $C.line 1
 T $g '对照 / 示例' 56 532 14 $C.green $true 500|Out-Null
 & $drawData $g 60 565 600 178
 $width=424;$bodies=@();$heights=@()
 for($i=0;$i -lt 4;$i++){
  $body=$points[$i][1]+"`n"+$supp[$no-1][$i];$bodies+=,$body
  $heights+=,(PanelHeight $g $points[$i][0] $body $width 13)
 }
 $row1=[math]::Max($heights[0],$heights[1]);$row2=[math]::Max($heights[2],$heights[3])
 if($row1+$row2+14 -gt 550){throw "Grid too tall page $no"}
 for($i=0;$i -lt 4;$i++){
  $x=680+($i%2)*440;$y=218
  if($i -ge 2){$y+=($row1+14)}
  $ht=if($i -lt 2){$row1}else{$row2}
  TightPanel $g $x $y $width $ht $points[$i][0] $bodies[$i] $C.green
 }
 $end=218+$row1+$row2+14
 if(770-$end -gt 65){
  T $g '复述顺序：先说明图中的角色与边界，再解释四个机制。' 694 ($end+20) 13 $C.orangeDk $true 820|Out-Null
  T $g ('换条件验证：'+$selftest) 694 ($end+48) 13 $C.body $false 820|Out-Null
 }
 EndStrips $g $mistake $onlyone $selftest $no
}
function FlowPage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$steps,$notes,$mistake,$selftest,$onlyone,$drawData,[int]$no)
 $script:pageNo=$no
 Header $g $section $titleParts $subtitle $nav
 $y=218;$left=696
 for($i=0;$i -lt $steps.Count;$i++){
  $title=('{0:00}  {1}' -f ($i+1),$steps[$i][0])
  $th=TextHeight $g $title 14 ($left-28) $true
  $bh=TextHeight $g $steps[$i][1] 13 ($left-28)
  $oh=TextHeight $g $steps[$i][2] 12 ($left-28)
  $ht=24+$th+6+$bh+9+$oh
  Rect $g 56 $y $left $ht $C.white $C.line 1 8
  T $g $title 70 ($y+11) 14 $C.green $true ($left-28)|Out-Null
  T $g $steps[$i][1] 70 ($y+17+$th) 13 $C.body $false ($left-28)|Out-Null
  T $g $steps[$i][2] 70 ($y+26+$th+$bh) 12 $C.green $false ($left-28)|Out-Null
  $y+=$ht
  if($i -lt $steps.Count-1){Arrow $g 400 ($y+2) 400 ($y+13) $C.arrow 1.3;$y+=16}
 }
 if($y -gt 770){throw "Flow overflow page $no bottom=$y"}
 $ny=218;$nw=770
 for($i=0;$i -lt $notes.Count;$i++){
  $body=$notes[$i][1]+"`n"+$supp[$no-1][[math]::Min(3,$i+1)]
  $ht=PanelHeight $g $notes[$i][0] $body $nw 13
  $accent=@($C.green,$C.orangeDk,$C.red)[$i%3]
  TightPanel $g 774 $ny $nw $ht $notes[$i][0] $body $accent
  $ny+=$ht+12
 }
 $available=768-$ny
 if($available -lt 104){throw "Flow data area too short page $no height=$available"}
 T $g '字段 / 完成条件对照' 784 ($ny+2) 12 $C.dim $true 710|Out-Null
 & $drawData $g 784 ($ny+28) 748 ($available-30)
 EndStrips $g $mistake $onlyone $selftest $no
}
function TablePage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$header,$rows,$colw,$notes,$mistake,$selftest,$onlyone,[int]$no)
 $script:pageNo=$no
 Header $g $section $titleParts $subtitle $nav
 $sum=0;foreach($val in $colw){$sum+=$val}
 $widths=@();foreach($val in $colw){$widths+=,[double]($val/$sum*970)}
 $x=56;$y=218
 for($j=0;$j -lt $header.Count;$j++){
  Rect $g $x $y $widths[$j] 44 $C.grayBg $C.line 1 0
  T $g $header[$j] ($x+10) ($y+10) 13 $C.ink $true ($widths[$j]-20)|Out-Null;$x+=$widths[$j]
 }
 $y+=44
 for($i=0;$i -lt $rows.Count;$i++){
  $rh=0
  for($j=0;$j -lt $header.Count;$j++){$rh=[math]::Max($rh,(TextHeight $g $rows[$i][$j] 13 ($widths[$j]-20) ($j -eq 0))+20)}
  $x=56
  for($j=0;$j -lt $header.Count;$j++){
   $bg=if($i%2 -eq 0){$C.white}else{$C.greenBg2}
   Rect $g $x $y $widths[$j] $rh $bg $C.line 1 0
   T $g $rows[$i][$j] ($x+10) ($y+10) 13 $C.body ($j -eq 0) ($widths[$j]-20)|Out-Null;$x+=$widths[$j]
  }
  $y+=$rh
 }
 $ny=218
 for($i=0;$i -lt $notes.Count;$i++){
  $ht=PanelHeight $g $notes[$i][0] $notes[$i][1] 496 13
  TightPanel $g 1048 $ny 496 $ht $notes[$i][0] $notes[$i][1] $C.green
  $ny+=$ht+12
 }
 if($ny -gt 780){throw "Table notes overflow $no"}
 $gy=$y+18
 for($r=0;$r -lt 2;$r++){
  $maxh=0
  for($j=0;$j -lt 2;$j++){
   $k=$r*2+$j;$body=$supp[$no-1][$k]
   $ht=PanelHeight $g ('判断提示 '+($k+1)) $body 476 13;$maxh=[math]::Max($maxh,$ht)
  }
  for($j=0;$j -lt 2;$j++){
   $k=$r*2+$j
   TightPanel $g (56+$j*494) $gy 476 $maxh ('判断提示 '+($k+1)) $supp[$no-1][$k] $C.orangeDk
  }
  $gy+=$maxh+12
 }
 if($gy -gt 782){throw "Table supplement overflow $no bottom=$gy"}
 EndStrips $g $mistake $onlyone $selftest $no
}
function ExamplePage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$question,$known,$steps,$answer,$mistake,$selftest,$onlyone,[int]$no)
 $script:pageNo=$no
 Header $g $section $titleParts $subtitle $nav
 $body=$question+"`n`n已知："+$known
 $h=PanelHeight $g '题目与条件' $body 438 14
 TightPanel $g 56 218 438 $h '题目与条件' $body $C.orangeDk 14
 $bodies=@();$hh=0
 for($i=0;$i -lt 3;$i++){
  $body=$steps[$i][1]+"`n`n"+$supp[$no-1][$i+1];$bodies+=,$body
  $hh=[math]::Max($hh,(PanelHeight $g $steps[$i][0] $body 330 14))
 }
 for($i=0;$i -lt 3;$i++){
  TightPanel $g (514+$i*348) 218 330 $hh $steps[$i][0] $bodies[$i] $C.green 14
  if($i -lt 2){Arrow $g (846+$i*348) 305 (859+$i*348) 305 $C.arrow 1}
 }
 $y=218+[math]::Max($h,$hh)+20
 $body='先给结论，再说明判断针对的主体。'+"`n`n"+$answer
 $ah=PanelHeight $g '结论与理由' $body 730 14
 $reason='① 定位：这条 syscall、事件或 CQE 由谁处理？'+"`n`n"+'② 列缺口：从当前完成点到应用拿到结果，还差哪些步骤？'+"`n`n"+'③ 给证据：用返回值、错误码或实际状态支持判断。'
 $rh=PanelHeight $g '把推理写完整' $reason 738 14
 $ht=[math]::Max($ah,$rh)
 TightPanel $g 56 $y 730 $ht '结论与理由' $body $C.green 14
 TightPanel $g 806 $y 738 $ht '把推理写完整' $reason $C.orangeDk 14
 if($y+$ht -gt 770){throw "Example overflow $no"}
 EndStrips $g $mistake $onlyone $selftest $no
}
function MistakesPage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$rows,$mistake,$selftest,$onlyone,[int]$no)
 $script:pageNo=$no
 Header $g $section $titleParts $subtitle $nav
 $y=218
 for($r=0;$r -lt 2;$r++){
  $maxh=0
  for($j=0;$j -lt 3;$j++){
   $k=$r*3+$j
   $body='正确：'+$rows[$k][1]
   $maxh=[math]::Max($maxh,(PanelHeight $g ('误区：'+$rows[$k][0]) $body 484 14))
  }
  for($j=0;$j -lt 3;$j++){
   $k=$r*3+$j
   TightPanel $g (56+$j*502) $y 484 $maxh ('误区：'+$rows[$k][0]) ('正确：'+$rows[$k][1]) $C.red 14
  }
  $y+=$maxh+16
 }
 T $g '检查方法：先找错答里的绝对判断，再补上它遗漏的主体、条件或完成点。' 70 ($y+10) 15 $C.green $true 1420|Out-Null
 EndStrips $g $mistake $onlyone $selftest $no
}
function SummaryPage {
 param($g,$section,$titleParts,$subtitle,[int]$nav,$must,$three,$next,$mistake,$selftest,$onlyone,[int]$no)
 $script:pageNo=$no
 Header $g $section $titleParts $subtitle $nav
 $y=218
 for($r=0;$r -lt 2;$r++){
  $maxh=0
  for($j=0;$j -lt 3;$j++){
   $k=$r*3+$j;$title=if($k -lt 5){'必须会 '+($k+1)}else{'下一步'}
   $body=if($k -lt 5){$must[$k]}else{$next}
   $maxh=[math]::Max($maxh,(PanelHeight $g $title $body 484 15))
  }
  for($j=0;$j -lt 3;$j++){
   $k=$r*3+$j;$title=if($k -lt 5){'必须会 '+($k+1)}else{'下一步'}
   $body=if($k -lt 5){$must[$k]}else{$next}
   TightPanel $g (56+$j*502) $y 484 $maxh $title $body $C.green 15
  }
  $y+=$maxh+16
 }
 T $g '如果只记三件事' 56 ($y+4) 18 $C.green $true 1000|Out-Null
 $y+=40;$maxh=0
 for($i=0;$i -lt 3;$i++){$maxh=[math]::Max($maxh,(PanelHeight $g ('0'+($i+1)) $three[$i] 484 15))}
 for($i=0;$i -lt 3;$i++){TightPanel $g (56+$i*502) $y 484 $maxh ('0'+($i+1)) $three[$i] $C.orangeDk 15}
 if($y+$maxh -gt 770){throw 'Summary overflow'}
 EndStrips $g $mistake $onlyone $selftest $no
}
function fig_layers3 {param($g,$x,$y,$w,$h)
 $names=@(@('server','实例编排 / 生命周期'),@('Firecracker','VMM / vCPU / 设备'),@('ublk-daemon','取任务 / 查层 / 提交'),@('KVM','执行与地址映射'),@('ublk 驱动','Host 块请求队列'),@('cgroup / seccomp','限制资源 / syscall'),@('Guest 内核','页表 / 文件系统 / 调度'),@('envd','命令与文件服务'),@('Guest 应用','执行代码 / 读写数据'))
 $bands=@('Host 用户态：各自是进程','Host 内核：机制，不是独立服务进程','Guest：自己的内核与进程表')
 for($r=0;$r -lt 3;$r++){
  T $g $bands[$r] $x ($y+$r*83) 12 $C.dim $true $w|Out-Null
  for($j=0;$j -lt 3;$j++){
   $xx=$x+$j*($w/3);$yy=$y+$r*83+23;$k=$r*3+$j
   Rect $g $xx $yy ($w/3-10) 52 $C.grayBg $C.line 1 6
   T $g $names[$k][0] ($xx+9) ($yy+6) 13 $C.green $true ($w/3-28)|Out-Null
   T $g $names[$k][1] ($xx+9) ($yy+29) 11.5 $C.body $false ($w/3-28)|Out-Null
  }
 }
}
