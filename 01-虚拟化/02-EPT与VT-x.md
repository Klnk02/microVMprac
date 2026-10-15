---
title: EPT 与 VT-x（硬件虚拟化基础）
tags:
  - virtualization
  - ept
  - vtx
  - trap
---

# EPT 与 VT-x

三个承重概念：trap、VT-x、EPT。

## trap（陷阱）

CPU 在检测到越权操作时，中止当前指令流、把控制权交给预设处理程序、并保存现场（处理完可原样恢复）。

- 已见过的 trap 是同一机制：`syscall` 陷入内核、#GP（ring3 执行特权指令）、#PF（碰 supervisor 页）。
- 为什么可行：CPU 取指 / 执行流水线内置特权检查，越权必被硬件发现。
- 虚拟化 = 把 guest 降权 / 放非根模式，让敏感操作都变成 trap，hypervisor 当处理程序（trap-and-emulate）。
- 前提（Popek-Goldberg 条件）：所有敏感指令都要能 trap。x86 有漏网（`pushf` / `popf`），所以纯软件方案不完整 → VT-x。

## VT-x

Intel 硬件虚拟化扩展（AMD-V / SVM）。核心：两套模式。

- 根模式 root mode：hypervisor 跑（真 ring0）。
- 非根模式 non-root mode：guest 跑（名义 ring0 是假的）。
- VM-Exit：非根 → 根，保存 guest / 恢复 host，跳到 hypervisor 处理函数。
- VM-Entry：根 → 非根，恢复 guest。
- VMCS：记录两边状态 + 触发 VM-Exit 的配置。
- vCPU：hypervisor 把 guest CPU 当线程调度到物理核。
- 顺带带 EPT 做内存虚拟化。

## EPT（第二层页表）

- GVA / GPA / HPA：guest 虚拟 / guest 物理（假）/ host 物理（真）。
- 老办法 shadow page table：hypervisor 维护 GVA→HPA，guest 改页表就要 VM-Exit 重算，慢。
- EPT：CPU 硬件两层翻译，MMU 一次访问同时走两套四级页表：GVA →（guest 页表）→ GPA →（EPT）→ HPA。
- guest 改自己页表无需 VM-Exit；hypervisor 用第二层 EPT 隔离。
- 代价：一次最多 4+4=8 级，靠 TLB / 大页缓解。

## 与进程地址空间的区别

同一套「多级页表 + MMU」机制，不同层：

- 进程页表 = OS 隔离进程（VA → PA）。
- EPT = hypervisor 隔离 guest（GPA → HPA）。

> [!tip] 一句话
> guest 之于 host，正如进程之于 OS。