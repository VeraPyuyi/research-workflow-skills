# Evidence-Led Paper Presentation

Read this when drafting or revising a full paper, a major section, or a
paper-facing figure argument. For a local sentence edit or a bounded abstract,
use only the applicable part. The observations summarized here come from a
frozen 90-paper study of CVPR, ICLR, ICML, ACL and NeurIPS papers; the source index and study limitations are in [the study index](paper-style-study/index.md). These are descriptive patterns,
not causes of acceptance and not a template to copy mechanically.

## Start with an argument, not a section outline

For a full paper, build a compact argument outline before prose. For a bounded
section or abstract, reuse the existing outline or capture only the relevant
claim, evidence and boundary; do not expand the assignment into a full outline:

| Field | Concrete content |
| --- | --- |
| Question | The phenomenon, decision or claim the paper resolves |
| Gap | What inspected prior work does not establish and why it matters |
| Core claim | One sentence whose strength matches current evidence |
| Supporting claims | Ordered claims needed for the core claim |
| Evidence | Source, run, derivation, table or figure supporting each claim |
| Conditions | Data, assumptions, population, budget and operating regime |
| Rival explanation | Alternative that the design or analysis distinguishes |
| Contribution boundary | What changes if the claim is true, and what remains untested |

Use section headings only after this map exists. Each section should answer a
reader question and make a specific contribution to the chain:

- **Introduction:** Why this question, what is missing, what the paper supplies,
  and what evidence makes the advance credible.
- **Related work:** The closest technical distinctions and the assumptions that
  make them relevant, not a catalogue of adjacent papers.
- **Method/theory:** Definitions and assumptions, the mechanism or argument, and
  the smallest example that makes it intelligible.
- **Evaluation/analysis:** Comparisons that can discriminate the claim, followed
  by conditions, failures and alternative explanations.
- **Discussion/limitations:** Scope, consequences and the evidence needed to
  extend it; not a generic disclaimer.

## Choose a research-type spine

### Method paper

Problem -> limitation of current mechanism -> design principle -> method ->
controlled evidence -> mechanism/boundary evidence -> cost and scope. Introduce
only the components needed to test the design principle. Explain a new module by
the failure mode it addresses, then report a baseline, an ablation or a controlled
diagnostic that distinguishes it from plausible alternatives.

### Theory paper

Intuition -> formal setting and assumptions -> result -> proof structure ->
interpretation -> validation of assumptions/predictions. Put the actual theorem
and quantifiers before its informal gloss. State whether each result is proved,
partly proved, conjectured or inherited. Examples illustrate; they do not replace
a proof unless the paper explicitly establishes the exhaustive case.

### Empirical or explanatory paper

Phenomenon -> competing explanations -> measurement/identification -> evidence
that separates explanations -> boundaries -> implications. State the estimand or
target quantity and selection rules. Label post-outcome groups and exploratory
analyses. A stable association does not become a causal mechanism by narrative
alone.

### Benchmark or evaluation paper

Capability or risk -> construct definition -> task/data construction -> validity
checks -> scoring and aggregation -> reference baselines -> diagnostic analyses
-> misuse and maintenance limits. Show what the benchmark can distinguish and
what it cannot. A new dataset is not automatically a new measurement claim.

## Build paragraphs that carry an argument

A reliable paragraph usually has a topic sentence, an evidence sentence, an
interpretive sentence and a transition. Vary this rhythm; do not force every
paragraph into four sentences.

- Make the grammatical subject the scientific object or action. Prefer
  "Caching reduces latency under matched decoding" to "It can be seen that..."
  when the evidence supports that direct statement.
- Put the comparison and condition next to the result. "The candidate is faster"
  is incomplete when latency is conditional on successful attempts.
- Use verbs with calibrated force: *observe*, *estimate*, *is associated with*,
  *supports*, *is consistent with*, *implies under Assumptions 1-3*, *proves*.
  Do not use *demonstrates*, *explains* or *causes* when the design supports only
  a descriptive association.
