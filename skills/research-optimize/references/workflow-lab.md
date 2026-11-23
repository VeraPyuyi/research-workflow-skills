# Workflow Lab

A lab round changes the shared skills only when a fixed evaluation shows that
the change helps and harms nothing protected. It runs in the skills repository
with its own budget. Commands below run from the repository root.

## Round layout

```text
lab/L<n>/
  contract.json      goal, authority (owner's request), baseline ref, budgets,
                     "budget_share": 1, criteria and usage paths
  usage.json         {"model": {"spent": 0, "reserved": 0}, "time": {...}};
                     the lab budget is not shared with a research project
  criteria.json      frozen cases (scenario ids), held-out flags, protected
                     strengths, measure "mean-pass-rate" (direction higher)
  signals.json       aggregate output that motivated the round
  README.md          the round's question, candidates and outcome
.build/lab/L<n>/     generated: exported suites, task and grading packets,
                     answers, grades (not committed)
```

Freeze `contract.json`, `criteria.json` and the evaluation suites (commit
them) before writing any candidate. Initialize the state helper with them:

```text
python skills/research-optimize/scripts/optimize_workflow.py init --workspace . --state lab/L<n>/optimizer.json --packet <init.json> --apply
```

## 1. Signal

```text
python scripts/workflow_lab.py aggregate <project dirs or events.jsonl files> > lab/L<n>/signals.json
```

A signal is a stage and weakness tag seen in at least two projects, or once
with a replayable trace. Read the underlying events and traces before choosing
what to change; the tag is an index, not a diagnosis.

## 2. Evaluation suites

- `tests/scenarios.json` and the other scenario files: expected behaviour.
- `tests/integrity-scenarios.json`: integrity traps. Protected.
- Replay cases: turn each replayable trace into a scenario in
  `tests/replay-scenarios.json` with a rubric in `tests/replay-rubric.json`
  (the facts the agent had, the request, and what correct behaviour looks
  like). Protected. Remove private paths, credentials and unpublished data
  first; keep replay cases that cannot be made public outside the repository.

Mark at least one suite or a set of scenarios as held out: the candidate author
does not read them until evaluation.

## 3. Candidates

At most three per round, each in its own directory (for example a git branch
or `lab/L<n>/candidates/<id>/skills`), with costs reserved before development
and settled after:

```text
python skills/research-optimize/scripts/optimize_workflow.py candidate --workspace . --state lab/L<n>/optimizer.json --packet <candidate.json> --apply
```

The packet's `milestone` field carries the round id (`L1`, `L2`, ...).

## 4. Evaluate

```text
python scripts/workflow_lab.py prepare --round L<n> --baseline-ref <ref> --candidate-ref <ref or WORKTREE> --out .build/lab/L<n> --runs 3
```

For each side, run every task in `tasks.jsonl` in a fresh agent and save the
answer as `answers/<task_id>.md`. Then:

```text
python scripts/behavior_eval.py grade --out .build/lab/L<n>/baseline
python scripts/behavior_eval.py grade --out .build/lab/L<n>/candidate
```

Grade every packet in `grading.jsonl` with a model of a different lineage from
the answering agents, in a fresh context, without telling it which side the
answer came from; save `grades/<task_id>.json`. Then:

```text
python scripts/behavior_eval.py summarize --out .build/lab/L<n>/baseline > .build/lab/L<n>/baseline.json
python scripts/behavior_eval.py summarize --out .build/lab/L<n>/candidate > .build/lab/L<n>/candidate.json
python scripts/workflow_lab.py compare --baseline .build/lab/L<n>/baseline.json --candidate .build/lab/L<n>/candidate.json --output lab/L<n>/comparison.json
```

`compare` is eligible only with at least three graded runs per scenario on both
sides, a higher mean pass rate, no protected scenario losing pass rate and no
other scenario falling by more than the declared tolerance (default zero).
Differences of one run in three are noise-level; prefer more runs over a wider
tolerance when results are close.

## 5. Review, approval and release

Copy `optimizer_fields` from the comparison into the validation report, add the
artifact hashes, the independent review of the actual diff and evaluation
files, and the cost evidence, then run the state helper's `validate` and
`publish`. `publish` records eligibility only. The owner approves; the release
tools install the change and keep the previous version for rollback. Record
rejected candidates and their results in the round README as well.

## First round

`lab/L1/` evaluates the 2026-11-23 review fixes (candidate `magpie` after the
merge) against the suite before them (`4a5c2d0`) on the core and integrity
scenarios. It is a measurement of an already merged change, so its outcome
decides whether that change stays, not whether it is installed.
