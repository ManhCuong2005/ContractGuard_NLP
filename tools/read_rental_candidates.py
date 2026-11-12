"""Read complete source-based candidates for agent annotation; never suggests risk labels."""
import argparse
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contract',default='')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=30)
    p.add_argument('--priority',action='store_true')
    p.add_argument('--unassigned',action='store_true',help='Reading queue only; never infers a label')
    p.add_argument('--body-only',action='store_true')
    args=p.parse_args()
    rows=read_json(ROOT/'data/rental_mvp1a_v1/candidates.json')
    if args.unassigned:
        from rental_annotation_decisions import DECISIONS
        rows=[r for r in rows if r['clause_id'] not in DECISIONS]
    if args.contract:
        rows=[r for r in rows if r['contract_id'] in args.contract.split(',')]
    if args.priority:
        pattern=re.compile(r'mọi|toàn bộ|bất kỳ|bất cứ|không hoàn|không trả|không chịu|không có trách nhiệm|tự động|tự ý|điều chỉnh|kiểm tra|im lặng|mặc nhiên|được xem|100%|hao mòn|thiệt hại',re.I)
        rows=[r for r in rows if pattern.search(r['clause_body'])]
    print('MATCHING',len(rows))
    for i,r in enumerate(rows[args.start:args.start+args.count],args.start):
        print('\n',i,r['clause_id'],f'pages {r["page_start"]}-{r["page_end"]}',r['heading'])
        print(r['clause_body'] if args.body_only else r['text'])

if __name__=='__main__': main()
