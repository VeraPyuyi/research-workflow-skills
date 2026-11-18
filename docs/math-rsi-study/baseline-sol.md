# Frozen old-version development baseline

Requested model: `gpt-6.1-sol`. Actual served model: not runtime-attested; exact identity unknown. No model dispatch or independent review occurred.

Scope: bounded offline responses under the frozen research-design, research-navigate and research-analyze instructions and necessary frozen references. This is a behavior baseline, not live scientific Goal work. No network, model calls or real project changes. Only this output file is written.

Read-boundary deviation: the initial read of math-rsi-cases.json exposed the embedded heldout entry along with the development entries. It was not analyzed or used below, but this run cannot be claimed to satisfy the requested heldout-read isolation. No rubric, updated skills or other model outputs were read.

## 1. theorem-import

Reject the survey note's independence inference. Independent vertex colors do not generally make overlapping-edge events independent. The original source is inaccessible, so its statement/proof and precise conditions are unverified; do not import it as an established theorem.

Let A and B be the monochromatic events for {1,2,3,4} and {1,2,3,5}, using independent fair binary vertex colors. Of the 2^5=32 equally likely assignments, A holds in 4, B holds in 4, and both hold in 2 (all five vertices have the same color). Thus

P(A)=P(B)=1/8,
P(A intersect B)=1/16 != P(A)P(B)=1/64.

This exact count was also executed by enumerating all 32 bit assignments with rational arithmetic. It refutes the note's event-independence claim for the supplied example, not the coloring theorem.

Complete the parent proof without that import. For any edge e of size four, exactly two of its sixteen color assignments are monochromatic, so P(M_e)=1/8. With m<=7 edges, the union bound gives

P(at least one monochromatic edge) <= sum_e P(M_e)=m/8<=7/8<1.

Consequently a coloring with no monochromatic edge exists, with probability at least 1-m/8>=1/8 under this experiment. Color the finite union of the edges; any remaining vertices may be colored arbitrarily. No event independence is required. This is a self-contained proof for every hypergraph in the stated class, rather than an extrapolation from the five-vertex enumeration.

Handoff to parent: use the union-bound argument and discard the false independence step. Source status: inaccessible original, secondary claim contradicted by exact calculation. Proof status: complete author derivation for the stated existence claim; finite enumeration checks the local counterexample, not every hypergraph. Independent review not performed. No missing source blocks this repaired proof.

## 2. actual-input

The child established the real symmetric case only. Its result cannot be applied to every square real matrix, and in particular not to the actual upstream matrix

A = [[1,1],[0,1]],   A^T = [[1,0],[1,1]] != A.

A stronger exact obstruction is available. Its characteristic polynomial is (lambda-1)^2, while

N=A-I=[[0,1],[0,0]],   N^2=0,   N!=0,
ker(A-I)={(s,0): s real}.

Thus the sole eigenvalue 1 has algebraic multiplicity two and a one-dimensional eigenspace. A has no eigenvector basis and is not diagonalizable even over the complex numbers, hence cannot be orthogonally diagonalized over the reals. A generalized eigenvector chain is (A-I)e2=e1 and (A-I)e1=0; the supplied A is already its Jordan block.

These exact computations carry out the next bounded applicability and counterexample check. They establish that any parent claim that all square real matrices admit a diagonalization is false. The symmetric theorem itself remains valid: this nonsymmetric input does not refute it. If the parent conclusion is something other than diagonalizability, the supplied information does not establish whether that conclusion is true or false.

Handoff to parent: preserve the child lemma with its symmetry hypothesis; invalidate any step applying it to arbitrary upstream matrices. Do not silently restrict the parent's arbitrary-matrix domain. Next prerequisite is the exact parent statement and the step requiring this lemma. With that statement, research-design should either repair the reduction using a result valid for arbitrary matrices or return the explicit Jordan-block obstruction to the claimed conclusion. Parent proof unresolved beyond the facts above; no claim of independent checking or source inspection.

## 3. hard-remainder

Keep O7 as the unresolved singular-boundary obligation. Calling it O8 does not discharge it. Splitting three proved interior cases into thirty creates no evidence for the missing boundary case. Two rounds without progress are grounds to stop repeating that route and choose a genuinely discriminating boundary check; they do not themselves prove O7 false or authorize abandoning the paper.

The actual mathematical statements of O7 and L4 are absent. Therefore no O7-specific proof, counterexample or valid application of L4 can be manufactured from this record. One useful scientific check can nevertheless be completed: interior validity alone does not justify boundary passage. For the explicitly illustrative scalar family A_t=[t], A_t is invertible for every t>0 with inverse [1/t], but A_0=[0] is singular and the inverses have no finite limit. This is an exact obstruction to a generic 'proved in the interior, therefore true at the singular boundary' argument. It is not a counterexample to O7, whose conclusion is unknown. A limit proof would need appropriate closure/continuity and control of its witnesses or inverses; none is supplied.

Perform the dependency audit in this handoff, without changing project state:

| Item | Recorded disposition and remaining check |
| --- | --- |
| O7 | Remains open under its existing identity; retain both unsuccessful rounds and the three established interior cases. |
| Proposed O8 / thirty interior cases | Reject as the next scientific action: no new boundary evidence or distinct obligation has been supplied. |
| C4 -> P1, lemma L4 | Two prior returns are already recorded. Do not generate a third identical child result. K owns incorporation into the parent proof; actual incorporation is not established. |
| T5 / T6, pending | Reported covered by L4. K should verify the exact statement/assumption mapping, then mark redundant tasks satisfied or superseded rather than execute them again. No status was changed here. |
| T7, running | Reported covered by L4. K should reconcile its actual job status and commitments; if exact redundancy and authority are confirmed, cancel through supported controls. Cancellation is neither attempted nor claimed here. |

Handoff: owner K; parent P1; stable blocker O7; reusable child artifact C4/L4. Completed here: rejection of the invalid interior-to-boundary inference by an explicit scalar example and the dependency audit above. Remaining scientific input: O7's exact hypotheses/conclusion, the definition of the singular locus, L4's statement/proof and conditions, and the precise failed boundary argument from the two rounds. Running-work input: T7 job identity/status and applicable resource/cancellation authority.

Next bounded package for research-design: using those inputs, test whether L4 actually covers O7, then try the smallest admissible singular instance or a justified limit argument. Return a proof, an in-domain counterexample, or the precise unresolved implication, with a bounded stopping condition. Do not rerun the same interior split. This package was not dispatched and O7 was not solved. The hypothetical paper remains incomplete; no native Goal was created, resumed, completed or otherwise changed.
