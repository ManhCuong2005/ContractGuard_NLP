"""Append the newly reviewed Danang residential source without changing prior IDs."""
from pathlib import Path
import sys
import shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,write_json,write_rows,sha256
from build_rental_candidates import BASE,choose_source,assemble

def main():
    history=BASE/'extraction_history/v5_before_danang_append'
    history.mkdir(parents=True,exist_ok=True)
    for name in ['candidates.json','candidates.csv','candidate_sources.json','candidate_coverage.json']:
        if (history/name).exists():raise ValueError('Already appended')
        shutil.copyfile(BASE/name,history/name)
    specs=read_json(ROOT/'configs/rental_contracts_v1.json')
    spec=dict(source='danang_bilingual_docx',contract='danang_bilingual',
        family='danang_residential_bilingual',subtype='house',lines=[21,119],vietnamese_only=True)
    if any(s['contract']==spec['contract'] for s in specs):raise ValueError('Already configured')
    catalog={s['document_id']:s for s in read_json(BASE/'collection_manifest.json')}
    source,path=choose_source(spec,catalog)
    source=dict(source,pages_path=path.relative_to(ROOT).as_posix(),pages_sha256=sha256(path),
        data_kind='public_contract_template',group_id=spec['family'],domain='residential_rental')
    rows,structural=assemble(spec,source,read_json(path))
    combined=read_json(BASE/'candidates.json')+rows
    write_json(BASE/'candidates.json',combined)
    write_rows(BASE/'candidates.csv',combined,list(combined[0]))
    write_json(BASE/'candidate_sources.json',read_json(BASE/'candidate_sources.json')+[source])
    write_json(BASE/'candidate_coverage.json',read_json(BASE/'candidate_coverage.json')+[
        dict(contract_id=spec['contract'],source=source['document_id'],candidate_count=len(rows),structural_lines=structural,selection=spec)])
    write_json(ROOT/'configs/rental_contracts_v1.json',specs+[spec])
    print('Appended',len(rows),'unlabelled candidates, previous IDs preserved.')

if __name__=='__main__':main()
