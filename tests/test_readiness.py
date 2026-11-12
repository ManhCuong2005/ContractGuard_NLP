"""Risk dataset integrity and approval regressions; no official fitting."""
from copy import deepcopy
from pathlib import Path

import pytest

from contractguard.cli import main
from contractguard.dataset import (audit_dataset, audit_provenance, read_json,
                                   read_rows, sha256, training_readiness, write_json)
from contractguard.provenance import verify_spans
from contractguard.training import train

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def pending_approval(monkeypatch):
    # Keep this regression valid after the real user eventually approves the dataset.
    import contractguard.dataset as module
    original = module.read_json
    def read_with_pending_approval(path):
        result = original(path)
        if Path(path).resolve() == (ROOT/'configs/approval.json').resolve():
            result.update(criteria_approved=False, dataset_approved=False, source_use_confirmed=False)
        return result
    monkeypatch.setattr(module, 'read_json', read_with_pending_approval)


def test_pending_canonical_rows_have_exact_source_evidence():
    result = audit_dataset(ROOT/'data/clauses.csv', ROOT/'configs/labels.json',
                           ROOT/'data/sources.json', ROOT)
    assert result['errors'] == []
    assert result['provenance']['clauses_verified'] == result['rows']


@pytest.mark.parametrize('field,value', [
    ('text', 'This text was invented and does not exist in the original source.'),
    ('source_sha256', '0'*64), ('page_end', '99999'), ('document_id', 'nonexistent'),
    ('source_spans', '[null]'),
])
def test_pending_source_corruption_is_reported(field, value):
    row = read_rows(ROOT/'data/clauses.csv')[0]
    row[field] = value
    result = audit_provenance([row], ROOT/'data/sources.json', ROOT)
    assert result['errors'] and result['clauses_verified'] == 0


def test_unapproved_readiness_is_readonly_and_has_no_fit(monkeypatch, pending_approval):
    before = {p: sha256(ROOT/p) for p in ['data/clauses.csv', 'configs/approval.json']}
    def forbidden(*args, **kwargs):
        raise AssertionError('Readiness must not fit')
    monkeypatch.setattr('sklearn.pipeline.Pipeline.fit', forbidden)
    result = training_readiness(ROOT, ROOT/'data/clauses.csv')
    assert result['official_training_ready'] is False
    assert result['blockers']
    assert result['official_metrics'] is None
    assert result['candidate_leakage_groups'] <= result['candidate_template_families']
    assert before == {p: sha256(ROOT/p) for p in before}


def test_readiness_cli_reports_blockers(capsys, pending_approval):
    import json
    assert main(['readiness']) == 0
    result = json.loads(capsys.readouterr().out)
    assert result['official_training_ready'] is False


def test_topic_task_cannot_enter_official_training(tmp_path):
    (tmp_path/'configs').mkdir()
    write_json(tmp_path/'configs/labels.json', {'task': 'clause_topic', 'labels': ['payment']})
    output = tmp_path/'run'
    with pytest.raises(ValueError, match='normal/abnormal'):
        train(tmp_path, tmp_path/'data.csv', output)
    assert not output.exists()


def test_source_manifest_path_cannot_escape_root(tmp_path):
    sources = deepcopy(read_json(ROOT/'data/sources.json'))
    sources[0]['raw_path'] = '../outside.pdf'
    path = tmp_path/'sources.json'
    write_json(path, sources)
    result = audit_provenance([], path, ROOT)
    assert any('Invalid provenance file' in e for e in result['errors'])


def test_malformed_span_is_a_validation_error():
    with pytest.raises(ValueError, match='object'):
        verify_spans('some clause', ['some clause'], [None])
