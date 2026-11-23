---
name: research-baseline
description: Use when a study needs trustworthy reference results, reproduction of prior methods, validation of a baseline implementation, or diagnosis of a discrepancy with published or earlier results.
---

# Verify Baselines and Reproductions

Read the [shared contract](../research-navigate/references/workflow-contract.md),
applicable [domains](../research-navigate/references/domains/index.md), and
[dependency rules](../research-navigate/references/stage-map.md). For a substantive
baseline, read [model routing](../research-navigate/references/model-routing.md) only when dispatching work to more than one model;
then use it and use a native implementation branch with comparison review consolidated at M2
for full-paper work. Reuse valid baseline/check records; do not re-review each run.
For reproduction, code replacement or port parity, read
[implementation comparison](../research-navigate/references/implementation-comparison.md).
Compare the declared output channels, including sample masks, warnings and
failures; test the comparator on wrong, absent, empty and misaligned outputs.

## Establish a trustworthy comparison

1. Identify the reference claim, actual paper/code/checkpoint, data/split,
   preprocessing, training/tuning budget, metric and the replication tolerance
   fixed in the protocol (not chosen after seeing the reproduction). Record the
   tuning budget of baselines and the proposed method as numbers. Distinguish verified details from inferred defaults.
2. Check data access, integrity, permitted use, leakage and evaluation validity.
   For a new benchmark, require a calibrated measurement pipeline before running
   reference methods; route missing infrastructure to research-implement.
3. Reuse valid existing runs. Execute a bounded smoke check and reference runs only
   within the approved protocol/resources. Record versions, configuration,
   environment, raw results, attempts and consumption.
   When a maintained implementation or standard baseline is available, prefer it
   over a bespoke reimplementation after checking version, license, protocol
   compatibility and behavioral equivalence. Run a regression before replacing an
   existing baseline.
4. Compare matched conditions. Investigate differences in data, split, augmentation,
   metric, training, tuning, checkpoint selection, environment and randomness.
   Record hypotheses and evidence for discrepancies rather than changing many
   conditions without attribution.
5. Classify the baseline as verified under stated conditions, partially reproduced,
   not reproduced, or unexecuted. Explain implications for the planned comparison.

## Deliver and finish

Deliver the baseline specification, runnable setup or unexecuted package,
comparison table, discrepancy investigation, validity checks and unresolved gaps.
Include the shared handoff and relevant resource state.

A local improvement over a weak, unexplained reproduction is not evidence of
improvement over the published method. If a valid alternative reference is needed,
return the comparison change to research-design and the affected approval.
Substantive implementation repairs route to research-implement; trustworthy
existing baselines can advance to method implementation or experiments.

Example: a reproduction that selects a different checkpoint and evaluation split
needs a condition-by-condition comparison before inheriting the published baseline
label. Keep the local result while resolving what it can legitimately support.
