#requires -Version 5.1
<#
  AgentENV 复习课件 —— 整页 PNG 生成器
  视觉系统：白底扁平 / 固定色板 / 逻辑 1600x900 / 位图 3200x1800
  用法：powershell -ExecutionPolicy Bypass -File .\build_deck.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing

# ---------------- 画布与色板 ----------------
$W = 1600; $H = 900; $SCALE = 2
$M = 56                      # 左右页边距
$CONTENT_TOP = 210           # 内容区起点
$FOOTER_Y = 840              # 页脚起点

$C = @{
  ink      = '#1D2125'
  green    = '#047761'
  greenBg1 = '#E3F2EE'
  greenBg2 = '#ECF6F4'
  orange   = '#DF962A'
  orangeDk = '#C97A12'
  orangeBg = '#FDF3E1'
  red      = '#D9573B'
  redBg    = '#FBEDE8'
  dim      = '#7D848C'
  body     = '#5B626A'
  grayBg   = '#F6F7F8'
  line     = '#E1E5E8'
  track    = '#F0F2F1'
  white    = '#FFFFFF'
  arrow    = '#AAB6B2'
  black    = '#000000'
}

function Brush([string]$hex) { New-Object System.Drawing.SolidBrush ([System.Drawing.ColorTranslator]::FromHtml($hex)) }
function Pen2([string]$hex, [double]$w = 1) { New-Object System.Drawing.Pen ([System.Drawing.ColorTranslator]::FromHtml($hex)), $w }
function Font2([double]$px, [bool]$bold = $false) {
  $style = if ($bold) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }
  New-Object System.Drawing.Font('Microsoft YaHei', [single]$px, $style, [System.Drawing.GraphicsUnit]::Pixel)
}

function RoundPath([double]$x, [double]$y, [double]$w, [double]$h, [double]$r) {
  $p = New-Object System.Drawing.Drawing2D.GraphicsPath
  if ($w -le 0) { $w = 0.5 }
  if ($h -le 0) { $h = 0.5 }
  if ($r -le 0.2) {
    $p.AddRectangle((New-Object System.Drawing.RectangleF([single]$x, [single]$y, [single]$w, [single]$h)))
    return $p
  }
  $d = $r * 2
  if ($d -gt $w) { $d = $w }; if ($d -gt $h) { $d = $h }
  $p.AddArc($x, $y, $d, $d, 180, 90)
  $p.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
  $p.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
  $p.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
  $p.CloseFigure()
  return $p
}

# ---------------- 基础绘制 ----------------
function Rect {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h,
        [string]$fill = '#FFFFFF', [string]$line = $null, [double]$lw = 1, [double]$r = 10)
  $path = RoundPath $x $y $w $h $r
  if ($fill) { $g.FillPath((Brush $fill), $path) }
  if ($line) { $g.DrawPath((Pen2 $line $lw), $path) }
  $path.Dispose()
}

function L {
  param($g, [double]$x1, [double]$y1, [double]$x2, [double]$y2, [string]$color = '#E1E5E8', [double]$width = 1)
  $g.DrawLine((Pen2 $color $width), [single]$x1, [single]$y1, [single]$x2, [single]$y2)
}

function Dot {
  param($g, [double]$x, [double]$y, [double]$s = 8, [string]$color = '#047761')
  $g.FillRectangle((Brush $color), [single]$x, [single]$y, [single]$s, [single]$s)
}

function WrapText {
  param($g, [string]$text, $font, [double]$maxW)
  $lines = New-Object System.Collections.Generic.List[string]
  foreach ($para in ($text -split "`n")) {
    if ($para -eq '') { $lines.Add(''); continue }
    $cur = ''
    foreach ($ch in $para.ToCharArray()) {
      $try = $cur + $ch
      $w = $g.MeasureString($try, $font).Width
      if ($w -gt $maxW -and $cur -ne '') { $lines.Add($cur); $cur = [string]$ch }
      else { $cur = $try }
    }
    if ($cur -ne '') { $lines.Add($cur) }
  }
  return ,$lines
}

