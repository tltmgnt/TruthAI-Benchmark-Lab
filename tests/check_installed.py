"""Installed CLI smoke check; runner subprocesses import outside the checkout."""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    temporary=Path(tmp);output=Path(args.output).resolve() if args.output else temporary/'bundle'
    commands=[sys.executable,'-I','-m','benchmark_lab']
    def call(arguments,expected=0):
        result=subprocess.run(commands+arguments,cwd=tmp,capture_output=True,text=True)
        assert result.returncode==expected,(result.stdout,result.stderr)
        return result
    for name in ('bfs','dfs'):
        call(['run',str(root/'examples/tasks.json'),'--implementation',name,'--operator','synthetic-local',
              '--repeats','2','--output',str(temporary/(name+'.json'))])
    expiry=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
    comparison=['compare',str(root/'examples/tasks.json'),str(root/'examples/labels.json'),
                str(temporary/'bfs.json'),str(temporary/'dfs.json'),'--expires-at',expiry,'--output',str(output)]
    result=call(comparison)
    assert json.loads(result.stdout)['status']=='COMPUTED_UNASSURED'
    assert json.loads(call(['verify',str(output)]).stdout)['status']=='REPLAY_CONSISTENT_UNASSURED'
    call(comparison,2)
    altered=temporary/'altered';shutil.copytree(output,altered)
    (altered/'comparison.json').write_text('{}')
    call(['verify',str(altered)],2)
    call(['run',str(root/'examples/tasks.json'),'--implementation','bfs','--operator','synthetic-local',
          '--output',str(temporary/'bfs.json')],2)
print('Installed run, compare, replay, overwrite and tamper checks passed')
