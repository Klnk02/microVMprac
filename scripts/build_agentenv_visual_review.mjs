// 图解复习版。native shapes/lines are editable technical diagrams requested by the learner.
// Run with the bundled Node runtime. Build previews stay outside the repository.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const runtime=process.env.CODEX_REVIEW_RUNTIME || 'C:/Users/a/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {Presentation,PresentationFile}=await import(pathToFileURL(runtime+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const repo=path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:)/,'$1')),'..');
const work=path.resolve(repo,'../.review-build');
const out=repo+'/04-AgentENV/复习-AgentENV图解增强版.pptx';
await fs.mkdir(work+'/render',{recursive:true});
const P=Presentation.create({slideSize:{width:1280,height:720}});
const C={ink:'#15283B',dim:'#526679',line:'#BCCAD7',blue:'#2367BD',teal:'#087E87',orange:'#B95A1D',purple:'#7550B5',paper:'#F8FAFC',soft:'#EAF1F8',green:'#18724C'};
const font='Microsoft YaHei';
const docs=repo+'/04-AgentENV/';
const urls={arch:'https://github.com/kvcache-ai/AgentENV/blob/9f62cbe07cebfecf416dc9bdcf497e2a97687644/docs/src/internals/architecture.md',kvm:'https://docs.kernel.org/virt/kvm/api.html',virtio:'https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html',ublk:'https://docs.kernel.org/block/ublk.html',pvm:'https://man7.org/linux/man-pages/man2/process_vm_readv.2.html',uring:'https://man7.org/linux/man-pages/man7/io_uring.7.html'};
let meta=[];
const roles=new Map();
function wrapText(value,width,size){
 const cap=(width-12)/size;return String(value).split('\n').map(part=>{let rows=[],cur='',units=0;const tokens=part.match(/[A-Za-z0-9_./()+=<>-]+|\s+|./gu)||[];for(const token of tokens){const u=[...token].reduce((v,c)=>v+(/[\u2e80-\uffff]/.test(c)?1:0.57),0);if(units+u>cap&&cur.trim()&&!/^[，。？！、；：）]$/.test(token)){rows.push(cur.trim());cur='';units=0;}cur+=token;units+=u;}if(cur.trim())rows.push(cur.trim());return rows.join('\n');}).join('\n');
}
const review={
3:['进程与内核','Firecracker 和 daemon 是宿主进程。KVM、ublk 驱动属于宿主内核。envd 和用户程序在 Guest 内。','对象与进程','OverlayBD 是 daemon 调用的库。server 内的管理对象，也不等于另一个进程。'],
4:['职责分开','server 建盘、配网、调用控制接口。普通块 IO 的字节通常交给 VMM、Host 内核和存储 daemon。','快照是另一条路','server 用 PVM 捕获 RAM 时，才会使用自己的本地快照 buffer。'],
5:['两阶段翻译','Guest 页表把 GVA 翻译为 GPA，EPT 把 GPA 翻译为 HPA。CPU 可缓存有效的组合翻译。','宿主视角','Firecracker 通过自己的 HVA 访问同一后备页。HVA 不在 Guest 的硬件访存链上。'],
7:['地址怎样解释','PID 确定目标进程。remote_iov 的地址字段按目标进程解释，local_iov 按调用者解释。','完成范围','返回 n 仅表示本次读到了 n 字节。未保证整段完整、VM 一致或文件持久化。'],
9:['退出如何分流','EPT 等事件可使 CPU 退出 Guest。KVM 先判断原因，能处理的就处理并重入。','线程仍是同一个','VM-Exit、ioctl 返回和宿主线程调度是不同边界。Guest syscall 也不必退出。'],
10:['缓存的上下文','TLB 随执行上下文缓存地址和权限。Guest 仍在同一物理 CPU 上运行，并非把 GPA 发给另一台 Host CPU。','未命中与异常','TLB 未命中可以硬件查表。映射或权限异常，才可能进入退出处理。'],
11:['谁停止谁','API 接请求，VMM 协调，vCPU 线程按协议退出运行并确认。没获调度不等于暂停完成。','一致性边界','vCPU 停止之后，设备后端仍可能写 Guest RAM，快照还要协调这些在途工作。'],
13:['三个存储区','描述符表描述 buffer。avail 发布可处理的链头，used 发布完成链的信息。','安全复用','设备领取还未完成，Guest 不可覆盖。发布 used 后，上层仍要检查状态和消费结果。'],
14:['通知不装数据','请求描述留在 virtqueue，实际字节在 buffer。QueueNotify 提醒后端检查队列。','不等于用户态退出','ioeventfd 可由 KVM 内核匹配并提醒后端，不要求 vCPU 的 KVM_RUN 返回用户态。'],
15:['命令在哪里执行','server 经 envd 客户端与 Guest 服务通信，envd 在 Guest 内创建命令进程。','不同接口','暂停等控制操作走 VMM 接口。创建客户端对象只准备了访问入口，还没验证服务。'],
16:['逐层确认','先有可用的控制接口，再有运行的 VM，最后是 Guest 服务真正响应健康检查。','就绪的范围','健康检查不保证所有文件、凭据、外部依赖与冷页都已准备好。'],
17:['各事件的意义','Start 表示启动，Data 携带输出，End 提供结束结果。输出中的“done”不能代替 End。','超时的含义','连接断开或等候超时，只表示没拿到明确结果。命令可能仍在运行或已有副作用。'],
19:['请求向下','文件系统先查缓存并解析块位置。Guest 驱动发布请求，FC 后端访问 Host 块设备。','结果逐层回来','daemon 取得字节后报告结果。FC 发布 used，Guest 检查状态，最终 pread 返回。'],
20:['SQ 与 CQ','daemon 向 SQ 发操作，内核向 CQ 发结果。user_data 让程序认出是哪一笔操作。','结果要对号','READ 的 res 是字节数或错误。FETCH 的完成只是领取任务，字节仍未必到达。'],
21:['请求槽的作用','qid/tag 标识一笔在途块请求。内核先交描述，daemon 再查层索引、填数据。','合并命令','COMMIT_AND_FETCH 报告旧请求并等下一项。它不表示下一项已完成。'],
24:['索引表达语义','上层无映射时向父层回落。显式零覆盖会屏蔽父层的旧内容。','不能靠省略表示零','“未驻留”“本层没数据”和“当前值为零”不等价，需要按格式明确记录。'],
25:['映射与取数','mmap 先建立虚拟区间。触碰页面后才可能需要准备后备页，缓存能缩短取数。','先辨是哪层','Guest 页表缺页、EPT 异常、Host 缺页分属不同层，并非每次都依次发生。'],
26:['读共享，写私有','多个实例可以读同一不可变底座。A 写入后拥有私有内容，B 继续读原值。','两个独立机制','COW 管修改归属，按需加载管何时准备页面。不能用 COW 解释所有冷恢复延迟。'],
27:['两块盘的用途','RAM 镜像设备给 Host 准备 Guest RAM 后备页。Guest 磁盘设备给 Guest 文件系统提供块内容。','缓存命中的层次','Guest 认为命中文件缓存，不证明 Host 上承载这些字节的页面已经驻留。'],
28:['完整恢复材料','RAM 保存变量和内核结构，VM 状态保存执行上下文。磁盘和配置把设备视图补齐。','版本与外部状态','恢复材料必须配套且兼容。外部挂载卷和数据库是否纳入快照，要看接口契约。'],
29:['先获得稳定视图','停止 vCPU 并协调设备写入，再捕获对应字节，避免跨时刻拼出不一致状态。','持久化另算','格式写完、名字发布、完整快照发布与稳定存储确认不是同一个完成点。'],
32:['先定义基准','必须能还原 S0，再记录相对它的变化。写入发生之前，就要启用跟踪并管理周期。','别留下时间缺口','切换基准、清理旧记录和恢复执行之间，不能漏掉任何需保存的写入。'],
33:['通过权限布防','VMM 设置 memslot 的脏页跟踪标志。KVM 按 GPA 范围修改已有 EPT 写权限。','保留模式边界','旧的可写 TLB 必须同步。PML 等硬件辅助模式不一定逐页用首次写退出跟踪。'],
35:['为什么再次保护','第一次写后，该页可能已恢复 W=1。只清位图，后面的写就可能绕过检测。','清除的是记录','清 dirty 不会把 RAM 内容清零。GET / CLEAR 的具体职责依 KVM 模式而定。'],
36:['先描述，再读取','范围只说明从哪段 FC HVA 读取、多长、对应 RAM 逻辑哪里。PVM 执行后才有字节。','三个位置分开','源 HVA、本地 buffer 偏移与镜像逻辑偏移不同，输出索引还要保留对应关系。'],
37:['批次与实际数据','chunk 汇集多条 entry。读取器逐项把内容填入 buffer，writer 再写到指定位置。','优化需测量','合并 iovec 或相邻范围是候选优化，不保证收益，也不能丢逻辑映射和短读处理。'],
39:['格式为何需要索引','payload 紧凑存放实际内容，索引将逻辑范围定位到层内部位置，trailer 等补全格式。','发布为何仍会失败','finalize 不保证落到稳定存储。单层 rename 也不代替 VM 状态和父引用的整体发布。'],
40:['为何先不运行','先装载 VM 状态和 RAM 后端、补充设备配置，再 resume，避免 Guest 访问未完成的环境。','区分两种 resume','原地恢复继续旧运行时。从快照恢复重建环境，还需等 envd 就绪。'],
41:['按需准备','恢复接口成功后，只需保证后续所需逻辑内容可取得，不必提前触碰全部 RAM。','观察首次访问','预取、Host 缓存和映射状态都影响首访问延迟，不能只看“冷 / 热”两个字。'],
42:['外部时间仍向前','对端连接、数据库、租约不会随 VM 回滚。内存中的“未完成”不代表外部没做完。','业务恢复协议','需要稳定操作 ID、查询、对账与重连，避免重放已经发生的副作用。'],
43:['发送链路','Guest 驱动交包给 VirtIO 后端，经 TAP 进入 Host 网络，再按路由与策略转发。','完成到哪一层','TX buffer 归还只说明本地设备处理结束，不证明远端应用完成。'],
45:['句柄与真实资源','server 持使用权，FC 实际使用设备，daemon / 内核管理设备。三者责任不同。','共享设备寿命','A 释放引用后，B 或预取任务可能仍在使用。使用权归零后是否销毁也看池策略。'],
46:['回收按依赖','先协调停止使用者，再释放设备和内存。异常路径要核对残留并记录清理失败。','RAII 的边界','析构管理对象寿命，异步 IO 的真正终止还需要显式协议，不能只丢句柄。'],
47:['为什么 B 跑不了','A 的同步 pread 尚未返回，唯一工作线程还没回 executor。B 就没有线程来推进。','睡眠与挂起不同','线程睡眠让 CPU 跑其他线程。任务 Pending 才让该工作线程回去运行其他任务。'],
48:['三种寿命','业务等待、运行时任务、底层 IO 可以在不同时间结束。超时先结束的是等待。','谁保管 buffer','IO 管理者继续保管 B 并消费最终结果，确认无访问后再释放或复用。'],
49:['重试保持同一身份','同一逻辑操作复用 op_id，校验参数，并原子认领进行中记录，阻止并发重复执行。','仍有崩溃窗口','副作用完成但记录未落下时仍可能重复，需要事务或外部幂等、查询对账协议。'],
50:['预算覆盖整件事','请求耗时和退避都消耗同一个 deadline。先检查错误是否可重试、操作是否安全。','避免重试叠乘','每层都重试会放大下游负载。总次数、总预算、责任层都要明确。'],
53:['占比限制收益','只缩短关键路径中的一小段，整体最多省掉这一段。并行重叠的阶段不能机械相加。','wall 不是 CPU','等待区间可能含调度、排队与设备服务，不能把时间线直接当 CPU 统计。'],
54:['卸载省的是什么','硬件代做搬运，可减少 CPU 执行复制。CPU 仍承担准备、提交及结果处理。','等待策略有代价','睡眠可省 CPU，但唤醒调度会加延迟。忙轮询消耗 CPU，还可能争用资源。'],
55:['并发有效的条件','重叠等待或使用更多计算资源能提升容量。达到瓶颈以后，加并发可能只增加等待。','比较要固定负载','并发比串行容量高，仍可能低于到达量。容量提升与队列稳定是两个判断。'],
58:['错误往回传播','FETCH 成功只交付描述。后端 READ 失败后，要按协议向原块请求报告错误。','不能伪造成功','发布 used 仍需提供正确设备状态。最终 Guest 返回值按实际读取结果解释。'],
59:['保留修改记录','P0 即使改回旧值，也可能仍被标脏。P1 无新覆盖时，从父层 S0 取得。','检查恢复依赖','新层、索引、VM 状态和父引用都要配套。增量缺少父层就失去完整视图。'],
60:['先有机制理解','解释角色、数据和完成条件，再压缩成短答。换条件后还能推理，才有理解证据。','案例可以是推演','明确标成纸面例子即可。不能冒称未做过的 VM 实测，也不以背出数字替代理解。'],
61:['当前尚待验证','EPT 权限变更后的 TLB 同步、dirty 周期重新布防，以及完整读路径独立复述。','后续课程','第25—28课尚未正式完成。完成本轮课程后，再进入 Go / Kubernetes 开源实践。']
};
function text(s,x,y,w,h,t,size=26,color=C.ink,bold=false,align='left'){
 const z=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 z.text=wrapText(t,w-5,size);z.text.style={typeface:font,fontSize:size,color,bold,alignment:align,verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:0};roles.set(z.id,'text');return z;
}
function box(s,x,y,w,h,t,color=C.blue,fill=C.soft,size=26){const z=s.shapes.add({geometry:'rect',name:t.replace(/\n/g,' '),position:{left:x,top:y,width:w,height:h},fill,line:{fill:color,width:1.4}});z.text=t;z.text.style={typeface:font,fontSize:size,color:C.ink,alignment:'center',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:12};roles.set(z.id,'box');return z;}
function line(s,x,y,w,h=0,color=C.line,width=2){return s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:color,width}});}
function link(s,a,b,from='right',to='left',color=C.blue){return s.shapes.connect(a,b,{kind:(from==='bottom'&&to==='top')||(from==='right'&&to==='left')||(from==='left'&&to==='right')?'straight':'elbow',fromSide:from,toSide:to,line:{fill:color,width:2},tail:{type:'triangle',width:'sm',length:'sm'}});}
function flow(s,labels,y=270,{x=60,w=1160,h=110,gap=44,color=C.blue,size=26,connect=true,reverse=false}={}){let bw=(w-gap*(labels.length-1))/labels.length;let a=labels.map((l,i)=>box(s,x+i*(bw+gap),y,bw,h,l,color,C.soft,size));if(connect)for(let i=1;i<a.length;i++){if(reverse)link(s,a[i],a[i-1],'left','right',color);else link(s,a[i-1],a[i],'right','left',color);}return a;}
function vertical(s,labels,x=70,y=180,w=510,h=72,gap=28,color=C.blue,size=25){let a=labels.map((l,i)=>box(s,x,y+i*(h+gap),w,h,l,color,C.soft,size));for(let i=1;i<a.length;i++)link(s,a[i-1],a[i],'bottom','top',color);return a;}
function table(s,values,x=60,y=200,w=1160,h=310,widths){const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values,...(widths?{columnWidths:widths}:{})});t.borders.assign({fill:C.line,width:1});for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){let q=t.getCell(r,c);q.fill=r===0?C.blue:(r%2?'#FFFFFF':C.paper);q.text.style={typeface:font,fontSize:24,color:r===0?'#FFFFFF':C.ink,bold:r===0,verticalAlignment:'middle',insets:12};}return t;}
function side(s,title,body,x=840,y=190){text(s,x,y,370,48,title,28,C.blue,true);text(s,x,y+66,370,280,body,25);}
function refine(s,n,start){
 const d=review[n];if(!d||s.tables.items.length)return;
 const body=s.shapes.items.slice(start);
 // Diagram stays native and editable; preserve meaningful coordinate labels.
 for(const z of body){
  const role=roles.get(z.id),p=z.position;
  if(z.connector)continue;
  if(role==='text'){
   const keep=n===3 || (n===5&&p.top<220) || (n===27&&p.top<440) || (n===47&&p.top<220) || n===54;
   if(!keep){z.text='';continue;}
  }
  const q={left:60+(p.left-60)*0.66,top:200+(p.top-180)*0.84,width:p.width*0.66,height:p.height*0.84};
  if(role==='box'){
   const value=z.text.toString();const cols=Math.max(5,(q.width-20)/22);
   const lines=value.split('\n').reduce((sum,l)=>sum+Math.max(1,Math.ceil([...l].reduce((a,c)=>a+(/[\u3000-\u9fff]/.test(c)?1:0.54),0)/cols)),0);
   const wrapped=wrapText(value,q.width-24,22);q.height=Math.max(q.height,wrapped.split('\n').length*27+20);
   z.text=wrapped;z.text.style={typeface:font,fontSize:22,color:C.ink,alignment:'center',verticalAlignment:'middle',wrap:'none',autoFit:'none',insets:10};
  }else if(role==='text'){
   z.text.fontSize=22;q.height=Math.max(q.height,n===3||n===27?54:32);if(n===5)q.top-=36;if(n===27)q.top-=15;
  }
  z.position=q;
 }
 line(s,855,190,0,365,C.line,1);
 text(s,890,190,330,38,d[0],27,C.blue,true);
 text(s,890,239,330,145,d[1],23);
 text(s,890,400,330,38,d[2],27,C.orange,true);
 text(s,890,449,330,120,d[3],23);
}
function add(title,topic,takeaway,draw,{note='',q='',answer='',source=[],color=C.blue}={}){
 const s=P.slides.add();s.background.fill=C.paper;
 text(s,60,30,1060,26,topic,18,color,true);text(s,60,76,1160,66,title,42,C.ink,true);
 line(s,60,155,1160);const start=s.shapes.items.length;draw(s);refine(s,meta.length+1,start);
 line(s,60,580,1160);text(s,60,598,1160,52,takeaway,26,color,true);
 text(s,60,666,1110,24,q?'自测：'+q:'示意图 / 课堂假设，非真实运行 trace',18,C.dim);
 text(s,1170,665,50,25,String(meta.length+1).padStart(2,'0'),18,C.dim,false,'right');
 s.speakerNotes.text=['机制解释：'+note,'自测答案：'+answer,'证据边界：所有示意地址、页号、时间线均为教学例子。仅第52页展示此前本地 Node 实测，非VM实测。配套Firecracker实际内存映射实现尚未重新审计。','来源：',...source].join('\n');
 meta.push({page:meta.length+1,title,topic,takeaway,note,q,answer,source});return s;
}
const src=(file,...extra)=>[docs+file,...extra];

