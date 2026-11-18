# MathRSI 数学研究与流程自改进调研

调研日期：2026-11-18，Asia/Shanghai。
源码基准：`lisresearchgroup/math-rsi`，`main` 提交
`de556f3d5427343153d8d24bed4578ccfe66400c`。
本轮交付是源码调研、一次精确算术复算和适配建议；未安装 MathRSI、
注册其 MCP、调用其外部模型或启动历史科研项目。

## 结论

值得吸收，尤其适合增强现有流程中的数学调查、证明推进和停滞诊断。
建议保留我们的 18 个 skills，将成熟机制放进相关阶段的按需参考资料，
暂不整套覆盖安装，也不另建第二个论文总调度者。

它的主要增量不是“多几个审稿模型”，而是让数学工作的输入、证明义务、
适用条件、返回位置和原问题的联系更明确。它的 RSI 更新的是工作流、
领域知识和工具，不是基础模型权重；仓库验收也明确区分历史数学成果、
当前接口试用和未测的通用研究效果。不能据此宣称它必然提高解题率、
论文质量、录用率或 GPU 利用收益。[S1, S3, S4, S15]

## 读到了什么

读取了 README、工作流、演进流程、插件合同、验收说明、快速开始、v6
变化说明，数学调查和 meta-evolve 的完整入口，以及实际输入覆盖、
全局重评、上下界协同探索、临界取等四份完整参考资料。
另外读取 reviewer MCP 指南第 1–110 行、verify 入口第 1–90 行、
历史验证记录第 1–160 行，以及证明修复示例的输入和完整复算程序。
详见文末来源索引。

没有阅读所有六个领域的全部证明、归档、求解器轨迹或 Lean 工程。
对其数学纪录和大规模计算的描述均按作者报告及其限定范围理解，
本轮不重新认证那些成果。一个错误猜测的 `proof-evidence.md` 路径
返回 404，后续直接读取真实 verify 入口，未把该缺失文件列为已读证据。

初始概览文件从 `main` 读取，随后查询并固定上述提交，后续实质阅读
都使用这个提交。上游 README 和 v6 说明将主线标为 v6；
`EVOLUTION_WORKFLOW.md` 中仍有“当前推荐 v4”的旧段落。
因此采用时必须绑定提交和具体文件，不能只依赖“当前版”字样。[S1, S3, S8]

## 机制与我们现有流程的对应

| 机制 | 上游的具体做法 | 我们已具备的内容 | 建议补齐的位置 |
|---|---|---|---|
| 可调用的文献结论 | 搜索异名、等价表述、前后引用、勘误和反例；关键结果读完整前提与证明依赖 | 跨领域迁移表、来源版本、适用条件、复用审计 | `research-survey` 增加“这条结果供给哪个证明义务、原对象怎样满足前提”的明确返回内容 |
| 单一调度者 | 子阶段完成后回原调用者；局部 verify 返回同一个 prove 义务 | Goal 接续、稳定任务编号、恢复和去重 | `research-navigate` 的任务包补充父义务与返回点，防止父子各启动一次下一阶段 |
| 原问题连接 | 证明局部结论后核对实际输入、共同对象和下游使用；不把条件引理当原题完成 | 理论材料、主张证据链、主线维护 | `research-design`、`research-review` 增加显式“前提供给—本引理—原结论”连接 |
| 最难余域优先 | 新分类先有界检查最难未闭分支；易分支通过不清零难核停滞计数 | 连续迭代、贡献审计、同主题调整 | `research-focus`、`research-analyze` 判断原问题实际减少了什么困难，避免用局部成果数量替代进展 |
| 新定理先消费 | 在已证明合法的表示或补全中应用新结论，再派发真实剩余工作 | 已有结果复用、避免重跑 | `research-design`、`research-navigate` 让新结论实际撤掉已覆盖的待办，仍保护有效在途任务 |
| 反例与候选共同演进 | 分开证明目标和搜索目标；合法反例回流修正候选；存活猜想仍为待证 | 小验证、竞争解释、负结果保留 | 为适合的问题增加按需的构造/反例与界/证明双分支，不替代正式证明 |
| 精确认证与停机 | 浮点发现与严格证书分开；收益低于修补误差、或现有松弛达到已证天花板时转向 | 版本固定、实验有效性、停止条件 | `research-implement`、`research-analyze`、`research-review` 增加有条件的精确复算与数值停滞判断 |
| 分层吸收经验 | 通用行为进 base，领域定理与检查器进插件，单题参数留项目；证据不足暂缓 | `research-optimize`、20% 预算、节点发布与版本保护 | 优化候选增加“适用层次、改变了哪个实际决定、谁消费改动”的记录 |

上表前三列来自上游源码与本机现有技能的比较；最后一列是本轮建议，
不是已经部署的新行为。[S2–S13]

