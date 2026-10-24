---
name: research-product-build
description: Use when an approved research tool, library, framework, Agent system or practical product MVP needs implementation, user-flow validation, or product and research regression checks.
---

# Build and Validate the Product

Read the [shared contract](../research-navigate/references/workflow-contract.md)
and relevant [domain references](../research-navigate/references/domains/index.md).
For a substantive build, use [model routing](../research-navigate/references/model-routing.md)
for free independent implementation branches and separate review/integration.

## Build the approved user outcome

1. Inspect the approved MVP, repository, interfaces, acceptance examples, user
   evidence, research dependencies and resource scope. Preserve existing decisions;
   do not restart product approval for routine implementation.
2. Select suitable available engineering/artifact tools. Implement the smallest
   complete user journey with clear inputs, outputs, failure handling and examples.
   Keep internal research mechanics out of the user flow unless they inform a
   meaningful choice.
3. Preserve the mapping from scientific definitions to product behavior: units,
   model/data/protocol versions, provenance, aggregation, failure treatment and
   limits. Check the effect of packaging or runtime changes on validated behavior.
4. Run appropriate functional checks plus research-effect regressions. A passing
   interface test alone cannot establish that the scientific output is unchanged.
   Verify installation/usage instructions in the relevant environment.
5. Exercise representative user journeys. Record actual observations and clearly
   label simulated or author-only validation. Return need/scope failures to
   product-discover and scientific validity failures to the relevant research stage.

## Deliver and finish

Deliver the usable implementation, examples/run instructions, actual verification
results, product/research acceptance status and remaining limitations. Include the
shared handoff. An unattached repository or unavailable runtime yields a clearly
unexecuted specification/package, not a claimed product or passing test suite.

Route a validated candidate to product-release. Public release, extra hosting,
expanded functionality and ongoing operation require the relevant existing or new
authorization; they are not implied by a bounded MVP implementation request.

Example: a model-serving optimization must preserve both its documented API and
the quality checks tied to the approved research claim before acceptance.
