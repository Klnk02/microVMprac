# DSH 导入：Agent 沙箱学习模式

这是本仓库自带的教学预设（DSH bundle），目的是**换一台机器、换一个 DSH 会话，也能原样接续这套教学**：教师人格、教学信条、实验红线、学生档案、当前「面试优先」模式和接续顺序都写在里面。

## 导入步骤

1. 在目标机器上把本仓库放到 DSH 的工作区（例如 `D:\learning\Learning\microVMprac`）。
2. 把 `dsh-preset/` 整个目录复制到 DSH 工作区的 bundle 目录并改名：

   ```powershell
   # Windows
   Copy-Item -Recurse -Force "microVMprac\dsh-preset" "$HOME\.dsh-bundles\study-mode"
   ```

   ```bash
   # Linux / WSL
   cp -r microVMprac/dsh-preset ~/.dsh-bundles/study-mode
   ```

   本机当前使用的 bundle 位置是 `D:\learning\Learning\.dsh-bundles\study-mode\`，两份内容应保持一致；改了其中一份记得同步另一份。

3. 重启 DSH，在预设（preset）选择里选 **「Agent 沙箱学习模式」**。
4. 新会话第一句话可以直接说「继续学习」，教师会按 persona 里的接续顺序先读：
   `AGENTS.md` → `04-AgentENV/学习记录.md` → `04-AgentENV/面试题库.md` → `04-AgentENV/源码索引.md`。

## 文件构成

| 文件 | 作用 |
|---|---|
| `package.json` | DSH bundle 声明，指向 `cordis.patch.yml` |
| `cordis.patch.yml` | 预设定义：persona 系统提示 + 工具插件清单 |

## 与仓库文档的分工

- **persona（本目录）**：教学方式、判据、红线、接续顺序。稳定，少改。
- **`AGENTS.md`**：给「读仓库的 agent」的同一套约定摘要，保证不导入 bundle 也能接续。
- **`04-AgentENV/学习记录.md`**：进度与接续点，每轮更新。
- **`04-AgentENV/面试题库.md`**：当前模式的题库、四段式模板、五个必深点。

改动 persona 时请同时更新本 README 的版本号与下表记录。

## 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-11-11 | 1.1.0 | 增加学生档案、接续顺序、面试优先模式（四段式答题、五个必深点、不贴原语言源码、承认并修正自身错误） |
