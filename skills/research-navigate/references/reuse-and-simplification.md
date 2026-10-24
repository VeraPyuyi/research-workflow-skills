# Reuse and Simplification Audit

Use this audit when existing theory, methods, benchmarks or implementations might
replace, shorten or simplify a project's mathematics, code, experiment, analysis
or manuscript. The goal is to reuse sound prior work and preserve genuine
contribution, not to make the paper look novel by ignoring prior results.

## Trigger

Perform or request this audit when:

- a derivation, implementation or experiment is lengthy or expensive;
- topic selection, protocol design or contribution review begins;
- a result resembles a known theorem, algorithm, benchmark or empirical pattern;
- a new theory section, experiment or mathematical rewrite is proposed;
- review suspects duplicate contribution, redundant verification or an
  unnecessarily bespoke implementation.

For a bounded paper reading or local bug fix, check the directly relevant existing
work without expanding into a full survey.

## Audit record

For each candidate, record:

| Field | Required content |
| --- | --- |
| Current content | Exact derivation, code, experiment, analysis or text; version and location |
| Prior result | Source identity/version, inspected location, statement/implementation and scope |
| Condition mapping | Objects, assumptions, quantifiers, units and conclusion correspondence |
| Relationship | Direct reuse, needs argument, requires model change, analogy only, or no replacement |
| Simplification | Effect on proof length, code, experiments, cost, risk and clarity |
| Proof obligations | Equivalence, assumptions, counterexamples, tests or reproduction needed before use |
| Contribution impact | Whether novelty weakens and what explanatory or boundary contribution remains |
| Decision | Reuse, adapt, simplify, retain, reframe or reject |

Keep a separate source/proof status. A theorem statement read in a secondary
source is not the same as an inspected proof; an available library is not the same
as a validated replacement in this project.

## Decision rules

- **Direct reuse:** verify every hypothesis, quantifier, definition and applicable
  regime. Preserve the source and state the reused result explicitly.
- **Needs argument:** treat as a candidate only. Complete the mapping proof,
  implementation compatibility check or experiment before deleting the old path.
- **Analogy only:** use for hypotheses or explanation; never as proof,
  implementation replacement or empirical evidence.
- **Contribution affected:** do not hide the overlap. Reframe around the new
  mechanism, conditions, boundary, measurement, negative result or application,
  and send it through contribution review.
- **Experiment removal:** prior theory can replace only the mathematical claim it
  actually covers. Keep experiments that test implementation, generalization,
  mechanism, causal identification or real-task behavior unless a valid substitute
  provides the same evidence.
- **Implementation replacement:** run behavioral and scientific regressions,
  compare protocol compatibility and record the new dependency/version. A simpler
  library is not automatically a valid reproduction of the original method.
- **Failure:** retain rejected reuse attempts and the reason. A failed transfer
  may reveal a useful boundary or assumption.

## Stage responsibilities

- `research-survey`: search primary sources and reusable artifacts; build the
  candidate table and report search coverage.
- `research-ideate`: test whether a candidate is only a renamed prior result;
  reuse sound foundations before inventing new notation or proofs.
- `research-design`: convert reuse into proof obligations, implementation
  substitutions and an explicit test of whether each experiment remains necessary.
- `research-implement`: prefer maintained, verified libraries and algorithms;
  test replacements against the approved behavior and preserve provenance.
- `research-analyze`: compare the old and simplified paths, quantify the actual
  benefit, and update affected evidence and contribution claims.
- `research-review`: independently check conditions, circularity, citation support,
  experimental necessity and the remaining contribution.
- `research-write`: distinguish prior results, adaptations and project additions;
  preserve citations, proof status and scope.

Return a simplification that changes the research question, central assumptions,
principal conclusion or resource plan to the applicable human decision gate.

