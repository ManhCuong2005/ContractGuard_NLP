"""Technical fixtures only. No fixture is an official contract or benchmark."""
import json
from pathlib import Path
import unicodedata

import numpy as np
import pytest

from contractguard.cli import main
from contractguard.dataset import (FIELDS, audit, leakage_groups, read_rows, require_approval,
                                   sha256, write_json, write_rows)
from contractguard.model import Predictor, candidates, save_model
from contractguard.text import normalize, require_text
from contractguard.training import _run_experiment, metrics, split_rows, train


@pytest.mark.parametrize('raw', ['\tKhông\u00a0thanh  toán 8%\n', unicodedata.normalize('NFD', 'Không thanh toán 8%')])
def test_normalization_retains_legal_signal(raw):
    assert normalize(raw) == 'không thanh toán 8%'


@pytest.mark.parametrize('raw', [None, '', '  ', 123, '!!!', '123 456 789', 'một hai'])
def test_invalid_input(raw):
    with pytest.raises(ValueError):
        require_text(raw)


def test_too_long_input():
    with pytest.raises(ValueError, match='20000'):
        require_text('abc ' * 6000)


def row(**changes):
    result = dict.fromkeys(FIELDS, '')
    result.update(clause_id='test_001', text='fixture orange fruit basket',
                  document_id='fixture_document', group_id='fixture_family',
                  source_url='https://example.org/test-fixture', source_sha256='a'*64,
                  page_start='1', page_end='1', label='fruit',
                  review_status='accepted', reviewer='unit-test-fixture')
    result.update(changes)
    return result


def test_audit_requires_human_label_and_reviewer():
    result = audit([row(label='', reviewer='')], ['fruit'])
    assert len(result['errors']) == 2


def test_pending_does_not_count_as_ground_truth():
    result = audit([row(review_status='pending', label='', suggested_label='fruit')], ['fruit'])
    assert result['label_counts'] == {}
    assert result['status_counts'] == {'pending': 1}


def test_rejection_requires_reason():
    assert audit([row(review_status='rejected')], ['fruit'])['errors']


def test_duplicate_normalized_and_ids_are_detected():
    result = audit([row(), row(text='FIXTURE   orange fruit basket')], ['fruit'])
    assert any('duplicate clause_id' in e for e in result['errors'])
    assert any('duplicate normalized' in e for e in result['errors'])


def test_csv_utf8_roundtrip(tmp_path):
    records = [row(text='Không tiết lộ dữ liệu cá nhân, tỷ lệ 8%.')]
    path = tmp_path/'review.csv'
    write_rows(path, records)
    assert read_rows(path) == records


def test_missing_columns(tmp_path):
    path = tmp_path/'bad.csv'
    path.write_text('text,label\nhello,fruit', encoding='utf-8')
    with pytest.raises(ValueError, match='columns'):
        read_rows(path)


def test_groups_join_documents_families_near_duplicates():
    long = ' '.join(f'unique{i}' for i in range(40))
    rows = [row(text=long, group_id='a', document_id='doca'),
            row(clause_id='b', text=long+' extra', group_id='b', document_id='docb'),
            row(clause_id='c', text='quite different fixture orange banana', group_id='b', document_id='docc'),
            row(clause_id='d', text='isolated document fixture pears apple', group_id='z', document_id='docc')]
    groups = leakage_groups(rows)
    assert len(set(groups)) == 1


def split_fixture():
    return [row(clause_id=f'{g}_{label}', document_id=f'd{g}', group_id=f'g{g}', label=label,
                text=f'group{g} {label} token{g} fixture{label} unique{g} extra{g}')
            for g in range(10) for label in ['fruit', 'animal']]


def test_group_split_disjoint_reproducible():
    rows = split_fixture()
    a, groups, _ = split_rows(rows, ['fruit', 'animal'])
    b, _, _ = split_rows(rows, ['fruit', 'animal'])
    for k in a:
        assert np.array_equal(a[k], b[k])
        assert {rows[i]['label'] for i in a[k]} == {'fruit', 'animal'}
    assert set(a['train']) | set(a['validation']) | set(a['test']) == set(range(len(rows)))
    gs = [set(groups[i] for i in a[k]) for k in a]
    assert all(not gs[i] & gs[j] for i in range(3) for j in range(i))


