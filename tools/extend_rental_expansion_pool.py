"""Append a separate sealed extension; never renumber or mutate annotated candidates."""
from pathlib import Path
import argparse
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,sha256,write_json
from rental_clause_assembly_v2 import assemble

BASE=ROOT/'data/rental_expansion_v2'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--number',default='01',choices=['01','02','03','04'])
    parser.add_argument('--sources',nargs='+')
    args=parser.parse_args()
    target=BASE/f'candidates_extension_{args.number}.json'
    if target.exists():raise ValueError('Extension exists; preserve it and use a new version.')
    selected={'v2_rentapartment_lease','v2_caselaw_apartment','v2_vinaaccounting_room','v2_replus_room'}
    if args.sources:selected=set(args.sources)
    sources=[s for s in read_json(BASE/'collection_manifest.json') if s['document_id'] in selected]
    rows=[]
    for source in sources:
        spec=dict(contract=source['document_id'],family='v2_'+source['document_id'],subtype='pending_scope_review')
        # Only retain Vietnamese lines from the bilingual operator contract.
        if source['document_id']=='v2_rentapartment_lease':spec['vietnamese_only']=True
        new,_=assemble(spec,source,read_json(ROOT/source['pages_path']))
        rows.extend(new)
        print(source['document_id'],len(new))
    write_json(target,rows)
    write_json(BASE/f'sources_extension_{args.number}.json',sources)
    write_json(BASE/f'extension_{args.number}_snapshot.json',dict(candidate_sha256=sha256(target),count=len(rows),labels_assigned=0))


if __name__=='__main__':main()
