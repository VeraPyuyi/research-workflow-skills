# Paper Presentation Study Index

This is an original, descriptive study of 90 official conference papers. It is
not a corpus of copied figures or a claim that a presentation pattern causes
acceptance. The frozen protocol, sampling rules, access limitations and
validation split are in [protocol.md](protocol.md).

## Scope

- Five venues: CVPR, ICLR, ICML, ACL and NeurIPS.
- Latest three publicly verifiable editions per venue at implementation time;
  NeurIPS 2023 is used as the bounded fallback when 2026 public full-text access
  was unavailable. ICLR 2026 officially uses Oral rather than Spotlight.
- Four officially selected papers and two ordinary accepted comparators per
  venue-year, with 60 discovery and 30 held-out papers.
- Main text, actual rendered figure/table pages and necessary appendices were
  inspected where available. PDF page locators are retained in the corpus record.

The selection was purposive and title/metadata-assisted; comparators are not
matched for measured writing quality or causal effect. Category names differ by
venue (Spotlight, Highlight, Oral, Outstanding Paper) and are retained as
reported. Failure to access a paper is an access limitation, not evidence that
the paper or edition does not exist.

## What was extracted

Each paper record describes the main question, argument sequence, section roles,
paragraph/language moves, visual encoding, caption/body division, readability,
transfer conditions and actual coverage. The study does not certify the paper's
proofs, novelty or experimental validity. Patterns require at least three
independent papers from two venues before they are stated as cross-venue
observations; single-paper observations and editorial recommendations remain
separate.

## Installed pattern cards

Read [the eight pattern cards](patterns.md) for conditional observations and
counterexamples, and [the source index](sources.md) for all 90 official identities.
Each card supplies purpose, applicability, action, an original example, source
IDs with PDF locators, and limits. `patterns.json` preserves the discovery freeze;
`sources.json` preserves categories, split, PDF digests and metadata corrections.
Reproducible generation and the sentence examples are editorial recommendations,
not claims that the sampled authors used the same workflow.

The [held-out applicability summary](holdout.md) records the separate 30-paper
check. Its genre limits and counterexamples do not turn the cards into universal
requirements; local tasks use only the guidance that helps their evidence.

The operational guidance is in
[paper presentation](../paper-presentation.md), with analysis handoff in
[evidence presentation](../../../research-analyze/references/evidence-presentation.md)
and a runnable plotting/table example under
[research-implement](../../../research-implement/SKILL.md).

## Limitations

The study is descriptive, not a randomized or causal analysis of writing. It
does not estimate acceptance probability. Conference categories, page limits,
review criteria and formatting changed across editions. Some PDFs contain
replacement glyphs in figure text; readers inspected detail images and marked
unreadable labels. Raw PDFs, extracted full text and copied figure assets are
kept only as local reading cache and are not part of the released skill bundle.
The CVPR 2026 virtual metadata frame was partial (200 rows, including 82 rows
without a decision label); chosen-paper identities and categories were checked
against their official pages, not treated as a complete proceedings frame.
