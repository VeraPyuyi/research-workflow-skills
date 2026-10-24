# Integrated review disposition

Date: 2026-10-24. One fresh-context independent release review examined actual
code, skill contracts and focused failure probes. It identified five actionable
issues. This disposition records the resulting author repairs and final
integration tests; it is not a second independent sign-off or a scientific
peer review.

| Finding | Repair | Verification |
| --- | --- | --- |
| Blind reviewer lacked an unambiguous manuscript location | Native packets require a canonical absolute submission root; generated neutral prompts list exact allowed files and hashes. | Different working directories, identically named bundles and changed manuscript bytes are covered in `tests/test_dispatch_guard.py`. |
| Completion could be assigned to another task or worker | Admission digest, task ID and actual spawn-returned agent are bound in a separate coordinator record. Completion must match; mismatch retains capacity. | Cross-task replay, wrong IDs/digests, live inventory and CLI record preservation are covered in `tests/test_dispatch_guard.py`. |
| Runtime labels could disagree with real routing | Manifest, release and routing must agree; build and inspection validate native workers and its separate optional Jev service. | Both profile directions, installed inspection, actual legacy migration and forbidden generative routes are covered in `tests/test_workflow_release.py` and `tests/test_bundle.py`. |
| Luna extraction could qualify as optimizer publication review | Native principal independent reviewers are restricted to Sol/Astra, distinct from the author. Jev cannot qualify. | Real candidate/control fixtures reject Luna and Jev-score objectives in `tests/test_optimizer.py`. |
| Review file references admitted unsafe aliases | Raw portable components, regular-file existence, containment, aliases and reparse markers are checked before use. | Real-file path cases and a reparse-marker regression pass. Some OS link-creation cases skip because this host lacks the needed Windows privilege. |

The coordinator also reconciled a real integration mismatch: the shared release
helper initially expected a list of decision services while the native adapter
used a keyed service registry. A focused failing test reproduced the mismatch.
Both now use the native `decision_services.jev` contract with the fixed official
endpoint, environment credential reference, explicit runtime whitelist, separate
pool and no generative/review eligibility. Targeted tests and the final suites
passed after that repair.

The native standalone Jev adapter has offline coverage for Choice/Score/Noul
schemas, abstention, credentials, credit authority, model whitelist, response
validation, error handling, limited retry, unknown completion and receipt/cache
invariants. No live Jev inference was performed because remaining credit could
not be verified.

The shared profile repair applies to both branches. Native-only repairs and their
tests are in the `codex-native` branch; the Magpie suite retains its own dispatch
implementation and tests. Code/structure and isolated-install results for this
branch are in `tests/results/release-code-validation.json`. Actual live probes
and their unresolved limits are recorded separately in `docs/release-validation.md`
and `tests/results/live-validation.json`.

No claim is made that instruction-only reviewer access is filesystem isolation,
that a coordinator journal is remote cryptographic attestation, or that local
passing tests establish research quality or acceptance probability.
