# 第 16 课：pause 时的跨进程读取

2026-11-03。关联：[第 15 课](15-保存范围与父层.md) · [第 2 课](02-指针属于谁.md) · [学习记录](学习记录.md)。固定基线 `9f62cbe07cebfecf416dc9bdcf497e2a97687644`。

## 1. 第 15 课收尾（教师答案，非用户答题）

S2 视图的页 1 来自 S1，页 4 来自 S2；写回原值不保证 dirty 清除；范围列表不冻结数据。本轮因用户要求继续，直接讲解，不自动将三题记为用户掌握。

## 2. 调用者、源与目的

AgentENV server 调用 process_vm_readv，远程 PID 是 Firecracker 宿主 PID，远程地址是 Firecracker 的 HVA，本地目的地址属于 server。不是 Guest 内执行，不把 GVA/GPA 直接作为远程地址，也不要求填写 HPA。

```text
Firecracker Guest RAM 映射
    → 内核执行跨进程复制
    → server 的目的缓冲区
```

普通 pwrite 的源指针属于调用者；因此该实现先获得 server 可访问的字节，再交给后续 writer。不是说原理上只能这样做：Firecracker 自己写其 HVA、共享映射等不同设计可改变路径，但格式、接口和一致性要另行处理。

## 3. iovec 是描述，不是数据

local_iov 描述 server 的目的地址及长度，remote_iov 描述远程源地址及长度；PID 选择地址空间。创建描述本身不复制 payload。源 HVA 和内存镜像 image_offset 是不同位置。

## 4. 当前代码的完整读取循环

read_exact_remote(dst) 在 dst 非空时构造一个远程范围和本地切片，调用 process_vm_readv。成功返回 n 后，远程地址加 n，目的切片前进 n，继续至全部填满。EINTR 重试；零进展、其他错误、异常返回长度、地址转换或加法溢出均报错。空切片直接成功。

例如请求 8192 字节，假设某次仅返回 4096：下一次须从源 HVA+4096 继续填目的 buffer+4096，而不是重读开头。后续失败时 buffer 可能已有部分字节，但函数返回错误，不能当作整段有效。此为短读演示，不保证每次调用固定读多少。

## 5. VirtualFile 抽象与同步边界

ProcessVmReader::new 只保存 PID，不复制 RAM。read_at(offset,len) 分配目的 Vec，read_at_into(offset,dst) 使用调用方提供的可写缓冲区；此实现的 offset 是源 HVA，不是镜像或磁盘偏移。trait 统一接口不保证每种实现参数底层语义相同。

这两个方法虽为 async，但直接调用同步 read_exact_remote；执行 process_vm_readv 期间不会凭 async 自动让出 Tokio worker。阻塞不等于全程 CPU 忙碌。当前代码注释也明确说明 offload 需要处理 owned buffer 等生命周期问题。

## 6. 成功和一致性的边界

完整读取成功仅说明目的 buffer 取得本次所需字节，不表示已封装 OverlayBD、写文件、持久化或形成完整快照。process_vm_readv 不提供整份快照原子性；多个范围/多次读取之间源内容变化仍可能形成不一致。权限、源映射生命周期与目标进程退出等均可能造成失败。

## 7. 课末自测

1. server 发起读取时，remote PID 和 remote address 分别属于谁？目的 buffer 在哪里？
2. 请求 8192 字节首次返回 4096，下一次源地址和目的位置怎样前进？
3. read_at_into 返回 Ok(dst.len()) 后，能否认为快照已经持久化？

来源：[固定版 process_vm_reader.rs](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/src/sandbox/firecracker/process_vm_reader.rs)、[Linux process_vm_readv 手册](https://man7.org/linux/man-pages/man2/process_vm_readv.2.html)。本轮读取源码，不是实际调用测试，未操作公司服务器。

## 8. 精讲补充：描述数组、向量顺序与内核复制

local_iov 与 remote_iov **两个数组本身都在调用者地址空间**；remote_iov 元素里的 iov_base 数值才指向目标进程内存。内核先从调用者导入元数据，再按目标 mm 解释远程地址。不能把 remote_iov 参数指针本身也误填成目标进程地址。

liovcnt/riovcnt 是元素数量，不是字节数，flags 必须为 0；长度不必逐项相等，源和目的均按数组顺序消费，支持多个远程段拼入一个本地段。受 IOV_MAX、长度溢出等限制，不能一次无限传入所有范围。

Linux v6.14 的 mm/process_vm_access.c 可见：import_iovec/iovec_from_user 导入描述；find_get_task_by_vpid 找目标，mm_access 以 PTRACE_MODE_ATTACH_REALCREDS 检查权限并取得目标 mm；pin_user_pages_remote 获取远程后端页；process_vm_rw_pages 使用 copy_page_to_iter 复制到本地目的；完成相应批次后解除 pin。这是所读内核版本的实现导航，不声称所有版本内部代码相同。

pin 保证处理中页面资源的相应生命周期，不冻结字节；目标进程未被这个调用自动暂停。页可能需按需准备，不是只查现成 PTE。返回正数也可能只是部分进展，后面遇到失败不会回滚已复制的字节。

“无需中间内核数据缓冲区”不是“内核不参与”，更不是零复制。内核可以直接从远程页向本地用户缓冲区复制，无需另做一份 payload 中转；仍存在真实字节复制和元数据/页引用等内核管理开销。调用没有自动映射共享，返回后 server 修改目的内容不会自动修改远程源。

常见错误：EPERM 是访问权限不足（不等于一律只能 root）；ESRCH 是找不到目标任务等情形；EFAULT 可能涉及本地/远程访问；EINVAL 包括 flags/向量数量/长度等问题；ENOMEM 表示内核内部资源分配失败。ptrace 检查不等于必须先 ptrace attach；不要为方便读取而直接关闭安全限制。

相关源：[Linux v6.14 mm/process_vm_access.c](https://github.com/torvalds/linux/blob/v6.14/mm/process_vm_access.c)。本轮未修改/运行内核或远程进程；buffer、进程映射和一致性仍由上层正确管理。
