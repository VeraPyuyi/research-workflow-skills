# Research Workflow Skills — Codex-native edition

Eighteen portable research workflows for LLM, Agent, DL, RL, causality and useful
research products. The runtime profile is `codex-native`. Install the whole suite:
stage skills share sibling-relative scientific contracts and references.

This edition uses exactly `gpt-6.1-sol`, `gpt-6-astra` and `gpt-6-luna` through the
host's native multi-agent tools. It reads no other-runtime model-routing
configuration. It offers optional standalone Jev structured decision assistance as the sole external
inference service. Jev is separate from generative workers and all scientific reviews.
A current chat or gateway identity does not establish direct native dispatch.
Actual host capability and identity observations must be recorded separately from
requested model names. No inference or model calibration is needed to install,
validate or run the offline helpers.

## Start with the actual task

```text
$research-navigate Continue from this protocol, handoff and experiment record.
$research-survey Close-read this paper and distinguish evidence from claims.
$research-survey Map useful cross-disciplinary theories and their transfer assumptions.
$research-ideate Formalize candidate questions and attempt useful derivations.
$research-design Design a fair study for this approved question.
$research-analyze Audit this paper's contributions and prioritize the next research round.
$research-review Independently check the actual proof, evidence and reuse conditions.
$research-focus Recover the main theme, assess cumulative drift and bound side branches.
$research-optimize Preserve strengths and evaluate bounded workflow improvements.
$research-product-discover Define a useful product, target users and bounded MVP.
```

Direct stage requests stay bounded; a paper reading does not start a full project
or create a Goal. Inspect supplied artifacts, preserve valid decisions, continue
within existing authorization and communicate in the user's preferred language.

| Area | Skills |
| --- | --- |
| Navigation | `research-navigate` |
| Preparation | `research-scope`, `research-survey`, `research-ideate`, `research-design` |
| Evidence | `research-baseline`, `research-implement`, `research-experiment`, `research-analyze` |
| Manuscript | `research-write`, `research-review`, `research-submit` |
| Product | `research-product-discover`, `research-product-build`, `research-product-release`, `research-product-maintain` |
| Main-line maintenance | `research-focus` |
| Improvement | `research-optimize` |

## Preserve the research main line

Keep a versioned `research_focus` record separating the stable user-governed
theme from the evidence-adjustable paper thesis. Recover original instructions,
record provenance gaps, and compare cumulative pivots with that same theme.
Within explicit delegation and existing resources, useful in-theme changes may
proceed. New theories, counterexamples and negative results can serve the main
question; convenient tooling alone cannot replace it. Bound auxiliary branches
by their claim link and return condition. Carry a short reminder at handoff and
consolidate alignment at M1-M5, without new per-edit agents or tests. Internal
anchors stay out of blind reviews; focus and optimizer events never recurse.

## Preserve scientific substance

For open research directions, survey relevant disciplines, record structural
correspondences and transfer gaps, formalize definitions, attempt useful proofs or
counterexamples, then run bounded informative checks and formal experiments.
Theory first allows small authorized calculations and empirical tests with
incomplete proofs. Empirical replication need not invent a theorem; pure theory
need not invent experiments. A successful experiment cannot prove a universal
statement. Preserve proof, conjecture, assumption and observation status.

For method research, trustworthy baselines generally precede substantial new-method
development. New benchmarks and empirical studies need implemented, calibrated
measurement infrastructure before reference runs. Keep data/splits, seeds, code,
protocol versions and failed/negative attempts visible. Review source support,
statistical/causal validity and the actual derivation, not only an author summary.

Reuse prior theory, methods or implementations only after checking applicability,
quantifiers, assumptions, licensing and equivalence. Record direct reuse, needed
arguments and analogy-only cases. Simplification must preserve citations and
contribution boundaries. A theorem cannot justify removing experiments that test
implementation fidelity or application assumptions the theorem does not establish.

Contribution analysis covers known project-related local and configured-server
evidence, distinguishing discovery, inspection and inaccessible material. Audit
strengths, gaps and redundancy, develop evidence-linked explanations and compare
theory, experiment and analysis opportunities by actual costs and learning value.
Carry a versioned next-round package through needed stages and back to analysis.
Preserve valid authorization and do not run until a preferred outcome appears.
Acceptance requests yield evidence-based risks and priorities, never invented
acceptance probabilities or guarantees.

## Native dispatch and review

| Work | Exact requested model |
| --- | --- |
| Default integration, engineering, experiment control and writing | `gpt-6.1-sol` |
| Hard mathematics, causality, scientific and contribution review | `gpt-6-astra` |
| Bounded extraction from inspected source material | `gpt-6-luna` |

