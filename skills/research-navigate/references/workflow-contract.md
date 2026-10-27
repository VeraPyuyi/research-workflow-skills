# Shared Research Workflow Contract

Read this once for the current task; revisit the relevant section after a material
change. Every stage in this suite uses this contract. The suite must be installed
together because stage skills refer to these files by sibling-relative paths.
If a required reference is unavailable, report the missing dependency and limit
work to supported preparation rather than inventing the missing guidance.

## Scope and entry

Honor the user's requested outcome and existing authorization. A one-paper
reading, a bounded analysis, or a local bug fix does not require a new full project
or every approval gate. Inspect supplied artifacts before asking for discoverable
facts. Ask only for decisions or missing inputs that materially affect the work;
continue independent useful preparation.

Use existing storage and tool conventions. If none are selected, deliver
portable Markdown/text and data tables in the conversation or the user's chosen
workspace. This is a fallback representation, not a new mandatory backend.
Never require a specific citation manager, experiment tracker, cloud, model
provider, manuscript format or compute platform merely to use a stage.

Skills are instructions, not a background scheduler or a persistent database.
Record progress in explicit artifacts; do not rely on another chat remembering
this conversation. If an execution or storage capability is unavailable, prepare
the actionable package and identify what has not actually happened.

For substantive model-assisted work, use the
[model routing guide](model-routing.md). Keep the free execution, independent
milestone review and integration roles visible, record requested and actually served model
and effort, account for shared quota pools, and state any skipped free route.
Model consensus is not independent scientific evidence. Exact-model dispatch must
match the host's actual allowlist; otherwise the package remains unexecuted.

## Logical project records

Use stable identifiers or unambiguous references appropriate to the existing tool:

| Record | Minimum decision-relevant content |
| --- | --- |
| Brief | Question, study type, users/audience, assets, constraints, success and stopping conditions |
| Decisions | Decision, actual user instruction, scope, relevant revision, resources, unresolved conditions |
| Literature | Identity, source, version/date, inspected portion, supported claim, limitations |
| Theory, when relevant | Definition/assumption revision, source results, statements/derivations, gaps/counterexamples, actual check status and linked validation tasks |
| Protocol | Question/hypothesis, measurement, data/splits, controls, analysis, budgets, stopping/retry limits |
| Runs | Attempt/job identity, code/data/config versions, environment, raw artifacts, status and consumption |
| Analysis | Included/excluded attempts with reasons, transformations, aggregation, uncertainty, claim mapping |
| Paper | Manuscript revision, source references, figure/table provenance, review issues and resolutions |
| Product | Need evidence, approved MVP, research boundary, acceptance, tested candidate and release target |
| Dispatch | Stage, requested/actual model and effort, free status, quota pool, dependencies, write scope, review and fallback |
| Full-paper Goal, when requested | Native binding, completion contract, startup authority, milestone, valid/stale coverage, venue-profile revision and two review-round records |
| Submission content audit | Exact artifact hashes, nested/member/metadata coverage, redacted findings, scoped exceptions, manual/rendered checks and unresolved gaps; private author-side record, excluded from blind inputs |
| Workflow improvement | Stable stage event, retained strengths, weaknesses, cost/commitments, frozen criteria, candidate outcomes, review and release/adoption references |
| Decision assistance, when used | Candidate/evidence/criteria versions, requested and served identity, raw structured outputs, usage, final choice and evidence-based disposition |

Do not create empty records for irrelevant stages. Link existing records instead
of copying their contents into every handoff.
For claim-bearing work, use the compact fields in
[the evidence ledger](evidence-ledger.md): keep claim location/revision, source
locator and inspected extent, conditions, evidence state, gap reason and next
check. Preserve bibliography verification separately from claim-support checks.

## Six human decisions

| Decision | Reviewable package | When it is required |
| --- | --- | --- |
| Topic | Compared questions, contribution, evidence, feasibility, recommendation | Committing a research direction |
| Protocol/resources | Method/study design, controls, validity checks, analysis, cost and stop/retry limits | Executing the research plan or materially expanding it |
| Main conclusions | Claim-evidence map, alternatives, uncertainty, scope and limitations | Adopting principal findings as the project's conclusions |
| Submission | Exact intended manuscript/attachments, authors, destination and actual action | Sending a paper or revision externally |
| Product/MVP | Users, evidence of need, scope, value, resource and acceptance plan | Committing a product build |
| Public release | Actual candidate, target, rights/provenance, validation and action | Making the relevant version/artifacts public |

