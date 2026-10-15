---
title: Type 1 / Type 2 与 KVM / QEMU 分工
tags:
  - virtualization
  - hypervisor
  - kvm
---

# Type 1 / Type 2 与 KVM / QEMU 分工

## 一句话分水岭

> hypervisor 下面是「裸硬件」，还是「另一个完整的操作系统」？

- **Type 1（裸机 bare-metal）**：hypervisor 直接管硬件，自己当最底层管家。
- **Type 2（寄居 hosted）**：hypervisor 是宿主 OS 里的一个普通程序，靠宿主 OS 调度和内存管理才能活。

## 分层对比

```
Type 1（裸机型）            Type 2（寄居型）
─────────────────          ─────────────────
  guest / guest / ...        guest / guest / ...
─────────────────          ─────────────────
  Hypervisor（自己当 OS）      Hypervisor（一个程序）
─────────────────          ─────────────────
    硬件 CPU/RAM/IO           宿主 OS（Windows/Linux）
                          ─────────────────
                             硬件 CPU/RAM/IO
```

- Type 1 亲自做三件事：调度 vCPU、切内存、分 I/O，干的就是操作系统的活，只是它管理的"进程"是一整台虚拟机。性能高、攻击面小、启动快。
- Type 2 凭空多一层：guest 想碰真硬件，得先经过 hypervisor、再经过宿主 OS。好处是装个软件就能用。

## vCPU = 宿主内核里的一个线程

关键类比：**vCPU 就是宿主内核里被调度的一个线程**，直接复用 Linux 的线程调度器。

但要和普通线程区分：

| | 普通线程 | vCPU 线程 |
|---|---|---|
| 被调度上核后 | 执行宿主自己的代码 | 执行 `VMRESUME`，把 CPU 交给 guest |
| 结果 | CPU 跑宿主函数 | CPU 切非根模式，guest 指令真跑硬件 |

## KVM 的真实定位（混合型）

数据流：

```
宿主内核调度 vCPU 线程 → 线程执行 VMRESUME → CPU 进非根模式
   → guest 指令在硬件上真跑（VT-x 管特权、EPT 管内存）
   → 越权/敏感 → VM-Exit → 回到内核态 KVM 处理
```

整条链上，guest 的指令执行和内存访问**从头到尾没经过宿主用户态**。QEMU 只在 VM-Exit 原因是「设备 I/O」时被唤起，模拟完再 `VMRESUME` 还权。

- **形式**：借住在 Linux 内核里，像 Type 2。
- **实质**：宿主内核直接管硬件、guest 直跑硬件，就是 Type 1 的能力。

所以教科书叫它「混合型」，或直接说「Linux + KVM 合起来就是一个 Type 1 hypervisor」。

## KVM vs QEMU 分工

> KVM 管最硬最重的两件事（CPU + 内存）；其余全交给 QEMU 模拟。

| 组件 | 运行态 | 职责 |
|---|---|---|
| KVM | 内核态 | CPU 虚拟化（VT-x）、内存虚拟化（EPT） |
| QEMU | 用户态 | 模拟磁盘/网卡/串口/PCI 等「假设备」，靠系统调用写真实文件/发真实网络 |

```
guest（跑在 CPU 非根模式，EPT 管内存）        ← KVM 负责
        │  设备 I/O → VM-Exit
        ▼
QEMU（用户态进程）：模拟磁盘/网卡/串口         ← QEMU 负责
        │  调系统调用 read/write/send
        ▼
宿主 Linux 内核 + 真实硬件
```

## 伏笔：Firecracker 的位置

Firecracker = QEMU 的极简替身：同样骑 KVM，但用 Rust 从零写，只保留 microVM 需要的极少数设备（virtio-net、virtio-block、串口、键盘），砍掉 BIOS/显卡/USB/热迁移等一切多余。启动快、内存小、攻击面小。

参见 [[01-虚拟化的本质]]、[[02-EPT与VT-x]]。