The host tools are `multi_agent_v1.spawn_agent(model, reasoning_effort, message,
fork_context)`, `multi_agent_v1.wait_agent(targets, timeout_ms)` and
`multi_agent_v1.send_input(target, message, interrupt)`. Verify current host
schemas, model allowlist, supported effort, context/modality, data permissions and
resource authority before dispatch. Use exact bare IDs and explicit supported
reasoning effort. Unsupported requests remain unexecuted; do not silently
substitute another model service. Model roles are task assignments, not benchmark
claims or guarantees.

Use disjoint output scopes and one integrator for shared artifacts. Global active
workers are limited to six; all three native models share one Codex pool with two
workers when confirmed and one when unknown. Effective parallelism here is at most
two, further bounded by live capacity. The coordinator owns the global inventory,
atomic reservations and dispatch. A timed-out or cancellation-requested job keeps
its commitment until reconciled. Do not launch a duplicate or infer completion.

The offline `skills/research-navigate/scripts/check_dispatch.py` checks snapshots
and prints an exact native spawn request plus canonical request digest. Blind review
requires an explicit canonical absolute `submission_root` and existing regular
allowlisted files. Unsafe raw path components, aliases, symlinks and reparse points
are rejected. The neutral reviewer message contains absolute allowlisted paths;
input contents are hashed into the admitted request.

After spawn, persist a separate coordinator dispatch record containing the task
ID, admitted request digest and the agent ID actually returned by spawn. Completion
must match that record, task and digest; replayed or mismatched receipts never free
capacity or pass review. Live inventory changes do not readmit a running task.
The checker never executes, reads model-service credentials or reserves quota. Requested and actual model identities remain
separate. Unknown actual identity or completion cannot certify independent review
or free capacity. See `skills/research-navigate/references/model-routing.md` for the
packet/receipt contract and explicit limits of local attestations.

Review ownership is assigned at substantive stages; execution is consolidated at
milestones. Fresh agent context and different model identity are separate facts.
Same-model reviewers can share bias; an expressly documented context-only check
never passes a required model-independent gate. Native candidate decisions follow
inspected evidence and program constraints, bounded native comparison when useful,
then an integrator decision with reasons. Model opinions are not proof, measured
improvement or authority to submit/release.

## Optional standalone Jev assistance

The optional `skills/research-navigate/scripts/jev_decide.py` adapter supports
structured Choice/Score/Noul candidate comparisons at one fixed Typesafe endpoint.
It reads `TYPESAFE_API_KEY` only on explicit execution. Optional `--config` accepts
exactly `api_key_env` and an explicit Jev model whitelist; the default permits only
`jev-latest`. No inline keys, endpoint overrides, other-runtime configuration reads
or generative Jev dispatch are supported. `config/jev.example.json` is portable.

A key does not prove available credit. Current Jev credit is **unverified**. The
adapter requires separate credit/budget authority, current version evidence,
recorded cost reservation, a shared dispatch snapshot and a durable receipt before
sending. Jev's own unknown pool stays at one; service tasks also count toward the
global six. Native workers still share Codex capacity of two when confirmed and
one when unknown. Missing key, unknown credit or an unavailable API returns native
evidence comparison as fallback without blocking other authorized research.
Uncertain service attempts retain commitments and cannot be retried automatically.

The adapter preserves validated raw outputs/usage, locks and flushes receipts before
transport, allows at most one explicit retry after a known failure and requires
current concrete-version evidence for cache reuse. Returned service distributions
are not scientific truth or acceptance probabilities. Jev cannot satisfy any
independent or optimizer publication review. No live call or credit verification
was performed. See the navigator's `references/decision-support.md` for the full
packet, authorization, receipt and fallback contract.

## Full-paper Goals and M1–M5

Only an explicit user instruction enables a native Goal. At startup, bind the
actual topic, venue/year/track, resources, delivery criteria and any delegated
in-scope protocol/conclusion authority. Continue authorized dependencies without
stage-by-stage approval. A partial draft, routing package, exhausted budget or
inaccessible required evidence does not complete a paper Goal.

On explicit activation, bind the native Goal immediately and record the actual
tool result. At a completed stage, start the next authorized dependency; a
blocked branch does not stop independent work. Save actual next-action state,
job commitments and valid coverage for native continuation. A workflow release
does not itself activate Goal or reload an already-running context.

1. M1: research/protocol and scientific assumptions.
2. M2: integrated implementation, measurement/baselines and pilot.
3. M3: evidence, principal conclusions and contribution audit.
4. M4: complete frozen manuscript and first fresh-context venue review.
5. M5: revised paper, second fresh-context venue review, repairs and delivery.

