# Shared experiment host

Use the local host profile named by the project, not an embedded server password.
The configured host's root contains per-project `inputs/` and `runs/<job-id>/`,
plus a common `.jobs/` reservation ledger. The SSH adapter pins the server public
key before authenticating and resolves a credential reference: `ssh-agent:`
(keys held by the running SSH agent, any platform), `keyfile:<path>` (an
unencrypted private key file; load encrypted keys into the agent instead) or
`wincred:research/<name>` (a password in Windows Credential Manager).
An initial `probe-key` reads a key without credentials. Record first-use trust
and pin that fingerprint; an unexpected later key change requires reconciliation.

Install the optional Paramiko dependency in the client environment. The host
needs Python 3.7 or later and SSH/SFTP (the controller was exercised on 3.7.3).
The Windows client uses the suite's Python 3.12 environment. The helper uploads its content-addressed
controller, not a service or a system configuration change.

From this skill's directory:

```text
python scripts/remote_experiment.py probe --config <local-host-profile>
python scripts/remote_experiment.py submit --config <local-host-profile> --packet <job.json>
python scripts/remote_experiment.py submit --config <local-host-profile> --packet <job.json> --apply
python scripts/remote_experiment.py status --config <local-host-profile> --project <id> --job <id>
```

Mutation commands default to a plan. `store-credential --apply` takes a hidden
interactive password; never place it in shell text or job JSON. `upload` accepts
one explicit input and a relative destination, refuses different existing bytes,
and reports its hash. `fetch` reads a named job artifact into a new local file.
`store-credential` applies only to `wincred:` references. `cancel --apply` writes a cancellation request for a confirmed protocol-2
supervisor. The supervisor reconciles its own child group; the client never
signals an unpinned numeric PID. A request is not confirmed cancellation. Active
legacy controllers require explicit reconciliation and keep their running version.

## Job packet

The packet names project/id, argv, authority reference, immutable budget identity
and total `budget_run_seconds`, `timeout_seconds`, resources (`cpu`, `memory_mb`,
`gpus: [{index, memory_mb}]`), workflow/protocol/code versions, and required relative
`outputs`. Empty GPU requests explicitly run CPU-only. Use project input paths
reported by upload; the command starts in its own run directory. Configure any
framework-specific GPU memory controls as part of the approved experiment.

The run-seconds allowance sums elapsed completed attempts and maximum durations
of active commitments; it is a measurable job-time budget, not wall-clock project
duration, API dollars or GPU-hours. Track those additional units when applicable.
Changing a recorded project's allowance requires a reconciled approval and
deliberate migration, not a different number in the next packet.

Multiple tasks may share CPUs, RAM and the same GPU. Admission checks available
RAM/GPU memory and all active reservations conservatively; reservation accounting
may underestimate usable capacity because observed free memory already reflects
some running jobs. This is safe admission guidance, not cgroup isolation or a
hard GPU-memory cap. External workloads can change capacity after admission.
CPU thread limits and visible GPU indices are passed to the child environment.

One atomic host lock serializes reservation and launch. Job identity plus packet
digest makes identical repeated submissions idempotent and rejects changed jobs
under the same identity. Unknown supervisor state holds new launches; inspect
records/processes rather than deleting the uncertainty. Do not remove a lock
without establishing that its owner is gone and the queue has been reconciled.

The host supervisor saves stdout/stderr, exit code, actual elapsed time, required
output presence and final state. A zero exit with missing required output fails.
Timeout/cancellation targets the owned process group; unresolved termination is
unknown and does not release the commitment as completed. No process or data
outside this workflow's owned records is stopped or removed.

The launcher stays unreaped until its session is reconciled, including children
that outlive the launcher. Work in another unpinned group keeps the state unknown
if it cannot be safely reconciled. Launchers must keep work in their observed
session: deliberately detached daemons are outside this cooperative controller's
containment. Cleanup grace and observation overhead are included in actual
elapsed usage; a workload timeout is not a hard whole-supervisor time limit.

Recheck permission, resource state and job identity at launch/resumption. Collect
normal runs for M3 rather than invoking complete testing/review after each job.
Each run pins its workflow and scientific versions; adopting a new skill release
does not edit an active run, protocol or result.
