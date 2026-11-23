---
name: research-product-maintain
description: Use when an existing research tool or product has a requested issue, compatibility change, user-feedback improvement, or functional/scientific regression requiring bounded maintenance.
---

# Maintain the Product and Its Scientific Outputs

Read the [shared contract](../research-navigate/references/workflow-contract.md)
and relevant [domain references](../research-navigate/references/domains/index.md).
Use [model routing](../research-navigate/references/model-routing.md) only when dispatching work to more than one model;
then use it for a free
reproduction/fix branch and independent regression review.

## Resolve the requested issue

1. Identify the requested behavior, affected version, user impact, reproduction
   evidence and authorized scope. Distinguish defect repair from a new product or
   research direction.
2. Reproduce or characterize the issue, trace its cause, and define a focused
   regression check before changing consequential behavior. If required artifacts
   or execution are unavailable, provide a precise investigation/fix package.
3. Implement the bounded repair using the project's engineering conventions.
   Check compatibility, supported user journeys, examples and the relevant
   research-effect regressions.
4. Trace scientific consequences. A bug in aggregation, measurement, sampling or
   model behavior may affect previous tables, claims or checkpoints. Preserve
   original records and produce a separately versioned impact analysis/correction.
   Route changed scientific conclusions to analysis/review and the affected owner
   decision rather than silently replacing historical results.
5. Separate resolved issues, remaining risks and optional improvements. New demand
   can become a product-discovery task; new scientific questions can become a
   research task after the appropriate decision.

## Deliver and finish

Deliver the actual patch or explicitly proposed work package, verification,
compatibility notes, affected research outputs, release-readiness status and
shared handoff. A local fix does not automatically publish a version or create a
recurring monitor. Ongoing operations are separate requested work.

Example: correcting a unit conversion should include a regression fixture and an
impact check on previously exported summaries, not only a passing UI test.
