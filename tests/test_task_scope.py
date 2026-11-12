"""Prevent topic labels or their historical approval becoming risk ground truth."""
from pathlib import Path

from contractguard.dataset import audit,read_json,read_rows,sha256
from contractguard.provenance import verify_clause_spans

ROOT=Path(__file__).resolve().parents[1]


def test_active_target_is_anomaly_not_clause_topic():
    config=read_json(ROOT/'configs/labels.json')
    assert config['task']=='contract_anomaly_detection'
    assert set(config['labels'])=={'normal','abnormal'}
    assert not set(config['labels']) & set(config['auxiliary_labels'])


def test_source_clauses_preserved_without_topic_to_risk_conversion():
    current=read_rows(ROOT/'data/clauses.csv')
    previous=read_rows(ROOT/'data/review/v2/clauses.csv')
    manifest=read_json(ROOT/'reports/risk_annotation_manifest.json')
    snapshot=read_rows(ROOT/manifest['snapshot'])
    assert sha256(ROOT/manifest['snapshot'])==manifest['snapshot_sha256']
    assert len(snapshot)==len(previous)
    for frozen,old in zip(snapshot,previous):
        assert frozen['clause_id']==old['clause_id'] and frozen['text']==old['text']
        assert frozen['source_spans']==old['source_spans']
        assert frozen['clause_type']==old['label']
    sources=read_json(ROOT/'data/sources.json')
    pages={s['document_id']:read_json(ROOT/s['pages_path']) for s in sources}
    for new in current:
        base=int(''.join(c for c in new['snapshot_index'] if c.isdigit()))
        assert new['clause_type']==previous[base]['label']
        assert new['source_sha256']==previous[base]['source_sha256']
        verify_clause_spans(new,pages[new['document_id']])
        assert new['label'] in {'', 'normal', 'abnormal'}
        assert new['task']=='contract_anomaly_detection'
    ledger=read_json(ROOT/'reports/risk_annotation_ledger.json')
    # All original candidates remain accounted for even when duplicates and
    # blank forms are removed from the user's label-confirmation queue.
    assert {str(i) for i in range(len(previous))} <= {r['snapshot_index'] for r in ledger}


def test_old_topic_cannot_be_accepted_as_risk_label():
    row=read_rows(ROOT/'data/clauses.csv')[0]
    row.update(label='payment',review_status='accepted',reviewer='test-fixture')
    result=audit([row],['normal','abnormal'])
    assert any('unknown/empty human label' in e for e in result['errors'])


def test_old_confirmation_does_not_approve_new_scope():
    historic=read_json(ROOT/'docs/history/clause_type_task/approval.json')
    current=read_json(ROOT/'configs/approval.json')
    assert historic['criteria_approved'] is True
    assert current['scope']=='contract_anomaly_detection'
    assert current['previous_topic_confirmation_record']=='docs/history/clause_type_task/approval.json'
