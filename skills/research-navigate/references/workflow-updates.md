# Portable workflow releases and project adoption

Use [the stdlib helper](../scripts/workflow_release.py) on a staged or installed
suite. `--skills-dir` names the directory containing `research-navigate` and its
sibling skills, such as a checkout's `skills` directory. The helper builds release
metadata and updates a project's workflow record. It does not install skills,
run a validator, dispatch agents, or modify scientific artifacts.

At entry, resumption, or a handoff, inspect the current suite and designated
project record. A validated compatible update within the same runtime profile can
be adopted under existing automatic-update authority without asking again.
Profiles are `magpie` and `codex-native`; changing profile requires an explicit
switch instruction and its authority reference, even with the same contract major.
Existing agents must explicitly
read updated instructions at a supported boundary; this is not hot injection.
Running jobs keep their recorded workflow/code/data/config versions.

The project's private runtime profile, such as
`config/workflow-runtime.local.json`, records the installed
suite location, external validation receipts and the user's compatible-update
instruction. At project entry, use that actual authority reference to initialize
`workflow.automatic_update_authority` if the project uses this suite and has no
contrary instruction. Preserve explicit project opt-outs and customized copies.
If the profile is absent, use the project's existing authority and installation
configuration; do not invent permission or require this machine-specific path.
The invocation still performs inspection/adoption explicitly. No background
process watches chats or modifies running instructions.

## Candidate construction and validation

Examples below use PowerShell variables only for shorter commands. Substitute
the actual staged suite and project directories. All mutations require `--apply`.

```powershell
$helper = Join-Path $env:RESEARCH_SUITE_ROOT 'skills/research-navigate/scripts/workflow_release.py'
$suite = Join-Path $env:RESEARCH_SUITE_ROOT 'skills'
$project = $env:RESEARCH_PROJECT_ROOT
python -B $helper build-release --skills-dir $suite --release-id research-20261024 --contract-version 1.0 --runtime-profile codex-native --receipt-ref 'validation:release-20261024'
python -B $helper build-release --skills-dir $suite --release-id research-20261024 --contract-version 1.0 --runtime-profile codex-native --receipt-ref 'validation:release-20261024' --apply
```

The first invocation prints a candidate without writing. The second atomically
writes `research-navigate/references/workflow-release.json` within `$suite`.
Candidate generation is not validation or publication. Finish all source edits,
including references, before building and validating the integration candidate.
The coordinator owns generation of the checkout's source release metadata.

Packaged metadata schema version 1:

```json
{
  "schema_version": 1,
  "contract_version": "1.0",
  "runtime_profile": "codex-native",
  "release_id": "research-20261024",
  "status": "candidate",
  "files": {
    "research-navigate/SKILL.md": "<64 lowercase hexadecimal SHA-256 characters>",
    "research-navigate/references/workflow-contract.md": "<SHA-256>"
  },
  "validation_receipts": ["validation:release-20261024"],
  "bundle_digest": "sha256:<64 lowercase hexadecimal characters>"
}
```

`files` contains every regular file under the supplied suite, using exact byte
hashes and forward slash relative paths. Only the metadata file itself and
`__pycache__` entries are excluded. Added, removed, or edited files invalidate the
inventory. Links, junctions, other reparse points, special files, path escapes,
Windows alternate streams, reserved path names and case-colliding files fail
closed. Even excluded entries may not be links or junctions.

The bundle digest is SHA-256 of the complete metadata object with only
`bundle_digest` removed, serialized by Python `json.dumps` with `sort_keys=True`,
`separators=(",", ":")`, `ensure_ascii=True`, `allow_nan=False`, then ASCII encoded.
Thus the digest binds the release identity, schema, contract, runtime profile, all file hashes,
receipt references and any extra metadata fields. The builder has no timestamp,
so identical inputs produce identical metadata. Set stable receipt references
before validation; changing them changes the digest. Receipts stay outside the
suite to avoid a circular content dependency.

Every new build requires an explicit `--runtime-profile codex-native|codex-native`.
The root manifest declares `runtime_profile: magpie`; the builder takes the
explicit argument and never guesses a profile from a directory, manifest, release
name, contract version, authority or installed host. Validation rejects invalid or
missing profiles, with one exact legacy exception: release
`research-20261024-jev-autonomy-v1` with digest
`sha256:ae6c9e10217a8dd14b4aab2c736366340ea568f533f47ff59671732c5d121d63`
has effective profile `magpie`. Both identity and content digest must match and
the metadata digest is still checked. Unknown unprofiled releases fail closed,
including previously adopted records with a separately asserted profile. Legacy
metadata remains byte-for-byte equivalent as a JSON value, preserving its digest
and receipt binding; reports expose its effective `runtime_profile` separately.

