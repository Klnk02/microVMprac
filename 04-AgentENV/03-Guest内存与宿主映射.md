# 第 3 课：Guest 内存与 Firecracker 映射怎样对应

关联：[学习计划](00-学习计划.md) · [第 2 课](02-指针属于谁.md) · [学习记录](学习记录.md)

本课只建立一个认识：在本课程的普通 KVM 用户态内存后端模型中，Guest 与 Firecracker 可以通过不同地址访问同一份宿主物理内存。先看一个已建立、稳定的普通 RAM 映射；后续再加入缺页、COW、回收与快照。

## 1. 四个名字各自从哪里观察

| 名称 | 全称 | 从哪个角度描述地址 |
|---|---|---|
| GVA | Guest Virtual Address | Guest 程序使用的虚拟地址 |
| GPA | Guest Physical Address | Guest 内核认为的物理地址 |
| HVA | Host Virtual Address | 某个宿主进程使用的虚拟地址；必须同时说明属于哪个进程 |
| HPA | Host Physical Address | 宿主机器的实际物理地址 |

GPA 中的“物理”是相对于 Guest 而言。HVA 也不是全宿主统一的一套虚拟地址；本课重点讨论 Firecracker 的 HVA，server 的 HVA 属于另一个进程。

## 2. 从一份数据出发

课堂假设：Guest 中某变量当前值为 42。它位于一张实际宿主物理页上，Guest 程序和 Firecracker 分别用自己的映射访问它。

下面地址仅为示意，不是运行环境取证：

```text
Guest 程序使用 GVA 0x400000
         │ Guest 页表
         ▼
        GPA 0x2000
         │ EPT（以 Intel x86 为例）
         ▼
        HPA 0xA12000  ←──── Host 页表 ──── Firecracker HVA 0x70002000
         │
         ▼
       值为 42
```

Guest 访存的概念路径是 `GVA → GPA → HPA`；Firecracker 访问其自身映射的路径是 `HVA → HPA`。两条路径落在同一物理页上，因此这里没有必须来回同步的两份数据。

HVA 没有被串进 Guest 的硬件访存路径。硬件可能使用缓存过的地址翻译结果，不必每次重新遍历所有页表；图表示映射关系，不表示每次访存的全部内部动作。

## 3. 这种对应关系从哪里来

KVM 的 `KVM_SET_USER_MEMORY_REGION` 接收一段 Guest 物理地址范围及其用户态内存地址。关键字段包括 `guest_phys_addr`、`userspace_addr`、`memory_size`。

用伪代码表达一段登记关系：

```cpp
// 课堂说明，不是 AgentENV 某版本的完整实现代码
guest_phys_addr = 0x00000000;
userspace_addr  = 0x70000000; // Firecracker 进程中已有的有效内存映射
memory_size    = 1 * MiB;
```

这表示 Guest 的相应物理范围由 Firecracker 这段映射提供。对于其中 `GPA = 0x2000` 的位置，在该范围内可找到 `Firecracker HVA = 0x70002000`。KVM 和宿主内存管理根据后端页建立相应映射，具体物理页可以按需准备或变化。

登记范围不是把一份数据复制到另一份 RAM，也不能简化成登记时一次性固定填完全部 EPT；本课不依赖这种错误假设。

