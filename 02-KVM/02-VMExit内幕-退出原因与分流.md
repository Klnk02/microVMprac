---
title: VM-Exit 内幕 · 退出原因与分流
tags:
  - kvm
  - vm-exit
  - virtualization
---

# VM-Exit 内幕 · 退出原因与分流

核心：VM-Exit 不是软件主动触发，是 CPU 硬件先斩后奏——先把现场和原因写进 VMCS，再跳到内核态 handler。

要回答三个问题：退出时 CPU 写了什么？KVM_RUN 怎么把原因告诉用户态？不同原因怎么分流？

## ① CPU 写进 VMCS 的东西

VMCS 内存上分两大区域（进/退出时硬件自动读写）：

| 区域 | 全称 | 作用 |
|---|---|---|
| guest-state area | guest 状态区 | 存 guest 寄存器快照（RIP/RSP/控制寄存器），退出时塞入，VM-Entry 时恢复 |
| host-state area | host 状态区 | 存 hypervisor 寄存器，退出时载入，切到宿主内核态 |

外加两个关键字段，回答「为什么退出」：

| 字段 | 全称 | 装什么 |
|---|---|---|
| exit reason | 退出原因码 | 数字，回答「发生了哪类事」 |
| exit qualification | 退出限定/详情 | 补充细节：具体哪个 I/O 端口 / 哪个 GPA |

## ② KVM_RUN 如何把原因交给用户态

每次 `ioctl(vcpufd, KVM_RUN)` 返回时，内核往共享内存 `kvm_run` 结构体填 `exit_reason` 字段：

```c
for (;;) {
    ioctl(vcpufd, KVM_RUN);        // 阻塞跑到退出，kvm_run->exit_reason 被填好
    switch (kvm_run->exit_reason) {
        case KVM_EXIT_IO:            走设备 I/O 模拟;    break;
        case KVM_EXIT_MMIO:          走内存映射 I/O 模拟; break;
        case KVM_EXIT_SHUTDOWN:      guest 关机了;       break;
    }
}
```

`exit_reason` = 内核态里 CPU 写的退出原因，翻译成用户态枚举值。

## ③ 三种典型退出（Firecracker 运行时主力）

- **特权指令退出**：guest 执行 `lgdt`/`cli` → 非根模式遇敏感指令 → 退出 → KVM 软件模拟出指令效果（不真关中断，只在状态里记「guest 以为关了」）。
- **设备 I/O 退出**：guest 执行 `out`/`in` 或 MMIO 碰假设备地址 → 退出（MMIO 靠 EPT 故意不给映射，一碰就拦）→ KVM 打包给用户态 → QEMU/Firecracker 模拟设备 → 再 `KVM_RUN` 还权。
- **EPT 缺页 / violation**：guest 访问未映射 GPA 或权限不足 → 退出，`exit qualification` 里记 GPA → KVM 判断：真缺页就补 HPA 映射放行；是 MMIO 就转给用户态。

## 一句话收束

> VM-Exit 的本质，是把「硬件无声的拦截」变成「一次带原因的显式返回」，让用户态 VMM 能在每条导致退出的指令上拿到控制权。VMM 的所有智能都挂在 exit reason 上。

参见 [[01-KVM原理-设备节点与ioctl]]、[[02-EPT与VT-x]]。