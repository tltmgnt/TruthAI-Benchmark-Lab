# Benchmark design and limits

This release supplies directed reachability tasks as a bounded first benchmark.
Omitted reachable nodes are not missing mathematical inference dependencies. Labels
may be wrong: digest binding prevents accidental mismatch, not invalid ground truth.
The scorer does not silently replace reference labels with its own traversal output.

Freeze dataset version/digest, label provenance, adjudication protocol, split, comparator
revisions, primary metrics and practical thresholds before evaluation. Record task sampling,
within-unit correlation, hardware, environment, execution-order controls, resource budgets,
warmup, repetitions, timeouts, missing-data policy and exclusions. Keep reference labels
outside development/runner access. A public fixture is not a hidden evaluation.

The importer rejects missing/duplicate task rows instead of silently selecting successful
pairs. Explicit errors/timeouts remain in correctness rates and omission counts, with
time deltas suppressed. It compares correctness before offering correctness-matched
timing differences. Memory remains Python allocation peak only. Grouped unit summaries
are descriptive; this release performs no bootstrap, significance test or causal attribution.
Do not count repeated deterministic timings as independent tasks or external reproductions.

The built-in runner is bounded by graph size, not a process sandbox or enforced timeout.
It accepts no arbitrary executable adapters. An external harness must enforce real budgets,
isolate untrusted code, collect observations and submit timeout/error rows. Interface
separation cannot guarantee operator honesty or data secrecy. No uploads, paid services,
messages, schedules or deployment permissions are added.

MathOS, human-review and calibration datasets require explicit future adapters: graph
reachability does not evaluate all three domains. This release does not silently map
reviewer time to independent observations or model probabilities to reachable nodes.
Cross-repository account integration and persistent result registries are not implemented.

Toward an empirical advantage claim, supply held-out independently adjudicated tasks,
justified independent experimental units, a preregistered practical margin, uncertainty
analysis appropriate to the design, and independently operated reproductions. ResearchOS
must keep those missing gates visible until the corresponding evidence actually exists.