# T：绘制文字，自动换行 + 自动缩字号（不低于 11.5），返回占用高度
function T {
  param($g, [string]$text, [double]$x, [double]$y, [double]$size, [string]$color = '#1D2125',
        [bool]$bold = $false, [double]$maxW = 0, [string]$align = 'left', [double]$lh = 1.45,
        [switch]$NoFit)
  $s = $size
  if ($maxW -le 0) { $maxW = $W - $x - $M }
  while ($s -ge 11.5) {
    $font = Font2 $s $bold
    $lines = @(WrapText $g $text $font $maxW)
    $hh = ($lines.Count * $s * $lh)
    if ($NoFit -or $hh -le 100000) { break }
    $font.Dispose(); $s -= 0.5
  }
  $font = Font2 $s $bold
  $lines = @(WrapText $g $text $font $maxW)
  $brush = Brush $color
  $fmt = New-Object System.Drawing.StringFormat
  $fmt.LineAlignment = 'Near'
  if ($align -eq 'center') { $fmt.Alignment = 'Center' }
  elseif ($align -eq 'right') { $fmt.Alignment = 'Far' }
  else { $fmt.Alignment = 'Near' }
  $yy = $y
  foreach ($ln in $lines) {
    $w = $g.MeasureString($ln, $font).Width
    $xx = $x
    if ($align -eq 'center') { $xx = $x + ($maxW - $w) / 2 }
    elseif ($align -eq 'right') { $xx = $x + ($maxW - $w) }
    $g.DrawString($ln, $font, $brush, [single]$xx, [single]$yy, $fmt)
    $yy += $s * $lh
  }
  $font.Dispose(); $brush.Dispose(); $fmt.Dispose()
  return ($yy - $y)
}

# Seg：一行多色文字（用于标题的前半句 + 加粗结论）
function Seg {
  param($g, $parts, [double]$x, [double]$y, [double]$size = 33, [double]$maxW = 0)
  if ($maxW -le 0) { $maxW = $W - $x - $M }
  $total = 0
  foreach ($p in $parts) { $f = Font2 $size $p.bold; $total += $g.MeasureString($p.t, $f).Width; $f.Dispose() }
  $s = $size
  while ($total -gt $maxW -and $s -gt 18) {
    $s -= 1; $total = 0
    foreach ($p in $parts) { $f = Font2 $s $p.bold; $total += $g.MeasureString($p.t, $f).Width; $f.Dispose() }
  }
  $xx = $x
  foreach ($p in $parts) {
    $f = Font2 $s $p.bold
    $b = Brush $p.c
    $g.DrawString($p.t, $f, $b, [single]$xx, [single]$y)
    $xx += $g.MeasureString($p.t, $f).Width
    $f.Dispose(); $b.Dispose()
  }
  return $s
}

function Arrow {
  param($g, [double]$x1, [double]$y1, [double]$x2, [double]$y2, [string]$color = '#AAB6B2', [double]$width = 1.4)
  $g.DrawLine((Pen2 $color $width), [single]$x1, [single]$y1, [single]$x2, [single]$y2)
  $ang = [Math]::Atan2($y2 - $y1, $x2 - $x1)
  $len = 7; $spread = 0.42
  $p1 = New-Object System.Drawing.PointF ([single]($x2 - $len * [Math]::Cos($ang - $spread))), ([single]($y2 - $len * [Math]::Sin($ang - $spread)))
  $p2 = New-Object System.Drawing.PointF ([single]($x2 - $len * [Math]::Cos($ang + $spread))), ([single]($y2 - $len * [Math]::Sin($ang + $spread)))
  $p3 = New-Object System.Drawing.PointF ([single]$x2), ([single]$y2)
  $g.FillPolygon((Brush $color), @($p1, $p2, $p3))
}

# ---------------- 版式组件 ----------------
$script:NAV = @('01 总览', '02 概念', '03 例题', '04 总结')

function Nav {
  param($g, [int]$current)   # 1..4
  $x = $W - $M
  for ($i = $script:NAV.Count - 1; $i -ge 0; $i--) {
    $label = $script:NAV[$i]
    $num = $label.Substring(0, 2); $name = $label.Substring(3)
    $fName = Font2 12 ($i + 1 -eq $current)
    $wn = $g.MeasureString($name, $fName).Width
    $fName.Dispose()
    $x -= $wn
    $col = if ($i + 1 -eq $current) { $C.green } else { $C.dim }
    $bold = ($i + 1 -eq $current)
    $b = Brush $col; $f = Font2 12 $bold
    $g.DrawString($name, $f, $b, [single]$x, [single]40)
    $f.Dispose(); $b.Dispose()
    $x -= 32
    if ($i + 1 -eq $current) {
      Rect $g $x 38 26 20 $C.green $null 0 6
      $f2 = Font2 11 $true; $b2 = Brush $C.white
      $nw = $g.MeasureString($num, $f2).Width
      $g.DrawString($num, $f2, $b2, [single]($x + (26 - $nw) / 2), [single]41)
      $f2.Dispose(); $b2.Dispose()
    } else {
      $f2 = Font2 11 $false; $b2 = Brush $C.dim
      $g.DrawString($num, $f2, $b2, [single]($x + 4), [single]41)
      $f2.Dispose(); $b2.Dispose()
    }
    $x -= 26
  }
}

