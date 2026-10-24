# Reinforcement Learning Adaptation

## Design and implementation

Specify online/offline setting, environment and wrapper revisions, observation and
action definitions, reward, termination versus truncation, discount, and evaluation
policy. For offline work, record behavior-policy coverage and data collection.

Declare training interactions/samples, tuning allowance, evaluation episodes and
compute budgets. Keep training/model selection separate from final evaluation.
Match comparison resources or explicitly report why they differ.

Validate environment resets, reward accumulation, terminal handling and policy
evaluation on small known cases. For multi-agent settings, identify opponents,
coordination/information assumptions and evaluation population.

## Execute and analyze

Retain run/seed identities, learning curves, evaluation episodes, checkpoints,
selection rules and failures. Distinguish training seeds from episodes nested
within a trained policy; treating all nested episodes as independent training
replicates can misstate uncertainty.

Analyze paired seeds/tasks where justified, the distribution across runs and tasks,
sample efficiency and final performance. Use an aggregation and uncertainty method
suited to the task suite and sampling design. Do not select only the best seed or
checkpoint after reviewing final test outcomes.

## Review and product

Separate simulator performance, offline estimates and actual deployment outcomes.
Report reward changes and environment shifts. For causal claims about policy
effects, also apply the Causality reference; predictive fit or high simulated
return does not by itself identify effects in observational deployment data.
