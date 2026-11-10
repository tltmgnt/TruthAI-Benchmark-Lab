# TruthAI Benchmark Lab

Offline versioned directed-graph reachability benchmarks with label-separated runners,
matched scoring, timing/allocation samples and canonical ResearchOS evidence replay.
This first release is a bounded benchmark tool, not an independent laboratory or proof
of performance superiority. It does not evaluate arbitrary mathematical dependencies.

## Install and complete a comparison

Python 3.10 or later; standard-library runtime, no API account required.

```bash
python -m pip install .
mkdir -p runs
truthai-benchmark run examples/tasks.json --implementation bfs --operator local --output runs/bfs.json
truthai-benchmark run examples/tasks.json --implementation dfs --operator local --output runs/dfs.json
truthai-benchmark compare examples/tasks.json examples/labels.json runs/bfs.json runs/dfs.json --expires-at 2027-01-01T00:00:00Z --output runs/comparison
truthai-benchmark verify runs/comparison
python -m unittest discover -s tests -v
python tests/check_installed.py
```

Choose a real expiry after assessment time; the illustrative date is not renewed by
the tool. Comparison captures current UTC assessment time unless `--as-of` is supplied.
Replay uses that captured historical assessment, not present-day evidence validity.
Without installation use `python -m benchmark_lab` from the checkout.

Open `runs/comparison/review.html` for task scores, captured inputs and assurance
blockers. Output paths must be new; parents must exist. Exit 0 means a bounded run,
scoring computation or exact replay succeeded, including a correctly recorded failed
candidate. It does not mean better performance or ASSURED status. Invalid inputs,
missing observations, existing outputs and altered bundles exit 2.

## Dataset and reference separation

[tasks.json](examples/tasks.json) contains only versioned task IDs, declared independent
unit IDs, split and graph inputs: nodes, directed edges and a start node. Reachability
includes the start node. Loops/cycles are permitted; undeclared nodes and duplicate
edges are rejected. Limits are 100 tasks, 256 nodes/task and 4096 edges/task. Input
files and each bundle output file are limited to 8 MiB. JSON keys/fields are strict.

[labels.json](examples/labels.json) is a separate evaluator input with expected node
sets, provenance and the canonical dataset digest. `run` cannot load a labels argument.
It runs only the built-in BFS/DFS algorithms; it does not import arbitrary user code.
Changing a dataset requires rebinding labels and submissions to the new digest.
The shipped labels are manually specified synthetic cases, not expert-adjudicated data.

Label separation in these interfaces is not access control: a local operator can read
files or leak labels. Keep hidden datasets/labels out of public Git and runner environments.
Evaluation bundles intentionally contain reference labels for replay; treat them as
restricted artifacts for a hidden evaluation. CI uploads only the public synthetic set.

## Measurements and comparisons

| Measure | Behavior |
| --- | --- |
| Missing/spurious nodes | Exact set difference from supplied reference labels |
| Precision/recall | Undefined precision for empty prediction is null; failed runs have no predictions and retain missed reference nodes |
| Exact match | Requires successful status and the exact reference set |
| Runtime | Raw nanosecond samples and per-task median, measured separately from allocations |
| Memory | Python tracemalloc peak samples, not RSS or total process memory |
| Paired differences | Same dataset/task coverage; time deltas suppressed for failures or differently declared environments |
| Correctness-matched time | Reported only when both implementations exactly match reference labels |
| Declared units | Within-unit task summaries; unit declarations do not establish independence |

Built-in runs record Python/platform, operator declaration, implementation, runner-source
digest, timestamps and raw samples. A warmup result precedes timing. Each timed run
includes adjacency construction and output sorting, excludes JSON parsing, and is
separate from a corresponding allocation run. Repeats are local timing samples, not
independent replications. Separate CLI runs do not counterbalance execution order,
isolate CPUs or enforce hard resource budgets. Do not infer broad speed gains from
the small included graphs. The algorithms are established techniques, not new methods.

External adapters may produce the same strict submission schema as `run` returns.
They must retain every task, using explicit timeout/error rows with empty predictions
when unsuccessful. Imported timing, environment and revision claims are not authenticated.
Matching environment strings does not establish identical hardware or resources.

## ResearchOS and replay

Six unchanged canonical v0.1.0 modules are vendored privately, pinned by source commit
and release hashes in [researchos-lock.json](researchos-lock.json). Tests enforce
conformance. The real Controller receives a receipt for the scoped scoring computation,
not a claim that the candidate is superior or correct. It records actual state
transitions and a rejection ledger. Missing domain attacks and separate reproduction
block REPRODUCED; no fictional external evidence is inserted.

Bundles capture study inputs, comparison, scenario, ledger, controller report, escaped
HTML and runtime/content fingerprints. Exact replay recomputes scores and controller
operations and compares every byte. It replays supplied run measurements; it does not
rerun historical nanosecond timings or prove those imported timings were genuine.
Hashes establish consistency, not authorship, reference correctness or independence.
Canonical confidence/density weights are declared policy settings, not calibrated trust.

## Evaluation boundaries

[protocol.json](examples/protocol.json) is an unregistered study template. Fill and freeze
it before collecting evaluation outcomes. No statistical significance, confidence interval,
external validation, general intelligence, theorem discovery or operational authority is
claimed. See [evaluation protocol](docs/EVALUATION.md). Actual independently labeled
datasets, sealed external submissions, statistically justified experiments and external
replications remain future work. Existing Apache-2.0 license retained; the vendored
ResearchOs code is Apache-2.0.

**∞**

## Topology compatibility and curriculum

See the [repository-specific v2 curriculum](docs/portfolio/TOPOLOGY_CURRICULUM_V2.md) for topology choices, worked explanations, a graded laboratory and adoption boundaries. Run the offline answer key from this repository root:\n\n```sh\npython curriculum/lab.py --verify\n```\n\n[Expected answers](curriculum/expected.json) · [Recorded local validation](curriculum/VALIDATION.json). The guide states any existing dependency needed for the lab.
