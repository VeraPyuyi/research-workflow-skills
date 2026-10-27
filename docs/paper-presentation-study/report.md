# Evidence-Led Paper Presentation Study

Status: corpus reading, frozen-pattern holdout assessment, four-case behavior
comparison and rendered artifact inspection completed. Consolidated validation
and deployment are recorded separately in the release and deployment receipts.

## Scope and provenance

The study contains 90 official conference papers: five venues, three editions
per venue, four selected papers and two ordinary accepted comparators in each
cell. Forty-five selected papers and fifteen controls form the discovery set;
fifteen selected papers and fifteen controls form the holdout set.

| Venue | Editions | Selected designation retained | Papers |
| --- | --- | --- | ---: |
| CVPR | 2026, 2025, 2024 | Highlight; 2025 Oral events | 18 |
| ICLR | 2026, 2025, 2024 | 2026 Oral; earlier Spotlight | 18 |
| ICML | 2026, 2025, 2024 | Spotlight; 2025 spotlight poster | 18 |
| ACL | 2026, 2025, 2024 | Outstanding Paper | 18 |
| NeurIPS | 2025, 2024, 2023 | Official Spotlight category | 18 |

Exact labels, official pages, pinned conference PDF digests, research-type
sampling tags and the frozen split are in [sources.json](sources.json).
The [sampling protocol](sampling-protocol.md) preceded qualitative reading.
The selection is purposive and metadata/title-assisted. Controls favor related
domains and research types but are not tightly matched for length or measured
writing quality. One ICML holdout is a position paper and is interpreted as that
genre, not relabeled as a conventional method or benchmark study.

NeurIPS 2026's six bounded candidate PDF attempts returned access failures.
The protocol therefore used 2025/2024/2023. This does not establish that every
2026 paper was inaccessible or that the edition did not exist. The
[access log](access-limitations.json) and
[official metadata retrieval receipts](source-retrieval.json) retain that scope.
The prior ACL entropy pilot was exchanged out of holdout before reading. No
paper was replaced because its writing was weak.

CVPR 2026 metadata was a partial 200-row frame, with 82 null decision fields.
Sample identities and selected categories were individually checked, but this
is not a complete sampling frame for that edition. The access log also retains
a repeated ICLR title-check event; it is not an additional paper or unique
access failure.

Fifteen metadata corrections are retained: inline ACL acronym typography and
PDF page counts previously distorted by form-feed extraction. Paper identities,
digests and the final split did not change. Readers used physical PDF pages.

## Actual reading and independent holdout check

All 90 main texts were read. The consolidated record contains **879 main-text
and boundary-page entries, 90 viewed overviews and 232 viewed detail pages**.
Twenty-three papers received targeted appendix inspection. These counts are
per-paper page records; they are not a claim that every appendix, every figure
or every fine label was inspected. Necessary missing pages were rendered;
unreadable labels and uninspected supplements remain explicit.

- [Discovery readings](discovery-readings.json): 60 individual original records.
- [Holdout readings](holdout-readings.json): 30 individual original records.
- [Coverage](reading-coverage.json): counts and scope.
- [Pattern freeze](pattern-freeze.json): immutable card hashes and chronology.
- [Holdout assessment](holdout-assessment.json): all 240 P1-P8 applicability codes,
  qualifications and counterexamples with locators.

Reading used fresh-context delegated readers and local PDF text/page tools.
Interrupted discovery work resumed from saved records; completed papers were
not discarded or repeated. The parent completed one remaining ICML paper and a
missing ICLR figure inspection, with the additional scope recorded.

The eight cards were frozen after all 60 discovery readings and before holdout
reading. Two new contexts assessed the holdout. They received cards and their
assigned papers, not discovery notes or behavior-test expectations. File access
was restricted by instructions on a shared filesystem, not by an enforced file
jail. Requested models inherited the host default; independent actual service
model identities were not established. Each holdout had one reader, so the
study does not estimate inter-rater reliability.

The [held-out summary](holdout-summary.md) separates fits, qualified matches,
not-applicable cases and counterexamples. These are qualitative reader codes,
not paper-quality ratings or population prevalence estimates. Formal exposition,
construct validation and cost-frontier patterns have substantial genre/evidence
boundaries. Readability and claim/display mismatches also occur in selected
papers. The cards were not rewritten to improve holdout counts.

## Skill changes

The suite remains at 18 skills. The main additions are:

- `research-write`: research-type argument structures, calibrated original
  English examples, section responsibilities and caption/body division.
- `research-analyze`: question-to-evidence-to-display planning, explicit
  denominators, and separation of presentation, analysis, evidence and claim
  repairs.
- `research-implement`: a small runnable data-to-figure/table helper with source,
  code, configuration and output provenance.

All three share an
[argument/display record](../../skills/research-write/references/argument-and-figure-contract.md).
The installed [pattern library](../../skills/research-write/references/paper-style-study/index.md)
contains concise cards and source records; the detailed study stays in project
documentation. Navigation, survey and review receive only the necessary
connections. Local requests remain bounded; whole checks remain at M2-M5.

