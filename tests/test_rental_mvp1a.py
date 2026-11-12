"""Technical tests only, never model quality or official dataset ground truth."""
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from rental_corpus import semantic_html
from build_rental_candidates import assemble
from package_rental_dataset import contextualize, RISK_CODES, PRESERVED
from contractguard.dataset import read_rows,read_json,sha256
from contractguard.provenance import verify_clause_spans
from contractguard.text import normalize


def test_technical_test_dom_inline_words_numbers_and_nested_lists():
    html='<article><p>technical_test '+'x '*360+'</p><p>thanh t<b>oá</b>n 3<span>0</span> ngày</p><ul><li>Câu dẫn:<ul><li>Nghĩa vụ một.</li><li>Nghĩa vụ hai.</li></ul></li></ul></article>'
    pages,_=semantic_html(html.encode('utf-8'))
    assert 'thanh toán 30 ngày' in pages[0].splitlines()
    assert pages[0].splitlines()[-3:]==['Câu dẫn:','Nghĩa vụ một.','Nghĩa vụ hai.']


def test_technical_test_pdf_cross_reference_and_copy_count_are_continuations():
    pages=['Điều 9. Sửa chữa\n9.6 Sau thời hạn bảo hành theo\nĐiều 9.7, việc sửa chữa thuộc trách nhiệm bên thuê.\n9.7 Bảo trì phần chung theo thỏa thuận.\nĐiều 19. Hiệu lực\n19.2 Có bốn bản, bên thuê giữ\n01 bản, bên cho thuê giữ ba bản.']
    source=dict(document_id='technical_test',format='pdf',source_url='https://example.test/technical_test.pdf',source_sha256='0'*64)
    spec=dict(contract='technical_test',family='technical_test',subtype='technical_test')
    rows,_=assemble(spec,source,pages)
    assert len(rows)==3
    assert 'Điều 9.7, việc sửa chữa' in rows[0]['clause_body']
    assert '01 bản, bên cho thuê' in rows[-1]['clause_body']
    assert all(not r['label'] for r in rows)
    for row in rows:verify_clause_spans(row,pages)


def test_technical_test_context_cannot_cross_contracts():
    row=dict(source_line_refs='[[1, 0]]',contract_id='technical_test_a')
    other=dict(source_line_refs='[[1, 1]]',contract_id='technical_test_b')
    with pytest.raises(ValueError,match='Cross-contract'):
        contextualize(row,['other'],{'other':other},['a\nb'])


def test_technical_test_pdf_role_intro_without_colon_and_black_circle():
    pages=['ĐIỀU 3 : QUYỀN VÀ NGHĨA VỤ\n3.1. Quyền và nghĩa vụ của Bên A\n● Giao phòng theo thỏa thuận.\n● Kiểm tra phòng theo lịch.\n3.2. Quyền và nghĩa vụ của Bên B\n● Sử dụng phòng để ở.']
    source=dict(document_id='technical_test',format='pdf',source_url='https://example.test/technical_test.pdf',source_sha256='0'*64)
    rows,_=assemble(dict(contract='technical_test',family='technical_test',subtype='technical_test'),source,pages)
    assert len(rows)==3
    assert '3.1. Quyền và nghĩa vụ của Bên A' in rows[1]['text']
    assert '3.2. Quyền và nghĩa vụ của Bên B' in rows[2]['text']
    assert 'của Bên A' not in rows[2]['text']
    assert all(not row['label'] for row in rows)


def test_scan_provenance_is_explicit_and_bound_to_images():
    sources=read_json(ROOT/'data/rental_mvp1a_v1/sources.json')
    scans=[s for s in sources if s.get('extractor')=='agent_visual_selected_transcription']
    assert scans
    for source in scans:
        path=ROOT/source['transcription_proof_path']
        assert sha256(path)==source['transcription_proof_sha256']
        proof=read_json(path)
        assert not proof['full_page_transcription'] and not proof['external_ai_api_used']
        assert proof['source_sha256']==source['source_sha256']
        assert proof['pages_sha256']==source['pages_sha256']
        assert len(proof['rendered_pages'])==source['page_count']
        for render in proof['rendered_pages']:
            assert sha256(ROOT/render['image_path'])==render['sha256']


def test_rental_review_integrity_and_no_human_approval_inferred():
    rows=read_rows(ROOT/'data/clauses_rental_v1.csv')
    sources={s['document_id']:s for s in read_json(ROOT/'data/rental_mvp1a_v1/sources.json')}
    pages={key:read_json(ROOT/s['pages_path']) for key,s in sources.items()}
    assert rows
    assert len({normalize(r['text']) for r in rows})==len(rows)
    for row in rows:
        assert row['label']==row['risk_label']
        assert row['clause_type']==row['category']
        assert row['annotation_reason']==row['label_reason']
        assert row['source_url']==row['source']
        assert row['annotation_status']=='draft' and row['review_status']=='pending'
        assert not row['reviewer'] and not row['verified_risk_label']
        assert row['annotation_reason'] and row['annotation_evidence']
        if row['label']=='abnormal':
            assert set(row['risk_category'].split('|'))<=RISK_CODES
            assert normalize(row['risk_evidence']) in normalize(row['text'])
        verify_clause_spans(row,pages[row['document_id']])
    for source in sources.values():
        assert sha256(ROOT/source['raw_path'])==source['source_sha256']
        assert sha256(ROOT/source['pages_path'])==source['pages_sha256']
    for name,digest in PRESERVED.items():assert sha256(ROOT/name)==digest
    approval=read_json(ROOT/'configs/rental_approval.json')
    assert approval['criteria_approved']
    # Draft remains historical; the actual later user acceptance authorizes a
    # separate frozen reviewed copy, never a silent mutation of these rows.
    if approval['dataset_approved']:
        record=read_json(ROOT/approval['dataset_confirmation_record'])
        assert record['confirmation_quote']=='Dataset thuê nhà Đạt'
        assert record['reviewed_draft_sha256']==sha256(ROOT/'data/clauses_rental_v1.csv')
        assert approval['source_use_confirmed']
    else:
        assert not approval['source_use_confirmed']


def test_unassigned_candidates_never_become_normal_and_legacy_is_separate():
    rows=read_rows(ROOT/'data/clauses_rental_v1.csv')
    ids={r['clause_id'] for r in rows}
    ledger=read_json(ROOT/'data/rental_mvp1a_v1/annotation_ledger.json')
    reserve=[r for r in ledger if r['action'] in {'reserve_unlabelled','hold'}]
    assert reserve and all(not r['label'] and r['clause_id'] not in ids for r in reserve)
    legacy=read_json(ROOT/'data/rental_mvp1a_v1/legacy_selection_audit.json')
    assert legacy['legacy_rows']==752 and legacy['primary_rental_reused']==0
    auxiliary=read_rows(ROOT/'data/rental_mvp1a_v1/legacy_auxiliary.csv')
    assert all(r['clause_id'] not in ids and r['dataset_role']=='auxiliary_only' for r in auxiliary)


def test_risk_coverage_does_not_silently_hide_missing_categories():
    audit=read_json(ROOT/'reports/rental_dataset_audit.json')
    covered=set(audit['risk_category_counts'])
    assert set(audit['missing_abnormal_categories'])==RISK_CODES-covered
    assert 'automatic_renewal' in audit['missing_abnormal_categories']
    assert not audit['official_training_run'] and not audit['human_dataset_approved']
