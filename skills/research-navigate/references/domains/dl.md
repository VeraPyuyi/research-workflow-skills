# Deep Learning Adaptation

## Design and implementation

Define population, target, split unit, preprocessing, augmentation, architecture,
objective, optimization, tuning search and model-selection rule. Check leakage
through preprocessing, related samples, time, subjects and repeated entities;
choose the split appropriate to the scientific claim.

Compare against credible tuned controls under documented data, tuning and training
resources. A changed resource budget is a study factor to report, not a hidden
method benefit. Keep validation/model selection separate from final testing.

Check tensor shapes, labels, loss/metric definitions and small known-answer or
overfitting cases. Passing these checks validates parts of the implementation,
not the claimed generalization improvement.

## Execute and analyze

Record seeds, configuration, code/data versions, environment, checkpoints and the
selection rule. Retain all attempts, including unstable or failed training.
Separate variation across data samples/splits from variation across training runs.
Choose repetitions and uncertainty methods for the actual sampling design.

Use ablations to isolate relevant components; consider calibration, robustness,
distribution shift or mechanism checks only when they bear on the claim.
Report resource and predictive-quality tradeoffs with their conditions.

## Review and product

Trace the evaluated checkpoint and preprocessing into the product. Check that
packaging, quantization or runtime changes retain required quality and behavior.
State the tested population and failure regimes instead of implying universal
generalization from a single benchmark.