def test_insufficient_independent_groups_fails():
    with pytest.raises(ValueError, match='5 independent'):
        split_rows(split_fixture()[:6], ['fruit', 'animal'])


@pytest.mark.parametrize('name', list(candidates()))
def test_all_models_fit_predict_and_reload_on_toy_fixture(tmp_path, name):
    # Generic toy strings; scores are deliberately not computed or reported.
    model = candidates()[name]
    texts = ['orange apple fruit basket', 'banana pear fruit tree',
             'cat dog animal running', 'horse rabbit animal field']
    model.fit(texts, ['fruit', 'fruit', 'animal', 'animal'])
    unseen = ['fresh orange apple basket', 'rabbit dog animal meadow']
    before = model.predict(unseen)
    path = tmp_path/(name+'.joblib')
    save_model(path, model, {'purpose':'technical_test', 'run_id':'unit-test-only'})
    predictor = Predictor(path, allow_test_artifact=True)
    assert np.array_equal(before, predictor.pipeline.predict(unseen))
    assert all(p['model_purpose'] == 'technical_test' for p in predictor.predict(unseen))
    with pytest.raises(ValueError, match='official model'):
        Predictor(path)
    with pytest.raises(ValueError, match='exists'):
        save_model(path, model, {'purpose':'technical_test'})


def test_vectorizer_never_fits_unseen_tokens():
    model = candidates()['linear_svm']
    model.fit(['apple orange fruit', 'cat dog animal'], ['fruit', 'animal'])
    vocab = model.named_steps['features'].vocabulary_.copy()
    model.predict(['heldoutzz tokenzz sentencezz'])
    assert model.named_steps['features'].vocabulary_ == vocab
    assert 'heldoutzz' not in vocab


def test_zero_feature_input_abstains(tmp_path):
    model = candidates()['linear_svm'].fit(['apple orange fruit', 'cat dog animal'], ['fruit', 'animal'])
    path = tmp_path/'toy.joblib'
    save_model(path, model, {'purpose':'technical_test'})
    predictor = Predictor(path, allow_test_artifact=True)
    output = predictor.predict(['qwertyzz asdfghzz zxcvbnzz'])[0]
    assert output['label'] is None and output['needs_review'] is True
    assert output['confidence'] is None
    with pytest.raises(ValueError):
        predictor.predict([])


def test_tampered_model_rejected_before_pickle_load(tmp_path):
    path = tmp_path/'toy.joblib'
    model = candidates()['linear_svm'].fit(['apple orange fruit', 'cat dog animal'], ['fruit', 'animal'])
    save_model(path, model, {'purpose':'technical_test'})
    path.write_bytes(b'not a pickle')
    with pytest.raises(ValueError, match='checksum'):
        Predictor(path, allow_test_artifact=True)


def test_metric_order_and_zero_division():
    # Known toy confusion counts validate arithmetic; not a reported experiment.
    m = metrics(['fruit', 'fruit', 'animal'], ['fruit', 'animal', 'animal'], ['animal', 'fruit'])
    assert m['confusion_matrix'] == [[1, 0], [1, 1]]
    assert m['accuracy'] == pytest.approx(2/3)
    assert m['precision_macro'] == pytest.approx(0.75)
    assert m['recall_macro'] == pytest.approx(0.75)
    assert m['f1_macro'] == pytest.approx(2/3)


