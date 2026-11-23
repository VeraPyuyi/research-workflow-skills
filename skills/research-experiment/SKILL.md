---
name: research-experiment
description: Use when a research protocol is ready for a pilot or formal runs, or when interrupted experiments, active jobs, failures, retries and resource consumption need reconciliation.
---

# Execute and Resume Experiments

Read the [shared contract](../research-navigate/references/workflow-contract.md)
and applicable [domain references](../research-navigate/references/domains/index.md).
For a substantive run, use [model routing](../research-navigate/references/model-routing.md) only when dispatching work to more than one model;
then use it to assign native status/log preparation and milestone execution review without
duplicating jobs or treating model calls as compute authorization.
For the configured SSH host, read [shared-server.md](references/shared-server.md)
and use `python scripts/remote_experiment.py` with the project's local host profile
(use the project-selected local profile; never embed a host or credential).
Resolve its credential reference at runtime. Share CPU, RAM and GPU capacity;
reserve bounded resources without default exclusive allocation. Query stable job
IDs before retries and retain running workflow/protocol/code versions across
suite updates.

## Reconcile before execution

For an improvement round, carry its identity and claim-to-test link into the run
manifest. Resume from its saved attempts and authorization rather than restarting
the research. Return actual artifacts, costs and unresolved jobs to that round
for research-analyze; an unfavorable result does not authorize additional runs.

For theory-driven tests, preserve definition/assumption revisions, the claim's
proof status and the prediction or applicability question being tested. Confirm
these and the protocol/resource authorization before formal runs. A proof gap
alone does not halt an approved test; numerical results cannot fill that gap.
Retain both agreement and disagreement with the prediction for analysis.

1. Confirm the applicable approved protocol/resource scope and actual environment.
   Inspect code/config/data revisions, measurement checks and existing run records.
2. Reconcile completed, failed, interrupted, pending and unknown-status attempts
   using stable job/attempt identities. Verify artifact completion rather than
   inferring success from a submitted job or a surviving process.
3. Compute available allowance using completed consumption and active commitments.
   If usage/status cannot be established, hold dependent launches and provide the
   exact operator/status request. Never duplicate a possibly running job.
4. Inspect the environment's real query, timeout and stopping controls. Do not
   promise automatic cancellation or a hard spending cap without such capability.

## Run the bounded plan

Reuse valid M1/M2 coverage and an already adequate pilot. Run a small validity pilot
when needed, then the approved matrix in manageable
batches. Retain raw outputs, configuration, versions, seeds/splits, environment,
logs, attempt status, timestamps and relevant resource units.

Retry only diagnosed transient failures within the agreed count and allowance.
Treat invalid measurement or data as a design/implementation issue, not as a reason
to run more trials. Preserve errors, negative outcomes and partial artifacts.
Stop expansion when the budget, validity or access conditions no longer hold.
Do not repeat the full engineering suite or convene a reviewer after every run.
Keep necessary status/budget checks and diagnose actual failures locally. Bundle
the completed evidence for M3; reopen M1/M2 only when their covered dependencies
materially changed. Scientific repetitions in the approved matrix are research,
not redundant process testing.

## Missing data, failed runs and infeasible checks

If required data, a run or a measurement is unavailable, report it as
unavailable. Never substitute simulated, synthetic, placeholder, interpolated,
remembered or silently sub-sampled values, and never fill a table cell from an
expectation. "Infeasible within the current data, access or resources" is a
valid, complete outcome of this stage; record the exact blocker and the
smallest action that would remove it. A deliberately synthetic fixture is
allowed only when the approved protocol names it, and every artifact derived
from it carries `data_kind: synthetic`. Sub-sampling is allowed only when the
protocol states the rule; record the rule and the counts before and after.

Record every attempt, including failed, interrupted and cancelled ones, as one
line in the project's run ledger (default `research/runs/ledger.jsonl`; see the
[default record layout](../research-navigate/references/records.md)): attempt
id, protocol revision and lock hash, code revision, configuration, seed/split,
status, output paths, data kind and consumption. A missing line is a finding.

## Deliver and finish

Deliver the run manifest, actual raw artifacts, completed/remaining matrix,
failures, consumption and recovery prerequisites. Use the shared handoff.
When no execution tool exists, deliver a clearly unexecuted task package.
Route usable records to research-analyze; return validity failures to implement,
baseline or design. Extra experiments require the relevant remaining authorization.

Example: a client timeout after submitting a training job does not establish that
the remote job stopped. Recover its identity and reconcile status and consumption
before considering a replacement attempt.
