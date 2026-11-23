# Codex host adapter: native Goal recovery

Read only on a Codex host that exposes native Goals, when a paper Goal is
blocked or paused and the user explicitly asks to resume it. The research
contract in [Goal execution](../goal-execution.md) does not depend on this file.

## Recover a blocked native Goal

A delivered "continue" message can run an ordinary chat turn while the native
Goal remains blocked. Read the actual Goal after delivery; do not infer activation
from chat activity or local project state. The in-turn `update_goal` tool may not
offer an active/resume status.

With an explicit user instruction to resume this Goal, use the host's actual
resume control. For compatible Codex hosts, the navigator's `scripts/goal_recovery.py` provides a
bounded app-server adapter: `--binary` selects the installed host, `--thread` the
existing owning chat, `--output` a new private receipt; read-only is the default.
`--resume --authority <USER_REQUEST_REF>` is an explicit mutation. Verify support
against the installed host's generated experimental app-server schema before
using it; never guess unsupported methods or modify the Goal database.

The adapter uses `thread/goal/get`, then `thread/goal/set` with only the existing
thread ID, `status: active` and `origin: user`, followed by a readback. It preserves
the objective, original creation time, token budget and accumulated usage. It
does not unpause or bypass budget/usage limits, create a Goal, start an inference
turn, add an automation or expand scientific authority.

An owning desktop session can retain its writer even after its turn is idle.
Let current substantive work finish naturally and preserve its checkpoint.
Prefer that same running application's native Resume Goal control: it uses
the owning server rather than a second process. An idle chat alone does not make
the standalone adapter eligible to write. If the writer remains, do not repeat
the standalone mutation, unload/restart the application, interrupt valid work,
create an empty turn or repeatedly send "continue". On uncertain transport
completion, inspect state once without repeating the mutation. If the interface
is unavailable, report that exact limitation and continue independent authorized
work; do not claim the host has resumed.

After status recovery, separately observe a later host-triggered Goal turn
(`source="goal"` where exposed) with no intervening human/coordinator continuation
message. A successful status readback is not that observation. If activation
alone does not schedule a turn, use the host's supported resume path and distinguish
any initiating recovery turn from a genuinely automatic following turn. Retain
timestamps and event provenance privately. Reuse completed results and checks.
A resumed blocked Goal starts a fresh consecutive-blocker audit under the actual
tool rules; a scientific decision/budget blocker remains binding.

## Resume a paused Goal

When the user explicitly requests resuming a paused project, the supported recovery
helper accepts `--resume --resume-paused --authority <current-request-reference>`.
Ordinary recovery never overrides a user pause. Preserve objective, original
budget and consumed usage; a changed status alone is not an automatic next turn.
An active writer rejection is respected; use the owning host rather than editing
state databases or repeatedly sending synthetic continuation messages.