function Header {
  param($g, [string]$section, $titleParts, [string]$subtitle = $null, [int]$navIndex = 2)
  Nav $g $navIndex
  # 章节胶囊
  Rect $g $M 96 88 26 '#FFFFFF' $C.green 1 13
  $f = Font2 12 $true; $b = Brush $C.green
  $tw = $g.MeasureString($section, $f).Width
  $g.DrawString($section, $f, $b, [single]($M + (88 - $tw) / 2), [single]101)
  $f.Dispose(); $b.Dispose()
  # 标题
  $used = Seg $g $titleParts $M 136 33 ($W - 2 * $M)
  # 绿线
  Rect $g $M 182 48 3 $C.green $null 0 1.5
  # 副标题
  if ($subtitle) { T $g $subtitle $M 192 15 $C.body $false ($W - 2 * $M) | Out-Null }
}

function Footer {
  param($g, [string]$note, [int]$no, [int]$total = 30)
  Rect $g 0 $FOOTER_Y $W 60 $C.grayBg $null 0 0
  Dot $g $M ($FOOTER_Y + 26) 8 $C.green
  T $g $note ($M + 18) ($FOOTER_Y + 21) 11.5 $C.dim $false 760 | Out-Null
  Rect $g ($W - $M - 100) ($FOOTER_Y + 18) 100 24 '#FFFFFF' $C.line 1 6
  $txt = "$no / $total"
  $f = Font2 12 $false; $b = Brush $C.body
  $tw = $g.MeasureString($txt, $f).Width
  $g.DrawString($txt, $f, $b, [single]($W - $M - 100 + (100 - $tw) / 2), [single]($FOOTER_Y + 21))
  $f.Dispose(); $b.Dispose()
}

function Card {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h, [string]$accent,
        [string]$title, [string]$body, [string]$note = $null, [string]$titleColor = $null)
  Rect $g $x $y $w $h '#FFFFFF' $C.line 1 10
  Rect $g $x $y 5 $h $accent $null 0 3
  $yy = $y + 14
  $tc = if ($titleColor) { $titleColor } else { $C.ink }
  $hTitle = T $g $title ($x + 18) $yy 12.5 $tc $true ($w - 32)
  $yy += $hTitle + 4
  if ($body) { $hBody = T $g $body ($x + 18) $yy 12.5 $C.body $false ($w - 32); $yy += $hBody + 2 }
  if ($note) { T $g $note ($x + 18) $yy 11.5 $C.dim $false ($w - 32) | Out-Null }
}

function NewPage {
  param([string]$path)
  $bmp = New-Object System.Drawing.Bitmap ($W * $SCALE), ($H * $SCALE)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.ScaleTransform($SCALE, $SCALE)
  $g.Clear([System.Drawing.ColorTranslator]::FromHtml('#FFFFFF'))
  return @{ bmp = $bmp; g = $g; path = $path }
}

function SavePage { param($page); $page.g.Dispose(); $page.bmp.Save($page.path, [System.Drawing.Imaging.ImageFormat]::Png); $page.bmp.Dispose() }


# ---------------- 课件小部件 ----------------
function Chip {
  param($g, [double]$x, [double]$y, [string]$text, [string]$fg, [string]$bg, [double]$w = 0, [double]$h = 24)
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
  Rect $g $x $y $w 4 $accent $null 0 2
  $f = Font2 18 $true; $b = Brush $accent
  $g.DrawString($num, $f, $b, [single]($x + 14), [single]($y + 10)); $f.Dispose(); $b.Dispose()
  T $g $title ($x + 14) ($y + 38) 12.5 $C.ink $true ($w - 26) | Out-Null
  T $g $detail ($x + 14) ($y + 64) 11.5 $C.body $false ($w - 26) | Out-Null
}

# 竖向条形图：items = @(@(label, value, displayText), ...)，maxV 用于归一化
function BarsV {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h, $items, [double]$maxV, [string]$accent = '#047761')
  $n = $items.Count
  $slot = $w / $n
  $bw = [Math]::Min(46, $slot * 0.5)
  for ($i = 0; $i -lt $n; $i++) {
    $it = $items[$i]
    $v = [double]$it[1]
    $bh = if ($maxV -gt 0) { ($v / $maxV) * ($h - 42) } else { 0 }
    if ($bh -lt 2) { $bh = 2 }
    $cx = $x + $slot * $i + ($slot - $bw) / 2
    $by = $y + $h - 22 - $bh
    Rect $g ($x + $slot * $i + 6) ($y + $h - 20) ($slot - 12) 3 $C.track $null 0 1.5
    Rect $g $cx $by $bw $bh $accent $null 0 4
    $f = Font2 11.5 $false; $b = Brush $C.body
    $tw = $g.MeasureString($it[2], $f).Width
    $g.DrawString($it[2], $f, $b, [single]($cx + ($bw - $tw) / 2), [single]($by - 17))
    $f.Dispose(); $b.Dispose()
    $f2 = Font2 11.5 $false; $b2 = Brush $C.dim
    $lw = $g.MeasureString($it[0], $f2).Width
    $g.DrawString($it[0], $f2, $b2, [single]($x + $slot * $i + ($slot - $lw) / 2), [single]($y + $h - 16))
    $f2.Dispose(); $b2.Dispose()
  }
}

