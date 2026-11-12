"""Read complete candidate bodies in bounded batches; keywords only prioritize, never label."""
import argparse
import json
from pathlib import Path
import re
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/rental_expansion_v2'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source')
    p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=25)
    p.add_argument('--priority',action='store_true')
    p.add_argument('--summary',action='store_true')
    p.add_argument('--novel',action='store_true',help='Hide exact body/text copies already in the draft, not a label decision')
    args=p.parse_args()
    rows=json.loads((BASE/'candidates.json').read_text('utf-8'))
    for extension in sorted(BASE.glob('candidates_extension_*.json')):
        rows.extend(json.loads(extension.read_text('utf-8')))
    if args.source:rows=[r for r in rows if r['document_id']==args.source or r['contract_id']==args.source]
    if args.novel:
        import csv
        from package_rental_dataset import exact_key
        from contractguard.text import normalize
        from rental_expansion_annotations_v2 import DECISIONS,HOLDS
        with (ROOT/'data/clauses_rental_v2.csv').open(encoding='utf-8-sig',newline='') as handle:
            existing=list(csv.DictReader(handle))
        bodies={exact_key(r['clause_body']) for r in existing}
        texts={normalize(r['text']) for r in existing}
        rows=[r for r in rows if r['clause_id'] not in DECISIONS and r['clause_id'] not in HOLDS
              and exact_key(r['clause_body']) not in bodies and normalize(r['text']) not in texts]
    if args.summary:
        print(json.dumps(Counter(r['document_id'] for r in rows),ensure_ascii=False,indent=2))
        return
    if args.priority:
        rows=[r for r in rows if re.search(r'không (?:hoàn|trả lại|chịu trách nhiệm)|mất (?:toàn bộ |tiền )?cọc|niêm phong|khóa (?:phòng|cửa)|bất (?:cứ|kỳ)|mọi (?:hư hỏng|thiệt hại|trách nhiệm)|tự động|im lặng|tự (?:ý |động )?(?:tăng|điều chỉnh)|toàn bộ.{0,40}sửa chữa|khấu trừ|đơn phương',r['clause_body'],re.I)]
        print('PRIORITY QUEUE ONLY, NOT TARGET LABELS')
    print('TOTAL',len(rows))
    for r in rows[args.start:args.start+args.count]:
        print('\n'+r['clause_id']+' | '+re.sub(r'\s+',' ',r['heading'])[:120]+'\n'+re.sub(r'\s+',' ',r['clause_body']))


if __name__=='__main__':main()
