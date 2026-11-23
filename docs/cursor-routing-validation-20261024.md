# Cursor 路由接入与验证记录

验证时间：2026 年 10 月 24 日。此变更将 Cursor 从“登记但未进入实际路由”修正为
Magpie 科研组及阶段分工中的实际工作路由。

## 根因

- `scripts/magpie_routing.py` 先前只收集 `codex`、`google-vertex/gemini-4-argon`
  及 `free: true` 的生成模型，忽略了所有 `free: false` 的 Cursor 端点。
- `model-routing.json` 中 Cursor 端点的 `group_eligible` 全部为 `false`，且没有
  `automatic_group_intents` 映射。
- `test_magpie_routing.py` 先前把“组内不含任何 `cursor/` 成员”写成了通过条件。
- 导航说明将 `covered_account_executors` 描述成普通备选，未要求在适用阶段实际评估
  并分配或记录跳过原因。

## 已实施修改

- **Magpie 科研组 (`group/smart-split`)：** 加入 `cursor/grok-4.6:medium`，并新增两条
  意图规则：竞争解释／备选方案比较，以及有界工程第二意见（代码、测试、基线差异与数值检查）。
- **档位与阻断保护：** 生成器仅将显式声明 `group_eligible: true`、具备
  `automatic_group_intents`、无 `dispatch_block_reason`、且本机 `models_cache.json`
  已确认支持其固定档位的账户模型加入混合组。
- **阶段分工：** 在任务界定、选题、设计、基线、实现、实验异常诊断、结果分析、审读、产品发现、
  产品构建、维护和优化共 12 个阶段的 `covered_account_executors` 中，将已核验的
  `cursor/grok-4.6` 设为首选已覆盖账户执行器，并在其模型登记的 `stage_roles` 中标明有界职责。
- **保留必要限制：** `cursor/composer-2.5` 因请求 `medium` 而网关记录 `xhigh` 的档位偏差，
  继续阻止严格派发，也不加入混合组。`grok-4.7@256k` 与 `grok-4.5` 保留为条件直接派发候选，
  不伪造已完成本机调用验证。

## 额度与边界核验

- 2026-10-24 22:32（北京时间）通过 `magpie quota refresh cursor --json` 刷新：
  计划为 `Plus`，`Cursor Models` 已用 `86.25%`、剩余 `13.75%`，于
  `2026-10-25T05:52:19.068Z`（北京时间 10 月 25 日 13:52:19）重置。
- 本轮未发起新的外部模型推理请求，沿用同一订阅窗口内已完成的 `cursor/grok-4.6`
  定向复测记录（请求、响应模型与网关记录的 `medium` 一致）。
- Magpie 对允许 on-demand 的 Cursor 账户会将 `Cursor Models` 标记为 `aside: true`，
  因此混合组或账户窗口百分比本身不能强制阻止订阅耗尽后转入 on-demand。严格要求
  “绝不触发按量付费”或“必须具备上游输出硬上限”的任务，必须先核对当前订阅余量并按项目预算选择
  具备相应保证的直接端点。

## 最终验证

- 源文件和便携发布副本分别完成 255 项测试：252 通过，0 失败，0 错误，3 项因
  Windows 链接权限或未提供旧版迁移固定样例而跳过。17 个 skills 的结构校验通过，
  便携副本另通过官方格式校验。
- 本机个人安装与源文件逐文件一致；便携副本在独立目录安装后逐文件一致，并核验完整发布摘要。
- 回读实际 Magpie 科研组确认：共 16 个成员、17 条规则，其中包括
  `cursor/grok-4.6:medium` 及上述两条 Cursor 意图规则。派发预检返回 `ready-for-dispatch`。
- 发布副本保留本机已安装的完整论文 Goal 接续规则，不因同步 Cursor 路由回退为旧版阶段收尾行为。
- 本轮新增外部推理调用为 0。两类意图规则和 12 项阶段职责已配置，不能据此宣称所有阶段
  都已实际调用 Cursor；具体任务仍须满足额度、数据权限、能力和资源条件。

发布版本为 `research-20261024-cursor-routing-v4`，运行版本为 `magpie`。
完整脱敏代码验收见 cursor-routing-code-validation.json（本地记录 `tests/results/cursor-routing-code-validation.json`，含私有路径，未随仓库公开）。
