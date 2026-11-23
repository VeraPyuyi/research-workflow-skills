# Changelog

## 2026-11-23 — review fixes

See [the review-fix notes](review-fixes-20261123.md). The repository is licensed
under Apache-2.0 ([LICENSE](../LICENSE)).

## Earlier README sections (moved here unchanged)

### Model, quota and configuration notes (Magpie profile)

[模型分工](../skills/research-navigate/references/model-routing.md) 和 [机器可读登记](../skills/research-navigate/references/model-routing.json) 记录免费模型、独立审读、Codex、Cursor、Vertex 及 Jev 决策服务。Jev 使用原生结构化接口，不能替代证明或授权。

- 按实际端点核验身份、能力、额度和数据权限；严格派发不经过混合组猜测，不自动进入未授权付费渠道。
- 全局最多 6 个工作者；已确认共享额度池最多 2 个并发，未知池按 1 个。共享文件由单一整合者修改。
- 免费模型执行实质分支；集中审读按里程碑开展。不可用或政策不允许时记录原因。
- Cursor Grok 4.6 已接入科研组的竞争解释、方案比较和有界工程审读规则，并分配到 13 个阶段（含主线维护）的适用分支；使用 `medium`、Fast 关闭和共享 Cursor 额度池。Composer 档位偏差仍待修复，其余 Grok 版本保留为条件候选。详见 [Cursor 路由修复记录](cursor-routing-validation-20261024.md)。
- 每批派发重新核对订阅额度与在途消耗。混合组不能保证订阅费用封顶；不能把 `max_tokens` 被接受等同于上游硬上限，也不能自动使用未经授权的按量付费。
- Jev/Vertex 额度未核实则跳过真实调用，继续其他已授权任务。详见 [验收报告](release-validation.md)。
- Vertex 只允许使用 **Trial credit for GenAI App Builder** 覆盖的调用。当前未核实赠金适用服务/SKU和余额，全部 Vertex 路由暂缓，Magpie 渠道停用；长文一致性转给 Step，复杂证据整合和独立审读使用现有授权内的 Sol/Astra。普通额度确认不能解除此限制，详见 [赠金路由核验](vertex-credit-validation-20261025.md)。

复制 `config/*.example.json` 为本机私有配置并填写实际位置。模板不提供账户、密钥、真实服务器连接或项目授权。Magpie 凭据只在运行时从用户配置读取，不存入仓库。共享服务器的 CPU、内存和 GPU 按资源预留共享，任务固定编号并可恢复；默认不独占。

[版本接续说明](../skills/research-navigate/references/workflow-updates.md) 解释同版本兼容升级、定制保护、运行中任务固定版本和显式跨版本切换。保存发布验证凭据到本机运行配置，并由项目记录引用。

### Goal recovery and submission privacy

A chat follow-up does not itself reactivate a blocked native Goal. Use
the original host's supported, explicitly authorized resume control. Its writer
lock may persist while the chat is idle; a separate app-server cannot override
it. Preserve the objective and budgets and separately observe an automatic Goal
turn. See the navigator's goal-execution reference.

Before M4/M5 and delivery, research-review inspects submitted sources,
rendered pages, metadata and nested attachments for private paths,
credentials and accidental internal agent material. Use relative paths
or explicit placeholders while retaining scientific AI descriptions and
required disclosures. Automated scans report coverage gaps; human/agent
inspection of rendered and unsupported content remains required.

[Goal/content-audit validation](goal-leakage-validation-20261025.md) distinguishes offline acceptance from pending live recovery.

### MathRSI integration and model readiness (2026-11-18)

The 18 existing skills now share optional mathematical handoffs: exact theorem
imports, connections to actual original inputs, a unique parent return owner,
and bounded probes of the hardest remainder. Returns are consumed once before
new work starts; useful in-flight work and original evidence remain pinned.
Goal completion and M1-M5 checks are unchanged. See
`skills/research-navigate/references/mathematical-work.md` and
`docs/math-rsi-validation-20261118.md` for scope and measured checks.

6.2 Astra/Sol are registered as pending local access. Old admissible models remain
active until the host actually exposes the new IDs and resources are verified.
Benchmark preferences do not grant access or certify mathematics. See
`docs/model-routing-20261118.md`. Updates stay within the project's runtime
profile; no paper is marked delivered merely because a suite was installed.

### 6.2 routing update (2026-11-21)

6.2 Astra and 6.2 Sol are activated for covered subscription work. See [the dated access and validation report](model-activation-20261121.md). Existing projects adopt this compatible update at recovery or handoff; running tasks remain pinned. A successful inference does not prove a fresh subagent spawn or host Goal auto-continuation.
