# Full-Paper Goals and Milestone Checks

Read for an explicitly requested end-to-end paper or native Codex Goal. A bounded
reading, calculation, review or implementation task keeps its requested scope.
This guide does not itself authorize a Goal, spending, submission or publication.

## Authority and cadence

Continue in-scope work without fresh approval at each stage transition: the user's
milestone checks, not a per-task review, are the required cadence. Queue findings
for M1-M5, keep running jobs pinned to their recorded versions, and adopt only
compatible validated workflow releases at entry, resumption or handoff.
Manage native Goal state only through actual tools with explicit user authority.
Without native Plan switching, plan within execution mode and continue. Optional
workflow optimization is never a reason to delay a paper ready for delivery.

## Bind the objective

The full-paper outcome is an actual submission-ready manuscript plus the
experiment reproducibility package appropriate to the chosen venue/year/track.
At startup, inspect existing assets and confirm the topic, venue, resource
envelope and completion contract. If the venue is undecided, proceed with useful
research preparation, but do not certify venue-specific readiness.

Record whether the user delegates in-scope protocol refinement, evidence-based
conclusion formation and manuscript revisions. With that startup authority, keep
working through stages and milestone reviews without asking again at each handoff.
Material changes to the direction, core protocol or assumptions, resource ceiling
or promised deliverable reopen only the affected decision. Submission, public
code/data release and authorship decisions remain separate user decisions.
Do not infer this delegated authority from a request merely to read one paper.

## Native Goal lifecycle

- On entry/resumption, use the available native `get_goal` to inspect the objective,
  status and allowance. Reuse a matching active Goal; do not overwrite an unrelated
  unfinished Goal. If none exists, call `create_goal` only after explicit user
  activation of Goal mode, not because a skill was selected.
- An explicit activation request is permission to perform this binding now.
  Retain the returned Goal identifier/status and the activation instruction in
  the project record. A locally written `"active"` field is not an activation
  receipt. A coordinator authorized to resume an existing chat sends the scoped
  instruction through the host's supported chat tool; Goal lifecycle calls run
  in that owning chat. Never edit a host Goal database or create a second chat
  merely to bypass the original project's state.
- Include the manuscript and reproduction completion conditions in the objective
  or its linked project record. Supply `token_budget` only when the user explicitly
  requested that token allowance. Token allowance is distinct from money, GPU
  hours, server jobs and per-provider quotas.
- Read the saved milestone, artifact revisions, check coverage, findings, authority,
  running job IDs and committed resources. Reconcile uncertain execution before
  launching more work. Continue the smallest missing dependency.
- A completed stage updates records and continues the Goal. An outline, route,
  unexecuted work package, partial draft or analysis report is not paper completion.
- Use `update_goal(complete)` only after the completion contract is actually met
  and required work is closed. Near-exhausted tokens are not evidence of completion.
  For a budgeted Goal, report the final usage returned by the completion tool.
- Pause only at the user's explicit request, with budget limits taking precedence.
  Do not treat waiting for a decision as user-requested pause.
- Mark blocked only at the native tool's actual threshold: currently the same
  blocker on at least three consecutive Goal turns, with no meaningful independent
  work left. A resumed blocked Goal begins a fresh audit. Do not manufacture extra
  turns or poll unchanged state to reach the threshold.
- Budget/usage limits and resume are controlled by the user/runtime. Do not claim
  the tool can raise an allowance, resume itself or cancel external jobs.

Native tool contracts take precedence if they change. When native Goal tools are
absent, preserve the same project handoff and state the limitation; do not claim
Goal activation or automatic continuation. Generic full-paper requests can still
advance within the current authorized interaction without silently creating a Goal.

