# LLM Adaptation

## Design and implementation

Identify whether the claim concerns training, adaptation, prompting, inference,
alignment or evaluation. Record model identity/revision, tokenizer, data revision,
prompt/system context, retrieval/tool context, decoding parameters and relevant
provider settings. When a hosted model revision is opaque, record that limitation.

Define task population and scoring before selecting successful outputs. Track
training/tuning/evaluation separation and possible benchmark contamination.
Specify comparable access to examples, tools, inference effort and tuning budget.
Methodological differences can be studied, but must be disclosed as differences.

For judge-based scores, define rubric, judge/version, presentation order,
calibration examples and handling of disagreements. Validate against suitable
reference judgments where available; automated preference alone is not a universal
measure of task quality.

## Execute and analyze

Preserve raw generations, prompts or safe references to them, attempt identities,
generation/scoring settings, failures, and resource records. Report relevant token,
latency, financial or training cost at an explicit unit and workload.

Match comparisons on task/example and on stochastic repetitions when the design
uses them. Separate between-task variation from repeated-generation variation.
Report invalid outputs, abstentions and API failures according to the protocol.
Use held-out confirmation when adapting prompts after observing evaluation results.

## Review and product

Check that claims distinguish capability, evaluator preference and deployed user
value. Trace prompt/model revisions to the reported result. Recheck provider/model
behavior after changes if the product depends on it. Record inaccessible training
data or unavailable model snapshots as reproducibility limits.
