# Synthetic aggregate example

This portable example reproduces a table and figure from supplied synthetic
acceptance data. It does not execute either agent or represent research results.

## Dependencies and execution

Python 3.10 or later; Python standard library only. No package installation,
network access, credentials, or model calls are required.

Run from this directory:

```text
python -B benchmark.py
```

The program reads `benchmark_input.json` next to its own source and writes its
outputs into that same directory, independent of the caller's working directory.
The fixed fixture check prevents an unchanged caption from silently accompanying
new data. Rerunning replaces the generated files with reproducible versions.

## Files

- `benchmark.py`: complete runnable table and SVG example.
- `benchmark_input.json`: sanitized supplied aggregate input and source fingerprint.
- `benchmark_table.csv`: numeric table with all success/failure denominators.
- `benchmark_table.md`: readable table, units, and interpretation limits.
- `benchmark_figure.svg`: vector figure, exactly 3.25 inches wide by 3 inches high.
- `benchmark_caption.txt`: short caption for the figure.
- `benchmark_provenance.json`: transformations, input/code/output hashes, Python
  version, dependencies, and scientific limitations.

## Interpretation

Success rates use all 20 attempts per agent. Mean successful latency uses only
16 reference successes or 14 candidate successes. The successful task subsets
may differ. Failure latency and per-task or per-seed variability are unavailable;
there are no imputed observations, uncertainty intervals, or overall-latency
estimates. A lower successful-only latency and a lower success rate describe a
tradeoff, not a demonstrated overall improvement.

The SVG uses vector shapes, ordinary text, and no external assets or scripts.
Format, anonymity, and disclosure compliance depend on the actual destination
and have not been evaluated for this synthetic example.