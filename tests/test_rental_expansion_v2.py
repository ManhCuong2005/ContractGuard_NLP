"""Expansion integrity and approval boundaries, never an NLP quality evaluation."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import csv
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from contractguard.dataset import audit_dataset, read_json, read_rows, require_approval, sha256
from contractguard.profiles import profile_paths
from contractguard.provenance import verify_clause_spans
from contractguard.text import normalize
from package_rental_dataset import exact_key, PRESERVED
from rental_clause_assembly_v2 import assemble
from rental_expansion_annotations_v2 import DECISIONS, HOLDS, SOURCE_REVIEWS

BASE = ROOT / 'data/rental_expansion_v2'
DATA = ROOT / 'data/clauses_rental_v2.csv'


def test_expansion_inherits_every_accepted_text_label_without_forging_acceptance():
    old = {r['clause_id']: r for r in read_rows(ROOT / 'data/rental_approved_v1/clauses.csv')}
    rows = read_rows(DATA)
    inherited = {r['clause_id']: r for r in rows if r['row_origin'].startswith('approved')}
    assert set(old) == set(inherited)
    for cid, before in old.items():
        after = inherited[cid]
        assert (before['text'], before['label']) == (after['text'], after['label'])
        assert after['inherited_approval_record'] == 'reports/rental_dataset_approval.json'
    for row in rows:
        assert row['annotation_status'] == 'draft' and row['review_status'] == 'pending'
        assert not any(row.get(k) for k in ['reviewer', 'reviewed_at', 'verified_risk_label',
                                         'verified_category', 'review_confirmation_record'])
        assert row['label'] == row['risk_label'] and row['category'] == row['clause_type']
        assert row['annotation_reason'] == row['label_reason']
        assert row['annotation_reason'] and row['annotation_evidence']


def test_expansion_cannot_borrow_v1_or_pending_approval():
    paths = profile_paths(ROOT, 'rental')
    with pytest.raises(ValueError, match='digest mismatch'):
        require_approval(DATA, paths['approval'], paths['rubric'], paths['labels'], paths['sources'], ROOT)
    with pytest.raises(ValueError, match='dataset_approved'):
        require_approval(DATA, BASE / 'approval.json', paths['rubric'], paths['labels'], BASE / 'sources.json', ROOT)
    approval = read_json(BASE / 'approval.json')
    assert approval['dataset_approved'] is False and approval['source_use_confirmed'] is False
    assert not approval['approved_by'] and not approval['approved_at']


def test_expansion_every_retained_span_and_source_digest_is_verifiable():
    result = audit_dataset(DATA, ROOT / 'configs/rental_labels.json', BASE / 'sources.json', ROOT)
    assert not result['errors'] and not result['provenance']['errors']
    sources = {s['document_id']: s for s in read_json(BASE / 'sources.json')}
    for source in sources.values():
        assert sha256(ROOT / source['raw_path']) == source['source_sha256']
        assert sha256(ROOT / source['pages_path']) == source['pages_sha256']
    pages = {sid: read_json(ROOT / s['pages_path']) for sid, s in sources.items()}
    for row in read_rows(DATA):
        verify_clause_spans(row, pages[row['document_id']])
        if row['label'] == 'abnormal':
            assert normalize(row['risk_evidence']) in normalize(row['text'])


def test_expansion_only_explicit_decisions_enter_and_reserve_has_no_target_label():
    rows = read_rows(DATA)
    pool = read_json(BASE / 'candidates.json')
    for path in sorted(BASE.glob('candidates_extension_*.json')):
        pool.extend(read_json(path))
    index = {r['clause_id']: r for r in pool}
    assert len(index) == len(pool) and all(not r['label'] for r in pool)
    assert not set(DECISIONS) & set(HOLDS)
    for row in rows:
        if not row['row_origin'].startswith('new'):
            continue
        decision = DECISIONS[row['clause_id']]
        assert row['label'] == decision['label']
        assert row['contract_id'] in SOURCE_REVIEWS or row['document_id'] in SOURCE_REVIEWS
        for cid in json.loads(row['context_clause_ids']):
            assert index[cid]['contract_id'] == row['contract_id']
            assert index[cid]['document_id'] == row['document_id']
    selected = {r['clause_id'] for r in rows}
    ledger = read_json(BASE / 'annotation_ledger.json')
    assert {r['clause_id'] for r in ledger} == set(index)
    for entry in ledger:
        if entry['action'] in {'reserve_unlabelled', 'needs_context'}:
            assert not entry['label'] and entry['clause_id'] not in selected


def test_expansion_duplicates_link_template_groups_and_never_increase_counts():
    rows = read_rows(DATA)
    index = {r['clause_id']: r for r in rows}
    assert len({normalize(r['text']) for r in rows}) == len(rows)
    assert len({exact_key(r['clause_body']) for r in rows}) == len(rows)
    by_doc = defaultdict(set)
    for row in rows:
        by_doc[row['document_id']].add(row['group_id'])
    assert all(len(groups) == 1 for groups in by_doc.values())
    duplicates = read_json(BASE / 'exact_duplicate_lineage.json')
    assert duplicates
    for duplicate in duplicates:
        assert duplicate['clause_id'] not in index and duplicate['canonical_clause_id'] in index
        if duplicate['document_id'] in by_doc:
            assert index[duplicate['canonical_clause_id']]['group_id'] in by_doc[duplicate['document_id']]
    assert by_doc['v2_attachment_6e5afb9b6dda'] == by_doc['acc_room_actual']


def test_expansion_audit_reports_real_shortfall_and_v1_test_exposure():
    rows = read_rows(DATA)
    audit = read_json(ROOT / 'reports/rental_expansion_v2_audit.json')
    counts = Counter(r['label'] for r in rows)
    assert audit['rows'] == len(rows) and audit['label_counts'] == counts
    assert audit['total_target_met'] == (1000 <= len(rows) <= 2000)
    assert audit['abnormal_target_met'] == (counts['abnormal'] >= 500)
    assert not audit['official_training_performed'] and audit['synthetic_rows'] == 0
    with (ROOT / 'outputs/rental_mvp1b_v1/splits.csv').open(encoding='utf-8-sig', newline='') as handle:
        splits = {r['clause_id']: r['split'] for r in csv.DictReader(handle)}
    seen_groups = {r['group_id'] for r in rows if r['clause_id'] in splits}
    for row in rows:
        assert row['prior_v1_split'] == splits.get(row['clause_id'], 'not_used_in_v1')
        assert row['shares_group_with_v1'] == ('yes' if row['group_id'] in seen_groups else 'no')


def test_expansion_snapshot_and_immutable_history_still_match():
    snapshot = read_json(BASE / 'review_snapshot.json')
    for key, path in [('dataset_sha256', DATA), ('candidate_sha256', BASE / 'candidates.json'),
                      ('sources_sha256', BASE / 'sources.json'),
                      ('decision_module_sha256', ROOT / 'tools/rental_expansion_annotations_v2.py'),
                      ('packaging_script_sha256', ROOT / 'tools/package_rental_expansion_v2.py')]:
        assert sha256(path) == snapshot[key]
    for name, digest in snapshot['extension_sha256'].items():
        assert sha256(BASE / name) == digest
    for name, digest in PRESERVED.items():
        assert sha256(ROOT / name) == digest
    assert sha256(ROOT / 'data/rental_approved_v1/clauses.csv') == '19d7554f2b27a754c570ffbb9b8a58dc75a5a053dfa3b5d593717c9541c4c442'
    precommit = read_json(ROOT / 'outputs/rental_mvp1b_v1/precommit.json')
    for name, digest in precommit['experiment_config']['code_sha256'].items():
        assert sha256(ROOT / 'src/contractguard' / name) == digest


@pytest.mark.parametrize('fmt', ['pdf', 'html', 'docx'])
def test_technical_test_expansion_preserves_role_intro_and_skips_invisible_lines(fmt):
    pages = ['Điều 3. Quyền và nghĩa vụ\n3.1. Quyền và nghĩa vụ của Bên A\n● Bàn giao phòng.\n\u200b\n3.2. Quyền và nghĩa vụ của Bên B\n● Sử dụng phòng để ở.']
    source = dict(document_id='technical_test', format=fmt, source_url='https://example.test/technical_test', source_sha256='0' * 64)
    rows, _ = assemble(dict(contract='technical_test', family='technical_test', subtype='technical_test'), source, pages)
    assert len(rows) == 2 and all(not r['label'] for r in rows)
    assert 'Bên A' in rows[0]['text'] and 'Bên B' in rows[1]['text']
    assert 'Bên A' not in rows[1]['text']
    assert all(r['clause_body'].strip() != '\u200b' for r in rows)
    for row in rows:
        verify_clause_spans(row, pages)


def test_offline_reader_defaults_remain_v1_and_new_positive_filter_works():
    command = [sys.executable, '-X', 'utf8', str(ROOT / 'tools/review_rental_dataset.py')]
    old = subprocess.run(command + ['--count', '0'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True)
    assert 'Matching 517;' in old.stdout
    new = subprocess.run(command + ['--data', str(DATA), '--origin', 'new', '--label', 'abnormal', '--count', '10'],
                         cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True)
    expected = sum(r['label'] == 'abnormal' and r['row_origin'].startswith('new') for r in read_rows(DATA))
    assert f'Matching {expected};' in new.stdout and 'Source:' in new.stdout and 'Reason:' in new.stdout
