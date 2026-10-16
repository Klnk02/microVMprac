---
title: Firecracker 本体 · 定位与 virtio
tags:
  - firecracker
  - virtio
  - rust
---

# Firecracker 本体 · 定位与 virtio

## Firecracker vs QEMU：差在哪

QEMU = 万能模拟器（BIOS/显卡/USB/声卡/PCI/热迁移），代码大、启动慢、攻击面大。

Firecracker 只回答一个极窄问题：跑一个**不需要 BIOS/显卡、只要网卡+磁盘+串口**的最小 Linux guest，跑快、跑安全。

| | QEMU | Firecracker |
|---|---|---|
| 语言 | C | Rust（内存安全、无 GC、单二进制） |
| 设备 | 全都要 | 只留 virtio-net / virtio-block / 串口+键盘 |
| 定位 | 通用 | microVM 专用 |
| 常驻内存 | MB 级 | 几百 KB 级 |

一句话：**Firecracker = 骑在 KVM 上的、只做最小设备集的、Rust 写的极简 VMM**，底层仍是 `ioctl(KVM_RUN)` 死循环。

## virtio：为什么高效

### 传统模拟的痛点

给 guest 模拟真实设备（如 e1000 网卡），guest 用真实驱动，每个寄存器访问都是一次 VM-Exit，发一个包退出几十上百次。

### 半虚拟化（paravirtualization）

- **全虚拟化**：guest 不知道自己被虚拟，装真硬件驱动，逐条模拟真实硬件动作。
- **半虚拟化**：guest 知道被虚拟，装专用 virtio 驱动，与 host 约定高效自定义协议，不做硬件 cosplay。

### virtio 的三个部件

1. **virtqueue（虚拟队列）**：guest 与 host 共享的物理内存（靠 EPT：guest 的 GPA 与 host 的 HVA 指向同一块 HPA）。分三个环：
   - descriptor ring（描述符环，guest 写）：数据在哪、多大、方向。
   - available ring（可用环，guest 写）：我放好活儿了。
   - used ring（已用环，host 写）：我干完了。
2. **门铃（doorbell）**：一块 MMIO 地址，guest 写一下触发 1 次 VM-Exit，通知 host。
3. **设备配置空间（MMIO）**：特性握手。

### 数据流（以发网络包为例）

```mermaid
graph LR
    A["guest 写数据到共享内存"] --> B["填 descriptor + available"]
    B --> C["敲门铃（1 次 VM-Exit）"]
    C --> D["host 读队列"]
    D --> E["host 真实 syscall send/write"]
    E --> F["写 used ring，通知 guest"]
```

**关键洞察**：数据搬运全程走共享内存，零 VM-Exit；只有"通知"敲门铃才付 1 次 VM-Exit。传统模拟"每寄存器退出一次"被压成"批量 + 1 次门铃"。

### 共享内存到底怎么"共享"（具体数字）

总纲：地址 = 名字 + 真实位置。同一块物理内存可以被多个名字指到，就像同一个人有多个外号。共享 = 两套表把两个不同外号翻译到同一个 HPA。

具体例子：

1. Firecracker 进程 `mmap` 一块 4KB，HVA = `0x7f00_0000`。宿主页表：`HVA 0x7f00_0000 → HPA 0x1000_0000`。
2. Firecracker 调 `KVM_SET_USER_MEMORY_REGION`：guest 的 GPA `[0x0, 0x1000)` 对应我进程里的 HVA `0x7f00_0000`。
3. KVM 查宿主页表把 HVA→HPA，再在 EPT 填：`GPA 0x0 → HPA 0x1000_0000`。

结果：

| 谁写 | 外号 | 翻译表 | 最终落到 |
|---|---|---|---|
| guest | GPA `0x0` | EPT | HPA `0x1000_0000` |
| Firecracker | HVA `0x7f00_0000` | 宿主进程页表 | HPA `0x1000_0000` |

guest 写 `[0x0]` 与 Firecracker 写 `*(0x7f00_0000)`，落的是同一块物理内存。

**融会贯通**：这跟 Linux 里"两个进程靠 mmap 共享内存"是同一原理——同一物理页被两个页表项映射，虚拟化只是把其中一套页表换成 EPT、把其中一个进程换成整台 guest。

参见 [[02-VMExit内幕-退出原因与分流]]、[[01-KVM原理-设备节点与ioctl]]。