- Define an abbreviation once, use it consistently, and keep metric names stable
  across text, tables and captions.
- Prefer a short causal/conceptual chain over a list of implementation details.
  Move reproduction details to method, appendix or artifact documentation.
- End a paragraph with the consequence for the argument, not a generic claim that
  the result is "promising".

Original English examples (editorial recommendations, not quotations from the
sampled papers), to adapt rather than paste:

| Purpose | Calibrated move |
| --- | --- |
| Frame a gap | "Existing X assumes __; under __, this leaves __ unresolved." |
| State a contribution | "We introduce __, which makes __ measurable under __." |
| Report a result | "Across __, __ changes from __ to __; __ remains unresolved." |
| Explain cautiously | "One explanation is __; the current evidence cannot distinguish it from __." |
| Report mixed evidence | "__ improves under __ but not under __; the aggregate hides this dependence." |
| Bound a claim | "These results support __ for __; they do not establish __." |
| Connect evidence | "This comparison isolates __ because __ is held fixed." |
| Mark theory status | "Proposition 1 is proved under __; its application to __ remains a conjecture." |

Avoid stock openings ("In recent years..."), empty novelty adjectives
("novel", "powerful", "significant" without a statistical or scientific referent),
and claims that the experiments "validate the effectiveness" of a method without
stating the compared behavior and scope.

## Make figures and tables part of the argument

For every display item, write a one-line **reader question** before designing it.
Then decide what visual comparison answers that question. A paper-facing figure
specification should carry:

1. claim and question;
2. data/run identities and transformation;
3. comparison, unit, denominator and uncertainty;
4. encoding (position, color, shape, panel order);
5. caption/body division;
6. target width and readability checks;
7. limitations that the graphic cannot show.

Caption pattern: identify what is shown and the conditions; define marks,
aggregation and uncertainty; state the main quantitative contrast; point to the
panel that supports it. Put interpretation and implications in the body. Avoid a
caption that repeats the body paragraph or a body paragraph that merely narrates
the figure.

Use consistent semantics: one color/shape per method, explicit units and scales,
ordered panels that follow the argument, and error bars only
when their meaning is known. For categorical comparisons, show all attempts and
the relevant denominator; do not silently drop failures. For distributions, show
observations or an appropriate summary rather than a bar chart that hides spread.
Magnitude bars normally need a zero baseline. Lines, interval plots and logarithmic
scales need a scientifically appropriate, explicit range; do not force a zero
baseline that hides relevant variation. Record display choices in the shared
[argument and figure contract](argument-and-figure-contract.md).

## Revise for truth, then clarity

At a major revision or manuscript milestone, audit headline claims before the
style pass: identify evidence, status and boundary. During ordinary edits, check
only changed claims and their affected displays; do not repeat a whole-paper
audit. For the relevant scope, revise:

- abstract: question, contribution, evidence, boundary;
- introduction: a gap that the actual contribution answers;
- results: comparison -> number -> condition -> interpretation;
- discussion: what the evidence changes and what it does not;
- appendix: proof obligations, full protocols and material needed to check claims.

Check numerical identity across abstract, text, tables, figures and appendix.
Do not let a more fluent sentence change a denominator, uncertainty type, causal
strength or proof status. Preserve negative and mixed results. If evidence is
missing, leave a marked gap rather than manufacturing a narrative resolution.

## Privacy and submission surface

Submission-facing prose, captions, metadata, source comments and attachments must
not contain local paths, account names, private endpoints, internal agent
messages or project-history notes. Use neutral placeholders only when the venue
permits them. Keep an internal audit trail outside the submitted bundle.

Before full manuscript delivery, inspect the rendered manuscript and nested
artifacts, not only the Markdown/TeX source. A bounded edit checks its affected
surface. Report actual build and render coverage. This reference
does not authorize submission, data release or public code.
