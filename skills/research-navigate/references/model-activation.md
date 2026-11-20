# 6.2 activation, 2026-11-21

Prefer 6.2 Astra for difficult theory, actual-input/original-problem connections,
hardest-branch probes and scientific review. Prefer 6.2 Sol for engineering,
experiment control and drafting. Keep old Astra and 6.1 Sol as fallbacks and
scientific second opinions. All versions share the existing Codex allowance.
Different Astra versions, or different Sol versions, are not independent reviewers.

Both exact model IDs returned successful high-effort synthetic responses on
2026-11-21 using existing subscription access. This is an access observation,
not a benchmark or a permanent allowance. The dated full report and sanitized
usage are in the repository's docs/model-activation-20261121.md.

Refresh the current tool's explicit model/effort allowlist before dispatch.
A registry entry and a successful standalone inference cannot establish that
an already-open chat has refreshed its subagent tools. If absent, use the old
qualified model; do not change global configuration or create duplicate work.
If the host exposes a different tool signature, inspect and validate that
signature before use; never synthesize an unsupported call.

Default effort remains high. Higher effort needs a scientific reason and the
endpoint's actual support. Catalog context is 272000 for Astra and 500000 for
Sol; effective native turns observed 258400 and 475000 respectively. Use the
current runtime's smaller effective limit, leaving room for the reply and tools;
these observations are not context stress tests or hard output caps.

Jev compares only currently eligible candidates. It cannot unlock an absent
model, increase quota, make same-family review independent, or start a task.
Maintain six global workers, two per confirmed Codex pool and one when unknown.
Goal continuation, M1-M5, two fresh-context reviews and the MathRSI records
remain unchanged. Adoption affects the next unstarted task; running tasks keep
their original model, source, protocol and evidence versions.

Native admission for either new model requires host_available_models containing
that exact unqualified ID, obtained from the current subagent tool rather than
the standalone catalog. This caller evidence is not a filesystem isolation claim.
The direct official transport was verified in a temporary configuration. Native
subagent spawning, multi-agent concurrency and later automatic Goal turns were
not exercised by these two short inference probes. Keep the standalone Jev
credential interface; no external generative service is introduced.
