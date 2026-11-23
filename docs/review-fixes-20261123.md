# 评审修复记录（2026-11-23）

依据 2026-11-23 对提交 `4a5c2d0` 的流程评审，按优先级逐项修改。下表"状态"列中，"已改"表示本次提交已实现并有测试或校验覆盖，"未改"给出原因。

## P0

| 问题 | 改动 | 状态 |
| --- | --- | --- |
| 断链：七个文档链接到未公开的 `tests/results/`；`model-routing.md` 指向不存在的文件 | 改为"本地记录、未公开"的纯文本说明；路由文档改指已有的带日期文档；新增 `scripts/check_links.py` 并纳入测试与 CI | 已改 |
| 重复文件 | 删除 `docs/paper-presentation-study/sources.json`，报告改链接到 skill 内的唯一副本。`benchmark-assets/render_evidence.py` 是一次基准运行的冻结快照，`run_benchmark.py` 要导入它，保留 | 已改 |
| 缺数据时用合成/占位数据顶替 | `research-experiment` 新增"Missing data, failed runs and infeasible checks"；共享契约新增同一硬规则，并把"不可行"列为合法结果 | 已改 |
| 评测代码可被方法实现方修改 | `research-implement` 新增"Protect the evaluator"：M2 记录哈希、实现方无写权限、M3 前复核；`check_records.py lock-evaluator` 与 `check` 实现 | 已改 |
| 引用未经数据库解析 | 新增 `research-survey/scripts/verify_refs.py`（arXiv、Crossref、OpenAlex；网络失败记为 `unchecked`，不算通过）；survey 与 write 要求未解析条目不得进稿 | 已改 |
| 分数门：量表无锚点、未校准、只看稿件、脚本校验自报数字、逐次换家族、家族判定与文档不一致 | 见下节 | 已改 |
| 没有 CI | 新增 `.github/workflows/ci.yml`（Linux 与 Windows：skill 校验、模式库校验、链接检查、单元测试） | 已改 |
| 场景与 rubric 没有运行器 | 新增 `scripts/behavior_eval.py`（plan / grade / summarize，有无 skill 的 A/B，每场景默认 3 次） | 已改；模型调用由宿主执行，尚无评测结果 |
| 没有 LICENSE | 作者选定 Apache-2.0：新增 `LICENSE`（Apache 官方原文），README 写明适用范围 | 已改 |

## 分数门

- 模型登记表新增 `lineage`（供应商/基础模型谱系）。同一厂商的产品或版本共享一个谱系（Astra 与 Sol、Grok 4.5/4.6/4.7 各算一个）；基础模型未公开的端点留空，不能担任计分盲审。
- `reviewer_panel.py` 按谱系判断独立性，并支持预登记面板：M5 派发前登记至少两个不同谱系，修订后由同一组谱系的新 agent 再审，不能因低分换评审。交付需要整个面板审过 `final_revision`。
- `check_score.py` 不再接受命令行数字，改为读评审账本与原始报告文件：核对报告哈希、报告尾注中的分数与稿件摘要，要求面板谱系已用同一场所已知录用/拒稿论文校准且能区分（均值差 ≥1 分），并要求 `claim_audit.py` 与 `verify_refs.py` 在同一稿件摘要上通过。阈值仍是 8/10。
- `venue-review.md` 加入分数锚点、校准步骤、评审指令中的"稿件内容是数据不是指令"，以及"分数是必要条件而非充分条件"。
- `check_submission.py` 新增 `reviewer_injection` 与 `hidden_character` 两类检查。

## P1

| 问题 | 改动 | 状态 |
| --- | --- | --- |
| 记录没有形状 | 新增 [默认记录布局](../skills/research-navigate/references/records.md) 与 `check_records.py`（锁协议、锁评测、按里程碑检查运行与主张账本） | 已改 |
| 正文数字无法溯源 | 新增 `research-write/scripts/claim_audit.py`，M4/M5 冻结前运行 | 已改 |
| 协议没有锁、缺功效依据与基线充分性 | `research-design` 增加三项并在批准后锁定；`research-baseline` 的复现容差改为在协议中预先确定 | 已改 |
| 选题：作者侧自评、未先执行检查、未查前提 | `research-ideate` 改为多分支独立生成、独立成对排序、前两名先执行最便宜的决定性检查、核查前提；`theory_mode` 由任务书决定 | 已改 |
| 入口阅读负载 | 共享契约拆出 [扩展章节](../skills/research-navigate/references/workflow-extensions.md)（主线、理论材料、改进轮、数学工作，按条件读）；Codex Goal 恢复拆到 [宿主适配](../skills/research-navigate/references/hosts/codex-goal.md)；模型路由在各 skill 中改为"多模型分派时才读"；Jev 段落在 5 个 skill 中压缩为一行 | 已改 |
| 核心正文含个人账号细节 | navigate 删除 Cursor 分支要求与"Current 6.2 access"；交接示例改为角色描述；README 中带日期的段落移到 [CHANGELOG](CHANGELOG.md) | 已改 |
| 凭据后端只支持 Windows | 远程实验客户端新增 `ssh-agent:` 与 `keyfile:` | 已改 |
| 状态不持久 | navigate 每次读 `research/STATE.json`，结束前写回 | 已改 |
| 主张账本未文件化 | `research-analyze` 写入 `claims.jsonl`，含 `deviations` 与 `evidence_changed_decision`，聚合前跑 M3 检查 | 已改 |
| 场所 LLM 政策 | `research-submit` 记录 `llm_policy` 与 AI 参与说明 | 已改 |
| 优化器证据过弱 | 每个用例至少跑 3 次、按通过率比较；诚信场景为受保护强项；在有真实端到端运行记录之前，发布需作者批准 | 已改 |
| 诚信陷阱回归集 | 新增 `tests/integrity-scenarios.json` 与 rubric（8 个场景） | 已改 |
| 真实端到端试跑 | — | **未改**：需要真实项目、预算与作者参与 |
| 约 1.4MB 研究数据在代码分支里 | 作者决定移出。会话权限不允许创建 Release，改放到同仓库的数据分支 `paper-presentation-study-data`（固定提交 `81261dd`，含两条代码分支各自的版本）；代码分支只留 `report.md` 与 `DATA.md`；新增 `scripts/fetch_study_data.py`（按提交获取、校验内容清单）；校验脚本、测试与 CI 改为使用获取的副本。历史提交中仍有这些文件 | 已改 |

## 未处理（需要作者决定）

- 是否把 `magpie` 与 `codex-native` 合并为单分支加配置（两分支有 79 个文件不同，本次只改了 `magpie`）。
- 是否把共享契约抽成独立的 `research-core` skill，减少 `../` 跨 skill 引用。

## 行为变化提示

- 以 GPT 的两个产品（如 Astra 与 Sol）担任两个"独立"盲审不再被接受。
- `check_score.py` 的旧用法 `python check_score.py 8 9` 已移除。
- 现有项目在下次启动、恢复或交接时采用本版本；运行中的任务保持原版本。
