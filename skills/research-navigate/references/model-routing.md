# Codex-native research routing

This edition has runtime profile `codex-native`. Use only the native host tools
and exact model IDs in [model-routing.json](model-routing.json). This registry is
a task allocation contract, not evidence of model superiority, account access,
remaining quota or the identity that served the current chat. An existing gateway
connection does not establish direct native dispatch. Do not inspect routing or
credential configuration from another runtime.

## Assign a bounded package

Inspect the actual inputs, scientific dependencies, authorization, context size,
modality, tools and canonical write scopes. Then choose an explicit model:

| Work | Requested model |
| --- | --- |
| Default integration, engineering, experiment control, writing | `gpt-6.2-sol`; 6.1 Sol fallback |
| Hard mathematics, causality, scientific and contribution review | `gpt-6.2-astra`; old Astra fallback |
| Bounded source extraction, structured records, log extraction | `gpt-6-luna` |

The stage defaults are starting assignments. Route hard mathematical or causal
subtasks to Astra even inside a Sol-led stage. Luna extracts from a bounded
inspected source set; it does not adopt scientific conclusions, approve a proof,
serve as the principal scientific reviewer or integrate an entire paper. Sol
checks extraction against original sources before using it. One integrator owns
shared definitions, protocols, conclusion records and manuscript files.

Choose a reasoning effort explicitly from the currently supported host levels.
Registry preferences do not prove a level is supported. Do not round, substitute
models, or claim execution if the exact dispatch is unavailable. Prepare the
work package and record `unexecuted` while continuing independent authorized work.
Every substantive stage retains execution, milestone review ownership and
integration; it need not launch a separate agent or review after every edit.

## Native host calls

The actual host interface is:

```text
multi_agent_v1.spawn_agent(model, reasoning_effort, message, fork_context)
multi_agent_v1.wait_agent(targets, timeout_ms)
multi_agent_v1.send_input(target, message, interrupt)
```

Pass the exact bare model ID to `model`. Supply a bounded task in `message`, with
input versions, allowed output paths, completion evidence and constraints. Set
`fork_context` explicitly; choose false for an independent branch and always for
review. Use the returned agent identity with `wait_agent` and `send_input` using
the host's current target representation. Use `interrupt` deliberately; sending
an interruption is not proof of completion, termination or freed capacity. Read
actual host schemas before constructing calls; these scripts do not implement an
RPC transport, service adapter or autonomous scheduler.

`check_dispatch.py` prints the precise `spawn_request` after offline admission.
The caller makes that call only when the host really exposes it, after the
coordinator's atomic reservation. Generative dispatch has no alternative model service or
automatic retry chain. An unsupported call stays unexecuted. Bounded retries need
reconciled completion, stable task identity and remaining authorized resources.

## Request, observation and completion are separate

A dispatch record contains `runtime_profile`, `requested_model`, explicit
`reasoning_effort`, capability evidence, resource authorization, the shared quota
inventory, output scopes and actual returned artifacts. Before execution,
`actual_model` is `unknown` (or null). Record the model actually reported by the
host separately, with its evidence, after execution. A requested ID, subscription,
current chat identity or successful tool response cannot establish the actual
served model. Preserve unknown identity and any mismatch. Never copy requested
identity into an actual-identity field as a default.

The offline checker validates local declarations only. It does not independently
verify permissions, data provenance, model identity, host tool availability,
account balances or the truth of a capability record. A ready packet is neither
an executed call nor a quota reservation nor passed independent review.

Validate an admission packet from the suite root:

```text
python -B skills/research-navigate/scripts/check_dispatch.py <packet.json>
python -B skills/research-navigate/scripts/check_dispatch.py <packet.json> --spawn-result <observed-spawn.json> --spawn-evidence <spawn-record-reference> --dispatch-record <new-dispatch-record.json>
python -B skills/research-navigate/scripts/check_dispatch.py <packet.json> --completion <receipt.json> --dispatch-record <dispatch-record.json>
```

