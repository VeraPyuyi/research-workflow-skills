# Frozen Presentation Pattern Cards

Frozen after 60 discovery readings at 2026-10-26T12:24:29.177599+00:00, before holdout reading.
Examples are original editorial illustrations, not quotations. Evidence concerns
presentation, not proof validity or acceptance. All locators are PDF pages.

Titles, exact categories and official URLs are in [the source index](sources.md).

## P1: Turn a diagnostic question into a design obligation

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Explain why components exist and what would show they address the problem.

**Applicable when:** Method or explanatory work with distinguishable failure modes and component-level evidence.

**Action:** Name the unresolved question; introduce the mechanism it motivates; return to the same question in a controlled diagnostic or ablation. Preserve alternatives.

**Original example:** The aggregate score hides delayed failures. We therefore retain event order and test whether the proposed memory component changes delayed, rather than immediate, outcomes.

**Observed sources:**

- `cvpr-2025-5`, Introduction; Section 4.4: Two challenges motivate two modules and recur in ablations.
- `icml-2026-5`, Diagnostic sections; Figure 5: Diagnostic questions precede an implementable gradient mask.
- `iclr-2026-3`, Sections 4-5: Observed expert-evaluation failures motivate targeted adversarial probes.
- `acl-2026-4`, Sections 4-5: Repeated mechanism/evidence/limitation units connect a shared model to several interventions.

**Limit:** Ablation performance alone does not identify a causal mechanism. Do not retrofit a prespecified story to an exploratory diagnostic.

**Counterexample:** `cvpr-2026-5`, Table 1, p.7: Question-led organization coexists with blanket-win wording contradicted by cells.

## P2: Bridge formal results to interpretation without dropping conditions

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Help a reader understand what a mathematical statement changes.

**Applicable when:** Theoretical or identification work; also method papers using inherited guarantees.

**Action:** Define objects and assumptions, state the result and proof status, then explain the consequence with a worked case. Map ideal results to practical approximations explicitly.

**Original example:** Under Assumptions A1-A3, the bound shrinks with the intervention budget. The implemented approximation is not covered by this statement; its error is measured separately.

**Observed sources:**

- `iclr-2026-1`, Section 2.3: A theorem is followed by intuition and a small example.
- `iclr-2025-1`, Sections 3-4, Remarks: Remarks explain algorithmic implications of bounds.
- `icml-2024-3`, Theorem interpretations; Section 5: Interpretations preserve valid-versus-tight and sampling distinctions.
- `icml-2024-1`, Section 5; Remark 2: Ideal and practical algorithms have different computational and output guarantees.
- `neurips-2023-1`, Sections 3-5: Plain-language results distinguish identifiability, a conjectured necessity condition and proof-of-concept simulations.

**Limit:** An analogy or numerical example cannot close a proof. Intuitive explanations must retain quantifiers, assumptions and whether a bound is only an upper bound.

**Counterexample:** `iclr-2024-5`, Sections 3.3-5, pp.7-9: The paper qualifies upper-bound comparisons and impractical stochastic batch sizes; theory is not neural-network practicality.

## P3: Operationalize a capability before presenting rankings

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Make benchmark scores interpretable as measurements of a specified construct.

**Applicable when:** Benchmarks, evaluations and empirical taxonomies with inspectable tasks and scoring.

**Action:** Define capability dimensions, show representative tasks and measurement boundaries, assess evaluator validity, then compare methods by those dimensions.

**Original example:** We measure recovery after a tool failure, not general autonomy. The task examples and scoring rules distinguish recovery from avoiding the tool entirely.

**Observed sources:**

