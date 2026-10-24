# 第 4 课：谁在执行 Guest 指令

关联：[学习计划](00-学习计划.md) · [第 3 课](03-Guest内存与宿主映射.md) · [学习记录](学习记录.md) · [第 5 课](05-Firecracker线程与暂停.md)

本页整理 2026-10-24 对话。示例为普通 x86 KVM 模型的纸面推演，没有运行真实 microVM 实验，也未确认 AgentENV 部署的 Firecracker 版本。

## 1. 四个对象

| 对象 | 含义 |
|---|---|
| microVM | 一台轻量虚拟机实例，提供 Guest 所见的 vCPU、RAM 和设备，运行 Guest 内核和应用 |
| Firecracker | 宿主用户态 VMM 进程，准备虚拟机资源，提供设备模型并驱动 vCPU 执行 |
| KVM | 宿主 Linux 内核的虚拟化子系统，通过硬件虚拟化机制运行 Guest |
| 宿主操作系统 | 调度宿主线程、管理物理内存和设备；KVM 属于其内核 |

AgentENV 在上层组织沙箱创建、命令执行、存储、网络、快照和回收。server 是 AgentENV 节点服务端进程，Firecracker 是由它控制的独立宿主进程。控制关系不意味着每条 Guest 指令都经过 server。

## 2. CPU 执行过程：每一步说清主语

```text
物理 CPU 执行 Firecracker 的 vCPU 线程代码
    ↓ vCPU 线程调用 ioctl(vcpu_fd, KVM_RUN)
物理 CPU 执行宿主内核中的 KVM 代码
    ↓ KVM 准备状态，借助硬件执行 VM-Entry
物理 CPU 执行 Guest 代码
    ↓ CPU 遇到配置的退出条件，发生 VM-Exit
物理 CPU 执行宿主内核中的 KVM 退出处理代码
    ├─ KVM 可处理：处理后再次进入 Guest
    └─ 需要用户态处理：KVM_RUN 返回，CPU 继续执行 Firecracker 代码
```

以 Intel x86 为例，进入 Guest 使用 VMLAUNCH/VMRESUME 等硬件机制。“KVM 进入 Guest”是简写：物理 CPU 执行 KVM 代码，由 KVM 控制硬件切换执行状态；不是 KVM 这个程序搬到 Guest 内运行。

CPU 执行环境包括指令位置、栈、权限、地址翻译及虚拟化控制等状态。硬件与 KVM 软件共同保存、恢复必要状态；不能认为所有寄存器都由硬件自动切换。磁盘和网卡的完整设备状态也不是每次 VM-Exit 都整体保存恢复。

## 3. 三个边界

| 边界 | 发生的变化 | 必然切换宿主线程吗 |
|---|---|---|
| KVM_RUN 系统调用 | Firecracker 用户态进入宿主内核 | 否 |
| VM-Entry/VM-Exit | Guest 与宿主执行环境切换 | 否 |
| 宿主线程切换 | 调度器让 CPU 执行另一个宿主线程 | 是 |

VM-Exit 回到宿主内核，不等于 KVM_RUN 已返回宿主用户态。KVM 可以处理退出事件并重入 Guest，整个调用仍未返回。

两个 vCPU 通常由两个宿主 vCPU 线程承载，不表示永久独占两个物理核心。宿主调度器可以暂停调度 vCPU 线程，转而运行其他线程。

## 4. 两类退出示例

- 普通 RAM 已登记，但缺少 EPT 映射：在正常可处理路径中，KVM 找到后端页并建立映射，直接重新进入 Guest，无需返回 Firecracker。
- 访问需要用户态设备模型处理的 MMIO 地址：KVM_RUN 以 KVM_EXIT_MMIO 等相应结果返回，Firecracker 处理后再次运行 vCPU。不是所有 MMIO 都必然返回用户态，具体路径取决于设备及配置。

退出原因还可能涉及外部中断等事件，不能仅按“Guest 是否主动请求设备”判断。VM-Exit 频率取决于负载与配置，不是每条指令、每次访存或每次系统调用都退出。

## 5. Guest 系统调用和 EPT

Guest Python 发起系统调用时，首先进入 Guest 内核。Guest 用户态与 Guest 内核态都属于 Guest 执行环境；权限切换本身不要求 VM-Exit。

```text
Guest 正常 RAM 访问：GVA → Guest 页表 → GPA → EPT → HPA
Firecracker 自身访问：HVA → 宿主页表 → HPA
```

两条路径可以访问同一物理页。KVM 建立或维护映射时使用 memslot/HVA 等软件关系，不意味着 Guest 每次访存都经过 HVA。

HPA 回答“数据实际位于哪里”；Guest/宿主执行环境回答“CPU 按哪套状态执行”。访问宿主物理内存不等于执行宿主代码，也不等于 VM-Exit。EPT 有效且权限允许时，CPU 通常直接完成普通 RAM 访问。

## 6. 答题证据与待验证项

- 用户正确解释两个 vCPU 不等于独占两个物理核心。
- 用户正确判断 Guest getpid 系统调用不必 VM-Exit。
- 用户正确判断修复 EPT 后重入 Guest 不必切换宿主线程。
- VM-Exit 与 KVM_RUN 返回、HPA 与执行环境的区别已讲解，但仍需用户换场景复述。课程保持学习中。

## 来源

- [KVM API：KVM_RUN](https://docs.kernel.org/virt/kvm/api.html#kvm-run)
- [KVM x86 MMU](https://docs.kernel.org/virt/kvm/x86/mmu.html)
- [Firecracker 上游设计](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)：用于机制说明，非已核实部署版本。
- [AgentENV 固定版本架构](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/docs/src/internals/architecture.md)
