---
name: research-implement
description: Use when an approved scientific method, evaluator, benchmark harness, or empirical analysis procedure needs implementation or correctness repair. Generic product features belong to the product build stage.
---

# Implement Research and Measurement

Read the [shared contract](../research-navigate/references/workflow-contract.md),
applicable [domains](../research-navigate/references/domains/index.md), and
[dependency rules](../research-navigate/references/stage-map.md). For a substantive
implementation, read [model routing](../research-navigate/references/model-routing.md)
and the [reuse and simplification audit](../research-navigate/references/reuse-and-simplification.md).
When replacing or porting an implementation, apply
[the comparison contract](../research-navigate/references/implementation-comparison.md)
before accepting parity. A matching headline value does not establish equivalence.
For paper-facing tables or figures, read the
[evidence presentation plan](../research-analyze/references/evidence-presentation.md)
and use [the runnable evidence renderer](scripts/render_evidence.py) or the
project's existing plotting stack. Treat the approved metric, denominator and
uncertainty as scientific interfaces, not cosmetic settings.
Consume the same
[argument and display record](../research-write/references/argument-and-figure-contract.md)
used by analysis and writing; keep conceptual schematics distinct from data plots.

## Implement the approved behavior

1. Inspect the existing repository, conventions, protocol, data interfaces,
   reference results and resource allowance. Identify whether this task builds
   shared measurement, a proposed method, or an analysis procedure.
2. Map scientific definitions to concrete inputs, outputs, units, failure states
   and invariants. Surface ambiguities that would change the scientific question.
3. Implement the smallest useful component, reusing existing engineering tools.
   Keep baseline and proposed-method comparisons on a shared, versioned protocol.
   New evaluation studies build and calibrate their harness before baseline runs.
   Prefer a verified library, algorithm or test utility to a new implementation
   when it preserves the scientific behavior. Record the dependency/version and
   run behavioral plus research-effect regressions before deleting the old path.
4. At integrated implementation readiness (M2 for full papers), check important
   behavior with known-answer examples, small synthetic mechanisms,
   unit/integration tests or small-sample checks appropriate to the component.
   Include consequential failure/empty/missing-data cases and reproducible
   configuration. Do not run a large training job merely to validate plumbing.
   Use targeted checks for actual defects or changed behavior during development;
   do not run the entire suite or dispatch a reviewer after each edit.
   For a display artifact, generate tables and figures from recorded data,
   preserve missing values and failures, write safe provenance, inspect the
   actual rendered output at target width, and verify that rerunning from the
   same inputs produces the same scientific content.
5. Record exactly which checks ran and their outcomes. Route a required metric,
   data or protocol change to design instead of silently changing the comparison.

## Deliver and finish

Deliver the actual implementation and configuration, interfaces/run instructions,
code revision, verification evidence and remaining limitations. Include the shared
handoff. If only a snippet/specification is possible, label it unexecuted; do not
claim a repository patch, passing checks or scientific performance.

Correct code makes a study runnable; the research claim still needs evidence.
Route calibrated measurement to baseline, and verified method code plus trustworthy
controls to experiment. Preserve the user's boundaries for a small requested fix.

Example: a discounted-return implementation can be checked on a short trajectory
with known rewards and termination before training a policy. Include truncation
and missing-reward cases required by the actual environment contract.

## Mathematical work when applicable

For mathematical computation distinguish floating-point discovery, exact finite checking, formal certificates and proof. Recheck actual-input and joint-witness conditions; use exact checks only where they answer the current obligation.
Read [mathematical work](../research-navigate/references/mathematical-work.md) for the optional record and return contract.
