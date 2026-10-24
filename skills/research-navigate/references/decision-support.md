# Native Jev decision assistance

`scripts/jev_decide.py` is a standard-library Python adapter for advisory
Choice, Score and Noul judgments at real candidate decisions: research questions,
theoretical routes, protocol variants, analysis interpretations, reuse decisions
and review dispositions. Use it when a comparison needs decision assistance.
Routine routing and work already resolved by inspected evidence do not require
a model call. No model-ranking, calibration or live inference call was used to
implement or test this adapter.

Evidence, measured results, hard constraints, protocols and approvals retain
authority. The adapter does not draft text, prove claims, pass scientific gates,
adopt recommendations or authorize external actions. Every receipt leaves
`integrator_disposition` as `pending`. Record any later human or delegated adoption
separately, with the underlying evidence. Confidence and Noul thresholds express
application policy, never scientific truth. Uncertainty is a reason to inspect
missing conditions; it is not permission to repeat calls until an answer changes.

## Prepare a comparable decision

Scientific workers first prepare each candidate in the same shape: stable id,
research objective, objects/definitions, assumptions, supporting and opposing
evidence with actual locations/revisions, prior-work/reuse relationship, proof
status, minimum informative validation, cost, applicable authority and unresolved
questions. Include those decision-relevant contents in `request.state`; local
manifest references alone are not sent to the model. A missing condition is a gap,
not permission to fabricate it. Inspect irrelevant long context out of the packet.

Programmatically reconcile numeric limits, reservations, dependencies and existing
approvals before comparison. Actual mathematics and applicability arguments belong
to the scientific workers. Jev does not perform numerical accounting, prove a
theorem or resolve a multistep scientific deduction merely by choosing a label.

Include useful abstentions such as insufficient evidence, none suitable or retain
the present method. Define Score levels descriptively before the call. Preserve
each criterion separately; calculate a weighted aggregate only with already
approved weights, outside Jev. Keep candidate order and materials versioned:
order-sensitive outcomes are a reason for bounded evidence checks, not a reason
to run a model-ranking calibration. Do not repeat unchanged requests to obtain a
preferred choice.

The integrator records its final choice, underlying evidence and any disagreement
with Jev. Never invent a rationale the API did not return. Close/uncertain
candidates usually call for the smallest useful authorized check; ask the user
only for a material unapproved trade-off. Confidence describes answer-distribution
concentration, not theorem correctness, scientific success or paper acceptance.

| Stage | Actual choice |
| --- | --- |
| Navigate | Missing dependency, independent branch order, next milestone |
| Survey | Cross-domain connection, mathematics tool or reuse candidate to read |
| Ideate | Research direction or minimum discriminating test |
| Design | Method, proof route, assumption repair or validation protocol |
| Analyze | Competing explanation, reanalysis, mechanism check, closure or pivot |
| Review | Issue type and repair priority; never scientific gate approval |
| Optimize | Experiences/candidates to validate; never release on a Jev score |

## Verified upstream interface

These official primary pages were fetched and read on 2026-10-24:

- [System One API](https://docs.typesafe.ai/api/system-one)
- [Choice](https://docs.typesafe.ai/primitives/choice)
- [Score](https://docs.typesafe.ai/primitives/score)
- [Noul](https://docs.typesafe.ai/primitives/noul)
- [List models](https://docs.typesafe.ai/api/list-models)

The network boundary is one HTTPS POST to
`https://api.typesafe.ai/v1/systemone`. The JSON body contains exactly `model`,
`state` and `questions`. The adapter fills in `model: "jev-latest"` if omitted.
Neither the packet nor the wire request accepts `effort`. There is no text-worker,
OpenCode or alternate-provider fallback. State and instructions accept a string,
object or array; this adapter requires nonempty content.

| Primitive | Request criteria | Answer fields besides type |
| --- | --- | --- |
| Choice | Object mapping option names to descriptions | choice, confidence, probabilities |
| Score | Ordered array of 2-10 level descriptions | score, confidence, legend, probabilities |
| Noul | Optional object with true and false descriptions, or null | noul |

Descriptions accept strings, objects or arrays. Choice descriptions can also be
null, as illustrated by the official Choice page; an abstention description must
be nonempty. The Noul answer is a number, not a boolean and not a fabricated
Choice distribution. It has no separate confidence field.

Choice and Score probability maps must cover exactly the submitted options or
level indices. JSON Score indices are strings starting at `"0"`. Each probability
must be finite and in [0, 1], and distributions must sum to one within absolute
tolerance `1e-6`. The selected Choice must have maximal probability. Score must
be between zero and the last level index, agree with the probability-weighted
level mean within `1e-6`, and include a legend matching the submitted levels.
Confidence and Noul must be finite numbers in [0, 1]. Booleans are not numbers.
The adapter does not round, renormalize or replace real primitive outputs.

The response must contain exactly `model`, `answers` and `usage`. Answer names
and types must match the request. Usage requires nonnegative integer
`input_tokens` and `output_tokens`; booleans are rejected. Additional response
fields, including provider errors and invented rationales, invalidate the result.
Duplicate JSON keys, nonfinite values, empty/malformed responses and bodies larger
than 2 MiB are rejected. This is a bounded subset of the upstream API: no assets,
Box, images or long-context danger-zone headers.

## Local packet, version 1

The packet is a local declaration, not the service request. Metadata,
authorization, accounting and served-version evidence stay local. Only its
validated `request` is posted, with the default model added if needed. This is a
complete illustrative packet; its evidence, approvals, versions and amounts are
examples, not established permissions or an account catalog observation:

```json
{
  "schema_version": 1,
  "id": "decision-1",
  "stage": "research-ideate",
  "purpose": "research",
  "evidence": {"revision": "e1", "items": ["Supplied artifact A"]},
  "candidates": {"revision": "c1", "items": {"a": "Method A", "b": "Method B"}},
  "criteria_revision": "r1",
  "account_supported_models": ["jev-latest", "jev-preview"],
  "served_model_evidence": {
    "revision": "served-v1",
    "reference": "supplied-version-evidence",
    "verified": true,
    "allowed_versions": ["jev-1.13.0"]
  },
  "abstention_options": {"compare": "insufficient_evidence"},
  "request": {
    "model": "jev-latest",
    "state": {"evidence": "Artifact A", "candidates": ["Method A", "Method B"]},
    "questions": {
      "compare": {
        "type": "choice",
        "instructions": "Which method merits further inspection?",
        "criteria": {
          "a": "Inspect A",
          "b": "Inspect B",
          "insufficient_evidence": "Decline: insufficient evidence"
        }
      },
      "quality": {
        "type": "score",
        "instructions": "Rate evidence completeness",
        "criteria": ["Missing", "Partial", "Complete"]
      },
      "relevant": {
        "type": "noul",
        "instructions": "Is A relevant?",
        "criteria": {"true": "Direct evidence", "false": "No direct evidence"}
      }
    }
  },
  "authorization": {
    "existing_credit_coverage": true,
    "budget_authorized": true,
    "coverage_reference": "existing-allocation-1",
    "budget_reference": "approval-1"
  },
  "cost_reservation": {
    "id": "reserve-1",
    "unit": "credits",
    "amount": 1,
    "approved_limit": 100,
    "spent": 10,
    "pending": 2,
    "recorded": true,
    "active": [{"id": "reserve-1", "amount": 1}]
  }
}
```

All fields shown are required, except `request.model`. The only additional
top-level field accepted is `optimization_budget`, required exclusively when
`purpose` is `optimization`. Unknown fields block. `schema_version` is integer
1, never boolean. Use a stable nonempty decision id and a supported stage:
`research-navigate`, `research-scope`, `research-survey`, `research-ideate`,
`research-design`, `research-baseline`, `research-implement`,
`research-experiment`, `research-analyze`, `research-write`, `research-review`,
`research-submit`, `research-product-discover`, `research-product-build`,
`research-product-maintain`, `research-product-release` or `research-optimize`.
The optimizer stage must use `purpose: "optimization"` and its quantitative
optimization budget; relabeling it as research cannot bypass that share.

Evidence and candidates require nonempty revisions and supplied content.
Candidate items are an object keyed by candidate id. Every comparative Choice
requires at least two substantive candidate options plus an explicit abstention
named by `abstention_options`. Substantive option ids must exist in the candidate
manifest; the abstention must not masquerade as a candidate. A returned decline
stays a decline in the receipt. An empty abstention map is valid when there are
no Choice questions. Freeze instructions, criteria, score levels and revisions
before the call; never tune them after seeing its output. The adapter does not
invent actual evidence or questions from revision labels.

## Account aliases and served-version evidence

`account_supported_models` is a nonempty unique list of current requestable
account names. Both `jev-latest` and `jev-preview` are accepted. The requested
name must appear here and in the runtime Magpie provider's `models` list.
The official models API lists account model names and aliases; an alias-only
catalog does not establish concrete versions.

Separately, `served_model_evidence` requires nonempty `revision` and `reference`,
literal `verified: true`, and a nonempty unique `allowed_versions` list. The
integrator supplies evidence that these are acceptable concrete served identities.
Do not claim semantic versions came from a catalog that returned only aliases.
`jev-latest` and `jev-preview` cannot appear in `allowed_versions`. Missing,
unknown or numeric verification does not pass. This evidence is required even
if the service eventually reports only an alias.

Identity is not inferred from a semantic-version pattern. For example, an
explicitly evidenced opaque identity such as `jev-build-20261024` is accepted.
The local token format for model names is `jev-` followed by an ASCII letter or
digit, then ASCII letters/digits or `.`, `_`, `+`, `-`, with at most 128 total
characters. This is a local restriction, not an upstream naming rule.

A response model must be admitted by the account-name list or served-version
evidence. If the requested name is an evidenced concrete version, the response
must match it exactly. Otherwise an alias request may return that same alias or
an explicitly allowed concrete version. It cannot silently switch to another
alias. Concrete response names need not occur in the account alias catalog.

An observed admitted name is recorded as `actual_model`; its concrete version
is recorded only when it appears in `allowed_versions`. Alias-only answers retain
`actual_model_version: "unknown"` and cannot be cached. Missing or unadmitted
identity remains unknown. An admitted version observed during a pin mismatch can
remain visible for diagnosis while the response is rejected. No identity is
filled in from the requested model.

## Credit and optimizer gates

Both authorization flags and reservation `recorded` require JSON literal `true`.
False, numbers, strings such as `"true"` or `"unknown"`, null and NaN do not
establish permission. Coverage and budget references must be nonempty. Unknown
existing allowance coverage continues to block live inference before key access.

All accounting amounts are finite nonnegative numbers. The current reservation
amount and approved limit must be positive. Booleans, negatives and unknown
quantities block. All cost amounts use one declared unit. Supply a conservative
upper reservation established outside the helper; it has no price estimate or
live credit query.

`spent` is settled usage. `pending` is unsettled consumption not also represented
in `active`. `active` is the complete list of outstanding recorded reservations,
including this request exactly once with its matching id and amount. Duplicate
ids block. Admission requires:

```text
spent + pending + sum(all active amounts) <= approved_limit
```

Exact rational arithmetic on decimal representations prevents a small commitment
from disappearing at the allowance boundary. For `purpose: "optimization"`,
also supply this field, with actual approved budgets and commitments:

```json
{
  "optimization_budget": {
    "state": "within20",
    "model": {"approved": 100, "spent": 10, "pending": 5, "active": 4, "reservation": 1},
    "time": {"approved": 200, "spent": 20, "pending": 10, "active": 5, "reservation": 5}
  }
}
```

These are separate measurable approved project budgets. Model amounts use the
cost reservation's unit; time amounts use seconds. Each dimension describes
optimizer usage only: `active` excludes the new request, whose `reservation` is
added separately. Model `reservation` must equal `cost_reservation.amount`.
For both dimensions, approved and reservation must be positive and:

```text
optimizer spent + pending + other active + current reservation <= 0.20 * approved
```

The literal `within20` alone is insufficient. Missing quantities, overruns,
invalid types and an understated model reservation block. Wider optimizer
milestone counts, publications and completion events remain the integrator's
responsibility.

## Runtime CLI and Python API

These PowerShell examples run from the repository root. Execute examples show
the interface only; they do not establish permission or credit coverage:

```powershell
# Offline validation; no credentials or network.
python -B skills/research-navigate/scripts/jev_decide.py packet.json

# One explicitly authorized POST, with a durable execution receipt.
python -B skills/research-navigate/scripts/jev_decide.py packet.json --execute --receipt decision-1.receipt.json

# Alternate Magpie file, still read only at runtime.
python -B skills/research-navigate/scripts/jev_decide.py packet.json --execute --receipt decision-1.receipt.json --providers path/to/providers.json --timeout 30

# Explicit second attempt after a recorded known failure.
python -B skills/research-navigate/scripts/jev_decide.py packet.json --execute --receipt decision-1.receipt.json --retry

# Reuse a completed receipt after current concrete-version verification.
python -B skills/research-navigate/scripts/jev_decide.py packet.json --execute --receipt decision-1.receipt.json --verified-model-version jev-1.13.0
```

Dry-run is the default. `--execute` selects the execution/cache path; a matching
cache hit makes no POST. `--timeout` is a per-socket-operation timeout in seconds,
default 30, at least 0.001 and at most 120. It is not a total wall-clock deadline.
There are no redirects, environment proxies, endpoint overrides, hidden retries
or provider fallback.

Credentials are resolved only at runtime from the unique Magpie provider with
`id: "typesafe"`. The canonical field is `key`. Legacy `apiKey` is accepted only
when `key` is absent, or both fields contain exactly the same valid value.
Conflicts, mixed invalid values and an invalid canonical value block; they never
trigger a silent fallback. The credential must be a nonempty ASCII string with
no whitespace or control characters. The requested model must appear in the
provider's string-array `models`.

The default file is `~/.config/magpie/providers.json`; `--providers` changes only
the path. The file is read, never modified. No environment-variable key fallback
exists. Provider base URLs are ignored. Never place credentials or headers in a
packet, shell text, reference, receipt or handoff.

The CLI prints one compact ASCII JSON result and exits 0 for `dry_run`,
`completed` or `cache_reused`; other outcomes and argument errors exit 2.
Optional dry-run `--receipt` creates a new file and refuses to overwrite an
existing one. Keep dry-run receipts separate from execution journals. Execute
requires a receipt path and a writable existing parent directory. Use the same
persistent execution receipt per decision across invocations; do not remove it
to repeat a decision.

An importing coordinator can load the module by file path and call:

```python
decide(packet, *, execute=False, providers_path=None, receipt_path=None,
       retry=False, verified_model_version=None, timeout=30, transport=None)
```

The result is the same JSON-compatible object printed by the CLI. Production
callers leave `transport` unset. For offline tests its signature is
`(wire_request, runtime_key, timeout) -> decoded_response`.
`validate_packet(packet)` returns the validated wire body or raises fixed-code
`Invalid`. `parse_response(response, request, supported_models,
served_model_evidence)` returns `(outputs, usage, actual_model)` after strict
validation. `decode_json` additionally rejects duplicate keys and nonstandard
nonfinite constants.

## Receipt, failures, retry and reuse

Receipts contain id, stage, purpose, reservation id/amount/unit, requested model,
observed admitted actual model, evidenced concrete version when present, valid
unaltered outputs, usage, attempts and execution status. They include SHA-256
fingerprints of the exact packet, normalized wire request, evidence manifest,
candidate manifest, served-model evidence, and criteria/revision/abstention
bundle. They omit state, credentials, headers and provider error bodies. Score
legends preserve supplied descriptions; choose receipt storage accordingly.
Later adoption belongs in a separate integrator record carried with the handoff.

| Execution status | Commitment state | Interpretation |
| --- | --- | --- |
| dry_run | not_started | Local declarations validated; no key or network access |
| in_flight | pending | Saved before transport; interrupted completion is unknown |
| completed | consumed_unreconciled | Valid output; retain cost until external reconciliation |
| known_failure | released | Explicit HTTP rejection; no automatic retry |
| completion_unknown | pending | Timeout, network ambiguity, redirect or server error |
| invalid_response | pending | Missing/invalid output or identity; no assumption of zero charge |
| blocked | preserved when a matching journal was read | No additional attempt permitted |
| cache_reused | consumed_unreconciled | Verified completed result reused without a new call |

The execution journal is locked for cooperating Windows/POSIX writers and flushed
with `fsync` before transport. No request is sent if that save fails. Concurrent
calls or corrupt/torn journals block. Final writes use the same lock. If the
process is interrupted after sending, the previously saved pending commitment
remains. Failure to read a journal does not prove that its commitment is zero;
consult the saved record before changing external accounting. A blocked result
does not replace the existing journal. Dry-run never overwrites it.

Only HTTP 400, 401, 403, 404, 405, 413, 415, 422 and 429 are treated as known
rejection. HTTP 429 returns `rate_limited`; Retry-After and raw error text are not
followed or logged. Other HTTP outcomes, including redirects/server errors,
conservatively retain pending commitments. Timeouts and transport exceptions
return fixed sanitized codes without exception messages. Malformed responses
expose no raw provider text. Credential echoes are rejected, and runtime receipts
defensively redact the resolved credential.

After a matching journal records one known failure, `--retry` allows a second
attempt. Nothing retries in the same invocation. A third attempt, implicit second
attempt, retry without a known failure, or retry of pending/unknown completion
is blocked. Re-establish the same reservation and sufficient allowance externally
before retrying. Do not delete, replace or rename a journal to bypass its history.

Cache reuse requires the identical full packet fingerprint and an explicit
current `--verified-model-version` matching the saved concrete actual version and
the packet's `allowed_versions`. Outputs are validated again. This applies even
to pinned requests; an alias-only response cannot be reused. `cache_reusable`
becomes true only on successful verified reuse. A moving alias, elapsed time,
a semantic-version-looking name or a previous result cannot establish current
identity. Version evidence and alias catalog changes alter the packet fingerprint
and block old receipt reuse. Prepare a new authorized decision if necessary;
the adapter never silently calls again using the old journal.

## Limits of local declarations

The helper proves types, arithmetic, exact matches and its own journal
transitions. It cannot independently establish real balances, billing coverage,
consent, catalog freshness, alias mapping, complete commitments, evidence
authenticity, candidate fairness or scientific correctness. References,
`served_model_evidence` and `--verified-model-version` are local attestations.
The adapter never fetches a catalog or runs calibration to substantiate them.
An account alias catalog alone is insufficient concrete-version evidence.

The file lock is not a global atomic quota ledger, remote idempotency key,
tamper-proof receipt or guarantee on arbitrary shared filesystems. External
accounting must atomically reserve shared allowances and include pending and
consumed-unreconciled records. Receipt deletion, edits or new paths defeat local
attempt history. Hashes bind supplied manifests, not unseen referenced files.
A torn journal requires reconciliation, never an automatic repeat inference.

Upstream usage is token counts, not settled charges. The supported request
schema provides no server-enforced cost cap or output-token reservation.
Conservative model/time reservations and reconciliation are external duties.
A socket timeout does not prove remote work stopped. Live inference remains
blocked while existing allowance coverage is unknown. No text-worker, proof,
scientific adoption, deployment or external-action authority is created here.

Module-only offline verification:

```powershell
python -B -m unittest discover -s tests -p test_jev_decide.py -v
```