@pytest.fixture
def approval_fixture(tmp_path):
    # A simulated approval fixture validates the gate, never passed to training.
    root = tmp_path
    for name in ['data', 'configs', 'docs']:
        (root/name).mkdir()
    raw = root/'data/source.txt'
    raw.write_text('fixture orange fruit basket', encoding='utf-8')
    pages = root/'data/pages.json'
    write_json(pages, ['fixture orange fruit basket'])
    source = {'document_id':'fixture_document', 'group_id':'fixture_family',
              'source_url':'https://example.org/test-fixture', 'source_sha256':sha256(raw),
              'pages_sha256':sha256(pages), 'raw_path':'data/source.txt',
              'pages_path':'data/pages.json', 'data_kind':'public_contract_template'}
    files = {'dataset_sha256':root/'data/clauses.csv', 'criteria_sha256':root/'docs/rubric.md',
             'labels_sha256':root/'configs/labels.json', 'sources_sha256':root/'data/sources.json'}
    files['criteria_sha256'].write_text('TEST FIXTURE ONLY', encoding='utf-8')
    write_json(files['labels_sha256'], {'labels':['fruit']})
    write_json(files['sources_sha256'], [source])
    write_rows(files['dataset_sha256'], [row(source_sha256=sha256(raw))])
    approval = {'criteria_approved':True, 'dataset_approved':True, 'source_use_confirmed':True,
                'approved_by':'simulated-unit-test', 'approved_at':'2026-01-01T00:00:00+07:00',
                'reviewed_source_ids':['fixture_document'], **{k:sha256(p) for k,p in files.items()}}
    path = root/'configs/approval.json'
    write_json(path, approval)
    return root, files, path, approval


def gate(fixture):
    root, files, path, _ = fixture
    return require_approval(files['dataset_sha256'], path, files['criteria_sha256'],
                            files['labels_sha256'], files['sources_sha256'], root)


def test_gate_checks_all_provenance(approval_fixture):
    rows, labels, _ = gate(approval_fixture)
    assert len(rows) == 1 and labels == ['fruit']


@pytest.mark.parametrize('flag', ['criteria_approved', 'dataset_approved', 'source_use_confirmed'])
def test_each_approval_flag_required(approval_fixture, flag):
    _, _, path, a = approval_fixture
    a[flag] = False
    write_json(path, a)
    with pytest.raises(ValueError, match=flag):
        gate(approval_fixture)


@pytest.mark.parametrize('key', ['dataset_sha256', 'criteria_sha256', 'labels_sha256', 'sources_sha256'])
def test_any_content_change_invalidates_approval(approval_fixture, key):
    _, files, _, _ = approval_fixture
    with files[key].open('a', encoding='utf-8') as f:
        f.write('\n')
    with pytest.raises(ValueError, match='digest mismatch'):
        gate(approval_fixture)


def test_changed_original_rejected(approval_fixture):
    root, _, _, _ = approval_fixture
    (root/'data/source.txt').write_text('changed original', encoding='utf-8')
    with pytest.raises(ValueError, match='Source file changed'):
        gate(approval_fixture)


def test_unknown_source_blocks(approval_fixture):
    _, _, path, a = approval_fixture
    a['reviewed_source_ids'] = []
    write_json(path, a)
    with pytest.raises(ValueError, match='Unreviewed source'):
        gate(approval_fixture)


def test_changed_text_repair_reference_blocks_approved_fixture(approval_fixture):
    # Simulated approval only exercises the gate; this fixture is never fitted.
    root, files, path, a = approval_fixture
    reference = root/'data/reference.json'
    write_json(reference, {'source_sha256':sha256(root/'data/source.txt'),
                           'pages':['fixture orange fruit basket']})
    record = row(source_sha256=sha256(root/'data/source.txt'),
                 source_text='fixture orange fruit basket', text_repairs='[]',
                 source_spans=json.dumps([{'page':1,'start':0,'end':27}]),
                 text_repair_reference=json.dumps({'path':'data/reference.json','sha256':sha256(reference)}))
    write_rows(files['dataset_sha256'], [record], list(record))
    a['dataset_sha256'] = sha256(files['dataset_sha256'])
    write_json(path,a)
    assert len(gate(approval_fixture)[0]) == 1
    reference.write_text('changed extraction evidence',encoding='utf-8')
    with pytest.raises(ValueError,match='Text repair reference hash changed'):
        gate(approval_fixture)


def test_gate_rejects_confirmation_from_another_task(approval_fixture):
    _, files, path, a = approval_fixture
    write_json(files['labels_sha256'], {'labels': ['fruit'], 'task': 'contract_anomaly_detection'})
    a.update(labels_sha256=sha256(files['labels_sha256']), scope='clause_topic')
    write_json(path, a)
    with pytest.raises(ValueError, match='scope'):
        gate(approval_fixture)


