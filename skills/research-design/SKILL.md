---
name: research-design
description: Use when an approved research question needs mathematical derivation, a method, benchmark, experiment, empirical analysis, identification strategy, or revised protocol and resource plan.
---

# Design the Research Protocol

Read the [shared contract](../research-navigate/references/workflow-contract.md),
the applicable [domain references](../research-navigate/references/domains/index.md),
the [dependency rules](../research-navigate/references/stage-map.md),
[model routing](../research-navigate/references/model-routing.md) when dispatching to more than one model, and the
[reuse and simplification audit](../research-navigate/references/reuse-and-simplification.md)
when prior work may replace a derivation, implementation or experiment.
Optional [Jev decision support](../research-navigate/references/decision-support.md) may assist a genuine candidate choice;
it is advisory and never decides a gate.

## Make the claim testable

Carry the versioned [research-focus](../research-focus/SKILL.md) anchor into the
protocol. Relate each derivation, metric and experiment to the main question;
bound calibration and auxiliary theory by their served claim and return condition.
In-theme delegated revisions reopen affected validity checks, not automatic
topic approval. Explicit locked assumptions and resource limits still apply.

When receiving a contribution-improvement round, preserve its identity, targeted
claim, competing explanations and applicable authorization. Turn its proposed
check into explicit proof/test obligations and support/refutation/inconclusive
branches, with cost and stopping conditions. Return the protocol revision and
any affected prior evidence to that round. Theory-only work need not acquire an
experimental dependency; a suggested study is not itself execution approval.

For a selected theory-first question, consume its versioned definitions, source
mapping and theoretical prototype. Follow the relevant
[mathematical work guidance](../research-ideate/references/mathematical-ideation.md).
Within the requested scope and reasoning allowance, deepen the actual derivation
and return a proof, counterexample or precise unresolved step, not only future
proof tasks. Missing definitions or a plan-only request limit what can be done.
Link each empirical prediction to the statement and assumptions it examines;
unfinished proof does not block informative tests already covered by approval.

1. Map each proposed claim to an observable comparison, measurement or proof
   obligation. Specify scope and alternatives that could explain the outcome.
   Evaluation/empirical papers need not invent a new method.
2. Define population/tasks, data provenance/access, sampling and splits,
   preprocessing, controls/baselines, metrics and unit of analysis. Identify
   measurement validity, leakage and fair resource/tuning conditions.
3. Specify the method or study procedure, relevant ablations/sensitivity checks,
   repetitions and uncertainty analysis. Match statistical treatment to the
   sampling design. Include theory or identification assumptions where needed.
   For inferential analyses, define the estimand, dependence/sampling unit,
   planned contrasts, missing-data handling and relevant multiplicity family
   before inspecting outcomes. Diagnostics guide judgment, not an automatic
   test-switching rule chosen to obtain a preferred result.
4. Define implementation checks, a minimal feasibility pilot, formal experiment
   matrix, model/config selection and independent final validation where feasible.
   Separate planned confirmatory tests from exploratory analyses.
   State the power rationale: the smallest effect worth detecting and why the
   planned repetitions, seeds or sample size can detect it, or that they cannot.
   Check baseline adequacy: list the strongest published results on the same
   task from the literature record and justify any omitted from the comparison.
   Fix the reproduction tolerance for each baseline here, before baseline runs.
5. Estimate all relevant resources, including tuning, evaluation and retries.
   State explicit success, futility, budget and retry stopping conditions, execution
   environment needs, and observable status/cancellation controls.
6. Arrange dependencies by study type. New measurement pipelines are implemented
   and calibrated before baseline runs; proposed methods use trustworthy controls.
7. For each reuse candidate, specify the equivalence or condition checks needed
   before deleting current work. Decide explicitly whether each experiment remains
   necessary for implementation, generalization, mechanism, identification or
   task-level evidence. Do not remove evidence merely because a related theorem
   or paper exists.

## Deliver and finish

Deliver a versioned protocol, claim-to-test map, execution dependencies, resource
estimate, risks and unresolved decisions. Once approved (or covered by startup
delegation), lock it with `research-navigate/scripts/check_records.py
lock-protocol` (see the [default record layout](../research-navigate/references/records.md)).
A later change is a new revision with its own lock; analysis lists every
departure from the locked revision as a deviation. Present the protocol/resource approval
package when needed; preserve approval already covering this revision and scope.
Then hand off to implement, baseline or experiment as dependencies require.
For a substantive protocol, record free execution branches, independent reviewers,
their resource pools and any unexecuted checks. Consolidate the research/protocol
review gate at M1; M2 handles integrated implementation and the needed pilot.
Reuse current coverage rather than reviewing every protocol edit. Formal runs need
valid applicable M1/M2 coverage and authority; existing startup delegation can
cover in-scope refinement but not materially changed assumptions or resources.

If the protocol changes, identify affected prior results and decisions. Label
post-outcome changes as exploratory and plan independent confirmation if necessary.
Do not invalidate unrelated completed work.

Example: observational policy data with unmeasured confounding requires a justified
identification path, restricted target, sensitivity/bounds or descriptive claim;
training an RL model alone does not complete the causal protocol.

## Mathematical work when applicable

Carry the chain from original input through local premises and result back to the original conclusion. Attempt the actual mappings and hardest branch, preserving quantifier order, common-object obligations and proof gaps. Consume accepted imports before expanding pending work.
Read [mathematical work](../research-navigate/references/mathematical-work.md) for the optional record and return contract.
