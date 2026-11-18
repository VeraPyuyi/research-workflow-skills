# Final independent MathRSI / 6.2 code review

Date: 2026-11-18. Bounded read-only source review, approximately five minutes. No external calls, agents, full test suite, or source edits. Only this report was written. Existing scripts were inspected as data; the small check executed only the inspected pure math_work module in memory, with bytecode writes disabled.

## Findings

### [P2] Bind the original specification reference, not just its revision

Locations: `git-merge/skills/research-navigate/scripts/math_work.py:34` (comparison at lines 34–38), and the identical `m18/native/skills/research-navigate/scripts/math_work.py`.

`validate_math_work` requires `original_spec_ref`, but omits it from the fields compared with an available `parent_binding`. A child can therefore change from `brief#problem-A` to `brief#problem-B` while retaining revision `1`, parent task/obligation, owner, and return point, and validation succeeds. Revision labels are not globally unique across specifications. This defeats the original-problem identity check precisely when a coordinator supplies a parent binding.

Evidence: an in-memory packet with `math_work.original_spec_ref = "brief#problem-B"` and `parent_binding.original_spec_ref = "brief#problem-A"`, with the five currently compared fields equal, returned `[]` from `validate_math_work`. Both candidates have byte-identical math_work.py.

Suggested fix: compare `original_spec_ref` along with `original_spec_revision` whenever the parent binding is supplied; carry and check that specification identity in the return binding too. Add a focused negative case for two distinct specification references with the same revision label. Keep math_work optional for non-mathematical packets.

### [P2] Check the returning child against the parent's recorded delegation

Locations: `git-merge/skills/research-navigate/scripts/math_work.py:48` and `:61` (identity checks), with state mutation at lines 79–86; identical native candidate file.

`consume_return` checks that `child_task_id` is nonempty and differs from the parent, but never checks it against a recorded child or delegated obligation. A return naming an unrelated or never-dispatched child is accepted if the caller is the continuation owner and the parent/revision/return-point fields match. It can then supersede pending work and replace the parent's next action. The owner check controls who invokes the transformation; it does not catch accidentally misassociated child results supplied by that owner.

Evidence: parent `P1` had tasks `C4` (running) and `T5` (pending). A return with `child_task_id = "never-dispatched"`, matching parent metadata, and `supersedes_pending = ["T5", "C4"]` produced status `consumed`, changed `T5` to `superseded`, and set the next action. There was no record of the purported returning child. `C4` remained running. Repeating the identical event correctly returned `already-consumed` with no next action and unchanged state.

Suggested fix: require a persisted delegation binding for the returning child and validate its child ID, original specification/revision, and delegated obligation before recording consumption or superseding work. If the task list does not represent all delegated children, use a separate explicit binding rather than assuming task-list membership. Add a negative test for an unknown child and a sibling with a different delegated obligation.

## Other inspected behavior

- Optional math_work remains optional. Existing required-field checks, parent task/obligation/revision/return-point comparisons, continuation-owner checks, digest-based replay handling, and pending-only supersession were inspected. The focused check confirmed that running tasks were preserved and identical replay did not return a second action.
- Both current registries explicitly mark 6.2 entries pending and supply nonempty dispatch_block_reason values. Both admission implementations reject those blocked entries. Native model IDs use an explicit allowlist.
- Native review admission uses the shared family mapping, so Astra/Sol version changes do not create independent-review credit. Completion reuses review_errors, binds the frozen request to a separately recorded spawned agent, requires actual identity evidence, and rejects an actual/requested model mismatch. The explicit same-family bias exception leaves independent credit false.
- Release validation enforces the versioned native model set, rejects duplicate IDs and unexpected model fields, and checks canonical family identities for the version-2 registry. These were static checks, not a release build or exhaustive mutation test.
- preserve_custom_group preserves retained subscription/API members and custom rule order/fields, substitutes the listed retired free endpoints, removes blocked targets, and appends the two mathematical intents. Inspected the focused custom API/pause test as data; did not run it or apply a routing plan. The direct dispatch guard still requires provider_fallback to be exactly an empty list and rejects billed endpoints for free_only tasks.
- Goal recovery requires a nonempty explicit authority reference before a resume attempt and admits paused Goals only with resume_paused enabled. CLI also requires --resume for --resume-paused. No recovery operation or host RPC was performed.

## Coverage limits

This was a targeted independent review of git-merge and the sibling m18/native candidate, using whitespace-insensitive Git diffs where useful and reading the relevant helpers, routing registries, native admission/completion, release validation, recovery, and focused tests. The snapshot comparison confirmed that the available source baseline is the Magpie implementation; its broad native diff was not treated as a focused incremental native change list.

No complete test suite, build, release digest validation, live routing, concurrency/single-writer-lock integration, scheduler execution, or host identity attestation was performed. Existing test files and documentation are context, not evidence that tests passed. The pure return helper leaves persistence and actual continuation execution to its caller; those integrations were not exercised. No MathRSI behavior output or rubric was reviewed. No exact actual served reviewer model is asserted: host attestation was not available in this review.

Two actionable findings are reported above; no additional actionable issue was established within the bounded coverage. This is not a certification of the entire change set.