A proposal, a draft, an AI review, or silence is not a user decision. Existing
explicit authorization is sufficient when its target, material content, scope and
resources still match. Record and reference it instead of asking again.
Only affected decisions reopen after material changes: new scientific claims,
changed authors or destination, changed evaluation/identification assumptions,
expanded resources/MVP, or different published assets. Routine edits within
approved scope do not invalidate everything.

Package the recommendation, evidence, alternatives, consequences and exact open
decision. Keep preparing independent authorized work while a decision is pending.
Authorship choices, third-party rights, submission and public release must reflect
actual user decisions and applicable verified conditions.

For an end-to-end paper, explicit startup delegation may cover protocol refinement,
evidence-based conclusion formation and writing within an agreed topic, venue,
resource envelope and completion contract. Record that authority and do not ask
again for each in-scope protocol or principal finding. The six decision categories
still identify ownership, not six mandatory interruptions. Material changes reopen
only affected decisions. Review is due at milestones, not every intermediate claim.
See [Goal execution](goal-execution.md) for lifecycle and exact completion conditions.
Chat activity and native Goal status are distinct: sending a follow-up does not
reactivate a blocked Goal. Apply the supported lifecycle recovery only under
explicit user authority, preserve the objective/budget, wait for an active writer
to finish, and separately observe a later automatic Goal turn before claiming
unattended continuation.

## Continuing under existing authority

Make internal plans and keep advancing work already covered by startup delegation,
the current round package and the approved resource envelope. Crossing a stage
boundary inside that scope does not require fresh approval, and waiting for a
decision is not a pause. The user's milestone check cadence takes precedence over
any guidance in this suite that asks for a reviewer or a full suite after every
task; queue findings for the applicable milestone instead.

