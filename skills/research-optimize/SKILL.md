---
name: research-optimize
description: Use when a research stage or handoff should leave a retrospective event for later workflow improvement, or when the suite owner runs a workflow-lab round that turns recurring weaknesses across projects into a tested skill change.
---

# Improve the Research Workflow

Two layers with different owners. Inside a research project this skill only
records what happened. Changing the shared skills happens outside projects, in
a workflow-lab round with its own budget, a fixed evaluation set and the suite
owner's approval. A research project never develops, validates or publishes a
workflow change, and never spends its research budget on one.

## Layer 1: retrospective events inside a project

At a meaningful handoff (a completed stage, a milestone, a failure worth
remembering), the coordinator appends one line to the project's event log
(default `research/optimizer/events.jsonl`; see the
[default record layout](../research-navigate/references/records.md)):

```json
{"project": "paper-1", "stage": "research-survey", "round": "R2", "revision": "M3",
 "date": "2026-11-23", "strengths": ["closest work compared on mechanism"],
 "weaknesses": [{"text": "two citations entered the draft before resolution",
                 "tag": "literature-citation", "trace_ref": "research/literature.jsonl"}],
 "cost": {"model": "unknown", "time_minutes": 40}, "artifact_refs": ["research/literature.jsonl"]}
```

- Record only observed facts. An empty weakness list is fine; do not invent a
  defect. Keep failures, negative results and corrections.
- Tag each weakness with one of: `scope-planning`, `literature-citation`,
  `ideation-novelty`, `protocol-design`, `implementation`,
  `evaluation-integrity`, `experiment-execution`, `analysis-statistics`,
  `writing-claims`, `review`, `coordination-state`, `resource-budget`,
  `authorization`, `other`.
- Add `trace_ref` when a log, transcript or artifact shows the problem; such
  traces become replay cases in the lab.
- Writing an event triggers nothing: no model call, review, test suite or
  workflow change, and it never delays the paper. Events from this skill and
  from research-focus are not logged, so neither can trigger the other.
- Keep the log out of blind venue-review bundles.

## Layer 2: workflow-lab rounds (repository level)

Run by the suite owner, or by an agent the owner asked to, in the skills
repository, not in a research project. Follow [the workflow lab](references/workflow-lab.md):

1. **Signal.** Aggregate event logs from several projects with
   `scripts/workflow_lab.py aggregate`. Work only on a weakness that recurs in at
   least two projects or that has a replayable trace. One project's anecdote is
   not a reason to change shared behaviour.
2. **Freeze controls.** Before writing any candidate, freeze the lab contract,
   the evaluation suites (core scenarios, integrity traps, replay cases built
   from traces) and the criteria, outside every candidate directory. Integrity
   and replay suites are protected: no candidate may lower their pass rate.
3. **Candidates.** At most three per round, one revision each, developed in
   isolation from the baseline, with costs reserved and settled through
   [the state helper](references/optimization-protocol.md). A candidate never
   judges itself and never edits the frozen criteria.
4. **Evaluate.** `workflow_lab.py prepare` exports baseline and candidate suites
   and plans the same scenarios for both, at least three runs each; the host
   runs them in fresh agents; a grader of a different lineage grades them
   blind to which side produced an answer; `workflow_lab.py compare` decides
   eligibility (more passes on average, no protected regression, enough runs).
   When these runs use more than one model, read
   [model routing](../research-navigate/references/model-routing.md) and the
   [shared contract](../research-navigate/references/workflow-contract.md).
5. **Review and approve.** An independent reviewer inspects the actual diff and
   evaluation artifacts. The state helper records eligibility; the owner
   approves publication; the release tools install it, keeping the previous
   version for rollback. At most one publication per round.

If a candidate would change scientific assumptions, evidence standards or
authorization rules, treat it as a change to the research contract and give it
the owner's explicit review, not only a passing evaluation.

## Deliver

Inside a project: the appended event line, nothing more. In a lab round: the
signal summary, frozen controls, candidate outcomes with evaluation results
(including failed and rejected candidates), costs, review, the owner's decision
and the release reference.
