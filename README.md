# microVMprac

从零到一理解 [Firecracker](https://github.com/firecracker-microvm/firecracker)（AWS 的轻量级 microVM 监视器）的学习笔记仓库。

以**苏格拉底式提问**推进：不直接给结论，而是从最底层原理一步步推导，目标是「不仅会用，更理解原理」。

## 学习路线

当前阶段：继续学习沙箱相关知识，吃透其原理、组成与关键调用链，通过源码、日志和小实验核对理解。

长期方向与阶段验收见：[[Agentic-Infra长期竞争力与2027春季求职计划]]（目标求职窗口：2027 年 3—4 月）。

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

> [!note] Obsidian
> 本仓库同时是 Obsidian 库 `D:\learning\Learning` 的子目录，笔记可在 Obsidian 中直接阅读（支持 wikilink、callout、SVG 嵌入）。

## 学习进度

- [x] Linux 地基：[[进程与系统调用]]、[[特权级与地址空间]]、[[多级页表]]、[[硬件隔离与软件隔离]]
- [ ] 虚拟化核心概念
- [ ] KVM
- [ ] 硬件虚拟化
- [ ] Firecracker