# 单条堆叠条：items = @(@(label, share 0..1, color), ...)
function StackBar {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h, $items)
  $xx = $x
  foreach ($it in $items) {
    $sw = $w * [double]$it[1]
    Rect $g $xx $y $sw $h $it[2] $null 0 3
    $xx += $sw
  }
  $xx = $x
  foreach ($it in $items) {
    $sw = $w * [double]$it[1]
    T $g $it[0] $xx ($y + $h + 3) 11.5 $C.body $false $sw | Out-Null
    $xx += $sw
  }
}

function MiniTable {
  param($g, [double]$x, [double]$y, [double]$w, $header, $rows, [double]$rh = 26, [double]$fs = 12)
  $n = $header.Count
  $cw = $w / $n
  for ($j = 0; $j -lt $n; $j++) {
    Rect $g ($x + $j * $cw) $y $cw $rh $C.grayBg $C.line 1 4
    T $g $header[$j] ($x + $j * $cw + 8) ($y + 6) $fs $C.ink $true ($cw - 16) | Out-Null
  }
  for ($i = 0; $i -lt $rows.Count; $i++) {
    for ($j = 0; $j -lt $n; $j++) {
      $bg = if ($i % 2 -eq 0) { '#FFFFFF' } else { $C.greenBg2 }
      Rect $g ($x + $j * $cw) ($y + ($i + 1) * $rh) $cw $rh $bg $C.line 1 0
      T $g $rows[$i][$j] ($x + $j * $cw + 8) ($y + ($i + 1) * $rh + 6) $fs $C.body ($j -eq 0) ($cw - 16) | Out-Null
    }
  }
}

function NumCard {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h, [string]$num, [string]$unit, [string]$cap, [string]$accent = '#047761')
  Rect $g $x $y $w $h '#FFFFFF' $C.line 1 10
  Rect $g $x $y 5 $h $accent $null 0 2
  T $g $num ($x + 16) ($y + 12) 26 $accent $true ($w - 34) | Out-Null
  if ($unit) { T $g $unit ($x + 16) ($y + 48) 12 $accent $false ($w - 34) | Out-Null }
  T $g $cap ($x + 16) ($y + 68) 11.5 $C.body $false ($w - 34) | Out-Null
}

# 左侧图示面板：标题 + 绘图区 + 数据图标题 + 数据区
function FigPanel {
  param($g, [double]$x, [double]$y, [double]$w, [double]$h, [string]$figTitle, [string]$dataTitle)
  Rect $g $x $y $w $h '#FFFFFF' $C.line 1 12
  T $g $figTitle ($x + 16) ($y + 12) 12 $C.dim $true 400 | Out-Null
  L $g ($x + 16) ($y + 0.52 * $h) ($x + $w - 16) ($y + 0.52 * $h) $C.line 1
  T $g $dataTitle ($x + 16) ($y + 0.55 * $h) 12 $C.dim $true 400 | Out-Null
}



# ---------------- 版式模板 ----------------
function EndStrips {
  param($g, [string]$mistake, [string]$onlyone, [string]$selftest, [int]$no)
  $by = 782
  if ($mistake) {
    Rect $g $M $by 896 50 $C.redBg $C.red 1 10
    Rect $g $M $by 5 50 $C.red $null 0 2
    T $g '易错' ($M + 16) ($by + 15) 11.5 $C.red $true 40 | Out-Null
    T $g $mistake ($M + 58) ($by + 15) 11.5 $C.body $false 824 | Out-Null
  }
  if ($onlyone) {
    Rect $g 968 $by 576 50 $C.greenBg1 $C.green 1 10
    Rect $g 968 $by 5 50 $C.green $null 0 2
    T $g '只记一件事' (984) ($by + 15) 11.5 $C.green $true 96 | Out-Null
    T $g $onlyone (1084) ($by + 15) 11.5 $C.body $false 452 | Out-Null
  }
  Footer $g ("自测：" + $selftest) $no 27
}

