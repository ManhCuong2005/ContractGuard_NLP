"""Source-bound annotation, dependent-list context and no invented risk labels."""
from pathlib import Path
import importlib.util
import json

import pytest

from contractguard.dataset import FIELDS,read_json,read_rows,sha256,write_json,write_rows
from contractguard.provenance import apply_verified_text_repairs,verify_clause_spans

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('apply_annotations',ROOT/'tools/apply_risk_annotations.py')
annotation=importlib.util.module_from_spec(spec)
spec.loader.exec_module(annotation)


def test_manual_decision_coverage_is_explicit():
    prepared=read_json(ROOT/'configs/annotation_preparation.json')
    decisions=annotation.load_notes(ROOT/'configs/risk_annotation_notes.tsv')
    assert set(decisions)=={r['index'] for r in prepared['rows']}
    assert prepared['rubric_sha256']==sha256(ROOT/'docs/ANNOTATION_GUIDELINES.md')
    assert set(r['decision'] for r in decisions.values())=={'normal','abnormal','hold','exclude'}


def test_holds_and_duplicate_lineage_are_not_training_ground_truth():
    ledger=read_json(ROOT/'reports/risk_annotation_ledger.json')
    current={r['clause_id']:r for r in read_rows(ROOT/'data/clauses.csv')}
    for record in ledger:
        if record['decision'] in {'hold','exclude','duplicate'}:
            assert record['clause_id'] not in current
        if record['decision']=='hold':
            assert not record['row']['label']
            assert record['reason']
        if record['decision']=='duplicate':
            assert record['retained_clause_id'] in current


def test_abnormal_evidence_is_verbatim_in_clause_or_declared_context():
    prep={r['clause_id']:r for r in read_json(ROOT/'configs/annotation_preparation.json')['rows']}
    for row in read_rows(ROOT/'data/clauses.csv'):
        if row['label']!='abnormal':
            continue
        evidence=json.loads(row['risk_evidence'])
        assert evidence['quote'] in prep[evidence['clause_id']]['text']
        context=json.loads(row['context_clause_ids'])
        assert evidence['clause_id']==row['clause_id'] or evidence['clause_id'] in context
        assert set(row['risk_category'].split(',')) <= annotation.RISK_CATEGORIES


def test_repaired_date_setting_intro_is_not_a_termination_ground():
    rows={r['snapshot_index']:r for r in read_rows(ROOT/'data/clauses.csv')}
    for key in ['484','485','486']:
        assert rows[key]['text'].startswith('Thời hạn chấm dứt hợp đồng được xác định:')
        assert 'sẽ chấm dứt trong' not in rows[key]['text']


def test_deletion_exception_preserves_its_negative_context():
    rows={r['snapshot_index']:r for r in read_rows(ROOT/'data/clauses.csv')}
    assert 'trường hợp không thể thực hiện được như sau:' in rows['120']['text']
    assert rows['120']['label']=='abnormal'
    assert rows['117']['label']=='normal'


def test_whitespace_repairs_are_replayable():
    original='Bên B ch ấm dứt hợp đồng.'
    offset=original.index(' ' ,original.index('ch'))
    repairs=[{'start':offset,'end':offset+1,'replacement':'','kind':'whitespace'}]
    assert apply_verified_text_repairs(original,repairs)=='Bên B chấm dứt hợp đồng.'


def test_font_mapping_is_limited_to_the_verified_source():
    edits=[{'start':1,'end':2,'replacement':'ư','kind':'verified_legacy_font_glyph'}]
    assert apply_verified_text_repairs('đƣợc', edits,'fpt_phone_business')=='được'
    with pytest.raises(ValueError,match='Unapproved'):
        apply_verified_text_repairs('đƣợc',edits,'another_document')


@pytest.mark.parametrize('original,replacement', [('Không được chia sẻ dữ liệu.','Được chia sẻ dữ liệu.'),
                                                ('Trả phí khi có lỗi.','Trả phí không cần lỗi.')])
def test_repairs_cannot_remove_negation_or_rewrite_obligation(original,replacement):
    with pytest.raises(ValueError,match='changes clause content'):
        apply_verified_text_repairs(original,[{'start':0,'end':len(original),'replacement':replacement}])


def test_missing_manual_decision_cannot_default_to_normal(tmp_path,monkeypatch):
    # Isolated technical_test project: partial notes must block the actual
    # application entry point before it can replace CSV or touch approval.
    for folder in ['configs','docs','data/snapshots','reports']:
        (tmp_path/folder).mkdir(parents=True,exist_ok=True)
    data=tmp_path/'data/clauses.csv'
    records=[]
    for index in range(2):
        record=dict.fromkeys(FIELDS,'')
        record.update(clause_id=f'technical_test_{index}',text='Technical fixture for missing annotation decisions.',
                      review_status='pending')
        records.append(record)
    write_rows(data,records)
    snapshot=tmp_path/'data/snapshots/technical_test.csv'
    snapshot.write_bytes(data.read_bytes())
    rubric=tmp_path/'docs/ANNOTATION_GUIDELINES.md'
    rubric.write_text('technical_test fixture rubric only',encoding='utf-8')
    approval=tmp_path/'configs/approval.json'
    write_json(approval,{'criteria_approved':True,'dataset_approved':False,
                         'criteria_sha256':sha256(rubric),'purpose':'technical_test'})
    write_json(tmp_path/'configs/annotation_preparation.json',{
        'snapshot':'data/snapshots/technical_test.csv','snapshot_sha256':sha256(snapshot),
        'rubric_sha256':sha256(rubric),'purpose':'technical_test','rows':[{'index':'0'},{'index':'1'}]})
    (tmp_path/'configs/risk_annotation_notes.tsv').write_text(
        '1|normal||Explicit technical_test fixture decision.|\n',encoding='utf-8')
    before_data,before_approval=data.read_bytes(),approval.read_bytes()
    monkeypatch.setattr(annotation,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='Incomplete manual review'):
        annotation.main()
    assert data.read_bytes()==before_data and approval.read_bytes()==before_approval
    assert not (tmp_path/'data/clauses.annotation_staging.csv').exists()
