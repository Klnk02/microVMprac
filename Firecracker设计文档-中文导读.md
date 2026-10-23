# Firecracker 设计文档：中文学习导读

> 本文依据 Firecracker 官方 `docs/design.md` 整理，按原文结构概括各节，供学习时快速建立整体图景；不是逐句全文翻译。实现和支持范围可能随版本变化，具体以链接中的官方文档及对应版本源码为准。
>
> 原文：[Firecracker Design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md) · [Raw Markdown](https://raw.githubusercontent.com/firecracker-microvm/firecracker/main/docs/design.md)

## 1. 文档讨论范围

Firecracker 是一种虚拟化技术，用于运行轻量级微型虚拟机（microVM）。设计目标是结合传统虚拟机的安全隔离能力与容器的启动速度、灵活性和资源效率，服务多租户工作负载。本文讨论的是 Firecracker 虚拟机监视器（VMM）的特性和架构；更完整的接口约束见官方 [技术规格](https://github.com/firecracker-microvm/firecracker/blob/main/docs/SPECIFICATION.md)。

文档列出的能力包括：同一宿主机运行不同租户的工作负载；按需配置 vCPU 与内存；在宿主机允许的范围内超额分配 CPU 和内存；每台 microVM 提供面向宿主机的 API，并能向 guest 提供由宿主配置的元数据。原文还给出了特定最小 guest 配置下的启动速率示例。这类数字依赖版本、硬件与测试条件，不宜脱离测试环境当作通用性能承诺。

## 2. 与宿主机集成

Firecracker 运行在 Linux 宿主机上，guest 也使用 Linux。生产部署应通过 `jailer` 启动 Firecracker。启动进程后，操作者先通过 Firecracker API 配置 microVM，再发出 `InstanceStart` 请求。

- **网络**：Firecracker 模拟的网络设备连接到宿主机 TAP 设备；其余主机侧网络接入由宿主网络方案提供。
- **存储**：模拟块设备以宿主机文件作为后端；宿主机文件需要包含 guest 内核能够识别的文件系统，guest 才能挂载。

理解边界时要区分：Firecracker 暴露给 guest 的是虚拟设备，TAP 和宿主文件则是宿主侧的接入方式。guest 不会因此直接取得宿主文件路径或宿主网络设备的任意访问权。

原文的宿主集成示意图：[Firecracker Host Integration](https://github.com/firecracker-microvm/firecracker/blob/main/docs/images/firecracker_host_integration.png)

## 3. 内部架构

一个 Firecracker 进程承载一台 microVM。原文把线程职责分成三类：

| 线程 | 主要职责 |
|---|---|
| API 线程 | 运行 Firecracker HTTP API，接收配置与控制请求；不处在虚拟机的快速执行路径上 |
| VMM 线程 | 提供机器模型、必要的设备模拟、MMDS，以及 VirtIO 网络、块和 vsock 设备；通过基于 `epoll` 的事件循环处理设备事件及 API 线程转发的请求 |
| vCPU 线程 | 每个 guest CPU 核心对应一个线程，通过 KVM 建立并循环调用 `KVM_RUN` 运行 guest；设备访问需要由虚拟化设备模型处理 |

当 API 请求暂停 microVM，VMM 线程停止轮询设备事件循环，并仅处理 API 请求，直到恢复。因此文档所述 `Paused` 状态下，vCPU 和设备模型都不再运行。暂停是设备与执行状态转换的一部分；涉及快照与恢复时还应结合官方[快照文档](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)。

## 4. 威胁隔离

从安全设计角度，guest vCPU 一旦启动，就按可能执行恶意代码处理。Firecracker 通过由低信任到高信任的多层边界收敛风险。比如 guest 发出的网络数据，会由 Firecracker 的 IO 线程从模拟网卡送往宿主 TAP 设备，并在该处执行 IO 限速。Firecracker 本身不负责过滤 guest 的出站网络流量，宿主侧应另行进行网络过滤。

原文的信任边界示意图：[Threat Containment](https://github.com/firecracker-microvm/firecracker/blob/main/docs/images/firecracker_threat_containment.png)

这里的重点是纵深防御：KVM 与虚拟机边界负责一层隔离，VMM 进程权限和资源约束负责另一层。单一边界不应被当作所有安全控制的替代品。

## 5. 机器模型与设备

Firecracker 为 guest 提供 VirtIO 网络和块设备，并提供串口控制台、部分键盘控制器；I8042 设备可用于通知 microVM guest 请求重启。guest 也会看到 KVM 支持的中断控制器和定时器等设备模型。

Firecracker 可通过 CPU 模板控制暴露给 guest 的处理器信息。guest 可见的时钟源与架构相关：文档列出 x86_64 的 `kvm-clock`、`tsc`，以及 aarch64 的 `arch_sys_counter`；对特定版本的 Linux guest，文档还说明了稳定性判断与默认选择行为。具体系统支持情况应查看所用版本的文档。

## 6. IO、限速与元数据

Firecracker 可以对块设备卷和网络接口实施限速，帮助多个 microVM 公平共享宿主资源。文档描述的限速采用令牌桶机制，分别约束操作速率和带宽，并允许配置桶容量、补充速率、单次 IO 成本、突发上限和初始令牌等参数。若使用 vhost-user 设备，限速应由相应后端负责。

MicroVM Metadata Service（MMDS）让 guest 经由特定接口获取宿主机配置的元数据；元数据内容由用户配置。

## 7. 进程沙箱、jailer 与资源配额

Firecracker 的安全隔离由多层措施组成。KVM 和虚拟化边界提供基础隔离；进程层则用 seccomp 限制系统调用，并结合 cgroup、namespace 和降权限制 Firecracker 进程能做的事。

Firecracker 默认安装 seccomp 过滤器，以每线程方式限制允许使用的系统调用及其参数。`jailer` 在启动 Firecracker 前设置需要较高权限才能建立的资源（例如 cgroup 和 chroot），随后降低权限并 `exec()` Firecracker。进入受限进程后，Firecracker 只能使用第三方明确授予的资源，例如放入 chroot 的文件或传递给它的文件描述符。

cgroup 还可用于约束每台 microVM 的 CPU 使用配额和 CPU 亲和性。亲和性可以避免 microVM 随线程迁移到其他节点，从而造成性能影响和额外竞争。

## 8. 监控

Firecracker 通过传入的命名管道输出日志和指标。日志逐行刷新；指标在实例启动时、运行过程中按周期发出，并在 panic 时输出。收集和保存这些日志文件属于使用方的责任。生产构建中不会暴露串口控制台，因为其中可能含有宿主机不应读取的 guest 数据。

## 术语速查

| 术语 | 本文语境下的含义 |
|---|---|
| microVM | Firecracker 创建和运行的轻量级虚拟机 |
| VMM | 虚拟机监视器；在 Firecracker 中负责虚拟机模型与设备模拟等工作 |
| guest / host | 虚拟机内部系统 / 运行虚拟机的宿主机系统 |
| VirtIO | guest 驱动与虚拟设备后端之间使用的半虚拟化设备接口 |
| vCPU 线程 | 在宿主机线程上通过 KVM 运行 guest CPU 的执行线程 |
| TAP | Linux 宿主机上的虚拟二层网络设备，接入 Firecracker 模拟网卡 |
| MMDS | MicroVM Metadata Service，向 guest 提供宿主配置的元数据 |
| jailer | 为 Firecracker 设置初始资源约束并降权的启动程序 |
| seccomp | Linux 系统调用过滤机制 |

## 建议的阅读顺序

1. 先画出 host、Firecracker 进程、vCPU/VMM/API 线程、guest 和外部 TAP/块文件。
2. 沿着启动与暂停路径，区分 API 控制路径和 guest 的 vCPU/设备 IO 路径。
3. 选块设备或网络设备，分别跟踪 guest 驱动、VirtIO 队列、Firecracker 设备模型和宿主后端。
4. 再回到威胁隔离章节，逐条标注数据跨越 host/guest 边界的位置，以及每个边界实际控制什么。
