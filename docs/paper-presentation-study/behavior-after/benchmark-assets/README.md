# Synthetic reliability and conditional-latency example

This package renders the supplied aggregate fixture for two agents under the same 20-task protocol. It does not evaluate agents or create per-task observations.

## Run

With Python and the declared dependencies available, run from this directory:

```text
python -X utf8 -B run_benchmark.py --output outputs
```

An optional rendering-only reproducibility check can use a separate destination:

```text
python -X utf8 -B run_benchmark.py --output outputs --reproduce-to reproduction
```

The implementation was exercised with Python 3.12.10 and Matplotlib 3.11.2. `requirements.txt` pins Matplotlib 3.11.2 and pypdf 6.21.2. The entry point records both installed versions; Matplotlib renders the outputs, and pypdf supports the separately performed PDF structure/text inspection. The generated bundle provenance records actual transitive plotting dependency versions. `validation-requirements.txt` repeats the PDF inspection dependency for clarity. pypdf does not render PDF pixels. No package installation is part of the example execution.

## Scientific contract

`fixture.json` preserves the supplied public scientific fields, including explicit failures. `aggregate.csv` is the four-column interface consumed by the supplied renderer; the entry point checks its rows against the fixture, including `failed = attempted - successful`. `evidence-spec.json` records width 3.25 inches, claim IDs, and analysis revision. The renderer's `illustrative` label denotes the input's `synthetic fixture` data kind, not measured research results.

Reference: 16 successful and 4 failed out of 20 attempts; success rate 80%; mean latency among its 16 successes is 15 seconds. Candidate: 14 successful and 6 failed out of 20 attempts; success rate 70%; mean latency among its 14 successes is 10 seconds. Successful subsets may differ. No uncertainty intervals, failure times, overall mean latency, per-task pairing, or utility scores are inferred.

`render_evidence.py` is copied unchanged from the supplied research-implement skill. `run_benchmark.py` validates the scientific interface, runs that implementation, checks actual table values, and optionally compares the hashes from a second render. It also checks missing successful-latency and invalid-count handling without introducing research observations. Fixed export date metadata and SVG IDs enable same-environment reproducibility; the export date is not an execution or experiment date.

## Outputs

`outputs/figure.pdf`, `figure.svg`, and `figure.png` show success over all attempts separately from latency among successes. `table.csv` and `table.tex` preserve counts, rate (a fraction), and conditional latency in seconds; `table.pdf` and `table.png` provide rendered table previews. Use `caption.md` alongside the figure. PNG outputs use 300 dpi; the PDF/SVG figure width is 3.25 inches.

`outputs/provenance.json` contains the renderer's input hash, transformations, environment, and generated-file hashes. `outputs/bundle-provenance.json` adds original data kind, exact input/code hashes, dependency versions, parser checks, and the optional reproduction outcome. All provenance paths are package-relative. The entry point reports generation/check status only; actual visual and PDF inspection is documented separately by the caller.

No venue requirements, author details, or public submission authorization are inferred. Treat this as a synthetic demonstration, not an empirical agent comparison.
