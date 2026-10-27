# Shared Argument and Display Handoff

Analysis, implementation and writing use one logical record. Extend the project's
existing claim/evidence map; this is not a new database, mandatory file format or
separate approval gate. A local edit uses only relevant fields.

## Argument record

- Versioned theme/question and current claim IDs.
- Claim text, evidence status and proof status as separate fields.
- Source/run/analysis/definition revisions; missing evidence.
- Comparison or estimand, population, assumptions and scope.
- Section role and the reader question it answers.
- Rival explanation and the evidence that could distinguish it.

## Display record

For each figure/table, retain a stable display ID linked to its claims:

| Field | What the next stage needs |
| --- | --- |
| Purpose | Reader question and exact bounded conclusion |
| Input | Data/run and analysis versions; measured, simulated, illustrative or pending |
| Transform | Formula, aggregation, filtering, exclusions, missing/failed attempts |
| Comparison | Groups, pairing, sample unit, denominator and matched conditions |
| Uncertainty | Type, level and independent n, or explicitly unavailable |
| Encoding | Panels, axes, scales, units, order, method colors/markers and precision |
| Text | Caption facts/conditions and body interpretation, separately |
| Output | Venue/template-derived width, formats and destination |
| Coverage | Generator/input hashes; actual render and readability checks; unresolved gaps |

Neutral example, with illustrative values:

```text
display_id: F-success-latency-v1
claims: [C-reliability, C-conditional-speed]
data_kind: illustrative
analysis: A1; attempts 24 per method; all attempts retained
comparison: success 21/24 vs 19/24; successful-only latency 12.5s vs 8s
uncertainty: unavailable; aggregate input does not supply repeated observations
encoding: two panels; rate and conditional time have separate units
caption: counts, latency population, unavailable uncertainty
body: conditional speed comes with lower observed completion; net utility unknown
output: template-derived single-column width; PDF/SVG and table
```

This example is not research evidence. A conceptual schematic uses conceptual
objects and assumptions instead of measured values; label that distinction and
do not fabricate a data provenance chain for a diagram.

## Responsibilities and invalidation

`research-analyze` determines quantities, comparisons, inferential limits and
evidence gaps. `research-implement` implements those transformations, retains
safe provenance and renders actual artifacts. `research-write` organizes the
argument and caption/body language without silently changing the specification.

A revised label can need only a local check. A changed denominator, filter,
definition, proof status or claim invalidates the affected display/text and its
prior check. Reuse unaffected coverage. Integrate checks into M2 implementation,
M3 evidence and M4/M5 manuscript nodes, rather than reviewing the whole paper
after each graphical change.

Keep private execution details in the internal record. Export only public-safe
IDs and provenance; submission-facing artifacts follow the existing leakage
audit and venue requirements.
