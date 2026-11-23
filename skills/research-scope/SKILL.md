---
name: research-scope
description: Use when an AI research interest or problem needs a concrete question, study type, project brief, constraints, resource limits, or success and stopping conditions before topic and protocol decisions.
---

# Define the Research Task

Read the [shared contract](../research-navigate/references/workflow-contract.md).
Use the [domain index](../research-navigate/references/domains/index.md) to select
only relevant references. Paths are relative to this skill.
For a substantive brief, use [model routing](../research-navigate/references/model-routing.md) only when dispatching work to more than one model;
then use it
to assign free background/question-definition branches and milestone review ownership.

## Build a decision-ready brief

Use [research-focus](../research-focus/SKILL.md) to separate the stable broad
theme/value from the current paper question. Recover original instructions and
later decisions; mark inferred boundaries and missing provenance. In an existing
project, extend its anchor instead of resetting it to the latest brief.

1. Inspect supplied questions, code, papers, data and prior decisions. Describe
   what already exists and which facts remain unknown.
2. Define the intended scientific question and contribution type: method,
   experiment, evaluation, empirical analysis, or a stated combination. Distinguish
   the target phenomenon from a preferred technique.
3. Specify audience/outcome, population/task, observable success, unacceptable
   failure, existing assets, data/access constraints, available environment, time
   and resource ceiling. Mark proposals and unknown limits explicitly.
4. Include **stopping conditions** as part of the brief: what observation would
   invalidate the direction, what missing asset makes it infeasible, and what
   time/resource limit ends the current exploration. Unknown thresholds become
   explicit decisions, not implied unlimited work.
5. Recommend the smallest useful next step. Use survey for missing understanding,
   ideate for a choice among contributions, or design when a topic is already
   settled. Do not select paid infrastructure or a venue on the user's behalf.

## Deliver and finish

Deliver a compact task brief with question, study type, domain tags, outcome,
assets, constraints/resources, success/stop conditions, assumptions and decisions.
Without an existing convention, write it as `research/brief.md` (see the
[default record layout](../research-navigate/references/records.md)) with these fields so later gates can check
against them: `question`, `study_type`, `success`, `stop`, `budget`, `venue`,
`delegation` (protocol, conclusions, writing: yes/no each), `theory_mode`
(`required`, `default` or `none`), `human_checkpoints` (default: topic, protocol,
main conclusions, submission) and `premise_check` (what evidence shows the
phenomenon is real, so the project does not build on a false premise).
"Infeasible with the stated assets" is an acceptable brief outcome.
Use the five-field shared handoff. A brief can be complete as a proposal even when
a budget or topic still needs approval; that status does not authorize experiments.
For a full-paper request, establish the startup completion contract, venue/resource
choices and explicit in-scope decision delegation from
[Goal execution](../research-navigate/references/goal-execution.md). Consolidate
scientific proposal review at M1 rather than reviewing every brief revision.

Example: for "can a small model match a large model?", make the task population,
matching tolerance, data access and resource ceiling explicit before treating the
comparison as executable.
