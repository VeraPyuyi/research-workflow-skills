# MathRSI integration validation, 2026-11-18

The 18 skills preserve Goal, M1-M5, two fresh venue reviews, negative results,
privacy checks, same-profile updates and resource limits. This is a workflow
release, not a completed research paper or a scientific-success benchmark.

## Evidence

- Frozen baseline: source/installation/config hashes and raw cases/rubric captured
  before edits. Old routing/dispatch baseline: 42 tests passed.
- Full Magpie suite: 323 tests, 4 skipped, no failures. Native: 326 tests,
  5 skipped, no failures. Skips concern unavailable symbolic-link creation and
  the optional exact legacy-release fixture. Initial restricted runs hit Windows
  temporary-directory permission errors; they are retained as failed environment
  runs, followed by successful isolated runs.
- Final source review found two P2 return-binding bugs: original specification
  reference was not compared, and the returning child lacked a stored delegation
  check. Both were reproduced, repaired in both profiles and followed by four
  passing math contract tests per profile. This adds one test beyond the full-run
  counts. No new full-suite rerun was necessary after this localized fix.
- Both temporary installations match every packaged file byte-for-byte; see the
  profile release receipt. Runtime-profile separation and customization protection
  retain their existing tests. New model readiness/family checks and native
  completion receipts have targeted regressions.
- Independent exact arithmetic enumerated 32 colorings: marginal 1/8, joint
  1/16, independence product 1/64. The union bound supplies the parent coloring
  proof for at most seven four-element edges. This is not a formal-assistant run.

## Behavioral comparison and limitations

See `math-rsi-study/baseline-sol.md` and `after-behavior.md` for actual fresh-context
outputs. Both correctly rejected the independence claim and the invalid matrix
transfer. The new output also passed the common-witness case, preserving the
original problem gap. The principal measurable addition is executable structural
checking and once-only result consumption, not an observed increase in general
mathematical success rate. Both responses were requested from old 6.1 Sol;
exact served identity was not attested by the returned tool records.

The baseline executor accidentally saw the heldout entry when opening the shared
case file; it disclosed this and did not analyze it. Therefore that baseline is
not evidence of heldout-read isolation. The after executor was a separate fresh
context and received no rubric, baseline answer or expected solution. File access
was instruction-constrained, not filesystem-isolated. The original free baseline
request had not returned useful output at packaging time; it is not counted as a
successful free execution or model comparison.

A returned recommendation is not an actual next task. The pure return helper was
exercised for duplicate returns, unknown child, mismatched original problem and
pending-only supersession. Real scientific stage advancement and host-generated
Goal continuation are recorded separately in the deployment/resumption report.
No 6.2 calls were made: local model access remains unverified. Anthropic remains
removed and Vertex remains on its promotional-credit hold.

Project adoption preflight caught an accidental contract-version regression in
the unpublished first packaging attempt (1.0 versus existing 1.4). The final
release uses compatible contract 1.5 and fresh v2 release IDs; both temporary
installations and fingerprints were regenerated. No project adopted the rejected
1.0 candidate. This was a packaging correction, not a scientific-results change.