- `iclr-2024-3`, Figure 1; Sections 3-4: Skill taxonomy and agreement checks precede capability comparisons.
- `cvpr-2024-3`, Figure 2; Section 5.2: Capability examples and a bounded human-agreement check expose measurement scope.
- `icml-2025-3`, Figure 2; Sections 5-7: Concept detection and steering remain separate tasks with label-quality limitations.
- `iclr-2025-5`, Sections 2-3; Figure 1: Three generalization categories organize tests and failures.
- `acl-2026-3`, Sections 3-4: Task variants and worked metric examples precede consistency comparisons.

**Limit:** A taxonomy does not establish construct validity. Judge agreement on a subset or correlation with humans does not prove universal alignment or real-world efficacy.

**Counterexample:** `iclr-2026-3`, Section 6, p.10: Expert QA ratings do not establish therapeutic efficacy or multi-turn behavior.

## P4: Put comparison conditions beside the numbers

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Let readers see which rows are comparable without reconstructing the entire protocol.

**Applicable when:** Comparisons that differ by modality, data access, budget, backbone, sampling or metric population.

**Action:** Use meaningful row blocks or condition columns, explicit units and metric direction. Keep attempts, exclusions and conditional denominators visible. State uncertainty rather than imply it.

**Original example:** Both systems attempted 24 tasks. The table reports 21 and 19 successes; latency uses successful tasks only, so it does not measure end-to-end utility.

**Observed sources:**

- `cvpr-2025-2`, Tables 2-3: Modality indicators and grouped rows expose input differences.
- `cvpr-2024-2`, Table 2: Supplementary data and target-shot conditions are distinguished.
- `iclr-2024-2`, Table 1: Buffer sizes accompany accuracy and forgetting.
- `icml-2026-1`, Tables 1-2: Backbone blocks and temperature rows expose comparison regimes.
- `neurips-2025-2`, Table 2: Dataset blocks and mixed-training exceptions identify evaluation conditions.

**Limit:** Visible conditions do not make an unfair comparison fair. Do not fabricate error bars or interpret absent variability as zero.

**Counterexample:** `cvpr-2024-2`, Table 2, p.6: Bold entries do not consistently follow the claimed best-value convention; compute emphasis from values.

## P5: Give diagrams, captions and body text different jobs

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Make the scientific objects and argument readable without redundant prose.

**Applicable when:** Multi-component methods, task definitions and quantitative figures.

**Action:** The graphic encodes the comparison or object relationship; the caption decodes panels, marks and conditions; the body explains why it changes the claim. Use stable semantics across panels.

**Original example:** The diagram separates observation, intervention and evaluation. Its caption defines the arrows; the body explains which intervention distinguishes the two hypotheses.

**Observed sources:**

- `cvpr-2026-1`, Figure 2: Colored geometry/topology branches identify operations; body defines operators.
- `iclr-2024-3`, Figure 1: Parallel workflows introduce evaluation objects before detailed definitions.
- `icml-2025-3`, Figure 2: Shared examples and three panels distinguish tasks and training differences.
- `icml-2024-5`, Figure 1: Conceptual sampling arrows precede distribution assumptions.
- `neurips-2024-2`, Figure 1: Shared inputs branch into two architectural choices, with adjacent notation and definitions.

**Limit:** Conceptual diagrams are not measurements. Small prompts, formulas or photographs can become illegible when a complex pipeline is squeezed into a column.

**Counterexample:** `cvpr-2026-2`, Figure 2, p.4: Clear stage grouping still contains crowded miniature prompt text.

## P6: Let exceptions delimit the contribution

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Strengthen interpretation of mixed or negative evidence without changing its direction.

**Applicable when:** Aggregate gains with subgroup losses, limited guarantees, counterexamples or failed conditions.

**Action:** Report the prespecified aggregate and relevant exceptions, state competing explanations, and identify which conclusion survives. Mark post-outcome subgroup selection as exploratory.

**Original example:** The aggregate contrast is small. A data-selected subgroup motivates a prospective test; it does not yet establish a structure-dependent mechanism.

**Observed sources:**