依据：[KVM_SET_USER_MEMORY_REGION 文档](https://www.kernel.org/doc/html/latest/virt/kvm/api.html#kvm-set-user-memory-region)。该例针对普通用户态内存模型，其他架构或机密虚拟机后端不在本课范围。

### 3.1 Firecracker 先建立自己的映射

下面是 C++ 风格的接口示意，不是完整可运行的 VM 程序；省略 VM 创建、检查和资源清理，只表示关键参数：

```cpp
size_t size = 128ULL * 1024 * 1024;
void* ram = mmap(nullptr, size,
                 PROT_READ | PROT_WRITE,
                 MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
// ram 在这里是 Firecracker 地址空间内的 HVA。
// 实际程序必须检查 MAP_FAILED，并管理整个映射生命周期。
```

匿名 mmap 建立可用的虚拟内存映射，不意味着此时立刻为全部 128 MiB 分配了物理 RAM。文件后端恢复时也可以通过映射提供 Guest RAM；本例先用匿名内存展示接口关系。

### 3.2 把范围描述通过 ioctl 交给 KVM

`vm_fd` 表示先前通过 `KVM_CREATE_VM` 创建的那台虚拟机的宿主文件描述符。它是控制该 VM 的句柄，不是快照文件。

```cpp
kvm_userspace_memory_region region{};
region.slot            = 0;
region.flags           = 0;
region.guest_phys_addr = 0;
region.memory_size     = size;
region.userspace_addr  = reinterpret_cast<uint64_t>(ram);

ioctl(vm_fd, KVM_SET_USER_MEMORY_REGION, &region);
// 实际程序需检查返回值；失败时不能假定登记已经完成。
```

`slot` 是这台 VM 内一段 RAM 范围的编号；`guest_phys_addr` 是 Guest 起点；`userspace_addr` 是调用登记的 Firecracker 进程中后端映射的起点。三者配合长度，构成范围关系。这里只示意一段简单 RAM，并不是完整 x86 机器地址布局。

Firecracker 上游 `vstate/vm.rs` 可见 `register_memory_region`、`set_user_memory_region` 和 `VmFd` 包装调用。Rust 包装最后使用的是这类 KVM ioctl；本文查阅的上游 main 未与 AgentENV 安装的 Firecracker 二进制对齐。

### 3.3 KVM 先记录 memslot 关系

内核检查参数、范围与冲突等条件，并为对应 VM 记录内存区域，通常称为 memslot。这个登记描述从 Guest 物理范围到调用者用户内存范围的对应。

若本例 `ram` 恰好为 `0x70000000`，访问范围内的 `GPA 0x2000` 时，软件可计算对应 HVA：

```text
HVA = userspace_addr + (GPA - guest_phys_addr)
    = 0x70000000 + (0x2000 - 0)
    = 0x70002000
```

ioctl 会传递并保存必要的描述信息；它不为 Guest 另造一份 RAM，也不搬运这 128 MiB payload。源映射需要由 Firecracker 持续保持有效。

### 3.4 实际 GPA→HPA 映射可按需建立

以 Intel EPT 为例，如果 Guest 访问某 RAM GPA 时缺少相应翻译，概念过程是：

```text
CPU 发现缺少 EPT 翻译，退出到 KVM
  → KVM 按 GPA 找 memslot
  → 计算对应 Firecracker HVA
  → 经宿主内存管理取得实际后端页，必要时触发缺页准备
  → 建立 GPA 指向该实际页的 EPT 条目和访问权限
  → 继续 Guest 执行
```

这只是普通 RAM 缺失映射的教学主路径，不覆盖 MMIO、权限异常或所有预填充/大页策略。这类退出通常可以由 KVM 内核处理后继续，不必每次都让 `KVM_RUN` 返回 Firecracker 用户态。

已有有效翻译时，CPU 可通过 EPT/TLB 等硬件机制完成 Guest 访问，不再每次运行上述软件查找。memslot 的 `GPA→HVA` 是建立/维护硬件翻译时使用的软件关系；CPU 正常 Guest 访存仍是 `GVA→GPA→HPA`。

本节检查：**登记 128 MiB 区域时，ioctl 传递的是整份内存内容，还是描述地址范围的信息？它为什么没有要求用户填写 HPA？**

实现来源：[Firecracker 上游 vm.rs](https://github.com/firecracker-microvm/firecracker/blob/main/src/vmm/src/vstate/vm.rs)、[Linux v6.14 KVM 核心代码](https://github.com/torvalds/linux/blob/v6.14/virt/kvm/kvm_main.c) 与本页 KVM API/MMU 文档。不同来源各自用于核对机制，不表示它们就是同一份部署版本。

## 4. Guest 修改后，Firecracker 为什么能读到

假设 Guest 把变量从 42 改成 43。在图示稳定映射下，它最终改的是那个宿主物理位置。随后 Firecracker 通过指向同一位置的 HVA 读取，就可看到更新。

这里先按执行顺序明确、访问正确同步且映射稳定的情况推演。并发无同步访问、COW 和页映射变化另课分析，不能据此宣称跨线程数据天然无竞态。

## 5. 接回 AgentENV 的跨进程提取

现在把 server 接进来：

```text
Guest：修改某页
          ↓ 改变对应 RAM 内容
Firecracker 的 Guest RAM 映射
          ↓ server 指定 Firecracker PID 和 HVA，调用 PVM
server 自己的目的缓冲区
```

server 提取这段内容时，远程指针需要按 Firecracker 的地址空间解释。因此在已确认的 AgentENV reader 实现里，remote address 使用 Firecracker HVA；它不接收 Guest 应用 GVA，也不要求调用者直接填写 HPA。

当前 reader 的代码入口见 [固定版本 process_vm_reader.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/src/sandbox/firecracker/process_vm_reader.rs)。源码将 reader 的 offset 明确解释为 HVA，并把它作为远程范围地址交给 PVM。

## 6. 为什么 Guest 内的 write 不等于宿主快照写入

Guest 程序执行 write 时，系统调用由 Guest 内核处理，文件描述符和虚拟地址也在 Guest 的上下文中解释。需要设备 IO 时，再通过虚拟设备等机制与宿主协作。

这与宿主 server 调用 pwrite 保存快照是两条调用链。Guest 可以正常访问自己的内存；保存快照仍需明确由哪个宿主组件读取、如何格式化以及写到哪个宿主文件。

## 7. 本课检查一题

### 本轮要点整理（2026-10-23）

- `guest_phys_addr` 是这段 RAM 在 Guest 物理地址空间中的起点，不是宿主物理地址 HPA。
- Firecracker 向 KVM 登记 GPA 起点、自己的 HVA 起点和长度。登记的是范围关系，不是复制整份 RAM。
- Firecracker 无需自行提供 HPA；KVM 借助宿主内存管理取得实际物理页。页面尚未准备好时，不能简化成只读取已有页表项。
- memslot 提供 GPA 与 HVA 的软件对应关系；Guest 正常硬件访存路径是 GVA → GPA → HPA（通过 Guest 页表与 EPT）。
- `process_vm_readv` 的远程 PID 填 Firecracker 进程号，远程地址填 Firecracker HVA，本地缓冲区属于调用者 server。

例如 region 的 GPA 起点为 `0`、HVA 起点为 `0x70000000`，则 GPA `0x2000` 对应：

```text
HVA = HVA 起点 + (目标 GPA - GPA 起点)
    = 0x70000000 + (0x2000 - 0)
    = 0x70002000
```

这个偏移计算要求目标位于该 region 内。server 用上述 HVA 跨进程读取，再把本地缓冲区交给快照写入逻辑；这一步不要求 server 知道 HPA。

用户已正确判断远程地址属于 Firecracker 的 HVA；回答中的 PID/地址称呼和十六进制笔误已澄清。后续继续学习快照范围如何确定与读取，而不重复这一题。

沿用课堂假设：Guest 使用 `GVA = 0x400000`，相应 Guest 物理位置为 `GPA = 0x2000`；Firecracker 中对应的 `HVA = 0x70002000`。

**server 要通过 process_vm_readv 读取这一页，已经指定 Firecracker PID。remote_iov 中的源地址应该填哪一个？为什么？**

换条件题：如果 Firecracker 因重新启动把自己的内存映射放到另一个 HVA，Guest 对应 GPA 是否必然需要跟着变化？先根据登记关系推理；实际重建流程在恢复课核对。

课末产物：分别画出 Guest 与 Firecracker 的两条访存路径，并在 PVM 上标出调用者、远程 PID、远程地址和目的缓冲区所属进程。

补充来源：[KVM x86 MMU 文档](https://docs.kernel.org/virt/kvm/x86/mmu.html)。本课纸面映射未在真实 microVM 中测出，不把示意地址当作 HPA 或服务器状态证据。
