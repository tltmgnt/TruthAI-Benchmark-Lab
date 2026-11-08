"""Versioned graph tasks, label-separated submissions and complete paired scoring."""
from statistics import mean, median
from ._tect.core import fields, text, digest, date


def unique_ids(items, maximum, allow_empty=False):
    if type(items) is not list or len(items) > maximum or not allow_empty and not items:
        raise ValueError('Bounded identifier list required')
    for value in items: text(value)
    if len(set(items)) != len(items): raise ValueError('Duplicate identifier')


def validate_dataset(dataset):
    fields(dataset, ('schema_version','dataset_id','version','split','tasks'))
    if type(dataset['schema_version']) is not int or dataset['schema_version'] != 1:
        raise ValueError('Unsupported dataset schema')
    text(dataset['dataset_id']); text(dataset['version'])
    if dataset['split'] not in ('development','validation','hidden','adversarial'):
        raise ValueError('Unknown dataset split')
    tasks = dataset['tasks']
    if type(tasks) is not list or not 1 <= len(tasks) <= 100:
        raise ValueError('Between 1 and 100 tasks required')
    seen = set()
    for task in tasks:
        fields(task, ('id','unit_id','input'))
        tid = text(task['id']); text(task['unit_id'])
        if tid in seen: raise ValueError('Duplicate task')
        seen.add(tid)
        graph = task['input']
        fields(graph, ('nodes','edges','start'))
        unique_ids(graph['nodes'],256)
        if graph['start'] not in graph['nodes']: raise ValueError('Unknown start node')
        if type(graph['edges']) is not list or len(graph['edges']) > 4096:
            raise ValueError('Bounded edges required')
        edges = set()
        for edge in graph['edges']:
            if type(edge) is not list or len(edge) != 2 or any(type(n) is not str or n not in graph['nodes'] for n in edge):
                raise ValueError('Edges must reference declared nodes')
            if tuple(edge) in edges: raise ValueError('Duplicate edge')
            edges.add(tuple(edge))
    return {task['id']: task for task in tasks}


def validate_labels(dataset, labels):
    tasks = validate_dataset(dataset)
    fields(labels, ('schema_version','dataset_sha256','provenance','expected'))
    if type(labels['schema_version']) is not int or labels['schema_version'] != 1 or labels['dataset_sha256'] != digest(dataset):
        raise ValueError('Labels do not bind this dataset')
    text(labels['provenance'])
    if type(labels['expected']) is not list or len(labels['expected']) != len(tasks):
        raise ValueError('Complete reference task coverage required')
    result = {}
    for row in labels['expected']:
        fields(row, ('task_id','reachable_nodes'))
        tid = row['task_id']
        if tid not in tasks or tid in result: raise ValueError('Unknown or duplicate reference task')
        unique_ids(row['reachable_nodes'],256)
        if any(n not in tasks[tid]['input']['nodes'] for n in row['reachable_nodes']):
            raise ValueError('Reference uses undeclared nodes')
        result[tid] = set(row['reachable_nodes'])
    return result


def validate_submission(dataset, submission):
    tasks = validate_dataset(dataset)
    fields(submission, ('schema_version','dataset_sha256','implementation','revision','operator_id',
                        'environment','started_at','finished_at','observations'))
    if type(submission['schema_version']) is not int or submission['schema_version'] != 1 or submission['dataset_sha256'] != digest(dataset):
        raise ValueError('Submission does not bind this dataset')
    for name in ('implementation','revision','operator_id','environment'): text(submission[name])
    if date(submission['finished_at']) < date(submission['started_at']):
        raise ValueError('Run finishes before it starts')
    if type(submission['observations']) is not list or len(submission['observations']) != len(tasks):
        raise ValueError('No missing task observations allowed')
    rows = {}
    for row in submission['observations']:
        fields(row, ('task_id','status','predicted_nodes','elapsed_ns','peak_python_bytes'))
        tid = row['task_id']
        if tid not in tasks or tid in rows or row['status'] not in ('ok','timeout','error'):
            raise ValueError('Invalid task observation')
        unique_ids(row['predicted_nodes'],256,True)
        if any(n not in tasks[tid]['input']['nodes'] for n in row['predicted_nodes']):
            raise ValueError('Prediction uses undeclared nodes')
        if row['status'] != 'ok' and row['predicted_nodes']:
            raise ValueError('Failed tasks cannot contain successful predictions')
        for key in ('elapsed_ns','peak_python_bytes'):
            samples = row[key]
            if type(samples) is not list or not 1 <= len(samples) <= 31 or any(type(v) is not int or not 0 <= v <= 10**18 for v in samples):
                raise ValueError('Bounded nonnegative integer measurement samples required')
        if len(row['elapsed_ns']) != len(row['peak_python_bytes']):
            raise ValueError('Timing/allocation sample counts must match')
        rows[tid] = row
    return rows


