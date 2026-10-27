# Integrated review disposition

A fresh-context reviewer inspected the actual study records, before/after
outputs, changed instructions, helper and tests. The reviewer did not modify
files, rerun the writing tasks or call external model services.

| Finding | Disposition and evidence |
| --- | --- |
| Stale release metadata describes the prior suite. | Rebuild each runtime profile only after final checks; bind separate receipts to exact content digests and inspect them before installing. See release receipts and deployment record. |
| Report does not yet compare completed behavior outputs. | Added the four-case comparison and explicit baseline strengths in `behavior-assessment.md`; report links actual portable outputs. |
| Executor receipt excludes later parent PDF rasterization. | Keep original executor scope and hashes; add separately attributed `behavior-after/parent-inspection.json`. |
| Figure/table source locators are only checked against text pages. | Require a figure/table locator to intersect a detail page actually viewed. The new regression rejects a text-only page. This is a record-consistency check, not proof that every label or every cited page was visually inspected. |
| Table PDF/PNG not asserted in tests. | Add both required outputs to the artifact contract test. |
| Historical local validation records contain private paths. | Exclude all historical `tests/results` from publication; preserve originals locally. Publish sanitized current acceptance evidence under this study directory. |
| CVPR 2026 metadata frame is incomplete. | Disclose 200 rows and 82 null decisions in report and installed index. No representativeness claim. |
| Repeated ICLR access-log event. | Preserve the original event log and explain that event count is not paper or distinct-failure count. No scientific effect. |
| Private discovery hashes have no per-paper independent clock. | Preserve frozen card hashes and consolidated readings. Chronology is receipt/hash-based; no independently clocked reading audit is claimed. |

No scientific blocker was found in the four synthetic outputs or recomputed
study records. Remaining limits include single-reader holdout coding,
unverified served-model identity, instructed filesystem separation, uninspected
appendix/fine-label content, unrendered specifications in three cases, and
environment-dependent rendering hashes.
