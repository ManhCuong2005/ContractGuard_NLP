"""Repair only the newly appended contracts; preserve all previously reviewed rows."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,write_json,write_rows,sha256
from build_rental_candidates import BASE,assemble

def main():
    history=BASE/'extraction_history/worker_role_intro_fix'
    history.mkdir(parents=True,exist_ok=True)
    for name in ['candidates.json','candidates.csv','candidate_coverage.json']:
        if (history/name).exists():raise ValueError('Already repaired')
        shutil.copyfile(BASE/name,history/name)
    specs=read_json(ROOT/'configs/rental_contracts_extension_v2.json')
    keys={s['contract'] for s in specs}
    old=read_json(BASE/'candidates.json')
    sources={s['document_id']:s for s in read_json(BASE/'candidate_sources.json')}
    repaired=[]
    coverage=[r for r in read_json(BASE/'candidate_coverage.json') if r['contract_id'] not in keys]
    for spec in specs:
        source=sources[spec['source']]
        new,structural=assemble(spec,source,read_json(ROOT/source['pages_path']))
        repaired.extend(new)
        coverage.append(dict(contract_id=spec['contract'],source=spec['source'],candidate_count=len(new),structural_lines=structural,selection=spec))
    current=[r for r in old if r['contract_id'] not in keys]+repaired
    assert [r for r in current if r['contract_id'] not in keys]==[r for r in old if r['contract_id'] not in keys]
    write_json(BASE/'candidates.json',current)
    write_rows(BASE/'candidates.csv',current,list(current[0]))
    write_json(BASE/'candidate_coverage.json',coverage)
    print('All earlier candidates unchanged; repaired role prefixes on new sources only.')
    print(sha256(BASE/'candidates.json'))

if __name__=='__main__':main()
