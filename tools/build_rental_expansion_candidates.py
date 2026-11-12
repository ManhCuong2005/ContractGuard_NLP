"""Build a new unlabelled pool, preserving every v1 source/candidate byte."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,sha256,write_json
from rental_clause_assembly_v2 import assemble

BASE=ROOT/'data/rental_expansion_v2'


def main():
    output=BASE/'candidates.json'
    if output.exists():
        old=BASE/'extraction_history/initial_pool/candidates.json'
        if not old.exists() or sha256(old)!=sha256(output):
            raise ValueError('Candidate pool already sealed. Create a new version for extraction changes.')
    old_rows=read_json(ROOT/'data/rental_mvp1a_v1/candidates.json')
    sources={s['document_id']:s for s in read_json(ROOT/'data/rental_mvp1a_v1/candidate_sources.json')}
    old_catalog=read_json(ROOT/'data/rental_mvp1a_v1/collection_manifest.json')
    new_catalog=read_json(BASE/'collection_manifest.json')
    selected=[]
    new_rows=[]
    exclusions={'v2_attachment_94e6eb8c651f':'Page 1: Mục đích sử dụng: Thuê nhà để kinh doanh. Not residential rental.'}
    # These are extraction candidates only, not approval of scope or annotations.
    new_ids={s['document_id'] for s in new_catalog if s['document_id'].startswith('v2_attachment_')}
    new_ids|={'v2_nhatrang_tdtu_edu_vn_04ae8be4','v2_alodev_vn_b95f3a56',
        'v2_enha_vn_3ec5e91c','v2_batdongsanonline_vn_1b8b6ee6','v2_hopdongmau_com_1af118ef',
        'v2_i_law_vn_91fabc89','v2_static1_cafeland_vn_9e38bcb2','v2_timespro_com_vn_f051340a'}
    old_ids={'danang_house2_docx','danang_house_docx','danang_house_simple_docx','danang_room_docx',
        'dkrs_full_docx','dkrs_notary_docx','dkrs_simple_docx','bdsdaily_house_pdf'}
    for source in old_catalog+new_catalog:
        sid=source['document_id']
        if sid not in new_ids|old_ids or sid in sources:continue
        if sid in exclusions:continue
        if sid=='bdsdaily_house_pdf':
            repaired=BASE/'source_repairs/bdsdaily_house_pdf/pages_geometry_v2.json'
            source=dict(source,pages_path=repaired.relative_to(ROOT).as_posix(),pages_sha256=sha256(repaired),extractor='pdfplumber_geometry_v2')
        pages=read_json(ROOT/source['pages_path'])
        if not any(p.strip() for p in pages):continue
        spec={'contract':sid,'family':'v2_candidate_family_'+sid,'subtype':'pending_residential_scope_review'}
        print('Assembling',sid,flush=True)
        rows,structural=assemble(spec,source,pages)
        new_rows.extend(rows)
        sources[sid]=source
        selected.append(dict(document_id=sid,candidate_count=len(rows),selection=spec,
                             structural_lines=structural))
    rows=old_rows+new_rows
    assert len({r['clause_id'] for r in rows})==len(rows)
    write_json(output,rows)
    write_json(BASE/'candidate_sources.json',list(sources.values()))
    write_json(BASE/'candidate_coverage.json',selected)
    write_json(BASE/'explicit_scope_exclusions.json',exclusions)
    write_json(BASE/'candidate_snapshot.json',{
        'candidate_sha256':sha256(output),'count':len(rows),'reused_v1_candidates':len(old_rows),
        'new_candidates':len(new_rows),'all_new_labels_blank':all(not r['label'] for r in new_rows),
        'v1_candidate_sha256':sha256(ROOT/'data/rental_mvp1a_v1/candidates.json'),
        'annotation_is_not_keyword_or_model_inference':True})
    print('Unlabelled pool:',len(rows),'including',len(new_rows),'new candidates')
    for item in selected:print(item['document_id'],item['candidate_count'])


if __name__=='__main__':main()
