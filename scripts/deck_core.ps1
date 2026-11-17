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

# ---------------- 内容 ----------------
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$OUT = Join-Path (Split-Path -Parent $ROOT) '04-AgentENV\图片-30页'
New-Item -ItemType Directory -Force -Path $OUT | Out-Null

$LOG = New-Object System.Collections.Generic.List[string]
function Note($s) { $LOG.Add($s); Write-Host $s }

Set-Location $OUT
