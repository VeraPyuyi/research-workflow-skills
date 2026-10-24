# Theme, paper thesis and cumulative drift

Use existing project records; field names below describe logical content, not a
new database. Read this when establishing an anchor, assessing a pivot or doing
milestone alignment. Ordinary handoffs reuse the short reminder and current record.

## Provenance before reconstruction

Read the original request and subsequent explicit decisions, then the brief and
current artifacts. For chat references use the host's actual read tool; a title,
cached summary or another agent's assertion is only a lead. Record source/turn or
file location, inspected range and whether the boundary is user-stated, inferred,
proposed or unresolved. Later explicit user decisions can revise earlier scope.
If original sources cannot be recovered, state what is missing and keep the
anchor provisional. Ask only when ambiguity prevents the next concrete choice.

Do not retrospectively call a current draft or assistant-generated plan an
approved original theme. Inherited software names and convenient datasets are
implementation facts, not authority.

## Record in the designated project state

`research_focus` contains or references:

| Field | Contents |
| --- | --- |
| `theme_envelope` | Version; core phenomenon/question family; why it matters; audience/use; explicit boundaries; source refs and verification/gaps |
| `active_thesis` | Version; current question; intended contribution; evidence gaps; how this answers an important part of the theme; artifact refs |
| `autonomy` | Actual instruction allowing in-theme changes, existing scope/resource references and exceptions; absent permission is not inferred |
| `theme_history` | Previous envelope, new envelope and explicit user decision for each real revision |
| `pivot_history` | Round, old/new thesis versions, reason/evidence, cumulative comparison with the envelope, value impact and affected artifacts/checks |
| `branch_map` | Tool/subtask, target object, served claim, role, remaining effort/allowance reference and return/stop condition |
| `current_alignment` | Inspected artifact/round versions; classification, rationale, provenance gaps and next action; lightweight versus milestone coverage |
| `reminder` | Compact theme/thesis versions, this task's claim link, boundaries and return condition |

Keep old versions retrievable. An initial reconstruction is not a historical
pivot: record unknown past changes as unknown. Do not append duplicate history for
the same round, artifact and decision. Unchanged versions reuse their alignment.
The coordinator is the only writer of shared theme, definitions and thesis;
workers propose deltas without rewriting the baseline.

## Decide by scientific relationship, not word overlap

Ask these together, with evidence references:

1. Which important part of the theme does the new work answer? What changes for
   the target reader's understanding, method choice or use if it succeeds?
2. Does it test a central claim, enable a necessary measurement, or merely make
   an incidental task easier? What remains of the paper without that side task?
3. Across all prior pivots, have the phenomenon, audience, contribution type,
   evaluation target or value standard changed? Several locally small changes
   can replace the original question even when terminology stays similar.
4. Are easier tasks, substitute metrics, a fashionable theory, sunk implementation
   effort or limited available resources driving the choice instead of evidence?
5. Is the new claim supported, limited, contradicted or unresolved? Does a proposed
   explanation distinguish alternatives, or merely make the result sound valuable?

Use one alignment classification per assessed task/argument, with uncertainty
recorded separately:

| Classification | Meaning and response |
| --- | --- |
| `on-spine` | Directly advances the current important question; continue within authority |
| `in-theme-pivot` | Changes the specific question/method/claim but retains the broad phenomenon and value; record reasons and affected coverage, then continue if delegated |
| `auxiliary-only` | Useful support, no independent headline entitlement; bound role, resources and return to the main dependency |
| `out-of-theme-drift` | Replaces the broad phenomenon/value, violates an explicit boundary, or cumulatively substitutes another problem; do not adopt without a user decision |

Classification is a reasoned judgment, not a universal similarity score. Jev can
compare fully specified candidate mappings under its existing allowance rules;
it cannot prove relevance, authorize an envelope change or make unknown evidence
true. No automatic per-round decision-model call.

Narrowing a conclusion in response to evidence is not by itself drift. Preserve
credible nulls, failures, counterexamples and alternative explanations. Conversely,
calling a calibration script an "evaluation contribution" is insufficient: explain
its distinct value to the same research question, with novelty and evidence.

## Map cross-domain work and bound side branches

Write a concrete chain:

`source/tool -> project object and assumptions -> claim or decision served`

Distinguish direct application, missing-condition transfer and analogy. Record
which definition, testable consequence or inference becomes possible. A new
mathematical area is allowed; relevance does not require using the original tool.
An unconnected lemma is a candidate lead, not a contribution established by notation.

For every substantive auxiliary branch state its role (method support, lemma,
control, measurement, appendix or separate future project), a bounded output,
cost/remaining allowance reference and return condition. No fixed percentage here:
use the actual project's resources. A free call still consumes time and context.
Unknown budgets cannot justify new experimental commitments.

Example: a grouped bootstrap for a retrieval pilot improves uncertainty reporting.
It may finish when the existing scores have an appropriate uncertainty analysis.
A general-purpose resampling library is a separate project unless the user changes
the theme. A role/negation counterexample could instead support the same retrieval
question, but its mechanism and scope still require evidence.

## Correction, checks and paper delivery

At an ordinary stage handoff record the compact relation and next dependency.
Do not launch a separate audit or reread the entire history after each edit.
At M1-M5 compare the accumulated thesis changes and whole argument against the
same envelope (or its explicit user-approved successor):

- M1: question value, literature gap, theory/tool mapping and protocol relevance.
- M2: implemented tasks and metrics still test the stated question; engineering
  calibration is not silently counted as scientific performance.
- M3: principal conclusions retain importance without overstating evidence;
  all result directions and changed hypotheses remain traceable.
- M4/M5: title, abstract, contribution list, discussion and actual evidence tell
  the same appropriately scoped story. Private focus history stays author-side.

Out-of-theme drift can be contained immediately without a full new review:
stop expanding that branch, preserve its artifacts, and return to a valuable
authorized dependency. Offer a concrete scope decision only if the user must
choose between changing the theme and closing/continuing the original project.
Do not erase a useful side asset or restart valid completed experiments.

If a method, hypothesis or conclusion changes within delegated scope, record the
delta and reopen affected scientific coverage, without demanding a new user vote.
Explicit locked assumptions, external actions and expanded resources keep their
own approval boundaries. Focus cannot waive a scientific validity gate.

If the requested contribution is infeasible, retain truthful partial results and
state the limitation. Neither "stay on theme" nor "deliver a paper" licenses weak
claims, unbounded work, invented experiments or a guaranteed acceptance claim.

## Updating active projects

Adopt compatible validated suite releases through the existing
[update protocol](../../research-navigate/references/workflow-updates.md).
Load the changed instructions at a supported boundary. Preserve Goal binding,
jobs, budgets, manuscript/theory versions and completed valid check coverage.

When another chat is actively writing the project, hand it a separate update
packet with source references and proposed focus record. Let that owning
coordinator merge into the designated state at its next handoff. Do not race it,
create an alternative authoritative state, restart jobs or claim hot injection.
Record prepared, delivered, adopted and actually read as distinct observations.

Focus and optimizer are sibling support functions. Attach their notes to the
original scientific-stage event; neither completion generates another support
event. Optional refinement never delays a paper meeting its completion contract.
