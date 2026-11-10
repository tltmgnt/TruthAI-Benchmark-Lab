# Topology compatibility and curriculum v2 — TruthAI-Benchmark-Lab

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | specialized evaluation |
| Minimum useful mathematics | Directed graph reachability and matched benchmark design |
| Relationships to preserve | Versioned tasks, split boundaries and paired submissions |
| Concrete operation / capstone | Construct a synthetic directed graph with one unreachable target and compare two label-separated submissions |
| Necessity and scope boundary | Benchmark agreement is not independent laboratory certification; retain unknown and missing outcomes |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with directed graph reachability and matched benchmark design and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify versioned tasks, split boundaries and paired submissions. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain directed graph reachability and matched benchmark design. | Construct a synthetic directed graph with one unreachable target and compare two label-separated submissions. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `47d916d5e2e95ca82c68c7cef9030779f95c1815` in [benchmark_lab/evaluation.py](../../benchmark_lab/evaluation.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [6](../../benchmark_lab/evaluation.py#L6) | `def unique_ids(items, maximum, allow_empty=False):` | State the input/output contract and trace one normal and one failing case. |
| [8](../../benchmark_lab/evaluation.py#L8) | `raise ValueError('Bounded identifier list required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [10](../../benchmark_lab/evaluation.py#L10) | `if len(set(items)) != len(items): raise ValueError('Duplicate identifier')` | Construct the triggering input and explain why rejection preserves the contract. |
| [13](../../benchmark_lab/evaluation.py#L13) | `def validate_dataset(dataset):` | State the input/output contract and trace one normal and one failing case. |
| [14](../../benchmark_lab/evaluation.py#L14) | `fields(dataset, ('schema_version','dataset_id','version','split','tasks'))` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [15](../../benchmark_lab/evaluation.py#L15) | `if type(dataset['schema_version']) is not int or dataset['schema_version'] != 1:` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [16](../../benchmark_lab/evaluation.py#L16) | `raise ValueError('Unsupported dataset schema')` | Construct the triggering input and explain why rejection preserves the contract. |
| [19](../../benchmark_lab/evaluation.py#L19) | `raise ValueError('Unknown dataset split')` | Construct the triggering input and explain why rejection preserves the contract. |
| [22](../../benchmark_lab/evaluation.py#L22) | `raise ValueError('Between 1 and 100 tasks required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [27](../../benchmark_lab/evaluation.py#L27) | `if tid in seen: raise ValueError('Duplicate task')` | Construct the triggering input and explain why rejection preserves the contract. |
| [32](../../benchmark_lab/evaluation.py#L32) | `if graph['start'] not in graph['nodes']: raise ValueError('Unknown start node')` | Construct the triggering input and explain why rejection preserves the contract. |
| [34](../../benchmark_lab/evaluation.py#L34) | `raise ValueError('Bounded edges required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [38](../../benchmark_lab/evaluation.py#L38) | `raise ValueError('Edges must reference declared nodes')` | Construct the triggering input and explain why rejection preserves the contract. |
| [39](../../benchmark_lab/evaluation.py#L39) | `if tuple(edge) in edges: raise ValueError('Duplicate edge')` | Construct the triggering input and explain why rejection preserves the contract. |
| [41](../../benchmark_lab/evaluation.py#L41) | `return {task['id']: task for task in tasks}` | Predict the returned value and distinguish a computed result from authorization. |
| [44](../../benchmark_lab/evaluation.py#L44) | `def validate_labels(dataset, labels):` | State the input/output contract and trace one normal and one failing case. |
| [46](../../benchmark_lab/evaluation.py#L46) | `fields(labels, ('schema_version','dataset_sha256','provenance','expected'))` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [47](../../benchmark_lab/evaluation.py#L47) | `if type(labels['schema_version']) is not int or labels['schema_version'] != 1 or labels['dataset_sha256'] != digest(dataset):` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [48](../../benchmark_lab/evaluation.py#L48) | `raise ValueError('Labels do not bind this dataset')` | Construct the triggering input and explain why rejection preserves the contract. |
| [51](../../benchmark_lab/evaluation.py#L51) | `raise ValueError('Complete reference task coverage required')` | Construct the triggering input and explain why rejection preserves the contract. |
| [56](../../benchmark_lab/evaluation.py#L56) | `if tid not in tasks or tid in result: raise ValueError('Unknown or duplicate reference task')` | Construct the triggering input and explain why rejection preserves the contract. |
| [59](../../benchmark_lab/evaluation.py#L59) | `raise ValueError('Reference uses undeclared nodes')` | Construct the triggering input and explain why rejection preserves the contract. |
| [61](../../benchmark_lab/evaluation.py#L61) | `return result` | Predict the returned value and distinguish a computed result from authorization. |
| [64](../../benchmark_lab/evaluation.py#L64) | `def validate_submission(dataset, submission):` | State the input/output contract and trace one normal and one failing case. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_lab.py](../../tests/test_lab.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. Benchmark agreement is not independent laboratory certification; retain unknown and missing outcomes.
