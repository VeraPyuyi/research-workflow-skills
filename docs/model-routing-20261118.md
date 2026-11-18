# Model routing evidence, 2026-11-18

Release intent: Magpie registry v8; native registry v2. Withdrawn Anthropic v7
is not revived. Public release, local admission and successful inference are
separate facts.

| Source and setting | Observation | Routing implication and limit |
|---|---|---|
| OpenAI, Introducing GPT-6.2 Astra and Sol, read 2026-11-18, FrontierCode 2.0, both max | Sol is within 0.5 points of Astra at about one-fifth cost/task | Prefer 6.2 Sol for routine engineering once locally admitted. Manufacturer-reported engineering evidence; not proof quality. |
| Vals Science Index v1, page labelled updated 2026-11-16, fetched 2026-11-18 | 6.2 Astra 68.44%, old Astra 65.09%, 6.1 Sol 59.63%, 6.2 Sol 57.76% | Prefer 6.2 Astra for hard science; retain older science second opinions. Point estimates alone do not establish significant differences. |
| Vals 6.2 Sol model page, max, OpenAI default provider, published 2026-11-17 | Science Index 57.76 +/- 2.26; Terminal-Bench-Science 58.57 +/- 5.93 | Separate scientific terminal execution from aggregate science. These are page-reported uncertainty values; do not invent their confidence level. |
| Epoch benchmark hub, updated 2026-11-18 | Mixes Epoch-administered and external results; harnesses and configurations matter | Keep version, tool environment and source type; do not pool incompatible settings into a universal champion. |

The Vals index averages biology investigation, mechanism discovery and scientific
terminal workflows. Its page date precedes public model release by one day; keep
both source dates instead of silently rewriting either. Detailed runtime images,
seeds and all Astra/legacy hyperparameters were not recovered in this refresh.
The 6.2 Sol page reports default provider OpenAI and max effort, with a warning
that individual benchmarks may differ. Unknown settings remain unknown.

Sources:

- https://openai.com/index/introducing-gpt-6-2-astra-sol/
  (web reader succeeded; separate direct HTTP fetch returned 403).
- https://www.vals.ai/benchmarks/science_index
- https://www.vals.ai/models/openai_gpt-6.2-sol
- https://epoch.ai/benchmarks?view=table

## Local evidence and decisions

Both inspected Codex catalogs and the current native subagent tool allowlist lack
`gpt-6.2-astra` and `gpt-6.2-sol`. Magpie's configured Codex list also lacks them.
Both profiles therefore register them as `pending-local-access` with a dispatch
block. The default working assignments remain old Astra, 6.1 Sol and Luna.
Preferred future assignments are explicit policy entries, not executable access.
No 6.2 functional calls were made; the allowed four-call ceiling is unused.

Codex quota refreshed at 2026-11-18 20:15 +08:00 showed 63% of its weekly
subscription window remaining, reset 2026-11-22 00:08 +08:00. This is neither
6.2 entitlement proof nor new API/PAYG permission. Recheck at actual dispatch.
No local context capacity for 6.2 has been assumed from its public model card.

Old `workbuddy-ai/hy3`, `workbuddy-ai/step-5-preview` and
`workbuddy-ai/deepseek-v4.1-flash` no longer appear in the current list. They remain
historical registry identities, blocked from new dispatch. Active free branches
use the separately named OpenCode Zen endpoints. A similarly named WorkBuddy
paid/different endpoint is not treated as the old free channel.

Cursor remains a covered-account branch subject to a fresh allowance check.
Vertex retains the App Builder promotional-credit hold. Anthropic remains absent.
Jev stays optional structured decision support with abstention and its own
authorization; it does not validate proofs or create access.

All Astra versions map to `gpt-astra`, all Sol versions to `gpt-sol`, across
channels. Same-family review cannot earn independent gate credit. Request and
actual identity, and context independence, are recorded separately.

The two custom research groups retain subscription/API ordering and user rules.
Only retired research targets and the new narrow mathematical intents are
changed. Strict, free-only and independent-review tasks still use direct
endpoints. Global six-worker and shared confirmed-two/unknown-one pool limits
remain in force.
