# Bounded optimization records

The stdlib [state helper](../scripts/optimize_workflow.py) implements stable
events, numeric allowance admission, candidate/revision limits and a single
milestone publication record. It does not call models, run tests, judge scientific
truth, install skills or publish externally. Use an existing equivalent tracker
when available; these logical invariants still apply.

## Stage record and resource accounting

An event includes `stage`, `round`, `revision`, `strengths`, `weaknesses`,
`artifact_refs`, inspected `coverage` and `actual_cost` or an explicit measurement
gap. Its project is the designated optimizer record. Identical repeat events do
not write again; conflicting data under the same identity needs reconciliation.
An event from `research-optimize` is suppressed, even if that skill changed itself.

Keep independently maintained controls outside candidate directories:

```json
{
  "project": "paper-1",
  "goal": "Deliver the agreed manuscript and reproduction package",
  "authority_ref": "actual-startup-delegation",
  "baseline": "workflow-baseline",
  "criteria": "controls/criteria.json",
  "project_usage": "controls/other-project-usage.json",
  "budgets": {
    "model": {"limit": 100, "unit": "approved-model-units"},
    "time": {"limit": 1000, "unit": "seconds"}
  }
}
```

The numbers above are illustrative, not granted resources. Use actual approved
limits and units; `null` permits initializing records but blocks spending.
The project usage file reports `{model: {spent, reserved}, time: {spent, reserved}}`
for **non-optimizer** consumption/commitments. The optimizer adds its own ledger,
so usage is counted once. Reconcile this external file from actual project records
before reserving or publishing. A stale or false declaration cannot establish a
real budget. Independent reviewers/validation calls also consume this allowance.

For each unit, admission requires both:

```text
optimizer spent + optimizer reserved + request <= 0.20 * approved total
other project spent + other reserved + optimizer total <= approved total
```

All values must be finite nonnegative JSON numbers, not strings or Booleans.
Do not use dollar estimates as actual billing or convert token/time budgets
without a project-approved conversion. Exact fractional comparisons avoid
rounding away commitments. Record overruns rather than rejecting or hiding the
actual cost; future work is then blocked. Lost/unknown calls keep their reservation.
Only settle after the actual outcome/consumption is reconciled.

## Frozen validation

The criteria file names required task cases, at least one held-out case, protected
strengths and task/cost measures:

```json
{
  "cases": [
    {"id": "recovery", "held_out": false},
    {"id": "new-project", "held_out": true}
  ],
  "strengths": ["negative-results-retained"],
  "metrics": [
    {"id": "duplicate-searches", "direction": "lower", "source": "task-outcome"}
  ]
}
```

Cases/rubrics must be meaningful, not keyword counts that mirror instructions.
Keep the held-out task outside candidate-author inputs until independent
evaluation. The helper checks declared coverage, not who actually saw a file.
Its frozen measures accept `task-outcome` or `measured-cost`, never Jev scores.
Every required case must pass, every protected strength must remain, no declared
measure may regress and at least one must improve. More nuanced trade-offs require
an independently approved new evaluation contract, never a candidate rewriting
its own criteria to make a failure disappear.

A candidate names its isolated path, author model/context and reserved model/time
cost. At most three candidates per M1-M5, one revision each, one publication.
Reserve with `candidate` before initial development, then develop and `freeze`
the resulting bytes. Run the bounded evaluation/review, reconcile actual costs
with `settle`, then record `validate`. For a repair, reserve with `revise` before
editing, develop, freeze again, evaluate, settle and validate. Freezing the initial
implementation does not consume its one repair slot. A frozen revision cannot
silently change; preserve its files before developing the next revision.
Do not create a new record or rename a milestone to reset these counters.
Preserve the previous candidate version before revising; the helper keeps its
digest/history, not a backup of its actual files.

A validation report binds `baseline_sha256`, `candidate_sha256`,
`criteria_sha256` and:

- `cases`: every frozen case id -> `{passed: true, artifact: ...}`.
- `strengths`: every strength id -> `{preserved: true, artifact: ...}`.
- `measurements`: every measure id -> `{baseline: number, candidate: number,
  artifact: ...}`.
- `review`: actual `reviewer_model`, fresh `context_id`, `findings_resolved: true`
  and the review `artifact`.
- `cost_evidence`: an artifact recording measured costs and their limitations.

Each `artifact` is `{path: "workspace-relative-file", sha256: "actual digest"}`.
The helper requires the files and matching bytes, a reviewer differing from the
author (including same-model free/provider aliases), a different context and
settled candidate costs. Independent review must inspect actual changes and
artifacts, not only the author summary. Unknown model identity cannot certify
independence. The shared routing registry's model-family mapping applies to
custom-tool aliases as well as provider/free variants.
Hashes and supplied review declarations are **not authenticated
execution evidence**; the coordinator must inspect the real logs and provenance.

## CLI and recovery

From this skill's directory, use the project root and its designated state:

```text
python scripts/optimize_workflow.py init --workspace <project> --state <project>/optimizer.json --packet <init.json>
python scripts/optimize_workflow.py event --workspace <project> --state <project>/optimizer.json --packet <event.json> --apply
```

Every action defaults to dry-run; add `--apply` to mutate. `init.json` is
`{"contract": "controls/contract.json"}`. Other packets:

| Action | Packet fields |
| --- | --- |
| `candidate` | id, milestone, path, author_model, author_context, cost `{model,time}` |
| `freeze` | id, milestone; record completed development bytes before evaluation |
| `settle` | id, milestone, actual_cost `{model,time}` |
| `revise` | id, milestone, cost `{model,time}`; same isolated path, one settled prior revision |
| `validate` | id, milestone, report (workspace-relative validation JSON) |
| `publish` | id, milestone |
| `status` | no packet needed |

Publication rechecks candidate, controls, report/evidence hashes and budget. It
records `eligible-for-protected-deployment` and **never installs**. Use the
[release/adoption protocol](../../research-navigate/references/workflow-updates.md)
and the existing snapshot/difference-protected installer afterwards. Rollback of
a failed installed version uses its preserved predecessor; do not erase the
failed candidate or its evaluation history.

The state uses an exclusive sibling lock and fsynced atomic replacement. Unknown
locks are not stolen automatically. Paths must stay in the declared workspace;
links, reparse paths and special candidate files are refused. These cooperative
controls cannot prevent a noncooperating editor from forging declarations or
changing files after inspection. They are not OS permission isolation. Resume
from actual state and evidence rather than resetting budgets or duplicating work.
