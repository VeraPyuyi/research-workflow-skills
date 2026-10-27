# Fixed-task behavior assessment

The four synthetic cases and independent rubric were frozen before baseline
execution. A fresh context completed the new tasks using the same raw inputs,
without baseline answers or expected results. No real research experiment,
external model-ranking call, or venue submission was part of these cases.
Independent review checked the actual artifacts, not just executor summaries.

| Skill | Baseline evidence | Observable new behavior | Interpretation |
| --- | --- | --- | --- |
| `research-analyze` | `behavior-before/method.md` and `mixed.md` already preserve paired values, uncertainty limits, all outcomes and claim states. | `behavior-after/method.md` links each reader question and claim to a display; `mixed.md` separates reporting the finite-suite result from new evidence needed for repeatability or structure. | More explicit analysis-to-display handoff and repair choice; no claim that the baseline was statistically unsound. |
| `research-write` | The baseline already has accurate prose, caveats and figure specifications. | The new method artifact includes a 120-word abstract and explicit caption/body responsibilities; the theory artifact separates the known bound, supplied lemma, displayed substitution and unvalidated application. | Clearer organization and proof-status communication within these cases. No blinded human readability rating or broad language-quality effect is established. |
| `research-implement` | A runnable standard-library SVG, CSV and provenance already existed; its rendered SVG was readable. | The new benchmark actually executes the packaged Matplotlib helper, produces vector/raster figures and tables, records configuration/source/output identity, and reproduces all eight renderer hashes. | Demonstrated export and provenance capability. The benefit includes a new helper and dependency, not only instruction wording; no general visual-superiority claim. |

## Fidelity and scope

- Method: both means are 73% accuracy; paired changes are +1, 0, -1 percentage
  points. Latency means are 81 and 41 ms, a 49.4% reduction. Neither version
  establishes accuracy equivalence or 3,000 independent examples.
- Theory: the displayed exact-gradient substitution yields the supplied descent
  bound under differentiability and an L-Lipschitz gradient, L > 0. Convexity,
  controller validity, independent proof review and novelty are not invented.
- Mixed: all eight task deltas average to zero. The post-outcome positive
  subgroup remains exploratory. An extra failed exploratory attempt is retained,
  without imputing a ninth score or changing the prespecified denominator.
- Benchmark: reliability remains 16/20 versus 14/20. Latency is conditional on
  16 and 14 successes respectively, 15 versus 10 seconds. Failure times,
  uncertainty intervals and overall superiority are not fabricated.
- All tasks remain bounded; no full-paper Goal, repeated workflow review,
  experiment launch or external submission was initiated by these local requests.

No new hard failure from the frozen rubric was found in the inspected outputs.
This is a scoped assessment, not proof of reliability over arbitrary future tasks.

## Execution and visual evidence

The executor performed one benchmark render, six focused interface checks and
one rendering-only reproduction. Eight renderer output hashes matched. The
figure and table PNGs were inspected. The parent later rasterized the two PDF
pages with Poppler and viewed those images; the addendum records this separate
operation and file hashes. The pages are 3.25 inches wide and show no observed
clipping for the two short labels. No physical print, arbitrary-label stress
test, separate SVG browser check or LaTeX table compilation is claimed.

The other three cases request specifications; their figures were not rendered.
The fixture values differ from the installed illustrative example. Neither
fixture is evidence of a scientific performance gain.

## Preserved failures and limitations

The executor retained a read-output truncation and a path-detector false
positive on mathematical notation. A narrow exception and one affected rerun
resolved the detector issue; outputs were not repeatedly sampled for favorable
answers. Raw local commands and account/environment paths remain private.

Baseline and new tasks each have one execution context, with no randomization or
inter-rater estimate. Served-model identity was not independently confirmed.
File separation was instructed on a shared filesystem, not enforced isolation.
The 30-paper holdout assesses pattern applicability, separately from these
four behavioral tasks; neither test estimates acceptance effects.
