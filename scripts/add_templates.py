# -*- coding: utf-8 -*-
"""在 deck_core.ps1 里加 8 套版式模板（封面/图文/流程/表格/公式/例题/易错/卡片/练习/总结/附录）。"""
import io

p = r"D:\learning\Learning\microVMprac\scripts\deck_core.ps1"
s = io.open(p, encoding="utf-8-sig").read()
if "function SplitPage" in s:
    print("already")
    raise SystemExit

TEMPLATES = r'''
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

'''

s = s.replace("# ---------------- 内容 ----------------", TEMPLATES + "\n# ---------------- 内容 ----------------")
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("templates appended")
