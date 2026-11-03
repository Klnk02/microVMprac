# 第 17 课：chunk 写出与快照封存

2026-11-03。基线 `9f62cbe07cebfecf416dc9bdcf497e2a97687644`。关联：[第 16 课](16-pause跨进程读取.md) · [学习记录](学习记录.md)。本轮实际读取 helper.rs 的 CompactChunkEntry/CompactChunk、compact_read_chunk/compact_write_chunk、compact_to，以及 overlaybd_snapshot.rs 的 publish_memory_overlaybd_layer。

## 1. 三个对象

entry 描述一段源读取，包括 tag、src_offset、len、logical_offset；chunk 是把若干 entry 组织起来的批次，带总长度和输出位置等信息；buffer 是实际装载 payload 的内存。创建 chunk 不等于已经复制数据，chunk 也不是 Guest 内运行的对象。

## 2. 元数据与字节两条线

```text
元数据：范围映射 → entry/chunk → 输出索引（逻辑范围→层内位置）
字节：Firecracker 源 HVA → ProcessVmReader → server buffer → writer
```

普通源层的 src_offset 是源文件位置；在 ProcessVmReader 上是 Firecracker HVA。logical_offset 表示完整镜像位置，输出 payload 存放位置由 writer 布局决定，不把三者当同一地址。

假设两段数据各 4 KiB，逻辑位置分别 4 KiB 和 36 KiB，装进同一个 8 KiB chunk buffer。buffer 中可以紧邻存放两份内容，但索引仍记录其逻辑位置分散；不能把逻辑间隙误填成连续数据或零。示意大小不代表真实 writer.buffer_size。

## 3. 当前代码的读取与写入

compact_read_chunk 先 writer.alloc_buffer，再顺序遍历 chunk.entries，调用选定 source 的 read_at_into 填入 buffer 的对应切片；校验 got==entry.len，同时生成输出 SegmentMapping。对 ProcessVmReader，每个 entry 调用又可能因短读循环多次 PVM；一个 chunk 不保证一次 syscall。

准备好后 compact_write_chunk 将持有数据的 buffer、预定 destination_offset 和 len 交给 writer。buffer 生命周期必须覆盖实际写入；异步提交不自动表示可立即复用。当前 read_at_into 的同步 PVM 不因调用链 async 自动变成异步 IO。

并发可让不同 chunk 完成顺序不同，当前结构携带 order 和目标位置来组织结果；不是按任务完成顺序随意拼接镜像。chunk大小、并发度、syscall次数和真实磁盘IO次数是不同指标。

## 4. 生成完整层格式

compact_to 写 header、数据、排序/整理后的索引、trailer，并调用 writer.finalize。以原始层作概念图：header | payload | index | trailer（含对齐，压缩封装另按 writer 解释）。索引使稀疏逻辑范围能对应紧凑存放的数据；payload 完整但缺索引或 trailer 仍不能据此视为有效层。

源码注释明确：finalize 表示 writer 完成格式处理，不保证已同步到稳定存储。源读/目的写/finalize 失败均返回错误，不能把 buffer 填满或最后一次普通 write 成功当作整层成功。

publish_memory_overlaybd_layer 使用临时输出路径，compact_to 成功后 rename 为最终路径；错误时尝试清理临时文件。rename 切换名字不自动保证断电持久化，也不代替 VM 状态、父层引用、磁盘和 manifest 的整体发布。

## 5. 完成边界

源读取完成 → chunk 数据准备好 → chunk 写入完成 → 全部层格式/finalize 完成 → 层路径发布 → 完整快照发布/持久化：这些完成条件分别检查。后续恢复从完整逻辑视图按需加载，写出顺序不等于恢复访问顺序。

## 6. 自测

1. 一个 chunk 有两段不连续逻辑范围，buffer 里紧邻存放后，为什么仍需要两段映射信息？
2. chunk 有两个 entry，是否保证只调用一次 process_vm_readv？
3. writer.finalize 成功、临时文件 rename 成功，是否足以证明完整快照已断电持久化？

来源：[helper.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/storage/overlaybd/src/lsmt/file/helper.rs)、[overlaybd_snapshot.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/src/sandbox/firecracker/overlaybd_snapshot.rs)。本轮为源码与纸面推演，未做实际快照读写测试。

## 7. chunk、队列与批量读取优化候选

用户曾将 chunk 理解成批处理，随后感觉像队列缓冲区。三者应分开：chunk 是一批任务描述，buffer 装本批实际字节，queue 可以组织等待处理的多个任务。按 writer buffer 容量组织 chunk 会使其尺寸相关，但不代表对象相同，也不能仅凭 chunk 结构断定系统存在某种专用队列。

用户提出这是优化点。候选方案是把逐 entry 的跨进程读取进一步批量化：

- 同一 PID 下，源 HVA 和目的区域都相邻时，可以考虑合并连续范围。
- 源不连续时，可以给 process_vm_readv 多个 remote iovec，并按顺序填入本地 buffer；一般 VirtualFile 来源不一定是同一 PID，需在合适抽象层提供专用批量接口，不能直接无条件改通用 reader。
- 始终保留各段的逻辑镜像位置；拼紧 payload 不表示逻辑地址也连续。
- 处理 IOV_MAX、长度与地址溢出、跨 entry 短读进度、失败后的部分 buffer、源映射与 buffer 生命周期；不改变快照一致性要求。
- 衡量每 chunk 的 entry 数及大小、PVM 调用次数/耗时、端到端捕获时间与 CPU 成本。entry 少而大时，减少调用的收益可能很小；不可未经测量就声称加速。

这是讨论中的优化假设，仅保存到笔记；未修改 AgentENV 实现、未做基准，也未把误发 Copier 实验数据作为证据。
