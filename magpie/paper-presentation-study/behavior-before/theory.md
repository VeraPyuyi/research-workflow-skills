# Theory case

Synthetic acceptance material, not a real paper.
Skill used: the old research-write skill.
Source: fixture version 1, `cases[id=theory].evidence`.

## Theorem-focused paragraph

We consider the deterministic one-step decrease obtained by an exact gradient
update. Let f: R^d -> R be differentiable with globally L-Lipschitz gradient,
where L > 0, and use the Euclidean norm. For every x, write g = gradient f(x)
and x' = x - g/L. The supplied descent lemma implies

```text
f(x') <= f(x) + <g, -g/L> + (L/2)||-g/L||^2
       = f(x) - ||g||^2/L + ||g||^2/(2L)
       = f(x) - ||g||^2/(2L).
```

Thus an exact step has the stated deterministic decrease; when g = 0, x' = x
and equality holds. Convexity is not used by this substitution. The inequality
is a known consequence of the supplied descent lemma. Its role is a standard
supporting fact, with provenance retained, rather than a new theorem contribution.
This statement alone establishes neither a convergence rate nor a guarantee for
a controller whose update and applicability assumptions have not been validated.
The paper's question remains deterministic optimization.

## Proof-status note

The fixture supplies the descent-lemma statement and identifies the consequence
as known; no bibliographic identity or source proof was supplied or inspected.
A complete substitution argument is written above. It has not been independently
checked in this task; no external reviewer or proof assistant was used. This
preserves the distinction between a written derivation and independent proof
verification. External model calls were prohibited by the user.

The fixture mentions three quadratic examples as illustrative only. Their
coefficients, raw calculations, and records are unavailable, and no numerical
examples were executed here. Those examples cannot replace a proof over every
x and every function satisfying the assumptions. Application to the proposed
controller remains unvalidated. Its exact update rule and a mapping of its
objects and smoothness assumptions would be needed before transferring the
inequality; numerical illustrations alone would not establish that transfer.

## Explanatory figure: specification

Title: "Why an exact gradient step guarantees descent". Draw one schematic
plot along the deterministic direction y(t) = x - t g/L, for g != 0. The
horizontal axis is the dimensionless step multiplier t from 0 to 2. The
vertical axis is the normalized quadratic upper bound

```text
[L / ||g||^2] [q_x(y(t)) - f(x)] = -t + t^2/2,
q_x(y) = f(x) + <g, y-x> + (L/2)||y-x||^2.
```

Plot only this analytically specified bound. Mark t=0 at height 0 and t=1 at
height -1/2. A vertical bracket from 0 to -1/2 is labeled "guaranteed decrease
||g||^2/(2L)" in the original function units. An arrow at t=1 points downward
from the bound, labeled "f(x') lies at or below q_x(x')". Do not invent a true
objective curve, controller trajectory, or numerical observations. Add a note
that g=0 is the stationary equality case and is excluded from the normalization.

Caption: "Schematic derivation of the standard deterministic descent bound.
For g != 0, the descent lemma gives the normalized upper curve -t+t^2/2 along
y(t)=x-tg/L. At the exact step t=1, the bound is -1/2, yielding
f(x') <= f(x)-||g||^2/(2L). The diagram represents an analytic bound, not measured
controller behavior or evidence of a novel theorem."

## Evidence and handoff

| Item | Kind and status | Boundary or next check |
| --- | --- | --- |
| L-smooth descent lemma | Supplied known source statement; source proof not inspected | Preserve assumptions and obtain a verified citation if used in an actual paper |
| Exact-step inequality | Complete substitution written here; independent check pending | Independently check the algebra and quantifiers before recording independent proof verification |
| Three quadratic examples | Fixture-reported illustrations only; not executed here | No coefficients or raw records; no universal proof support |
| Controller application | Proposed, unvalidated | Inspect the update and prove the applicable condition mapping before claiming transfer |

Artifacts: theorem paragraph, displayed derivation, proof-status note, and one
explanatory figure specification in this file. Status: requested writing
completed; independent proof verification and controller validation remain open.
No theorem-novelty search, numerical experiments, or figure render was performed.
Next scientific step: independently check the substitution and, only for a
controller claim, establish the exact-update and smoothness mapping. No new
empirical stage is required merely to explain this deterministic inequality.