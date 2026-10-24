# Integrated implementation review — 2026-10-25

Disposition: two reproducible P2 scanner defects remain. The bounded Goal-recovery implementation has no additional functional defect established by this review. This is an offline implementation review and four-case instruction evaluation, not evidence of a real Goal resumption, automatic continuation, or submission readiness.

## Scope and identity

Inspected the requested Goal adapter, Goal-execution and workflow-contract references, research-review skill and leakage/venue references, and the two corresponding test files under `<workspace>`, plus their counterparts in `.build/goal-review-20261025/native`. Read the updated research-navigate entry instructions for the behavioral exercise. Inspected only the supplied synthetic submission fixture for submission-content decisions. Did not read behavior-rubric.json or previous assessments, inspect the actual private research project, launch another agent, call a real API, or operate any host lifecycle.

Actually served reviewer model and effort: unknown; no host receipt establishes them. Independence from the producer's model or context is unverified. No claim of model-independent review or actual external peer review is made.

## Actionable findings

### P2 — TAR end-of-archive silently drops trailing submitted bytes

Locations: `<workspace>/skills/research-review/scripts/check_submission.py:478`, `_Scanner.tar`, at the `member is None` break; native counterpart `<workspace>/.build/goal-review-20261025/native/skills/research-review/scripts/check_submission.py:476`. The private probe `reviewer-scratch/probe.py` constructs the reproduction under `tar_trailing`.

Reproduction: create a normal 10,240-byte stdlib TAR containing one eight-byte clean text member, then append a newline and a synthetic password assignment. Scan this 10,280-byte explicit input. Both editions returned no findings, only the nonblocking generic `manual_review` gap, and `automated_passed: true`. `submission_ready` correctly remained false. Repeated against the revised source after the user-reported fix; the omission persists.

Cause/effect: `tarfile.next()` stops at the TAR terminator; the scanner breaks without checking the remaining bytes. The submitted artifact's hash covers the tail, but its content is neither scanned nor recorded as unparsed. A nonzero tail or concatenated payload can therefore retain a credential or internal material while the report implies no blocking automated coverage gap. Mandatory manual review limits the consequence but does not make this report's missing coverage accurate.

Requested correction: distinguish permitted zero padding from nonzero unconsumed bytes; inspect such bytes within the existing limits and/or record an explicit blocking unsupported/unparsed-tail gap. Add a small regression for clean padding and a credential-bearing tail. No archive extraction or scientific rerun is needed.

### P2 — UNC-path regex has quadratic behavior below the byte cap

Locations: `<workspace>/skills/research-review/scripts/check_submission.py:39`, the UNC alternative of `_PATH`, called by `_Scanner.text`'s `pattern.finditer`. This pattern is unchanged by the concurrent fixes and is shared with native.

Reproduction: scan a string consisting solely of backslashes. Isolated matcher probes measured approximately 0.003 seconds for 1,000 bytes, 0.050 seconds for 4,000, and 0.905 seconds for 16,000. A separate actual scanner CLI invocation on a 64,000-byte file exceeded the probe's two-second timeout and was terminated; a repeat against the revised source also timed out. These are observed local timings, not a runtime guarantee or an extrapolated measurement for an 8 MiB file.

Cause/effect: the unanchored `\\{2,}` run can consume and backtrack over the remaining backslashes at each starting position before the required nonseparator host fails. Input byte/member/finding limits do not bound this work, and text scanning runs outside the optional PDF worker's timeout. A small malformed text or metadata input can stall admission checks well below the default 8 MiB input allowance.

Requested correction: make separator-run matching linear, for example by admitting the beginning of a run only once, or use a bounded recognizer. Preserve normal UNC detection and add a small adversarial timing/termination regression. The reviewer did not patch the implementation.

## Concurrent source repair

The user reported private integration evidence of false endpoint findings on Python indexing/slicing and matrix multiplication, missed workflow markers/chat URIs, and two regressions observed RED before a narrow fix. That private evidence and RED observation are attributed to the user; this review did not inspect the private supplement or reproduce the earlier RED state.

Independently inspected the revised `_PRIVATE_HOST`, IPv6 validation and `_INTERNAL` patterns. The source now requires explicit SSH context for the account/host alternative, skips invalid bracketed IP candidates, and includes project-state.json, research-focus, research-optimize and the declared thread/chatgpt-conversation URI schemes. Ran the two new tests plus existing private-network, report-redaction and placeholder/disclosure checks: all five passed on updated source. A direct mixed probe retained detection of a valid private IPv6 endpoint and an explicit private SSH endpoint. The new workflow-marker regression asserts a combined `internal_process` result; it does not independently assert that each marker is detected, nor cover every possible chat URL scheme.

