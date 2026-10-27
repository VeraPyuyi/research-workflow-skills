# Method: caching integration and its observed trade-off

Revision: method-v1. Evidence: supplied fixture version 1, `paper-presentation-cases.json`, case `method`, all evidence fields. These are synthetic acceptance inputs, not results of a research experiment performed here.

## Evidence presentation plan

Reader question: can cached representations reduce inference time without materially changing task accuracy? Lead with the integration of established caching, then the matched comparison, then the unresolved accuracy-preservation criterion. No architecture, cache policy, mechanism intervention, or primary related-work source was supplied; do not invent one.

| Claim | Supplied evidence and calculation | Display and bounded conclusion |
| --- | --- | --- |
| M1: lower observed latency | Three paired seed summaries: baseline 80, 82, 81 ms; cache 41, 42, 40 ms. Equal-weight means 81 and 41 ms; differences -39, -40, -41 ms. | Figure M-F1a: all pairs. Reduction of the mean is 40 ms, or 49.4% relative to baseline, under the matched conditions only. Supported descriptively. |
| M2: equal observed mean accuracy | Baseline 72, 74, 73%; cache 73, 74, 72%; both means 73%. Paired differences +1, 0, -1 percentage points. | Figure M-F1b: retain every paired difference, including the loss. Equal means and an observed difference range of [-1, +1] points are supported; accuracy equivalence is unresolved. |
| M3: integration contribution | The fixture states that caching is established. | Frame the contribution as this integration and its observed trade-off; neither invention of caching nor a verified mechanism is established. Source identity for related work remains unavailable. |

The comparison uses the same hardware, batch size, decoding configuration, fixed evaluation set, and three paired training seeds. Each seed evaluates 1,000 examples; reusing the set does not provide 3,000 independent test examples. Timing repetitions and per-example predictions are unavailable. Use descriptive paired values, not a confidence interval, equivalence claim, or significance claim. Failure/attempt counts were not supplied for this case and are not assumed zero.

The existing evidence permits presentation and claim repair. An accuracy-preservation claim needs a justified, prospectively specified materiality/equivalence margin and an analysis with appropriate paired uncertainty and dependence treatment; new validation may be needed. Extra seeds alone do not define that margin. Mechanism attribution needs a targeted intervention; broader generalization needs additional settings. Those are proposed evidence repairs, not executed work.

## Abstract (120 whitespace-delimited words)

Cached representations may reduce inference latency, but their accuracy trade-off requires matched evaluation. Using supplied synthetic summaries, we examine a caching integration on one fixed evaluation set of 1,000 examples across three paired training seeds, holding hardware, batch size, and decoding configuration constant. Mean latency decreases from 81 to 41 milliseconds, a 49.4% reduction, while mean accuracy is 73% for both systems. Paired accuracy changes are +1, 0, and -1 percentage points. The contribution concerns integration of established caching and its measured trade-off. Equal mean accuracy does not establish equivalence: no acceptable accuracy margin was prespecified. These summaries support lower observed latency in this setting; accuracy preservation and generalization remain unresolved, and three training seeds offer limited information about variability.

## Main figure specification: M-F1

- **Purpose/claims:** make the latency advantage and accuracy uncertainty visible together; support M1 and the descriptive part of M2.
- **Input/transform:** fixture `method` arrays in supplied order; label pairs 1-3 as display indices, not actual seed identifiers. Latency is untransformed in ms. Accuracy change is cache minus baseline in percentage points. No exclusions, imputation, or new observations.
- **Panel a:** paired dots and lines from baseline to cache, one line per seed pair. X: method; Y: latency (ms), an explicitly shown 35-85 ms range suitable for points, not magnitude bars. Blue circles for baseline and orange triangles for cache. Annotate the two arithmetic means, 81 and 41 ms.
- **Panel b:** dots for all three accuracy differences (+1, 0, -1), plus a separately labeled mean diamond at 0. X: pair index, with a separate mean position; Y: accuracy change (percentage points), -2 to +2 with a zero reference line. Retain the negative difference. Do not draw a tolerance band because no margin was specified.
- **Uncertainty:** n=3 paired seeds; raw paired spread only, with no inferential interval. The fixed evaluation set contains 1,000 examples per seed. Neither the range nor equal means is an equivalence test.
- **Output/readability:** proposed 7-inch-wide, two-panel PDF/SVG with a PNG preview; this is an editorial suggestion, not a venue requirement. Use at least 8-point labels at that width and redundant shapes. Verify clipping, signs, and legibility when implemented.

**Caption.** Synthetic comparison of a caching integration with its baseline on one fixed 1,000-example evaluation set across three paired training seeds, under the same hardware, batch size, and decoding configuration. (a) Paired latency summaries and their means: 81 ms for the baseline and 41 ms with caching, a 49.4% reduction of the mean. (b) Paired accuracy changes of +1, 0, and -1 percentage points; mean accuracy is 73% for both methods. Marks show supplied seed summaries, not confidence intervals. No accuracy equivalence margin was prespecified.

The body interprets whether this trade-off meets the scientific objective; the caption defines the comparison. Equal mean accuracy cannot settle the materiality question.

## Bounded handoff

Artifacts: this plan, abstract, and M-F1 specification, version 1. Evidence: supplied case plus local arithmetic recorded in `internal/calculations.json`. Status: requested writing and calculation complete; figure specified only, not rendered or visually inspected. Open issues: accuracy margin, sampling uncertainty, mechanism and external validity, missing related-work citation. Next step: return this bounded artifact; any further study needs its own protocol. No independent review or external verification is claimed.
