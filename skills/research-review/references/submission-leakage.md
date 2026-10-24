# Submission Content and Leakage Audit

Read before freezing M4/M5 reviewer inputs or delivering a submission package.
Audit the exact submitted copies, not the entire internal research workspace.
This protects privacy and paper quality; it does not conceal scientific AI use
or remove disclosures required by the venue.

## Inspect the complete submission surface

Check the manuscript source and rendered document, figures (including screenshots),
captions, bibliography, appendix, intended supplements and reproduction package.
Inspect archive member names and nested archives, document properties, comments,
tracked changes, hidden sheets, hyperlinks, embedded files, image metadata and
accessible text layers. An allowlist or a clean PDF body does not establish that
the attachment contents are clean. Do not include internal recovery/protocol
notes, prompts, reviews, project-state records or old source bundles accidentally.

At the milestone, run `python scripts/check_submission.py` from this skill's
directory with the explicit submitted artifact paths and `--output` pointing to
an internal audit file. It reads without changing inputs or extracting archives.
The report contains redacted finding locators/hashes and actual coverage gaps.
No raw credentials, local usernames or private paths belong in reports shared
with reviewers. Keep the report and any private replacement map outside the bundle.

The automated scan is a candidate detector, not a complete privacy or scientific
review. Inspect rendered pages, images and all unparsed/limited surfaces with
appropriate local tools; record exactly what was checked. A truncated archive,
unsupported format or missing parser is unchecked, never a clean result. Do not
upload private artifacts to an external detector merely to complete coverage.

## Findings and replacements

- Remove credentials, session tokens, private keys, real server/account identifiers
  and private endpoints. A private repository is not a substitute for sanitization.
- Replace local drive, home, network-share and file-URI paths with functional
  project-relative paths or explicit placeholders such as `<PROJECT_ROOT>`,
  `<SERVER_HOST>` and `<API_KEY>`. Do not include the private mapping in the bundle.
  Inspect JSON-escaped values, manifest keys and file names as well as prose.
- Remove accidental assistant replies, hidden reasoning tags, tool-call transcripts,
  conversation links, model-routing notes, Goal state, reviewer instructions,
  optimization notes and unrendered draft scaffolding from submitted artifacts.
- Review author/institution/user metadata under the actual anonymity policy.
  Legitimate author information in a nonanonymous submission is not automatically
  a leak. Do not invent author identities or infer private identity from prose.
- Scientific descriptions of AI, LLMs, agents, tools and reproducibility commands
  can be necessary content. Preserve accurate AI-use declarations and citations.
  A keyword or an alleged AI-writing style cannot establish misconduct or leakage.
  If a flagged term is genuinely the object of study, inspect the exact passage
  and document the narrow exception; never apply a blanket keyword exemption.
- Placeholders may stand for private infrastructure. They must not stand for
  missing results, citations, proofs or required declarations in a completed paper.

Create sanitized submission copies while retaining restricted original evidence.
Keep numeric results and scientific provenance intact. When a path-keyed manifest
changes, keep each data digest associated with the same relative scientific asset;
regenerate the manifest/container hash and update only affected delivery records.
Check the affected reproduction entry point after replacing paths. Do not rerun
training just because packaging metadata changed.

## Gate and cadence

Author-side admission precedes each blind review. Record artifact hashes,
archive-member coverage, scanner/tool versions, visual/manual scope, findings,
resolved replacements, justified exceptions and remaining gaps. Unresolved leaks
or required unchecked surfaces block the clean-input/delivery claim, not unrelated
authorized research. Send the blind reviewer only the sanitized frozen materials,
official criteria and neutral task; never the internal sanitization history.

If contamination is found after dispatch, preserve the actual review and label
its affected independence/coverage. Do not rewrite history as a clean blind round.
Replace contaminated inputs and resolve the required clean review under the
existing review budget; avoid an automatic sequence of additional full reviews.

Reuse a valid audit for unchanged artifacts. After repair, check changed files,
their containing archives and affected rendered pages. Full checks remain at
M4/M5 and final packaging, not after every paragraph or stage handoff. A passing
automated scan alone never certifies submission readiness.
