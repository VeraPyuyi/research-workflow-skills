# Goal Recovery and Submission Leakage Validation

Checked October 25, 2026 (Asia/Shanghai).
Profile: `codex-native`.
Release: `research-20261025-goal-leakage-v6-codex-native`.

## Changes

The existing 18 skills now distinguish a coordinator message from native Goal
activation and a subsequent host-triggered Goal turn. The recovery helper uses
the installed official experimental app-server interface, is read-only by
default, requires explicit resume authority, and preserves the same objective
and resource limits. It refuses unsupported states and does not create turns.

Research review adds an author-side submission audit at M4, M5 and delivery:
actual submitted source, rendered pages, metadata, figures and nested attachments.
Private paths, credentials and accidental internal agent material are removed
from submission copies; original evidence is retained privately. Relative paths
and explicit infrastructure placeholders are allowed. Scientific AI content and
required use declarations remain accurate.

## Concentrated code and behavior validation

- 288 distinct tests covered: 281 passed,
  7 explicitly skipped, no failures/errors.
- Counts combine the initial full suite and four added regressions. The final
  affected modules ran 29 tests: 27 passed, two link-privilege skips. Unrelated
  full suites were not repeated after narrow repairs.
- All 18 official skill validators, reference checks and an isolated installation
  with byte-for-byte comparison passed on the final edition.
- Four fresh-context synthetic cases met frozen criteria. The executor received
  the requests and instructions without the grading rubric. Its actual served
  model is unknown; this does not certify model independence.
- Review found TAR trailer coverage and pathological UNC matching defects;
  integration found Python syntax false positives and missing workflow markers.
  All four have observed RED-to-GREEN regression evidence.

Windows privilege skips do not establish actual symlink creation behavior; the
other skips concern an unavailable exact legacy fixture or existing profile
scope. See code validation (local record `tests/results/goal-leakage-code-validation.json`; withheld from the public repository because it contains private paths),
behavior (local record `tests/results/goal-leakage-behavior.json`; withheld from the public repository because it contains private paths) and
review disposition (local record `tests/results/goal-leakage-review-disposition.json`; withheld from the public repository because it contains private paths).
The earlier review is retained as a dated pre-repair finding record.

## Live Goal recovery remains incomplete

The actual affected native Goal still reads **blocked**. The original desktop
instance rejects an external writer even after its research turn completes.
The original UI recovery attempt has no confirmed state change. Its objective,
creation time, budget and accumulated usage were preserved. No post-repair
automatic Goal continuation was observed. The next required action is successful
resume through the original host, followed by separate observation of a later
host-triggered turn with no intervening coordinator continuation message.

This release passes the offline skill-delivery gate; it does **not** certify
that the affected live project has resumed or reached paper completion. See the
runtime status (local record `tests/results/goal-leakage-runtime-status.json`; withheld from the public repository because it contains private paths).

## Submission coverage limits and cadence

The scanner's `automated_passed` is separate from `submission_ready`; it never
asserts readiness on its own. Bounded/unsupported archives, missing PDF parsing,
visual content and other unchecked surfaces are recorded. PDF text extraction
was unavailable in the exercised default environment; raw-byte candidates may
be false positives and require adjudication. Do not upload private inputs to an
external detector or treat missing coverage as a pass.

Final-source scanning of an ongoing project was performed read-only and retained
privately. Required PDF/size-limited coverage remains for its owning project to
resolve. This is not a claim that its submission is fully sanitized.

Valid existing evidence is reused. Routine edits receive affected-scope checks;
full review stays at M1-M5. No extra full peer-review round, model-ranking call,
scientific rerun, budget increase, external submission or public release was
performed by these repairs. Local receipts and project-specific records are not
included in this portable release.