Supply an actual release-validation receipt from the validation process:

```json
{
  "schema_version": 1,
  "receipt_id": "release-validation-20261024",
  "bundle_digest": "sha256:<exact candidate digest>",
  "scope": "workflow-release",
  "status": "passed",
  "evidence_refs": ["validation:actual-targeted-tests", "validation:actual-package-checks"]
}
```

This is an illustrative shape, not an executed receipt. Its producer should
declare the `workflow-release` scope only after checking the exact candidate's
package and relevant adoption behavior. `evidence_refs` must be a nonempty list
of nonempty strings. Schema version must be integer 1; boolean `true` is not a
schema version or a passed status. Receipt identity, matching content digest,
exact scope and string status `passed` are required. A bare `validated: true`, a
receipt for other bytes, or a unit-test-only scope cannot authorize adoption.

```powershell
python -B $helper inspect-release --skills-dir $suite
python -B $helper inspect-release --skills-dir $suite --validation $env:RESEARCH_VALIDATION_RECEIPT
```

Build metadata only from an isolated suite. During inspection, the metadata's
top-level packages define the suite: every file within those packages is rehashed,
including unexpected additions. Other personal/system skills beside them are
outside that release and remain untouched. This permits inspection of the real
personal skills directory without treating unrelated skills as package corruption.
Supplied receipts
are explicit `--validation` inputs; packaged receipt references are provenance
locators and are never automatically followed. Multiple receipts may be supplied;
each must pass these checks. No receipt means `candidate` for release inspection
and `validation-needed` for project adoption. A malformed or mismatched receipt
is an error, even if another supplied receipt is valid.

The helper describes accepted receipts honestly as **supplied declarations**.
It does not authenticate their author, execute or inspect their evidence refs,
provide signatures, establish cryptographic external trust, or prove scientific
validity. SHA-256 binds content; it does not establish who validated that content.

## Project state and authority

Select an existing JSON object with `--state`, using a forward slash path relative
to the project. Missing, malformed, incompatible, external, linked or ambiguous
designated state is an error; the helper never silently falls back around it.
Without `--state`, discovery recognizes `project-state.json` and
`.research/project.json`. If both exist, select explicitly. If neither is present,
and no state is designated, `.research/workflow.json` is the optional fallback.
Dry runs never create it or its parent directory.
The state must also be outside the digested suite; adopting into a packaged
state file would change the very candidate being adopted and is rejected.

For a differently named state file, always supply `--state`. For a tracker,
database, non-JSON record, or state outside the project, use the existing system's
adapter; this helper cannot discover arbitrary storage conventions. Do not use
the fallback to bypass a known designated store. This is a portable JSON adapter,
not a mandatory new project backend.

The chosen object retains its existing keys and extends a `workflow` object.
An existing automatic-update authority has this representation:

```json
{
  "goal": {"id": "existing-native-binding"},
  "delegation": {"reference": "existing-startup-instruction"},
  "milestone": "M3",
  "workflow": {
    "runtime_profile": "codex-native",
    "automatic_update_authority": {
      "enabled": true,
      "reference": "user:actual-instruction-covering-compatible-workflow-updates"
    }
  }
}
```

The helper never manufactures this authorization. The enabled flag and a
nonempty instruction reference must already exist. An invocation's `--apply`
opts into writing; it does not grant scientific or workflow authority. Missing
authority returns `decision-needed` without changing the record. Preserve the
actual instruction and scope when establishing authority in the existing system.

Contract versions use `MAJOR.MINOR` or `MAJOR.MINOR.PATCH`, with missing patch
treated as zero. The publishing convention is that a nondecreasing version with
the same major is compatible. A major change or version downgrade returns
`decision-needed` with `incompatible-contract`. Reusing an adopted release id
for a different digest returns `decision-needed` with `release-id-reused`.
The helper cannot infer semantic compatibility from prose or migrate an
incompatible contract. Resolve that decision and any migration in the existing
project workflow; it provides no force/bypass option.

