"""Apply explicitly authored clause/context decisions; never infer a class.

The canonical CSV contains only finished agent drafts for user confirmation.
Unresolved source facts, nonclauses and duplicate lineage stay in the immutable
snapshot and internal decision ledger, not in the user's label review queue.
No approval flag, reviewer, raw source or approved rubric is changed.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import audit_dataset, read_json, read_rows, sha256, write_json, write_rows
from contractguard.provenance import verify_clause_spans
from contractguard.text import normalize

RISK_QUOTES = {
    '12':'Bên B không có trách nhiệm',
    '26':'không có trách nhiệm bồi thường và hoàn trả các khoản tiền',
    '110':'bất kỳ thông tin nào khác',
    '120':'Dữ liệu cá nhân đã được sử dụng phục vụ nghiên cứu',
    '121':'quy định nội bộ của Viettel',
    '141':'Viettel không chịu bất kỳ trách nhiệm pháp lý hoặc bồi thường',
    '155':'với điều kiện chấp nhận các rủi ro, thiệt hại',
    '177':'đồng nghĩa với việc đã đồng ý',
    '247':'Khi Bên B thay đổi chính sách',
    '285':'Khi Bên B thay đổi chính sách',
    '297':'không hạn chế số lần tự động gia hạn',
    '342':'Bên A không có bất kỳ phản hồi nào',
    '353':'Khi Bên B thay đổi chính sách',
    '365':'không có thông báo về việc chấm dứt dịch vụ thì được xem',
    '396':'Nhà đăng ký không chịu bất kỳ trách nhiệm nào liên quan.',
    '551':'miễn cho Techcombank mọi trách nhiệm liên quan',
    '552':'chịu hoàn toàn các rủi ro',
    '553':'vì bất cứ lý do nào',
    '599':'ảnh hưởng đến các quyền và lợi ích mong muốn',
    '656':'được xem là Khách Hàng đã đồng ý',
    '659':'được xem là Khách Hàng đã đồng ý',
    '669':('683','bất kể là lỗi của người lái Xe hay lỗi của một bên thứ ba khác'),
    '675':'không phải chịu bất kỳ trách nhiệm nào khác',
    '681':'theo thông báo bằng văn bản của Green Future',
    '683':'bất kể là lỗi của người lái Xe hay lỗi của một bên thứ ba khác',
    '687':'miễn trừ Green Future và Tài Xế',
    '695':'tại từng thời điểm',
    '703':'tùy thuộc vào quyết định của Green Future',
    '738':'Bên B không chịu bất cứ trách nhiệm gì.',
    '743':'có nguy cơ gây thiệt hại',
    '745':'các khoản lợi nhuận mà Bên A có thể được hưởng',
}
RISK_CATEGORIES={'unilateral_change','broad_liability','deemed_consent',
                 'automatic_renewal','termination_discretion','overbroad_data_use'}


def keys(spec):
    for part in spec.split(','):
        if re.fullmatch(r'\d+-\d+', part):
            start,end=map(int,part.split('-'))
            if start>end:
                raise ValueError('Reversed annotation index range')
            yield from map(str,range(start,end+1))
        else:
            if not re.fullmatch(r'\d+[a-z]?', part):
                raise ValueError('Invalid explicit annotation index')
            yield part


def load_notes(path):
    decisions={}
    for number,line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        spec,label,categories,reason,context=line.split('|')
        if label not in {'normal','abnormal','hold','exclude'} or not reason.strip():
            raise ValueError(f'Invalid manual decision at line {number}')
        cats=set(categories.split(',')) if categories else set()
        if not cats <= RISK_CATEGORIES or bool(cats) != (label=='abnormal'):
            raise ValueError(f'Risk category mismatch at line {number}')
        for key in keys(spec):
            if key in decisions:
                raise ValueError(f'Duplicate manual decision for {key}')
            decisions[key]={'decision':label,'risk_category':categories,'reason':reason,
                            'context':context,'notes_line':number}
    return decisions


def main():
    path=ROOT/'data/clauses.csv'
    approval_path=ROOT/'configs/approval.json'
    approval_bytes=approval_path.read_bytes()
    approval=read_json(approval_path)
    prep=read_json(ROOT/'configs/annotation_preparation.json')
    if approval.get('criteria_approved') is not True or approval.get('dataset_approved') is not False:
        raise ValueError('Need confirmed criteria and a still-unapproved dataset')
    if approval['criteria_sha256'] != sha256(ROOT/'docs/ANNOTATION_GUIDELINES.md') or prep['rubric_sha256'] != approval['criteria_sha256']:
        raise ValueError('Approved rubric changed; do not annotate a different version')
    if sha256(ROOT/prep['snapshot']) != prep['snapshot_sha256']:
        raise ValueError('Annotation snapshot changed')
    manifest_path=ROOT/'reports/risk_annotation_manifest.json'
    previous=read_json(manifest_path) if manifest_path.exists() else {}
    if sha256(path) not in {prep['snapshot_sha256'],previous.get('dataset_sha256')}:
        raise ValueError('Canonical dataset has changed since preparation; preserve and reconcile review work')
    if any(r['review_status']!='pending' or r['reviewer'] or r['review_notes'] for r in read_rows(path)):
        raise ValueError('User review work exists; do not overwrite it')
    notes_path=ROOT/'configs/risk_annotation_notes.tsv'
    decisions=load_notes(notes_path)
    prepared={str(r['index']):r for r in prep['rows']}
    if decisions.keys()!=prepared.keys():
        raise ValueError(f'Incomplete manual review: {sorted(prepared.keys()-decisions.keys())}')
    sources=read_json(ROOT/'data/sources.json')
    snapshot_rows=read_rows(ROOT/prep['snapshot'])
    pages={s['document_id']:read_json(ROOT/s['pages_path']) for s in sources}
    final=[]
    ledger=[]
    seen={}
    for key,item in prepared.items():
        decision=decisions[key]
        row={**item['source_row'],'text':item['text'],'source_text':item['source_text'],
             'text_repairs':json.dumps(item['text_repairs'],ensure_ascii=False),
             'text_repair_reference':json.dumps(item['reference'],ensure_ascii=False) if item['reference'] else '',
             'snapshot_index':key,'label':'','annotation_reason':decision['reason'],
             'risk_category':decision['risk_category'],'review_status':'pending','reviewer':'','review_notes':'',
             'annotation_by':'Codex — nhãn sơ bộ, chưa được người dùng duyệt',
             'annotation_method':'manual_clause_context_review_v1',
             'annotation_scope':'six_approved_risk_categories_only',
             'annotation_criteria_sha256':prep['rubric_sha256']}
        verify_clause_spans(row,pages[row['document_id']])
        record={'snapshot_index':key,'clause_id':row['clause_id'],
                'snapshot_clause_id':snapshot_rows[int(re.match(r'\d+',key).group())]['clause_id'],
                'decision':decision['decision'],'reason':decision['reason'],
                'source_text_sha256':item['source_text_sha256'],
                'text_sha256':hashlib.sha256(row['text'].encode('utf-8')).hexdigest()}
        if decision['decision'] in {'hold','exclude'}:
            row.update(annotation_status='needs_context' if decision['decision']=='hold' else 'non_training_material',
                       context_required='true' if decision['decision']=='hold' else 'false',
                       proposed_action=decision['decision'])
            ledger.append({**record,'row':row})
            continue
        row.update(label=decision['decision'],annotation_status='draft',context_required='false',proposed_action='keep')
        context_ids=[]
        context_pages=set()
        for part in decision['context'].split(','):
            if not part:
                continue
            if re.fullmatch(r'p\d+(?:-p\d+)?',part):
                nums=list(map(int,re.findall(r'\d+',part)))
                context_pages.update(range(nums[0],nums[-1]+1))
            else:
                for target in keys(part):
                    if target not in prepared:
                        raise ValueError(f'Unknown context reference: {key} -> {target}')
                    other=prepared[target]['source_row']
                    context_ids.append(other['clause_id'])
        if any(not 1<=p<=len(pages[row['document_id']]) for p in context_pages):
            raise ValueError('Context page outside document')
        row['context_clause_ids']=json.dumps(context_ids,ensure_ascii=False)
        row['context_source_pages']=json.dumps(sorted(context_pages))
        row['risk_evidence']=''
        if row['label']=='abnormal':
            evidence=RISK_QUOTES[key]
            evidence_key,quote=evidence if isinstance(evidence,tuple) else (key,evidence)
            if normalize(quote) not in normalize(prepared[evidence_key]['text']):
                raise ValueError(f'Risk quote not found verbatim: {key}')
            row['risk_evidence']=json.dumps({'clause_id':prepared[evidence_key]['clause_id'],'quote':quote},ensure_ascii=False)
        normalized=normalize(row['text'])
        if normalized in seen:
            canonical=seen[normalized]
            if row['label']!=canonical['label'] or row['risk_category']!=canonical['risk_category']:
                raise ValueError('Identical text has conflicting contextual annotations; reconcile manually')
            row.update(annotation_status='duplicate_link',proposed_action='duplicate')
            ledger.append({**record,'decision':'duplicate','retained_clause_id':canonical['clause_id'],'row':row})
            continue
        seen[normalized]=row
        final.append(row)
        ledger.append(record)
    fields=list(dict.fromkeys(list(read_rows(ROOT/prep['snapshot'])[0])+[k for row in final for k in row]))
    temporary=path.with_name('clauses.annotation_staging.csv')
    write_rows(temporary,final,fields)
    quality=audit_dataset(temporary,ROOT/'configs/labels.json',ROOT/'data/sources.json',ROOT)
    if quality['errors']:
        raise ValueError(f'Prepared dataset failed integrity audit: {quality["errors"][:10]}')
    if approval_path.read_bytes()!=approval_bytes:
        raise ValueError('Approval was changed during annotation')
    temporary.replace(path)
    write_json(ROOT/'reports/risk_annotation_ledger.json',ledger)
    manifest={'purpose':'agent_draft_annotations_for_user_review_not_ground_truth',
              'prepared_at':datetime.now(timezone.utc).isoformat(),'canonical_dataset':'data/clauses.csv',
              'dataset_sha256':sha256(path),'criteria_sha256':prep['rubric_sha256'],
              'snapshot':prep['snapshot'],'snapshot_sha256':prep['snapshot_sha256'],
              'notes_sha256':sha256(notes_path),'preparation_sha256':sha256(ROOT/'configs/annotation_preparation.json'),
              'original_candidates':len(snapshot_rows),'prepared_units':len(prepared),'review_rows':len(final),
              'draft_label_counts':dict(Counter(r['label'] for r in final)),
              'decisions':dict(Counter(r['decision'] for r in ledger)),
              'risk_category_counts':dict(Counter(c for r in final for c in r['risk_category'].split(',') if c)),
              'per_source':dict(Counter(r['document_id'] for r in final)),
              'sources_sha256':sha256(ROOT/'data/sources.json'),
              'approval_sha256_unchanged':sha256(approval_path),
              'dataset_approved':False,'official_training_performed':False,'official_metrics':None}
    write_json(manifest_path,manifest)
    print(json.dumps({k:manifest[k] for k in ['original_candidates','prepared_units','review_rows','draft_label_counts','decisions']},ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