Use native Plan transitions only when supported; otherwise plan within execution
mode and continue authorized work. Native Goal creation requires explicit user
authorization and actual Goal tools. When those tools are absent, preserve the
project handoff without claiming native activation or background continuation.
For an explicit paper Goal request, bind it through those tools at entry and
retain the actual result. A completed stage, failed optional branch or prepared
next-round package does not end the paper task. Apply the
[stage-to-stage continuation procedure](goal-execution.md#stage-to-stage-continuation):
execute the next authorized dependency, and scope blockers to their dependent work.

At entry, resumption or a handoff, inspect the current suite and adopt a
compatible validated release under recorded automatic-update authority through
[workflow updates](workflow-updates.md). Running jobs keep their pinned versions;
independently customized local copies stay untouched and report a conflict.

Each substantial stage completion queues one stable completion event for the
sibling [research-optimize](../../research-optimize/SKILL.md) skill, carrying strengths, weaknesses, artifact and
evidence references, and the actual cost. That event triggers no full test suite
and no scientific review; the optimizer queues no event for its own completion;
and optional optimization never delays a completed paper. Optimization stays
inside 20% of the measurable approved model/time allowance, counting spent and
reserved amounts, with three candidates, one revision each and one publication per
milestone. Read `research-optimize` for its authoritative
bounds and record shapes rather than duplicating them here.

## Research main line

For an ongoing project, maintain `research_focus` through
[research-focus](../../research-focus/SKILL.md) and its
[anchor protocol](../../research-focus/references/thesis-anchor.md).
Keep the original/later user-approved `theme_envelope` separate from the
evidence-adjustable `active_thesis`. Recover instruction provenance, preserve
history, and mark gaps rather than treating the latest draft as the original goal.
This is not required for an unrelated single-paper reading or bounded calculation.

When the user delegates autonomous pivots within the theme, this specific policy
governs direction/method/assumption changes covered by that delegation: record
the evidence, value and affected coverage, then continue without a repeated vote.
Cross-theme changes, explicit locked boundaries, expanded resources and external
actions retain their decisions. No instruction here creates missing delegation.

At a stage handoff, relate the next task to the theme/current thesis and cumulative
pivots; use `on-spine`, `in-theme-pivot`, `auxiliary-only`, or
`out-of-theme-drift`. Carry a short reminder and a concrete claim link in worker
packages. Borrowed theory, engineering and calibration retain a bounded supporting
role unless evidence establishes a valuable on-theme contribution.
Keep evidence/proof and execution status separate from alignment.

Consolidate full alignment at existing M1-M5 checks. Internal review can inspect
the anchor; blind venue reviewers receive neither focus history nor internal
reminders. Focus/optimizer completion emits no new optimizer or focus event;
attach support notes to the original scientific stage's handoff instead.
Negative results and revised hypotheses can be on-theme. Do not lower the value
standard just to complete an easier paper.

## Check cadence

For full papers, consolidate checks at M1 research/protocol, M2 implementation and
pilot, M3 evidence/conclusions, M4 first complete-paper review, and M5 revised-paper
review and final delivery. Each substantial stage retains free execution and
independent review ownership, but intermediate work packages queue findings for
their milestone instead of automatically spawning reviewers or full test runs.
Bounded requests and product tasks retain their appropriate completion boundaries.

Reuse coverage for unchanged artifacts/dependencies. Routine edits do not trigger
full test suites, citation sweeps or whole-manuscript rereviews. Diagnose actual
failures promptly, recheck affected behavior and reopen only invalidated milestones.
Budget, permission and job-state admission still precede dependent execution.
Scientific experiments, proofs and counterexample searches remain research work.
M4/M5 use [fresh-context venue review](../../research-review/references/venue-review.md);
internal evidence audits may inspect project records, while blind reviewers may not.
Before M4/M5 dispatch and final packaging, apply the
[submission leakage audit](../../research-review/references/submission-leakage.md)
to exact sources, rendered outputs and all submitted attachments. A clean filename
list or regex scan is insufficient. Retain required AI-use disclosures and
scientific AI content; use relative paths/placeholders for private infrastructure.
Reuse unchanged audit coverage and recheck only affected surfaces after repair.

## Evidence and validity

- Separate observed results, source-reported claims, hypotheses, inferences and
  exploratory findings. Mark absent or inaccessible evidence.
- Verify source identity and inspect the primary material needed for a claim.
  Record when only metadata or an abstract is accessible. Search coverage bounds
  novelty claims; no search certifies universal novelty.
- Maintain a frozen measurement protocol for comparable runs. A material protocol
  change creates a new revision and identifies affected results/approvals.
- Retain failed, interrupted and negative attempts. State inclusion rules and
  exclusions. A failed run is not automatically a zero score or a removable row;
  the protocol determines its treatment.
- Record exploratory changes made after seeing outcomes. Protect the final
  validation set or explicitly disclose that independent confirmation is absent.
- Engineering correctness supports execution; scientific evidence supports
  research conclusions. Simulated user tests support only claims about simulation.
- A completed analysis can conclude insufficient evidence or recommend stopping.
  Do not keep running until a preferred result appears.

When prior theory, methods, benchmarks or implementations could replace project
content, apply the [reuse and simplification audit](reuse-and-simplification.md).
Check source conditions before reuse, preserve citations and proof status, and do
not delete experiments that supply evidence the reused result does not cover.

## Resources and resumption

Before consuming resources, identify approved limits and the actual environment:
time, money, API calls, GPU-hours, samples/interactions or other relevant units.
Include tuning, evaluation, retries and active commitments when relevant.
Unknown budget is an unresolved input, not unlimited authorization.

Reconcile job IDs, completed artifacts, pending work and resource use before
resuming. If job status is unknown, do not duplicate it. Query supported status
and cancellation controls; without them, report uncertainty and request the
necessary operator action. Do not promise a hard budget cap if the environment
cannot measure or enforce it.

Use bounded retries only for understood transient failures within the approved
allowance. Stop expansion on exhausted budget, unknown running commitments,
unavailable required access, or a failed validity check. Preserve logs and provide
the precise recovery prerequisite. Cancel active work only under applicable
authorization and supported control; never claim a cancellation without evidence.

## Theory materials and empirical evidence

For open-ended new directions and methods, prefer formal definitions and an actual
theory attempt before formal experiments. Bounded exploratory calculations and
counterexample checks can inform that attempt. Respect explicit empirical and
replication scope; pure-theory work need not acquire an experimental dependency.
Survey supplies cross-disciplinary source/assumption mappings, ideate develops
candidate mathematical prototypes, and design deepens selected arguments and
their validation. See the conditional
[mathematical guidance](../../research-ideate/references/mathematical-ideation.md)
when doing that work.

Keep optional theory materials in existing project records, with links from the
round/handoff rather than a new storage system. Separate content type and proof
status from the existing supported/limited/contradicted/unresolved evidence status.
Record whether a source statement or its proof was inspected, whether a project
argument is partial or complete, and the actual independent or machine checks.
Do not equate an author-completed derivation or "supported" status with independent
verification. Numerical checks are evidence only for their checked scope.

Definition or assumption changes preserve the old revision and identify affected
derivations, experimental interpretations and paper claims. A counterexample must
meet the claim's hypotheses and violate its actual quantifiers/conclusion; an
out-of-domain run can reveal an applicability limit without refuting the theorem.
For theory-driven formal experiments, carry the problem, assumptions, statement
and proof status, validation target and approved protocol/resources. A remaining
proof gap does not by itself invalidate already authorized informative tests.
New principal theory conclusions use the existing conclusion decision. Core
assumption/resource changes reopen only the affected decisions.

## Research improvement rounds

When the request includes continued research improvement, use explicit rounds
linked to existing analysis and decision records. A bounded calculation or
analysis-only request does not authorize a full research loop.

Each round package contains:

| Part | Required information |
| --- | --- |
| Question/evidence | Round identity, contribution gap, competing explanations, claim/evidence versions and prior understanding |
| Main line | Theme/thesis versions or reference, cumulative alignment, task-to-core-claim link, auxiliary return condition and any proposed pivot |
| Action/rationale | Chosen work, expected learning, minimal discriminating check, inputs, responsible stage and dependencies |
| Resources/authority | Estimated cost or explicit unknown, remaining allowance and actual approval reference covering the action |
| Decision/stop | For support, refutation and inconclusive results: next action (continue, close or pivot) and expected-information-value rationale; completion, futility and resource stopping conditions |
| Actual outcome | Execution status, artifact/run identities, actual consumption or measurement limits, changed understanding and next action |

These are logical fields, not a new storage schema. Extend the existing records
and five-part handoff; reference them rather than duplicating contents. Stages
preserve the round identity, return actual artifacts and distinguish proposed
work from execution. A completed stage is not necessarily a completed round.

Advance feasible work already covered by the current request, protocol and
resources without a new approval at every stage transition. A recommended
experiment or proof does not authorize a materially changed plan. Consolidate
principal findings at M3 before adopting them as settled. Use existing startup
delegation when it covers conclusion formation; otherwise present the human
decision and continue independent authorized work while it is pending.

After each round, compare new evidence and understanding against the prior
revision. Use the agreed scientific completion and resource boundaries, not
"until positive" or a predicted reviewer score. A useful negative result,
explanation, boundary, theorem or evaluation asset can meet the contribution
goal. Recommend closure or a pivot when another round has no reasonable expected
information value. Preserve search/selection history and independent validation.
Cross-chat continuation uses the saved package; it is not a background scheduler.

## Required handoff

Paper-facing analysis, graphics and prose share the
[argument and display record](../../research-write/references/argument-and-figure-contract.md)
when applicable. Link its claim/data/analysis versions from existing handoffs;
do not maintain conflicting specifications in each stage. Target-width rendering
and claim/display consistency join the relevant M2-M5 check, without a new gate.

Record these five items at meaningful stage transitions, compactly and in the
user's language. An internal handoff does not require ending a full-paper Goal,
printing a long report after each edit, or requesting fresh approval:

1. **Artifacts:** exact deliverables or locations, and their relevant versions.
2. **Evidence:** sources, runs, transformations and verification actually used.
3. **Status:** completed, partial, proposed/unexecuted, blocked, or ready for review;
   distinguish stage completion from project completion and action authorization.
4. **Open issues:** remaining uncertainty, unavailable inputs, invalidated results,
   pending decisions or execution/resource limits.
5. **Next step:** concrete work package, appropriate stage, prerequisites, and any
   specific human decision.

In a full-paper Goal, also record whether that next step actually started, is
ready for the native continuation, is waiting on a named job, or needs a specific
decision. Keep stage status separate from paper status. Stage completion normally
hands control back to the navigator inside the ongoing Goal; it does not require
a new user message. Resume from valid evidence and checks instead of rerunning
them to demonstrate activity.

For a dispatched or parallel round, also state each branch's requested and actual
model/effort, free/paid status, actual artifacts, review status and unresolved
resource or dependency limits. A branch that was not run is `unexecuted`, not
evidence.

For resumption, carry the active round, latest artifact/definition/protocol
revisions, completed checks and coverage, open finding IDs, applicable approvals,
running job IDs and committed resources. Mark dependent results and prior reviews
stale after material changes. This compact context snapshot can link existing
records; it need not repeat every source or create a new file system.
For full papers also carry the Goal binding/completion conditions, M1-M5 node,
venue requirements and two review rounds. Native Goal statuses are distinct from
local stage statuses; follow the actual Goal-tool lifecycle before setting them.
Preserve the focus reference and short reminder across context recovery. A suite
update does not replace project themes, thresholds, valid results or job pins.

Use [the handoff example](handoff-example.md) for a compact representation. The
fields are the contract; exact headings and serialization are not mandatory.
