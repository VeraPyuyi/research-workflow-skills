# Magpie Routing Notes

As of 2026-10-25, Vertex is held under the App Builder credit-only policy.
The generator no longer hardcodes Argon or accepts Vertex via generic registry
eligibility. Long-evidence consistency is routed to Step. The local provider
is off and explicit Vertex members were retired from the research, GitHub,
architecture and slides groups. See [the dated validation](vertex-credit-validation-20261025.md).
No credit-backed Vertex adapter is implemented in this release.

This repository now includes an offline helper for preparing the `smart-split`
research group update without touching live Magpie configuration by default.

## Helper

```powershell
python scripts/magpie_routing.py
python scripts/magpie_routing.py --config "<private-providers-config.json>" --artifact-dir ".build\model-collaboration\magpie"
python scripts/magpie_routing.py --apply --expected-before-hash <config_sha256_before>
```

Default mode is dry-run. The helper:

- builds a proposed `smart-split` group from `skills/research-navigate/references/model-routing.json`
- validates known group/rule fields and literal provider/model membership
- checks effort suffixes only against `supported_reasoning_levels` in the local catalog
- maps bare catalog slugs to `codex` only; other providers need a provider-qualified slug
- includes explicitly eligible account routes and their `automatic_group_intents`
- excludes blocked endpoints and omits fixed-effort account routes when that exact level is absent from the catalog
- keeps intents at or below Magpie's native 200-character limit
- writes sanitized before/after config snapshots and a group diff under `.build/model-collaboration/magpie/`
- aborts apply when the live config hash changed
- writes a timestamped backup beside the live config before apply
- rechecks the hash after backup and verifies the bytes read back after replacement

## Important limits

- `group/smart-split` rules only prioritize members. They do **not** pin execution.
- `routing: order` still allows later members to receive failed requests.
- strict free tasks must bypass `group/smart-split` and use direct exact endpoints
- the helper does not make live model requests and does not claim unsupported schema guarantees
- Cursor account coverage is checked before dispatch; mixed groups cannot enforce subscription-only spending when the account permits on-demand use. Strict cost/identity work uses an appropriate direct endpoint under the project's budget.
- Magpie has no explicit live-reload call in this helper. An atomic file replacement refreshes config on the next read, while in-flight plans, turn state, and a held catalog cache can persist until their own boundary.
- The pre-replacement hash check is not an OS compare-and-swap lock. A writer that changes the file between the last check and `os.replace` can still be overwritten. Apply during an exclusive configuration-writer window; the helper's guarantee is limited to atomic file replacement, observed-hash mismatch detection and post-write read-back verification.

## Effort evidence

Verified levels come only from the configured local model catalog (default: `~/.codex/models_cache.json`) field `supported_reasoning_levels`. `default_reasoning_level`, `settings.json` `modelEfforts`, and routing recommendations are not capability evidence. A model without a verified level is stored without an effort suffix.

Earlier generated sanitized artifacts used a recursive redaction heuristic. Those files were overwritten with an allowlist projection: provider id, model names, fallback presence, and known group routing fields only. Provider keys, headers, cookies, URLs, and arbitrary values are not copied.

## Prepared target shape

The prepared group keeps:

- `codex/gpt-6-astra:max`
- `codex/gpt-6.1-sol:max`
- `cursor/grok-4.6:medium`, with explicit alternative-explanation and bounded-engineering intent rules
- the 12 approved free generative endpoints from `model-routing.json`
- classifier `typesafe/jev-latest`, which is not added as a worker member

Composer remains excluded due to the observed effort mismatch. Other Cursor
variants are conditional direct candidates. New account models are not included
merely because they are catalogued: inclusion needs explicit group eligibility,
an intent mapping, no dispatch block, and supported effort evidence.
The Vertex credit hold overrides generic eligibility until an exact credited
route and enforceable no-overage behavior are verified and implemented.

It removes:

- blanket `tokens`, `images`, and `compact` rules
- Dot members and nested Dot routes
- nested auto-group members such as `group/auto-hy3` and `group/auto-step-5-preview`

Intent rules cover classification, retrieval, reuse review, independent review, mathematics, engineering, visual extraction, long-evidence consistency, difficult research, formal derivation, experiment coordination, routine writing, manuscript integration, and routine assistance.

## Evidence artifacts

Generated files:

- `.build/model-collaboration/magpie/smart-split.before.sanitized.json`
- `.build/model-collaboration/magpie/smart-split.after.sanitized.json`
- `.build/model-collaboration/magpie/smart-split.before.group.json`
- `.build/model-collaboration/magpie/smart-split.after.group.json`
- `.build/model-collaboration/magpie/smart-split.diff`
- `.build/model-collaboration/magpie/effort-evidence.json`
- `.build/model-collaboration/magpie/manifest.json`
