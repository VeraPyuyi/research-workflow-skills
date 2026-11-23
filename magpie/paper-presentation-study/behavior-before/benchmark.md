# Benchmark case

Synthetic acceptance material, not a real evaluation of either agent.
Skills used: the old research-implement and research-write skills.
Source: fixture version 1, `cases[id=benchmark].evidence`.

## Runnable example and actual outputs

The complete Python plotting/table example is
`benchmark-submission/benchmark.py`. Dependencies: Python 3.10 or later and the
Python standard library only (`csv`, `hashlib`, `html`, `json`, `math`, `pathlib`,
`platform`, and `xml.etree.ElementTree`). Matplotlib is unavailable in the
installed interpreter and was not installed. NumPy is present but unused. The
example writes a vector SVG directly, so no plotting package is required.

Run from `benchmark-submission`:

```text
python -B benchmark.py
```

The script reads `benchmark_input.json` next to itself and writes all generated
files into that same directory. It validates nonnegative counts, nonzero
attempt denominators, successful+failed=attempted, finite successful latency,
the supplied fixture values, and the 3.25-inch width. It rejects empty,
inconsistent, missing, or changed aggregate data instead of silently inventing
observations or retaining a stale caption. It is a runnable aggregate reporting
example, not an implementation or rerun of either evaluated agent.

Executed successfully with the already installed Python 3.12.10, exit code 0.
The actual stdout is retained in `execution-coverage.json`. Generated outputs:

- `benchmark-submission/benchmark_table.csv`: machine-readable counts, rates,
  successful-only latency, and its denominator.
- `benchmark-submission/benchmark_table.md`: the same table with units and limits.
- `benchmark-submission/benchmark_figure.svg`: two-panel vector figure, 3.25 inches
  wide by 3 inches high; XML parsed and physical width checked in execution.
- `benchmark-submission/benchmark_caption.txt`: the caption below.
- `benchmark-submission/benchmark_provenance.json`: exact source/input/code/output
  SHA-256 fingerprints, transformations, dependency information, and limitations.

The sanitized input, source code, and `benchmark-submission/README.md` are also
retained, so the example can be reproduced without any additional input files.

## Table and interpretation

| Agent | Attempted | Successful | Failed | Success (%) | Failure (%) | Mean successful latency (s) | Latency n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| reference | 20 | 16 | 4 | 80 | 20 | 15.0 | 16 |
| candidate | 20 | 14 | 6 | 70 | 30 | 10.0 | 14 |

Candidate minus reference success is -10 percentage points. Its supplied mean
successful latency is 5 seconds lower, or 33.3% lower relative to the reference.
The latency means condition on potentially different successful task subsets.
They do not establish lower overall task latency or a matched-task speedup. All
failures remain visible in the all-attempt success and failure denominators;
no failure latency or fabricated task record is added.

Only aggregates were supplied. No per-task paired outcomes, seed variability,
confidence intervals, failure-time distribution, all-attempt mean latency, or
throughput estimate can be recovered without additional observations or
assumptions. The observation is a reliability/conditional-latency tradeoff;
these summaries do not identify a uniformly better agent.

## Short research-write caption

Synthetic aggregate comparison of two agents under the same 20-task protocol. The reference succeeds on 16/20 tasks (80%); the candidate succeeds on 14/20 (70%). Mean latency among successful attempts is 15 s (n=16) and 10 s (n=14), respectively. These means condition on potentially different successful tasks. Failure latencies and task-level variability are unavailable; no uncertainty intervals or overall-latency estimate are shown.

## Provenance and delivery boundary

The submission-facing example is confined to `benchmark-submission`. The
supplied private internal note was not copied into its input, source, table,
figure, caption, README, or provenance. That directory uses relative scientific
asset names, contains no private machine paths, and includes no model planning
or tool transcript. Provenance identifies the original fixture by basename,
version, case selector, and digest; the numeric input is included separately.
The SVG contains vector marks and text with no external resources or scripts.
All files in that directory are directly inspectable text, including SVG
metadata. Final local integrity and content-inspection coverage is recorded in
`execution-coverage.json`, outside the submission-facing directory.

Status: code execution, table export, SVG export, caption, and provenance output
completed. No dependencies were installed; no network, external model calls,
new benchmark runs, or rubric assessment were performed. The SVG has not been
raster rendered or visually inspected at final print size, and no actual venue's
format, anonymity, or disclosure requirements were supplied. No submission or
publication occurred. Next scientific step, if a broader comparison is desired:
obtain paired task outcomes, failure latencies, and repeated-run information
under a prespecified protocol. The supplied aggregates remain the only evidence
used here.