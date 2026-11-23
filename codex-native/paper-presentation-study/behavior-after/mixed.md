# Mixed results: no average gain on the prespecified suite

Revision: mixed-v1. Evidence: supplied fixture version 1, `paper-presentation-cases.json`, case `mixed`. All quantities below describe synthetic inputs. The question remains whether method A improves average performance across the prespecified suite.

## Evidence and interpretation

| Quantity | Result | Meaning |
| --- | --- | --- |
| Paired task deltas, supplied order | +1, -1, +2, -2, 0, +1, -1, 0 percentage points | Eight tasks, each evaluated once; task labels 1-8 below are display indices. |
| Prespecified equal-task mean | 0 percentage points (sum 0 / 8) | No observed average improvement on this suite; no outcome is discarded. |
| Pattern | 3 gains, 3 losses, 2 unchanged; range [-2, +2] points | Heterogeneous observed outcomes; this range is descriptive, not a confidence interval. |
| Outcome-selected subgroup | Tasks 1, 3, 6; mean +4/3 points | The author selected the three positive outcomes after inspection and called them structured. This is exploratory and circular as evidence of a structure advantage. |

No task weights were supplied, so the suite summary uses one equal weight per task and states that convention. The tasks are not eight random seeds, and no random sampling of tasks is documented. Neither repeatability within a task nor uncertainty about a broader task population is identifiable here. A zero observed mean establishes neither equivalence nor that every task is unaffected.

A true interaction with independently defined task structure is one possible hypothesis. Selection on positive outcomes is an immediate alternative explanation for the favorable subgroup; run-to-run variability could also matter but was not measured. No intervention or independent structure confirmation separates these explanations. The name assigned to the selected tasks adds no mechanism evidence.

| Claim | Evidence/state | Missing evidence or next check |
| --- | --- | --- |
| X1: zero observed mean on this suite | Supported descriptively by all eight paired deltas. | Reconcile any later source correction before changing this finite-suite result. |
| X2: method A improves suite-average performance | Contradicted as a description of the observed single-evaluation mean; unresolved as an expected-performance claim. | Prespecified paired repetitions and an appropriate task/repetition analysis would assess repeatability. |
| X3: structure explains a favorable subgroup | Unresolved; outcome-based subgroup definition supplies no independent support. | Define and measure structure without outcome access; confirm on independent data and use a suitable intervention for a causal mechanism claim. |

## Attempt accounting

Eight prespecified evaluations contribute the eight supplied deltas. One additional exploratory attempt crashed before evaluation and lies outside this prespecified suite. It remains an unsuccessful, unscored attempt in the supplied attempt ledger; it is not a ninth zero and is not part of the denominator eight. Only this aggregate attempt description is available, not original logs, identifiers, or a crash cause. This paragraph retains the failure without inventing those records.

## Focused results subsection

### No observed aggregate improvement, with gains and losses across tasks

Method A has an equal-task mean paired difference of 0 percentage points across the eight prespecified tasks, each evaluated once. Three tasks improve, three decline, and two are unchanged; the observed differences range from -2 to +2 points. The aggregate therefore masks opposing task outcomes rather than a uniform absence of change. These single evaluations do not quantify repeatability or establish equivalence.

The three improving tasks were labeled structured only after their outcomes were inspected. Their favorable mean is exploratory and cannot establish that task structure predicts benefit or causes it. Outcome selection remains an alternative explanation. An extra exploratory attempt crashed before evaluation; it is retained in the attempt accounting but excluded from the prespecified eight-task mean because it was outside that suite and has no score.

## Figure specification and caption: X-F1

Reader question: how does the zero suite mean relate to the individual outcomes? Plot all eight paired deltas as horizontal dots in original task order, plus a separated diamond row for the equal-task mean (0). Use a percentage-point X axis spanning -2.5 to +2.5 with a zero reference line, and Y labels Task 1-8 (input indices), then Mean (8 tasks). Use one neutral dot style; do not facet or color the positive tasks as a prespecified structural group. Include no confidence bars or invented task attributes. Link X-F1 to X1-X3, fixture `mixed`, and the arithmetic in `internal/calculations.json`.

Propose a 3.25-inch-wide PDF/SVG with a PNG preview and labels of at least 8 points. The width is a proposed presentation choice. A future render should check the signs, zero line, distinction of the aggregate row, and readable negative values. No figure is rendered for this specification-only request.

**Caption.** Synthetic paired performance differences for method A across eight prespecified tasks, each evaluated once. Dots show all task differences in supplied order; the diamond shows the equal-task mean of 0 percentage points. Three tasks improve, three decline, and two are unchanged, with an observed range of -2 to +2 points. No inferential intervals are available. The three positive tasks were called structured only after outcome inspection; the plot does not encode that label as a prespecified group. One extra exploratory attempt crashed before evaluation, remains in the attempt accounting, and is outside the plotted suite.

## What would change the judgment?

No additional work is needed to report the current finite-suite arithmetic honestly. Reformatting, renaming the positive tasks, or dropping losses would not change its interpretation. Only a documented source correction could change that historical mean. To judge expected performance, a new prespecified analysis with paired repetitions on the unchanged suite could estimate within-task variation; preserve task dependence and weights and distinguish the new estimand from this single-evaluation result. More observations may still support no gain.

A structural hypothesis needs a definition fixed without outcome access and independent confirmation, with all relevant tasks and null/negative cases retained. A causal mechanism claim additionally needs a discriminating intervention or justified identification strategy. Investigating the exploratory crash could inform robustness, but its absent score cannot be imputed to improve the mean. These are focused proposals only; no additional runs or broader research loop are executed.

## Bounded handoff

Artifacts: explanation, claim map, results subsection, X-F1 specification/caption. Evidence: all eight deltas and the supplied failure/selection history. Status: requested analysis and writing complete; figure remains unrendered. Open issues: repeatability and independent structure evidence. Next step: deliver the bounded result, without changing the suite or initiating experiments.
