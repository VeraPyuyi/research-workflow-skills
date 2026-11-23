# Method case

Synthetic acceptance material, not a real paper or new experimental result.
Skills used: the old research-analyze and research-write skills.
Source: fixture version 1, `cases[id=method].evidence`.

## Evidence presentation plan

1. Lead with the observed integration tradeoff on the fixed evaluation set:
   mean latency is 81 ms for the baseline and 41 ms with caching; mean accuracy
   is 73% for both. The contribution is this integration and its measured
   tradeoff. Caching is established according to the supplied related-work note;
   no primary literature or bibliographic identity was supplied or retrieved.
2. Present every paired training-seed result before the aggregate. The table's
   pair numbers indicate array positions; actual seed identities are unavailable.
3. Separate the latency finding from the accuracy question. Mean latency falls
   by 40 ms, or 49.4%, using the ratio of means; the ratio 81/41 is 1.98.
   Accuracy differences are +1, 0, and -1 percentage points, with a mean of zero.
   Equal means do not establish equivalence, noninferiority, or immaterial loss.
4. Close with scope: three paired training seeds, one fixed set of 1,000 examples
   per seed, and matched hardware, batch size, and decoding configuration. The
   reused examples are not 3,000 independent evaluation examples. No equivalence
   margin, prediction-level paired outcomes, timing repetitions, additional
   datasets, or independent confirmation were supplied. Recommend reporting the
   tradeoff and leaving practical accuracy preservation unresolved.

| Pair position | Baseline accuracy (%) | Cache accuracy (%) | Accuracy change (pp) | Baseline latency (ms) | Cache latency (ms) | Latency change (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 72 | 73 | +1 | 80 | 41 | -39 |
| 2 | 74 | 74 | 0 | 82 | 42 | -40 |
| 3 | 73 | 72 | -1 | 81 | 40 | -41 |
| Mean | 73 | 73 | 0 | 81 | 41 | -40 |

The sample SD of paired accuracy changes is 1.0 pp; the sample SD of paired
latency changes is 1.0 ms. These describe variation across the three paired
training-seed summaries, conditional on the fixed evaluation set. They are not
confidence intervals or estimates of population/dataset variation.

## Abstract

Cached representations may reduce inference cost, but their accuracy tradeoff requires explicit measurement. We compare a caching integration with its baseline on one fixed evaluation set of 1,000 examples using three paired training seeds under identical hardware, batch size, and decoding conditions. Mean accuracy is 73% for both systems; paired changes are +1, 0, and -1 percentage points. Mean latency decreases from 81 to 41 milliseconds, a 49.4% reduction and approximately 1.98 times faster inference. These synthetic acceptance measurements support a latency reduction in this configuration, while equal mean accuracy does not establish equivalence or rule out meaningful degradation. No equivalence margin was specified. Caching is established; the contribution is this evaluated integration and its measured tradeoff. Generalization remains untested.

## One main figure: specification

Use one two-panel figure titled "Observed accuracy and latency tradeoff".
Both panels have baseline and cache categories on the horizontal axis. Panel A
shows accuracy (%) from 70 to 76; Panel B shows latency (ms) from 0 to 90. Draw
three raw paired dot connections per panel using the table above, with consistent
pair identifiers across panels. Distinguish methods by both marker shape and
color. Overlay a clearly labeled mean diamond at 73/73% and 81/41 ms. The
nonzero accuracy-axis origin must be explicit. Do not add an equivalence band,
invent an acceptable-loss threshold, or use error bars with an unspecified type.

Caption: "Synthetic fixed-set comparison across three paired training seeds.
Each seed uses the same 1,000 evaluation examples; hardware, batch size, and
decoding are matched. Lines connect paired summaries and diamonds mark means.
Caching changes mean latency from 81 to 41 ms (49.4% lower); mean accuracy is
73% for both methods, with paired changes of +1, 0, and -1 pp. No equivalence
margin was specified, so equal mean accuracy does not establish equivalence."

## Claim evidence and handoff

| Claim | Evidence and transformation | State and remaining gap |
| --- | --- | --- |
| Lower latency in this supplied configuration | Three paired changes; mean -40 ms; (81-41)/81 | Supported descriptively in the synthetic record; timing variability and external validity absent |
| Equal observed mean accuracy | Means of the two three-element accuracy arrays are both 73% | Supported descriptively; individual paired effects differ |
| No material accuracy change | No practical margin or equivalence analysis | Unresolved; specify a justified margin before a new confirmatory comparison and retain paired outcomes |
| Invention of caching | Supplied note says caching is established | Contradicted by the supplied framing; retain integration-level contribution |

Artifacts: this requested section and figure specification; arithmetic and source
fingerprint are in `case_calculations.json`, reproduced by `case_calculations.py`.
Status: bounded presentation and arithmetic completed; the figure is specified,
not rendered. No training or inference experiment was run. External drafting and
independent review routes were not used because the user prohibited external
model calls. Next scientific step, if authorized separately: define what accuracy
loss would be material and design a paired confirmatory comparison. That work
has not been executed in this bounded task.