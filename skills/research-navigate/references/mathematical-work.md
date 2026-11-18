# Mathematical imports, original problems and returns

Use this reference for substantial theorem reuse, decomposition or delegated
proof work. Ordinary reading, a local calculation and empirical research do not
need this full record. Reuse the project's theory material, stable task IDs and
handoff; this is not another scheduler or a new review cadence.

## Import a result that can actually be used

For a theorem, bound, algorithmic guarantee or counterexample being used, record:

- Source version, theorem/page/section and actual reading range; unavailable
  statements or dependencies remain unverified. Check relevant corrections and
  counterexamples, including older foundational work.
- Full domains, quantifiers, hypotheses and conclusion, with current objects,
  parameters and probability spaces mapped to the source.
- Each premise already supplied, missing, contradicted or requiring a mapping
  proof; references to those proofs, avoiding circular dependence.
- Consuming obligation and exact use location; distinguish source theorem,
  direct application and the project's new corollary.
- Remaining obligation and validity limits after this import.

An analogy is a search lead, not a usable theorem. A supported empirical claim
does not imply a proved theorem. Preserve proof status and source coverage.

## Connect back to the actual input

Maintain the chain: original problem and actual input -> local object and
premises -> local result -> original conclusion. Audit both arrows. A correct
conditional lemma can leave the original theorem completely open.

Separate arbitrary original inputs, auxiliaries we may choose and outputs
actually produced upstream. Preserve quantifier order. Independently existing
witnesses cannot be silently merged into a common witness. Equally sized sets
need not be equal. A feasible relaxation need not produce an original object.
Check realizability and simultaneous downstream conditions before claiming
coverage. Record numeric exploration, exact finite checking, formal verification
and mathematical proof separately, including each one's actual scope.

## Return to one owner, then act

For a delegated mathematical package, optional `math_work` contains:

```json
{
  "original_spec_ref": "brief#problem",
  "original_spec_revision": "v1",
  "active_obligation": "O2",
  "parent_obligation": "O1",
  "parent_task_id": "P1",
  "return_to": "theory#O1",
  "continuation_owner": "coordinator",
  "theorem_uses": ["theory#import-1"],
  "established_connection": ["local lemma L1"],
  "remaining_connection": ["actual upstream output satisfies premise H"],
  "obstacle_id": "O1-hard-core",
  "next_discriminating_action": "bounded check of H on actual output"
}
```

The parent supplies `parent_binding` for identity comparison where available,
including the original specification reference as well as its revision.
The child returns artifacts, derivations, counterexamples, gaps and a next-action
recommendation to this point; it does not separately dispatch the successor.
The owner checks the connection, consumes the stable return once, updates the
public record under the existing single-writer lock and **executes** the smallest
authorized missing dependency. A saved recommendation alone is not continuation.

`scripts/math_work.py` validates structure and offers `consume_return`, a pure
idempotent transformation. A return includes stable `id`, `child_task_id`,
parent identity, original specification reference/revision, active obligation,
return point, `artifact_refs`, `connection_review_ref`,
`supersedes_pending` and `next_action`. The caller persists the change and starts
the action through existing tools. This helper neither proves correctness nor
reserves resources, launches agents, wakes Goal or replaces host lifecycle tools.
Before dispatch, persist the child's mathematical binding under the existing
parent state's `delegations[child_task_id]`; consumption rejects unknown children
or a mismatched delegated obligation. Do not reconstruct this binding from the
return itself, or count a newly received ID as evidence of a prior dispatch.

Before more branching, consume new results across already justified equivalent
representations. Supersede only redundant **pending** tasks. Keep useful in-flight
work pinned and retain all historical evidence. A separately valuable subtheorem
may be delivered while its parent remains unresolved.

## Probe the hardest remainder

Before accepting a new decomposition or increasing its batch, identify the
hardest unclosed branch and its connection to the original bottleneck. Spend a
bounded amount of existing budget on a derivation, counterexample or interface
check. Record the result and what it changes. Missing definitions justify
recovering the exact obligation; they do not justify an invented successful probe.

Track stagnation against the same `obstacle_id` and original input. Renaming it,
repeating old coverage or finishing easy siblings does not reset two rounds with
no new understanding. Then compare repairing assumptions, narrowing the claim,
changing tools, a discriminating test or preserving the gap. Do not expand batches
indefinitely. Necessary repetitions, confirmation runs and informative negative
results remain useful. Do not invent a proof-completion percentage.

## Checks and learning

Lightweight returns record decisions; M1 checks premises/decomposition, M3 checks
principal evidence and original-problem connection, M4/M5 retain the two fresh
venue reviews. Reopen only affected checks when definitions or claims change.
No mandatory per-lemma reviewer, full test suite or new literature sweep.

Optimizer lessons name the actual changed decision, consuming stage, protected
strengths and evidence. Classify as `shared_behavior`, `domain_reference`,
`project_only` or `defer`. Keep the existing 20% budget, at most three candidates,
one targeted revision each and one publication per milestone. Do not delay a
complete paper for optional optimization.

Adapted independently from MathRSI commit
`de556f3d5427343153d8d24bed4578ccfe66400c`: survey, actual-input-coverage,
global-reassessment and meta-evolve. Source audit is in the repository's
`docs/math-rsi-study/assessment-20261118.md`; no upstream dispatcher is installed.