# ① 封面：左标题+目标+结论横幅，右一页看懂卡，底四段链
function CoverPage {
  param($g, $titleParts, $subtitle, $goals, $keywords, $chain, [int]$no)
  Nav $g 1
  Seg $g $titleParts $M 118 40 (1000) | Out-Null
  T $g $subtitle $M 176 15 $C.green $false 1000 | Out-Null
  L $g $M 208 48 3 $C.green 1 | Out-Null
  T $g '本讲目标' $M 228 12.5 $C.ink $true 200 | Out-Null
  $yy = 254
  foreach ($it in $goals) { Dot $g $M ($yy + 6) 6 $C.green; T $g $it ($M + 16) $yy 12 $C.body $false 620 | Out-Null; $yy += 34 }
  Rect $g $M 372 700 62 $C.greenBg1 $C.green 1 10
  T $g '一句话记住：所有问题的答案都落在「谁在哪一层、这一步算完成了吗」' ($M + 16) 386 12 $C.green $true 668 | Out-Null
  T $g '数字必须带口径；未实测一律标「资料不足」，不写毫秒。' ($M + 16) 410 11.5 $C.body $false 668 | Out-Null
  # 右侧卡
  Rect $g 792 118 756 380 '#FFFFFF' $C.line 1 12
  T $g '一页看懂' (816) 134 13 $C.ink $true 200 | Out-Null
  $kx = 816
  foreach ($k in $keywords) { $kw = Chip $g $kx 162 $k $C.green $C.greenBg1; $kx += $kw + 10 }
  L $g 816 208 706 1 $C.line
  T $g '迷你知识地图' (816) 220 11.5 $C.dim $true 240 | Out-Null
  $mods = @('位置', '地址', '执行', '存储', '状态', '平台')
  for ($i = 0; $i -lt 6; $i++) {
    $bx = 816 + ($i % 3) * 236; $by = 248 + [Math]::Floor($i / 3) * 96
    Rect $g $bx $by 214 76 '#FFFFFF' $C.line 1 8
    T $g $mods[$i] ($bx + 12) ($by + 12) 13 $C.ink $true 180 | Out-Null
    if ($i % 3 -lt 2) { Arrow $g ($bx + 216) ($by + 38) ($bx + 232) ($by + 38) $C.arrow 1.2 }
  }
  T $g '先学：位置 / 地址　　后学：执行 / 存储　　易混：状态 / 平台' (816) 356 11.5 $C.green $false 700 | Out-Null
  T $g '六条链：创建 · 执行 · 读文件 · 暂停 · 恢复 · 销毁' (816) 388 11.5 $C.body $false 700 | Out-Null
  T $g '每页一条：模拟图给结构，数据图给数字，右侧四条给机制。' (816) 420 11.5 $C.body $false 700 | Out-Null
  T $g '顶部导航 01 总览 → 02 概念 → 03 例题 → 04 总结' (816) 452 11.5 $C.dim $false 700 | Out-Null
  # 底部四段
  $cy = 528
  for ($i = 0; $i -lt 4; $i++) {
    $cx = $M + $i * 372
    Rect $g $cx $cy 352 118 '#FFFFFF' $C.line 1 10
    Rect $g $cx $cy 5 118 $C.green $null 0 2
    T $g $chain[$i][0] ($cx + 16) ($cy + 12) 13 $C.green $true 300 | Out-Null
    T $g $chain[$i][1] ($cx + 16) ($cy + 40) 11.5 $C.body $false 320 | Out-Null
    if ($i -lt 3) { Arrow $g ($cx + 356) ($cy + 58) ($cx + 366) ($cy + 58) $C.arrow 1.2 }
  }
  Rect $g $M 666 1488 108 '#FFFFFF' $C.line 1 10
  T $g '怎么用这份课件' ($M + 16) 680 12.5 $C.ink $true 200 | Out-Null
  T $g '① 先看左侧模拟图，能把结构复述出来；② 再看右下四条，补机制细节；③ 最后看数据图，记住一个数字或一条换算。每页末尾的「易错 / 只记一件事 / 自测」是复习检查点。' ($M + 16) 706 11.5 $C.body $false 1440 | Out-Null
  Footer $g '白底扁平 · 固定色板 · 每页一个知识点' $no 27
}

# ② 图文页：左模拟图+数据图，右 4 条长机制
function SplitPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $points, $mistake, $selftest, $onlyone, $drawFig, $drawData, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $px = $M; $py = 210; $pw = 660; $ph = 560
  Rect $g $px $py $pw $ph '#FFFFFF' $C.line 1 12
  T $g '模拟图' ($px + 14) ($py + 10) 11.5 $C.dim $true 200 | Out-Null
  L $g ($px + 14) ($py + 26) ($px + 120) ($py + 26) $C.line 1
  & $drawFig $g ($px + 14) ($py + 36) ($pw - 28) 246
  L $g ($px + 14) ($py + 300) ($px + $pw - 14) ($py + 300) $C.line 1
  T $g '数据图' ($px + 14) ($py + 310) 11.5 $C.dim $true 200 | Out-Null
  & $drawData $g ($px + 14) ($py + 338) ($pw - 28) 206
  $cx = 736; $cw = 812; $cy = 210; $ch = 132; $gap = 11
  for ($i = 0; $i -lt $points.Count -and $i -lt 4; $i++) {
    $yy = $cy + $i * ($ch + $gap)
    Rect $g $cx $yy $cw $ch '#FFFFFF' $C.line 1 10
    Rect $g $cx $yy 5 $ch $C.green $null 0 2
    T $g ([string]($i + 1)) ($cx + 12) ($yy + 10) 18 $C.green $true 24 | Out-Null
    T $g $points[$i][0] ($cx + 38) ($yy + 10) 12.5 $C.ink $true ($cw - 52) | Out-Null
    T $g $points[$i][1] ($cx + 38) ($yy + 32) 11.5 $C.body $false ($cw - 54) | Out-Null
  }
  EndStrips $g $mistake $onlyone $selftest $no
}