## 数学理论调查应怎样增强

在现有文献和理论记录上补一份简短的“定理使用记录”，不另建数据库：

1. 原结论：来源、版本、实际阅读页码/定理号，完整对象域、量词、
   假设及结论。区分原文定理、证明中的中间估计和我们组合出的新推论。
2. 对应关系：当前对象与原对象、参数、概率空间、算子如何对应。
   不能只因名字相近就认定等价。
3. 前提供给：哪些条件已经得到，哪些需要新证明，哪些在当前任务不成立。
4. 使用位置：解决哪个现有义务，使用后原问题仍欠什么。
5. 失败边界：不适用的输入、真正反例、未核原文、重试需要的新证据。

在关键结果上查勘误与反例，在基础数学上不设“只看近三年”的截断。
发现式浏览可看摘要；承担证明的结果必须读完整相关声明和必要依赖。
缺原文时保留待核状态，继续不依赖它的路线，不写成“没有已有研究”。[S5]

这会比单纯扩大文献数量更有用：下一阶段收到的是可以应用或明确不能
应用的数学工具，而不只是领域名和阅读清单。

## 证明推进中最值得优先吸收的三项规则

**第一，保护量词和同一个对象。** 区分任意原输入、我们可选的辅助量、
上游实际输出和后继所需性质。`∀x∃a`、`∃a∀x` 和 `∀x∀a` 不是同一任务；
不能无意中要求过强命题，也不能在上游只保证“存在某输出”时自行选取
一个尚未证明可达的理想输出。多个局部见证要共同满足条件。[S9, S13]

**第二，统计原问题的实际新增覆盖。** 新表示、新命名或重复覆盖同一类
原输入不等于新进展。对于确有有限覆盖定义的问题，可比较新结果相对
既有结论并集的新增部分；没有可计算覆盖率的开放问题，就记录关闭了
哪条真实义务，不能杜撰“理论完成百分比”。先对最难余域做小探针，
仍保留有用的负结果、必要完整枚举和已批准确认实验。[S9, S11]

**第三，取等后要兑现为可使用的结构。** 当严格整数界只差一单位时，
可以研究临界等号层，但要在同一对象上证明非负松弛项共同为零。
“集合等大”不能直接推出“集合相同”；“存在见证”不能直接推出
“存在经过指定端点的相容见证”。这适合收紧界、等号条件和机制证明，
不是所有数学论文的强制步骤。[S12]

## RSI 设置：保留现有节奏，改变改进依据

建议继续使用我们的阶段轻量复盘和 M1–M5 集中检查，而不照搬上游所有
审读循环。上游 `global-reassessment` 在触发停滞、扩批或默认同路线
三批检查点时，通常要求两个独立只读意见；这会增加日常模型调用。
适配时应保留“原问题瓶颈是否变化”的轻量判断，只有真实停滞、
主要假设变化或所属大节点才运行针对性独立审读。[S11]

本轮建议的记录可并入现有 handoff：

```yaml
math_work:
  original_spec_ref: "<existing specification>"
  active_obligation: "<exact remaining mathematical claim>"
  parent_obligation: "<claim that consumes this result>"
  return_to: "<owning stage or coordinator>"
  imports: "<existing literature/theory records>"
  proved_connection: "<what is actually established>"
  remaining_connection: "<what still needs proof>"
  next_discriminating_action: "<bounded, authorized next action>"

workflow_improvement:
  evidence_ref: "<actual success, failure or correction>"
  destination: "shared_behavior | domain_reference | project_only | defer"
  protected_strengths: "<existing behavior to retain>"
  consuming_stage: "<who will actually use the change>"
  verification_milestone: "M1 | M2 | M3 | M4 | M5"
  adoption_status: "proposal"
```

这是建议格式，未写入运行配置。继续沿用最多 3 个候选、每候选一次
定向修正、每节点最多一个合并版本，以及既有预算内 20% 的优化份额。
候选不能修改冻结验收标准；优化待办不能拖住已满足条件的论文交付。
运行中实验保持版本固定，新版只在原有兼容升级点采用。

上下界协同探索只用于存在清晰构造/反例与界/障碍对应的问题。上游用
目标、挑战、新颖性、条件四类信号引导探索，并在全部适用历史对象上
检查候选不等式。移植时保留其数学意义，不照搬具体图问题的奖励函数。
“未找到反例”只是候选尚未被推翻；严格上界仍需要证明或范围明确的
证书。近极值样本带不能偷偷变成最终定理的条件。[S10]

数值停机也要有证据：只有确立舍入/修补残差后，才比较新的收益是否
足以超过误差；只有原始/对偶证书在同一松弛中真正闭合，才能宣布该
松弛已到上限。松弛可行解不一定对应原问题的真实对象。[S8, S13]

