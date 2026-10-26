# microVMprac

从零到一理解 [Firecracker](https://github.com/firecracker-microvm/firecracker)（AWS 的轻量级 microVM 监视器）的学习笔记仓库。

以**引导式教学**推进：从具体场景出发，结合直接解释、用户推理与换条件验证，目标是「不仅会用，更理解原理」。不同 agent 接续时先读 [教学约定](AGENTS.md) 与 [学习记录](04-AgentENV/学习记录.md)，保持教学方式和进度一致。

## 学习路线

当前阶段：继续学习沙箱相关知识，吃透其原理、组成与关键调用链，通过源码、日志和小实验核对理解。

长期方向与阶段验收见：[[Agentic-Infra长期竞争力与2027春季求职计划]]（目标求职窗口：2027 年 3—4 月）。

Firecracker 官方设计文档的中文学习导读：[[Firecracker设计文档-中文导读]]。

2026-10-23 起，基于 AgentENV 按课学习：[[04-AgentENV/00-学习计划|28 课详细计划]] → [[04-AgentENV/01-系统地图与第一课|系统地图与第一课]]。当前进度与答题证据记录在 [[04-AgentENV/学习记录]]，固定版本入口见 [[04-AgentENV/源码索引]]。

1. **Linux 操作系统基础** —— 进程、特权级、系统调用、内存与页表
2. **虚拟化核心概念** —— VM vs 容器、Hypervisor、Type 1/2
3. **KVM 原理** —— 内核如何变成 hypervisor、KVM 与 QEMU 的分工
4. **硬件虚拟化** —— VT-x / AMD-V、EPT、VM-Exit、IO 虚拟化
5. **Firecracker 本体** —— VMM、virtio、vhost、seccomp / chroot、最小化哲学

## 目录结构

| 目录 / 文件 | 说明 |
|---|---|
| [[术语表]] | 英文缩写滚动清单（PML4、CPL、MMU…） |
| `00-Linux基础/` | 第一层：Linux 地基 |
| `assets/` | 笔记引用的示意图（SVG） |
| `01-虚拟化/` `02-KVM/` … | 后续按路线逐层新增 |
| `04-AgentENV/` | 系统地图、逐课计划、源码导航与学习记录 |

> [!note] Obsidian
> 本仓库同时是 Obsidian 库 `D:\learning\Learning` 的子目录，笔记可在 Obsidian 中直接阅读（支持 wikilink、callout、SVG 嵌入）。

## 学习进度

- [x] Linux 地基：[[进程与系统调用]]、[[特权级与地址空间]]、[[多级页表]]、[[硬件隔离与软件隔离]]
- [ ] 虚拟化核心概念
- [ ] KVM
- [ ] 硬件虚拟化
- [ ] Firecracker