# ③ 流程页：上四步横排（每步含输入/处理/输出），下三栏机制 + 数据条
function FlowPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $steps, $notes, $mistake, $selftest, $onlyone, $drawData, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $n = $steps.Count
  $gap = 12; $bw = (1488 - $gap * ($n - 1)) / $n; $by = 216; $bh = 168
  for ($i = 0; $i -lt $n; $i++) {
    $bx = $M + $i * ($bw + $gap)
    Rect $g $bx $by $bw $bh '#FFFFFF' $C.line 1 10
    Rect $g $bx $by $bw 4 $C.green $null 0 2
    T $g ([string]($i + 1)) ($bx + 12) ($by + 12) 18 $C.green $true 24 | Out-Null
    T $g $steps[$i][0] ($bx + 38) ($by + 12) 12.5 $C.ink $true ($bw - 50) | Out-Null
    T $g $steps[$i][1] ($bx + 12) ($by + 38) 11 $C.body $false ($bw - 24) | Out-Null
    T $g $steps[$i][2] ($bx + 12) ($by + $bh - 26) 10.5 $C.green $false ($bw - 24) | Out-Null
    if ($i -lt $n - 1) { Arrow $g ($bx + $bw + 1) ($by + 84) ($bx + $bw + $gap - 1) ($by + 84) $C.arrow 1.4 }
  }
  # 三栏机制
  $ny = 404
  $cw = (1488 - 2 * 14) / 3
  for ($i = 0; $i -lt $notes.Count -and $i -lt 3; $i++) {
    $cx = $M + $i * ($cw + 14)
    Rect $g $cx $ny $cw 156 '#FFFFFF' $C.line 1 10
    Rect $g $cx $ny 5 156 $(if ($i -eq 0) { $C.green } elseif ($i -eq 1) { $C.orange } else { $C.red }) $null 0 2
    T $g $notes[$i][0] ($cx + 14) ($ny + 10) 12.5 $C.ink $true ($cw - 28) | Out-Null
    T $g $notes[$i][1] ($cx + 14) ($ny + 34) 11.5 $C.body $false ($cw - 30) | Out-Null
  }
  # 数据条
  Rect $g $M 572 1488 190 '#FFFFFF' $C.line 1 10
  T $g '数据' ($M + 14) 584 11.5 $C.dim $true 100 | Out-Null
  & $drawData $g ($M + 14) 606 1460 146
  EndStrips $g $mistake $onlyone $selftest $no
}

