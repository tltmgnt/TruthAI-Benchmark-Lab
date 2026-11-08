"""Run label-blind graph tasks, score captured submissions, and replay results."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
from ._tect.core import canonical
from ._tect.io import load
from .runner import run
from .bundle import write, verify


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    runner=commands.add_parser('run')
    runner.add_argument('dataset');runner.add_argument('--implementation',choices=['bfs','dfs'],required=True)
    runner.add_argument('--operator',required=True);runner.add_argument('--repeats',type=int,default=3)
    runner.add_argument('--output',required=True)
    compare=commands.add_parser('compare')
    for name in ('dataset','labels','baseline','candidate'): compare.add_argument(name)
    compare.add_argument('--as-of');compare.add_argument('--expires-at',required=True)
    compare.add_argument('--output',required=True)
    check=commands.add_parser('verify');check.add_argument('bundle')
    args=parser.parse_args(argv)
    try:
        if args.command=='run':
            result=run(load(args.dataset),args.implementation,args.operator,args.repeats)
            with Path(args.output).open('x',encoding='utf-8') as stream: stream.write(canonical(result))
            print(json.dumps({'status':'RUN_RECORDED_NOT_INDEPENDENT','dataset_sha256':result['dataset_sha256']}))
        else:
            if args.command=='compare':
                data={name:load(getattr(args,name)) for name in ('dataset','labels','baseline','candidate')}
                data.update(as_of=args.as_of or datetime.now(timezone.utc).isoformat(),expires_at=args.expires_at)
                report=write(data,args.output)
            else: report=verify(args.bundle)
            print(json.dumps({'status':'COMPUTED_UNASSURED' if args.command=='compare' else 'REPLAY_CONSISTENT_UNASSURED',
                              'state':report['state']['claims']['benchmark-scoring']['state'],
                              'assurance_blockers':report['assurance_blockers'],
                              'execution_authorized':report['execution_authorized']},indent=2))
        return 0
    except (ValueError,TypeError,KeyError,OSError,RecursionError) as exc: parser.exit(2,str(exc)+'\n')


if __name__=='__main__': raise SystemExit(main())
