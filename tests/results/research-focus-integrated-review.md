### Strengths
- `research-focus` is the 18th skill in both source and candidate trees, with a versioned `theme_envelope` / `active_thesis` split, provenance gaps, in-theme delegated pivots, auxiliary claim-link/return bounds, compact handoff reminders, M1-M5 cumulative alignment, and explicit exclusion of private focus history from M4/M5 blind packets.
- Optimizer bookkeeping is closed: `optimize_workflow.py` suppresses `research-focus` and `research-optimize` events without mutating state (`focus-event-suppressed` / `self-event-suppressed`). Magpie group routing includes a dedicated Step-5 focus intent plus Cursor Grok 4.6 critique intents; native generative IDs remain only Sol/Astra/Luna, with optional standalone `jev`.
- Generative admission for `research-focus` is ready-for-dispatch on both editions. Declared `research_focus` inputs fail Magpie and native `review_errors`. Native spawn messages do not copy extra packet fields such as a `research_focus` object. Goal continuation and no-fake-complete/activate language remain in `goal-execution.md` after native integration.

### Issues

#### Critical (Must Fix)
1. **Jev stage allowlist omits `research-focus` while both routing registries assign it**
   - File: `<workspace>/skills/research-navigate/scripts/jev_decide.py:25-31` and `:110`; same `STAGES` at `<workspace>/.build/research-focus-20261025/native/skills/research-navigate/scripts/jev_decide.py:26-32` and `:111`; Magpie assignment `<workspace>/skills/research-navigate/references/model-routing.json:1044-1046`; native assignment `<workspace>/.build/research-focus-20261025/native/skills/research-navigate/references/model-routing.json:262-272`.
   - What's wrong: `research-focus` is the only packaged skill missing from `STAGES`. An otherwise valid offline packet with `stage: "research-focus"` returns `execution_status=blocked`, `error_code=invalid_identity_or_stage` on source, Magpie, and native. The same packet with `stage: "research-ideate"` is `dry_run`. Native still reports `fallback=native-evidence-comparison`; Magpie does not. Tests only assert that Magpie lists `typesafe/jev-latest` (`tests/test_research_focus.py:50`), not that the adapter accepts the stage.
   - Why it matters: a real in-theme candidate comparison at focus cannot use the assigned decision service. Magpie workers following the registry will treat a valid optional comparison as a packet error instead of an unavailable-credit skip. Native still has a native-comparison fallback, but the adapter never validates a focus packet.
   - How to fix: add `research-focus` to both `STAGES` sets, or remove the registry `decision_services` assignment and the Magpie "optional Jev at real candidate choices" gate text if focus is intentionally comparison-only via generative workers. Add an offline packet asserting the chosen contract.

#### Important (Should Fix)
1. **Native focus packaging test does not execute the native isolation checker**
   - File: `<workspace>/.build/research-focus-20261025/native/tests/test_research_focus.py:68-73`; native checker `<workspace>/.build/research-focus-20261025/native/skills/research-navigate/scripts/check_dispatch.py:140-210` and `:116-129`.
   - What's wrong: `test_blind_review_cannot_receive_focus_history` skips whenever `runtime_profile != magpie`. The copied native test therefore never calls native `review_errors` or `spawn_request`. Native isolation is real and was observed here only by a one-off read-only probe, not by the shipped native test.
   - Why it matters: a later native-only regression (for example allowing extra input kinds, or interpolating coordinator `research_focus` into the generated prompt) would not fail this suite.
   - How to fix: keep Magpie's declared-kind check; add a native case that rejects `kind: research_focus` and asserts a generated prompt contains only allowlisted absolute files/hashes.

2. **Stage-map candidate-choice list never names `research-focus`**
   - File: `<workspace>/skills/research-navigate/references/stage-map.md:96-104`; native copy `<workspace>/.build/research-focus-20261025/native/skills/research-navigate/references/stage-map.md` at the same heading. Contrast `workflow-contract.md` "Research main line" and Magpie `model-routing.md:298-309`.
   - What's wrong: the map now routes drift into `research-focus`, but "Candidate-choice support" still lists only survey, ideate, design, analyze, review, and navigate. Focus comparisons (stay vs in-theme pivot vs auxiliary bound vs out-of-theme pending) are exactly the comparison the new skill exists to record.
   - Why it matters: navigators using the map as the dispatch index can run focus as provenance bookkeeping and never attach a bounded comparison, which is the same class of miss as the Jev allowlist gap.
   - How to fix: add focus alignment/pivot choices to that list, with the edition-correct decision-support link.

#### Minor (Nice to Have)
1. **Cursor automatic-group intents still omit the focus comparison text**
   - File: `<workspace>/skills/research-navigate/references/model-routing.json` `cursor/grok-4.6.automatic_group_intents`; helper `<workspace>/scripts/magpie_routing.py:344-369`.
   - What's wrong: `stage_roles` includes `research-focus`, and tests require Cursor rules plus a separate Step-5 rule whose intent contains "topic drift". Cursor's two group intents remain competing-explanations and bounded engineering. Magpie `model-routing.md:298-309` still tells operators to use Grok 4.6 for alternative-question critique.
   - Why it matters: mixed-group intent routing can send a focus critique to Step-5 even when a covered Cursor branch was intended. Direct `covered_account_executors` dispatch still works.
   - How to fix: add a Cursor intent that names original theme, cumulative pivots, and scientific value, or narrow the Magpie gate text to direct dispatch only.

### Declined to judge
- Expected stale pending `workflow-release.json` / unsealed receipts: known staging, not a finding.
- `native-conflicts.json` leftover patch failures: `integrate_native.py` already rewrote those files; residual patch logs are not live native content.
- Magpie vs native wording (`free` vs `native`, Jev-first vs native-comparison-first): profile adaptation, not focus drift.
- Magpie/source vs native `goal-execution.md` "per-provider quotas" vs "shared Codex model quotas": intended native quota language.
- Magpie candidate vs current source `docs/`, `config/*.local.json`, `tests/results/`, `tests/continuation-*.json`: not in `changed-skills.json`; outside this skills delta.
- Scientific effectiveness of the new skill on live projects: this is implementation/workflow review, not a paper or live-project audit. Active-project packets were out of scope.
- Full `unittest` / installer / publication suite: a separate validation track is running; this review used targeted read-only offline probes only.
- Host-served model identity and whether any M4/M5 gate is model-independent: unknown unless the host supplies it. No model-independent scientific-gate claim.

### Recommendations
- Repair the Jev `STAGES` / registry contradiction in both editions before seal; that is the one executable contract break.
- Make native `test_research_focus.py` actually exercise native `check_dispatch.py`.
- After those, re-run only the already-owned focus/Jev/dispatch tests rather than inventing a new framework or per-edit test duty.

### Assessment

**Ready to merge?** No

**Reasoning:** Main-line policy, Magpie Cursor membership, native Sol/Astra/Luna-only generative workers, optimizer non-recursion, Goal continuation text, and blind declared-input rejection are in place. The shipped Jev adapter still cannot accept the new stage that both registries assign, so an authorized in-theme comparison at focus is not a coherent dual-edition integration yet.

Reviewer identity: unknown unless the host records it. Scope: read-only comparison of current source `<workspace>` against `.build/research-focus-20261025/before-source`, Magpie, and native; no installs, publishes, or live project writes.
