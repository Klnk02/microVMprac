"""Generate the illustrated Markdown companion from reviewed slide metadata.
Only stdlib is used; this script does not author PowerPoint.
"""
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILD = REPO.parent / '.review-build'
COURSE = REPO / '04-AgentENV'
ASSETS = REPO / 'assets' / 'agentenv-review'
groups = [
    ('系统角色与三条路径', [3, 4], [3], '01-系统地图与第一课.md'),
    ('地址空间、memslot与跨进程读取', [5, 6, 7, 8], [5, 7], '03-Guest内存与宿主映射.md'),
    ('KVM_RUN、TLB与暂停', [9, 10, 11], [9], '04-Guest指令执行.md'),
    ('VirtIO描述符、环与通知', [12, 13, 14, 63], [13, 63], '06-VirtIO描述符队列与通知.md'),
    ('设备准备与就绪', [16, 62], [62], '08-启动与就绪.md'),
    ('控制请求与命令事件流', [15, 17], [17], '09-命令执行与事件流.md'),
    ('完整Guest文件读取与SQ/CQ', [18, 19, 20, 21, 22, 64], [19, 64], '12-ublk与存储daemon.md'),
    ('OverlayBD层、索引和零覆盖', [23, 24], [23], '11-OverlayBD层与索引.md'),
    ('mmap、缺页与COW', [25, 26, 27], [26, 27], '13-mmap缺页与COW.md'),
    ('快照材料、完成边界与一致性', [28, 29, 30, 68], [28, 68], '14-快照状态与一致性.md'),
    ('冷热、脏页跟踪与EPT', [31, 32, 33, 34, 35, 65, 66], [33, 35, 66], '15a-冷热页与脏页跟踪.md'),
    ('pause捕获、chunk与buffer', [36, 37, 38], [37], '17-chunk写出与快照封存.md'),
    ('层格式、封存与持久化', [39], [39], '17-chunk写出与快照封存.md'),
    ('恢复、按需加载与外部状态', [40, 41, 42], [40], '18-从快照恢复.md'),
    ('网络包与发送完成', [43], [43], '19-网络包怎样出去.md'),
    ('隔离机制的作用对象', [44], [44], '20-各种隔离分别限制什么.md'),
    ('资源拥有、回收与寿命', [45, 46], [46], '21-资源拥有与回收.md'),
    ('async、线程阻塞与取消', [47, 48, 67], [67, 48], '22-async与并发.md'),
    ('结果未知、幂等和重试', [49, 50], [49], '23-失败与恢复.md'),
    ('性能度量与公平实验', [51, 52, 53, 54, 55, 56, 57], [51, 54, 56], '24-性能指标怎样读.md'),
    ('综合推演与下一步', [58, 59, 60, 61], [59], '学习记录.md'),
]

def main():
    slides = json.loads((BUILD / 'slides.json').read_text(encoding='utf-8'))
    ASSETS.mkdir(parents=True, exist_ok=True)
    txt = [
        '# AgentENV 图解复习手册', '',
        '更新：2026-11-13。覆盖第1—24课与冷热/脏页专题，配套 [68页图解PPT](复习-AgentENV图解增强版.pptx)。', '',
        '> 阅读顺序：先看图并尝试复述，再看机制说明，最后展开自测答案。PPT备注中也有详细解释与来源。材料完善不代表独立掌握；第25—28课仍按学习计划继续。', '',
        '## 证据与适用范围', '',
        '- AgentENV 源码基线为 `9f62cbe07cebfecf416dc9bdcf497e2a97687644`。通用Linux机制与具体项目选择分开理解。',
        '- 地址、页号、请求编号和多数时间线均为课堂假设。第52页的数据来自此前教师本地Windows/Node实验，不是microVM或DSA实测。',
        '- 恢复内存以固定基线文档的私有映射/COW模型说明；尚未重新审计配套Firecracker底层映射，不能把共享page cache或匿名页模式当成部署定论。',
        '- 完整读例采用split virtqueue、传统ublk交接以及选定的io_uring后端READ，不声称所有内核版本和后端都采用相同接法或复制次数。', '',
        '## 按问题定位', '',
        '| 主题 | PPT页码 | 课程详解 |', '|---|---|---|',
    ]
    for title, pages, images, lesson in groups:
        txt.append(f'| {title} | {"、".join(map(str, pages))} | [{lesson[:-3]}]({lesson}) |')
    for idx, (title, pages, images, lesson) in enumerate(groups, 1):
        txt += ['', f'## {idx:02d} {title}', '', f'对应PPT：{"、".join(map(str, pages))}页。深入阅读：[{lesson[:-3]}]({lesson})。', '']
        for n in images:
            image_name = f'{n:02d}.png'
            shutil.copyfile(BUILD / 'render' / image_name, ASSETS / image_name)
            txt += [f'![第{n}页：{slides[n-1]["title"]}](../assets/agentenv-review/{image_name})', '']
        for n in pages:
            s = slides[n - 1]
            txt += [f'### {s["title"]}', '', f'**{s["takeaway"]}**', '', s['note'], '']
        questions = [slides[n-1] for n in pages if slides[n-1].get('q')]
        if questions:
            txt += ['<details>', '<summary>自测与参考答案</summary>', '']
            for s in questions:
                txt += [f'**第{s["page"]}页：{s["q"]}**', '', s['answer'] or '结合本节图与机制说明回答，避免只背结论。', '']
            txt += ['</details>', '']
    txt += ['## 来源与版本核对入口', '',
            '- [固定AgentENV架构文档](https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/docs/src/internals/architecture.md)',
            '- [本地源码索引](源码索引.md)与每课文末的固定提交链接。',
            '- [KVM API](https://docs.kernel.org/virt/kvm/api.html)、[Linux ublk](https://docs.kernel.org/block/ublk.html)、[VirtIO 1.2](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html)。',
            '- [process_vm_readv](https://man7.org/linux/man-pages/man2/process_vm_readv.2.html)、[io_uring](https://man7.org/linux/man-pages/man7/io_uring.7.html)。',
            '- [实验脚本](实验/24_cpu_wall.cjs)与[原始结果](实验/24_cpu_wall_result.json)。', '',
            '下一步：先独立解释EPT变更后的TLB同步及新周期重新布防，再复述Guest完整读路径；之后进入第25课多节点与资源池。', '']
    (COURSE / '复习-AgentENV图解手册.md').write_text('\n'.join(txt), encoding='utf-8')
    print(f'Generated handbook: {len(groups)} sections, {sum(len(g[2]) for g in groups)} diagrams')

if __name__ == '__main__':
    main()
