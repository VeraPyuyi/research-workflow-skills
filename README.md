# Paper-presentation study data

Data of the 90-paper presentation study behind
`skills/research-write/references/paper-style-study/` in the `magpie` and
`codex-native` branches. It was moved out of those branches on 2026-11-23 to
keep the skill bundle small; this branch holds no code.

| Directory | Source |
| --- | --- |
| `magpie/paper-presentation-study/` | `magpie` @ 4a5c2d0 (`docs/paper-presentation-study/`) |
| `codex-native/paper-presentation-study/` | `codex-native` @ 04975f2 (`docs/paper-presentation-study/`) |

The two copies differ only in five release-bookkeeping files
(`deployment.json`, `publication-check.json`, `release-receipt.json`,
`temporary-install.json`, `validation.json`).

Fetch for validation with `python scripts/fetch_study_data.py` from either code
branch, which checks out this branch at a pinned commit into `.build/`.

The files contain the authors' own descriptions, metadata and page locators of
public papers, not the papers' text or figures. Licensed under Apache-2.0
(see `LICENSE`).