# ④ 表格页：大表 + 右侧三条注
function TablePage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $header, $rows, $colw, $notes, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $tw = 0; foreach ($w in $colw) { $tw += $w }
  $x = $M; $y = 216; $rh = 62
  for ($j = 0; $j -lt $header.Count; $j++) {
    Rect $g ($x) $y $colw[$j] 44 $C.grayBg $C.line 1 6
    T $g $header[$j] ($x + 10) ($y + 12) 12 $C.ink $true ($colw[$j] - 20) | Out-Null
    $x += $colw[$j]
  }
  for ($i = 0; $i -lt $rows.Count; $i++) {
    $x = $M
    for ($j = 0; $j -lt $rows[$i].Count; $j++) {
      $bg = if ($i % 2 -eq 0) { '#FFFFFF' } else { $C.greenBg2 }
      Rect $g $x ($y + 44 + $i * $rh) $colw[$j] $rh $bg $C.line 1 0
      $col = if ($j -eq 0) { $C.ink } else { $C.body }
      T $g $rows[$i][$j] ($x + 10) ($y + 44 + $i * $rh + 10) 11.5 $col ($j -eq 0) ($colw[$j] - 20) | Out-Null
      $x += $colw[$j]
    }
  }
  # 右侧注
  $ny = $y + 44 + $rows.Count * $rh + 16
  for ($i = 0; $i -lt $notes.Count; $i++) {
    Rect $g $M $ny 1488 56 '#FFFFFF' $C.line 1 8
    Rect $g $M $ny 5 56 $C.green $null 0 2
    T $g $notes[$i][0] ($M + 16) ($ny + 8) 12 $C.green $true 200 | Out-Null
    T $g $notes[$i][1] ($M + 220) ($ny + 8) 11.5 $C.body $false 1250 | Out-Null
    $ny += 62
  }
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑤ 公式页
function FormulaPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $formula, $vars, $example, $notes, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  Rect $g $M 216 940 96 $C.greenBg1 $C.green 1.5 10
  $f = Font2 21 $true; $b = Brush $C.green
  $ew = $g.MeasureString($formula, $f).Width
  $g.DrawString($formula, $f, $b, [single]($M + (940 - $ew) / 2), [single]246)
  $f.Dispose(); $b.Dispose()
  Rect $g 1006 216 538 96 '#FFFFFF' $C.line 1 10
  T $g '变量含义' (1024) 228 11.5 $C.ink $true 200 | Out-Null
  T $g $vars (1024) 252 11 $C.body $false 506 | Out-Null
  # 例子
  Rect $g $M 330 940 176 '#FFFFFF' $C.line 1 10
  T $g '代入一个数' ($M + 16) 344 12.5 $C.ink $true 200 | Out-Null
  T $g $example ($M + 16) 372 11.5 $C.body $false 908 | Out-Null
  # 三条注
  Rect $g 1006 330 538 176 '#FFFFFF' $C.line 1 10
  T $g '边界与变形' (1024) 344 12.5 $C.ink $true 200 | Out-Null
  T $g $notes (1024) 372 11.5 $C.body $false 506 | Out-Null
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑥ 例题页：左题面，右三步骤，底答案
function ExamplePage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $question, $known, $steps, $answer, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  Rect $g $M 216 640 300 '#FFFFFF' $C.line 1 10
  T $g '题目' ($M + 16) 230 12.5 $C.ink $true 100 | Out-Null
  T $g $question ($M + 16) 256 11.5 $C.body $false 608 | Out-Null
  T $g '已知' ($M + 16) 360 12 $C.green $true 100 | Out-Null
  T $g $known ($M + 16) 384 11.5 $C.body $false 608 | Out-Null
  $sx = 728; $sy = 216
  for ($i = 0; $i -lt $steps.Count; $i++) {
    $bh = 96
    Rect $g $sx $sy 816 $bh '#FFFFFF' $C.line 1 10
    Rect $g $sx $sy 5 $bh $C.green $null 0 2
    T $g ([string]($i + 1)) ($sx + 14) ($sy + 12) 18 $C.green $true 24 | Out-Null
    T $g $steps[$i][0] ($sx + 40) ($sy + 12) 12.5 $C.ink $true 760 | Out-Null
    T $g $steps[$i][1] ($sx + 40) ($sy + 36) 11.5 $C.body $false 758 | Out-Null
    $sy += $bh + 8
  }
  Rect $g $M 536 1488 96 $C.greenBg1 $C.green 1 10
  T $g '答案' ($M + 16) 550 12.5 $C.green $true 80 | Out-Null
  T $g $answer ($M + 84) 550 11.5 $C.body $false 1390 | Out-Null
  Rect $g $M 644 1488 116 '#FFFFFF' $C.line 1 10
  T $g '解题思路' ($M + 16) 658 12.5 $C.ink $true 120 | Out-Null
  T $g '先定位语义（这条事件/回调对应哪条命令）→ 再列还差哪些动作 → 最后给判据（看到什么才能说完成）。三步都写出来，才算答对；只给结论等于没答。' ($M + 16) 684 11.5 $C.body $false 1440 | Out-Null
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑦ 易错页：红绿对照 6 行
function MistakesPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $rows, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $y = 216
  for ($i = 0; $i -lt $rows.Count; $i++) {
    Rect $g $M $y 1488 82 '#FFFFFF' $C.line 1 8
    Rect $g $M $y 5 82 $C.red $null 0 2
    T $g '错' ($M + 14) ($y + 12) 12 $C.red $true 20 | Out-Null
    T $g $rows[$i][0] ($M + 40) ($y + 10) 11.5 $C.red $false 620 | Out-Null
    T $g '对' ($M + 700) ($y + 12) 12 $C.green $true 20 | Out-Null
    T $g $rows[$i][1] ($M + 726) ($y + 10) 11.5 $C.green $false 740 | Out-Null
    $y += 88
  }
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑧ 卡片页：5 个数字卡 + 口径表
function CardsPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $cards, $table, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $bw = (1488 - 4 * 10) / 5
  for ($i = 0; $i -lt 5; $i++) {
    $bx = $M + $i * ($bw + 10)
    Rect $g $bx 216 $bw 150 '#FFFFFF' $C.line 1 10
    T $g $cards[$i][0] ($bx + 14) 232 26 $C.green $true ($bw - 28) | Out-Null
    T $g $cards[$i][1] ($bx + 14) 272 12 $C.green $false ($bw - 28) | Out-Null
    T $g $cards[$i][2] ($bx + 14) 300 11 $C.body $false ($bw - 28) | Out-Null
  }
  Rect $g $M 386 1488 250 '#FFFFFF' $C.line 1 10
  T $g '口径与出处' ($M + 16) 400 12.5 $C.ink $true 200 | Out-Null
  $hdr = @('数字', '口径', '出处')
  $cw = @(360, 700, 400)
  $x = $M + 16; $y = 430
  for ($j = 0; $j -lt 3; $j++) { T $g $hdr[$j] $x $y 11.5 $C.dim $true $cw[$j] | Out-Null; $x += $cw[$j] }
  $y += 28
  foreach ($r in $table) {
    $x = $M + 16
    for ($j = 0; $j -lt 3; $j++) { T $g $r[$j] $x $y 11.5 $C.body $false $cw[$j] | Out-Null; $x += $cw[$j] }
    $y += 30
  }
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑨ 练习页：三题 + 作答留白
function PracticePage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $qs, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $y = 216
  for ($i = 0; $i -lt 3; $i++) {
    Rect $g $M $y 1488 176 '#FFFFFF' $C.line 1 10
    Rect $g $M $y 5 176 $(if ($i -eq 0) { $C.green } elseif ($i -eq 1) { $C.orange } else { $C.red }) $null 0 2
    $cw = Chip $g ($M + 16) ($y + 14) $qs[$i][0] $(if ($i -eq 0) { $C.green } elseif ($i -eq 1) { $C.orangeDk } else { $C.red }) $C.grayBg
    T $g $qs[$i][1] ($M + 16) ($y + 50) 12.5 $C.ink $false 1440 | Out-Null
    T $g '作答：（留白，自己写三行：结论 / 机制 / 一个可验证的观测）' ($M + 16) ($y + 120) 11 $C.dim $false 1440 | Out-Null
    $y += 188
  }
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑩ 总结页：左 5 条必须会，右 3 件事
function SummaryPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $must, $three, $next, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  T $g '必须会' ($M) 214 12.5 $C.ink $true 120 | Out-Null
  $y = 240
  for ($i = 0; $i -lt 5; $i++) {
    Rect $g $M $y 900 88 '#FFFFFF' $C.line 1 10
    T $g ([string]($i + 1)) ($M + 14) ($y + 12) 16 $C.green $true 24 | Out-Null
    T $g $must[$i] ($M + 44) ($y + 12) 11.5 $C.body $false 840 | Out-Null
    $y += 96
  }
  Rect $g 984 214 560 480 '#FFFFFF' $C.line 1 10
  T $g '如果只记三件事' (1004) 230 13 $C.green $true 300 | Out-Null
  $yy = 262
  for ($i = 0; $i -lt 3; $i++) {
    Rect $g 1004 $yy 520 118 $C.greenBg2 $C.green 1 10
    T $g $three[$i] (1020) ($yy + 14) 11.5 $C.green $false 490 | Out-Null
    $yy += 130
  }
  Rect $g $M 700 1488 62 $C.grayBg $null 0 8
  T $g '下一步' ($M + 16) 714 12 $C.ink $true 70 | Out-Null
  T $g $next ($M + 84) 714 11.5 $C.body $false 1390 | Out-Null
  EndStrips $g $mistake $onlyone $selftest $no
}

