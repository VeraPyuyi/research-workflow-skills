# Mixed-results case

Synthetic acceptance material, not a real paper or new experimental result.
Skills used: the old research-analyze and research-write skills.
Source: fixture version 1, `cases[id=mixed].evidence`.

## Interpretation

The estimand available from the fixture is the equally weighted mean paired
performance change across the eight prespecified tasks, with each task evaluated
once. It is 0 pp: the deltas sum to zero. The median is 0 pp, the range is -2 to
+2 pp, and the sample SD across task deltas is 1.31 pp. That SD describes
heterogeneity across these tasks; it is not a standard error, confidence
interval, or estimate of variation across random seeds. No task-population
sampling design or repeat evaluations were supplied.

| Task position in supplied array | Paired change (pp) |
| --- | ---: |
| 1 | +1 |
| 2 | -1 |
| 3 | +2 |
| 4 | -2 |
| 5 | 0 |
| 6 | +1 |
| 7 | -1 |
| 8 | 0 |
| Mean over all eight tasks | 0 |

Task positions are locators, not invented task identities. Three tasks improve,
three worsen, and two are unchanged. The three positive tasks have a mean change
of +1.33 pp, but they were selected after their outcomes were inspected. Calling
them "structured tasks" supplies no independent evidence for that category or
for a mechanism. The full-suite observation does not demonstrate an average
improvement, and its zero mean does not establish equivalence or no underlying
effect.

The attempt record also contains one extra exploratory run that crashed before
evaluation. Keep that failed attempt visible, with its supplied status and
exclusion reason. It is outside the prespecified eight-task suite, has no task
score, and is neither inserted as a ninth task nor assigned a zero effect. No
crash cause, elapsed time, or recovery outcome was supplied.

## Focused results subsection

### No observed average improvement across the prespecified suite

Across eight prespecified tasks, each evaluated once, method A has an equally
weighted mean paired change of 0 percentage points. Three task deltas are
positive, three are negative, and two are zero; effects range from -2 to +2 pp
(Figure 1). The sample SD across task changes is 1.31 pp and summarizes
between-task spread. These synthetic observations provide no observed average
advantage on this suite; they do not resolve repeated-run uncertainty,
generalization to other tasks, or practical equivalence.

After inspecting outcomes, the three positive tasks were grouped and labeled
"structured." This post hoc grouping is exploratory. Neither an independent
structure definition nor held-out confirmation or an intervention was supplied,
so we make no structure-specific benefit or mechanism claim. A separate
exploratory attempt crashed before evaluation and remains in the attempt ledger;
it is excluded from the fixed eight-task summary because it was not part of that
prespecified suite.

## Figure and caption

Use one horizontal dot plot in the original task order, labeled "Task position
1" through "Task position 8". The horizontal axis is "Method A paired change
(percentage points)", spanning -2.5 to +2.5, with a vertical reference line at
zero. Plot all eight supplied deltas as the same marker and print their signed
values. Add a separated diamond row labeled "Eight-task mean" at zero. Use no
post hoc subgroup colors, sorting by performance, or uncertainty bars. Mark the
figure as synthetic. The exploratory crash belongs in the caption/ledger, not
as a fabricated score on this plot.

Caption: "Synthetic paired performance changes on eight prespecified tasks,
each evaluated once. Positions follow the supplied array. Three changes are
positive, three negative, and two zero; the equally weighted mean is 0 pp
(diamond). No repeated-seed uncertainty is available. The later 'structured'
label was selected after observing outcomes and is not a confirmed moderator.
One separate exploratory run crashed before evaluation and is retained in the
attempt record outside the eight-task denominator."

## What additional work could change the judgment

1. Reconcile the original task scores, scoring definitions, pairing, and attempt
   records if they become available. Only a documented scoring or inclusion
   correction can change the arithmetic conclusion for these exact eight
   observations; preserve the old revision and disclose any correction.
2. For expected performance over repeated executions of this same suite, define
   the repetition and pairing design before collecting further results. Retain
   failures under a declared policy, choose repetitions for useful precision,
   and specify any practically relevant margin in advance. New matched repeats
   could support an expected advantage, a disadvantage, or continued uncertainty.
   They would not erase the original zero mean.
3. For generalization beyond this suite or a structure-specific benefit, define
   the target task population and operational structure criteria without using
   evaluation outcomes. Test the prespecified full-suite effect and subgroup
   contrast on independent held-out tasks, retaining adverse tasks. Confirmation
   of a subgroup contrast would change that narrower judgment, not retroactively
   make the post hoc discovery confirmatory.
4. A causal mechanism claim needs a discriminating intervention or controlled
   perturbation of the proposed structural factor with relevant conditions
   matched. A successful subgroup replication alone would not establish the
   mechanism. Diagnose the extra crash before any separately authorized rerun;
   a successful retry would not revise the frozen suite's denominator.

These are proposed checks, not executed work. No further experiment is needed to
report the bounded descriptive result and its uncertainty limits. Do not replace
the prespecified question with a positive-only subgroup claim.

## Claim evidence and handoff

| Claim | Supplied support | State |
| --- | --- | --- |
| Observed average improvement across the eight tasks | Mean of all eight deltas is exactly 0 pp | Contradicted as a positive observed mean; broader expected benefit unresolved |
| Heterogeneous task outcomes | Three positive, three negative, two zero; range -2 to +2 pp | Supported descriptively for the fixed suite |
| Confirmed benefit on structured tasks | Outcome-selected positive subset only | Unresolved; selection and absent independent category validation |
| Structure causes the observed benefit | No intervention or independent mechanism evidence | Unresolved |

Artifacts: this subsection and figure specification; exact summaries and source
fingerprint in `case_calculations.json`, with runnable `case_calculations.py`.
Status: bounded analysis and writing completed; no figure render, new evaluations,
crash recovery, or independent model review was performed. External routes were
skipped under the user's no-external-model instruction. Recommendation: report
the full-suite zero mean and heterogeneity, retain the crash record, and keep
subgroup and mechanism claims exploratory. Additional research requires its own
protocol and inputs; none is silently launched here.