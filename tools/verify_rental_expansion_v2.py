"""Verify draft expansion files and actual technical test results, without fitting."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from contractguard.dataset import audit_dataset, read_json, read_rows, require_approval, sha256, write_json
from contractguard.profiles import profile_paths
from package_rental_dataset import PRESERVED, exact_key
from contractguard.text import normalize


def main():
    base = ROOT / 'data/rental_expansion_v2'
    data = ROOT / 'data/clauses_rental_v2.csv'
    rows = read_rows(data)
    snapshot = read_json(base / 'review_snapshot.json')
    assert sha256(data) == snapshot['dataset_sha256']
    for path, key in [(base / 'candidates.json','candidate_sha256'),
                      (base / 'sources.json','sources_sha256'),
                      (ROOT / 'tools/rental_expansion_annotations_v2.py','decision_module_sha256'),
                      (ROOT / 'tools/package_rental_expansion_v2.py','packaging_script_sha256')]:
        assert sha256(path) == snapshot[key]
    for name,digest in snapshot['extension_sha256'].items():
        assert sha256(base / name) == digest
    audit = audit_dataset(data, ROOT / 'configs/rental_labels.json', base / 'sources.json', ROOT)
    assert not audit['errors']
    assert len({normalize(r['text']) for r in rows}) == len(rows)
    assert len({exact_key(r['clause_body']) for r in rows}) == len(rows)
    assert all(r['annotation_status'] == 'draft' and r['review_status'] == 'pending' and not r['reviewer'] for r in rows)
    previous = {r['clause_id']:r for r in read_rows(ROOT / 'data/rental_approved_v1/clauses.csv')}
    index = {r['clause_id']:r for r in rows}
    assert all((index[cid]['text'],index[cid]['label']) == (r['text'],r['label']) for cid,r in previous.items())
    for name,digest in PRESERVED.items():
        assert sha256(ROOT / name) == digest
    paths = profile_paths(ROOT,'rental')
    assert sha256(paths['dataset']) == '19d7554f2b27a754c570ffbb9b8a58dc75a5a053dfa3b5d593717c9541c4c442'
    precommit = read_json(ROOT / 'outputs/rental_mvp1b_v1/precommit.json')
    for name,digest in precommit['experiment_config']['code_sha256'].items():
        assert sha256(ROOT / 'src/contractguard' / name) == digest
    refusals = {}
    for name, approval, sources in [('v1_approval',paths['approval'],paths['sources']),
                                    ('v2_pending_approval',base / 'approval.json',base / 'sources.json')]:
        try:
            require_approval(data, approval, paths['rubric'], paths['labels'], sources, ROOT)
        except ValueError as exc:
            refusals[name] = str(exc)
        else:
            raise AssertionError('Unapproved expansion passed '+name)
    report_snapshot = read_json(base / 'report_snapshot.json')
    assert report_snapshot['dataset_sha256'] == sha256(data)
    assert report_snapshot['report_sha256'] == sha256(ROOT / 'reports/RENTAL_EXPANSION_V2_REVIEW.md')
    assert report_snapshot['data_card_sha256'] == sha256(ROOT / 'docs/RENTAL_V2_DATA_CARD.md')
    collection = read_json(base / 'collection_manifest.json')
    for source in collection:
        assert sha256(ROOT / source['raw_path']) == source['source_sha256']
        assert sha256(ROOT / source['pages_path']) == source['pages_sha256']
    suites = list(ET.parse(ROOT / 'reports/rental-v2-test-results.xml').getroot().iter('testsuite'))
    tests = {key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','errors','failures','skipped']}
    assert tests['tests'] >= 110 and tests['errors'] == tests['failures'] == tests['skipped'] == 0
    pip = subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True,check=True)
    counts = Counter(r['label'] for r in rows)
    result = dict(verified_at=datetime.now(timezone.utc).isoformat(),dataset_path='data/clauses_rental_v2.csv',
        dataset_sha256=sha256(data),rows=len(rows),label_counts=dict(counts),
        technical_tests=tests,dependency_check=pip.stdout.strip(),source_provenance_errors=audit['provenance']['errors'],
        selected_source_documents=len(read_json(base / 'sources.json')),new_parsed_source_records=len(collection),
        inherited_v1_rows=len(previous),old_text_and_labels_preserved=True,protected_hashes_unchanged=True,
        training_code_matches_v1_precommit=True,approval_refusals=refusals,
        exact_text_and_body_duplicates=0,dataset_approved=False,new_model_fitted=False,
        official_v2_quality_metrics_available=False,total_target_met=1000<=len(rows)<=2000,
        abnormal_target_met=counts['abnormal']>=500,
        note='Integrity and technical checks only. No independent label-accuracy estimate, dataset acceptance or model-quality claim.')
    write_json(ROOT / 'reports/rental_expansion_v2_verification.json',result)
    print('Verified',len(rows),'draft rows;',tests['tests'],'technical tests; target abnormal met:',result['abnormal_target_met'])


if __name__ == '__main__':
    main()
