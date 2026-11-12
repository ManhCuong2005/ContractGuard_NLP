"""Record the actual chat acceptance and freeze the approved rental dataset.

User confirmation: Dataset thuê nhà Đạt. Run once for this exact reviewed v1.
This does not approve future edits, external redistribution or MVP 2.
"""
from datetime import datetime,timezone,timedelta
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,read_rows,write_json,write_rows,sha256,audit_dataset

def main():
    approval_path=ROOT/'configs/rental_approval.json'
    before=read_json(approval_path)
    destination=ROOT/'data/rental_approved_v1'
    if destination.exists() or before.get('dataset_approved'):
        raise ValueError('Acceptance already recorded or destination exists; preserve and inspect it.')
    snapshot=read_json(ROOT/'data/rental_mvp1a_v1/review_snapshot.json')
    for relative,digest in snapshot['files'].items():
        if sha256(ROOT/relative)!=digest:
            raise ValueError(f'Reviewed snapshot changed: {relative}')
    if not before['criteria_approved'] or sha256(ROOT/'docs/LABELING_GUIDELINES.md')!=before['criteria_sha256']:
        raise ValueError('Accepted criteria version does not match')
    draft=ROOT/'data/clauses_rental_v1.csv'
    sources_path=ROOT/'data/rental_mvp1a_v1/sources.json'
    rows=read_rows(draft)
    sources=read_json(sources_path)
    audit=audit_dataset(draft,ROOT/'configs/rental_labels.json',sources_path,ROOT)
    if audit['errors'] or len(rows)!=517:
        raise ValueError(f'Reviewed dataset integrity failed: {audit["errors"]}')
    destination.mkdir()
    shutil.copyfile(approval_path,destination/'approval_before_acceptance.json')
    shutil.copyfile(draft,destination/'reviewed_draft.csv')
    shutil.copyfile(sources_path,destination/'reviewed_draft_sources.json')
    shutil.copyfile(ROOT/'data/rental_mvp1a_v1/review_snapshot.json',destination/'review_snapshot.json')
    recorded=datetime.now(timezone(timedelta(hours=7))).isoformat()
    for row in rows:
        if row['review_status']!='pending' or row['annotation_status']!='draft':
            raise ValueError('Unexpected prior row review status')
        row.update(review_status='accepted',annotation_status='reviewed',reviewer='user_in_chat',
            verified_risk_label=row['label'],verified_category=row['clause_type'],
            review_notes='User accepted the presented dataset in chat: Dataset thuê nhà Đạt',
            reviewed_at=recorded,review_confirmation_record='reports/rental_dataset_approval.json')
    for source in sources:
        source.update(source_use_review_status='accepted_for_local_academic_experiment',
            dataset_review_status='accepted',review_confirmation_record='reports/rental_dataset_approval.json')
    accepted_path=destination/'clauses.csv'
    accepted_sources=destination/'sources.json'
    write_rows(accepted_path,rows,list(rows[0]))
    write_json(accepted_sources,sources)
    record=dict(decision='accepted',confirmation_quote='Dataset thuê nhà Đạt',confirmed_by='user_in_chat',
        reviewer_name_supplied=False,recorded_at=recorded,
        timestamp_note='Recording time; not a claim of exact chat-message timestamp.',
        decision_scope='Presented rental v1 dataset, labels and listed public sources for local academic MVP 1B experiments',
        scope='contract_anomaly_detection',domain='residential_rental',protected_party='tenant',
        reviewed_draft_sha256=sha256(draft),reviewed_draft_sources_sha256=sha256(sources_path),
        approved_dataset_path=accepted_path.relative_to(ROOT).as_posix(),approved_dataset_sha256=sha256(accepted_path),
        approved_sources_path=accepted_sources.relative_to(ROOT).as_posix(),approved_sources_sha256=sha256(accepted_sources),
        criteria_sha256=before['criteria_sha256'],labels_sha256=before['labels_sha256'],
        row_count=len(rows),labels_changed=0,texts_changed=0,
        official_training_authorized=True,
        authorization_basis='User accepted after the immediately preceding explanation that Dataset Đạt advances to MVP 1B training/evaluation.',
        external_redistribution_authorized=False,mvp2_authorized=False,
        limitations_acknowledged='Only 28 abnormal; three risk mechanisms missing; public templates and scanned selected transcription limitations remain.')
    write_json(ROOT/'reports/rental_dataset_approval.json',record)
    current=dict(before,dataset_approved=True,source_use_confirmed=True,
        approved_by='user_in_chat',approved_at=recorded,
        dataset_sha256=sha256(accepted_path),sources_sha256=sha256(accepted_sources),
        dataset_path=record['approved_dataset_path'],sources_path=record['approved_sources_path'],
        reviewed_source_ids=sorted(s['document_id'] for s in sources),
        dataset_confirmation_record='reports/rental_dataset_approval.json',
        dataset_confirmation_quote='Dataset thuê nhà Đạt',
        approval_record_sha256=sha256(ROOT/'reports/rental_dataset_approval.json'),
        reviewed_draft_sha256=sha256(draft),official_training_authorized=True,
        note='Actual user chat acceptance recorded for this frozen rental dataset only; original draft, legacy data and historical approval are preserved.')
    write_json(approval_path,current)
    write_json(destination/'approval.json',current)
    print('Frozen accepted rental snapshot:',len(rows),'rows; no labels or texts changed.')

if __name__=='__main__':main()
