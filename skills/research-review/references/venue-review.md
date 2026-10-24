# Fresh-Context Venue Review

Use for a full-paper Goal's M4/M5 or an explicit simulated venue-review request.
This is adversarial scientific reading, not pressure to reject. Report strengths
as well as deficiencies. It is not actual journal/conference peer review.

## Prepare an isolated input bundle

Freeze the paper and intended reviewer attachments for the current round. Obtain
the target venue/year/track's authoritative reviewer criteria through
research-submit, including the source and inspected date. If criteria are missing,
provide only a clearly provisional general review; it cannot certify the promised
venue-specific milestone.

Supply only:

- The current manuscript and attachments an actual reviewer would receive.
- Verified target-venue criteria and a neutral task instruction.
- Public literature found during review, with actual source/access records.

Exclude project chat/history, internal experiment records not submitted, author
self-assessments, desired acceptance verdicts/scores, prior reviews and response
letters. Do not attach internal evidence ledgers or the coordinator's handoff.
Exclude optimizer events, candidate evaluations, native selections and internal
workflow-improvement records from both blind rounds.

Also exclude private `research_focus` anchors, pivot history and alignment
reminders. The coordinator assesses intent alignment separately; blind reviewers
judge the scientific question and contribution actually presented in the submission.
For anonymous venues, also remove identifying material required by the actual
policy. An abstract or author summary cannot replace the full paper.

Keep producer-model evidence, earlier reviewer IDs and review/response matrices in
coordinator-only records. The dispatch preflight packet is not the reviewer prompt.
Copy allowlisted artifacts into a dedicated review bundle. Declare its canonical
absolute `submission_root` in the coordinator packet, using forward slashes. Every
raw relative file reference must resolve to a distinct existing regular file
beneath it. Reject dot/empty/parent components, Windows device names, controls,
trailing dots/spaces, aliases and every symlink/reparse component. The checker
hashes files and emits absolute allowlisted paths in the neutral prompt, so a
fresh agent does not guess a working directory or search the project root. Check the actual contents for excluded material; filenames
and an `allowed_inputs` label alone do not establish clean inputs.

## Launch a new reviewer

Use a newly spawned agent with explicit `fork_context: false`, not a fork, resumed
author agent, research participant or prior-round reviewer. When supported, constrain
tools/filesystem reads to the review bundle and public sources. Otherwise restrict
reads in the prompt and record this as instruction-only isolation, not an OS sandbox.
Do not request internal project access to help the reviewer understand the paper:
missing manuscript information is itself a review finding.

Prefer a model different from the main producer(s), respecting the existing exact
native model, data-policy and resource rules. Context independence and
model independence are separate records. Record requested and actually served
identities or `unknown`; unknown identity cannot certify a model-independent gate.
If a truly fresh context or required compatible reviewer cannot be dispatched,
return an unexecuted/provisional review package rather than claiming a blind review.

A neutral instruction can be:

> Review the supplied submission under the supplied venue criteria. Work independently
> from this submission and permitted public literature. Identify its contributions,
> strengths, validity gaps, alternative explanations, reproducibility limitations
> and actionable improvements. Locate findings in the submission and justify them
> with evidence. Do not infer experiments or assumptions absent from the submission.

Do not include a desired outcome, author interpretation, first-round objections
or this project's internal audit conclusions in that instruction.

## Exactly two default complete rounds

1. M4 / round 1: a fresh reviewer reads the complete first submission version.
2. The author/integrator adjudicates the actual findings using internal evidence.
   Record accepted, partially accepted or not accepted with reasons and changes.
   Fix scientific problems through the responsible stage within approved scope.
3. M5 / round 2: another newly spawned agent reviews the revised submission and
   current venue criteria, without round-1 comments, replies or reviewer context.
   Reusing the same model is not reusing the same agent; prefer different models
   when compatible, but record each dimension of independence separately.