def score(dataset, labels, submission):
    expected, observed = validate_labels(dataset,labels), validate_submission(dataset,submission)
    tasks = {t['id']:t for t in dataset['tasks']}
    results = {}
    for tid in sorted(tasks):
        truth, row = expected[tid], observed[tid]
        prediction = set(row['predicted_nodes'])
        hits = len(truth & prediction)
        results[tid] = {'unit_id': tasks[tid]['unit_id'], 'status': row['status'],
            'missed_nodes': sorted(truth-prediction), 'spurious_nodes': sorted(prediction-truth),
            'recall': hits/len(truth) if truth else None,
            'precision': hits/len(prediction) if prediction else None,
            'exact_match': row['status']=='ok' and truth==prediction,
            'median_elapsed_ns': median(row['elapsed_ns']),
            'median_peak_python_bytes': median(row['peak_python_bytes'])}
    units = {}
    for tid,row in results.items(): units.setdefault(row['unit_id'],[]).append(row)
    grouped = {uid:{'exact_match_rate':mean(r['exact_match'] for r in rows),
                    'mean_missed_nodes':mean(len(r['missed_nodes']) for r in rows),
                    'mean_spurious_nodes':mean(len(r['spurious_nodes']) for r in rows),
                    'mean_task_median_elapsed_ns':mean(r['median_elapsed_ns'] for r in rows)}
               for uid,rows in sorted(units.items())}
    return {'tasks':results,'units':grouped,'summary':{
        'task_count':len(results),'declared_unit_count':len(units),
        'failed_tasks':sum(r['status']!='ok' for r in results.values()),
        'exact_match_rate':mean(r['exact_match'] for r in results.values()),
        'missed_nodes':sum(len(r['missed_nodes']) for r in results.values()),
        'spurious_nodes':sum(len(r['spurious_nodes']) for r in results.values())}}


def compare(dataset, labels, baseline, candidate):
    if (baseline['implementation'],baseline['revision']) == (candidate['implementation'],candidate['revision']):
        raise ValueError('Distinct implementation/revision identities required')
    first, second = score(dataset,labels,baseline), score(dataset,labels,candidate)
    paired = {}
    same_environment = baseline['environment'] == candidate['environment']
    for tid in first['tasks']:
        a,b = first['tasks'][tid],second['tasks'][tid]
        both_ok = a['status']=='ok' and b['status']=='ok'
        both_correct = a['exact_match'] and b['exact_match']
        paired[tid] = {'missed_nodes_reduction':len(a['missed_nodes'])-len(b['missed_nodes']),
                       'spurious_nodes_reduction':len(a['spurious_nodes'])-len(b['spurious_nodes']),
                       'elapsed_ns_saved':a['median_elapsed_ns']-b['median_elapsed_ns'] if both_ok and same_environment else None,
                       'correctness_matched_elapsed_ns_saved':a['median_elapsed_ns']-b['median_elapsed_ns'] if both_correct and same_environment else None}
    return {'schema_version':1,'dataset_sha256':digest(dataset),'labels_sha256':digest(labels),
            'baseline_sha256':digest(baseline),'candidate_sha256':digest(candidate),
            'baseline':first,'candidate':second,'paired_tasks':paired,
            'same_environment_declared':same_environment,
            'status':'descriptive_comparison_not_superiority_or_independence',
            'limits':['Labels, operator identities and imported timings are supplied declarations',
                      'Reachable-node coverage is not discovery of missing mathematical dependencies',
                      'Unit IDs do not establish statistical independence; no confidence interval or significance claim',
                      'Python allocation peaks are not process RSS; repeats are timing samples, not independent replications']}