`workflow.runtime_profile` binds the project's active runtime. If an adopted
release exists, this field must agree with that release's effective profile.
Older project records without the field use their validated adopted metadata's
profile, including the exact legacy mapping above. On first adoption, an existing
project profile still constrains automatic adoption. An unbound new project may
adopt the explicitly profiled candidate under its recorded automatic authority.
Each successful adoption stores the profile in the workflow record and history;
original historical entries and legacy metadata retain their original values.

A cross-profile candidate returns `decision-needed` with `runtime-profile-switch`.
`--apply` and automatic-update authority alone cannot authorize it. To execute an
already authorized switch, supply both its target and the actual instruction:

```powershell
python -B $helper adopt-project --project $project --skills-dir $suite --validation 'D:\validation\native-release.json' --switch-runtime-profile codex-native --switch-authority-ref 'user:actual-instruction-to-switch-this-project' --apply
```

Omit `--apply` or use `inspect-project` with the same switch arguments to preview.
The target must match the candidate. A target without authority, authority without
a target, or a mismatched target cannot authorize a cross-profile adoption.
Alternatively, the project's existing authority system can record this exact
transition in `workflow.runtime_profile_switch`:

```json
{
  "from_runtime_profile": "magpie",
  "to_runtime_profile": "codex-native",
  "bundle_digest": "sha256:<exact target candidate digest>",
  "authority_ref": "user:actual-instruction-to-switch-this-project"
}
```

All four fields must match; the authority reference must be a nonempty string.
The helper consumes the recorded switch only after successful adoption and saves
the transition in that history entry. Explicit switch arguments take precedence
over a recorded switch. Switch authority can authorize that transition while
automatic updates are disabled; it does not enable later automatic upgrades.
It still requires a matching passed release-validation declaration, compatible
contract, distinct release identity for changed bytes, and pristine local copies.
Job versions and retained copies keep their existing pins. Authority references
remain declarations of actual instructions, with no authentication added by the
helper. A switch never fabricates release-validation evidence.

```powershell
python -B $helper inspect-project --project $project --state 'records/state.json' --skills-dir $suite --validation $env:RESEARCH_VALIDATION_RECEIPT
python -B $helper adopt-project --project $project --state 'records/state.json' --skills-dir $suite --validation $env:RESEARCH_VALIDATION_RECEIPT
python -B $helper adopt-project --project $project --state 'records/state.json' --skills-dir $suite --validation $env:RESEARCH_VALIDATION_RECEIPT --apply
```

Omit `--state` only when discovery or the documented fallback applies. Inspection
and adoption without `--apply` return the proposed record. When all conditions
hold, `--apply` adopts automatically under the recorded authority. It updates:

- `workflow.adopted_release`: the complete content-bound metadata and file hashes.
- `workflow.runtime_profile`: the adopted release's effective runtime profile.
- `workflow.previous_release`: the prior adopted metadata, or null on first adoption.
- `workflow.upgrade_history`: appended UTC time, from/to ids, digest, authority ref,
  `runtime_profile`, `from_runtime_profile`, `to_runtime_profile` and checked receipt
  declarations. Explicit switches also record the scoped `runtime_profile_switch`.
  Existing entries remain.
- `workflow.running_job_pins`: existing pins remain intact. Missing pins are
  captured from existing `jobs` list or id-keyed object entries with status
  running, queued, submitted, pending or unknown. Recognized version fields are
  workflow_release, release_id, code, data, config, versions and suffixes
  `_version`, `_revision`, `_digest`. Unknown job representations stay unchanged;
  no version is invented or assigned to a live job.
- `workflow.local_copy_pins`, when copies exist: project-relative copy locations,
  observed file hashes and the known release digest, so retained pristine copies
  remain distinguishable from customization across successive adoptions.

Existing Goal, delegation, milestones, protocol, jobs and unknown fields retain
their JSON values in the same record. Scientific protocol files, datasets,
manuscripts and job artifacts are never opened for writing. JSON formatting may
change because the record is serialized atomically. Repeating an adoption of the
same digest requires supplied validation again and makes no write or history
entry; it reports `already-adopted`. A newly customized local copy still reports
a conflict, including after an earlier successful adoption.

## Project-local copies

The helper checks project-local `.agents/skills`, `.codex/skills` and `skills`
directories for `research-*` copies. Add one more project-relative root with
`--local-skills`. Compare all files of each present skill against the previously
adopted hashes, or the candidate on initial adoption. Added, missing or changed
files and unknown research skills are conflicts. A copy matching the new
candidate is also recognized as pristine; saved copy pins recognize previously
retained pristine copies. Cache and release metadata exclusions remain the same.