4. Resolve round-2 findings and do scoped internal rechecks against changed content.
   Preserve each actual review's coverage; do not call a later revision blindly
   reviewed if it was only checked by the integrator.

No automatic third full round or consensus loop. If core changes invalidate the
second review, route to the affected milestone, explain the need/cost for another
full review and resolve authority. Do not certify completion while that required
review or a central validity repair remains outstanding.

For a single explicitly requested venue review, run only that requested round.
Two rounds are the full-paper completion contract, not a prerequisite for every
use of research-review.

## Review output and adjudication

Ask for a balanced contribution summary, strengths, and critical/major/minor
findings with paper/equation/table locations, evidence, consequence and requested
correction. Separate submission-blocking defects from optional future work.
Include questions for authors, missing necessary experiments/assumptions, reuse
or duplication opportunities, competing explanations and inspected/uninspected scope.

Use the venue's actual rating scale only if supplied and verified. Label any score,
recommendation and confidence as simulated and explain its basis; no invented
numerical scale, acceptance probability or guarantee. Lack of an observed defect
does not prove universal correctness or novelty.

The integrator retains raw reports, author-side dispositions and repair evidence.
Confirm a defect and the proposed remedy before editing, using
[independent-review.md](independent-review.md). A proposed new experiment must earn
its cost; a prior theorem does not justify deleting unrelated empirical evidence.
Do not reveal author-side adjudication to the second blind reviewer.

## Dispatch and execution records

Extend the existing offline dispatch packet with:

```json
{
  "review_mode": "venue_blind",
  "submission_root": "<canonical-absolute-submission-bundle-directory>",
  "review_round": 2,
  "prior_agent_ids": ["author-agent"],
  "prior_review_agent_ids": ["round-one-reviewer"],
  "previous_round_completed": true,
  "new_agent": true,
  "fork_context": false,
  "manuscript_revision": "M7",
  "venue_profile": "V2",
  "allowed_inputs": [
    {"kind": "manuscript", "ref": "review-bundle/paper.pdf", "revision": "M7"},
    {"kind": "submitted_attachment", "ref": "review-bundle/appendix.pdf", "revision": "S7"},
    {"kind": "venue_criteria", "ref": "review-bundle/criteria.txt", "revision": "V2"}
  ]
}
```

These supplement the required native profile/author/resource fields; they are not proof
that the agent ran. Missing `review_mode` selects internal-review admission.
The checker generates a neutral prompt from the manifest; omit `message` for blind
reviews. Keep earlier agent IDs coordinator-only. Round two requires reconciled
round-one completion and a distinct new reviewer.
The preflight rejects declared history, invalid rounds, inherited contexts, missing
paper/criteria and mismatched paper/profile revisions. It does not judge
semantic contamination of document contents or verify live identities,
restrict filesystem access or reserve quota. It checks canonical filesystem
containment, regular-file identity and hashes the submitted bytes. Validate actual completion with `--completion` plus its separate
`--dispatch-record`, and retain unknown completion commitments until reconciled.

Persist a separate coordinator dispatch record immediately after the actual spawn:
`record_dispatch(admission, spawn_result, spawn_evidence=reference)` binds the
admitted task ID and canonical request digest to the observed returned agent ID.
Do not derive that binding from the later completion receipt. Completion must
supply matching `task_id`, `request_digest` and `agent_id`; use the separate
`--dispatch-record` with `--completion`. Missing/mismatched/replayed task or agent
receipts and changed submitted bytes retain capacity and cannot pass a gate.
The original admission is separate from the live inventory; completion does not
readmit a running reviewer as a new task.

After the actual call, record agent ID, fresh-context invocation, requested/actual
model, input manifest/revisions, actual access coverage and isolation mechanism,
raw review, consumed resources, and author-side dispositions. Verify the round-2
agent ID differs from round 1 and project participants. Any observed context/input
contamination invalidates the blind designation; preserve the contaminated report
as internal-only evidence and resolve whether a clean replacement is in scope.
