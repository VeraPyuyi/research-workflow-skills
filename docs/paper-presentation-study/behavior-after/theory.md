# Theory: deterministic one-step descent

Revision: theory-v1. Evidence: supplied fixture version 1, `paper-presentation-cases.json`, case `theory`. Preserve the deterministic optimization question: what decrease follows from one exact gradient step under smoothness? This is a known-result application, not a new theorem or a validated controller claim.

## Theorem-focused paragraph

Let $f:\mathbb{R}^d\to\mathbb{R}$ be differentiable with an $L$-Lipschitz gradient, $L>0$, in the Euclidean norm. For every $x\in\mathbb{R}^d$, define $g=\nabla f(x)$ and the exact update $x'=x-g/L$. The supplied descent lemma implies

$$f(x')\le f(x)-\frac{\|\nabla f(x)\|^2}{2L}.$$

Indeed, substituting $y=x'$ gives

$$f(x')\le f(x)+\langle g,-g/L\rangle+\frac{L}{2}\|-g/L\|^2
=f(x)-\frac{\|g\|^2}{L}+\frac{\|g\|^2}{2L}
=f(x)-\frac{\|g\|^2}{2L}.$$

Thus the exact step decreases the objective by at least the displayed amount when $g\ne0$; when $g=0$, $x'=x$. Convexity is not needed for this one-step bound. No rate of convergence, global optimality, stochastic-gradient statement, or controller stability guarantee follows here without further assumptions and arguments. The fixture identifies the inequality as a known consequence. The unvalidated controller application remains a possible application rather than an established contribution.

## Proof-status and source note

Definition/assumption revision T-A1 is exactly the setting above. T1 (the one-step inequality) is a direct derivation from the supplied lemma: the substitution and algebra are displayed and inspected in this drafting pass. The input says the proposed proof has not been independently checked; no independent checker or proof assistant was used here. This is a completed explanatory derivation conditional on the supplied lemma, not an independently verified proof record. The lemma statement was supplied and inspected; its original source, source proof, and bibliographic identity were not supplied or externally inspected.

T2 (usefulness or validity for the proposed controller) is unresolved: no controller definition, assumption mapping, or validation is available. Reusing the known bound simplifies the mathematical argument but cannot replace evidence for controller behavior. A later controller claim requires a precise controller/update mapping, checks that the same smoothness and exact-gradient hypotheses apply, and validation of its actual claimed behavior.

The fixture mentions three quadratic examples as illustrative checks. It supplies no functions, coefficients, outputs, or logs. They were not rerun, reconstructed, or used as evidence for a universal theorem. Numerical examples would not replace the missing independent proof check.

## Explanatory figure specification: T-F1

**Reader question:** why does the step size $1/L$ deliver the stated deterministic decrease? Use a conceptual bound schematic, not an empirical plot or a newly invented numerical example.

Let $x_s=x-sg/L$ and display only the symbolic upper bound

$$q(s)=f(x)-(s-s^2/2)\|g\|^2/L,\qquad f(x_s)\le q(s).$$

For $g\ne0$, show the schematic parabola over $0\le s\le2$, marking $q(0)=f(x)$ and its minimum at $s=1$, where $q(1)=f(x)-\|g\|^2/(2L)$. Label the vertical difference algebraically. X is dimensionless step multiplier $s$; Y is the symbolic upper bound on objective value. No observed function curve, controller trajectory, numeric axis values, or uncertainty bars are supplied. Handle $g=0$ in a note: the step leaves $x$ unchanged. The schematic's parameters are assumptions and symbols, not measured data.

Propose a 3.25-inch-wide vector figure, with at least 8-point annotations and distinct line/marker encodings; this width is a design choice, not an asserted venue rule. If later rendered, inspect it at that width and ensure the bound is visually distinguished from the unknown actual objective along the step.

**Caption.** Conceptual illustration of the supplied descent lemma along the exact gradient direction. At multiplier $s=1$, its quadratic upper bound decreases by $\|\nabla f(x)\|^2/(2L)$ under differentiability and an $L$-Lipschitz gradient with $L>0$. The curve represents a symbolic bound, not measured function values. The known inequality does not validate the proposed controller application.

## Bounded handoff

Artifacts: theorem-focused paragraph, proof-status note, and T-F1 specification. Evidence: fixture lemma and transparent substitution; no external theorem source. Status: writing complete, independent proof verification absent, figure not rendered. Open issues: source identification and controller applicability/validation. Next step: return the requested materials; independent checking or controller research would be separate work. No experimental dependency is added to this deterministic question.
