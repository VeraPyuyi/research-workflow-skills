# 6.2 model activation, 2026-11-21

## Access and cause

The updated official account catalog exposes gpt-6.2-astra and gpt-6.2-sol.
The local Codex setting still routes through a gateway, so a separate temporary
official-subscription configuration was used for native verification. No global
Codex setting, authentication identity or PAYG permission was changed.

The gateway refreshed its upstream catalog but its Codex provider still selected
only the older five models. Two exact subscription IDs were added, preserving
other provider settings and all keys. Scientific group changes preserve API
member ordering, arbitrary user intents and paused rules. Only known active
research intents are upgraded; legacy versions remain available as fallbacks.

The current subagent tool description lists both 6.2 IDs as permitted overrides.
That allowlist is checked separately from inference access. A future host with
a different signature or missing model must fall back rather than fabricate a
successful spawn. This release does not change host Goal lifecycle behavior.

## Functional evidence

Four synthetic inference requests completed, one per model per runtime profile.
All used high effort and existing Codex Pro subscription access; the refreshed
weekly allowance showed 41% remaining, resetting 2026-11-22 00:08:09 +08:00.
No benchmark ranking or research-success calibration was run.

| Runtime | Model | Input tokens | Output tokens | Identity and interface evidence |
|---|---|---:|---:|---|
| Native official subscription | 6.2 Astra | 11371 | 30 | Host-reported model and completed turn; correct JSON |
| Native official subscription | 6.2 Sol | 11371 | 34 | Host-reported model and completed turn; 8576 cached input tokens |
| Gateway subscription endpoint | 6.2 Astra | 5554 | 67 | Response identity matched usage row; function schema passed |
| Gateway subscription endpoint | 6.2 Sol | 5605 | 59 | Response identity matched usage row; function schema passed |

The gateway reports accounting amounts of USD 0.047112 and USD 0.011800,
respectively. These are not treated as invoices or newly authorized API charges.
Native monetary cost was not reported. No hard output cap was verified.
One initial local configuration check rejected a reserved built-in provider
override before a thread or inference started; it consumed no model request.
It was corrected without changing global configuration. There were no caller
inference retries. Native raw wire identity, native tool execution, subagent
spawning/concurrency and later host Goal auto-turns were not tested by these
four probes. See tests/routing-evidence-20261121.json for sanitized receipts.

## Allocation and constraints

6.2 Astra is preferred for hard theory, original-problem connections,
hardest-branch probes and scientific review. 6.2 Sol handles routine engineering,
experiment control and drafting. Old Astra and 6.1 Sol remain fallbacks and
second opinions. Same-family versions/providers cannot claim independent review.

This activates the November 18 allocation, not a new benchmark winner claim.
The dated benchmark table remains in docs/model-routing-20261118.md. Public web
lookups during this activation did not return fresh source content, so no prior
benchmark score was relabelled as newly checked.

Both profiles keep standalone Jev, the shared Codex pool limits, MathRSI records,
Goal completion conditions and M1-M5 cadence. The multi-channel edition retains
free branches and covered Cursor work, the Vertex credit hold and Anthropic
removal. No new external worker is added to the native edition.

## Verification and deployment

Focused regression first reproduced the missing new group members and unchanged
old active rules. Tests cover activated admission, unavailable-host fallback,
same-family independence, preserved custom/paused/API-first rules and old models.
Whole-suite, installation and remote-byte results are recorded in the release
receipt after the final verification. The prior native release receipt omitted
from its Git tree is included, without changing its original digest.

Projects adopt the compatible profile at their next recovery or handoff. Existing
results, valid checks and in-flight jobs remain pinned. A routing upgrade and a
coordinator message do not prove a host-generated automatic Goal turn.

The final live catalog check also found LongCat, GLM Flash Free and Space Bunny
absent from their prior free endpoints. The multi-channel registry keeps their
historical identities but blocks new dispatch; active scientific text branches
use the separately identified DeepSeek free endpoint, and engineering uses MiMo
free. This changes no native endpoint or billing authorization. No new free-model
inference was attempted in this bounded 6.2 activation.
