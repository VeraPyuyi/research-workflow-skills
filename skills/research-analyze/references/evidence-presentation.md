# Evidence Presentation Planning

Use this when a result must become a defensible paper figure, table or results
subsection. It complements the
[contribution audit](contribution-audit.md): the audit decides what the evidence
can support; this reference decides how to expose that evidence without changing
its meaning.

## Plan from the question to the display

Write one row per intended claim:

| Field | Required content |
| --- | --- |
| Research question | The decision or phenomenon the reader must understand |
| Claim | Exact statement, with direction and scope |
| Comparison | Baseline, treatment, condition and matched factors |
| Evidence | Source/run versions, sample unit, denominator and uncertainty |
| Display | Figure/table type and why it answers this question |
| Bounded conclusion | What the display supports and what it cannot |
| Gap | Missing observation, test, assumption or implementation check |

If the display cannot answer the question with the supplied evidence, mark the
gap. Do not substitute a more attractive graphic for a missing comparison.

## Separate evidence from presentation repair

Classify each requested improvement:

- **Presentation repair:** numbers and comparisons already exist; improve
  ordering, labels, caption, aggregation or panel structure.
- **Analysis repair:** the data exist but the comparison, denominator,
  uncertainty, stratification or sensitivity analysis is missing.
- **Evidence repair:** new observations, experiments, proofs or source
  verification are needed.
- **Claim repair:** the evidence exists but the current sentence overstates
  causality, generality or certainty.

Presentation, analysis and bounded claim repairs can be completed from existing
evidence when within the request. Evidence repair needs the appropriate research
stage and existing authorization. Record the smallest missing action; do not
automatically expand a local analysis request into new experiments.

## Select a display by inferential job

| Job | Suitable display | Avoid when |
| --- | --- | --- |
| Overall level and denominator | Dot/bar with n and failures visible | A bar hides unequal attempt counts |
| Paired or repeated comparison | Slope/paired dot or difference distribution | Independent-looking bars obscure pairing |
| Distribution and spread | Strip, box/violin with observations, interval plot | Error bars lack a defined type |
| Trend or scaling | Line with units, axes and regime boundaries | Connecting unordered categories |
| Conditional effect | Faceted or stratified comparison | A single aggregate implies homogeneity |
| Ablation/mechanism | Ordered component removal plus diagnostic | Claiming mechanism from performance alone |
| Cost-effect trade-off | Scatter/line with both axes and budget | Reporting only the favorable axis |
| Benchmark reliability | Success/failure and conditional latency separated | Treating failures as zero latency |
| Table of exact values | Compact table with units, n and uncertainty | Excessive decimals or unlabeled arrows |

Choose position over color for the primary comparison; use color and shape as
redundant encodings. Keep the same method identity across panels. Use a common
scale when comparing panels unless a break is scientifically necessary and
explicitly marked.

## Preserve denominators and uncertainty

For each plotted or tabulated value retain:

- attempted and successful counts;
- exclusions and missingness;
- the population for conditional summaries;
- sample size or number of independent units;
- uncertainty type and level, or "not supplied";
- aggregation and transformation;
- the actual data/run and analysis revision.

Do not turn an unavailable uncertainty into zero, infer a confidence interval
from a standard deviation, or present a successful-only latency as overall
latency. A zero-success method has unknown successful latency, not latency zero.

## Explain mixed and negative results

Present the prespecified aggregate and the task/condition-level pattern together.
If a subgroup was chosen after seeing results, label it exploratory and preserve
the selection history. Compare at least one alternative explanation (for example
task difficulty, selection noise, implementation failure or resource difference).
Do not make the figure's visual grouping look prespecified when it was not.

Useful sequence: observation -> uncertainty -> competing explanations ->
discriminating evidence -> boundary. A null average can be informative without
establishing equivalence; a failure can be a result when the protocol and
attempt ledger are complete.

## Caption and body

The caption should state what is shown, conditions, encoding, n/denominator,
uncertainty and the main contrast. The body should explain why the contrast
matters and connect it to the claim. Neither should repeat the other. If the
caption needs a long proof or implementation history, move that material to the
body or appendix.

## Handoff to implementation and writing

Reuse the shared
[argument and display record](../../research-write/references/argument-and-figure-contract.md).
Give `research-implement` a machine-readable or tabular specification containing
the source data identity, transformation, panels, encodings, labels, units,
width, output formats and provenance requirements. Give `research-write` the
bounded conclusion and caption/body split. Keep the claim IDs stable so a later
data or revision change invalidates the right text and display.

Do not claim that a figure was rendered, a PDF was inspected or a table was
reproduced unless that operation actually occurred. Record the exact command,
output path and visual/structural check.
