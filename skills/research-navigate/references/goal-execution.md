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
- Include the manuscript and reproduction completion conditions in the objective
  or its linked project record. Supply `token_budget` only when the user explicitly
  requested that token allowance. Token allowance is distinct from money, GPU
  hours, server jobs and shared Codex model quotas.
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