add('AgentENV 图解复习','第1—24课 + 冷热页与脏页跟踪','先解释数据在哪里，再解释谁在执行、何时算完成。',s=>{
 text(s,70,200,1100,100,'把一次读取、一次暂停、一次恢复\n讲到具体的地址、队列和缓冲区',38,C.ink,true);
 flow(s,['Guest\n程序与内核','Firecracker\nVMM 与设备','Host 内核\nKVM / ublk','存储 daemon\nOverlayBD'],390,{h:112,size:26});
},{note:'本版替代原20讲的复习入口，原文件保留。增加第21—24课和dirty专题，正文保留机制关键步骤，详细解释和答案放备注。本版材料制作不代表用户独立掌握。',source:src('学习记录.md',urls.arch)});
add('复习路线与页码','导航','每轮选一条链，遮住结论复述，再用变式检查。',s=>{
 const rows=[['位置、地址与执行','03—11','谁运行？地址属于谁？'],['VirtIO、控制与文件读取','12—24','任务、数据、通知分别在哪？'],['内存、快照与恢复','25—42','映射、复制、保存、运行各何时完成？'],['网络、隔离与可靠性','43—50','谁拥有资源？失败后怎样安全处理？'],['性能与综合复习','51—61','测什么？能证明什么？'],['微观补充图解','62—68','设备准备、请求时序、追踪与异步细节']];
 table(s,[['主题','页码','复习时先问'],...rows],60,190,1160,350,[340,150,670]);
},{note:'正文图形与表格可在PowerPoint中编辑。每页备注有机制解释、自测参考答案和来源。第25—28课仍未正式展开，不冒称全部课程完成。',source:src('00-学习计划.md')});
add('同一台宿主机上的角色位置','01 系统地图','server 管理生命周期；普通块 IO 通常由 VMM、内核与 daemon 处理。',s=>{
 text(s,60,181,170,40,'Host 用户态',25,C.blue,true);flow(s,['AgentENV\nserver','Firecracker\n进程','ublk-daemon\n内含 OverlayBD'],180,{x:250,w:970,h:95,gap:40,connect:false});
 text(s,60,324,170,40,'Host 内核',25,C.purple,true);flow(s,['KVM：vCPU 执行','ublk：块请求交接'],320,{x:250,w:970,h:75,color:C.purple,connect:false});
 text(s,60,451,170,40,'Guest 内部',25,C.green,true);flow(s,['用户程序','Guest 内核','envd 服务'],445,{x:250,w:970,h:90,color:C.green,connect:false});
},{note:'Firecracker和存储daemon都是宿主进程。KVM与ublk驱动属于宿主内核。envd在Guest内。OverlayBD是daemon调用的库，不必是独立进程。Guest进程由Guest内核管理，宿主ps不直接列出Guest进程。图中同一行仅表示位置，不表示强制串行调用。',q:'Guest 里的 python，是宿主 Firecracker 的普通子进程吗？',answer:'不是。它由Guest内核管理；宿主主要看到VMM的进程与vCPU等线程。',source:src('01-系统地图与第一课.md',urls.arch)});
add('三条路径分别承载什么','01 系统地图','控制请求、Guest 磁盘 IO、Host 内存捕获是三条不同路径。',s=>{
 text(s,60,180,170,36,'控制',25,C.blue,true);flow(s,['server','Firecracker API','暂停 / 恢复'],180,{x:250,w:970,h:80});
 text(s,60,310,170,36,'磁盘读取',25,C.teal,true);flow(s,['Guest VirtIO','FC / Host ublk','daemon / 层数据'],305,{x:250,w:970,h:80,color:C.teal});
 text(s,60,440,170,36,'内存捕获',25,C.orange,true);flow(s,['Firecracker RAM','server 的 buffer','快照层 writer'],430,{x:250,w:970,h:80,color:C.orange});
},{note:'server会准备设备、保存句柄和控制生命周期，不应因此被画成每一次普通Guest磁盘读取的payload中转者。内存快照跨进程读取由server执行，使用自己的本地buffer。恢复内存后端的Host块读取又不同于Guest磁盘VirtIO路径。',q:'保存 Guest RAM 一定要先让 Guest 发布 VirtIO 描述符吗？',answer:'不一定。本课PVM捕获在宿主执行，不依赖Guest VirtIO。',source:src('06-VirtIO描述符队列与通知.md')});
add('同一物理页的两种访问视角','02—03 地址空间','Guest 硬件访存不经过 HVA；HVA 属于宿主进程的视角。',s=>{
 flow(s,['GVA\nGuest 虚拟地址','GPA\nGuest 物理地址','HPA\nHost 物理页'],220,{w:1160});
 text(s,345,186,220,30,'Guest 页表',22,C.dim,false,'center');text(s,790,186,200,30,'EPT / NPT',22,C.dim,false,'center');
 const h=box(s,400,425,340,95,'Firecracker HVA\n宿主虚拟地址',C.purple);const p=box(s,890,425,330,95,'同一 Host 物理页',C.purple);link(s,h,p,'right','left',C.purple);text(s,70,435,270,70,'Firecracker\n自己的访问路径',24,C.purple,true);
},{note:'GPA是Guest看见的物理地址，不是宿主DRAM位置。硬件第二阶段页表将GPA映射到HPA。Firecracker通过自己的宿主页表用HVA访问Guest RAM后备页。两种视角可访问同一物理页，不表示又复制了一份数据。',q:'把 GPA 直接当作 server 的指针传给 pwrite，可行吗？',answer:'不可行。普通指针按调用者地址空间解释，GPA不是server HVA。',source:src('03-Guest内存与宿主映射.md',urls.kvm)});
add('memslot 登记的是一段对应关系','03 Guest 内存与宿主映射','KVM 用 GPA 范围与 Firecracker HVA 找后备页，不要求 VMM 填 HPA。',s=>{
 table(s,[['slot = 2（假设）','填写内容'],['Guest 物理起点','0x400000'],['Firecracker 用户态起点','0x70000000'],['长度','16 KiB，覆盖4个4 KiB页']],60,190,700,290,[340,360]);
 side(s,'登记之后','GPA 0x402120\n对应 HVA 0x70002120\n\nHPA 由宿主内存管理与\nKVM 按需解析、建映射。');
},{note:'偏移0x2120加到HVA基址得到0x70002120。KVM_SET_USER_MEMORY_REGION记录memslot。登记不等于提前触碰每一页、复制全部RAM或固定全部物理页。公式只适用于该连续区域且地址合法。',q:'登记完 memslot，能否断言所有 EPT 叶项都已建立？',answer:'不能。后备页和映射可以按需准备。',source:src('03-Guest内存与宿主映射.md',urls.kvm)});
add('process_vm_readv 的两个地址空间','02 / 16 跨进程读取','PID 选择远程进程；remote_iov 给远程 HVA，local_iov 给本地 HVA。',s=>{
 const a=box(s,70,240,340,140,'Firecracker\nGuest RAM 映射\nremote：FC HVA',C.purple);
 const b=box(s,500,240,260,140,'Host 内核\n跨进程读取',C.blue);
 const c=box(s,850,240,350,140,'AgentENV server\n本地 buffer\nlocal：server HVA',C.teal);link(s,a,b);link(s,b,c);
 text(s,80,430,1120,65,'两个 iovec 数组本身都在调用者内存里。\nremote_iov 中的地址字段，才按 Firecracker 的地址空间解释。',26);
},{note:'Linux接口还包含local_iov元素数、remote_iov元素数和flags，不能把简化示意当成完整函数声明。成功返回的是实际复制字节数，可能短读；不是快照持久化保证。不能以“内核会翻译地址”推导普通write能解释其他进程指针。',q:'remote_iov 应该填 GVA、GPA，还是 Firecracker HVA？',answer:'Firecracker HVA。PID与该地址共同定位远程进程内存。',source:src('16-pause跨进程读取.md',urls.pvm)});
add('短读后，源和目的都要前进','16 跨进程读取','成功复制部分字节，不代表整段读取完成，也不代表快照一致。',s=>{
 flow(s,['请求 8 KiB','返回 4 KiB','剩余 4 KiB'],220,{h:105});
 table(s,[['下一次调用','更新后的值'],['远程源地址','原 remote HVA + 4096'],['本地目的地址','原 buffer HVA + 4096'],['剩余长度','8192 − 4096 = 4096']],140,370,1000,185,[440,560]);
},{note:'实际循环需校验返回值、地址/长度溢出、零进展以及错误。内存可在多次读取之间变化，PVM不提供整个VM的一致性快照。async函数调用同步PVM不会自动把操作变成非阻塞；执行线程直到调用返回才回到运行时。',q:'第一次短读后，能否只移动源地址、不移动目的地址？',answer:'不能，否则后续字节会覆盖此前已读取的数据。',source:src('16-pause跨进程读取.md',urls.pvm)});
add('KVM_RUN 包住了哪些执行','04 Guest 指令执行','VM-Exit 先进入 KVM；只有需要用户态处理等情况，ioctl 才返回。',s=>{
 const a=box(s,60,210,310,95,'Firecracker vCPU 线程\nioctl(KVM_RUN)',C.blue);
 const b=box(s,480,210,310,95,'KVM 进入 Guest\n物理 CPU 执行指令',C.green);link(s,a,b);
 const c=box(s,480,415,310,95,'VM-Exit\n先由 KVM 判断原因',C.purple);link(s,b,c,'bottom','top');
 const d=box(s,900,210,310,95,'内核可处理\n处理后重入 Guest',C.green);link(s,c,d,'right','bottom');link(s,d,b,'left','right',C.green);
 const e=box(s,900,415,310,95,'需用户态等处理\nKVM_RUN 返回',C.orange);link(s,c,e);
},{note:'KVM_RUN是vcpu fd上的ioctl，调用者仍是宿主线程。进入Guest和返回Host不自动等于宿主调度切换。普通Guest syscall由Guest内核处理，不必退出；EPT权限/映射问题可能退出。ioeventfd可让KVM在内核处理通知并唤醒设备后端。',q:'每次 VM-Exit 都必须让 Firecracker vCPU 线程回用户态吗？',answer:'不必须，KVM能处理时可直接重入。',source:src('04-Guest指令执行.md',urls.kvm)});
add('TLB 缓存的是当前上下文的翻译','03—04 地址翻译','TLB 未命中只要求重新查表；有效映射齐全时，不必 VM-Exit。',s=>{
 const a=box(s,60,210,290,90,'Guest 使用 GVA',C.blue);const b=box(s,470,210,310,90,'TLB 有有效缓存',C.green);const c=box(s,910,210,310,90,'快速访问 HPA',C.green);link(s,a,b);link(s,b,c);
 const d=box(s,470,420,310,90,'TLB 未命中\n硬件完成两阶段查表',C.purple);link(s,a,d,'bottom','left');const e=box(s,910,420,310,90,'若 EPT 映射 / 权限异常\n可能 VM-Exit',C.orange);link(s,d,e);
},{note:'在Guest执行上下文中，CPU可以缓存组合翻译及权限。不能把CPU想成先完成Guest地址翻译再把GPA“发到另一台Host CPU”。Guest与Host共享物理处理器的执行资源，虚拟化模式与标识用于区分上下文。页表更新还需按协议同步缓存。',q:'Guest 页表允许写，是否足以保证最终可以写入？',answer:'不足以，第二阶段权限等仍可能限制写入。',source:src('03-Guest内存与宿主映射.md')});
add('暂停由多个执行角色共同完成','05 Firecracker 线程与暂停','暂停请求已送达、所有 vCPU 已停、快照已保存，是不同完成点。',s=>{
 flow(s,['API 线程\n接到暂停请求','VMM 协调\n发出停止执行要求','vCPU 线程\n退出运行并确认'],230,{h:125});
 text(s,85,440,1100,70,'同一进程的线程共享地址空间，但执行职责不同。\n停止 vCPU 之后，仍需协调在途设备 IO 与宿主侧写入。',27);
},{note:'本页表达职责，不宣称每一版本使用相同信号和屏障实现。vCPU线程失去CPU调度不等于已按快照协议暂停。VMM设备处理代码可在宿主执行并访问Guest RAM，不要求Guest vCPU先执行。',q:'vCPU 已暂停，能否据此断言 RAM 快照写盘成功？',answer:'不能。捕获与写出是后续独立步骤。',source:src('05-Firecracker线程与暂停.md')});
add('描述符描述 buffer，自己不搬数据','06 VirtIO 描述符','addr 指向缓冲区，len 描述容量，flags 和 next 描述方向与链。',s=>{
 table(s,[['编号','addr（GPA）','len','flags / next'],['3','请求头地址','请求头长度','NEXT，next=4'],['4','数据 buffer G','4096','WRITE + NEXT，next=5'],['5','状态字节地址','1','WRITE']],60,220,1160,260,[100,430,160,470]);
 text(s,65,500,1150,46,'WRITE 按设备视角：设备可以向该 buffer 写入。编号是表下标。',26,C.purple,true);
},{note:'这是未启用额外地址转换扩展的split virtio-blk读请求教学例。请求头含块操作和扇区位置，addr指内存，两者不能混。设备后端需检查并将GPA范围对应到Guest RAM宿主映射，不能把GPA直接当宿主指针。',q:'描述符 addr 是要读取的磁盘偏移吗？',answer:'不是，是Guest缓冲区地址；磁盘位置在请求头等协议字段中。',source:src('06-VirtIO描述符队列与通知.md',urls.virtio)});
add('可用环与已用环的交接','06 VirtIO split queue','领取只推进消费进度；设备完成后，Guest 处理结果再决定复用。',s=>{
 const a=box(s,60,210,310,125,'Guest 发布 avail\n[3] [7] [9]\navail.idx = 3',C.blue);
 const b=box(s,480,210,310,125,'设备领取链头 3\n读取描述符\n执行请求',C.purple);
 const c=box(s,900,210,310,125,'设备发布 used\n{id:3, len:…}\n推进 used.idx',C.teal);link(s,a,b);link(s,b,c);
 const d=box(s,480,440,310,90,'Guest 检查结果\n处理后才可复用',C.green);link(s,c,d,'bottom','right');
 text(s,60,435,325,100,'描述符表、avail、used\n占不同字节区域。\n实际字节另在 buffer 中。',24);
},{note:'队列取走条目通常不需要将槽清空，靠索引与各方消费位置区分新旧。两个环可在同一大分配中分区，并不意味着同一个环。used只提供完成记录，块设备状态还需检查。发布与读取要遵守内存顺序，本图不是并发实现。',q:'设备取走链头3时，Guest 能立即覆盖其 buffer 吗？',answer:'不能，设备仍可能在使用。',source:src('06-VirtIO描述符队列与通知.md',urls.virtio)});
add('QueueNotify 负责提醒检查队列','06 VirtIO 通知','任务在队列，字节在 buffer，通知只提醒对方有进展。',s=>{
 flow(s,['Guest 写描述符\n发布 avail','需要通知时\n写 MMIO QueueNotify','KVM / ioeventfd\n提醒设备后端','Firecracker\n检查 virtqueue'],230,{h:125,gap:35,size:24});
 text(s,100,440,1080,70,'一次通知可以对应多项工作。\n匹配的 ioeventfd 路径，不必让该次 KVM_RUN 返回用户态。',27);
},{note:'QueueNotify是virtio-mmio传输中的通知寄存器。Guest对相应MMIO位置写入时可触发退出，由KVM分流；ioeventfd将匹配写转换为事件通知。设备后端事件线程处理，不表示vCPU线程一定回到了用户态。设备完成后也按需用虚拟中断提醒Guest。',q:'收到一次 eventfd 通知，就等于只处理一个块请求吗？',answer:'不等于，后端必须检查队列，可能有多项。',source:src('06-VirtIO描述符队列与通知.md',urls.kvm)});
add('控制面如何到达 Guest 命令服务','07 请求控制路径','API 模块和对象不等于独立进程，socket 连接也不等于业务完成。',s=>{
 flow(s,['客户端','节点 server\nAPI / orchestrator','宿主 envd 客户端','Guest envd'],245,{h:125,size:25});
 text(s,80,440,1120,76,'创建、暂停、恢复会调用 VMM 控制接口。\n执行命令则与 Guest envd 通信，命令进程在 Guest 内启动。',27);
},{note:'同一server进程内可有多个模块和对象。控制链路存在超时和重试，必须区分请求发出、被接收、动作完成和结果返回。普通文件块读取不需要让每个数据块都穿过orchestrator。',q:'构造 EnvdInstance 客户端对象，能证明 Guest envd 可用吗？',answer:'不能，需要实际通信与就绪检查。',source:src('07-请求控制路径.md')});
add('就绪检查有不同层次','08 启动与就绪','API socket 可用、Guest 服务响应、你的工作负载成功需要分别验证。',s=>{
 vertical(s,['Firecracker 控制 socket 可用','VM 已配置并执行','Guest envd 健康检查成功'],70,195,670,82,34);
 side(s,'还不能推出','文件一定存在\n凭据一定正确\n网络对端一定可达\n首条业务命令一定成功');
},{note:'start_nowait与wait_for_ready的边界要按具体调用链解释。健康检查是特定协议请求的结果，不自动等价于所有鉴权、业务依赖和冷页均准备好。超时不证明Firecracker退出，需要另行核实与清理。',q:'健康检查超时，能否直接认为 Firecracker 已退出？',answer:'不能。',source:src('08-启动与就绪.md')});
add('命令结果是一段事件流','09 命令执行与事件流','Start、输出、End、exit code 分别表达不同进展。',s=>{
 flow(s,['Start\n命令已启动','Data\nstdout / stderr','End\n进程结束信息'],250,{h:125});
 text(s,90,440,1100,75,'退出码 0：命令按其契约成功。\n连接超时或输出流中断：结果可能未知，不能直接重跑有副作用的命令。',27);
},{note:'Guest PID与宿主PID不可混用。收到一段输出不意味着命令结束。请求终止失败也不能推导进程已经结束。即使exit code非零也可能已经产生部分外部副作用。',q:'输出已包含“done”，但没有 End，能断言进程结束吗？',answer:'不能，文本输出不能代替明确的结束结果。',source:src('09-命令执行与事件流.md')});
add('rootfs、文件名与块地址','10 文件、文件系统与块设备','rootfs 是 Guest 挂载为 / 的文件系统，文件偏移与磁盘偏移不同。',s=>{
 flow(s,['/workspace/a\n文件偏移 8 MiB','Guest 文件系统\n解析文件与缓存','/dev/vda\n块偏移 40 MiB','Host 后端\n/dev/ublkbN'],245,{h:130,size:24,gap:35});
 text(s,80,440,1120,65,'文件路径由 Guest 文件系统解释。\n到达块层后，主要描述操作、块位置、长度与 buffer。',27);
},{note:'偏移8MiB/40MiB均为教学假设。rootfs不等于RAM，也不等于某个特定镜像文件格式。缓冲写返回、Guest文件系统写回、Host层写出、介质持久化属于不同完成点。',q:'读文件 offset=0，是否意味着读虚拟磁盘 offset=0？',answer:'不意味着，文件系统会解析到实际块位置。',source:src('10-文件文件系统与块设备.md')});
add('一次 Guest 文件读取的全景','10—12 4 KiB 读取','先假设 Guest 数据缓存未命中、元数据已准备，沿选定后端看完整路径。',s=>{
 const a=flow(s,['Guest 程序\npread','Guest FS\nVirtIO 驱动','Firecracker\n虚拟设备'],195,{h:95});
 const b=flow(s,['层数据 / 缓存','daemon\nOverlayBD','Host ublk\n块设备'],400,{h:95,reverse:true});
 link(s,a[2],b[2],'bottom','top');text(s,400,327,500,40,'请求沿箭头下行，结果逐层回传',23,C.blue,true);
},{note:'上行从左向右，下行从右向左表达请求依赖。server负责前期设备配置，通常不在普通磁盘payload中转路径。缓存命中可能跳过后端段；实际复制方式依实现，不能从流程框数复制次数。',q:'如果 Guest 文件缓存命中，这条路径从哪里开始缩短？',answer:'Guest直接取RAM中的缓存内容，可能不产生该次VirtIO-blk数据读取。',source:src('12-ublk与存储daemon.md',urls.ublk)});
add('io_uring 的 SQ、CQ 与 buffer','12 Host 内核与用户态交接','CQE 的结果必须对照对应 SQE 的操作解释。',s=>{
 const a=box(s,60,220,315,130,'daemon 用户态\n向 SQ 发布操作\nuser_data 关联身份',C.teal);
 const b=box(s,485,220,310,130,'Host 内核\n处理对应操作\n向 CQ 发布结果',C.purple);link(s,a,b);
 const c=box(s,905,220,305,130,'daemon 消费 CQE\n检查 res / 身份\n推进后续工作',C.teal);link(s,b,c);
 box(s,370,440,540,83,'实际数据字节在 buffer\nSQ / CQ 主要存操作与结果描述',C.blue);
},{note:'用户态发布SQ，内核发布CQ；共享环不等于零拷贝或无需系统调用。普通READ CQE的res可为字节数或负错误码，短读需要处理。FETCH是一类请求交接命令，CQE仅说明领取任务完成。',q:'所有 CQE 到来，都意味着目标文件数据已读完吗？',answer:'不是，取决于完成的是FETCH、READ、取消还是其他操作。',source:src('12-ublk与存储daemon.md',urls.uring)});
add('FETCH 完成的是领取任务','12 ublk 请求槽','先接任务，再取得数据，最后报告原块请求完成。',s=>{
 flow(s,['FETCH\n等内核交任务','FETCH CQE\n得到 qid / tag','OverlayBD / READ\n找到并取得字节','COMMIT + FETCH\n报告旧任务并等下一项'],245,{h:135,size:23,gap:32});
 text(s,80,455,1120,65,'后端 READ 使用 io_uring 是本页选定示例。\n合并提交完成与再次领取，不代表下一项任务已经完成。',25);
},{note:'传统ublk交接模型。daemon为槽位预挂FETCH，内核将操作/位置/长度写入描述区并交任务。READ的完成需另查结果。COMMIT_AND_FETCH可同时提交旧结果并挂接新领取，后续CQE常要等新任务到达。内核版本/模式会改变具体命令。',q:'FETCH CQE 到达后，buffer 里必然已有那4 KiB文件内容吗？',answer:'不必然；只是领取完成，后端处理尚需进行。',source:src('12-ublk与存储daemon.md',urls.ublk)});
add('同一笔 IO 的身份与四块 buffer','12 微观读路径','请求编号负责关联，buffer 负责字节，各层编号不能互换。',s=>{
 table(s,[['层 / 身份','数据位置与拥有者'],['VirtIO 链头 3','G：Guest 文件缓存页'],['ublk qid=0 / tag=7','B：存储 daemon 的 IO buffer'],['io_uring user_data','关联 FETCH / READ 等各自操作'],['Guest pread 返回 4096','U：Guest 程序的用户 buffer 已有字节']],60,190,1160,310,[440,720]);
 text(s,70,516,1140,42,'H：本例可有 Firecracker 中转 buffer，具体实现也可能直接使用 Guest RAM。',23,C.purple);
},{note:'编号3、qid0/tag7是课堂假设。实际路径可从B经块请求页面及FC中转到G，再由Guest复制给U；不得将示例视为每种模式的固定复制次数。设备状态完成后Guest上层仍需处理。',q:'普通磁盘 IO 的 B，和 server 捕获快照的 buffer 是同一个对象吗？',answer:'不是，它们属于不同进程/路径和寿命。',source:src('12-ublk与存储daemon.md')});
add('OverlayBD 用索引组成逻辑磁盘','11 层与索引','读请求按逻辑范围找覆盖记录，较新层优先，缺记录时向父层回落。',s=>{
 table(s,[['层 / 块号','0','1','2','3'],['新层 S2','—','—','C2','—'],['父层 S1','—','B1','—','—'],['底层 S0','A','B','C','D'],['最终视图','A','B1','C2','D']],60,205,1160,295,[360,200,200,200,200]);
 text(s,80,520,1120,35,'— 表示没有覆盖记录，并非逻辑零。',26,C.orange,true);
},{note:'OverlayBD由索引把完整逻辑磁盘范围映射到具体层文件位置。不能将多个层文件直接拼接。一个读取范围可能跨多层/映射段，缓存和压缩后端会改变实际IO。S2视图依赖父层，不能随意删除S1/S0。',q:'读取最终块1，应从 S2、S1 还是 S0 提供？',answer:'S1，因为其B1覆盖底层B，S2没有该范围记录。',source:src('11-OverlayBD层与索引.md',urls.arch)});
add('空洞回落与显式零覆盖','11 OverlayBD 边界','新状态为零时，需要表达零覆盖，不能用“本层没数据”代替。',s=>{
 text(s,100,190,460,45,'本层没有记录',30,C.blue,true);text(s,750,190,460,45,'本层有零覆盖',30,C.orange,true);
 vertical(s,['新层：—','父层：旧值 99','读取结果：99'],90,265,440,67,23,C.blue);
 vertical(s,['新层：显式零','本层命中，屏蔽父层99','读取结果：0'],750,265,440,67,23,C.orange);
},{note:'是否有映射、是否显式零、是否驻留是不同属性。空洞在分层视图中可能意味着父层回落，而不是读取零。逻辑位置与压缩层内部位置也不能相互替代。',q:'父层有旧值，当前应为0，直接省略这一段会怎样？',answer:'可能读回父层旧值，形成错误快照/磁盘视图。',source:src('11-OverlayBD层与索引.md')});
add('mmap 建立映射，缺页准备页面','13 mmap 与缺页','映射存在，不保证所有页面已驻留，更不保证已读取全部介质数据。',s=>{
 flow(s,['mmap 建立\n虚拟地址区间','首次触碰某页\n需要后备字节','缓存已有：复用\n缓存没有：取数','页准备好\n继续访问'],245,{h:130,size:24,gap:32});
 text(s,80,452,1120,75,'Guest 页表缺页、EPT 映射异常、Host 后备映射缺页分属不同层。\n慢路径可能嵌套，但不能把所有访问都画成每层必然各缺一次页。',25);
},{note:'mmap不是将文件内容一次性复制进内存。缺页的具体处理依映射类型和已有缓存状态。匿名页、文件私有映射和只读块设备模型不能混为一谈。共享/驻留结论必须以具体Firecracker实现及版本核验。',q:'mmap 了2 GiB，是否可以断言已读入2 GiB？',answer:'不能，映射大小不同于实际驻留量和读取量。',source:src('13-mmap缺页与COW.md')});
add('COW 将私有修改与底座分开','13 写时复制','按需加载决定何时取页，COW 决定写入后谁拥有新内容。',s=>{
 const base=box(s,485,200,310,90,'不可变底座页 P\n值 = 10',C.purple);const a=box(s,80,410,330,110,'实例 A 私有页 P_A\n写后值 = 20',C.orange);const b=box(s,875,410,330,110,'实例 B 仍读底座\n值 = 10',C.green);link(s,base,a,'left','top',C.orange);link(s,base,b,'right','top',C.green);text(s,450,390,360,85,'A 写入时获得私有内容\n底座仍保持 10',26,C.purple,true,'center');
},{note:'这是共享页发生私有化的常见COW语义图，非断言每次写都整页复制。已经私有可写的页后续写入通常不用每次复制。AgentENV固定基线架构文档描述只读内存设备私有映射/COW，配套FC底层实现尚待独立审计。',q:'A 改成20，B和原快照应该分别读到多少？',answer:'未修改的B与原快照仍为10。',source:src('13-mmap缺页与COW.md',urls.arch)});
add('恢复 RAM 缺页与 Guest 磁盘读','13 / 18 两条存储依赖','访问未准备的 RAM 页可触发 Host 存储 IO，不要求 Guest 走 VirtIO。',s=>{
 text(s,60,190,1150,37,'Guest 文件缓存命中，但承载字节的 Host 页尚未准备',27,C.blue,true);flow(s,['访问 Guest RAM','Host RAM 镜像后端','准备页并继续'],250,{h:85});
 text(s,60,390,1150,37,'Guest 文件缓存未命中，需要读取虚拟磁盘',27,C.orange,true);flow(s,['Guest VirtIO-blk','Host 磁盘后端','文件缓存得到字节'],445,{h:85,color:C.orange});
},{note:'RAM镜像ublk与Guest磁盘ublk用途不同。“Guest缓存命中”只是Guest层视图，不证明承载这些内容的Host页已驻留。Host后端再命中缓存时也可能没有物理介质读。按固定基线文档解释，不绑定未经核验的部署内核映射分支。',q:'Guest 缓存命中而 Host 有块读，两者矛盾吗？',answer:'不矛盾，可能是为恢复RAM准备后备页，非Guest磁盘数据读取。',source:src('18-从快照恢复.md')});
add('完整快照需要配套的恢复材料','14 快照状态与一致性','寄存器、RAM、磁盘视图与恢复配置共同决定能否继续执行。',s=>{
 const m=box(s,475,300,330,100,'可恢复的快照',C.blue);const a=box(s,60,205,300,90,'VM 状态\n寄存器 / 设备状态',C.purple);const b=box(s,910,205,310,90,'RAM 逻辑镜像\n新层 + 父层',C.green);const c=box(s,60,450,300,90,'磁盘视图\nrootfs / 挂载卷',C.teal);const d=box(s,910,450,310,90,'恢复配置与引用\n设备关联 / 兼容信息',C.orange);link(s,a,m);link(s,b,m,'left','right');link(s,c,m,'right','bottom');link(s,d,m,'left','bottom');
},{note:'这是恢复所需材料的概念分组，不是宣称项目manifest恰好有四个文件。仅保存RAM无法提供CPU执行位置和设备上下文。外部挂载卷/数据库是否纳入快照需按契约明确，不因VM暂停就自动一致。',q:'有完整 RAM 文件但 VM 状态保存失败，能保证恢复执行吗？',answer:'不能，寄存器及设备上下文缺失。',source:src('14-快照状态与一致性.md')});
add('暂停、捕获、封存与持久化','14 快照完成边界','每个完成点只证明本阶段，不能提前报告完整快照成功。',s=>{
 flow(s,['确认 vCPU 暂停','捕获 RAM / VM 状态','生成层与索引','发布配套快照'],245,{h:135,size:24,gap:32});
 text(s,80,450,1120,80,'一致性还要协调设备侧在途写入。\nwrite / finalize / rename 各有语义，断电持久化需要相应同步与发布协议。',26);
},{note:'写保护dirty tracking仅提供写历史，不冻结字节。暂停vCPU只覆盖其执行写入，VMM设备后端仍可能写Guest RAM，必须由整体协议协调。文件格式完成、名字发布与稳定存储确认不同。',q:'pause 成功但 RAM 写出失败，能否报告快照成功？',answer:'不能，需要记录快照失败及原运行时状态。',source:src('14-快照状态与一致性.md')});
add('快照失败后核实三个状态','14 / 23 故障边界','请求失败、运行时状态、清理结果要分别记录。',s=>{
 table(s,[['已确认事实','仍需检查'],['vCPU 暂停已确认','原运行时是否仍健全，可否原地继续'],['VM 状态文件写出','RAM层、磁盘层、父引用是否配套'],['RAM层写出失败','临时文件与新分配资源是否回收'],['向客户端返回失败','不能自动将真实状态写成 Running 或 Paused']],60,205,1160,310,[470,690]);
},{note:'失败处理需要依据事实决定继续、清理或对账。新恢复实例load失败，不一定破坏旧快照；不能因新实例失败把共享父层一并删掉。清理失败需单列，不可用原请求错误掩盖资源残留。',q:'恢复请求超时，是否足以断言 VM 根本没恢复？',answer:'不足以，可能动作完成而响应迟到，需要查询真实状态。',source:src('23-失败与恢复.md')});
add('冷热、驻留和脏是三个维度','15a 冷热页与脏页跟踪','热度看观察窗口，驻留看当前页面，脏看相对基线的写历史。',s=>{
 table(s,[['页的行为','热度示例','脏页状态'],['反复读取、没有写','读热','可以干净'],['早先写过、最近不访问','最近冷','仍可能脏'],['10改20再改回10','不由结果值决定','仍可能脏'],['没有驻留','不等于冷','不等于零，也不等于干净']],60,205,1160,310,[530,280,350]);
},{note:'热/冷依时间窗口和采样粒度。Guest文件脏页、RAM快照dirty、Host文件缓存脏页和OverlayBD upper不是同一标记。Accessed位只有访问线索，不直接给精确频率。DAMON/idle tracking在虚拟化场景要验证跟踪后端覆盖，不能简单用FC普通进程访问观测覆盖所有Guest访存。',q:'读热且干净、冷且脏，能否同时存在？',answer:'可以，两个维度独立。',source:src('15a-冷热页与脏页跟踪.md')});
add('跟踪必须早于要捕获的写入','15a 跟踪周期','事后打开 dirty logging，通常找不回此前没有记录的写历史。',s=>{
 flow(s,['S0 基准\n内容可恢复','开启 / 划定\n跟踪周期','Guest 运行\n记录期间写入','暂停并收集\n保存增量 S1'],245,{h:130,size:24,gap:32});
 text(s,80,455,1120,60,'VMM 可在启动时或迁移等流程开始时启用。\n持续开启的实现仍需正确管理每一轮的收集、清理与重新布防。',25);
},{note:'本页是语义时间线，不能把“创建基准后”死板理解成中间可以遗漏写入。基准稳定、跟踪开始/重置与运行继续之间必须按协议避免缺口。AgentENV配套FC实际enable/reset时序尚未重新审计。',q:'到 pause 时才开始记录，能用它补齐相对旧 S0 的全部变化吗？',answer:'通常不能，没有记录此前的写入历史。',source:src('15a-冷热页与脏页跟踪.md',urls.kvm)});
add('EPT 写保护怎样发现第一次写','15a 写保护跟踪模型','先布置检测条件，发生写入时再根据 GPA 定位页面。',s=>{
 flow(s,['VMM 开启\nmemslot dirty log','KVM 收紧 EPT\nW=1 改为 W=0\n同步旧 TLB','Guest 首次写\nEPT violation','KVM 记录页号\n恢复写入条件\n重试继续'],235,{h:150,size:24,gap:32});
 text(s,80,460,1120,60,'Guest 页表仍可允许写。该次退出可在 KVM 内核处理。\nPML 等硬件辅助模式不要求每一页首次写都采用这条退出路径。',25);
},{note:'以Linux v6.14 x86无硬件dirty辅助的写保护路径解释。VMM设置KVM_MEM_LOG_DIRTY_PAGES，KVM按memslot GFN范围调整已有SPTE，缺失项以后按策略建立。不能裸改W而忽略并发锁和TLB。EPT violation也可能是MMIO/真正只读等其他原因，必须识别。软件设备直接写RAM需要覆盖软件计脏。',q:'已改 EPT 的 W 位，旧可写 TLB 未失效，会有什么风险？',answer:'CPU可能继续用旧权限直接写，绕过本轮检测而漏记。',source:src('15a-冷热页与脏页跟踪.md','https://github.com/torvalds/linux/blob/v6.14/arch/x86/kvm/x86.c')});
add('故障 GPA 怎样定位到位图','15a 脏页位图','位图记录页身份，页面字节仍需另外读取。',s=>{
 flow(s,['slot 起点\nGPA 0x400000','Guest 写入\nGPA 0x402120','slot 内页号\n2'],190,{h:90});
 table(s,[['4 KiB 页','P0','P1','P2','P3'],['起点','0x400000','0x401000','0x402000','0x403000'],['dirty bit','0','0','1','0']],60,355,1160,155,[280,220,220,220,220]);
 text(s,70,530,1140,36,'页号 = floor((故障 GPA − slot 起点) / 4096) = 2（本例地址均为假设）',23,C.purple,true);
},{note:'页大小4KiB及地址为教学例。dirty bit表示该页被记录为写过，不给出写次数、页内字节位置或新内容。保守记录可先于指令重试真正完成，不应把标脏视为新字节已保存。',q:'同一页写1000次，位图需要保存1000条记录吗？',answer:'位图通常只需该页一位为1，不表达次数。',source:src('15a-冷热页与脏页跟踪.md')});
add('下一轮要清记录并重新布防','15a 跟踪周期切换','写保护模式下，仅把位图清零可能漏掉下一轮写入。',s=>{
 vertical(s,['第一轮：P2 已记录，EPT 可写','暂停并保存对应页面 → S1','按协议清记录、重新布置检测','恢复运行，记录下一轮 → S2'],70,185,680,72,22);
 side(s,'只清位图的风险','dirty[P2] = 0\n但 EPT 的 W 仍为 1\n\n再次写入直接通过，\n可能没有写保护退出。');
},{note:'KVM GET/CLEAR语义取决于能力和模式。手动保护模式可以把读取与清理重置分开。真实在线跟踪需避免并发写在收集/清理间丢失；本图选暂停协调的教学模型。清标记不会清RAM数据。',q:'清掉 P2 的 dirty 位，会把页里的数值20清成0吗？',answer:'不会。标记元数据与实际内容分开。',source:src('15a-冷热页与脏页跟踪.md',urls.kvm+'#kvm-clear-dirty-log')});
add('pause 捕获的三种位置','15—16 范围与字节','源 HVA、RAM 逻辑偏移、server buffer 偏移分别描述不同位置。',s=>{
 flow(s,['范围记录\n源 HVA + 长度\nRAM 逻辑位置','PVM 读取\n从 FC 取字节','server buffer\n本地紧凑存放','writer\n保存 payload 与索引'],235,{h:145,gap:32,size:24});
 text(s,80,458,1120,62,'创建范围描述不搬数据，也不冻结数据。\n一致性依赖暂停与协调；恢复逻辑视图依赖索引和父层。',26);
},{note:'范围消费者将页/区间转为数据读入与输出映射。RAM逻辑位置不是Firecracker HVA，不等于buffer位置，也不等于输出文件实际位置。数据捕获不必先在Guest里形成chunk。',q:'获得一份范围列表，是否意味着范围内的字节已经保存在 server？',answer:'没有，需要执行读取。',source:src('15-保存范围与父层.md')});
add('chunk、buffer 与 queue','17 chunk 写出','chunk 组织本批任务，buffer 装字节，queue 组织等待处理的工作。',s=>{
 const a=box(s,60,240,315,150,'chunk 元数据\nentry A / B\n源与逻辑位置',C.blue);
 const b=box(s,485,240,310,150,'buffer 字节\n[A内容][B内容]\n由读取操作填入',C.teal);link(s,a,b);
 const c=box(s,905,240,305,150,'writer 写出\npayload + 索引',C.orange);link(s,b,c);
 text(s,85,460,1110,60,'一个 chunk 含多个 entry，不保证合为一次 PVM 系统调用。\nchunk 大小、在途并发、调用次数、物理 IO 次数分别测量。',25);
},{note:'固定版compact_read_chunk先分配buffer，再顺序遍历entries读取选定source并校验长度。PVM来源一个entry可能因短读多次调用。队列可持有chunk等任务，但chunk本身不是ring或buffer。批量化是优化候选，未实施或实测。',q:'一个 chunk 有两个 entry，是否保证只有一次 PVM？',answer:'不保证，当前按entry读取，且可能短读循环。',source:src('17-chunk写出与快照封存.md')});
add('紧凑 payload 保留稀疏逻辑位置','17 chunk 的索引作用','字节放在一起，不代表它们在完整 RAM 镜像中也相邻。',s=>{
 table(s,[['entry','RAM 逻辑位置','本地 buffer','长度'],['A','4 KiB','0 KiB','4 KiB'],['B','36 KiB','4 KiB','4 KiB']],60,190,1160,190,[180,340,340,300]);
 flow(s,['完整镜像\n两段相距32 KiB','紧凑 payload\n两段相邻存放','索引\n映射回各自位置'],435,{h:100});
},{note:'所有大小为纸面例子，不代表实际buffer_size。源位置普通文件时是源文件offset，ProcessVmReader时是FC HVA。writer索引必须保留各段逻辑位置，否则恢复会把B放错位置或错误补零。并发完成顺序也不能决定最终逻辑顺序。',q:'A/B 紧邻写出后，为什么仍需要两条逻辑映射？',answer:'因为它们对应的RAM逻辑位置不连续。',source:src('17-chunk写出与快照封存.md')});
add('层格式完成与快照持久化','17 封存与发布','finalize 完成格式处理，rename 切换名字，完整发布另有配套要求。',s=>{
 flow(s,['Header','Payload','Index','Trailer'],220,{h:95,gap:30});
 flow(s,['writer.finalize','临时路径 rename','配套状态 / 父引用','持久化确认'],425,{h:100,gap:30,size:23,color:C.orange});
},{note:'图为概念格式，不画压缩封装与对齐细节。源码注释finalize不保证同步到稳定存储。rename原子切名与断电持久性不同。完整快照还需VM状态、RAM层、磁盘层、父引用与manifest配套；具体fsync/远端确认协议按实现检查。',q:'文件有 payload，但 index 没写完，可以作为有效层发布吗？',answer:'不能，读者可能无法恢复逻辑视图。',source:src('17-chunk写出与快照封存.md')});
add('从快照恢复的控制顺序','18 恢复','先装载状态与设备关联，再运行 vCPU，最后核实 Guest 服务就绪。',s=>{
 flow(s,['准备磁盘 / 网络\n取得内存设备','加载 VM 状态\n暂不运行','补配置\n调用 resume','wait_for_ready\n检查 envd'],240,{h:140,size:24,gap:32});
 text(s,85,465,1110,60,'原地 resume：原运行时仍在，继续执行。\n从快照恢复：重建必要运行环境，RAM 可按需准备。',26);
},{note:'固定基线resume_from_snapshot_config经start/start_resume加载快照；普通路径acquire_shared_mem_device，load_snapshot_file指定内存后端和网络覆盖。具体FC映射模式尚待独立核验，按固定文档的私有映射/COW模型讲解，不当作部署实测。',q:'load 成功而 wait_for_ready 超时，能报告服务就绪吗？',answer:'不能，需分别报告装载/运行与服务就绪状态。',source:src('18-从快照恢复.md')});
add('恢复成功不等于全部页面已驻留','18 按需恢复','冷、热必须说明是哪层缓存；首次访问和预取都可能准备页面。',s=>{
 const a=box(s,60,250,310,120,'RAM 逻辑镜像\n例如 2 GiB',C.purple);const b=box(s,480,250,310,120,'本次访问所需页\n只准备相关部分',C.blue);const c=box(s,900,250,310,120,'继续执行\n其余页仍可按需加载',C.green);link(s,a,b);link(s,b,c);
 text(s,80,455,1120,65,'若后备数据已在 Host 缓存，可避免新增介质读取。\n页面可访问以后，普通内存访问仍走硬件地址翻译。',27);
},{note:'按需加载与COW分别决定时间和私有写语义。不能因envd健康检查成功就推导所有RAM页已读回。图中2GiB为假设。实际预取可能使后端IO提前，不应把每次读都归因于Guest首次触碰。',q:'恢复后第一次访问某页慢，能直接断言读了物理磁盘吗？',answer:'不能，可能是映射、缓存、调度、后端读取等多种工作。',source:src('18-从快照恢复.md')});
add('快照不会回滚外部世界','18 / 23 外部一致性','恢复 VM 内部状态，不保证外部连接、租约和副作用仍匹配。',s=>{
 flow(s,['VM 内部\n“付款已发送，等响应”','快照后外部系统\n已经扣款成功','恢复旧 VM\n仍以为正在等待'],240,{h:135});
 text(s,90,450,1100,70,'若直接重发，可能重复扣款。\n外部结果查询、稳定操作 ID 和对账协议需要独立设计。',28,C.orange,true);
},{note:'例子是通用分布式场景，不是AgentENV内置支付功能。TCP对端、Host conntrack/NAT、租约和外部数据库不随Guest RAM回滚。恢复后按协议重连/重新握手，不能把旧连接可用当保证。',q:'VM 状态恢复完整，就能证明外部数据库也恢复到同一时刻吗？',answer:'不能。',source:src('14-快照状态与一致性.md')});
add('网络包经过虚拟设备和 Host 网络','19 网络路径','队列完成说明发送 buffer 可以回收，不证明远端已接收或业务成功。',s=>{
 flow(s,['Guest eth0\nVirtIO-net','Firecracker\nTAP 后端','Host netns\n路由 / NAT / 策略','外部网络\n服务端'],245,{h:130,size:24,gap:32});
 text(s,80,455,1120,65,'同名接口可存在不同 netns 中。\n恢复 Guest socket 状态，不会自动恢复对端与 Host 连接跟踪状态。',27);
},{note:'本页只画通用关系，不固定项目全部SNAT/DNAT规则或代理覆盖协议。namespace网络视图与访问策略是不同控制。代理能力、TLS SNI可见性及已有连接策略取决于实现，不能当全协议域名防火墙。',q:'TX used 已发布，就能认为 HTTP 请求成功吗？',answer:'不能，远端接收、协议处理和业务成功是更高层完成点。',source:src('19-网络包怎样出去.md')});
add('隔离机制各自限制什么','20 隔离','Guest 边界与 VMM 自身的宿主权限，需要分别分析。',s=>{
 table(s,[['机制','主要作用','不能单独保证'],['硬件虚拟化','Guest 与 Host 的执行 / 内存边界','VMM 被攻破后无破坏能力'],['namespace','分隔资源视图','自动撤销所有权限'],['cgroup','资源记账与限额','限制所有 Guest 内进程数量'],['seccomp / 降权','限制 VMM 的宿主 syscall / 权限','过滤 Guest 内部 syscall']],60,190,1160,345,[280,450,430]);
},{note:'cgroup pids计数宿主task，不直接数Guest进程。内存/CPU等Host资源仍可限制VMM整体用量。seccomp作用于安装过滤器的宿主线程，其覆盖和失败动作须查具体配置，不能概称所有版本trap必杀。namespace不等于降权，chroot也不单独构成完整安全边界。',q:'Guest 内部 fork bomb，Host pids.max 会逐个计数 Guest 子进程吗？',answer:'不会，Guest进程不是宿主task，仍需Guest内约束及Host整体资源限制。',source:src('20-各种隔离分别限制什么.md')});
add('资源的拥有者、管理者和使用者','21 资源生命周期','释放一个句柄，不等于后端资源立即消失。',s=>{
 flow(s,['server\n持有资源使用权','Firecracker\n使用设备','daemon / 内核\n管理设备'],210,{h:115});
 const a=box(s,160,430,330,90,'实例 A：一个使用权',C.blue);const b=box(s,790,430,330,90,'实例 B：另一个使用权',C.teal);text(s,505,447,270,50,'共享同一只读设备',25,C.purple,true,'center');
},{note:'共享设备还可能被预取任务等使用。引用归零只是具备回收条件，实际池策略可以保留。server退出不保证独立daemon或内核设备消失，需显式清理和残留对账。',q:'删除 A，是否应该立即销毁 B 仍在用的设备？',answer:'不应该。',source:src('21-资源拥有与回收.md')});
add('清理要先停止使用者','21 回收依赖','业务超时不能替代底层终止确认，buffer 和设备都要遵守寿命。',s=>{
 flow(s,['停止 / 协调\nFC 与相关后台工作','确认不再使用\nbuffer / 设备','释放引用与句柄','按策略回收\n核对残留'],245,{h:140,size:24,gap:32});
 text(s,85,460,1110,60,'C++ RAII 管理对象寿命，异步 stop / close 协议处理仍在进行的操作。\nDrop / 析构兜底，不自动保证远端和内核资源全部回收。',25);
},{note:'固定版stop清理存在错误路径和尽力处理，不能把返回成功当成验证所有外部资源消失。停止FC不证明独立DMA或daemon工作终止。多线程和异步资源不能只按创建顺序机械反转，需按实际依赖图。',q:'上层等待读取超时，能马上复用内核仍写入的 buffer 吗？',answer:'不能，须确认底层不再访问。',source:src('21-资源拥有与回收.md')});
add('阻塞线程与挂起任务的区别','22 async 与并发','线程睡眠可让出 CPU，但不能让该线程自动回到运行时推进其他任务。',s=>{
 text(s,80,190,1110,40,'只有一个运行时工作线程（假设）',28,C.blue,true);
 flow(s,['任务 A 调用\n阻塞 pread','该工作线程\n等待系统调用返回','任务 B 已就绪\n仍无人推进'],260,{h:125});
 text(s,85,460,1110,60,'正确的异步等待：任务保存状态并返回 Pending，线程回到运行时。\n其他宿主线程可以使用 CPU，但不等于同一工作线程已经可用。',26);
},{note:'async语法不自动将同步PVM/pread改成非阻塞。阻塞期间该线程可能off-CPU，不持续消耗CPU，却仍没有返回executor。运行时可通过真正非阻塞IO或合适blocking池组织；不声称所有runtime都有相同调度策略。',q:'“阻塞”是否意味着一直占着 CPU 忙算？',answer:'不是。它可能睡眠；问题是工作线程尚未回运行时。',source:src('22-async与并发.md')});
add('取消请求与原 IO 有两个结果','22 超时与取消','上层等待结束，不保证底层停止；IO 管理者要持有资源直到安全终态。',s=>{
 flow(s,['0 ms\nREAD=42 提交到 B','5 ms\n业务超时\n发送 CANCEL=99','8 ms\n原 READ 才完成'],235,{h:140});
 text(s,80,455,1120,75,'42 和 99 的 CQE 要分别关联。\n取消返回 -ENOENT，可能是已完成或标识不匹配，不能直接判读失败。',26);
},{note:'时间为假设，仅限普通单次READ模型。需要依据API终态语义处理取消/正常完成竞态，buffer由在途IO管理者持有。Tokio丢弃JoinHandle可detach，abort不能强中断已开始的spawn_blocking，故句柄丢弃不等于底层取消。',q:'收到取消操作的任意 CQE，就能释放 B 吗？',answer:'不能，必须确认目标IO终态且不再访问B。',source:src('22-async与并发.md','https://man7.org/linux/man-pages/man3/io_uring_prep_cancel.3.html')});
add('超时之后可能已经成功','23 结果未知与幂等','同一逻辑操作重试复用稳定 ID，并核对参数与真实结果。',s=>{
 flow(s,['客户端发出 op=42','服务端完成副作用','响应丢失','客户端超时'],240,{h:125,gap:32,size:24});
 text(s,85,450,1110,80,'先查询结果，必要时按协议重试。\n原子认领记录能防并发重复，但副作用与记录之间的崩溃窗口仍需处理。',27);
},{note:'不能将进行中记录提前写成完成。相同key不同参数要校验。事务、外部服务幂等和对账/补偿用于不同边界；任意shell命令不能只加exec_id就保证所有外部副作用恰好一次。VM回滚也可能回滚去重记录而不回滚外部操作。',q:'超时后换一个新 ID 重试递增操作，风险是什么？',answer:'服务端可能当新操作再次执行，造成重复递增。',source:src('23-失败与恢复.md')});
add('重试次数与总预算一起限制','23 有限重试','多层独立重试会叠乘，退避与抖动不能替代安全性判断。',s=>{
 flow(s,['第1次尝试','等待 / 抖动','第2次尝试','第3次尝试'],220,{h:95,gap:32,size:24});
 box(s,170,415,940,105,'同一操作总预算 5 秒（假设）\n每次请求与等待都消耗这一个预算',C.orange);
 text(s,90,535,1100,35,'两层各最多3次尝试，底层最坏可达9次。',25,C.purple,true);
},{note:'初次+2次重试共3次。对参数/格式错误原样重试通常无效；暂时故障也要满足安全重试条件。固定总deadline，不给每次尝试重置完整预算。等待随机化缓解同步重试，但不解决副作用未知问题。',q:'已用4秒，下一次请求能再单独获得完整5秒吗？',answer:'不能，仍受原总预算约束。',source:src('23-失败与恢复.md')});
add('wall time 与 CPU time','24 / A5 性能度量','wall 看起止经过时间，CPU 看指定执行对象实际占用处理器的累计时间。',s=>{
 table(s,[['场景','wall','CPU'],['单线程计算','包含执行与调度等待','统计实际占用'],['线程阻塞睡眠','继续流逝','睡眠期间不计该线程 CPU'],['忙轮询','继续流逝','轮询执行计入 CPU'],['两个线程并行','同一时间窗','累计 CPU 可以超过 wall']],60,190,1160,345,[470,350,340]);
},{note:'只对同一线程同一时间窗，wall-CPU才可近似看作off-CPU。进程范围还含其他线程，跨请求/跨进程不能简单相减得磁盘时间。CPU执行包括执行期间的硬件停顿，并非仅有效指令计算。',q:'wall=10ms，两个线程各用8ms，总CPU=16ms，矛盾吗？',answer:'不矛盾，两个线程可并行执行。',source:src('24-性能指标怎样读.md')});
add('本地实验：睡眠与忙轮询','24 已有本地计量演示','等待时间相近，CPU 成本可以完全不同。',s=>{
 table(s,[['Windows / Node，n=3','平均 wall ms','平均进程 CPU ms'],['固定计算','104.90','109.00'],['计时器睡眠','506.82','0.00'],['忙轮询','500.04','500.00']],60,205,1160,260,[560,300,300]);
 text(s,80,490,1120,65,'0 是此次计量精度下的读数，不表示等待零成本。\n进程 CPU 含运行时线程。这里只演示计量语义，不代表 microVM 性能。',25);
},{note:'2026-11-13此前教师本地实测，Windows10.0.26200、Node24.21.0，每组3次。脚本performance.now与process.cpuUsage。计算组CPU略高于wall可受多线程/记账粒度影响，不证明单线程超限。无Linux perf/真实磁盘/Guest测试，无尾分位统计依据。',q:'能用这组三次样本宣称方案的 p99 已改善吗？',answer:'不能，样本与实验目的均不支持。',source:src('24-性能指标怎样读.md',docs+'实验/24_cpu_wall_result.json')});
add('10 ms 请求中的关键路径','24 局部优化与整体延迟','只优化1 ms阶段为0.5 ms，其余不变，总耗时为9.5 ms。',s=>{
 flow(s,['发布 / 处理\n3 ms','后端等待区间\n5 ms','交付 / 返回\n2 ms'],225,{h:125});
 text(s,85,430,1110,85,'10 ms 减少到 9.5 ms，端到端延迟降低 5%。\n这些是互不重叠的关键路径区间，不是 CPU 实测，也不能随意相加嵌套 span。',28);
},{note:'所有数值为教学假设。局部加速受到关键路径占比限制。异步阶段wall可能与其他工作重叠，需确认是否真的缩短关键路径，不能把并行阶段所有wall相加。',q:'1 ms阶段即使完全消失，总延迟最多下降多少？',answer:'在无其他变化的假设下最多10%。',source:src('24-性能指标怎样读.md')});
add('DSA 卸载要同时看 CPU 与延迟','24 搬运优化的代价','卸载减少 CPU 搬运工作，但提交、等待和完成处理仍有成本。',s=>{
 text(s,60,185,1120,40,'CPU 路径',27,C.blue,true);flow(s,['CPU 执行 memcpy','数据搬运完成'],235,{h:85});
 text(s,60,375,1120,40,'DSA 路径',27,C.orange,true);flow(s,['CPU 准备 / 提交','DSA 执行搬运','等待 / 发现完成','CPU 收尾'],425,{h:105,gap:32,color:C.orange,size:24});
},{note:'图为职责图，非具体CPU/IOdie拓扑，不含未测阶段比例。CPU与DSA访问内存的具体路径依硬件型号/NUMA部署。阻塞等待可省CPU但调度可能延迟发现完成，忙轮询计CPU且会争用。真实选择需测相同工作量的端到端wall及所有相关CPU。',q:'CPU成本下降，是否足以证明单请求延迟降低？',answer:'不足以，需要分别测延迟和CPU。',source:src('24-性能指标怎样读.md')});
add('并发提升容量，也可能增加排队','24 吞吐与排队','到达量持续超过处理能力，无拒绝、取消或扩容时队列会增长。',s=>{
 flow(s,['每秒到达\n600 个请求','等待队列\n每秒净增约200','每秒最多完成\n400 个请求'],245,{h:140});
 text(s,85,455,1110,75,'有效并发可以重叠等待或利用多核。\n瓶颈饱和后继续增加在途请求，吞吐可能不变，而延迟继续升高。',27);
},{note:'600/400为稳定速率教学假设。比较并发vs串行时必须固定到达率和工作负载；并发若将容量从100提升400，确实可比串行少排队，但600仍大于400所以仍不稳定。不能把这两种比较混淆。',q:'并发16增至64，吞吐不变而延迟上升，多出的请求主要在哪？',answer:'通常更多在排队/等待瓶颈，但需观测定位具体资源。',source:src('24-性能指标怎样读.md')});
add('perf 与 /proc 回答不同问题','24 观测工具','CPU热点解释在 CPU 上做什么，不能直接解释全部请求等待。',s=>{
 table(s,[['工具 / 数据','适合回答','常见边界'],['单调时钟 + 请求 ID','每笔操作端到端延迟','Guest / Host 时钟需校准'],['/proc utime + stime','选定进程 / 线程 CPU 增量','tick换算、PID复用、范围'],['perf stat','CPU时间 / 计数事件','不自动含独立 daemon'],['perf record / report','采样事件的热点归因','Self / Children 不可混加']],60,190,1160,345,[330,370,460]);
},{note:'proc PID stat14/15是utime/stime，cutime/cstime是已等待回收子进程记账，无对应CPU字段ctime。Firecracker utime已含guest_time，勿重复加。CPU采样40%不等于wall40%；off-CPU等待需要调度/IO时间线等额外证据。',q:'memcpy占CPU样本40%，能断言10ms请求有4ms在复制吗？',answer:'不能，事件、统计范围和wall口径不同。',source:src('24-性能指标怎样读.md')});
add('公平 A/B 比较的控制条件','24 实验设计','相同工作量、缓存、并发和统计范围，才能解释方案差异。',s=>{
 table(s,[['需要固定或分组','需要一起报告'],['数据大小、镜像 / 快照链、版本','延迟分布、样本量、失败 / 超时'],['并发 / 到达率、CPU / NUMA、限额','成功吞吐与排队情况'],['Guest / Host / 后端缓存状态','所有相关组件的 CPU / 成功工作量'],['交替或随机测试顺序','原始样本、配置与边界说明']],60,205,1160,315,[600,560]);
},{note:'A冷缓存并发1与B热缓存并发8不能隔离实现差异。并发批次wall/N不是每请求延迟。若有失败、残留后台任务和快照链增长，必须保留并说明。取中位数时总CPU需逐样本相加再汇总，不能随意把组件中位数相加。',q:'B延迟降低10%但CPU/请求增加40%，能直接宣布更好吗？',answer:'不能，需要延迟、容量、成本目标与资源预算。',source:src('24-性能指标怎样读.md')});
add('综合推演：读取中途失败','复习题 A 普通读路径','用请求身份和完成条件回答，先区分领取成功与数据读取成功。',s=>{
 flow(s,['FETCH CQE 已到\nqid=0 / tag=7','后端 READ 返回\n负错误码','daemon 报告失败','Guest 读如何结束？'],245,{h:140,gap:32,size:24});
 text(s,90,455,1100,70,'补充变式：Guest 缓存命中时跳过哪里？\n后端缓存命中时又跳过哪里？server 是否搬运这些字节？',26);
},{note:'参考答案：FETCH成功仅领取；READ失败不能伪装成功数据。错误经ublk、FC、VirtIO状态传播，Guest最终按实际错误/短读契约结束。Guest缓存命中可免此笔VirtIO读；后端缓存命中可免新增介质读但不必消除整条虚拟设备链。',q:'请分别指出任务描述、实际字节、通知各在哪里。',answer:'描述在virtqueue/ublk描述区/SQ；字节在各层buffer；通知经MMIO/eventfd/完成事件等。',source:src('12-ublk与存储daemon.md')});
add('综合推演：增量快照与恢复','复习题 B 快照路径','从基准、写入记录、范围、字节到恢复视图，逐步检查信息是否丢失。',s=>{
 flow(s,['基准 S0\nP0=10，P1=20','运行期间\nP0改30再改10','保存增量 S1\nP0是否要记录？','从 S1 恢复\nP1从哪里取得？'],245,{h:145,gap:32,size:24});
 text(s,90,460,1100,65,'补充变式：RAM层写失败、父层被删除、仅位图清零。\n分别影响哪一个完成条件，能否安全继续？',26);
},{note:'参考答案：P0仍可能dirty，不能仅因字节改回就自动清位；P1若未被新层覆盖则从S0回落。RAM层失败无法发布完整成功快照；父层缺失破坏逻辑视图；仅清位图在写保护模式可能漏下一轮写入。',q:'恢复成功后，是否能断言所有 RAM 页都已读入？',answer:'不能，按需恢复可只准备已用部分。',source:src('15a-冷热页与脏页跟踪.md')});
add('把机制压缩成可核验的表达','面试表达与理解检验','结论、机制、边界、案例用来组织表达，理解仍靠解释因果和预测变式。',s=>{
 vertical(s,['结论：Guest 普通访存不走 VirtIO','机制：GVA 经 Guest 页表与 EPT 到 HPA','边界：后备页未准备可能触发 Host 取页','案例：Guest 文件缓存命中，Host 仍可能读 RAM 镜像'],70,185,1140,72,22);
},{note:'案例可用明确标注的纸面推演，不必冒称实测。五个优先深点不是深度上限，其他主题出现前置缺口时同样深入。缺数字不等于没理解，但不能用未做实验支撑实现性能结论。',q:'把这页遮住，用自己的话解释同一个边界。',answer:'关键是区分Guest虚拟设备数据路径与Host准备RAM后备页的路径。',source:src('面试题库.md')});
add('下一步复习与课程接续','学习记录','先复述 dirty 周期与完整读路径，再进入第25课多节点与资源池。',s=>{
 text(s,80,195,1100,90,'当前复习：为什么 EPT 收紧后还要处理旧 TLB？\n下一轮为什么不能只清脏页位图？',31,C.blue,true);
 flow(s,['地址与执行\n独立画图','读取与快照\n完整复述','冷热与脏页\n变式推理','第25课\n多节点 / 资源池'],365,{h:135,gap:32,size:24});
},{note:'本轮材料完善不改变独立验收状态。第21—24课已在对话讲解并有局部作答证据，旧状态表需校正为待复习而非未开始。尚待核验：实际配套Firecracker mmap与共享page cache、实际dirty生成/清除时序、具体io_uring接法。',source:src('学习记录.md')});