Official background: [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
Use the tools actually exposed by the current host, not a guessed CLI switch.

## Stage-to-stage continuation

Apply this at meaningful stage completion or resumption, using existing project
records rather than creating a second scheduler:

1. Close only the completed stage or round. Preserve its artifact versions, valid
   check coverage, actual consumption and unresolved findings. Legacy R0/R1
   stopping rules describe those rounds; they do not shorten a newly authorized
   complete-paper objective.
2. Compare the actual manuscript, evidence, reviews and reproduction package with
   the paper completion contract. If anything required remains, leave the native
   Goal active. Do not use a checklist of planned deliverables as evidence.
3. Select a concrete unfinished dependency covered by existing authority and
   resources, and start it in this turn when possible. Record stage/owner, inputs,
   intended artifact and the action actually taken. Merely recommending the next
   skill does not execute it.
4. Scope a blocker to the work it prevents. For example, an unavailable original
   attachment blocks an exact original-draft audit; it does not automatically
   block source checking, theory work or an independently specified implementation.
   Failed reviewer calls remain failed; choose a supported authorized alternative
   or continue independent preparation while that review stays pending.
5. Reconcile possibly active jobs and resource commitments before new launches.
   Reuse unchanged completed runs, pilots and checks. Proposed budgets are not
   approved budgets; stop expansion of the affected resource use while doing
   work covered by the existing envelope. Ask for an actual missing decision only
   when it is needed, with a concrete bounded choice and its consequences.
6. When the host ends a turn before paper delivery, save a compact resumption
   checkpoint and keep the native Goal active for host-driven continuation. An
   interim final response describes progress and unfinished work; it is not an
   invitation requiring another human "continue". Native host limits still apply.
   If no meaningful authorized work remains, follow the actual blocker/decision
   lifecycle rather than manufacturing activity or empty continuation turns.

The checkpoint adds these fields to the existing handoff (names/serialization
may follow the project):

- `goal`: actual native binding/status, completion-contract reference and authority.
- `stage_status` and `paper_status`: separate values with artifact evidence.
- `next_action`: owner/stage, inputs, intended artifact and execution state
  (`started`, `ready`, `waiting_for_job`, or `needs_decision`).
- `blockers`: affected dependencies and independent work still available.
- `resume`: job IDs, budget commitments, retained artifact/check versions and
  the last meaningful transition. Do not replace an existing richer state store.

At first activation or recovery from a premature stop, distinguish three kinds
of evidence: a real Goal binding; work crossing a stage boundary; and, if observed,
a later native continuation turn with no intervening human continue prompt.
Installing a skill or passing a simulated scenario proves none of those runtime
events. Do not fabricate a turn to make this verification pass. If Goal tools or
host continuation are unavailable, report that precise limit and continue useful
in-turn work; do not claim unattended execution or install an unrequested service.

## Five substantial milestones

These are check boundaries, not five compulsory user interruptions. Choose review
branches for the artifact and consolidate findings at the applicable node.

| Node | Ready for concentrated checks | Coverage |
| --- | --- | --- |
| M1: research/protocol | Question, literature, theory prototype and protocol form a coherent proposal | Novelty/reuse conditions, assumptions, derivations, controls, budget, stopping conditions |
| M2: execution readiness | Measurement, baseline and core implementation are integrated | Relevant correctness/regression tests, data/metrics, one needed small end-to-end pilot, formal-run readiness |
| M3: principal conclusions | Formal evidence or theory and analysis are available | Uncertainty, proofs/counterexamples, fairness, alternative explanations, claim/figure provenance |
| M4: complete manuscript | Paper and intended reviewer attachments are complete | First fresh-context venue review |
| M5: revised delivery | Round-1 substantive issues resolved, revision and package assembled | Second fresh-context venue review, final build/export, required reproduction acceptance |

M1/M3/M5 correspond to the existing research/protocol, principal-conclusions and
submission/release gates for paper work. M2 consolidates engineering checks; M4
adds the first manuscript-wide venue simulation. Product-specific acceptance and
release gates retain their existing scope. Pure theory may skip M2 or empirical
checks with a reason, without skipping proof and manuscript checks.

During a milestone, collect pending findings and do the work. Do not invoke a
reviewer or full test suite after every edit, branch or stage transition. Assign
review ownership ahead of time; execution of that review is due at the milestone.
Provisional outputs may support authorized downstream drafting/preparation, but
are not settled evidence before their applicable gate passes.

Keep lightweight budget/permission/job-state admission and necessary correctness
checks before consuming dependent resources. An observed error, invalid metric,
data leak or failed run warrants immediate local diagnosis. Research experiments,
proof work and counterexample searches are scientific work, not redundant QA.

Reuse checks by artifact revision and covered dependencies. A spelling edit does
not invalidate statistical review. A changed metric stales affected results,
figures and claims; a core definition/protocol change reopens affected milestones
and authority. After repair, test the affected behavior and dependencies once.
Do not rerun unrelated checks or refresh every citation by default.

## Venue requirements and completion

Use research-submit to establish a dated authoritative venue/year/track profile:
format/anonymity/declarations, reviewer criteria and artifact obligations.
Classify each obligation as required at submission, recommended, after acceptance,
or optional artifact evaluation, with source and actual verification status.
Recheck material current requirements at final packaging; reuse the verified
profile between milestones unless the venue or rules change.

The user-requested reproduction package is still delivered if the venue makes
artifact evaluation optional. Its appropriate contents include code/environment,
configurations, permitted data or acquisition instructions, commands, raw/run
references and the map from results to figures/tables. No blanket full training
rerun is required: execute the checks required by the venue and approved project's
completion contract. Record tested commands/environment/results and untested scope.
Never replace executed verification with a runnable-looking script.

Before completion, establish all of the following:

- Actual final manuscript, figures, references, appendix and required statements
  are present, consistent and conform to the verified target profile.
- Central claims have adequate evidence and accurate proof status; exploratory,
  failed and negative findings and limitations remain represented.
- Both fresh-context venue reviews ran on recorded versions. Submission-blocking
  scientific findings are resolved or refuted with evidence, not merely labeled
  "fixed"; remaining optional suggestions do not silently become new obligations.
- Reproduction contents and required acceptance checks are complete; the final
  document was actually built/exported and inspected with the applicable tools.
- The delivery manifest names exact versions, actual check coverage and limitations.
  No unresolved blocker to the promised submission-ready outcome remains.

After the second review, make scoped repairs and recheck affected material. A
third full review is not automatic; if a core change makes another full review
necessary, explain the scope, reason and resource need and resolve any additional
authority before running it. Do not iterate until reviewers agree or give a score.

If credible paper completion is not achievable within the allowance, preserve the
best truthful draft, evidence, failures and exact recovery needs. Report partial
delivery or the applicable native status rather than declaring success or inventing
evidence. A useful negative finding can support a paper; a preferred result cannot
be an implicit stopping condition.

## Compact resumption record

Extend existing records with Goal identity/objective and completion contract,
startup delegation, current M1-M5 node, artifact revisions, valid/stale check
coverage, venue-profile revision, both review identities/versions/dispositions,
remaining work, job IDs and committed/remaining resources. Update at meaningful
transitions; do not build a second database or repeat the record after every edit.
