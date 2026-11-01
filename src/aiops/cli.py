"""Local operations command line."""
import argparse, csv, json, os
from pathlib import Path
from aiops.export.jsonl import write_jsonl
from aiops.storage.sqlite import SQLiteStore

def main() -> None:
    parser=argparse.ArgumentParser(prog='aiops',description='AI Operations Platform utilities')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('validate-jsonl'); p.add_argument('path',type=Path)
    p=sub.add_parser('export-jsonl'); p.add_argument('input',type=Path); p.add_argument('output',type=Path)
    p=sub.add_parser('init-db'); p.add_argument('--db',type=Path,default=Path(os.getenv('AIOPS_DB_PATH','./data/aiops.db')))
    p=sub.add_parser('csv-to-jsonl'); p.add_argument('input',type=Path); p.add_argument('output',type=Path)
    p=sub.add_parser('run-status'); p.add_argument('run_id'); p.add_argument('--db',type=Path,default=Path(os.getenv('AIOPS_DB_PATH','./data/aiops.db')))
    a=parser.parse_args()
    if a.command=='validate-jsonl':
        count=0
        with a.path.open(encoding='utf-8') as f:
            for n,line in enumerate(f,1):
                if line.strip():
                    try: json.loads(line)
                    except json.JSONDecodeError as exc: raise SystemExit(f'Invalid JSON on line {n}: {exc}') from exc
                    count+=1
        print(f'Valid JSONL: {count} records')
    elif a.command=='export-jsonl':
        rows=json.loads(a.input.read_text(encoding='utf-8'))
        if not isinstance(rows,list) or not all(isinstance(x,dict) for x in rows): raise SystemExit('Input must be a JSON array of objects')
        print(write_jsonl(rows,a.output))
    elif a.command=='init-db':
        SQLiteStore(a.db); print(f'Initialized SQLite database: {a.db}')
    elif a.command=='csv-to-jsonl':
        with a.input.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
        print(write_jsonl(rows,a.output)); print(f'Converted {len(rows)} CSV rows')
    elif a.command=='run-status':
        record=SQLiteStore(a.db).get_run(a.run_id)
        if record is None: raise SystemExit(f'Run not found: {a.run_id}')
        print(json.dumps(record,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
