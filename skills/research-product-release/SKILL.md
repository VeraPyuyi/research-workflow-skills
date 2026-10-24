---
name: research-product-release
description: Use when a research tool or practical product needs release packaging, clean-environment verification, documentation and distribution-readiness checks, or an explicitly authorized public release.
---

# Prepare and Publish a Verified Candidate

Read the [shared contract](../research-navigate/references/workflow-contract.md)
and relevant [domain references](../research-navigate/references/domains/index.md).
Use [model routing](../research-navigate/references/model-routing.md) for free
packaging/documentation/example checks and an independent release review.

## Verify what would actually be distributed

1. Identify candidate revision, included source/binaries/data/models, release
   target, supported environment, existing validation and publication authority.
2. Assemble install/run instructions, a meaningful example, limitations, research
   evaluation references, version and compatibility/migration notes as applicable.
   Keep reproducibility statements consistent with available artifacts.
3. Run the documented installation and core use case in a clean environment when
   available. Record versions, exact candidate and actual results. If unavailable,
   mark the check pending; an unexecuted recipe is not fresh-environment evidence.
   Complete the submission/release review gate on the actual candidate before a
   public release; internal review never substitutes for publication authorization.
4. Inventory distribution conditions for source, dependencies, model weights and
   data. Obtain the owner's unresolved license choice and needed rights decisions.
   Do not infer redistribution permission from access or invent a license decision.
   Exclude non-distributable assets from a proposed release package and explain how
   permitted setup would work; preserve the original project.
5. Check the actual public payload for sensitive material. When making repository
   history public, inspect relevant history and attached assets as well as the
   current tree. Report findings without reproducing secrets.
6. Present readiness and the exact candidate/action. Publish only under explicit
   authority matching this target and material content, reusing valid prior
   authorization. Confirm the resulting version/location after an actual action.

## Deliver and finish

Deliver candidate manifest, documentation/examples, actual clean-environment and
regression evidence, rights/remaining decisions, release notes, action status and
shared handoff. Distinguish prepared, ready, and actually published.
Route failures to product-build, rights/goal decisions to the owner, and approved
post-release issues to product-maintain.

Example: a release can include code plus instructions for obtaining a model under
its own conditions while omitting weights the project cannot redistribute.
