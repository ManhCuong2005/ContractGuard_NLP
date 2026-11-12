"""Print canonical risk clauses and source context; never infer labels."""
from pathlib import Path
import argparse
import collections
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import read_json, read_rows

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--start', type=int, default=0)
    p.add_argument('--count', type=int, default=40)
    p.add_argument('--document')
    p.add_argument('--label', choices=['normal','abnormal'])
    p.add_argument('--clause-id')
    p.add_argument('--context', action='store_true', help='Include complete source pages')
    args = p.parse_args()
    if args.start < 0 or args.count < 1:
        p.error('start must be nonnegative and count must be positive')
    rows = read_rows(ROOT/'data/clauses.csv')
    sources = {s['document_id']: s for s in read_json(ROOT/'data/sources.json')}
    print(json.dumps({'rows': len(rows), 'characters':sum(len(r['text']) for r in rows),
                      'labelled':sum(bool(r['label']) for r in rows),
                      'statuses':dict(collections.Counter(r['review_status'] for r in rows))}))
    selection = [(i,r) for i,r in enumerate(rows) if
                 (not args.document or r['document_id']==args.document) and
                 (not args.label or r['label']==args.label) and
                 (not args.clause_id or r['clause_id']==args.clause_id)]
    shown_pages = set()
    for i,r in selection[args.start:args.start+args.count]:
        print(json.dumps({k: r.get(k,'') for k in ['clause_id','text','label','annotation_reason',
                         'risk_category','risk_evidence','context_clause_ids','context_source_pages',
                         'annotation_status','review_status','page_start','page_end']}, ensure_ascii=False))
        if args.context:
            pages = read_json(ROOT/sources[r['document_id']]['pages_path'])
            numbers=set(range(int(r['page_start']), int(r['page_end'])+1))
            numbers.update(json.loads(r.get('context_source_pages') or '[]'))
            for number in sorted(numbers):
                key = (r['document_id'], number)
                if key not in shown_pages:
                    print(json.dumps({'source_document': key[0], 'page': number,
                                      'original_page_text': pages[number-1]}, ensure_ascii=False))
                    shown_pages.add(key)