Custom variants stay untouched and block adoption with `conflict`; the report
names copy locations and differing files. Neither pristine nor customized copies
are overwritten by this helper. Record adoption identifies the suite for future
work; it is not installation or a claim that an older project-local copy loaded
new instructions. Retained copies keep their hashes/version pins until explicitly
reconciled by the existing installation workflow. Personal installations are
outside this helper's discovery and writes.

## Public Python API and output

Import the standalone script with Python 3.10 or later; it has no third-party
dependencies and no network behavior. Public entry points:

```python
build_release(skills_dir, release_id, contract_version,
              validation_receipts=(), apply=False, runtime_profile=None)
inspect_release(skills_dir, validation_receipts=())
inspect_project(project, skills_dir, state=None,
                validation_receipts=(), local_skills=None,
                switch_runtime_profile=None, switch_authority_ref=None)
adopt_project(project, skills_dir, state=None,
              validation_receipts=(), local_skills=None, apply=False,
              switch_runtime_profile=None, switch_authority_ref=None)
exclusive_lock(record_path)  # context manager, parent directory must exist
main(argv=None)
```

For `build_release`, `validation_receipts` contains provenance reference strings;
for inspection/adoption it contains receipt file paths.
`runtime_profile` must explicitly be `magpie` or `codex-native` (`None` raises
`ValueError`, preserving existing positional argument meanings).
Functions return ordinary
JSON-compatible dictionaries. Unsafe inputs raise `ValueError`, I/O failures raise
`OSError`, and lock contention raises `LockError`, a `ValueError` subclass.

All CLI output records use `schema_version: 1`. Build output has `status:
candidate`, `applied`, `metadata_path`, `runtime_profile`, `release`.
Release inspection output has `status: candidate|verified`, `runtime_profile`,
`release`, `validation`. `verified` means the content
matched supplied declarations with the limitations above, not external attestation.

Project inspection/adoption output has:

| Field | Meaning |
| --- | --- |
| `status` | `ready`, `adopted`, `already-adopted`, `validation-needed`, `decision-needed`, or `conflict` |
| `applied` | True only after this invocation successfully replaces the project record |
| `project`, `state_path`, `state_source` | Absolute paths and `designated` or `fallback` |
| `release`, `previous_release` | Candidate and currently adopted release metadata |
| `runtime_profile`, `previous_runtime_profile` | Effective candidate and current project profiles, including the exact legacy mapping |
| `validation` | Derived `accepted`, checked receipt details and explicit declaration trust limitation |
| `decisions` | Stable reason strings such as `incompatible-contract`, `automatic-update-authority`, `runtime-profile-switch`, or `runtime-profile-switch-target` |
| `conflicts`, `local_copies` | Locations, `customized` or match status, differing files and observed hashes |
| `running_job_pins` | Preserved or captured versions; no running job changes |
| `record` | Proposed record for `ready`, written record for `adopted`, original record otherwise |

CLI exit code is 0 for successful candidate/inspection/adoption or idempotent
no-op, 2 for `conflict`, `validation-needed` or `decision-needed`, and 1 for invalid
input/I/O/lock errors. Errors are JSON on stderr with `schema_version`, `status:
error` and `error`. Argument syntax errors use argparse's normal exit code 2.

## Atomicity and limits

Apply holds an exclusive `O_EXCL` sibling `<state>.lock`, rereads and revalidates
the project/candidate under that lock, writes a same-directory temporary file,
flushes/fsyncs it and calls `os.replace`. A failed replacement leaves the old
record intact, removes the temporary and releases the lock for retry. The builder
uses an exclusive sibling `.<suite-name>.workflow-release.lock` outside the suite
inventory and the same atomic replacement. All cooperating writers must use
these locks. Stale locks are never stolen automatically: reconcile the owner
before an operator removes one. A hard process termination can leave a stale
lock or orphan temporary; inspect before recovery.

The helper rejects existing links/junctions/reparse ancestors before use. This
is not an adversarial filesystem sandbox: portable stdlib checks cannot prevent
a hostile process replacing directories between checks, and locks cannot stop
noncooperating editors. File fsync plus atomic replace does not promise directory
fsync or crash durability on every filesystem/network share. Keep validated
staging immutable during adoption. These limits do not turn receipt declarations
into a trusted signing system or change scientific permissions.
