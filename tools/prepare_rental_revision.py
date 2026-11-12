"""Preserve extraction history, extend reviewed source boundaries, repair chat encoding."""
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'data/rental_mvp1a_v1'

def main():
    history=BASE/'extraction_history/v3_before_reference_repair'
    history.mkdir(parents=True,exist_ok=True)
    for name in ['candidates.json','candidates.csv','candidate_sources.json','candidate_coverage.json']:
        current=BASE/name
        if current.exists():
            target=history/name
            if target.exists():
                raise ValueError('Snapshot already exists; inspect before rebuilding')
            shutil.move(str(current),str(target))
    path=ROOT/'configs/rental_contracts_v1.json'
    shutil.copyfile(path,history/'rental_contracts_v1.json')
    specs=json.loads(path.read_text('utf-8'))
    specs=[s for s in specs if s['contract']!='acc_room']
    specs.extend([
        dict(source='bandon_room',contract='bandon_room',family='bandon_operator',subtype='room',lines=[20,93]),
        dict(source='roomi_registration_template',contract='roomi_registration',family='roomi_registration',subtype='room',lines=[26,103]),
        dict(source='iuoss_dorm_pdf',contract='iuoss_dorm',family='iuoss_phanliem',subtype='student_dorm',pages=[1,2]),
    ])
    path.write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Exact prior chat decisions only; no dataset approval and no new reviewer.
    backup=ROOT/'reports/approval_encoding_history'
    backup.mkdir(exist_ok=True)
    for relative in ['reports/rental_criteria_approval.json','configs/rental_approval.json']:
        p=ROOT/relative
        shutil.copyfile(p,backup/p.name)
        record=json.loads(p.read_text('utf-8'))
        if 'scope_confirmation_quote' in record:
            record['scope_confirmation_quote']='Thuê nhà, bảo vệ người thuê theo prompt gốc'
            record['confirmation_quote']='Tiêu chí thuê nhà Đạt'
        else:
            record['criteria_confirmation_quote']='Tiêu chí thuê nhà Đạt'
        record['encoding_correction']='Restored exact existing chat quotations from Unicode loss; earlier bytes preserved in reports/approval_encoding_history. Decisions and criteria hashes unchanged.'
        p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Extraction v3 and approval encoding history preserved; no approval decisions changed.')

if __name__=='__main__':
    main()
