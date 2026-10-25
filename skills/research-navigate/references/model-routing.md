# Multi-Model Research Routing

Use this guide when a stage needs one or more model-backed work packages, a
free-model execution branch, independent review, or parallel dispatch. It records
which models this environment can actually use; it does not declare a universal
model champion.

For current allowance checks and observed adapter limits, read
[live validation](live-validation.md). Account-specific restrictions override
an unconstrained model catalog; an endpoint under re-verification is blocked
by the dispatch checker.

Read [model-routing.json](model-routing.json) for the machine-readable stage map
and evidence status. Re-check live availability, access and model metadata before
dispatch. A catalog entry is not proof that the current account can call it.

## Routing a work package

1. Inspect the requested outcome, artifacts, dependencies, data restrictions,
   approved resources and write scope. Read
   [reuse-and-simplification.md](reuse-and-simplification.md) when the task may
   replace, shorten or merge an existing derivation, implementation, experiment
   or analysis.
2. Select one free executor and independent review ownership from the stage map.
   Schedule the review at the applicable milestone, not after every branch/edit.
   Select an integrator when branches must be combined. Assign a paid escalation
   only when the work needs it and the applicable scope already covers the cost.
3. Select the service type first. Native Jev uses
   [decision support](decision-support.md), not a generative worker or group.
   For generative work, state the requested model and reasoning effort explicitly. A model's default
   effort is not a substitute for the stage's required effort. If the host cannot
   dispatch that exact model, provide a runnable work package for a compatible
   candidate; never claim the unexecuted model ran.
   The listed effort is a preference, not proof of endpoint support. Verify the
   live supported levels; reject silent rounding. Map a host alias to the exact
   provider only when documented by that host.
4. Split only work that has independent inputs or outputs. Reserve the shared
   resource budget before dispatch, give each branch a non-overlapping write
   scope, and keep one integrator for shared definitions, protocols and files.
5. Require each branch to return its actual artifacts, source locations,
   verification, status, uncertainty, consumption and unresolved work. Record
   requested and actually served models, effort, fallback and the reason for any
   difference.
6. Apply the relevant milestone gate before treating a branch as final evidence.
   Use startup delegation for in-scope protocol/conclusion decisions when recorded;
   a review never authorizes submission, release or a materially expanded plan.

## Access and evidence status

The following are separate facts and must remain separate in records:

- **Catalogued:** Magpie lists the model for a provider.
- **Accessible:** the configured account or key has demonstrated access.
- **Free:** the exact channel costs nothing under the recorded conditions; a
  different channel serving a same-named model may be billed.
- **Capable:** the exact endpoint supports the required context, modality, tool
  use or reasoning level.
- **Publicly evaluated:** a dated, comparable primary source supports the
  capability claim.
- **Locally validated:** an actual task in this environment succeeded.

Use `unknown` rather than inferring accessible, free or capable from a model name.
Do not transfer a benchmark from a base model, another provider, an older
checkpoint or another effort level to an exact endpoint without evidence.

The initial evidence is in `tests/magpie-evidence-snapshot.json` and
`docs/model-routing-evidence.md`. Those files describe the observed environment
at their recorded date; they are not a live entitlement check.

## Default allocation

These are working assignments for research and product stages. Use the detailed
map in [model-routing.json](model-routing.json); do not use a single global
quality ranking.

