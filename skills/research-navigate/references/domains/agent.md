# Agent Adaptation

## Design and implementation

Specify task distribution, initial state, environment revision, tools/APIs,
permissions, user simulator if any, completion validator and termination rules.
Define the unit of success as the intended task outcome; intermediate successful
tool calls do not automatically imply episode success.

Distinguish agent failures, environment outages, evaluator errors and user/task
ambiguities. Predefine timeout, retry and exclusion treatment. Control access to
tools, context, memory, interactions and cost across comparisons, or explicitly
study their differences.

Calibrate validators against known terminal states before reference-agent runs.
For interactive benchmarks, test reset/isolation and leakage across episodes.
Do not assume a simulated user represents real user behavior without evidence.

## Execute and analyze

Retain trajectory/episode identity, initial state, actions, tool requests/results,
terminal state, validator outcome, interruptions and resource consumption. Use
redacted or access-controlled traces when full records contain protected data;
preserve the information needed to audit outcomes.

Report task success, failure types, repeated-run reliability where relevant,
latency, tool/intervention counts and cost. Keep the task and attempt denominators
explicit. Assess recovery and failure propagation, not only successful examples.

## Review and product

Test supported user journeys and tool failures within the actual permission model.
Distinguish benchmark success from deployable usefulness. Preserve a regression
set for terminal outcomes and tool-contract changes. State when evaluation uses
simulated environments, users or stub tools.
