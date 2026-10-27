# Reproducible Evidence Display Example

This example turns a small aggregate CSV into a table, a two-panel figure and
provenance without inventing observations. The values are illustrative.

## Run

From this directory:

```text
python ../../scripts/render_evidence.py --spec figure.json --output rendered
```

The renderer requires Python 3.10+ and `matplotlib` for the figure. It writes
`figure.pdf`, `figure.svg`, `figure.png`, `table.csv`, `table.tex`,
`table.pdf`, `table.png` and `provenance.json`. If `results.csv` is missing or empty, it reports
`pending-data` and does not create a figure.

This example was visually validated with two methods, aggregate attempt/success
counts and successful-only latency. More methods require layout adjustment and
actual inspection. Use the project's plotting tools for
distributions, intervals, paired observations or other inferential quantities.
The example width is illustrative; derive the real width from the target
venue's current template. Inspect the output at that size.

The renderer replaces only unchanged outputs identified by its prior provenance.
It refuses to overwrite unrelated or edited files with reserved output names.
Input validation occurs before output replacement.

## What the example preserves

- Success uses all attempts; failures remain visible.
- Latency is conditional on successful attempts and includes its own `n`.
- Missing latency stays missing and is never replaced by zero.
- The figure and provenance state that uncertainty was not supplied.
- The data label is explicit (`illustrative`) and the source digest is recorded.
- Rerunning the same input yields the same table and scientific content.

The example does not establish scientific performance, venue compliance or
acceptance. Replace the illustrative data only after the research record supplies
the corresponding real run identities, analysis revision and claim IDs.
