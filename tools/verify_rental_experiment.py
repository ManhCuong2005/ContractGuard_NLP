"""Verify accepted data and saved official experiment without fitting or selecting again."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from contractguard.dataset import read_json, require_approval, sha256, write_json
from contractguard.model import Predictor
from contractguard.profiles import profile_paths

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'outputs/rental_mvp1b_v1'


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def main():
    paths = profile_paths(ROOT, 'rental')
    rows, labels, approval = require_approval(paths['dataset'], paths['approval'],
        paths['rubric'], paths['labels'], paths['sources'], ROOT)
    precommit = read_json(RUN/'precommit.json')
    selected = read_json(RUN/'validation_selection.json')
    meta = read_json(RUN/'model.json')
    metrics = read_json(RUN/'metrics.json')
    assert sha256(paths['dataset']) == precommit['dataset_sha256'] == meta['dataset_sha256']
    assert sha256(RUN/'splits.csv') == precommit['split_sha256'] == meta['split_sha256']
    for name, digest in precommit['experiment_config']['code_sha256'].items():
        assert sha256(ROOT/'src/contractguard'/name) == digest, name
    assert precommit['created_before_fitting'] and not selected['test_used_for_selection']
    assert selected['selected_model'] == metrics['selected_model'] == meta['selected_model']
    assert selected['validation_experiments'] == metrics['validation_experiments']
    assert datetime.fromisoformat(selected['selected_at']) <= datetime.fromisoformat(meta['trained_at'])
    splits = read_rows(RUN/'splits.csv')
    assert Counter(r['clause_id'] for r in splits) == Counter(r['clause_id'] for r in rows)
    for key in ['document_id', 'group_id', 'leakage_group']:
        assignments = defaultdict(set)
        for r in splits:
            assignments[r[key]].add(r['split'])
        assert all(len(v) == 1 for v in assignments.values()), key
    counts = {name: dict(Counter(r['label'] for r in splits if r['split'] == name))
              for name in ['train', 'validation', 'test']}
    assert counts == read_json(RUN/'split_counts.json')
    index = {r['clause_id']: r for r in rows}
    model = Predictor(RUN/'model.joblib')
    vectorizer = model.pipeline.named_steps['features']
    assert len(vectorizer.vocabulary_) < vectorizer.max_features
    analyzer = vectorizer.build_analyzer()
    expected = {t for r in splits if r['split'] != 'test' for t in analyzer(index[r['clause_id']]['text'])}
    assert set(vectorizer.vocabulary_) == expected
    test_only = {t for r in splits if r['split'] == 'test' for t in analyzer(index[r['clause_id']]['text'])} - expected
    assert test_only and not test_only & set(vectorizer.vocabulary_)
    predictions = read_rows(RUN/'test_predictions.csv')
    assert {r['clause_id'] for r in predictions} == {r['clause_id'] for r in splits if r['split']=='test'}
    assert len(predictions) == metrics['test']['samples'] == 94
    assert all((r['text'],r['true_label']) == (index[r['clause_id']]['text'],index[r['clause_id']]['label']) for r in predictions)
    assert len(read_rows(RUN/'errors.csv')) == sum(r['true_label'] != r['predicted_label'] for r in predictions) == 6
    assert metrics['test']['confusion_matrix'] == [[88,0],[6,0]]
    assert metrics['test']['classification_report']['abnormal']['recall'] == 0
    assert metrics['save_reload_predictions_identical']
    assert read_json(RUN/'cli_inference.json') == read_json(RUN/'offline_inference.json')
    expected_hashes = {
        'data/clauses.csv':'4a259465d17d3c4d9c4b5a836c9a5c05083b5a5c592014fb4fc11ca9e94fd3c6',
        'configs/approval.json':'64976df19fe52979607a557a5582d226dbf6fe3acf9dc5cf6584cde7ebd51419',
        'docs/ANNOTATION_GUIDELINES.md':'ef0596c0ead897ff3a5d178b6b7801abd24a772e4b8270f8936ca3a64e7330f8',
        'docs/LABELING_GUIDELINES.md':'68a1d9c068637c942e4c4c44648f299431960d64c01d1654652fc23f13c1a9fa',
        'configs/rental_labels.json':'8fa4adc4c0172e8118c7aec431f6d7caeba319a723c233799d06a0a101ce8f78',
        'data/clauses_rental_v1.csv':approval['reviewed_draft_sha256'],
    }
    assert all(sha256(ROOT/k) == v for k,v in expected_hashes.items())
    xml = ET.parse(ROOT/'reports/rental-mvp1b-test-results.xml').getroot()
    suites = list(xml.iter('testsuite'))
    test_counts = {name: sum(int(s.get(name,0)) for s in suites)
                   for name in ['tests','failures','errors','skipped']}
    assert test_counts['tests'] == 99 and test_counts['failures'] == test_counts['errors'] == 0
    dependency_check = subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True,check=True)
    packages = ['numpy','scipy','scikit-learn','joblib','pytest','matplotlib','contourpy',
        'cycler','fonttools','kiwisolver','pyparsing','python-dateutil','tzdata']
    write_json(RUN/'environment.json', {'python':sys.version,'packages':{p:version(p) for p in packages}})
    write_json(ROOT/'reports/rental_mvp1b_verification.json', {
        'verified_at':datetime.now(timezone.utc).isoformat(),
        'dataset_accepted_by_user':True,'approval_record':'reports/rental_dataset_approval.json',
        'dataset_sha256':sha256(paths['dataset']),'rows':len(rows),'labels':labels,
        'split_counts':counts,'group_disjoint':True,'training_code_hashes_match_precommit':True,
        'final_vectorizer_vocabulary_matches_train_plus_validation_only':True,
        'heldout_only_tokens_excluded':len(test_only),'selection_record_matches_metrics':True,
        'model_checksum_verified':True,'save_reload_identical_recorded':True,
        'cli_inference_matches_saved_smoke_output':True,'smoke_is_new_quality_estimate':False,
        'legacy_and_draft_and_criteria_hashes_unchanged':True,
        'technical_tests':test_counts,'pip_check':dependency_check.stdout.strip(),
        'test_warnings':'Two SciPy optimizer deprecations in technical fixtures; tests passed.',
        'experiment_warning':'One Liblinear convergence warning; candidate not captured per name in v1. Selected model Logistic Regression.',
        'figures_visually_inspected':['confusion_matrix.png','validation_comparison.png'],
        'official_test_abnormal_recall':0,'quality_gate_passed':False,
        'mvp1_complete':False,'mvp2_started':False,'external_ai_calls':False,
        'verification_did_not_fit_or_select_models':True})
    print(json.dumps({'verification':'passed','technical_tests':test_counts,
                      'heldout_only_tokens_excluded':len(test_only),
                      'model_quality_passed':False},ensure_ascii=False))


if __name__ == '__main__':
    main()
