"""Label-blind built-in BFS/DFS runner for bounded directed reachability tasks."""
from collections import deque
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import platform
from time import perf_counter_ns
import tracemalloc

from .evaluation import validate_dataset
from ._tect.core import digest, text


def reachable(graph, implementation):
    adjacency = {n:[] for n in graph['nodes']}
    for source,target in graph['edges']: adjacency[source].append(target)
    seen, pending = set(), deque([graph['start']])
    while pending:
        node = pending.popleft() if implementation=='bfs' else pending.pop()
        if node in seen: continue
        seen.add(node)
        pending.extend(n for n in adjacency[node] if n not in seen)
    return sorted(seen)


def run(dataset, implementation, operator_id, repeats=3):
    tasks=validate_dataset(dataset); text(operator_id)
    if implementation not in ('bfs','dfs'): raise ValueError('Built-in bfs or dfs required')
    if type(repeats) is not int or not 1 <= repeats <= 31: raise ValueError('Between 1 and 31 repeats required')
    if tracemalloc.is_tracing(): raise ValueError('Runner requires ownership of allocation tracing')
    timestamp=lambda: datetime.now(timezone.utc).isoformat()
    started=timestamp(); observations=[]
    for tid,task in tasks.items():
        graph=task['input']; expected=reachable(graph,implementation)
        elapsed,peaks=[],[]
        for _ in range(repeats):
            start=perf_counter_ns(); result=reachable(graph,implementation)
            elapsed.append(perf_counter_ns()-start)
            if result!=expected: raise ValueError('Nondeterministic built-in result')
            tracemalloc.start()
            try:
                reachable(graph,implementation)
                peaks.append(tracemalloc.get_traced_memory()[1])
            finally: tracemalloc.stop()
        observations.append({'task_id':tid,'status':'ok','predicted_nodes':expected,
                             'elapsed_ns':elapsed,'peak_python_bytes':peaks})
    return {'schema_version':1,'dataset_sha256':digest(dataset),'implementation':implementation,
            'revision':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'operator_id':operator_id,'environment':platform.python_version()+' '+platform.platform(),
            'started_at':started,'finished_at':timestamp(),'observations':observations}
