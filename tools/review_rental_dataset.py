"""Read-only offline review of all rental rows; never accepts labels or trains."""
import argparse
from collections import Counter
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label',choices=['normal','abnormal'])
    parser.add_argument('--risk')
    parser.add_argument('--clause-id')
    parser.add_argument('--source')
    parser.add_argument('--data',type=Path,default=ROOT/'data/clauses_rental_v1.csv')
    parser.add_argument('--origin',choices=['new','inherited'])
    parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--count',type=int,default=5)
    args=parser.parse_args()
    rows=read_rows(args.data)
    rows=[r for r in rows if (not args.label or r['label']==args.label)
        and (not args.risk or args.risk in r['risk_category'].split('|'))
        and (not args.source or args.source==r['document_id'])
        and (not args.origin or r.get('row_origin','').startswith('new' if args.origin=='new' else 'approved'))
        and (not args.clause_id or args.clause_id==r['clause_id'])]
    statuses=Counter(r['annotation_status']+'/'+r['review_status'] for r in rows)
    print(f'Matching {len(rows)}; statuses={dict(statuses)}. Read-only review; no approval is recorded.')
    for row in rows[args.start:args.start+args.count]:
        print(f'\n{row["clause_id"]} | {row["label"]} | confidence={row["label_confidence"]}')
        print(row['text'])
        print('\nReason:',row['annotation_reason'])
        print('Risk:',row['risk_category'] or 'none identified in this unit')
        print('Source:',row['source_url'])
        print('Pages:',row['page_start'],'-',row['page_end'])
        print('Context IDs:',row['context_clause_ids'])

if __name__=='__main__':main()
