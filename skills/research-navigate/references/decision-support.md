# Evidence comparison and optional standalone Jev

Use this reference at a genuine candidate choice: topics, cross-domain transfers,
proof routes, identification/protocol choices, interpretations, repair/reuse
options or workflow improvements. Routine routing and decisions already settled
by inspected evidence do not require another model call. The default path uses the same native model workers as the scientific stages.
An optional standalone Jev structured decision service may assist a genuine
candidate choice under explicit credit/resource authorization. It is separate
from the three generative models and never performs scientific or venue review.

## Build the comparison from evidence

1. Freeze the candidate identities, input revisions, scientific objective, resource
   envelope and authorized decision scope. Include a retain-current-work option
   when useful. Record unknown and inaccessible evidence explicitly.
2. Check hard program constraints first: authorization, budgets and commitments,
   theory assumptions/quantifiers, data and license permission, required evidence,
   output ownership and frozen acceptance cases. Use calculations and deterministic
   program checks for accounting, type validity and known-answer constraints.
   A candidate failing a necessary condition is ineligible regardless of an
   attractive model opinion. Do not delete a failed case or relax frozen criteria
   to make a preferred candidate win.
3. Compare the surviving candidates on actual evidence, proof obligations,
   implementation fidelity, costs, reversibility, information gained and decisive
   missing checks. Distinguish measured results from a hypothesis or proposed
   experiment. Avoid unexplained numeric scores and invented probabilities.
4. When comparison would add value within existing resources, ask an explicitly
   selected native worker for a bounded comparison through the routing contract.
   Use `gpt-6-astra` for hard mathematics, causality and scientific contribution
   comparisons; `gpt-6.1-sol` for engineering, integration and experiment control;
   `gpt-6-luna` only for bounded source extraction, checked against originals.
   Independent comparison uses a new agent with `fork_context: false`; it does
   not inherit an author's preferred verdict. Give branches disjoint outputs.
5. The integrator checks the actual returned arguments against sources and program
   constraints, resolves objections, and records the chosen candidate or pending
   discriminating check. Consensus does not establish correctness. Record requested
   and actual model identity separately, leaving unknown identity unknown. An
   unavailable worker yields an unexecuted package; continue evidence-based work
   within current authority without requiring the optional service.

## Required comparison record

Keep candidate IDs/revisions, inspected evidence and limitations, hard constraint
results, reasoned comparison, actual native call status/identities if any,
integrator decision and reasons, dissent, resource cost including commitments,
next discriminating check and applicable authorization. A table is useful when
candidates share criteria. Preserve rejected routes and negative results.
Do not manufacture a model rationale that was not returned.

A borrowed theorem with unmet independence assumptions remains inapplicable even
if a reviewer favors it. A complete elementary route may be pursued within an
approved derivation allowance while independent proof checking remains pending.
An observed metric improvement alone cannot establish a mechanism, and an
unproved mechanism does not invalidate a real observation.

## Stage and optimizer boundaries

Survey compares source coverage and valid transfers; ideate compares formal
candidate questions and derivations; design compares identification and fair
protocols; analyze compares evidence-supported explanations and next checks;
review compares dispositions/repairs; navigate coordinates dependencies.
Writing preserves verified status and does not turn a preference into a finding.

The optimizer uses actual task outcomes and measured cost under frozen protected
controls. Keep its 20% allowance, at most three candidates, one revision per
candidate and one validated combined publication per M1-M5 milestone. A native
comparison cannot authorize adoption, change held-out criteria, relax a budget,
create a recursive optimizer cycle or delay a completed paper. Follow
[the optimization protocol](../../research-optimize/references/optimization-protocol.md).

Comparison records remain internal. Neither M4 nor M5 blind reviewer receives
candidate comparisons, optimizer history, author preferences or prior reviews.
Scientific adoption, actual submission, deployment and public release retain
separate authority under the shared contract and any existing delegation.


## Optional Jev service: credentials and runtime whitelist

`../scripts/jev_decide.py` is a standalone standard-library System One adapter.
The endpoint is fixed to `https://api.typesafe.ai/v1/systemone`; there is no
endpoint flag, environment endpoint override, redirect, proxy, alternate service
or automatic network retry. Generative dispatch remains the three exact native
models. The registry lists Jev only under `decision_services`, never `models`.
It cannot generate code/proofs, use tools or reasoning-effort parameters, review
a manuscript or satisfy an independent/optimizer publication gate.

By default, execution reads only `TYPESAFE_API_KEY` from the process environment
and permits only `jev-latest`. A key is not evidence of credit, model access,
current version or budget authorization. Set it through the host's private
credential/environment mechanism, never a command argument, packet, committed
file, copied terminal command or log. No personal or other-runtime configuration
is discovered or read. An optional explicit `--config` JSON contains exactly:

```json
{"api_key_env": "TYPESAFE_API_KEY", "models": ["jev-latest"]}
```