# ⑪ 附录页：三栏
function AppendixPage {
  param($g, $section, $titleParts, $subtitle, [int]$nav, $cols, $mistake, $selftest, $onlyone, [int]$no)
  Header $g $section $titleParts $subtitle $nav
  $cw = (1488 - 2 * 14) / 3
  for ($i = 0; $i -lt 3; $i++) {
    $cx = $M + $i * ($cw + 14)
    $accent = if ($i -eq 0) { $C.green } elseif ($i -eq 1) { $C.red } else { $C.orange }
    Rect $g $cx 216 $cw 552 '#FFFFFF' $C.line 1 10
    Rect $g $cx 216 $cw 4 $accent $null 0 2
    T $g $cols[$i][0] ($cx + 14) 230 13 $accent $true ($cw - 28) | Out-Null
    T $g $cols[$i][1] ($cx + 14) 258 11.5 $C.body $false ($cw - 28) | Out-Null
  }
  EndStrips $g $mistake $onlyone $selftest $no
}


# ---------------- 内容 ----------------
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$OUT = Join-Path (Split-Path -Parent $ROOT) '04-AgentENV\图片-30页'
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

$LOG = New-Object System.Collections.Generic.List[string]
function Note($s) { $LOG.Add($s); Write-Host $s }

Set-Location $OUT