The `--spawn-result` path records only a real host response and creates a new
coordinator dispatch-record file exclusively; it never overwrites one. It does
not call spawn or turn a proposed agent ID into an observation. Keep the original
admission packet for this operation and reconcile live inventory separately.
The portable `config/native-dispatch.example.json` shows the required fields;
replace project-relative example output paths with resolved absolute scopes before
admission. Do not claim its sample authorization/capability text as real evidence.
Admission returns `task_id`, `request_digest` and the full `admitted_request`.
The digest is SHA-256 over canonical JSON for the task, immutable request fields,
exact spawn arguments, and (for blind review) the absolute input paths, revisions
and file-content hashes. Keep this frozen admission packet separate from live
worker inventory. After the actual spawn returns, the coordinator uses
`record_dispatch(admission, spawn_result, spawn_evidence=reference)` and persists
the separate record before accepting completion. `spawn_result.agent_id` must be
the ID observed in that host response, never an ID copied from a completion claim.
The record keeps task ID, admitted digest and `spawn_returned_agent_id` with its
spawn evidence. It is an explicit coordinator journal, not a remote attestation.

A completion receipt needs matching `task_id`, `request_digest`, status `completed`,
`agent_id` exactly matching the recorded spawn result, actual model identity,
model evidence and returned artifact references. Call
`check_completion(plan, receipt, dispatch_record)` with that separate record.
A missing binding, a same-model receipt from another task/agent, a changed request
or changed frozen input bytes never frees capacity or passes a gate. Completion
compares the frozen contract; it does not readmit the now-running task against
live inventory. Reviews also need observed
`fork_context: false`, input-audit and isolation records; blind reviews need the
actual input manifest. Unknown completion, missing evidence or mismatched identity
returns `needs-reconciliation`, with no release of capacity or gate credit. An
explicitly failed or cancelled task is reconciled by the coordinator; it is never
counted as scientific success. Keep unsuccessful and unknown attempts in history.

## Shared worker limits and output ownership

Use at most six active/reserved workers globally, at most two in a confirmed
Codex shared pool, and at most one if its pool status is unknown. All five native
models share `codex`; changing model does not create capacity. The effective
parallelism of this edition is therefore two when the pool is confirmed and one
otherwise, further bounded by live host capacity and approved resources. Include
other chats' commitments in the coordinator's inventory, not only this branch.

Before each spawn, reconcile running, reserved, cancellation-requested and unknown
jobs, atomically reserve capacity in the coordinator's existing ledger, then
spawn sequentially. A timeout does not mean the agent stopped. Retain unknown
commitments and reconcile through `wait_agent`; never dispatch a duplicate to
replace an unknown job. The checker rejects stale/unknown active state, duplicate
identities and a seventh worker even when other fields are invalid. It is a
snapshot check, not a lock, atomic quota ledger or reservation service.

Optional Jev uses its separate unknown pool of one. Declare `decision_active` explicitly (an empty list when none). Include Jev in
`decision_active`, with explicit service identity, profile, running/reserved state
and write scopes. Its task identity and outputs participate in collision checks
and every listed service task counts toward the global six. Native Codex pool
limits remain separate. Unknown Jev completion retains its commitment; see
[optional decision assistance](decision-support.md). Only that standalone adapter
may call the fixed Jev endpoint; native generative dispatch rejects service/key/
endpoint fields and never treats Jev as a worker or scientific reviewer.

Resolve actual paths and aliases before checking. Give parallel branches disjoint
write scopes, including directory ancestors. Empty scopes explicitly mean read
only. Windows scopes compare without case sensitivity; POSIX scopes are case
sensitive. For general worker output scopes the checker cannot discover symbolic links,
mapped-drive aliases, filesystem permissions or unseen workers. Blind review
inputs receive the stricter local filesystem checks below. A coordinator performs those checks.
Shared CPU/RAM/GPU jobs additionally follow
[the experiment host contract](../../research-experiment/references/shared-server.md).
Model worker capacity is separate from compute admission.

## Independent review and same-model bias

At M1 research/protocol, M2 implementation/pilot, M3 evidence/conclusions, M4 first
complete-paper review and M5 revised-paper review/delivery, consolidate the
appropriate checks. Reuse valid coverage; reopen affected checks after material
changes. Review never authorizes a scientific scope expansion, submission or
public release. See [reuse and simplification](reuse-and-simplification.md).