| Role | Exact model | Default effort | Use | Main limitation |
| --- | --- | --- | --- | --- |
| Difficult scientific integration | `codex/gpt-6-astra` | `max` for difficult, `xhigh` for revision | original research, contribution judgement, difficult diagnosis | paid shared Codex pool |
| Formal derivation and reliable implementation | `codex/gpt-6.1-sol` | `max` for formal/engineering, `high` for coordination | mathematical subproblems, implementation, reproducibility | paid shared Codex pool; not the legacy `gpt-6-sol` |
| Covered Cursor branch | `cursor/grok-4.6` | `medium`, Fast off | competing explanations, bounded engineering, protocol alternatives and milestone critique | shared Cursor subscription pool; refresh coverage; no verified hard output cap |
| Vertex catalogue (held) | `google-vertex/*` | not admitted | no executable default assignment | App Builder promotional credit scope unverified; provider off; see [credit policy](vertex-credit-policy.md) |
| Free scientific reasoning and code | `workbuddy-ai/deepseek-v4.1-flash` | `max` | derivations, statistics, code, independent review | exact served checkpoint may be opaque; channel-specific |
| Free literature and research synthesis | `workbuddy-ai/step-5-preview` | `high` | long-context synthesis, alternatives, contribution and reuse review | preview model; public evidence is limited |
| Free retrieval and source checks | `workbuddy-ai/hy3` | `high` | search branches, source verification, requirement checks | upstream reports 256K; endpoint context and tools need checking |
| Free mathematical checks | `opencode-zen/beam-free` | `max` | bounded verification and counterexample search | base model and free endpoint parity unverified |
| Free engineering branch | `opencode-zen/glm-5.3-flash-free` | `max` | code, tests, packaging, document production | free endpoint limits; data policy must be checked |
| Free multimodal extraction | `opencode-zen/nemotron-3.5-super-vl-free` | `xhigh` | public figures, equations, screenshots | do not send private research data to a trial endpoint |
| Free second implementation branch | `opencode-zen/mimo-v2.6-flash-free` | `max` | independent modules, examples, reproductions | no verified endpoint-specific benchmark |
| Native structured decisions | `typesafe/jev-latest` | not applicable | Choice, Score, Noul over prepared evidence | account coverage required; alias identity recorded per response |
| Separate free decision candidate | `opencode-zen/jev-1.13-free` | not applicable | reserved for an independently verified compatible adapter | interface unverified; not a generative worker |
| Free long-context alternative | `opencode-zen/longcat-2.5-preview-free` | `max` | bulk reading and cross-material extraction | current official availability must be checked |
| Free long-context alternative | `opencode-zen/nemotron-3-ultra-free` | `max` | bulk reading, information extraction | current official availability must be checked |
| Free challenging alternative | `opencode-zen/space-bunny-free` | `max` | competing explanations and adversarial checks | identity/benchmark evidence incomplete |
| Free structured task checks | `opencode-zen/nemotron-3.5-lightning-free` | `max` | checklists, structured extraction, light tool work | limited scientific reasoning evidence |

Only use a free endpoint for data it is permitted to process. The OpenCode
documentation's free-trial restrictions are channel conditions, not merely
recommendations. Public papers and synthetic examples may be usable where private
unpublished material is not. Record the policy source and date.

## Stage routing

Each row is a default, not a mandatory cast. The JSON file is authoritative for
programmatic routing and records the full list of free and reviewer candidates.

