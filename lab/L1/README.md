# Workflow lab round L1: do the 2026-11-23 review fixes help?

**Question.** Does the suite after the review fixes (`codex-native` after merge
`070f46f`, candidate) behave better than the suite before them (`04975f2`,
baseline) on the 16 core scenarios and the 8 integrity scenarios, without
lowering any integrity scenario?

**Status.** Prepared, not run. No project events exist yet, so this round is a
measurement of an already merged change rather than a response to recurring
signals; its result decides whether the change stays or is partly reverted.

**Frozen controls.** `contract.json`, `criteria.json` (24 cases; the integrity
suite is held out and protected) and `usage.json`. The budget limits are
`null` until the owner approves an amount: the state helper allows recording
but blocks spending until then.

**Run.** Integrity scenarios were written together with the candidate, so the
candidate had them in view; treat their result as a regression check, not as
independent held-out evidence.

```text
python scripts/workflow_lab.py prepare --round L1 --baseline-ref 04975f2 --candidate-ref 070f46f --out .build/lab/L1 --runs 3 --suite core --suite integrity
```

Then follow steps 4 and 5 of `skills/research-optimize/references/workflow-lab.md`:
answer every task in a fresh agent, grade blind with a different model
lineage, summarize both sides and run `compare`. Record the comparison, the
review and the owner's decision here.

**Size.** 24 scenarios x 3 runs x 2 sides = 144 answers and 144 gradings.