@pytest.mark.parametrize('missing', ['annotation_reason', 'annotation_status', 'risk_category', 'task'])
def test_risk_acceptance_requires_annotation_evidence(approval_fixture, missing):
    _, files, path, a = approval_fixture
    fields = FIELDS + ['task', 'annotation_reason', 'annotation_status', 'risk_category']
    record = row(source_sha256=sha256(approval_fixture[0]/'data/source.txt'),
                 label='abnormal', task='contract_anomaly_detection', annotation_reason='Technical gate fixture only',
                 annotation_status='reviewed', risk_category='broad_liability')
    record[missing] = ''
    write_rows(files['dataset_sha256'], [record], fields)
    write_json(files['labels_sha256'], {'labels': ['abnormal'], 'task': 'contract_anomaly_detection'})
    a.update(scope='contract_anomaly_detection',
             labels_sha256=sha256(files['labels_sha256']), dataset_sha256=sha256(files['dataset_sha256']))
    write_json(path, a)
    with pytest.raises(ValueError, match='required|reviewed|risk_category'):
        gate(approval_fixture)


def test_official_topic_artifact_cannot_be_loaded_as_risk_model(tmp_path):
    model = candidates()['linear_svm'].fit(['apple orange fruit', 'cat dog animal'], ['fruit', 'animal'])
    path = tmp_path/'old_topic.joblib'
    save_model(path, model, {'purpose': 'official', 'task': 'clause_topic', 'labels': ['fruit', 'animal']})
    with pytest.raises(ValueError, match='normal/abnormal'):
        Predictor(path)


def test_official_training_locked_and_no_artifact(tmp_path):
    root = Path(__file__).resolve().parents[1]
    (tmp_path/'configs').mkdir()
    write_json(tmp_path/'configs/labels.json', {'task':'contract_anomaly_detection', 'labels':['normal','abnormal']})
    write_json(tmp_path/'configs/approval.json', {'criteria_approved':False})
    output = tmp_path/'must_not_exist'
    with pytest.raises(ValueError, match='Human approval required: criteria_approved'):
        train(tmp_path, root/'data/clauses.csv', output)
    assert not output.exists()


def test_cli_reports_locked_training(tmp_path, capsys):
    (tmp_path/'configs').mkdir()
    write_json(tmp_path/'configs/labels.json', {'task':'contract_anomaly_detection', 'labels':['normal','abnormal']})
    write_json(tmp_path/'configs/approval.json', {'criteria_approved':False})
    assert main(['--root', str(tmp_path), 'train', '--data', 'data/clauses.csv', '--output', str(tmp_path/'run')]) == 2
    assert 'Human approval required' in capsys.readouterr().err


def test_cli_audit_has_no_fit(capsys):
    assert main(['audit', '--data', 'data/clauses.csv']) == 0
    data = json.loads(capsys.readouterr().out)
    assert data['provenance']['clauses_verified'] == data['rows']


def test_full_experiment_engine_test_only(tmp_path):
    records = split_fixture()
    data = tmp_path/'toy_fixture.csv'
    write_rows(data, records)
    output = tmp_path/'technical_test_run'
    _run_experiment(records, ['fruit', 'animal'], data, output, purpose='technical_test')
    result = json.loads((output/'metrics.json').read_text(encoding='utf-8'))
    assert result['purpose'] == 'technical_test'
    assert result['save_reload_predictions_identical'] is True
    assert result['selected_model'] != 'dummy'
    assert sum(map(sum, result['test']['confusion_matrix'])) == result['test']['samples']
    assert (output/'errors.csv').is_file()
    assert (output/'report.md').is_file()
    assert 'Purpose: technical_test' in (output/'report.md').read_text(encoding='utf-8')
    with pytest.raises(ValueError, match='official model'):
        Predictor(output/'model.joblib')
    # Changing future output paths cannot turn a test artifact into an official model.
    with pytest.raises(ValueError, match='exists'):
        _run_experiment(records, ['fruit', 'animal'], data, output, purpose='technical_test')
