---
name: research-navigate
description: Use when starting, resuming, or coordinating multi-stage AI research, a full-paper Codex Goal, or a research-product project. A direct request for one research stage belongs to that stage skill.
---

# Research Navigator

Advance the user's requested outcome from the actual project artifacts.
Coordinate the stages; leave their scientific work to the stage skills. For a
full-paper request, a useful next work package is an intermediate step.

Read the [workflow contract](references/workflow-contract.md) and
[stage map](references/stage-map.md). Select relevant references through the
[domain index](references/domains/index.md); do not load every domain by default.
Read [model routing](references/model-routing.md) when assigning work packages,
native execution branches, independent reviews or parallel workers. Read
[reuse and simplification](references/reuse-and-simplification.md) when existing
theory, methods, implementations or results may replace or simplify current work.
Read [workflow updates](references/workflow-updates.md) at entry, resumption or a
handoff to adopt a compatible validated suite release.
Resolve all reference paths relative to this skill's directory.

At project entry/resumption, use [research-focus](../research-focus/SKILL.md)
to recover the stable theme and current thesis from original instructions and
explicit decisions. Carry its compact reminder in scientific task packages.
Compare cumulative pivots at M1-M5; ordinary handoffs need only an alignment note.
An evidence-backed in-theme pivot within delegated scope/resources can proceed.
Changing the theme or an explicit boundary needs the user's concrete decision.

For a full-paper task or explicitly enabled native Goal, read
[Goal execution](references/goal-execution.md). The endpoint is a submission-ready
paper and venue-appropriate reproduction package, not the next route or outline.
Preserve bounded stage requests; selecting this skill alone does not create a Goal.
When the user explicitly asks to enable or resume a paper Goal, perform the native
Goal binding at entry, record the actual tool result, and then advance the project.
Do not turn that request into only a plan for enabling Goal later.

## Route from evidence

1. Inspect the supplied brief, protocol, decisions, sources, code, runs, manuscript
   or product artifacts. Distinguish existing, verified, stale and absent material.
   A new chat is not evidence that a project must restart.
2. Identify the requested outcome and study type: method, experiment, evaluation,
   empirical analysis, theory, a combination, or product. Combine relevant domain tags.
3. Find the smallest missing dependency for the next outcome. Preserve valid
   previous decisions. Skip irrelevant stages with a reason.
4. For method studies, arrange minimal evaluation support, baseline verification,
   then substantial new-method implementation. For new benchmarks or empirical
   studies, arrange measurement implementation and calibration before baselines.
   For open theoretical/method directions, route structural literature connections
   to survey, formal candidate work to ideate, and selected derivations/validation
   to design. Carry theory revisions and proof status; do not restart an approved
   topic or impose a completed-proof gate on approved empirical tests.
5. Identify the next applicable human decision and any resource/permission blocker.
   Advance already authorized work. Do not treat every handoff as a new approval.
   At a real candidate choice, use inspected evidence and hard program constraints,
   then a bounded native comparison and an integrator decision; see
   [evidence comparison and optional Jev](references/decision-support.md).
   Jev has no proof or gate authority, and unknown account coverage means no call.
6. For substantive work, assign a native executor, milestone review ownership and an
   integrator from the model map. Consolidate review at the applicable milestone;
   do not dispatch a reviewer after every branch or edit. Check model access, effort, context,
   modality and data restrictions. Split independent branches; reserve shared
   resources and non-overlapping write scopes. Route to the matching stage using
   the host's supported skill mechanism, or name the next skill with its input
   package when dispatch is unavailable. Do not claim to have invoked a tool,
   model or stage that did not run.
7. For full papers, use M1 research/protocol, M2 implementation/pilot, M3 principal
   conclusions, M4 first venue review and M5 revised-paper review/delivery.
   Reuse valid coverage; reopen only affected checks. Review findings return to
   their stage. Existing startup delegation covers in-scope decisions; scientific
   review never authorizes submission or release.

For contribution-improvement requests, preserve the shared round package and
coordinate analyze -> needed design/implementation/experiment -> analyze.
Advance feasible authorized stages while the requested loop remains in scope.
Carry actual artifacts and consumption back into the same round. A completed
round closes that round; in a paper Goal, select and execute the next dependency.
An unavailable input, reviewer or resource blocks its dependent work, not every
other authorized stage. A bounded request retains its own completion boundary.

## Continue under existing authority

Plan internally and keep advancing work already covered by startup delegation, the
current round package and the approved resource envelope; a stage transition does
not require fresh approval. The user's milestone check cadence takes precedence
over generic advice to run a reviewer or a full suite after every task: queue
findings for the applicable milestone. Switch native Plan mode only when the host
provides that operation; otherwise plan within execution mode and continue.
Create or reuse a native Goal only under explicit user authorization and the
actual Goal tools. Preserve the project handoff if native support is unavailable.

At entry, resumption or a handoff, adopt a compatible validated suite release
through [workflow updates](references/workflow-updates.md) under recorded
automatic-update authority. Running jobs keep their pinned versions and
independently customized local copies are never overwritten.
After adopting a release, actually read its affected instructions. A release
record alone neither reloads an old context nor activates a native Goal.

Each substantial scientific stage completion queues one stable event for the sibling
[research-optimize](../research-optimize/SKILL.md) skill, carrying strengths,
weaknesses, artifact/evidence references and actual cost. Use its bounded event
and milestone protocol; an event alone triggers no comprehensive review or tests.
Optional optimization never delays a paper that meets its completion contract.
Focus/optimizer bookkeeping emits no new support event. The focus record's
scientific task mapping is maintained by the integrator, not a recurring reviewer.

## Deliver

Provide current objective and artifact status, missing/stale dependencies,
recommended stage and work package, applicable decision, and the shared handoff.
The package includes inputs, intended outcome, accepted constraints, evidence
needed for completion, executor and reviewer assignments, requested/actual model and
effort, resource-pool accounting, parallel branches, write scopes, and the next
decision if any. If an exact model cannot be dispatched, label the work
unexecuted and provide a compatible package rather than inventing a result.

An existing benchmark with approved tasks but no evaluator goes to
`research-implement` for measurement infrastructure, then `research-baseline`;
it does not restart topic selection.

A routing-only request is complete when the next action and prerequisites are
unambiguous. A continued-research request also needs actual round progress or an
explicit unmet prerequisite. Routing completion is not completed scientific work.
For a full-paper Goal, keep advancing authorized dependencies until its delivery
contract is met or a genuine limit prevents progress. Save the compact milestone
handoff for continuation, including the next action actually started or the exact
dependency preventing it. A phase report is an internal checkpoint. Follow the
[continuation procedure](references/goal-execution.md#stage-to-stage-continuation)
before ending a turn; do not finish the Goal merely because this stage ended.