Prefer Astra scientific/contribution review of Sol-produced work. If Astra authored
a central proof, assign a capable different model such as Sol to its independent
review, recording limitations. Distinct agents of the same model provide context
independence but can share model bias. Normally block same-model independent
review. An expressly declared `allow_same_model_review: true` plus
`same_model_bias_record` permits a provisional context-only check; it never
satisfies a required model-independent gate. Unknown producer or reviewer identity
also cannot certify such a gate. The optimizer retains its stricter different
model/different context publication requirement.

For reviews, the packet keeps `author_models`, `author_evidence`, `new_agent`,
`prior_agent_ids` and `prior_review_agent_ids` as coordinator-only records. Do not
include them in a blind reviewer prompt. The completion receipt must prove a new
agent identity distinct from authors, participants and earlier reviewers.

M4 and M5 require two newly spawned agents, both with `fork_context: false`, as
specified in [venue review](../../research-review/references/venue-review.md).
Round two receives only the revised submission, permitted attachments and verified
venue criteria, never round-one findings, replies, optimizer records or project
history. Before round two, reconcile round one's actual completion and record its
agent ID. The checker builds a neutral prompt only from the allowed input
manifest and rejects an additional `message`. Declare an existing canonical
absolute `submission_root` using forward slashes and put only submitted files
beneath it. Each manifest `ref` is raw POSIX relative syntax: reject empty/dot/
parent components, device names, control characters, trailing dots/spaces and
alias spellings before normalization. Inputs must be distinct existing regular
files, with canonical paths contained under that root. Symlink and reparse-point
components, including the root's ancestors, are rejected. The emitted neutral
message contains absolute allowlisted file paths and content hashes, so a fresh
worker needs no inherited directory or project search. The root is a path base,
not permission to read every local file there.

Inspect actual bundle contents for
contamination; manifest labels alone prove nothing. Enforce read restrictions
with host capabilities when available; otherwise record instruction-only isolation.
No automatic third complete round is created by this routing guide.

## Candidate choices

Use [research-focus](../../research-focus/SKILL.md) for theme-sensitive choices.
Sol maintains the shared anchor and next-task mapping; Luna can extract
instruction provenance from supplied sources. Astra reviews material scientific
alignment at M1-M5. Routine reminders require no new worker or review.
Preserve evidence-backed in-theme pivots and negative findings. Private theme,
pivot history and reminders remain outside both blind-review bundles.
Focus/optimizer bookkeeping cannot generate recursive stage events.

Use [native evidence comparison](decision-support.md): inspected evidence and
program constraints first, bounded native comparison when useful, then the
integrator's justified decision. Do not invent confidence distributions or
acceptance probabilities. A model opinion is neither scientific evidence nor
release/adoption authority. Preserve candidate failures and unresolved proof or
empirical obligations instead of voting them away.


The optional standalone Jev service is defined in `decision_services`, outside
`models`. Environment key/config loading, explicit credit authorization, response
validation, durable receipts, bounded retries, cache version checks and native
fallback are specified in [decision-support.md](decision-support.md). A key does
not establish current credit; this edition records credit as unverified. Jev
results are advisory evidence for the integrator and never independent-review or
optimizer-publication approval.

## November 18 model update

On November 18 the exact IDs `gpt-6.2-astra` and `gpt-6.2-sol` were registered
but blocked. The November 21 checks in [model-activation.md](model-activation.md)
verified covered subscription inference and supersede that pending state.
Current subagent tool exposure is still required independently.
Prefer 6.2 Astra for difficult science,
actual-input connections and hardest branches; prefer 6.2 Sol for engineering,
experiment control and drafting. Retain old Astra and 6.1 Sol for scientific
second opinions; Luna remains bounded extraction. Benchmark evidence and limits
are recorded in the repository's `docs/model-routing-20261118.md`.

All Astra versions/channels share the Astra family, all Sol versions/channels the
Sol family. A version change is not independent review. Record actual served
identity and fresh context independently. Ordinary tasks prefer high only where
supported; difficulty does not authorize an unsupported effort or API billing.
New endpoints stay blocked until the registry and live capability evidence are
updated together. Preserve six workers, confirmed-two/unknown-one shared pools,
Jev abstention and M1-M5 review cadence.

## Current 6.2 access

Read [model-activation.md](model-activation.md) when selecting the newly activated 6.2 models. Use the current registry, current host allowlist and actual allowance; retain qualified legacy fallbacks.
