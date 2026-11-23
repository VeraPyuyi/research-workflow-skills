# Research Workflow Skills

18 个可组合的科研 skills，覆盖 LLM、Agent、DL、RL、Causality 及交叉研究，从问题、理论与实验推进到正式论文和适用的复现包，并支持研究工具产品化。

> **现状**：套件的脚本与控制逻辑有 360 余项离线测试，但还没有在真实论文项目上完成端到端运行；行为效果的 A/B 评测已有运行器，尚无结果。见 [验证与范围](#验证与范围)。

本分支的 `runtime_profile` 为 **magpie**（作者的多模型网关配置）。`codex-native` 分支使用 Codex 原生子代理。两版科研要求相同；没有任何多模型配置时，单个模型也能按本套件工作，交接里会注明"未做模型独立复核"。

## 开始使用

需要 Python 3.12 或更新版本。结构校验依赖 PyYAML，绘图示例依赖 Matplotlib；共享服务器适配器另需 Paramiko。

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py
.venv/bin/python scripts/install_skills.py            # 预览
.venv/bin/python scripts/install_skills.py --apply    # 安装
```

Windows（PowerShell）：

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python scripts/validate_skills.py
.venv/Scripts/python scripts/install_skills.py
.venv/Scripts/python scripts/install_skills.py --apply
```

安装默认写入个人 Codex skills 目录，可用 `--target <目录>` 指定其他宿主的 skills 目录。相同文件重复安装不改动；内容不同的已有 skill 会被保护。更新已有安装用 `scripts/update_skills.py`（快照、外部备份、差异保护）。

调用示例：

```text
$research-navigate 为当前项目启用完整论文 Goal，按已批准课题、目标场所与预算自主推进，完成正式稿、适用复现包和两轮全新上下文模拟审稿。
$research-survey 调研当前问题及相邻领域的已有理论、方法和可复用结果。
$research-analyze 审计现有稿件和实验的贡献，区分解释与猜想，提出并推进预算内最有信息价值的下一轮工作。
$research-focus 回溯原始研究主题和历次转向，判断当前论文是否偏离主线，在同一大主题与既有预算内继续有证据支持的研究。
```

完整论文 Goal 仅在用户明确启用时创建或复用，单阶段调用保持指定范围。更改核心方向、资源承诺或执行投稿/公开发布时，沿用真实授权边界。宿主专用的 Goal 恢复流程见 [Codex Goal 适配](skills/research-navigate/references/hosts/codex-goal.md)。

## 流程

| Skill | 交付 |
| --- | --- |
| research-navigate | 路径、依赖、项目状态、Goal 与交接 |
| research-scope | 任务书、资源、停止条件与人工检查点 |
| research-survey | 已解析的文献记录、证据、跨领域迁移与复用候选 |
| research-ideate | 形式化定义、候选比较与已执行的决定性检查 |
| research-design | 推导、证明义务、对照、功效依据与锁定的实验协议 |
| research-baseline | 可信基线及复现差异 |
| research-implement | 科研实现、受保护的评测、必要的正确性检查 |
| research-experiment | 有界试运行、正式实验、运行账本与用量 |
| research-analyze | 不确定性、主张账本、贡献审计与迭代工作包 |
| research-write | 有证据支撑的正式稿、图表与数字溯源 |
| research-review | 科学审读、复用审计、盲审面板 |
| research-submit | 场所要求（含 LLM 政策）、投稿/返修包 |
| research-product-discover / build / release / maintain | 研究工具的需求、构建、发布与维护 |
| research-optimize | 项目内只记复盘事件；仓库层面的"流程实验室"负责经过评测的改进 |
| research-focus | 稳定大主题、当前论文主线、累积偏移与旁支边界 |

理论优先但允许有界的小验证和反例搜索（由任务书的 `theory_mode` 决定，明确的经验或复现研究可以关闭）；不把数值结果当作证明。完整检查集中于 M1 方案、M2 实现试运行、M3 证据结论、M4 完整稿和 M5 修订交付；局部故障只诊断与重测受影响部分。

## 项目记录与校验

项目没有既有约定时，状态和证据写入 `research/` 下的固定文件（[默认布局](skills/research-navigate/references/records.md)）：`STATE.json`、`brief.md`、`literature.jsonl`、锁定的协议 `protocol/P<n>.md` 与 `.lock`、`protocol/evaluator.lock`、`runs/ledger.jsonl`、`analysis/claims.jsonl`、`reviews/panel.json`。对应的脚本：

| 脚本 | 作用 |
| --- | --- |
| `research-navigate/scripts/check_records.py` | 锁定协议与评测文件；按里程碑检查记录是否完整、互相一致 |
| `research-survey/scripts/verify_refs.py` | 用 arXiv、Crossref、OpenAlex 解析每条参考文献；查不到的不得进稿 |
| `research-write/scripts/claim_audit.py` | 列出正文里无法溯源到主张账本或生成表格的数字 |
| `research-review/scripts/check_submission.py` | 投稿包泄漏审计，含写给 LLM 评审的隐藏指令与不可见字符 |
| `research-review/scripts/check_score.py` | 从评审原始报告读分，核对报告与稿件哈希、校准和审计 |
| `research-navigate/scripts/reviewer_panel.py` | 按模型谱系检查盲审独立性与预登记面板 |

三条硬规则写入了共享契约：缺数据或运行失败时不得用合成、占位或记忆中的数值顶替（"在现有条件下不可行"是合法结果）；评测代码与数据对方法实现方只读，M3 前核对哈希；参考文献必须能被书目数据库解析才可引用。

## 盲审与完成条件

M4 一位全新上下文的盲审；M5 在派发前预登记至少两个（默认三个）不同**谱系**的评审组成面板，所有成员审同一份冻结稿，修订后由同一组谱系的新 agent 再审，不允许因为低分而换评审。谱系按供应商/基础模型判断：同一厂商的不同产品或版本只算一个，谱系不明的模型不能担任计分盲审。

每个面板谱系先用同一场所已知录用与拒稿的公开论文做一次校准，区分不开的不能计分。M5 要求：每位面板成员 ≥8/10（来自原始报告文件）、主张审计与参考文献检查在同一稿件哈希上通过、没有未解决的 critical/major 问题。分数是必要条件而不是充分条件，是否投稿始终由用户决定；在额度内如实交付部分结果是合法的结束状态。

## 流程改进（优化器）

项目内，协调者在有意义的交接点向 `research/optimizer/events.jsonl` 追加一行复盘：优点、带标签的缺点、可复现的轨迹和成本。写事件不触发任何操作，不占研究预算，也不会拖住论文。

修改共享 skill 只在仓库层面的[流程实验室](skills/research-optimize/references/workflow-lab.md)里进行，有独立预算和你的批准：
1. 汇总多个项目的事件，只处理在至少两个项目中重复出现、或有可复现轨迹的弱点（`scripts/workflow_lab.py aggregate`）；
2. 先冻结评测集和标准，诚信场景与回放用例受保护；
3. 每轮最多 3 个候选；
4. 改动前后两套 skill 在同一批场景上各跑至少 3 次，由另一谱系的模型盲评，`workflow_lab.py compare` 判定；
5. 独立评审后由你批准，再走发布工具，保留旧版本以便回滚。

第一轮 [`lab/L1`](lab/L1/README.md) 用来测量 2026-11-23 的评审修复是否真的更好，控制文件已冻结，尚未运行。

## 模型与配置

阶段 skill 只在需要多模型分派时才读取 [模型分工](skills/research-navigate/references/model-routing.md)。具体端点、额度和账户状态属于作者的 Magpie 配置，见 [机器可读登记](skills/research-navigate/references/model-routing.json) 与 [变更记录](docs/CHANGELOG.md)；别的用户可以忽略它们，或复制 `config/*.example.json` 为本机私有配置后填写自己的。

共享实验服务器的凭据支持 `ssh-agent:`、`keyfile:<路径>` 和 Windows 凭据管理器 `wincred:research/<名称>`；配置模板不含账户、密钥或真实服务器。

## 验证与范围

```bash
python -B -m unittest discover -s tests -p "test_*.py"
python scripts/validate_skills.py
python scripts/fetch_study_data.py && python scripts/validate_presentation_study.py
python scripts/check_links.py
```

以上检查在 CI 中对 Linux 与 Windows 运行（`.github/workflows/ci.yml`）。它们验证脚本与控制逻辑，不证明这套流程能产出好论文。行为效果用 `scripts/behavior_eval.py` 评测：把 `tests/` 下的场景在"加载 skill / 不加载"两种条件下各跑至少三次，由另一谱系的模型按 rubric 评分并汇总通过率；其中 `tests/integrity-scenarios.json` 是诚信陷阱场景（缺数据、可利用的评测、要求改结果、错误前提、注入评审等）。

[论证与图表记录](skills/research-write/references/argument-and-figure-contract.md) 与 [表达模式库](skills/research-write/references/paper-style-study/index.md)（90 篇论文的描述性研究，见 [研究报告](docs/paper-presentation-study/report.md)）用于写作阶段；模式库不预测录用概率。研究的原始数据（约 1.4MB）放在独立的数据分支 `paper-presentation-study-data`，不随 skill 安装，见 [数据位置](docs/paper-presentation-study/DATA.md)；`python scripts/fetch_study_data.py` 会按固定提交获取并校验。

本仓库不包含 API key、原始账户响应、真实服务器配置或开发缓存；历史验证文档中引用的本地 `tests/results/` 记录因含私有路径未公开。

**许可证**：[Apache License 2.0](LICENSE)，Copyright 2026 VeraPyuyi。该许可证覆盖本仓库中作者自己的代码、skill 与文档；论文表达研究只收录了作者对公开论文的描述、元数据与页码定位，不包含、也不重新授权论文原文或图表。

变更历史见 [docs/CHANGELOG.md](docs/CHANGELOG.md)。
