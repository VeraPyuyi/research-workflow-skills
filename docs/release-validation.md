Current presentation release (October 26, 2026): [90-paper study, behavior comparison and deployment](paper-presentation-study/report.md).

Current Goal/content-audit release (October 25, 2026): [validation and live-runtime limits](goal-leakage-validation-20261025.md).

Earlier acceptance below is historical.

Current focus release (October 25, 2026): [18-skill acceptance](research-focus-validation-20261025.md).

The earlier checks below are historical.

# 发布验收记录 — codex-native

核验日期：2026 年 10 月 24 日。此版本以 Sol、Astra、Luna 原生子代理执行科研，并可用独立 API key 调用 Jev；不读取 Magpie 配置。缺少 Jev 密钥或额度依据时使用原生证据比较。

## 集中代码、结构与安装检查

- 自动测试：254 项，250 通过，0 失败，0 错误，4 跳过。
- 跳过项仅为 Windows 当前权限无法创建的符号链接/目录联接案例；已有替代路径检查保留。详情见 测试记录（本地记录 `tests/results/release-code-validation.json`，含私有路径，未随仓库公开）。
- 17 个 skill 通过套件结构和官方 skill-creator 格式校验，临时安装逐文件一致。
- 版本与项目采用记录绑定 runtime_profile，兼容自动升级不跨运行版本，显式切换仍检查验证凭据、定制内容和运行任务固定版本。
- 这些是代码与工作流控制验证，不是已完成真实科研项目或论文的证明。

## 少量真实调用

Cursor 共 2 次请求（首次 Composer 2.5，加一次 Grok 4.6 定向复测），没有重复抽样挑选答案。两次返回的均值函数均通过空输入、单元素和普通序列检查。接口报告合计 **977 tokens**：630 输入、347 输出，其中输入包含 1 个缓存 token；这是接口计数，不是转换后的费用。

Composer 请求 medium，但网关记录 xhigh，档位一致性未通过。科研派发已阻止该端点，待适配器与账户条件重新核验。Grok 4.6 的请求、响应模型及网关记录的 medium 一致；这是网关与响应层的身份依据，不是独立供应商证明。

两次请求均附带 128 的输出限制，但返回的输出用量分别为 168 和 179，因此不宣称硬上限有效。要求严格输出/成本硬上限的任务不能使用这一未经验证的能力。

刷新后的 Cursor 订阅余额读数仍为 13.75%，北京时间 **2026 年 10 月 25 日 13:52:19** 重置；按量付费读数仍为 $0.00。百分比有精度限制，不能据此声称订阅消耗为零。按量付费额度未获准使用，也未进入渠道回退。

Jev **0 次**、Vertex **0 次**。账户官方入口要求登录，现有资料无法证明剩余额度覆盖，因此按已批准规则保留待验证。Jev 三种 primitive 的真实返回、Vertex Flash 真实路由均未判为通过。API key、历史成功和启用计费不替代额度证据。

## 原生 Codex 验证

使用隔离配置、现有订阅认证和独立实例，未读取 Magpie 网关配置，未修改全局配置。Luna 的单次证据提取返回正确结果，直接原生执行成立。

另一次 Sol 协调的玩具案例返回了 Luna 提取、Astra 两轮新上下文审稿的报告；报告称最多两个工作者并行。第一轮指出对数的定义域错误，第二轮接受修正后的正数定义域。但 CLI JSON 仅保留等待事件，未提供完整 spawn 参数及实际服务模型，所以**严格多模型身份与输入隔离的验收仍是部分覆盖**。其中提取分支没有按状态分组，保留这一不足，没有重试挑选成功结果。

当前可执行派发检查支持已核验的 Desktop `multi_agent_v1` 工具。CLI 自报使用另一种上下文参数；应读取实际宿主 schema 后适配，不能把工具名称或参数硬套过去。实际模型未知时保持未知，不能仅凭请求名称给独立审稿放行。

## 修复与保留边界

- 修正 Cursor Plus 的档位/Fast 约束，阻止已观察到的 Composer 档位偏差及未验证的硬上限要求。
- 保留 Jev 的实际运行白名单、固定官方端点、额度前提、脱敏记录、有限重试和未知完成状态处理。
- 纯原生工作者继续保留理论优先、跨领域复用、负结果、20% 优化预算、M1—M5、两轮新 agent 审稿和投稿/公开发布授权。
- 仓库只含配置模板、适用源码/测试和脱敏记录，不含账户原始响应、真实服务器地址、凭据或本机路径。

完整脱敏调用记录见 live-validation.json（本地记录 `tests/results/live-validation.json`，含私有路径，未随仓库公开）。发布验证凭据仅覆盖它声明的工作流发布范围；待验证渠道不被写成真实调用通过。
