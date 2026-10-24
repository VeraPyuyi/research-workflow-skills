# Research Workflow Skills — Magpie

17 个可组合的科研 skills，覆盖 LLM、Agent、DL、RL、Causality 及交叉研究，从问题、理论与实验推进到正式论文和适用的复现包，并支持研究工具产品化。

本分支的 `runtime_profile` 为 **magpie**。仓库的 `codex-native` 分支使用 Codex 原生子代理执行科研，并可通过独立 API key 使用 Jev 决策辅助。两版保留相同科研要求，自动升级不会跨运行版本切换。

## 开始使用

需要 Python 3.12 或更新版本；科研工具和模型账户由具体项目配置。结构校验依赖 PyYAML；共享服务器适配器另需 Paramiko，当前凭据后端为 Windows Credential Manager。

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python scripts/validate_skills.py
.venv/Scripts/python scripts/install_skills.py
.venv/Scripts/python scripts/install_skills.py --apply
```

安装默认使用个人 Codex skills 目录，也可用 `--target <目录>` 指定。相同文件重复安装不改动；内容不同的已有技能会被保护。已有安装更新使用 `scripts/update_skills.py` 的快照、外部备份和差异保护流程，不能用强制覆盖绕过定制保护。

在新的 Codex 对话中调用，例如：

```text
$research-navigate 为当前项目启用完整论文 Goal，按已批准课题、目标场所与预算自主推进，完成正式稿、适用复现包和两轮全新上下文模拟审稿。
$research-survey 调研当前问题及相邻领域的已有理论、方法和可复用结果。
$research-analyze 审计现有稿件和实验的贡献，区分解释与猜想，提出并推进预算内最有信息价值的下一轮工作。
```

完整论文 Goal 仅在用户明确启用时创建或复用。单阶段调用保持指定范围。原生 Plan/Goal 操作遵循宿主实际工具；该套件不伪造模式切换，不安装后台服务。更改核心方向、资源承诺或执行投稿/公开发布时，沿用真实授权边界。

恢复已有项目时，请在原聊天明确授权“启用完整论文 Goal，从已有进度继续”。导航会实际读取/创建该聊天的原生 Goal，并将阶段完成与论文完成分开记录；阶段交接后直接执行下一项已授权工作。更新技能文件本身不会唤醒已结束的聊天，版本采用记录也不能代替实际 Goal 激活。原生接续、真实阶段进展和最终论文交付分别记录验证证据。

## 流程

| Skill | 交付 |
| --- | --- |
| research-navigate | 路径、依赖、Goal 恢复和交接 |
| research-scope | 任务书、资源和停止条件 |
| research-survey | 文献证据、跨领域迁移与复用候选 |
| research-ideate | 形式化定义、理论原型与选题 |
| research-design | 推导、证明义务、对照和实验协议 |
| research-baseline | 可信基线及复现差异 |
| research-implement | 科研实现、配置和必要正确性检查 |
| research-experiment | 有界试运行、正式实验、状态与用量 |
| research-analyze | 不确定性、贡献审计与迭代工作包 |
| research-write | 有证据支撑的正式稿、图表与附录 |
| research-review | 科学审读、复用审计、两轮独立模拟审稿 |
| research-submit | 场所要求、投稿/返修包 |
| research-product-discover | 用户需求、范围与验收 |
| research-product-build | 可用工具及使用验证 |
| research-product-release | 可审核的发布包 |
| research-product-maintain | 有界修复与演进 |
| research-optimize | 轻量阶段复盘、节点上的优化验证 |

理论优先但允许有界的小验证和反例搜索；不把数值结果当作证明。保留负结果、替代解释、来源范围和真实实验状态。完整检查集中于 M1 方案、M2 实现试运行、M3 证据结论、M4 完整稿和 M5 修订交付。局部故障只诊断与重测受影响部分。

两轮模拟审稿分别创建全新 agent，`fork_context: false`；第二轮仅取得修订稿、允许附件和目标场所标准，不取得第一轮意见或作者内部历史。文件访问是否隔离按宿主实情记录。

优化器使用已批准模型与时间预算内最多 20%，每节点最多 3 个候选、每候选一次修正、最多发布一个版本；优化待办不阻碍已符合标准的论文交付。

## 模型、额度与配置

[模型分工](skills/research-navigate/references/model-routing.md) 和 [机器可读登记](skills/research-navigate/references/model-routing.json) 记录免费模型、独立审读、Codex、Cursor、Vertex 及 Jev 决策服务。Jev 使用原生结构化接口，不能替代证明或授权。

- 按实际端点核验身份、能力、额度和数据权限；严格派发不经过混合组猜测，不自动进入未授权付费渠道。
- 全局最多 6 个工作者；已确认共享额度池最多 2 个并发，未知池按 1 个。共享文件由单一整合者修改。
- 免费模型执行实质分支；集中审读按里程碑开展。不可用或政策不允许时记录原因。
- Cursor Grok 4.6 已接入科研组的竞争解释、方案比较和有界工程审读规则，并分配到 12 个阶段的适用分支；使用 `medium`、Fast 关闭和共享 Cursor 额度池。Composer 档位偏差仍待修复，其余 Grok 版本保留为条件候选。详见 [Cursor 路由修复记录](docs/cursor-routing-validation-20261024.md)。
- 每批派发重新核对订阅额度与在途消耗。混合组不能保证订阅费用封顶；不能把 `max_tokens` 被接受等同于上游硬上限，也不能自动使用未经授权的按量付费。
- Jev/Vertex 额度未核实则跳过真实调用，继续其他已授权任务。详见 [验收报告](docs/release-validation.md)。

复制 `config/*.example.json` 为本机私有配置并填写实际位置。模板不提供账户、密钥、真实服务器连接或项目授权。Magpie 凭据只在运行时从用户配置读取，不存入仓库。共享服务器的 CPU、内存和 GPU 按资源预留共享，任务固定编号并可恢复；默认不独占。

[版本接续说明](skills/research-navigate/references/workflow-updates.md) 解释同版本兼容升级、定制保护、运行中任务固定版本和显式跨版本切换。保存发布验证凭据到本机运行配置，并由项目记录引用。

## 验证与范围

```powershell
python -B -m unittest discover -s tests -p "test_*.py"
python scripts/validate_skills.py
```

测试覆盖安装/回滚、同运行版本升级、派发与审稿输入边界、Jev 离线接口、优化预算和共享服务器恢复。最终报告分别列出离线行为、真实调用、身份与计费观察；功能性验收不是模型排名，也不是已经完成真实科研论文的证据。

本仓库不包含 API key、原始账户响应、真实服务器配置、开发缓存或收费托管工作流。未附加开源许可证；私人仓库访问权不等同于额外再分发授权。
