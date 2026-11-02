# 第 12 课：ublk 如何连接内核与用户态存储

2026-11-02 第一轮。基线 `9f62cbe07cebfecf416dc9bdcf497e2a97687644`。本课按「整课连续讲解、课末集中自测」写：先讲角色，再讲创建设备和一次 4 KiB 读取，最后集中自测。

**要解决的问题**：OverlayBD 是用户态的存储代码，怎样让 Firecracker 把它当作一块磁盘来读取？

**一句话答案**：ublk 在宿主内核提供块设备接口，`uvm-ublk-daemon` 在用户态接住块请求，再交给 OverlayBD 找数据。

## 前置知识：daemon、系统调用与 io_uring

daemon 是通常长期在后台提供服务的普通进程，不是内核线程或特殊硬件；没工作时可以等待，不要求一直占用 CPU。系统调用是用户态请求内核服务的入口，例如 read；线程在阻塞等待时可以让出 CPU，而“位于某个系统调用中”本身并不证明线程一直睡眠。

内核通知 daemon，不是内核直接调用 daemon 内的 Rust/C++ 函数。内核准备描述和事件，daemon 被调度后在用户态读取并处理，随后通过接口报告结果。

io_uring 的两个共享队列与数据缓冲区分工：

| 对象 | 谁发布 | 放什么 |
|---|---|---|
| SQ（提交队列） | 用户态程序 | 要内核执行的操作描述，例如 fd、offset、len、buffer 信息 |
| CQ（完成队列） | 内核 | 对应操作的结果与关联信息 |
| buffer | 按操作约定由读取方/写入方访问 | 实际数据字节 |

普通 READ 的完成结果 4096 表示实际读到 4096 字节，不是数据内容。ublk 的“领取请求”命令完成表示任务到达，不表示实际磁盘数据已取得。多个操作可并发、完成顺序可能不同；CQ 的含义要结合对应 SQ 操作判断。共享队列不自动消除系统调用或所有数据复制。

