# Select Domain References

Use explicit project tags or infer only clear task relevance. Read the applicable
reference(s), focusing on the current stage; skip irrelevant checks with a reason.
These are composable tags, not mutually exclusive categories.

| Domain | Reference | Typical relevance |
| --- | --- | --- |
| LLM | [LLM](llm.md) | Language-model training, prompting, generation and judging |
| Agent | [Agent](agent.md) | Tool use, interactive tasks, environments and trajectories |
| DL | [DL](dl.md) | Neural-network training and empirical generalization |
| RL | [RL](rl.md) | Policies, rewards, interactions, offline/online learning |
| Causality | [Causality](causality.md) | Effects, discovery, causal representations and identification |

For LLM + Agent, combine model/decoding/judge records with end-to-end task traces
and tool budgets. For RL + Causality, combine policy/environment and interaction
records with identification, overlap, confounding and intervention assumptions.

During design, reconcile incompatible measurement, budget, unit-of-analysis or
identification assumptions explicitly. One domain's score does not substitute
for another domain's required evidence. Do not load other domain documents merely
because the suite supports them.
