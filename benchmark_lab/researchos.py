"""Canonical ResearchOS adapter for scoped scoring computation, not benchmark victory."""
import base64
import hashlib
from ._tect.core import canonical, policy_default, replay, fields, date


def assess(data, report):
    fields(data, ('as_of','expires_at','dataset','labels','baseline','candidate'))
    if date(data['expires_at']) <= date(data['as_of']): raise ValueError('Expiry must follow assessment time')
    if any(date(s['finished_at']) > date(data['as_of']) for s in (data['baseline'],data['candidate'])):
        raise ValueError('Assessment precedes submitted runs')
    content=canonical({'report_sha256':hashlib.sha256(canonical(report).encode()).hexdigest(),
                       'dataset_sha256':report['dataset_sha256'],
                       'scope':'Local scoring of supplied observations; no external replication or performance superiority'}).encode()
    cid='benchmark-scoring'
    operations=[
        {'op':'register','actor':'author','data':{'id':cid,
         'statement':'Compute matched graph benchmark scores from captured labels and submissions',
         'provenance':['local:input.json','local:benchmark_lab.evaluation'],
         'confidence':.5,'assurance_scope':'Offline declared-reference scoring only'}},
        {'op':'transition','actor':'validator','data':{'claim':cid,'target':'UNVERIFIED'}},
        {'op':'evidence','actor':'validator','data':{
         'id':'scoring-receipt','claim':cid,'claim_version':1,'kind':'validation','result':'PASS',
         'source':'local:captured-study','method':'domain-adapter-v1','run_id':'local-evaluation',
         'group':'same-local-process','weight':1,'quality':1,'reliability':1,'independence':.5,
         'observed_at':data['as_of'],'expires_at':data['expires_at'],
         'content_base64':base64.b64encode(content).decode(),'sha256':hashlib.sha256(content).hexdigest()}}]
    for target in ('SUPPORTED','ADVERSARIAL_TEST','REPRODUCED'):
        operations.append({'op':'transition','actor':'validator','data':{'claim':cid,'target':target}})
    scenario={'schema_version':1,'as_of':data['as_of'],'policy':policy_default(),'operations':operations}
    controller=replay(scenario)
    if any(e['outcome']!='PASS' for e in controller.ledger[:-1]) or controller.ledger[-1]['outcome']!='UNCERTAIN':
        raise ValueError('Unexpected ResearchOS scoring transition')
    return scenario,controller.ledger,controller.report()
