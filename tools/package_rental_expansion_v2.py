"""Package only explicit reviewed-source decisions into a new draft; never grant approval."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import json
import re
import csv
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,read_rows,sha256,write_json,write_rows,audit_dataset
from contractguard.provenance import verify_clause_spans
from contractguard.text import normalize
from package_rental_dataset import contextualize,exact_key,grams,Union,PRESERVED,RISK_CODES
from rental_expansion_annotations_v2 import DECISIONS,HOLDS,SOURCE_REVIEWS,CANDIDATE_SHA256,FAMILY_OVERRIDES,BODY_LINE_LIMITS

BASE=ROOT/'data/rental_expansion_v2'
OUTPUT=ROOT/'data/clauses_rental_v2.csv'


def package():
    approval=BASE/'approval.json'
    if approval.exists() and read_json(approval).get('dataset_approved'):
        raise ValueError('Expansion already approved; preserve it and create a new version.')
    assert sha256(BASE/'candidates.json')==CANDIDATE_SHA256
    for path,digest in PRESERVED.items():assert sha256(ROOT/path)==digest,path
    accepted=ROOT/'data/rental_approved_v1/clauses.csv'
    assert sha256(accepted)=='19d7554f2b27a754c570ffbb9b8a58dc75a5a053dfa3b5d593717c9541c4c442'
    pool=read_json(BASE/'candidates.json')
    sources={s['document_id']:s for s in read_json(BASE/'candidate_sources.json')}
    extension_hashes={}
    for p in sorted(BASE.glob('candidates_extension_*.json')):
        number=p.stem.rsplit('_',1)[1]
        snapshot=read_json(BASE/f'extension_{number}_snapshot.json')
        assert sha256(p)==snapshot['candidate_sha256']
        extension_hashes[p.name]=sha256(p)
        pool.extend(read_json(p))
        sources.update({s['document_id']:s for s in read_json(BASE/f'sources_extension_{number}.json')})
    candidates={r['clause_id']:r for r in pool}
    assert len(candidates)==len(pool)
    missing=set(DECISIONS)-set(candidates)
    assert not missing,missing
    assert not set(DECISIONS)&set(HOLDS)
    pages={sid:read_json(ROOT/s['pages_path']) for sid,s in sources.items()}
    v1sources={s['document_id']:s for s in read_json(ROOT/'data/rental_approved_v1/sources.json')}
    allsources={**sources,**v1sources}
    rows=[]
    for old in read_rows(accepted):
        r=dict(old,annotation_status='draft',review_status='pending',reviewer='',reviewed_at='',
            verified_risk_label='',verified_category='',review_confirmation_record='',
            review_notes='Carried from genuinely approved v1; entire new expansion still awaits a separate user decision.',
            dataset_version='rental_v2_draft',row_origin='approved_v1_unchanged_text_and_label',
            inherited_approval_record='reports/rental_dataset_approval.json',
            inherited_group_id=old['group_id'])
        rows.append(r)
    for cid,d in DECISIONS.items():
        candidate=dict(candidates[cid])
        assert cid not in {r['clause_id'] for r in rows},cid
        sid=candidate['document_id']
        review=SOURCE_REVIEWS.get(candidate['contract_id'],SOURCE_REVIEWS.get(sid))
        if not review:raise ValueError('Source scope/role has not been explicitly reviewed: '+cid)
        source=sources[sid]
        assert sha256(ROOT/source['raw_path'])==source['source_sha256']
        assert sha256(ROOT/source['pages_path'])==source['pages_sha256']
        body_refs=[tuple(x) for x in json.loads(candidate['body_line_refs'])]
        retained=body_refs[:BODY_LINE_LIMITS.get(cid,len(body_refs))]
        if candidate['contract_id']=='v2_rentapartment_lease':
            # Source-reviewed bilingual headings from the following article were
            # accidentally appended to the preceding body; remove those lines.
            retained=[(p,line) for p,line in retained if not re.match(r'^Điều/Article\s+\d',pages[sid][p-1].splitlines()[line].strip())]
        if retained!=body_refs:
            removed=set(body_refs)-set(retained)
            candidate['source_line_refs']=json.dumps([x for x in json.loads(candidate['source_line_refs']) if tuple(x) not in removed])
            candidate['body_line_refs']=json.dumps(retained)
            candidate['clause_body']='\n'.join(pages[sid][p-1].splitlines()[line].strip() for p,line in retained)
            candidate['selection_repairs']=json.dumps(dict(method='source-line selection only, no paraphrase',
                removed_body_line_refs=sorted(removed),reason='Remove signatures or next-article headings from the operative unit.'),ensure_ascii=False)
        r=contextualize(candidate,d['context_clause_ids'],candidates,pages[sid])
        r.update(d)
        r.update({k:review[k] for k in ['domain','protected_party','rental_subtype','tenant_role']})
        r.update(context_clause_ids=json.dumps(d['context_clause_ids']),
            annotation_status='draft',review_status='pending',reviewer='',review_notes='',
            annotation_method='explicit_agent_source_reading',annotation_evidence=candidate['clause_body'],
            category=d['clause_type'],risk_label=d['label'],source=source['source_url'],
            label_reason=d['annotation_reason'],verified_risk_label='',verified_category='',
            review_priority=1 if d['label']=='abnormal' else 4,
            dataset_role='primary_residential_rental',proposed_action='keep',
            template_family=FAMILY_OVERRIDES.get(candidate['contract_id'],candidate['group_id']),inherited_group_id=candidate['group_id'],
            dataset_version='rental_v2_draft',row_origin='new_explicit_agent_annotation',inherited_approval_record='')
        if r['label']=='abnormal':
            assert set(r['risk_category'].split('|'))<=RISK_CODES
            assert normalize(r['risk_evidence']) in normalize(r['text']),cid
        verify_clause_spans(r,pages[sid])
        rows.append(r)
    unique=[]
    canonical={}
    canonical_text={}
    duplicates=[]
    for row in rows:
        key=exact_key(row['clause_body'])
        text_key=normalize(row['text'])
        if key in canonical or text_key in canonical_text:
            previous=canonical.get(key) or canonical_text[text_key]
            if previous['label']!=row['label']:raise ValueError('Duplicate-label conflict: '+row['clause_id']+' / '+previous['clause_id'])
            duplicates.append(dict(clause_id=row['clause_id'],canonical_clause_id=previous['clause_id'],
                document_id=row['document_id'],source_url=row['source_url'],source_sha256=row['source_sha256'],
                reason='Exact normalized body repetition; provenance kept, not counted again.'))
        else:
            canonical[key]=row
            canonical_text[text_key]=row
            unique.append(row)
    rows=unique
    union=Union([r['clause_id'] for r in rows])
    seen=defaultdict(dict)
    for row in rows:
        for name in ['document_id','template_family','inherited_group_id']:
            key=row.get(name)
            if not key:continue
            if key in seen[name]:union.join(row['clause_id'],seen[name][key])
            else:seen[name][key]=row['clause_id']
    # Duplicate lineage also connects source documents, even if their repeated body was removed.
    anchors={r['clause_id']:r for r in rows}
    for item in duplicates:
        sid=item['document_id']
        if sid in seen['document_id']:union.join(item['canonical_clause_id'],seen['document_id'][sid])
        else:seen['document_id'][sid]=item['canonical_clause_id']
    fingerprints=[grams(r['clause_body']) for r in rows]
    near=[]
    for i,row in enumerate(rows):
        a=fingerprints[i]
        if len(a)<15:continue
        for j in range(i):
            b=fingerprints[j]
            if len(b)<15 or min(len(a),len(b))/max(len(a),len(b))<.86:continue
            score=len(a&b)/len(a|b)
            if score>=.86:
                union.join(row['clause_id'],rows[j]['clause_id'])
                near.append(dict(left=rows[j]['clause_id'],right=row['clause_id'],trigram_jaccard=score,
                                 same_label=rows[j]['label']==row['label']))
    roots=sorted({union.find(r['clause_id']) for r in rows})
    groups={g:f'rental_v2_group_{i:03d}' for i,g in enumerate(roots,1)}
    for row in rows:row['group_id']=groups[union.find(row['clause_id'])]
    with (ROOT/'outputs/rental_mvp1b_v1/splits.csv').open(encoding='utf-8-sig',newline='') as handle:
        prior_splits={r['clause_id']:r['split'] for r in csv.DictReader(handle)}
    prior_groups={r['group_id'] for r in rows if r['row_origin'].startswith('approved')}
    for row in rows:
        row['prior_v1_split']=prior_splits.get(row['clause_id'],'not_used_in_v1')
        row['shares_group_with_v1']='yes' if row['group_id'] in prior_groups else 'no'
    rows.sort(key=lambda r:(int(r['review_priority']),r['document_id'],r['clause_id']))
    fields=list(read_rows(accepted)[0])
    for row in rows:
        for key in row:
            if key not in fields:fields.append(key)
    write_rows(OUTPUT,rows,fields)
    selected_sources=[]
    for sid in sorted({r['document_id'] for r in rows}):
        s=dict(allsources[sid],source_use_status='pending_dataset_and_source_review',
               domain='residential_rental',data_kind='public_contract_template',
               group_id=next(r['group_id'] for r in rows if r['document_id']==sid))
        selected_sources.append(s)
        assert sha256(ROOT/s['raw_path'])==s['source_sha256']
        assert sha256(ROOT/s['pages_path'])==s['pages_sha256']
        for r in rows:
            if r['document_id']==sid:verify_clause_spans(r,read_json(ROOT/s['pages_path']))
    write_json(BASE/'sources.json',selected_sources)
    write_json(BASE/'annotation_decisions.json',DECISIONS)
    write_json(BASE/'source_scope_reviews.json',SOURCE_REVIEWS)
    write_json(BASE/'exact_duplicate_lineage.json',duplicates)
    write_json(BASE/'near_duplicate_pairs.json',near)
    inherited={r['clause_id']:r for r in read_rows(accepted)}
    duplicate_ids={d['clause_id']:d for d in duplicates}
    ledger=[]
    for item in pool:
        cid=item['clause_id']
        if cid in inherited:
            entry=dict(action='carried_from_approved_v1',label=inherited[cid]['label'],
                reason='Actual v1 acceptance preserved; expansion as a whole is still pending.')
        elif cid in duplicate_ids:
            entry=dict(action='exact_duplicate_not_counted',label=DECISIONS[cid]['label'],
                canonical_clause_id=duplicate_ids[cid]['canonical_clause_id'],reason='Provenance retained in duplicate lineage.')
        elif cid in DECISIONS:entry=dict(action='annotated_draft',label=DECISIONS[cid]['label'],reason=DECISIONS[cid]['annotation_reason'])
        elif cid in HOLDS:entry=dict(action='needs_context',label='',reason=HOLDS[cid])
        else:entry=dict(action='reserve_unlabelled',label='',reason='No target label inferred.')
        ledger.append(dict(clause_id=cid,**entry))
    write_json(BASE/'annotation_ledger.json',ledger)
    audit=audit_dataset(OUTPUT,ROOT/'configs/rental_labels.json',BASE/'sources.json',ROOT)
    if audit['errors']:raise ValueError(audit['errors'])
    counts=Counter(r['label'] for r in rows)
    write_json(BASE/'approval.json',dict(dataset_approved=False,source_use_confirmed=False,
        approved_by='',approved_at='',criteria_approved=True,
        criteria_sha256=sha256(ROOT/'docs/LABELING_GUIDELINES.md'),
        dataset_sha256=sha256(OUTPUT),sources_sha256=sha256(BASE/'sources.json'),
        note='New version is not covered by v1 acceptance; no official fitting permitted.'))
    write_json(BASE/'review_snapshot.json',dict(dataset_path=OUTPUT.relative_to(ROOT).as_posix(),
        dataset_sha256=sha256(OUTPUT),candidate_sha256=CANDIDATE_SHA256,extension_sha256=extension_hashes,
        decision_module_sha256=sha256(ROOT/'tools/rental_expansion_annotations_v2.py'),
        packaging_script_sha256=sha256(Path(__file__)),
        sources_sha256=sha256(BASE/'sources.json'),criteria_sha256=sha256(ROOT/'docs/LABELING_GUIDELINES.md')))
    write_json(ROOT/'reports/rental_expansion_v2_audit.json',dict(
        recorded_at=datetime.now(timezone.utc).isoformat(),rows=len(rows),label_counts=dict(counts),
        inherited_v1_rows=sum(r['row_origin'].startswith('approved') for r in rows),
        newly_selected_rows=sum(r['row_origin'].startswith('new') for r in rows),
        explicit_new_decisions=len(DECISIONS),exact_repetitions_not_counted=len(duplicates),
        source_documents=len(selected_sources),leakage_groups=len(roots),candidate_pool=len(pool),
        hold_count=len(HOLDS),risk_category_counts=dict(Counter(code for r in rows if r['label']=='abnormal' for code in r['risk_category'].split('|'))),
        positive_groups=len({r['group_id'] for r in rows if r['label']=='abnormal'}),
        fresh_positive_groups_outside_v1=len({r['group_id'] for r in rows if r['label']=='abnormal' and r['shares_group_with_v1']=='no'}),
        target_total_minimum=1000,target_total_maximum=2000,target_abnormal=500,
        total_target_met=1000<=len(rows)<=2000,abnormal_target_met=counts['abnormal']>=500,
        dataset_approved=False,official_training_performed=False,synthetic_rows=0,
        provenance_audit=audit))
    print(json.dumps(dict(rows=len(rows),labels=counts,new_decisions=len(DECISIONS),duplicates=len(duplicates),
        new_unique=sum(r['row_origin'].startswith('new') for r in rows),target_abnormal_met=counts['abnormal']>=500),ensure_ascii=False))


if __name__=='__main__':package()