M4 and M5 each use a newly spawned agent with `fork_context: false`. Both receive
only the frozen submission, permitted attachments and verified venue criteria.
Round two uses a different agent and never sees round-one reports/replies, project
history or optimizer records. Keep producer provenance and reviewer IDs in
coordinator-only records. Check actual input contents and report instruction-only
isolation when stronger host restrictions are unavailable. Adjudicate findings
against evidence and recheck affected repairs; no automatic third review loop.
These are simulated reviews, separate from actual external peer review.

Deliver the actual submission-ready manuscript and venue-appropriate reproduction
package, distinguishing required submission material, recommendations, optional
artifact evaluation and post-acceptance duties. Full training reruns are not
automatic. Native Goal completion requires actual delivery acceptance and both
reviews under the agreed contract. External submission and public release retain
their own authority.

## Bounded workflow improvement and releases

Every substantial stage records one stable retrospective event with strengths,
evidence-backed weaknesses, artifact references and actual cost. Duplicates are
idempotent; the optimizer does not trigger itself. At M1–M5, freeze goals, authority,
criteria, baseline and held-out coverage outside candidates. Optimization stays
within 20% of existing measurable model/time allowances including spent and
reserved amounts. Independent publication review requires Sol or Astra; Luna
extraction and Jev comparison are supporting evidence only. Compare at most three candidates, revise each once and publish
at most one validated combined version per milestone. Preserve failed candidates,
protected strengths and rollback conditions. Optional optimization never delays
a paper that meets its delivery contract.

`optimize_workflow.py` records events, reservations, actual evidence, independent
review and eligibility; it does not deploy. `workflow_release.py` handles compatible
validated release metadata and explicit project adoption, preserving customized
copies, opt-outs and running job version pins. Runtime profile is part of release
identity. A profile change needs explicit recorded switching authority, separate
from an ordinary compatible update. The shared release helper retains migration
support for other profile metadata; that support performs no model calls or
external configuration reads.

The release metadata binds the `codex-native` profile to the packaged content.
The supplied release receipt covers the recorded code, workflow-control and
installation checks; it does not certify unverified live channels or scientific
results. Load updated instructions at supported entry/resume/handoff boundaries;
there is no background scheduler or hot injection.

## Validate and use portable configuration

Python 3.12+ and PyYAML are required by the suite helpers. Optional SSH support
uses `requirements-ssh.txt`. From the bundle root:

```text
python -m pip install -r requirements-dev.txt
python -B scripts/validate_skills.py
python -B -m unittest discover -s tests -p test_dispatch_guard.py -v
python -B -m unittest discover -s tests -p test_model_routing.py -v
python -B -m unittest discover -s tests -p test_optimizer.py -v
python -B scripts/install_skills.py --target <chosen-skills-directory>
```

The installer command is a dry run; an authorized installation additionally uses
`--apply`. It checks conflicts before copying, preserves unrelated/customized
skills and refuses differing same-name directories. No installation or personal
configuration change is needed for offline validation. Install all eighteen
skills together for local reference closure.

`config/` contains portable examples for native dispatch, workflow runtime and
an optional experiment host. They are templates, not current authorization,
capability observations, verified identity, live quota records or ready server
credentials. Copy to a private project-selected location, replace placeholders
with inspected values and keep private profiles/results outside distributable
artifacts. Example dispatch write scopes are project-relative placeholders; the
checker requires resolved absolute paths at execution. No machine-specific path,
private host, password, API token or raw research result is shipped.

The shared experiment adapter preserves pinned SSH host keys, credential
references, atomic CPU/RAM/GPU reservations, stable job identities, recovery,
required outputs and unknown-state reconciliation. Its optional credential backend
uses Windows Credential Manager; model routing does not read that store. Host
jobs pin workflow/protocol/code versions; workflow adoption does not edit active
runs. A reservation is conservative admission guidance, not operating-system
resource isolation. Consult `skills/research-experiment/references/shared-server.md`.

Offline structural and synthetic tests establish only their checked contracts.
They do not prove scientific correctness, reviewer quality or a completed
experiment/paper. Behavioral scenario fixtures are synthetic and are kept
separate from held-out rubrics. See [release validation](docs/release-validation.md)
for final test counts, real native calls and their identity/isolation limits.
The [review disposition](docs/review-disposition.md) records the integrated
review findings and their verified repairs.

[Research-focus release validation](docs/research-focus-validation-20261025.md) records the 18-skill checks and their limits.

## Goal recovery and submission privacy

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

[Goal/content-audit validation](docs/goal-leakage-validation-20261025.md) distinguishes offline acceptance from pending live recovery.
