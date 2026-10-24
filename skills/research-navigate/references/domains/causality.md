# Causality Adaptation

## Define the claim

Identify effect estimation, causal discovery, causal representation, intervention
design or another causal task. State the target population, variables, time order
and target quantity/structure/representation. Draw a causal graph when useful;
the graph encodes assumptions and is not evidence that those assumptions hold.

## Design and implementation

List identification or recoverability assumptions appropriate to the task:
confounding, selection, measurement, consistency, interference, positivity/overlap
or structural assumptions as applicable. Explain which are supported, testable,
untestable or contradicted. Do not silently assume away unmeasured confounding.

Separate identification from estimation and numerical implementation. If the
target is not identified from available information, propose a justified
restricted estimand, bounds/sensitivity, additional measurement or a different
study design. A predictive analysis can continue under a descriptive claim.

For discovery, define graph equivalence, interventions or ground truth available,
and evaluation of orientation/structure. For causal representations, state
identifiability and intervention/transfer assumptions; prediction accuracy alone
does not validate a causal interpretation.

## Execute and analyze

Keep data provenance, treatment/exposure assignment, overlap/missingness,
estimators and nuisance-model choices. Apply sample splitting/cross-fitting when
required by the chosen estimator, not as an unexamined universal rule.

Check implementation on known synthetic mechanisms when useful; identify these
results as simulation. Analyze sensitivity, alternative assumptions and the
sampling/estimation uncertainty relevant to the claim. Distinguish sampling
precision from uncertainty about identification.

## Review and product

Trace each causal assertion to its assumptions and evidence. State what can change
when population, policy or measurement changes. Product recommendations should
retain the claim's limits; a convenient interface must not upgrade an association
into an intervention guarantee.
