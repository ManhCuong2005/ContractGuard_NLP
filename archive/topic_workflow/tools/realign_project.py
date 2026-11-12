"""Correct project scope without inventing anomaly labels or granting approval.

The current binary label names are a proposal. Source clauses and their existing
topic annotations are retained, with topics explicitly separated from labels.
"""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import FIELDS,read_json,read_rows,sha256,write_json,write_rows


def main():
    archive=ROOT/'docs/history/clause_type_task'
    archive.mkdir(parents=True,exist_ok=True)
    for name,source in [('labels.json','configs/labels.json'),('approval.json','configs/approval.json'),
                        ('README.md','README.md'),('ANNOTATION_GUIDELINES.md','docs/ANNOTATION_GUIDELINES.md'),
                        ('ARCHITECTURE.md','docs/ARCHITECTURE.md')]:
        target=archive/name
        if not target.exists():
            target.write_bytes((ROOT/source).read_bytes())
    labels=read_json(ROOT/'configs/labels.json')
    old_approval=read_json(ROOT/'configs/approval.json')
    target=ROOT/'data/clauses.csv'
    if target.exists():
        raise SystemExit('Canonical anomaly CSV already exists; preserve it and reconcile deliberately')
    rows=read_rows(ROOT/'data/review/v2/clauses.csv')
    output=[]
    for r in rows:
        if r['review_status']!='pending' or r['reviewer'] or r['review_notes']:
            raise SystemExit('Review work found; reconcile before changing schema')
        output.append({**r,'clause_type':r['label'],'clause_type_reason':r['annotation_reason'],
                       'label':'','annotation_reason':'',
                       'annotation_status':'awaiting_anomaly_criteria',
                       'annotation_method':'not_yet_annotated_for_anomaly',
                       'review_status':'pending','reviewer':'','review_notes':'',
                       'proposed_action':'','is_anomaly':'','risk_category':'',
                       'context_required':'','task':'contract_anomaly_detection'})
    ordered=['clause_id','text','label','annotation_reason','review_status','clause_type',
             'clause_type_reason','risk_category','context_required','document_id','group_id',
             'source_url','source_sha256','page_start','page_end','source_spans',
             'heading','reviewer','review_notes','annotation_status','annotation_method',
             'annotation_by','original_text','text_preparation','legacy_clause_id','repair_kind',
             'parent_clause_id','task']
    write_rows(target,output,ordered)
    write_json(ROOT/'configs/labels.json',{
        'version':'2.0-draft','language':'vi','task':'contract_anomaly_detection',
        'labels':['normal','abnormal'],'status':'pending_anomaly_criteria_confirmation',
        'decision_unit':'clause_with_contract_context',
        'interpretation':'pending_user_clarification_risk_content_or_template_deviation',
        'auxiliary_field':'clause_type','auxiliary_labels':labels.get('labels',[]),
        'note':'Topic labels are not anomaly labels; unknown labels must remain unannotated.'})
    write_json(ROOT/'configs/approval.json',{
        'criteria_approved':False,'dataset_approved':False,'approved_by':'','approved_at':'',
        'criteria_sha256':'','labels_sha256':'','dataset_sha256':'','sources_sha256':'',
        'reviewed_source_ids':[],'source_use_confirmed':False,
        'scope':'contract_anomaly_detection',
        'previous_topic_confirmation_record':'docs/history/clause_type_task/approval.json',
        'note':'User clarified anomaly detection. Prior topic-label confirmation is preserved in history and does not approve anomaly criteria or dataset.'})
    write_json(ROOT/'reports/scope_realignment.json',{
        'task':'contract_anomaly_detection','canonical_dataset':'data/clauses.csv',
        'source_rows':len(rows),'preserved_rows':len(output),
        'texts_preserved':all(a['text']==b['text'] for a,b in zip(rows,output)),
        'source_ids_preserved':all(a['clause_id']==b['clause_id'] for a,b in zip(rows,output)),
        'anomaly_labels_populated':sum(bool(r['label']) for r in output),
        'auxiliary_topic_labels_populated':sum(bool(r['clause_type']) for r in output),
        'dataset_sha256':sha256(target),'official_training_performed':False,
        'reason':'Correcting mistaken topic classification objective; no topic-to-risk conversion.'})
    print(f'Preserved {len(output)} clauses in data/clauses.csv. Topic labels moved to clause_type; no anomaly labels invented.')


if __name__=='__main__':
    main()
