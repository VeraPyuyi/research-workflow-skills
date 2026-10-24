# Comparing Implementations and Reusing Code

Read for baseline replication, replacing code with a library, porting an evaluator
or accepting a regression comparison. Matching a reference establishes fidelity
to a stated contract; it does not establish that either implementation or the
scientific method is correct.

1. Fix the reference and intended claim. Record input/data revisions, inclusion
   masks, seeds or realized splits, versions and mapped options. Defaults in two
   libraries are not necessarily equivalent.
2. Inventory expected output channels before looking at the new comparison:
   values, uncertainty, denominators, IDs/order, diagnostics, warnings and failure
   states. Give each channel a comparison or a reason it is outside scope.
3. Define tolerances by meaning: exact labels/counts/statuses, justified absolute
   and relative numerical tolerances, and a suitable uncertainty criterion for
   stochastic outputs. Align by identifiers where order is irrelevant; test order
   explicitly where it is meaningful. Record any changed tolerance with its
   reason; do not widen it just to admit the observed discrepancy.
4. Check the comparator with a deliberate wrong value, an absent output, an empty
   result and misaligned identifiers. Required-output faults must be detected;
   skipping them is not a successful comparison.
5. Use known-answer cases and small witnesses for each consequential difference,
   then applicable regression checks. Classify a difference as a defect, an
   intentional difference, a reference limitation or unresolved.
6. Have a separate reviewer check important edge conditions and scientific
   assumptions against the actual artifacts. Do not equate two implementations
   copied from each other with independent confirmation.

Deliver the frozen comparison contract, actual results, mismatch witnesses,
unresolved differences and the specific scope established. A theorem can justify
an algorithmic identity while implementation, generalization and real-task
experiments remain necessary. Keep the evidence that supports each kind of claim.