add('设备准备时，server 做了什么','微观补充 / 12 ublk','设备准备主要发生在创建或恢复阶段，普通 IO 复用已经建立的设备通路。',s=>{
 flow(s,['server 发控制请求','daemon 建立设备\n配置队列与请求槽','块设备节点可打开','FC 配置 drive\nGuest 看到 /dev/vda'],185,{h:105,gap:30,size:23});
 table(s,[['Host 节点','职责'],['/dev/ublk-control','全局创建设备、配置参数'],['/dev/ublkcN','该设备的命令与 IO 请求交接'],['/dev/ublkbN','Firecracker 访问的块设备接口']],60,340,1160,200,[420,740]);
},{note:'固定基线daemon集中管理设备，通过Unix socket接server创建请求。块节点可能已经出现但权限尚未就绪，因此需要确认实际可打开。N是内核分配设备号，不应假设它与某个沙箱编号永久相同。',q:'Host /dev/ublkbN 和 Guest /dev/vda 是同一个节点吗？',answer:'不是。FC把宿主设备作为后端，Guest看到自己的VirtIO块设备。',source:src('12-ublk与存储daemon.md',urls.ublk)});
add('描述符表、两个环与数据区域','微观补充 / 06 内存布局','四块内容都可位于 Guest RAM，但地址范围和用途各自独立。',s=>{
 const a=box(s,60,195,255,90,'可用环 avail\n链头编号 3',C.blue);const b=box(s,405,195,440,90,'描述符表\n#3 请求头 / #4 数据 / #5 状态',C.purple);link(s,a,b);
 const c=box(s,405,425,440,100,'实际 buffer\n请求头、4096字节数据、状态字节',C.teal);link(s,b,c,'bottom','top');
 const d=box(s,945,425,275,100,'已用环 used\n{id:3, len:…}',C.orange);link(s,c,d);
 text(s,60,350,275,115,'领取后不需要擦除槽位，\n靠发布索引和消费位置\n识别新旧工作。',24);
 text(s,905,200,315,100,'已用环记录链的完成。\nGuest 仍需检查设备状态\n并处理收到的内容。',24);
},{note:'示意未启用额外地址翻译扩展的split queue。描述符表、avail、used是不重叠区域，可同一大分配分区。箭头表达定位与处理依赖，不代表拷贝。描述符链头3、数据描述符4与ublk tag属于不同身份空间。',q:'已用环里的 len，能代替 virtio-blk 的成功 / 失败状态吗？',answer:'不能，必须检查设备协议状态。',source:src('06-VirtIO描述符队列与通知.md',urls.virtio)});
add('一笔 4 KiB 读的请求与完成时序','微观补充 / 12 完整交接','FETCH、后端 READ、COMMIT 和 Guest 返回有不同的完成条件。',s=>{
 const xs=[70,335,630,950];['Guest / FC','Host ublk','daemon / OverlayBD','后端'].forEach((v,i)=>{text(s,xs[i],180,240,35,v,24,C.blue,true);line(s,xs[i]+90,230,0,305,C.line,1);});
 function event(x1,x2,y,label,color=C.blue){s.shapes.add({geometry:'connector',kind:'straight',position:{left:Math.min(x1,x2),top:y,width:Math.abs(x2-x1),height:0},line:{fill:color,width:2},...(x2>x1?{tail:{type:'triangle'}}:{head:{type:'triangle'}})});text(s,Math.min(x1,x2)+8,y-29,Math.abs(x2-x1)-12,27,label,20,color);}
 event(160,425,270,'块 READ');event(425,720,325,'FETCH 完成 / 交任务');event(720,1040,380,'后端 READ');event(1040,720,435,'字节 / 结果',C.teal);event(720,425,490,'COMMIT 旧请求',C.orange);event(425,160,545,'后端完成，FC再发布used',C.orange);
},{note:'线从上到下表示事件顺序，不按真实时间比例。daemon提前挂FETCH，此图省略预挂步骤。READ后端使用io_uring是选定示例，缓存命中可省略新增后端介质读。Guest驱动检查used与状态，再经FS把字节交用户buffer。',q:'哪条完成首先证明目标字节已被读取？还需要检查什么？',answer:'后端READ结果在本例表示读到字节，但要检查错误/短读；Guest用户buffer有效还需后续交付。',source:src('12-ublk与存储daemon.md')});
add('冷热识别先确定观察窗口','微观补充 / 15a 冷热识别','“最近访问过”不等于精确访问次数，Host 普通进程采样也不必覆盖全部 Guest 访存。',s=>{
 table(s,[['观察方式','能提供什么','需要核对'],['应用日志 / 计数','键、文件、请求的访问频率','对象到页的关联'],['Accessed / idle tracking','一段时间是否被访问的线索','清除、采样开销与覆盖'],['DAMON','按区域采样并聚合访问模式','内核后端、权限与粒度'],['虚拟机中的 Host 观测','Guest RAM 后备页相关信号','KVM / 二阶段访问是否纳入']],60,195,1160,330,[350,400,410]);
},{note:'热度必须定义时间窗口、采样周期、粒度和阈值。只看到Accessed=1不能得出1000次访问。虚拟化下实际硬件访存与普通进程HVA访问路径不同，要验证backend覆盖，不能仅统计FC用户态读写。',q:'某页在一小时内写过一次、最近一分钟不访问，它可以冷且脏吗？',answer:'可以，热度窗口与dirty基准不同。',source:src('15a-冷热页与脏页跟踪.md','https://docs.kernel.org/admin-guide/mm/idle_page_tracking.html','https://docs.kernel.org/mm/damon/design.html')});
add('四种“脏”对应不同目标','微观补充 / 15a 修改记录','Guest 文件写回、RAM 快照和 Host 文件持久化是不同处理链。',s=>{
 table(s,[['位置 / 记录','相对什么目标','后续处理'],['Guest 文件缓存脏页','Guest 文件系统 / 虚拟磁盘','Guest 写回或 fsync 协议'],['Guest RAM 快照 dirty','跟踪周期 / 父快照','捕获内存字节并生成增量'],['Host 文件缓存脏页','Host 文件的后备存储','Host 写回与同步'],['OverlayBD writable upper','逻辑块的新修改','索引更新、封存与发布']],60,195,1160,330,[400,390,370]);
},{note:'Guest fsync推进文件到Guest磁盘路径的语义，不会自动清掉RAM相对父快照的dirty。除vCPU写入外，VMM设备后端也可能直接写Guest RAM，需要软件记录覆盖。不能用EPT写保护保证捕捉一切宿主HVA写入。',q:'VMM 直接用 HVA 写 Guest RAM，必然触发同一条 EPT 写保护吗？',answer:'不必然。它走宿主页表，因此需要覆盖宿主设备写入的软件计脏。',source:src('15a-冷热页与脏页跟踪.md')});
add('同一工作线程如何推进另一个任务','微观补充 / 22 执行器','任务在未就绪时返回控制权，运行时线程才有机会选择其他任务。',s=>{
 text(s,70,185,510,40,'直接调用阻塞接口',29,C.orange,true);text(s,720,185,510,40,'正确的异步等待',29,C.teal,true);
 vertical(s,['A 执行同步 pread','线程睡眠，等待调用返回','B 仍排队，无线程推进'],70,255,500,75,25,C.orange,25);
 vertical(s,['A 提交 IO，返回 Pending','线程回到 executor','线程执行 B，IO 完成后再推进 A'],720,255,500,75,25,C.teal,25);
},{note:'假设唯一运行时worker。右侧需要非阻塞/异步IO以及正确注册唤醒，不是把同步函数加async关键字。阻塞worker时物理CPU仍可执行其他宿主线程，但不能凭空产生第二个executor worker。',q:'把同步 pread 放在 async 函数体内，自动变成右侧吗？',answer:'不会，需要真正让出控制权的等待机制或合适的blocking隔离。',source:src('22-async与并发.md')});
add('机器一致与业务一致的区别','微观补充 / 14 一致性','稳定捕获避免拼出不存在的状态，但合法机器状态也可能处于业务操作中途。',s=>{
 table(s,[['运行时刻','x','y','状态'],['t0','100','100','操作之前'],['t1','90','100','中间状态，尚未写 y'],['t2','90','110','操作之后'],['错误拼接','100（取自t0）','110（取自t2）','从未同时存在']],60,195,1160,285,[300,240,240,380]);
 text(s,70,500,1140,60,'暂停在 t1 可以得到合法机器状态，恢复后应用继续执行。\n是否满足业务事务边界，还需要应用与外部系统的协议。',25);
},{note:'数值为教学例。机器一致不是只暂停单个vCPU，还要协调全部相关执行者和设备写入。合法中间态与跨时刻错误拼接不同，不能要求VM快照自动处于每一应用事务的提交点。',q:'快照保存 t1 的90/100，是否必然是损坏快照？',answer:'不必然，它可能是合法暂停时刻，应用恢复后继续；业务一致性需另行约定。',source:src('14-快照状态与一致性.md')});

await fs.writeFile(work+'/slides.json',JSON.stringify(meta,null,2));
await fs.writeFile(work+'/presentation.json',JSON.stringify(P.toProto()));
for(let i=0;i<P.slides.items.length;i++){
 const s=P.slides.items[i];
 await fs.writeFile(work+'/render/'+String(i+1).padStart(2,'0')+'.png',new Uint8Array(await (await P.export({slide:s,format:'png',scale:1})).arrayBuffer()));
 await fs.writeFile(work+'/render/'+String(i+1).padStart(2,'0')+'.layout.json',await (await s.export({format:'layout'})).text());
 if(i%10===0)console.log('rendered',i+1,'/',P.slides.items.length);
}
await (await PresentationFile.exportPptx(P)).save(work+'/candidate.pptx');
console.log('draft',work+'/candidate.pptx','slides',P.slides.items.length);
process.exitCode=0;