The cards distinguish observed patterns from editorial recommendations. Original
sentence examples and the shared implementation record are recommendations, not
quotations or claims about the sampled authors' internal workflows. Figures
illustrating a concept remain distinct from measured evidence.

Existing theory status, negative results, cross-domain reuse, contribution
auditing, focus maintenance, Goal continuation, optimizer bounds, two fresh
manuscript review rounds and submission authorization remain part of the suite.
Profile-specific model routing remains unchanged; the Magpie version retains
its Vertex credit hold.

## Runnable example and artifact inspection

The example input deliberately differs from the behavior fixture: 24 attempts
per method, 21/19 successes and successful-only latency 12.5/8.0 seconds. It is
explicitly illustrative. The [generated outputs](example-output/provenance.json)
include PDF/SVG/PNG, CSV/TeX, a table PDF/PNG and provenance.

Run from the repository root:

```text
python skills/research-implement/scripts/render_evidence.py --spec skills/research-implement/assets/evidence-example/figure.json --output .build/evidence-example
```

Thirteen focused renderer checks passed after implementation and repairs. They
exercise counts, failure/missing-data behavior, invalid values, duplicate/private
labels, reproducibility and protection of unrelated or edited outputs. Empty or
missing input produces pending status; it does not synthesize measurements.

The final PDFs are 3.25 inches wide. Both generator PNGs and the actual PDF pages
rendered with Poppler were viewed. Counts, precision, method identities and
conditional latency agree; no clipping was observed. This covers two short
method labels, not arbitrary complex figures or a specific venue's template.

The existing submission scanner produced three candidates and retained explicit
PDF/raster coverage gaps. Scoped inspection identified `/Root` as a PDF catalog
keyword and `//W3C//DTD` as a public SVG identifier. The original scan was not
relabeled as automated success. Metadata, text and actual pages were inspected;
the [disposition](example-submission-disposition.json) records limits and narrow
exceptions. This is not a submission approval.

## Before/after behavior

The four fixed synthetic tasks cover a method comparison, a known mathematical
consequence with unreviewed application, mixed results with a post-outcome
subgroup, and an aggregate agent benchmark.

[Before outputs](behavior-before/execution-coverage.json) were produced before
instruction edits. The baseline already preserves mathematical assumptions,
negative results, denominators, uncertainty limits and privacy. Its SVG was also
subsequently rendered and inspected by the parent without changing baseline
files; it is readable. The study does not invent a weak baseline or assume the
new layout is visually better.

The new execution uses the same raw tasks in a fresh context, without the rubric
or baseline outputs. The new bundle deliberately adds Matplotlib for its helper;
the original execution used a standard-library SVG renderer. Any implementation
benefit therefore includes the new helper/dependency, not solely prompt wording.

The [behavior assessment](behavior-assessment.md) compares actual outputs under
the frozen rubric. Both versions preserve numbers, proof status, failures and
scope. The new analysis makes question/claim/display links and repair choices
more explicit; the new writing makes the reader question and caption/body
division easier to hand off. These are organizational gains in these four small
tasks, not a general preference study or evidence of improved acceptance.

The implementation case actually produced PDF/SVG/PNG figures, CSV/TeX tables,
table PDF/PNG and provenance. One primary render and one rendering-only rerun
matched all eight renderer output hashes. The parent additionally rasterized
and viewed the actual figure/table PDF pages after the executor's receipt.
The immutable executor record says that it did not perform this extra check;
the [parent addendum](behavior-after/parent-inspection.json) records the later
coverage without changing that historical record. Method, theory and mixed
figures remain specifications, not rendered artifacts.

An independent fresh-context evidence review found no scientific blocker in the
four cases or recomputed study records. It identified release/report gaps and a
visual-locator validation gap, now addressed as recorded in
[review disposition](review-disposition.md). The review is an artifact audit,
not a simulated conference review or a scientific correctness certificate.

## Validation and deployment

See [validation](validation.json) for executed checks and the profile-specific
release receipt for the exact skills digest. Temporary installation, source and
personal-install hash guards, external backup and branch publication are
recorded in [deployment](deployment.json). Deployment is not inferred from
successful tests. Historical local `tests/results` records are excluded from
publication because they contain machine-specific paths; the current sanitized
study records provide the portable acceptance evidence.

## Limits

This descriptive, purposive study does not identify causes of conference
selection, forecast acceptance, or certify the sampled papers' proofs, novelty
or experimental validity. Reader-noted inconsistencies are presentation
observations within inspected scope, not comprehensive scientific errata.
The behavior tasks are synthetic and small. No real research experiment or
completed-paper outcome is attributed to the new guidance.

Raw PDFs, full-text extraction, copied paper figures, private configurations,
credentials, personal paths, browser profiles and raw gateway logs remain outside
the publication. The original illustrative outputs are the only study figure
assets included.
