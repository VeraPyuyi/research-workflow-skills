# Study data location

The data behind [the study report](report.md) — 90 reading records, the
behaviour comparison, rendered figures and release bookkeeping (84 files, about
1.4 MB) — was moved out of this branch on 2026-11-23 to keep the skill bundle
small. It lives on the data-only branch `paper-presentation-study-data` of this
repository, pinned at commit `81261ddcdd05fbee53a728ebdb8618f6bc5ce7bc`:

- Browse: <https://github.com/VeraPyuyi/research-workflow-skills/tree/81261ddcdd05fbee53a728ebdb8618f6bc5ce7bc/magpie/paper-presentation-study>
- Fetch for validation: `python scripts/fetch_study_data.py`, which checks the
  content manifest and writes the files to `.build/paper-presentation-study`.
  Then run `python scripts/validate_presentation_study.py`.

The removed files remain in this branch's git history before the move.
