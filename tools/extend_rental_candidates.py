"""Append additional source-scoped contracts, preserving the previous review version."""
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,write_json,write_rows,sha256
from build_rental_candidates import BASE,choose_source,assemble

def main():
    history=BASE/'dataset_history/before_worker_extension_466'
    if history.exists():raise ValueError('Extension snapshot exists; inspect before running again')
    for relative in ['data/clauses_rental_v1.csv','reports/rental_dataset_audit.json',
        'reports/MVP1A_REVIEW.md','data/rental_mvp1a_v1/sources.json',
        'data/rental_mvp1a_v1/candidates.json','data/rental_mvp1a_v1/candidate_sources.json',
        'data/rental_mvp1a_v1/candidate_coverage.json','data/rental_mvp1a_v1/annotation_decisions.json',
        'data/rental_mvp1a_v1/review_snapshot.json','configs/rental_contracts_v1.json',
        'tools/rental_annotation_decisions.py']:
        target=history/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
    catalog={s['document_id']:s for s in read_json(BASE/'collection_manifest.json')}
    specs=read_json(ROOT/'configs/rental_contracts_v1.json')
    rows=read_json(BASE/'candidates.json')
    sources={s['document_id']:s for s in read_json(BASE/'candidate_sources.json')}
    coverage=read_json(BASE/'candidate_coverage.json')
    for spec in read_json(ROOT/'configs/rental_contracts_extension_v2.json'):
        if any(s['contract']==spec['contract'] for s in specs):raise ValueError('Contract already exists')
        source,path=choose_source(spec,catalog)
        source=dict(source,pages_path=path.relative_to(ROOT).as_posix(),pages_sha256=sha256(path),
            data_kind='public_contract_template',group_id=spec['family'],domain='residential_rental')
        if path.name.startswith('pages_visual_'):
            proof=path.parent/'visual_transcription_v1.json'
            metadata=read_json(proof)
            if metadata['source_sha256']!=source['source_sha256'] or metadata['pages_sha256']!=sha256(path):
                raise ValueError('Scan transcription mismatch')
            source.update(extractor='agent_visual_selected_transcription',
                transcription_proof_path=proof.relative_to(ROOT).as_posix(),
                transcription_proof_sha256=sha256(proof),full_page_transcription=False)
        new,structural=assemble(spec,source,read_json(path))
        rows.extend(new)
        sources[source['document_id']]=source
        specs.append(spec)
        coverage.append(dict(contract_id=spec['contract'],source=source['document_id'],
            candidate_count=len(new),structural_lines=structural,selection=spec))
        print(spec['contract'],len(new))
    write_json(BASE/'candidates.json',rows)
    write_rows(BASE/'candidates.csv',rows,list(rows[0]))
    write_json(BASE/'candidate_sources.json',list(sources.values()))
    write_json(BASE/'candidate_coverage.json',coverage)
    write_json(ROOT/'configs/rental_contracts_v1.json',specs)
    print('Candidate snapshot SHA256:',sha256(BASE/'candidates.json'))

if __name__=='__main__':main()
