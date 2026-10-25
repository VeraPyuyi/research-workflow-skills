# Vertex App Builder credit restriction, 2026-10-25

Only usage covered by **Trial credit for GenAI App Builder** is authorized for
the configured Vertex provider. The exact balance, expiry and eligible
service/SKU mapping could not be verified: the official billing account page
required sign-in. Public pricing, configured credentials, model listings and
historical successes do not substitute for this account evidence.

No Vertex inference or charge-eligibility probe was initiated during this repair.
No model ranking calibration, scientific experiment or account billing change
was performed. The current confirmed eligible set is empty; this means
**unverified**, not a finding that the promotion covers no models.

## Root cause and repair

The research-group generator hardcoded `google-vertex/gemini-4-argon`, bypassing
the registry's ordinary eligibility flags. The dispatch checker admitted all
six Vertex variants after only generic allowance confirmation.

Observed regression failures demonstrated both issues before the repair. The
current generator excludes Vertex even when generic registry flags are changed,
and the dispatch checker denies Vertex independently of caller allowance flags.
The six catalogue entries remain with explicit credit holds and no default
stage/review assignments. There is no automatic re-enable path in this release.

The documented Magpie provider-off command was used. Readback first showed only
the provider's `off` field changed; credentials and model lists were retained.
The subsequent hash-protected routing update:

| Group | Change |
| --- | --- |
| `smart-split` | Removed Argon; long-evidence consistency selects Step `high`. |
| `github` | Removed three Vertex members and the unverified audio/video rule. |
| `gh-arch` | Removed Vertex Pro; the existing Astra member remains. |
| `slides` | Removed Vertex Pro; its text-outline rule selects existing Sol. |

Cursor's two research intent routes, free execution, Jev and other providers'
settings remain intact. The local `magpie models codex` catalogue query completed
successfully with zero Vertex entries. No inference was used for that observation.
Previously in-flight work and historical bills were not retroactively reconciled.

## Validation and limits

- 67 focused routing/dispatch/registry tests passed.
- The concentrated suite ran 293 tests: 289 passed, 4 skipped. The first run in
  the restricted environment had 48 temporary-file access/cleanup errors in
  submission-leakage tests; rerunning with appropriate local filesystem
  permissions passed. This was an environment issue, not hidden test success.
- All 18 skills passed metadata/reference validation.
- A new-context evaluation independently selected the Vertex hold and pending
  video route; see [the evaluation and disposition](../tests/results/vertex-credit-forward.md).
- Automated admission remains advisory for other providers: it does not create
  a universal spending cap or verify arbitrary audio/video packet declarations.

The unchanged Codex-native edition has no Vertex dependency and is not relabeled
as newly validated. This Magpie release changes the navigator's routing resources;
existing scientific results, goals, milestone cadence and project budgets remain
outside the repair.

## Re-enable evidence

Follow [the installed credit policy](../skills/research-navigate/references/vertex-credit-policy.md).
The local account's credit details must establish identity, remaining amount,
validity, scope and billing-project correspondence. Map the exact API/model and
features to eligible SKUs and establish enforceable no-paid-overage behavior.
Only that verified subset can be reconsidered. Do not test eligibility by sending
a model request.

Primary references: [Billing credit details](https://docs.cloud.google.com/billing/docs/how-to/resolve-issues),
[product pricing](https://cloud.google.com/generative-ai-app-builder/pricing?hl=en),
and [budget documentation](https://docs.cloud.google.com/billing/docs/how-to/budgets).
These were read as public documentation, not as this account's credit statement.
