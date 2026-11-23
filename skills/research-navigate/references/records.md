# Default Record Layout

Use this layout when the project has no established convention for the logical
records in the [workflow contract](workflow-contract.md). An existing tracker,
lab notebook or repository layout still takes precedence; then map its files to
these fields once in `research/STATE.json` (`record_paths`) so the checks below
can find them. The layout is a serialization of the contract, not extra work:
each file replaces prose that would otherwise be written into handoffs.

```text
research/
  STATE.json              current milestone, next action, coverage, focus, Goal
  brief.md                task brief (question, study type, success/stop,
                          budget, venue, delegation, theory_mode, checkpoints)
  focus/anchor.md         research_focus: theme_envelope and active_thesis
  literature.jsonl        one source per line
  protocol/P3.md          protocol revision
  protocol/P3.lock        hash lock of that revision
  protocol/evaluator.lock hashes of evaluation code and data manifests
  runs/ledger.jsonl       one attempt per line, failed and cancelled included
  analysis/claims.jsonl   one claim per line
  paper/                  manuscript sources, figures, provenance
  reviews/panel.json      blind-review ledger (see research-review venue review)
  reviews/calibration.json reviewer calibration per venue profile
```

## Fields

`STATE.json`

```json
{"schema_version": 1, "milestone": "M2", "stage": "research-implement",
 "next_action": {"stage": "research-experiment", "state": "ready",
                 "inputs": ["protocol/P3.md"]},
 "coverage": {"M1": {"status": "passed", "artifacts": {"protocol/P3.md": "<sha256>"}}},
 "research_focus": "focus/anchor.md", "goal": null, "record_paths": {},
 "updated": "2026-11-23T10:00Z"}
```

`literature.jsonl`: `id`, `title`, `authors`, `year`, `doi` or `arxiv`,
`read_depth` (`full`, `section`, `abstract`, `metadata`, `none`),
`verified` (`resolved`, `title_mismatch`, `unresolved`, `unchecked`), and
`claims` (`[{"text", "locator"}]`).

`protocol/P<n>.lock`: `protocol`, `sha256`, `approval`, `locked_at`.

`runs/ledger.jsonl`: `attempt_id`, `protocol`, `protocol_sha256`, `code_rev`,
`config`, `seed`, `status` (`completed`, `failed`, `interrupted`, `cancelled`,
`unknown`), `outputs`, `data_kind` (`measured`, `synthetic`, `illustrative`),
`evaluator_sha256` (the `digest` field of `evaluator.lock` in force), `cost`.

`analysis/claims.jsonl`: `claim_id`, `text`, `status` (`supported`, `limited`,
`contradicted`, `unresolved`), `run_ids`, `values` (name to number),
`uncertainty` (`type`, `level`, `n`), `protocol_sha256`, `deviations` (a list,
empty when the analysis followed the protocol), `evidence_changed_decision`
(which observation changed which decision, or `null`).

## Checks

From the navigator's directory:

```text
python scripts/check_records.py lock-protocol --project <dir> --protocol research/protocol/P3.md --approval <ref>
python scripts/check_records.py lock-evaluator --project <dir> <evaluator files...>
python scripts/check_records.py check --project <dir> --milestone M3
```

`check` reports structural problems by milestone: M1 needs a brief and a
locked protocol; M2 adds the evaluator lock; M3 adds run and claim ledgers
whose claims cite completed, measured runs under the locked protocol and an
unchanged evaluator; M4 and M5 add resolved literature for every source the
manuscript cites. It checks consistency of the records, not the science.