At the source-update checkpoint, native still had the earlier scanner and test hashes and lacked both new tests; its three existing neighboring checks passed. Synchronization was announced by the user and was not performed by this reviewer. Final edition/hash status is recorded below after the last comparison; earlier native results must not be presented as verification of a later sync.

## Verified behavior and coverage limits

Before the concurrent fix, each edition ran exactly the two requested modules: seven Goal tests passed; the scanner module reported 18 tests with 16 passing and two skipped because this host does not grant symlink creation. Across both editions that is 46 passes, four skips and no failures/errors. No whole-suite run occurred. The updated-source delta checks above are separate from that baseline; they do not certify every test against the revised source.

Goal checks use fake RPCs only. They establish read-only default behavior, a required nonempty explicit authority reference before requesting resume, refusal to set active for paused/complete/usageLimited/budgetLimited/already-active states, the exact same-thread status-only mutation payload, objective/creation-time/budget and monotonic-usage checks, one mutation on busy-writer or transport-failure paths, and no automatic-continuation claim. An authority string records the caller's asserted instruction reference; it does not independently authenticate user intent. Actual installed-host schema compatibility, active-writer behavior, enforcement of exhausted allowances, successful recovery, and a later automatic turn remain untested. No database or lifecycle mutation was attempted.

Scanner checks cover representative local/JSON-escaped paths, credentials, private endpoints, internal scaffolding, permitted infrastructure placeholders and scientific AI disclosures; redacted reports; nested archives/metadata and bounded unsupported cases; forged short ZIP size/CRC handling; PDF fallback coverage gaps; explicit-input-only reads; and CLI refusal to overwrite the supplied input. Source/fixture hash snapshots were unchanged during the baseline probes. Symlink/reparse behavior was inspected in code but its two creation-dependent tests were skipped. POSIX traversal, Windows junction races, real PDF extraction/rendering and arbitrary document/image metadata were not empirically covered. The PDF test exercises the unavailable-parser fallback and raw strings, not successful pypdf extraction.

A home-relative path probe (`~/private-experiment/raw.csv`) was not detected. Record this as a candidate-detector coverage limitation; it is not evidence that a manual audit may accept the path. The scanner deliberately requires separate manual/visual review and never sets `submission_ready` true. Explicit placeholders are infrastructure substitutions, not evidence that a missing result, proof, citation or declaration is complete.

The supplied fixture produced exactly a local-path finding and a credential finding inside the second ZIP layer. Its incomplete PNG produced blocking `figure_visual_review` and `opaque_binary` gaps. Nothing establishes that the fixture is a complete scientific paper or reproduction package. Behavioral decisions are in the separate forward-behavior.md.

The instructions preserve M1–M5 cadence, two default complete venue rounds, scoped repairs and reuse of valid coverage. Native wording differs in routing/dispatch details and omits a local continuation paragraph from research-review/SKILL.md; its shared contract and Goal-execution reference still retain the continuation rule. No separate cadence or Goal-stopping defect is established from that difference.

## Final edition checkpoint

Final read-only comparison still found the announced source repair unsynchronized into the isolated native edition. This is a recorded integration prerequisite, not a claim that synchronization failed or permission for this reviewer to modify native. The source fixes are verified only to the delta-check extent above; native retains the earlier false positives and marker omissions until synchronization. The unchanged Goal adapter remains byte-identical across editions.

| File | Source SHA-256 | Native SHA-256 |
| --- | --- | --- |
| check_submission.py | 38c62a0eb0b7ffa9611f706cc04a3ef7ce27a0af2d00d4465169ca691d0141eb | 41fc3fd392c067f311d2fdfdd5a639f4ba0ff9927d14578d1ab76e9c711b79cc |
| test_submission_leakage.py | c35387ffbb1d3bb878831bf53f82660c18fbcdc808acc9c7a63defd7564fa554 | 91e0bd02d5c9a5174be712e12b041bb4d932d68e38a9a6af6a84402b38fdccdc |
| goal_recovery.py | 4792997d64911bf6b6e8570382a2f53fc6e0aee5d94aecde5bb9ad25dd3aba41 | 4792997d64911bf6b6e8570382a2f53fc6e0aee5d94aecde5bb9ad25dd3aba41 |

Review evidence is private under `<workspace>/.build/goal-review-20261025/reviewer-scratch/`; only this report, forward-behavior.md and that scratch directory were written by the reviewer. Source/test changes during the review were the user's concurrent integration work, not reviewer modifications.
