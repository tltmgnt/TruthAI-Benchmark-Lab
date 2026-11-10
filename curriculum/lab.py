"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")

def sample(path):
    return json.loads((ROOT / path).read_text())



def run():
    from benchmark_lab.evaluation import compare
    from benchmark_lab.runner import run as run_graph
    data, labels = sample("examples/tasks.json"), sample("examples/labels.json")
    baseline = run_graph(data,"bfs","synthetic-local",1)
    candidate = run_graph(data,"dfs","synthetic-local",1)
    r = compare(data,labels,baseline,candidate)
    check("BFS exact-match reference", r["baseline"]["summary"]["exact_match_rate"], 1.0)
    check("DFS exact-match reference", r["candidate"]["summary"]["exact_match_rate"], 1.0)
    check("four matched tasks", r["baseline"]["summary"]["task_count"], 4)
    bad = copy.deepcopy(candidate)
    bad["observations"][0].update(status="timeout",predicted_nodes=[],elapsed_ns=[0],peak_python_bytes=[0])
    q = compare(data,labels,baseline,bad)
    check("timeout retained as failure", q["candidate"]["summary"]["failed_tasks"], 1)
    check("timeout is not an apparent speed win", q["paired_tasks"]["chain"]["elapsed_ns_saved"], None)
    bad = copy.deepcopy(candidate); bad["environment"] = "different-declared-host"
    q = compare(data,labels,baseline,bad)
    check("mismatched environment suppresses timing comparison", all(x["elapsed_ns_saved"] is None for x in q["paired_tasks"].values()), True)

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