| Stage | Free execution branch | Independent review / integration |
| --- | --- | --- |
| `research-navigate` | Step progress; Lightning structured records | Sol complex coordination; Astra scientific disputes |
| `research-scope` | Hy3 background; Step brief; DeepSeek question definition | Astra or Step reviews scope and stopping conditions |
| `research-survey` | Hy3 searches; Step synthesis; DeepSeek transfer; Nemotron VL figures | Astra research judgement; Sol long evidence; DeepSeek reuse conditions |
| `research-ideate` | DeepSeek definitions/derivations; Step alternatives; Beam checks; Space Bunny objections | Sol/Astra key mathematics; Step duplicate-contribution review |
| `research-design` | DeepSeek theory/statistics; Step controls; GLM protocol support | Astra validity; Sol mathematics; independent Sol/Astra experiment-necessity review |
| `research-baseline` | GLM and MiMo separate baselines; DeepSeek formula/code; Step discrepancy record | Sol engineering; Astra independent reproduction |
| `research-implement` | GLM/MiMo modules; DeepSeek algorithm; Hy3 tests/docs | Sol integration with Astra review; Astra unresolved method design |
| `research-experiment` | GLM run scripts; Step status; DeepSeek anomalies; Lightning public logs | Sol run coordination; Astra difficult diagnosis |
| `research-analyze` | DeepSeek statistics/interpretations; Step contribution/reuse audit; GLM figures; Nemotron VL public figures | Sol evidence chain; Sol mathematics; Astra contribution decision |
| `research-write` | Step sections; DeepSeek mathematics/method; Hy3 citations; GLM artifacts | Sol consistency; Astra integration |
| `research-review` | DeepSeek scientific; Beam mathematics; Step reuse; GLM/MiMo engineering | Sol evidence chair; Astra/Sol escalation |
| `research-submit` | Hy3 venue requirements; Step response matrix; DeepSeek technical response; GLM attachments | Sol package; Astra evidence consistency |
| `research-product-discover` | Hy3 need/alternatives; Step product brief; DeepSeek research boundary | Astra product value; Sol need evidence |
| `research-product-build` | GLM/MiMo modules; DeepSeek algorithm; Step/Hy3 examples | Sol integration with Astra review; Astra complex design |
| `research-product-release` | GLM package; Step release text; Hy3 install checks; MiMo examples | Sol release candidate; Astra independent user journey |
| `research-product-maintain` | Hy3 triage; MiMo reproduction; GLM fix; DeepSeek effect regression | Sol integration; Astra regression; Astra scientific impact |
| `research-optimize` | Step preserves strengths and proposes changes; GLM implements bounded candidates | Sol/Astra independent milestone validation |

Use `covered_account_executors` as real assignment choices alongside the free
branch, with each model entry's `stage_roles` defining its bounded work. When an
independent task fits and Cursor's current subscription covers it, assign
`cursor/grok-4.6` at `medium` with Fast off; do not silently ignore this list
because the stage already has a free executor. This is useful when the shared
Codex pool is busy. Record the dispatch/result or an actual reason for skipping.
Do not add a redundant task or an immediate review just to consume a channel.

Grok 4.6 has a recorded direct functional check and is eligible for two
`smart-split` intent rules: competing explanations/design alternatives and
bounded engineering second opinions. The generator reads `automatic_group_intents`
from the registry and requires the fixed effort in the live capability catalog.
Group membership is an ordering choice, not verified current coverage or a
guarantee of execution. Strict stage assignments still use the direct endpoint.
Composer 2.5 remains blocked because its requested and observed efforts disagree;
Grok 4.7/4.5 remain conditional direct candidates. Do not claim they were tested
merely because their account lists them.

All Vertex variants, including Argon, are held outside executable assignments
until **Trial credit for GenAI App Builder** coverage and no-overage enforcement
are verified. Follow [the credit policy](vertex-credit-policy.md); a generic
allowance confirmation cannot admit these endpoints. The provider remains off,
including for direct calls and groups outside research. These assignments are
not benchmark rankings. All Cursor variants share one Cursor pool, with one concurrent worker while its
concurrency limit is unknown. Refresh the actual subscription window before a
batch and account for shared in-flight use; a historical percentage or reset is
not current authorization. On-demand/top-up usage is excluded unless separately
authorized. Magpie may continue into on-demand usage when the account allows it,
so a mixed group is not a subscription-spend guard. Do not use it when the task
requires enforceable no-overage or hard-output limits; choose a covered endpoint
with those guarantees. Do not change account billing settings to work around this.

For a simple bounded request, use one free executor and proportionate checks;
do not spawn every model merely to satisfy the table. For a full paper, queue
independent review at M1-M5 under [Goal execution](goal-execution.md).
Each substantive stage records actual free work or why none was usable; its
independent review may be consolidated with other outputs at the shared milestone.
Reusing unchanged check coverage does not require another model call.

## Parallelism and resources

- At most six active workers by default; obey a lower host limit.
- At most two concurrent tasks per confirmed quota pool. Use one while a pool's
  limit is unknown. Astra and Sol share the Codex pool even when exposed through
  different providers.
