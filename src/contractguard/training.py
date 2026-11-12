"""Approval-gated training, validation selection and one held-out test."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import platform
import time

import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             precision_recall_fscore_support)
from sklearn.model_selection import StratifiedGroupKFold

from .dataset import (leakage_groups, read_json, require_approval, sha256, write_json, write_rows)
from .model import Predictor, candidates, save_model


def metrics(y_true, y_pred, labels):
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels,
                                                average='macro', zero_division=0)
    return {'accuracy': float(accuracy_score(y_true, y_pred)), 'precision_macro': float(p),
            'recall_macro': float(r), 'f1_macro': float(f1),
            'f1_weighted': float(precision_recall_fscore_support(
                y_true, y_pred, labels=labels, average='weighted', zero_division=0)[2]),
            'classification_report': classification_report(y_true, y_pred, labels=labels,
                                                           output_dict=True, zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred, labels=labels).tolist(),
            'labels': labels, 'samples': len(y_true)}


def split_rows(rows, labels, seed=42):
    y = np.array([r['label'] for r in rows])
    groups = np.array(leakage_groups(rows))
    for label in labels:
        count = len(set(groups[y == label]))
        if count < 5:
            raise ValueError(f'{label}: needs at least 5 independent template/near-duplicate groups; got {count}')
    # Fold 0 test, fold 1 validation, other folds train. No model scores influence split.
    for attempt in range(50):
        folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed+attempt)
                     .split(np.zeros(len(y)), y, groups))
        test = folds[0][1]
        val = folds[1][1]
        train = np.array(sorted(set(range(len(rows))) - set(test) - set(val)))
        if all(set(y[idx]) == set(labels) for idx in [train, val, test]):
            return {'train': train, 'validation': val, 'test': test}, groups, seed+attempt
    raise ValueError('Cannot form three group-disjoint partitions covering all labels; collect more independent contracts')


def train(root, dataset, output, seed=42, *, profile='legacy'):
    root, dataset, output = Path(root), Path(dataset), Path(output)
    from .profiles import profile_paths
    paths=profile_paths(root,profile)
    config = read_json(paths['labels'])
    if config.get('task') != 'contract_anomaly_detection' or set(config['labels']) != {'normal', 'abnormal'}:
        raise ValueError('Official ContractGuard training requires the normal/abnormal risk task')
    rows, labels, approval = require_approval(
        dataset, paths['approval'], paths['rubric'],paths['labels'],paths['sources'], root)
    if profile=='rental':
        from .rental_split import balanced_split_rows
        from .rental_features import rental_candidates
        models,model_config=rental_candidates(seed)
        fixed=balanced_split_rows(rows,labels,seed)
        return _run_experiment(rows,labels,dataset,output,seed,approval=approval,purpose='official',
            fixed_split=fixed,models=models,experiment_config=dict(profile=profile,models=model_config,
                selection_metric='validation.f1_macro',input_columns=['text'],
                split_method='128 fixed-seed StratifiedGroupKFold attempts, all ordered held-out fold pairs; minimize row/label ratio error; no predictions inspected',
                minimum_abnormal_in_validation_and_test=5,minimum_positive_groups_per_heldout=2,
                pretrained_models=False,external_ai_api=False,
                code_sha256={name:sha256(Path(__file__).parent/name) for name in ['training.py','rental_features.py','rental_split.py','text.py','model.py']}))
    return _run_experiment(rows, labels, dataset, output, seed, approval=approval, purpose='official')


def _run_experiment(rows, labels, dataset, output, seed=42, *, approval=None, purpose='technical_test',fixed_split=None,models=None,experiment_config=None):
    """Shared engine. Technical tests are explicitly marked and unusable by normal inference."""
    if purpose not in {'official', 'technical_test'} or (purpose == 'official' and not approval):
        raise ValueError('Official experiments require the approval-gated entry point')
    dataset, output = Path(dataset), Path(output)
    split, groups, split_seed = fixed_split if fixed_split is not None else split_rows(rows, labels, seed)
    if output.exists():
        raise ValueError('Run directory exists; choose a new destination to preserve prior experiments')
    texts = np.array([r['text'] for r in rows])
    y = np.array([r['label'] for r in rows])
    tr, va, te = (split[k] for k in ['train', 'validation', 'test'])
    assignments = []
    for name,indices in split.items():
        for idx in indices:
            assignments.append({'clause_id':rows[idx]['clause_id'],'document_id':rows[idx]['document_id'],
                'group_id':rows[idx]['group_id'],'leakage_group':groups[idx],'label':rows[idx]['label'],'split':name})
    for a,b in [('train','validation'),('train','test'),('validation','test')]:
        if set(groups[split[a]]) & set(groups[split[b]]):raise ValueError('Split groups overlap')
    output.mkdir(parents=True)
    write_rows(output/'splits.csv',assignments,['clause_id','document_id','group_id','leakage_group','label','split'])
    write_json(output/'precommit.json',dict(purpose=purpose,dataset_sha256=sha256(dataset),
        split_sha256=sha256(output/'splits.csv'),seed=seed,split_seed=split_seed,
        experiment_config=experiment_config,created_before_fitting=True,
        test_selection_policy='Select using validation only; final refit on train+validation, one final selected-model test evaluation plus dummy comparator.'))
    results = []
    models = models if models is not None else candidates(seed)
    for name, pipeline in models.items():
        start = time.perf_counter()
        pipeline.fit(texts[tr].tolist(), y[tr])
        score = metrics(y[va], pipeline.predict(texts[va].tolist()), labels)
        results.append({'model': name, 'validation': score, 'seconds': time.perf_counter()-start})
    # Durable validation evidence and winner recorded before touching test data.
    # Dummy is a comparator only. Stable insertion order breaks ties.
    best = max((r for r in results if r['model'] != 'dummy'), key=lambda r: r['validation']['f1_macro'])['model']
    write_json(output/'validation_selection.json',dict(selected_model=best,selection_metric='validation.f1_macro',
        validation_experiments=results,test_used_for_selection=False,
        selected_at=datetime.now(timezone.utc).isoformat()))
    final = clone(models[best])
    development = np.concatenate([tr, va])
    final.fit(texts[development].tolist(), y[development])
    predictions = final.predict(texts[te].tolist())
    test = metrics(y[te], predictions, labels)
    dummy = clone(models['dummy']).fit(texts[development].tolist(), y[development])
    dummy_test = metrics(y[te], dummy.predict(texts[te].tolist()), labels)
    run_id = output.name
    meta = {'purpose': purpose, 'run_id': run_id, 'selected_model': best,
            'task': approval.get('scope', 'technical_test') if approval else 'technical_test',
            'trained_at': datetime.now(timezone.utc).isoformat(), 'seed': seed,
            'split_seed': split_seed, 'dataset_sha256': sha256(dataset),
            'approval': approval, 'python_version': platform.python_version(),
            'experiment_config':experiment_config,'split_sha256':sha256(output/'splits.csv'),
            'sklearn_version': sklearn.__version__, 'numpy_version': np.__version__,
            'labels': labels, 'preprocessing': 'NFC + whitespace + lowercase; negation/numbers retained',
            'test_not_used_for_fitting': True}
    if experiment_config:
        meta['feature_configuration']=experiment_config['models'][best]
        meta['preprocessing']=experiment_config['models'][best].get('preprocessing','conservative')
    save_model(output/'model.joblib', final, meta)
    loaded = Predictor(output/'model.joblib', allow_test_artifact=purpose == 'technical_test')
    # Raw labels match even on an all-OOV test clause; Predictor flags those for review.
    reloaded_predictions = loaded.pipeline.predict(texts[te].tolist())
    if not np.array_equal(predictions, reloaded_predictions):
        raise RuntimeError('Save/reload changed predictions')
    test['zero_feature_samples'] = int(sum(final.named_steps['features'].transform(texts[te].tolist()).getnnz(axis=1) == 0))
    write_json(output/'metrics.json', {'purpose': purpose, 'validation_experiments': results,
                                      'selected_model': best, 'test': test, 'dummy_test': dummy_test,
                                      'save_reload_predictions_identical': True})
    write_rows(output/'splits.csv', assignments,
               ['clause_id', 'document_id', 'group_id', 'leakage_group', 'label', 'split'])
    pred_rows = [{'clause_id': rows[i]['clause_id'], 'text': rows[i]['text'],
                  'true_label': str(y[i]), 'predicted_label': str(pred)} for i, pred in zip(te, predictions)]
    write_rows(output/'test_predictions.csv', pred_rows,
               ['clause_id', 'text', 'true_label', 'predicted_label'])
    write_rows(output/'errors.csv', [r for r in pred_rows if r['true_label'] != r['predicted_label']],
               ['clause_id', 'text', 'true_label', 'predicted_label'])
    write_rows(output/'confusion_matrix.csv', [dict(zip(['true_label']+labels, [label]+values))
               for label, values in zip(labels, test['confusion_matrix'])], ['true_label']+labels)
    counts = {k: dict(Counter(y[idx])) for k, idx in split.items()}
    write_json(output/'split_counts.json', counts)
    report = [f'# ContractGuard MVP 1 — {run_id}', '', f'Purpose: {purpose}.', f'Model: {best}.',
              'Selected using validation Macro F1; refit train + validation; evaluate test once.',
              f'Save/reload identical predictions: True. Dataset SHA256: {sha256(dataset)}.', '',
              '| Metric | Test | Dummy |', '|---|---:|---:|']
    for key in ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro', 'f1_weighted']:
        report.append(f'| {key} | {test[key]:.6f} | {dummy_test[key]:.6f} |')
    report += ['', 'Confusion matrix: rows = true, columns = predicted; see confusion_matrix.csv.',
               'Review errors.csv manually. Metrics describe this dataset/split only.',
               'Limitations: public templates, domain imbalance, single-label ambiguity, no calibrated confidence.',
               'No legal risk assessment or legal advice. Stop after MVP 1.']
    (output/'report.md').write_text('\n'.join(report), encoding='utf-8')
    return {'selected_model': best, 'test': test, 'output': str(output)}
