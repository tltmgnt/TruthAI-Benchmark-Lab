import copy
import hashlib
import json
from pathlib import Path
import random
import tempfile
import unittest

from benchmark_lab.evaluation import compare, score, validate_dataset
from benchmark_lab.runner import run
from benchmark_lab.researchos import assess
from benchmark_lab.bundle import write, verify, contents
from benchmark_lab._tect.core import digest, replay
from benchmark_lab._tect.io import load

ROOT=Path(__file__).resolve().parents[1]


def inputs():
    dataset=json.loads((ROOT/'examples/tasks.json').read_text())
    labels=json.loads((ROOT/'examples/labels.json').read_text())
    return dataset,labels


def study():
    dataset,labels=inputs()
    return {'dataset':dataset,'labels':labels,'baseline':run(dataset,'bfs','synthetic-local',1),
            'candidate':run(dataset,'dfs','synthetic-local',1),
            'as_of':'2099-01-01T00:00:00Z','expires_at':'2099-02-01T00:00:00Z'}


class LabTests(unittest.TestCase):
    def test_hand_labeled_graphs_and_matched_scoring(self):
        data=study();report=compare(data['dataset'],data['labels'],data['baseline'],data['candidate'])
        self.assertEqual(report['baseline']['summary']['exact_match_rate'],1)
        self.assertEqual(report['candidate']['summary']['exact_match_rate'],1)
        self.assertEqual(report['baseline']['summary']['task_count'],4)
        self.assertTrue(report['same_environment_declared'])

    def test_missing_and_spurious_predictions(self):
        data=study();row=data['candidate']['observations'][0]
        row['predicted_nodes']=['A']
        result=compare(data['dataset'],data['labels'],data['baseline'],data['candidate'])
        self.assertEqual(result['candidate']['tasks']['chain']['missed_nodes'],['B','C'])
        self.assertIsNone(result['paired_tasks']['chain']['correctness_matched_elapsed_ns_saved'])
        row=data['candidate']['observations'][-1];row['predicted_nodes']=['A','B']
        report=score(data['dataset'],data['labels'],data['candidate'])
        self.assertEqual(report['tasks']['isolated']['spurious_nodes'],['B'])

    def test_timeout_not_dropped_or_treated_as_fast_success(self):
        data=study();row=data['candidate']['observations'][0]
        row.update(status='timeout',predicted_nodes=[],elapsed_ns=[0],peak_python_bytes=[0])
        report=compare(data['dataset'],data['labels'],data['baseline'],data['candidate'])
        self.assertEqual(report['candidate']['summary']['failed_tasks'],1)
        self.assertEqual(report['candidate']['tasks']['chain']['recall'],0)
        self.assertIsNone(report['paired_tasks']['chain']['elapsed_ns_saved'])

    def test_mismatched_environment_suppresses_time_delta(self):
        data=study();data['candidate']['environment']='different-host-declaration'
        report=compare(data['dataset'],data['labels'],data['baseline'],data['candidate'])
        self.assertFalse(report['same_environment_declared'])
        self.assertTrue(all(r['elapsed_ns_saved'] is None for r in report['paired_tasks'].values()))

    def test_missing_duplicate_or_unbound_observations_rejected(self):
        for change in ('missing','duplicate','digest','nodes','negative','bool','same'):
            data=study();candidate=data['candidate']
            if change=='missing': candidate['observations'].pop()
            if change=='duplicate': candidate['observations'][1]=copy.deepcopy(candidate['observations'][0])
            if change=='digest': candidate['dataset_sha256']='0'*64
            if change=='nodes': candidate['observations'][0]['predicted_nodes']=['unknown']
            if change=='negative': candidate['observations'][0]['elapsed_ns']=[-1]
            if change=='bool': candidate['observations'][0]['elapsed_ns']=[True]
            if change=='same': candidate['implementation']=data['baseline']['implementation']
            with self.subTest(change=change),self.assertRaises(ValueError):
                compare(data['dataset'],data['labels'],data['baseline'],candidate)

    def test_reference_coverage_and_graph_validation(self):
        for change in ('labels','label_hash','edge','duplicate_node','unknown'):
            data=study()
            if change=='labels': data['labels']['expected'].pop()
            if change=='label_hash': data['labels']['dataset_sha256']='0'*64
            if change=='edge': data['dataset']['tasks'][0]['input']['edges'].append(['A','unknown'])
            if change=='duplicate_node': data['dataset']['tasks'][0]['input']['nodes'].append('A')
            if change=='unknown': data['dataset']['tasks'][0]['input']['expected']=['leak']
            with self.subTest(change=change),self.assertRaises(ValueError):
                compare(data['dataset'],data['labels'],data['baseline'],data['candidate'])

    def test_runner_against_separate_transitive_closure(self):
        rng=random.Random(173)
        for trial in range(80):
            count=rng.randint(1,12);nodes=[str(i) for i in range(count)]
            edges=[[a,b] for a in nodes for b in nodes if rng.random()<.15]
            closure={(a,b) for a,b in edges}|{(a,a) for a in nodes}
            for k in nodes:
                closure |= {(a,b) for a in nodes for b in nodes if (a,k) in closure and (k,b) in closure}
            dataset={'schema_version':1,'dataset_id':'generated','version':'1','split':'development',
                     'tasks':[{'id':'g','unit_id':'g','input':{'nodes':nodes,'edges':edges,'start':'0'}}]}
            expected=sorted(b for a,b in closure if a=='0')
            for implementation in ('bfs','dfs'):
                with self.subTest(trial=trial,implementation=implementation):
                    self.assertEqual(run(dataset,implementation,'local',1)['observations'][0]['predicted_nodes'],expected)

    def test_unit_aggregation(self):
        data=study()
        for task in data['dataset']['tasks']: task['unit_id']='same-correlated-unit'
        value=digest(data['dataset'])
        data['labels']['dataset_sha256']=value
        for name in ('baseline','candidate'): data[name]['dataset_sha256']=value
        report=score(data['dataset'],data['labels'],data['candidate'])
        self.assertEqual(report['summary']['declared_unit_count'],1)

    def test_researchos_missing_reproduction_and_rejection_probes(self):
        data=study();report=compare(data['dataset'],data['labels'],data['baseline'],data['candidate'])
        scenario,ledger,result=assess(data,report)
        self.assertEqual(ledger[-1]['outcome'],'UNCERTAIN')
        self.assertIn('SEPARATE_REPRODUCTION_MISSING',ledger[-1]['reasons'])
        self.assertFalse(result['execution_authorized'])
        for change in ('hash','actor','expiry'):
            bad=copy.deepcopy(scenario);operation=bad['operations'][2]
            if change=='hash': operation['data']['sha256']='0'*64
            if change=='actor': operation['actor']='author'
            if change=='expiry': operation['data']['expires_at']=data['as_of']
            self.assertEqual(replay(bad).ledger[2]['outcome'],'FAIL')

    def test_bundle_recompute_tamper_and_escaped_html(self):
        data=study();data['labels']['provenance']='<script>fictional</script>'
        self.assertNotIn('<script>',contents(data)['review.html'])
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run';write(data,output);verify(output)
            with self.assertRaises(FileExistsError): write(data,output)
            (output/'comparison.json').write_text('{}')
            with self.assertRaises(ValueError): verify(output)
            invalid=Path(tmp)/'bad.json';invalid.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): load(invalid)

    def test_time_and_repeat_boundaries(self):
        data=study()
        with self.assertRaises(ValueError): run(data['dataset'],'bfs','local',0)
        data['as_of']='2020-01-01T00:00:00Z'
        with self.assertRaises(ValueError):
            assess(data,compare(data['dataset'],data['labels'],data['baseline'],data['candidate']))

    def test_core_hashes(self):
        lock=json.loads((ROOT/'researchos-lock.json').read_text())
        for name,expected in lock['release']['modules'].items():
            self.assertEqual(hashlib.sha256((ROOT/'benchmark_lab/_tect'/name).read_bytes()).hexdigest(),expected)


if __name__=='__main__': unittest.main()