Only an inspected private config may expand that Jev runtime model whitelist;
packet `account_supported_models` and `request.model` cannot expand it. Config
allows no inline secret, endpoint or provider settings. A missing key, unknown
credit, unavailable API or inadmissible service snapshot returns the ordinary
sanitized service status plus `fallback: native-evidence-comparison` and
`blocks_research: false`. Continue native evidence/program checks and integrator
work within existing authority. Unknown remote completion still retains its
Jev commitment; fallback does not erase a possibly running or chargeable attempt.
Current Jev credit remains unverified; no live call was made for this edition.

## Decision packet and wire primitives

The local schema version is 1. Required records are `id`, `stage`, `purpose`
(`research` or `optimization`), revisioned `evidence` and `candidates` mappings,
`criteria_revision`, `account_supported_models`, `served_model_evidence`,
`abstention_options`, `request`, `authorization` and `cost_reservation`.
Execution also requires `dispatch_snapshot`; optimization requires its extra
`optimization_budget`. Unknown fields, duplicate JSON keys, booleans disguised
as numbers and nonfinite values are rejected.

The wire request contains only `model`, `state` and named `questions`. State and
instructions use the supported string/object/array content union. Questions use:

- `choice`: named candidate criteria plus a real insufficient-evidence/decline
  option, declared in `abstention_options`. At least two candidates and abstention.
- `score`: an ordered list of 2–10 supported levels.
- `noul`: the supported bounded primitive, with optional true/false criteria.

Responses require exact question names/types, supported selected choices,
normalized finite probability distributions, bounded confidence, consistent score
means/legends, bounded Noul output, and nonnegative integer token usage. Preserve
actual primitive outputs and usage; do not invent a rationale. Jev's returned
confidence/distribution is a service output, not a probability of scientific truth,
venue acceptance, real improvement or permission. Hard program constraints and
original evidence take precedence; the integrator records the final disposition.

`authorization` requires boolean `existing_credit_coverage: true` and
`budget_authorized: true` with current coverage/budget references. The cost
reservation includes stable identity, unit, amount, approved limit, spending,
pending consumption, an explicit recorded flag and all active reservations.
Exact rational arithmetic checks the envelope. These declarations do not measure
real balances or create a server-enforced cost cap. Never infer coverage from a
key, prior successful call or catalog. Optimization additionally checks both
model/time dimensions within the existing 20% allowance and preserves all frozen
criteria, measured outcomes, candidate/revision/publication limits.

## Shared worker admission and durable receipts

The execution packet's `dispatch_snapshot` must use the same task `id`,
`runtime_profile: codex-native`, reconciled `budget_state: within`, an applicable
`resource_authorization`, absolute `write_paths`, the complete `active` native
worker inventory and separate `decision_active` service inventory. It may name
`confirmed_pools: [codex]` when actually confirmed. Each Jev inventory entry has
exactly `id`, `service: jev`, `runtime_profile: codex-native`, `status` and
`write_paths`. Only running/reserved states are admitted; unknown/stale attempts
must be reconciled first. The snapshot excludes the proposed task itself.

`check_dispatch.check_decision()` keeps Jev's separate unknown pool at one and
counts it with all native workers toward the global six. It also checks stable
identity collisions, write overlap and the existing native shared-pool state.
No key or HTTP transport is accessed before packet, credit, runtime whitelist
and snapshot checks pass. The coordinator atomically reserves shared resources;
the snapshot checker is not a quota ledger. A key alone cannot start an inference.

From the navigator skill directory:

```text
python -B scripts/jev_decide.py <decision.json>
python -B scripts/jev_decide.py <decision.json> --execute --receipt <decision-receipt.json>
python -B scripts/jev_decide.py <decision.json> --config <private-jev-config.json> --execute --receipt <decision-receipt.json>
```

Dry-run validates offline and never reads the secret. Execution needs the explicit
flag and a durable per-decision receipt. The journal is locked and flushed before
transport, binds packet/request/evidence/candidate/criteria fingerprints, and keeps
requested and actual model identities separate. Unknown actual version stays
unknown. Errors, keys, raw headers and service error bodies are never logged;
unsupported CLI arguments are reported without echoing their values.

A known recorded rejection may receive one explicit `--retry`, at most two total
attempts. Unknown completion, server/redirect ambiguity, torn receipts or uncertain
attempt history cannot authorize retry. Successful usage remains consumed but
unreconciled until external accounting settles it. Cache reuse requires identical
packet fingerprints and an explicit current `--verified-model-version` matching
the saved concrete version and the independently declared allowed-version evidence;
aliases, elapsed time and catalogs are not concrete-version evidence. Runtime
whitelist checks also apply before cache reuse. Never delete or replace a receipt
to reset attempts. Neither the lock nor local references are a global ledger,
remote idempotency key, tamper-proof attestation or proof of scientific correctness.

Keep service receipts, comparisons and optimizer records out of both blind venue
review bundles. Optional Jev assistance never delays a paper that already meets
its completion contract, and it creates no submission/release authority.
