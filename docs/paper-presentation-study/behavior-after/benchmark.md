# Benchmark: reliability and conditional latency

Revision: benchmark-v1. Evidence: supplied fixture version 1, case `benchmark` in `paper-presentation-cases.json`. These are synthetic summary inputs, not agent evaluations executed in this task.

## Question, evidence, and bounded conclusion

Reader question: how do reliability and latency compare for two agents under the same supplied 20-task protocol? Preserve every attempted task in the reliability denominator and report time only for the successful populations supplied.

| Method | Attempted | Successful | Failed | Success rate | Mean latency among successes (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| reference | 20 | 16 | 4 | 80% | 15.0 (n=16) |
| candidate | 20 | 14 | 6 | 70% | 10.0 (n=14) |

B1 (descriptive reliability) is supported by successes divided by all 20 attempts per method: the candidate is lower by 10 percentage points, or two successes. B2 (descriptive conditional latency) is supported by the supplied success-only means: the candidate is lower by 5 seconds (33.3% relative to 15 seconds). No latency is assigned to failures. The successful subsets may differ, so this is not a paired speed effect or an overall latency comparison. B3 (overall superiority) is unresolved: no paired task outcomes, failure times, variability, cost weighting, or utility function was supplied. No uncertainty interval or significance claim is inferred from these aggregates.

## Actual runnable deliverables

The portable package is `benchmark-assets/`. Its `run_benchmark.py` executes the supplied `render_evidence.py`, copied without modification. `fixture.json` retains only the allowed scientific fields; `aggregate.csv` and `evidence-spec.json` give the renderer's exact input, 3.25-inch width, and claim IDs. The original data kind remains synthetic fixture; the renderer uses its supported label illustrative, which is explained in the caption and provenance.

Run from that package using:

```text
python -X utf8 -B run_benchmark.py --output outputs
```

The executed environment was Python 3.12.10, Matplotlib 3.11.2, and pypdf 6.21.2. Dependencies are declared in `requirements.txt`, with actual transitive plotting versions in the provenance. The entry point records the pypdf version; separate PDF verification uses pypdf. No dependency was installed. Exact local commands, timings, stdout/stderr, and environment settings are retained under `internal/`, outside the portable package.

Actual outputs in `benchmark-assets/outputs/` are `figure.pdf`, `figure.svg`, `figure.png`, `table.csv`, `table.tex`, `table.pdf`, `table.png`, `provenance.json`, and `bundle-provenance.json`. The figure uses two vertically arranged panels: all-attempt success rate and success-only mean latency. Rates and times have separate zero-based axes and units, with consistent method colors and categorical positions. Tables explicitly retain failures.

## Caption

Synthetic comparison under the same supplied 20-task protocol. (a) Success over all attempts is 16/20 (80%) for the reference and 14/20 (70%) for the candidate, with 4 and 6 failures respectively. (b) Mean latency among successful attempts only is 15 seconds (n=16) and 10 seconds (n=14). The candidate has a 5-second lower conditional mean alongside a 10-percentage-point lower success rate. Successful subsets may differ. Only aggregates were supplied; no per-task or repeated-run uncertainty is available, and no inferential intervals are shown. These illustrative values do not establish overall latency or utility superiority.

## Execution and inspection coverage

One primary rendering run completed with exit code 0. Six focused checks passed: source/CSV agreement, attempt accounting, table values, preservation of missing latency with zero successes, rejection of a zero-success latency value, and rejection of a negative count. One rendering-only reproduction check matched all eight renderer output hashes and scientific rows. No agent task, new data collection, training, or live research experiment was performed.

The actual figure/table PNGs and their 312-pixel-wide, nominal-96-dpi previews were viewed. Labels and values were readable without observed clipping. Both PDF files have one page at exactly 3.25 inches wide; their text, metadata, and embedded fonts were checked. SVG XML/text and PNG metadata were inspected. The scoped package check found no supplied private note, concrete author-machine path, or internal planning text in the inspected export surfaces. Public provenance contains relative paths; the internal receipt is not part of the export package.

Limits: PDF pages were not rasterized or visually opened, no physical print was inspected, SVG was not separately displayed, and the LaTeX table was not compiled. No venue rules, author information, independent scientific review, or submission authorization are inferred. Thus the output is a checked synthetic example with explicit inspection coverage, not a venue-readiness certification.

Two tooling issues are retained in the internal receipt: a reference-read display truncation recovered by smaller reads, and an overly broad path detector that flagged mathematical notation in `theory.md`. The latter was resolved by a narrow, documented non-path exception and one successful affected check rerun; benchmark displays were not regenerated. Dependency documentation was also reconciled with the installed pypdf requirement after rendering, with updated documentation hashes and unchanged scientific assets.

## Bounded handoff

Artifacts: this explanation/caption, the runnable package, actual generated displays/tables, safe provenance, and `execution-coverage.json`. Evidence: only the supplied aggregates and local generation/check operations. Status: all requested benchmark work completed, with inspection limits above. Open issues: aggregate-only scientific uncertainty and unperformed format inspections. Next step: return these artifacts; no extra review, experiment, or submission is initiated.