- Treat different provider names for the same account or subscription as one
  resource unless verified otherwise.
- Keep Dot to one active task. Dot is an optional execution environment, not an
  inferred model identity.
- Charge model calls, GPU jobs, server jobs, retries and review work against the
  project's approved resources. A free model call is not free GPU time.
- Do not let a free-model failure fall through to a billed endpoint outside the
  approved budget. Permit at most one caller retry for a known transient failure,
  using a compatible free candidate; otherwise return a pending work package.
  Magpie can retry internally beyond this caller limit. Reserve for that behavior
  or stop when a required hard allowance cannot be enforced. A 429 with known
  completion is different from an unknown running request.
- Before resuming, reconcile task IDs and consumption. If execution status is
  unknown, do not resubmit the job.

## Review and fallback

Reviewers must use a different model from the producer when an independent route
is available. A new context or another provider serving the same base model does
not establish model independence. Prefer a different model family/provider for
scientific controversies. If independence is impossible, state the same-source
limitation; do not label the independent-review gate passed.

Use a fallback only within the capability class and access status recorded for the
task. Free alternatives may replace free failures; a paid escalation requires
existing authorization. A model with unknown identity or access cannot be the
sole reviewer of a central mathematical or scientific claim.

Useful fallback groups:

- **Long evidence:** Step `high` -> LongCat/Nemotron Ultra free -> Sol,
  with context and data-policy checks.
- **Mathematics:** DeepSeek free `max` -> Beam `max` -> Sol `max`; Astra `max`
  for an unresolved research-level dispute.
- **Engineering:** GLM free `max` -> MiMo free `max` -> Sol `max`; Astra for
  a scientific blocker rather than routine implementation.
- **Science review:** DeepSeek free `max` -> Sol `max` -> Astra `max`.
- **Generative routing records:** Lightning -> Step -> Sol `high`.
- **Structured decisions:** native Typesafe Jev only through its verified adapter.
  If unavailable, the scientific integrator continues from evidence and records
  that no decision call occurred. OpenCode Jev is not an assumed API substitute.

Do not treat fallback as silent substitution. Record the requested model, the
actual model, why the switch happened and whether the work remains comparable.
These lists are escalation suggestions, not automatic fallback chains. A free-only
task stops before any paid candidate without a changed cost authorization.

## Magpie dispatch boundary

Magpie `use` and `useEffort` rules rank group members. The remaining members can
still be tried after failure; nested free groups do not block paid parent fallback.
Token length, historical images and compaction are not sufficient scientific
intent signals. The mixed `group/smart-split` is suitable only when its fallback
scope and auxiliary classifier/vision calls are already authorized. It does not
start parallel workers or enforce review gates.

For strict stage, reviewer or free-only work, bypass that mixed group and request
the fully qualified endpoint directly. Before dispatch, verify the provider's
fallback list is empty, the host accepts the endpoint/effort, and the complete
input (including historical images) is compatible. Automatic image description
can itself call a different model; use a verified direct vision endpoint or a
bounded text-only package, with any lost evidence identified. Do not alter global
vision settings or a group's shared `pick` as a per-worker workaround.

Use [the offline preflight](../scripts/check_dispatch.py) when a structured
admission check helps: `python scripts/check_dispatch.py packet.json`, from this
skill's directory. It sends no requests. Its packet is a projection of the current
records, not another database:

```json
{
  "id": "literature-branch-4",
  "stage": "research-survey",
  "model": "workbuddy-ai/hy3",
  "effort": "high",
  "free_only": true,
  "budget_state": "within",
  "capability_record": "dated access, context, tools and channel policy evidence",
  "supported_efforts": ["high"],
  "provider_fallback": [],
  "data_allowed": true,
  "contains_images": false,
  "direct_vision": false,
  "vision_endpoint_verified": false,
  "tools_allowed": true,
  "write_paths": ["D:/project/branches/literature-4"],
  "active": [],
  "confirmed_pools": ["codex"]
}
```

