# AgentENV 图解复习材料的维护

主文件为 `04-AgentENV/复习-AgentENV图解增强版.pptx`，配套入口为 `04-AgentENV/复习-AgentENV图解手册.md`。原 `复习-AgentENV全课20讲.pptx` 保留作历史参考，本次不覆盖。

本版共68页，覆盖第1—24课和冷热/脏页专题，另附设备准备、内存布局、完整读时序与异步执行器微观图。文本、图形、连接线及19张表格使用原生可编辑对象。正文给图、机制和边界，备注给解释、答案与来源。示意地址与时间线不冒充实测，配套Firecracker的映射模式仍保留核验边界。

## 源文件

- `build_agentenv_visual_review.mjs`：使用 `@oai/artifact-tool` 生成68页草稿，图与文字均在此维护。`review` 字典提供紧凑图旁的机制说明与边界说明。
- `build_agentenv_review_handbook.py`：读取构建元数据，生成21主题手册，复制31张选定页面到 `assets/agentenv-review/`。仅使用Python标准库，不生成PPT。
- `finalize_agentenv_review.mjs`：调用演示文稿技能的校验器，另存校验后的输出，保留原草稿。

默认构建目录为仓库父目录的 `.review-build/`，不在Git仓库内。需修改运行时位置时设置 `CODEX_REVIEW_RUNTIME`，技能目录可设置 `CODEX_REVIEW_PRESENTATION_SKILL`。默认路径是当前Codex桌面环境的已安装版本；迁移环境后应先重新加载其依赖路径，不安装替代依赖。

## 重建与检查

用Codex提供的Node运行时执行 `build_agentenv_visual_review.mjs`，随后执行 `finalize_agentenv_review.mjs`。后者会打印校验后PPT的路径。逐页查看 `.review-build/render/` 下的图片，尤其检查文字换行、箭头方向、位图与表格内容；自动检查通过不代表视觉检查通过。

确认后将已校验输出原样复制到 `04-AgentENV/复习-AgentENV图解增强版.pptx`，再用Python运行 `build_agentenv_review_handbook.py`。更新页码时同步修改导航、手册分组与备注中的实验页码。改变页数或表格所在页时同步修改校验策略。

更新后检查Markdown所有本地链接、图片、PPT备注及来源，再按用户授权提交。材料完善不改变用户独立掌握状态。不要把旧动画中尚未核实的匿名页/共享缓存解释直接移植到本版。