- `cvpr-2026-1`, Sections 4.6-5: Unimproved void counts and computational cost bound controllability.
- `iclr-2025-2`, Section 7: Difficult digit programs delimit the capability narrative.
- `icml-2025-5`, Section 7: Score-estimation dependence qualifies directional-discovery performance.
- `icml-2024-5`, Example 2; Section 5.2: A counterexample limits collaboration and similar real-data effects are retained.
- `neurips-2025-3`, Sections 4-6: Null changes, opposing model effects and entanglement limits remain in the explanation.

**Limit:** No difference is not equivalence. A subgroup selected after outcomes needs independent confirmation; a mechanism label is not evidence.

**Counterexample:** `cvpr-2026-3`, Table 3, p.6: Best mean coexists with dataset losses; universal superiority would misstate the table.

## P7: Show the cost axis alongside the performance claim

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Explain an efficiency contribution and its tradeoffs.

**Applicable when:** Work claiming faster, cheaper, smaller, safer or more robust behavior with another quantity at risk.

**Action:** Define both quantities and their measurement conditions. Use paired tables, common-setting curves or a tradeoff plot; retain dominated or unfavorable regimes when material.

**Original example:** Latency decreases under matched settings. The observed accuracy difference is small, but equivalence needs a justified margin and an appropriate comparison.

**Observed sources:**

- `cvpr-2024-1`, Section 4.3; Table 5: Inference alternatives are paired with accuracy and relative speed.
- `iclr-2026-1`, Figure 4: Rate-quality curves appear beside overhead measures.
- `iclr-2026-2`, Figure 1; Section 4: Success and inference speed are compared, with task exceptions.
- `icml-2025-2`, Figures 3-4: Transfer and quality displays show different evaluation axes.
- `acl-2025-1`, Figures 3,5-7: Budget-matched comparisons and dashed oracle curves distinguish attainable performance from ceilings.

**Limit:** A Pareto frontier is conditional on the sampled configurations and metric definitions. Successful-only timing cannot silently represent overall completion cost.

**Counterexample:** `icml-2025-2`, Figure 4, p.7: Overlapping labels in a tradeoff scatter obscure some points despite a useful scientific question.

## P8: Treat readability and text-display consistency as failure modes

**Evidence level:** repeated-cross-venue-observation.

**Purpose:** Avoid imitating weaknesses that also occur in selected papers.

**Applicable when:** Final-size diagrams, multi-panel plots and result tables.

**Action:** Inspect actual rendered size; verify labels, scales, uncertainty definitions, precision and computed emphasis against source values. Repair only affected artifacts during drafting; consolidate full checks at the milestone.

**Original example:** A table cell is emphasized only if it satisfies the declared ranking rule. The caption defines the interval type and the body uses the same population and units.

**Observed sources:**

- `cvpr-2024-3`, Figure 8: Nonzero magnitude-bar baseline magnifies differences.
- `iclr-2026-2`, Figure 4: Shaded bands lack a local uncertainty definition.
- `icml-2024-3`, Figures 2-4: Some fine labels remain unreadable at the inspected detail scale.
- `icml-2024-5`, Figure 4 and adjacent body: Reference estimates and directional descriptions differ between caption and body.
- `acl-2026-3`, Table 4 and surrounding prose; future-work discussion: Metric naming and described model coverage are not fully synchronized across sections.

**Limit:** The observation is that such defects occurred, not that a fixed font or palette caused acceptance. Target widths come from the actual venue template.

**Counterexample:** `cvpr-2025-5`, Table 3 and Figure 6, p.8: The compact ablation table is readable, while neighboring heatmaps lack a numeric scale; assess each display separately.

## Editorial recommendations

- **R1:** Use a shared argument/display record and reproducible generator. Engineering response to observed consistency failures, not a claim that PDF authors used this workflow.
- **R2:** Use original calibrated sentence examples proportionally to the request. Editorial synthesis from condition/interpretation patterns; examples are not quotations or scored optimal wording.