传统交接中涉及 FETCH_REQ 和 COMMIT_AND_FETCH_REQ 一类命令，具体内核版本命名和能力不同，先按“领取／处理／报告完成”理解。参考 [io_uring 手册](https://man7.org/linux/man-pages/man7/io_uring.7.html) 与文末内核 ublk 文档。

## 一、角色放对位置

| 组件 | 所在位置 | 负责什么 |
|---|---|---|
| Firecracker | 宿主用户态进程 | 处理 Guest 的虚拟设备请求，访问后端存储 |
| ublk 驱动 | 宿主内核 | 提供块设备接口，组织请求交接 |
| `uvm-ublk-daemon` | 宿主用户态进程 | 管理设备，执行具体存储处理 |
| OverlayBD | daemon 依赖的库 | 查询层索引，读写分层数据 |
| AgentENV server | 宿主用户态进程 | 让 daemon 建盘，再把盘交给 Firecracker |

三点容易忽略：

1. **daemon 是处理工作的进程，OverlayBD 是它调用的库**，不是两个必须通过网络通信的服务。
2. daemon 是**集中式**的：一个进程管理所有 ublk 设备（`main.rs` 的说明为 "Centralized ublk device manager daemon"）。server 通过 **Unix socket** 发控制请求（`--socket_path`），和 Firecracker 的 `--api-sock` 同一种模式：**控制面走 socket，数据面走块设备**。
3. `/dev/vda` 与 `/dev/ublkbN` 分属 Guest 与宿主，不是同一个节点的两个名字。

## 二、三个设备名

| 名称 | 用途 |
|---|---|
| `/dev/ublk-control` | 全局管理接口：创建、删除、设置参数 |
| `/dev/ublkcN` | 该设备的控制字符设备：daemon 与内核交接 IO 命令、读取请求描述 |
| `/dev/ublkbN` | 对外读写的**块设备** |

`N` 是内核分配的编号。**Firecracker 作为磁盘后端访问的是 `/dev/ublkbN`**，不是全局管理接口，也不是控制字符设备。

设备创建/参数设置主要走全局 control；daemon 的每设备 IO 命令交接使用 ublkcN；Firecracker 对外发起读写使用 ublkbN。不能把 ublkcN 简化成“只用于管理、不参与 IO 交接”。

## 三、创建阶段：先有设备，才有读取

```text
daemon 启动，监听 Unix socket
    ↓
server 发送 CreateOverlaybd{image_config, global_config}
    ↓
daemon 创建 UVMUblkDev<OverlaybdTarget>，向 ublk 驱动注册
    ↓
内核出现块设备 /dev/ublkbN（编号由内核分配）
    ↓
daemon 等这个节点真正可打开（wait_for_ublk_dev）
    ↓
daemon 把 (dev_id, device_path) 回给 server
    ↓
Firecracker 把它作为 drive 后端挂到 Guest 的 /dev/vdX
```

两个细节：

- **等待节点可打开**，不只是“文件存在”。注释说明块节点可能先出现、udev 还没改好组和权限，非 root 消费者会打开失败。
- `N` 由内核分配，**不能当作随实例固定的编号**；server 侧保存的是 `(dev_id, path)`。

## 四、完整走一次 4 KiB 读取

假设 Guest 文件系统已经算出：要读的数据在虚拟磁盘逻辑偏移 **8 MiB**，长度 **4 KiB**。以下位置与编号均为课堂假设，并先忽略缓存命中的捷径。

```text
Guest 文件系统
    ↓
Guest VirtIO 块设备驱动
    ↓
Firecracker 虚拟设备处理代码
    ↓
宿主后端 /dev/ublkbN
    ↓
ublk 内核驱动
    ↓
daemon 调用 OverlayBD
    ↓
具体层的数据
```

**第一步：daemon 提前等待工作。** daemon 在 io_uring 上提交等待命令，意思类似“有块请求时交给我”。此时还没有要求 OverlayBD 读某个文件，只是在建立接收等待。

**第二步：内核交付请求。** 请求描述包含：操作（READ）、逻辑位置（8 MiB）、长度（4 KiB）、身份（队列编号 + tag）、缓冲区信息。内核通过 io_uring 完成事件让 daemon 知道“请求到了”。

**关键区别**：这里完成的是**领取请求**的命令本身，原来的 4 KiB 读取还没有完成。`tag` 是队列内编号，多个请求同时在飞，靠它把结果对回原请求。

**第三步：OverlayBD 找数据。** daemon 把逻辑位置和长度交给 OverlayBD，它查索引回答：这段逻辑区间由哪一层提供、该层里的数据在哪。**逻辑偏移不等于层文件中的实际偏移。** 命中可用缓存就直接取；否则按后端实现发起读取，此时才涉及实际字节。

**第四步：提交完成。** 数据准备好后，daemon 向 ublk 驱动报告结果，内核据此完成原块请求。有些交接模式把“报告完成”和“安排下一次领取”合并为一条命令，但**不表示**下一项已经处理完。

## 五、结果怎样回到 Guest

```text
daemon 提交处理结果
    ↓
ublk 完成宿主块 IO
    ↓
Firecracker 得到后端结果
    ↓
发布 VirtIO 完成信息，必要时通知 Guest
    ↓
Guest 驱动处理结果
    ↓
文件系统继续完成读取
    ↓
应用的 read() 返回
```

每一层的“完成”只说明那一层完成了自己的工作：

- daemon 拿到请求 ≠ 数据已读出；
- 后端数据已读出 ≠ Guest 驱动已处理；
- Guest 驱动处理完 ≠ 应用已执行下一行代码。

遇到 CQ 事件先问：**它对应的提交操作是什么？** 普通 READ 的完成和“等待请求”命令的完成，含义不同。

## 六、边界

- **缓存会缩短路径**：Guest 页缓存命中可能不产生 VirtIO 读；宿主或 OverlayBD 缓存命中可能不再访问底层存储。
- **底层请求不包含 Guest 文件名**：`/workspace/a.txt` 由 Guest 文件系统解释；到 ublk 层只剩操作、逻辑位置、长度。
- **数据不靠完成记录承载**：描述区与队列负责交接，实际字节在 buffer 里；具体复制或共享方式取决于实现，不能凭流程图数出固定复制次数。
- **失败必须正确返回**：后端读失败不能当作“成功读到数据”，错误要沿调用链传播；daemon 无响应可能使 IO 停滞或失败，取决于配置与实现。
- **快照恢复依赖它**：`sandbox.rs` 检查“恢复内存需要可用的 ublk daemon client”，因为内存恢复使用共享 ublk 设备，第 14—18 课再展开。

## 七、证据边界

- 已核对（固定提交）：daemon 包名与 `--socket_path`、集中管理说明、`DaemonRequest` 的 Create/Delete/Acquire/Release 等分支、`UblkDevice { dev_id, device_path }`、`/dev/ublkbN` 等待逻辑、Firecracker `add_drive` 使用设备路径、快照恢复对 ublk 的依赖。
- 未核对：队列深度、io_uring 命令组合细节、错误码映射、缓存与预热池参数。课上的 8 MiB / 4 KiB、`N` 均为示意。
- 路径只针对所选 OverlayBD/ublk 磁盘后端，不代表所有 Firecracker 磁盘后端；普通缓冲读取可能命中缓存，图示是简化路径。

## 八、课末自测

1. daemon 收到“请求已到达”的 CQ 事件后，为什么还不能认为数据已经读出？
2. OverlayBD 命中缓存时，是否还必须再发一次磁盘读取，才能报告完成？

只讲解不计独立验收。

用户课末回答证据：①知道领取任务后还要查找；校准为 OverlayBD 查询数据映射并取得字节，而非查找事件。②正确判断缓存命中不必再读取磁盘。两项是局部独立作答，不等于实测或全实现验收。

## 源码锚点

- [main.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/storage/ublk-daemon/src/main.rs)
- [server.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/storage/ublk-daemon/src/server.rs)
- [storage/ublk/src/lib.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/storage/ublk/src/lib.rs)
- [src/sandbox/ublk/device.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/src/sandbox/ublk/device.rs)
- [src/sandbox/firecracker/sandbox.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/src/sandbox/firecracker/sandbox.rs)
- [Linux ublk 文档](https://docs.kernel.org/block/ublk.html)