Use actual evidence, never copy the example assertions as checked facts. Each
active entry includes `id`, `model`, `status` (`running` or `reserved`) and resolved
absolute `write_paths`; include all workers sharing the allowance. A review adds
`author_model` and `author_evidence` for its actually served identity; a billed
dispatch adds `cost_authorization`, `allowance_coverage: "confirmed"` and
`allowance_record` pointing to the actual account evidence. These are distinct
from a catalog entry or a user preference. Vertex remains blocked by the specific
App Builder credit hold even when these generic fields are present. Same-model
review will fail independent
preflight even if its channel differs. A direct image route also needs
`vision_endpoint_verified: true` after checking that it accepts the input and will
not invoke an auxiliary model. `tools_allowed: false` blocks a task that needs tools.

A native decision packet adds `call_type: "structured_decision"`,
`adapter: "jev_decide.py"`, supported `decision_types`, and `effort: null`.
The adapter validates the complete candidate/request/response and measured
allowance separately. A generative endpoint with `effort_mode: "fixed"` must
match the registered fixed level; never invent another setting. Preserve actual
served identity and model-family mappings for independence, including custom-tool
variants of the same underlying model.

Stage retrospectives use the existing handoff; they do not automatically dispatch
Jev or a reviewer. Count optimizer calls under its bounded share of project model
and time budgets, including in-flight reservations. Selection scores cannot
publish a workflow version or pass a scientific review.

A single coordinator must reconcile records, check capacity, reserve the task
and then dispatch sequentially; workers can execute in parallel afterwards.
This helper does not reserve capacity, verify the truth of supplied evidence,
resolve filesystem aliases or guarantee endpoint behavior. Concurrent preflight
calls can race. Record actual served model/effort from runtime evidence when
available; otherwise mark it unknown and do not certify independence. Count
gateway retries and auxiliary calls when the runtime exposes them.

Its declared packet checks image inputs, not general audio/video capability or
a universal spending cap. Adding ad hoc fields such as `video_endpoint_verified`
or `no_paid_overage_verified` does not implement those checks. Keep audio/video
work pending until the coordinator verifies the actual endpoint and coverage;
use the provider-level hold for the current Vertex restriction. A `ready` result
for a different provider is not proof of zero incremental charges.

For M4/M5 blind venue review, add `review_mode: "venue_blind"`, round 1/2,
`new_agent: true`, `fork_context: false`, `manuscript_revision`, `venue_profile`
and an explicit `allowed_inputs` manifest. See
[venue review](../../research-review/references/venue-review.md) for its fields.
Keep author identity and prior review records coordinator-side; do not forward
the whole preflight packet to the reviewer. Input declarations are not proof of
content isolation. Record the actual fresh-agent call and actual access coverage.

## Gates

`research-focus` uses Step/DeepSeek free branches for a substantive provenance or
alignment task, Cursor Grok 4.6 for a bounded alternative-question critique when
current subscription coverage permits, and Sol integration with Astra/Sol
milestone review. See the actual stage registry; this is allocation, not a new
model ranking or a claim of current quota. Routine focus reminders reuse records
without model calls. Jev comparison is optional at real candidate choices.
Use the covered Cursor critique branch through direct exact-endpoint dispatch;
the mixed group's general focus intent selects Step and does not promise Cursor.
Carry the theme/current-thesis reminder in scientific task packets, excluding
blind venue-review packets. Focus and optimizer bookkeeping cannot recursively
spawn each other or create a per-handoff independent-review requirement.

Run `research-review` at the research/protocol gate, the principal-conclusions
gate and the submission/release gate. For full papers these map to M1/M3/M5;
M2 consolidates engineering checks and M4 is the first complete-manuscript venue
review. Schedule mathematics, experiment and writing checks at their corresponding
milestone, not continuously per edit. Round 2 uses a different fresh agent without
round-1 comments. A finding routes to its repair stage and never authorizes an
external action. Internal audits retain project evidence; blind venue reviewers
receive only the submitted bundle and criteria.

