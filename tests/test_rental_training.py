"""Approval, split and feature invariants; fixtures are technical_test only."""
from pathlib import Path
from collections import Counter
import json
import sys
import numpy as np
import pytest
from contractguard.dataset import read_json,read_rows,require_approval,sha256,write_json
from contractguard.profiles import profile_paths
from contractguard.rental_split import balanced_split_rows
from contractguard.rental_features import rental_candidates,domain_tokenize,vector
ROOT=Path(__file__).resolve().parents[1]

def test_actual_acceptance_freezes_labels_and_text_without_reviewer_invention():
    paths=profile_paths(ROOT,'rental')
    rows,labels,approval=require_approval(paths['dataset'],paths['approval'],paths['rubric'],paths['labels'],paths['sources'],ROOT)
    draft=read_rows(ROOT/'data/clauses_rental_v1.csv')
    assert len(rows)==len(draft)==517
    assert all((a['text'],a['label'])==(b['text'],b['label']) for a,b in zip(rows,draft))
    assert all(r['reviewer']=='user_in_chat' and r['annotation_status']=='reviewed' for r in rows)
    assert all(r['verified_risk_label']==r['label'] for r in rows)
    record=read_json(ROOT/'reports/rental_dataset_approval.json')
    assert record['labels_changed']==record['texts_changed']==0
    assert not record['reviewer_name_supplied']
    assert not record['mvp2_authorized'] and not record['external_redistribution_authorized']

def test_draft_and_legacy_approval_cannot_train_rental(tmp_path):
    p=profile_paths(ROOT,'rental')
    with pytest.raises(ValueError,match='digest mismatch'):
        require_approval(ROOT/'data/clauses_rental_v1.csv',p['approval'],p['rubric'],p['labels'],p['sources'],ROOT)
    with pytest.raises(ValueError):
        require_approval(p['dataset'],ROOT/'configs/approval.json',p['rubric'],p['labels'],p['sources'],ROOT)
    bad=read_json(p['approval'])
    bad['domain']='technical_test_wrong_domain'
    target=tmp_path/'technical_test_approval.json'
    write_json(target,bad)
    with pytest.raises(ValueError,match='domain'):
        require_approval(p['dataset'],target,p['rubric'],p['labels'],p['sources'],ROOT)

def test_balanced_group_split_has_real_heldout_support_and_is_reproducible():
    rows=read_rows(profile_paths(ROOT,'rental')['dataset'])
    a,groups,seed=balanced_split_rows(rows,['normal','abnormal'])
    b,other,other_seed=balanced_split_rows(rows,['normal','abnormal'])
    assert seed==other_seed and np.array_equal(groups,other)
    assert all(np.array_equal(a[k],b[k]) for k in a)
    assert sorted(np.concatenate(list(a.values())))==list(range(len(rows)))
    for name,idx in a.items():
        assert set(rows[i]['label'] for i in idx)=={'normal','abnormal'}
        if name!='train':assert sum(rows[i]['label']=='abnormal' for i in idx)>=5
        for second in a:
            if second!=name:
                assert not set(groups[idx])&set(groups[a[second]])
                assert not {rows[i]['document_id'] for i in idx}&{rows[i]['document_id'] for i in a[second]}

def test_technical_test_features_never_learn_heldout_text_and_keep_negation_numbers():
    train=['technical_test bên thuê không trả 12345 đồng tiền thuê.','technical_test bên cho thuê phải sửa chữa.']
    unseen='technical_test exclusivelyheldouttoken'
    features=vector()
    features.fit(train)
    before=dict(features.vocabulary_)
    features.transform([unseen])
    assert before==features.vocabulary_ and 'exclusivelyheldouttoken' not in features.vocabulary_
    assert {'không','phải','12345'}<=set(before)
    assert 'đặt_cọc' in domain_tokenize('technical_test KHÔNG hoàn lại tiền đặt cọc 99999.')
    assert 'không' in domain_tokenize('Không hoàn lại đặt cọc.')

def test_experiment_grid_contains_classical_representations_and_no_fitted_models():
    models,config=rental_candidates()
    assert {'naive_bayes','logistic_regression','linear_svm'}<=set(c['algorithm'] for c in config.values())
    assert {'bow_unigram','bow_bigram','tfidf_unigram','tfidf_bigram'}<=set(c['representation'] for c in config.values())
    assert all(not hasattr(p.named_steps['classifier'],'classes_') for p in models.values())
