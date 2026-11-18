"""Independent exact check of MathRSI's public proof-repair example.

Source example: lisresearchgroup/math-rsi, revision
de556f3d5427343153d8d24bed4578ccfe66400c, examples/proof-repair/.
This is a finite arithmetic check, not a run of the agent research workflow.
"""

from fractions import Fraction
import json


def main():
    events = []
    for mask in range(32):
        bits = [(mask >> i) & 1 for i in range(5)]
        events.append((
            len({bits[i] for i in (0, 1, 2, 3)}) == 1,
            len({bits[i] for i in (0, 1, 2, 4)}) == 1,
        ))
    p_e = Fraction(sum(e for e, _ in events), 32)
    p_f = Fraction(sum(f for _, f in events), 32)
    joint = Fraction(sum(e and f for e, f in events), 32)
    assert (p_e, p_f, joint) == (Fraction(1, 8), Fraction(1, 8), Fraction(1, 16))
    assert joint != p_e * p_f
    bounds = {m: 1 - m * Fraction(1, 8) for m in range(8)}
    assert min(bounds.values()) == Fraction(1, 8)
    print(json.dumps({
        "source_revision": "de556f3d5427343153d8d24bed4578ccfe66400c",
        "execution": "independent exact arithmetic; no model calls",
        "assignments_checked": len(events),
        "p_e": str(p_e),
        "p_f": str(p_f),
        "p_joint": str(joint),
        "independence_product": str(p_e * p_f),
        "independence_claim": "refuted by the two overlapping edges",
        "minimum_union_bound_for_m_0_to_7": str(min(bounds.values())),
        "scope": "finite counterexample and bound arithmetic; not general workflow validation",
    }, indent=2))


if __name__ == "__main__":
    main()