## 依赖、模型与安装判断

MathRSI 自身以 Markdown 工作流、领域材料和轻量 Python 工具为主，
支持 Claude Code 和 Codex；不要求 Anthropic API key 才能使用数学
入口。外部 reviewer 需要各自的 CLI、认证和实际服务，单有桥接文件
不等于已能调用。上游提供的模型名和 effort 是其项目选择，不能直接
取代本机已验证的模型路由。[S7, S14]

建议只把按需数学参考接入现有流程：

- 继续由我们原有导航和 Goal 环境负责阶段接续。上游指令不是后台
  自动唤醒器，不能把安装技能写成“已验证无人干预长期续跑”。
- 保留 Jev 的决策辅助，科学证明与审读仍由实际证据承担。
- 使用本机可用且已授权的审读模型；同家族新上下文只能报告其真实
  独立范围。不给失效的 Anthropic 通道安排任务。
- 不将上游同名 `research-review` 或完整 ARIS 安装器覆盖到个人技能目录。
  如将来采用领域插件，先固定提交并仅接相关入口及必要资源。
- Lean、SAT/SMT、精确整数或有理数检查按问题使用。LLM、RL、Causality
  的建模假设与现实有效性仍需各自的实验和识别依据。

## 本轮实际复算

检查了上游证明修复示例：对两个共享三个顶点的四元超边，
顶点独立二染色并不使两个“整条边单色”事件独立。

本地独立实现穷举 5 个顶点的 32 种染色，得到：

- `P(B_e)=P(B_f)=1/8`
- `P(B_e ∩ B_f)=1/16`
- `P(B_e)P(B_f)=1/64`

因此原证明中的独立性步骤确实错误。原目标仍可用不依赖事件独立性的
并集上界证明：最多 7 条四元边时，坏事件并的概率至多 `7/8`，所以
存在没有单色边的染色。程序还用精确分数核对了 `m=0,...,7` 的算术。

复算代码为 [finite-replay.py](finite-replay.py)，实际结果为
[replay-result.json](replay-result.json)。它验证了这个有限反例和算术，
不是一项全新数学发现、完整 agent 修复循环、Lean 验证、跨模型审稿，
也不是 RSI 性能评测。源例与输入见 [S16, S17]。

## 建议的后续开发顺序

1. **先补语义和交接。** 在 `research-survey`、`research-design`、
   `research-navigate` 加入定理使用记录、原题连接和唯一返回点。
   在原有小案例上检查是否真正继续父义务，而不是只生成材料。
2. **再补停滞与证明证据。** 在 `research-focus`、`research-analyze`、
   `research-review` 加入最难余域、量词与共同对象检查。验证错误引理
   能被拒绝，正确的弱结论能被及时使用，必要重复不被误停。
3. **最后按课题扩展工具。** 在 `research-implement` 增加当前课题确实
   需要的精确检查器或稀疏证书，在 `research-optimize` 中按四种层次
   分流经验。先证明实际任务收益，再考虑自动生成/调用这些工具。

以上是可落地的适配建议；本轮没有把它们伪记成已安装能力或新科研成果。

## 来源索引

以下链接固定到本轮核对的提交。除标明片段者外，为完整读取。

- S1 [README](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/README.md)
- S2 [WORKFLOWS](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/WORKFLOWS.md)
- S3 [EVOLUTION_WORKFLOW](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/EVOLUTION_WORKFLOW.md)
- S4 [SKILL_ACCEPTANCE](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/SKILL_ACCEPTANCE.md)
- S5 [mathrsi-survey](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-survey/SKILL.md)
- S6 [mathrsi-meta-evolve](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-meta-evolve/SKILL.md)
- S7 [QUICKSTART](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/QUICKSTART.md)
- S8 [V6_CHANGES](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/V6_CHANGES.md)
- S9 [actual-input-coverage](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-prove/references/actual-input-coverage.md)
- S10 [primal-dual-coevolution](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-route-loop/references/primal-dual-coevolution.md)
- S11 [global-reassessment](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-research/references/global-reassessment.md)
- S12 [critical-equality](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-prove/references/critical-equality.md)
- S13 [mathrsi-verify，1–90 行](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/base/skills/mathrsi-verify/SKILL.md)
- S14 [REVIEWER_MCP，1–110 行](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/REVIEWER_MCP.md)
- S15 [VALIDATION，1–160 行请求范围](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/development/VALIDATION.md)
- S16 [示例复算程序](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/examples/proof-repair/replay.py)
- S17 [示例原证明](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/examples/proof-repair/starter/PROOF.tex)
- S18 [PLUGIN_CONTRACT](https://github.com/lisresearchgroup/math-rsi/blob/de556f3d5427343153d8d24bed4578ccfe66400c/docs/PLUGIN_CONTRACT.md)
