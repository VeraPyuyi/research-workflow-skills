# Stage Routing Map

Route by the next requested outcome and missing evidence, not by the age of the
chat or an obligatory stage number. Inspect existing artifacts first.

| Missing outcome | Stage | Ready to leave when |
| --- | --- | --- |
| Defined question, constraints or stopping conditions | research-scope | Brief distinguishes decisions from assumptions |
| Source understanding, closest work or cross-disciplinary connections | research-survey | Sources, transfer assumptions and verification gaps are traceable |
| Candidate contribution/question and relevant mathematical prototype | research-ideate | Actual candidate work and comparison are ready for user selection |
| Selected derivation, method, comparison or identification plan | research-design | Arguments/gaps and protocol/resources are reviewable; actual work is explicit |
| Trustworthy reference result | research-baseline | Conditions and discrepancies are accounted for |
| Correct measurement or research code | research-implement | Required behavior is verified, or unexecuted work is identified |
| Actual experiment records | research-experiment | Attempts, outcomes and resource use are reconciled |
| Defensible interpretation or stronger existing-paper contribution | research-analyze | Claims map to evidence; requested contribution audit yields prioritized next work |
| Manuscript or revision text | research-write | Supported content and evidence gaps are distinguishable |
| Paper-facing claim/display specification | research-analyze | Question, comparison, denominator, uncertainty and bounded conclusion are linked |
| Reproducible table/figure/provenance generation | research-implement | Actual outputs and provenance reproduce; missing data remain missing |
| Scientific challenge and rework decisions | research-review | Material findings identify evidence, impact and destination |
| Submission/rebuttal package | research-submit | Package checks and action authorization are explicit |
| Product value and bounded MVP | research-product-discover | Need evidence, scope and acceptance are reviewable |
| Usable product and acceptance evidence | research-product-build | Functional/research/user checks have actual outcomes |
| Installable, distributable release candidate | research-product-release | Candidate readiness and publishing authority are explicit |
| Requested issue or compatibility/effect regression | research-product-maintain | Fix and affected outputs are checked, remaining work is stated |
| Bounded workflow improvement of a completed, delivered stage | research-optimize | Candidate set, revision and single publication are recorded inside its own bounds |
| Original theme, cumulative alignment or auxiliary-branch boundaries | research-focus | Provenance, theme/thesis versions, alignment and next scientific dependency are explicit |

## Dependencies by study type

- **Method:** use or implement minimal common measurement support; verify existing
  controls; implement the proposed mechanism; execute comparisons.
- **Evaluation/benchmark:** implement measurement and validate it against labeled
  or known-answer cases; run reference methods; evaluate the intended population.
- **Empirical analysis:** validate extraction/measurement and data definitions;
  establish meaningful controls/comparators; execute the analysis protocol.
- **Experiment/replication:** first identify valid existing code and data; repair
  only missing infrastructure before the bounded reproduction.
- **Mixed:** write a small dependency graph. A measurement component may be built
  before baseline validation even when a new method is built afterwards.

For open theoretical/method directions, survey structural connections across
disciplines, then formalize and attempt candidate theory in ideate. Once selected,
design deepens the argument and connects predictions to validation. Small authorized
checks can inform definitions; completing all proofs is not a gate for approved
informative experiments. Review checks arguments, and analyze feeds evidence back
to the affected definition, proof or implementation.
Do not fabricate an experimental stage for a pure-theory task or force a theorem
into an explicitly empirical study. Preserve existing valid project dependencies.

Before committing a topic, protocol or expensive experiment, use the
[reuse and simplification audit](reuse-and-simplification.md)
to check whether prior theory, methods, benchmarks or implementations can replace
or shorten current work. Preserve genuine contribution and the evidence supplied
only by the project's own experiments.

For full-paper delivery, read [Goal execution](goal-execution.md). Consolidate the
research/protocol gate at M1, engineering/pilot checks at M2, principal-conclusions
gate at M3, first complete-paper venue review at M4 and second venue review plus
submission/release gate packaging at M5. Internal reviews receive actual evidence;
venue-blind reviews receive only submitted materials and criteria. Preserve valid
checks instead of reviewing after every handoff. A result may require rework but
never authorizes submission or release.

## Return paths

- Cumulative topic drift or a side tool becoming the paper's subject -> focus,
  then the relevant scientific stage. An authorized in-theme pivot needs a
  recorded rationale, not a new topic vote. An out-of-theme proposal stays pending.

- Missing source, theoretical transfer conditions or unsupported novelty -> survey,
  then ideate only if the question/contribution needs changing.
- Existing-paper contribution strength or explanatory/theoretical opportunities
  -> analyze for an evidence audit and prioritized round, then the needed stage.
- Confounding, flawed metric, weak control or changed protocol -> design.
- Incorrect code, instrumentation or unexplained replication gap -> implement or baseline.
- Missing evidence under an otherwise valid plan -> experiment, then analyze.
- Missing proof or revised mechanism/identification test -> design; use theory
  work directly when empirical runs are not needed.
- Unsupported hypothesis -> analyze alternatives; ideate, redesign or stop.
- Unsupported wording with adequate evidence -> write.
- Product need/scope failure -> product-discover; implementation/usability failure -> product-build.
- Product behavior changes a scientific summary -> analyze the research impact
  alongside the local engineering fix.

Submission/release readiness and actual external submission/release are distinct
outcomes. A return route never authorizes the external action by itself.

For continued research, carry the shared round package through each dependency
and return actual outputs to analyze. Keep existing-data work in analyze when it
needs no other stage. Once approved findings meet the round's evidence goal,
route argument updates to write; queue independent review at the next applicable
milestone. Reopen only affected decisions; explicit startup delegation covers
in-scope conclusion formation and no new approval is required solely because a
round crosses a stage boundary. A completed round does not finish a paper Goal.

## Candidate-choice support

Where a stage compares genuine candidates - topic and transfer choices in survey,
direction selection in ideate, protocol and identification choices in design,
interpretation and reuse choices in analyze, theme-aligned pivot and auxiliary
scope choices in focus, disposition choices in review, and
routing between them in navigate - read
[native evidence comparison](decision-support.md). It is advisory: evidence and hard
program constraints decide first, then a bounded native comparison and the
integrator decision. No invented probabilities or model scores establish truth.
The evidence-linked comparison record is the deliverable.

## Optimizer event queue

Each substantial scientific stage completion queues one stable event for the sibling
`research-optimize` skill: stage identity, strengths, weaknesses, artifact and
evidence references, and the actual cost. The event does not trigger a full test
suite or a scientific review, does not authorize new scientific claims, and does
not delay a completed paper. Duplicate delivery of the same event is idempotent.
Read `research-optimize` for its authoritative bounds; this map records only the
routing edge and no new stage skill.
Focus and optimizer bookkeeping never generate new support events. Carry the
focus reminder into each scientific branch and keep it out of blind venue inputs.
