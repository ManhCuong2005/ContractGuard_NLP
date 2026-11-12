"""Package a source-verified, explicitly annotated rental review dataset.

This is an MVP 1A data tool. It never fits a predictor, grants approval, changes
the legacy corpus, or includes unassigned candidates as normal.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,read_rows,sha256,write_json,write_rows
from contractguard.provenance import verify_clause_spans
from contractguard.text import normalize
from rental_annotation_decisions import DECISIONS,CANDIDATE_SNAPSHOT_SHA256

BASE=ROOT/'data/rental_mvp1a_v1'
OUTPUT=ROOT/'data/clauses_rental_v1.csv'
CRITERIA='68a1d9c068637c942e4c4c44648f299431960d64c01d1654652fc23f13c1a9fa'
RISK_CODES={'deposit_forfeiture','unilateral_change','termination_discretion',
    'broad_liability','repair_burden','access_interference','deemed_consent',
    'automatic_renewal','overbroad_data_use'}
PRESERVED={
 'data/clauses.csv':'4a259465d17d3c4d9c4b5a836c9a5c05083b5a5c592014fb4fc11ca9e94fd3c6',
 'configs/approval.json':'64976df19fe52979607a557a5582d226dbf6fe3acf9dc5cf6584cde7ebd51419',
 'docs/LABELING_GUIDELINES.md':CRITERIA,
 'docs/ANNOTATION_GUIDELINES.md':'ef0596c0ead897ff3a5d178b6b7801abd24a772e4b8270f8936ca3a64e7330f8',
}
HOLDS={
 'sadeco_worker_0004':'Minimum annual increase/owner notice must be read with Article 5 requiring both parties to sign a price annex; not forced abnormal.',
 'sadeco_worker_0008':'Deposit return deductions require resolving costs/remedies in 3.2; not auto-normal from a stated refund.',
 'sadeco_worker_0028':'Return/repainting clause must be reconciled with fault-limited repairs 3.1; natural-wear responsibility not unambiguous.',
 'sadeco_worker_0029':'Compensation merely on a notice depends on internal rules/amounts not provided.',
 'resident_apartment_0007':'Open allocation of taxes/charges; needs a narrower, unambiguous financial scope before a binary label.',
 'resident_apartment_0021':'Original says return to tenant B, not landlord A; substantive source ambiguity, not silently corrected.',
 'resident_apartment_0026':'Compensation amount is incomplete in the original.',
 'thuecanho123_apartment_0016':'Original says before the first five days; timing ambiguity in source, cannot silently replace before with after.',
 'thuecanho123_apartment_0037':'Deposit loss on early departure must be reconciled with 8.6 breach exception; compensation exemption does not explicitly settle deposit.',
 'homedy_room_full_0024':'Broad loss wording conflicts with fault-limited 2.1; no forced label.',
 'roomi_registration_0005':'General compliance condition for refund does not alone establish arbitrary forfeiture.',
 'roomi_registration_0038':'Generic breach termination requires additional procedural scope; not labelled from termination keyword.',
 'roomi_registration_0059':'Automatic liquidation on either-party breach lacks settled consequences/context.',
 'bandon_room_0018':'Read with compensation and room replacement at 3.A.3/4; no isolated arbitrary-termination label.',
 'bandon_room_0019':'Alternative room/refund in upstream owner cancellation; prepaid-rent treatment not specified.',
 'bandon_room_0023':'Notice-linked deposit loss is not automatically arbitrary under approved criteria.',
 'bandon_room_0028':'Original-condition return wording requires reconciling natural wear and fault-limited return 6.5.',
 'sunshine_longterm_0076':'Tax gross-up versus owner tax responsibility 7.3 requires financial-context adjudication.',
}
LEGACY_AUX={
 'viettel_stracking_2026_0202','viettel_tv_personal_0075','fpt_internet_0072',
 'fpt_domain_legacy_0031','fpt_server_legacy_0033','fpt_phone_business_0045',
 'moj_transport_template_0054',
}

def exact_key(text):
    value=normalize(text)
    value=re.sub(r'^(?:điều\s+\d+[.:]?\s*|\d+(?:\.\d+)*[.)]?\s+|[-–+•]\s*|\(?[a-zđ]\)[ ]*)','',value)
    return value.strip(' ;.\n')

def grams(text):
    words=re.findall(r'\w+',normalize(text))
    return {tuple(words[i:i+3]) for i in range(len(words)-2)}

class Union:
    def __init__(self,keys):self.parent={k:k for k in keys}
    def find(self,a):
        while self.parent[a]!=a:
            self.parent[a]=self.parent[self.parent[a]]
            a=self.parent[a]
        return a
    def join(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:self.parent[max(a,b)]=min(a,b)

def contextualize(row,context_ids,candidates,pages):
    """Use the union of real source spans in reading order, without invented prose."""
    refs=set(tuple(r) for r in read_json_value(row['source_line_refs']))
    for cid in context_ids:
        context=candidates[cid]
        if context['contract_id']!=row['contract_id']:
            raise ValueError(f'Cross-contract context: {cid}')
        refs.update(tuple(r) for r in read_json_value(context['source_line_refs']))
    parts=[]
    spans=[]
    for p,line in sorted(refs):
        lines=pages[p-1].splitlines()
        value=lines[line].strip()
        before=normalize('\n'.join(lines[:line]))
        start=len(before)+bool(before)
        spans.append(dict(page=p,start=start,end=start+len(normalize(value))))
        parts.append(value)
    updated=dict(row,text='\n'.join(parts),source_text='\n'.join(parts),
        source_spans=json.dumps(spans,ensure_ascii=False),source_line_refs=json.dumps(sorted(refs)),
        page_start=min(p for p,_ in refs),page_end=max(p for p,_ in refs))
    verify_clause_spans(updated,pages)
    return updated

def read_json_value(value):return json.loads(value)

def package():
    if read_json(ROOT/'configs/rental_approval.json').get('dataset_approved'):
        raise ValueError('Rental dataset already accepted; preserve the reviewed draft and use data/rental_approved_v1. Create a new reviewed version for changes.')
    for name,digest in PRESERVED.items():
        if sha256(ROOT/name)!=digest:raise ValueError(f'Protected input changed: {name}')
    if sha256(BASE/'candidates.json')!=CANDIDATE_SNAPSHOT_SHA256:
        raise ValueError('Candidate snapshot changed; recheck explicit source decisions before packaging.')
    candidates_list=read_json(BASE/'candidates.json')
    candidates={r['clause_id']:r for r in candidates_list}
    sources={s['document_id']:s for s in read_json(BASE/'candidate_sources.json')}
    missing=set(DECISIONS)-set(candidates)
    if missing:raise ValueError(f'Decisions without current candidate: {sorted(missing)}')
    pages={k:read_json(ROOT/s['pages_path']) for k,s in sources.items()}
    for source in sources.values():
        for name,key in [('raw_path','source_sha256'),('pages_path','pages_sha256')]:
            if sha256(ROOT/source[name])!=source[key]:raise ValueError(f'Source hash mismatch: {source["document_id"]}')
        if source.get('transcription_proof_path'):
            proof_path=ROOT/source['transcription_proof_path']
            if sha256(proof_path)!=source['transcription_proof_sha256']:
                raise ValueError('Visual transcription proof changed')
            proof=read_json(proof_path)
            if proof['source_sha256']!=source['source_sha256'] or proof['pages_sha256']!=source['pages_sha256']:
                raise ValueError('Visual transcription not bound to these raw/pages')
            for render in proof['rendered_pages']:
                if sha256(ROOT/render['image_path'])!=render['sha256']:
                    raise ValueError('Scan render proof changed')
    rows=[]
    ledger=[]
    for candidate in candidates_list:
        cid=candidate['clause_id']
        if cid in HOLDS:
            ledger.append(dict(clause_id=cid,action='hold',label='',reason=HOLDS[cid]))
            continue
        decision=DECISIONS.get(cid)
        if decision is None:
            ledger.append(dict(clause_id=cid,action='reserve_unlabelled',label='',reason='Not selected in curated v1; no target label inferred. Original source and candidate remain available.'))
            continue
        row=contextualize(candidate,decision['context_clause_ids'],candidates,pages[candidate['document_id']])
        row.update(decision)
        row['context_clause_ids']=json.dumps(decision['context_clause_ids'])
        row['template_family']=row['group_id']
        row['tenant_role']='Bên B (bên thuê); đối chiếu phần định nghĩa các bên của nguồn'
        if row['contract_id'] in {'gov_residential','homedy_student','sunshine_longterm'}:
            row['tenant_role']='Bên Thuê (định danh theo nguồn, không suy từ chữ A/B)'
        row['annotation_status']='draft'
        row['review_status']='pending'
        row['reviewer']=''
        row['proposed_action']='keep'
        row['dataset_role']='primary_residential_rental'
        row['annotation_method']='explicit_agent_source_reading'
        row['risk_evidence']=decision.get('risk_evidence','')
        row['annotation_evidence']=candidate['clause_body']
        row['category']=row['clause_type']
        row['risk_label']=row['label']
        row['source']=row['source_url']
        row['label_reason']=row['annotation_reason']
        row['verified_risk_label']=''
        row['verified_category']=''
        row['review_priority']=1 if row['label']=='abnormal' and row['label_confidence']=='medium' else (2 if row['label']=='abnormal' else 4)
        if cid in {'gov_residential_0056','resident_room_0015','roomi_registration_0036',
            'roomi_registration_0037','roomi_registration_0046','roomi_registration_0052',
            'sunshine_longterm_0033','sunshine_longterm_0084','minhkhue_house_0012',
            'thuecanho123_apartment_0031','troxanh_room_0014'}:
            row['review_priority']=3
        if row['risk_evidence'] and normalize(row['risk_evidence']) not in normalize(row['text']):
            raise ValueError(f'Risk quotation not found in assembled text: {cid}')
        ledger.append(dict(clause_id=cid,action='annotated_draft',label=row['label'],reason=row['annotation_reason']))
        rows.append(row)
    # Exact body repetitions add provenance, not additional training samples.
    seen={}
    unique=[]
    duplicates=[]
    for row in rows:
        key=exact_key(row['clause_body'])
        if key in seen:
            previous=seen[key]
            if previous['label']!=row['label']:
                raise ValueError(f'Exact duplicate label conflict: {row["clause_id"]}')
            duplicates.append(dict(clause_id=row['clause_id'],canonical_clause_id=previous['clause_id'],
                source_url=row['source_url'],source_sha256=row['source_sha256'],reason='Exact normalized body repetition; provenance retained.'))
        else:
            seen[key]=row
            unique.append(row)
    rows=unique
    rows.sort(key=lambda r:(r['review_priority'],r['contract_id'],r['clause_id']))
    # Conservative leakage components, no learned text representation.
    union=Union([r['clause_id'] for r in rows])
    doc,families={},{}
    for row in rows:
        for key,index in [(row['document_id'],doc),(row['template_family'],families)]:
            if key in index:union.join(row['clause_id'],index[key])
            else:index[key]=row['clause_id']
    fingerprints=[grams(r['clause_body']) for r in rows]
    near=[]
    for i,row in enumerate(rows):
        a=fingerprints[i]
        if len(a)<15:continue
        for j in range(i):
            b=fingerprints[j]
            if len(b)<15 or min(len(a),len(b))/max(len(a),len(b))<.86:continue
            similarity=len(a&b)/len(a|b)
            if similarity>=.86:
                union.join(row['clause_id'],rows[j]['clause_id'])
                near.append(dict(left=rows[j]['clause_id'],right=row['clause_id'],word_trigram_jaccard=round(similarity,5),same_label=rows[j]['label']==row['label']))
    roots=sorted({union.find(r['clause_id']) for r in rows})
    group_names={root:f'rental_leakage_{i:03d}' for i,root in enumerate(roots,1)}
    for row in rows:row['group_id']=group_names[union.find(row['clause_id'])]
    fields=list(rows[0])
    # Put review-relevant columns first; full evidence follows, in the same CSV.
    front=['clause_id','text','label','clause_type','risk_category','annotation_reason',
           'risk_evidence','label_confidence','review_status','annotation_status','tenant_role',
           'contract_id','document_id','template_family','group_id','context_clause_ids']
    fields=front+[f for f in fields if f not in front]
    write_rows(OUTPUT,rows,fields)
    write_json(BASE/'annotation_decisions.json',DECISIONS)
    write_json(BASE/'annotation_ledger.json',ledger)
    write_json(BASE/'exact_duplicate_lineage.json',duplicates)
    write_json(BASE/'near_duplicate_pairs.json',near)
    selected_sources=[]
    for document in sorted({r['document_id'] for r in rows}):
        subset=[r for r in rows if r['document_id']==document]
        s=dict(sources[document])
        s.update(group_id=subset[0]['group_id'],contract_ids=sorted({r['contract_id'] for r in subset}),
            template_families=sorted({r['template_family'] for r in subset}),
            public_access_verified=True,redistribution_license='not_established',
            source_use_review_status='pending',dataset_review_status='pending',
            source_kind='public_unexecuted_template',
            note='Publicly readable template; not proof of an executed lease, legal validity, or open redistribution licence.')
        selected_sources.append(s)
    write_json(BASE/'sources.json',selected_sources)
    legacy_audit()
    integrity=verify_package(rows,selected_sources)
    stats=statistics(rows,ledger,duplicates,near)
    write_json(ROOT/'reports/rental_dataset_audit.json',{**stats,**integrity,
        'dataset_path':OUTPUT.relative_to(ROOT).as_posix(),'dataset_sha256':sha256(OUTPUT),
        'sources_path':'data/rental_mvp1a_v1/sources.json','sources_sha256':sha256(BASE/'sources.json'),
        'criteria_sha256':CRITERIA,'human_dataset_approved':False,'official_training_run':False,
        'generated_at_utc':datetime.now(timezone.utc).isoformat()})
    snapshot={name:sha256(ROOT/name) for name in [
        'data/clauses_rental_v1.csv','data/rental_mvp1a_v1/sources.json',
        'data/rental_mvp1a_v1/annotation_decisions.json','data/rental_mvp1a_v1/candidates.json',
        'configs/rental_contracts_v1.json','tools/rental_annotation_decisions.py']}
    write_json(BASE/'review_snapshot.json',dict(files=snapshot,status='pending_user_dataset_review',criteria_sha256=CRITERIA))
    acquisition_audit()
    print(json.dumps({**stats,**integrity},ensure_ascii=False,indent=2))

def verify_package(rows,sources):
    source_map={s['document_id']:s for s in sources}
    verified=0
    for row in rows:
        assert row['label'] in {'normal','abnormal'} and row['annotation_reason']
        assert row['annotation_status']=='draft' and row['review_status']=='pending' and not row['reviewer']
        assert row['annotation_criteria_sha256']==CRITERIA
        assert row['domain']=='residential_rental'
        assert row['label']!='abnormal' or (row['risk_category'] and row['risk_evidence'])
        verify_clause_spans(row,read_json(ROOT/source_map[row['document_id']]['pages_path']))
        verified+=1
    assert len({r['clause_id'] for r in rows})==len(rows)
    assert len({normalize(r['text']) for r in rows})==len(rows)
    assert len(read_rows(OUTPUT))==len(rows)
    for name,digest in PRESERVED.items():assert sha256(ROOT/name)==digest
    approval=read_json(ROOT/'configs/rental_approval.json')
    assert approval['criteria_approved'] and not approval['dataset_approved']
    assert not approval['source_use_confirmed']
    return dict(verified_source_spans=verified,raw_and_pages_hashes_verified=True,
        visually_transcribed_rows=sum(source_map[r['document_id']].get('extractor')=='agent_visual_selected_transcription' for r in rows),
        visual_transcription_note='For scanned sources, spans match the visually checked selected transcription; they are not an independently extracted PDF text layer.',
        csv_utf8_bom_roundtrip=True,legacy_inputs_unchanged=True,
        dataset_gate_remains_closed=True,integrity_errors=[])

def statistics(rows,ledger,duplicates,near):
    by_source={}
    for doc in sorted({r['document_id'] for r in rows}):
        subset=[r for r in rows if r['document_id']==doc]
        by_source[doc]=dict(Counter(r['label'] for r in subset))
    groups={}
    for gid in sorted({r['group_id'] for r in rows}):
        subset=[r for r in rows if r['group_id']==gid]
        groups[gid]=dict(counts=dict(Counter(r['label'] for r in subset)),
            documents=sorted({r['document_id'] for r in subset}))
    risk_counts=Counter(c for r in rows for c in r['risk_category'].split('|') if c)
    all_codes=RISK_CODES
    counts=Counter(r['label'] for r in rows)
    positive_groups=sum(g['counts'].get('abnormal',0)>0 for g in groups.values())
    return dict(rows=len(rows),draft_label_counts=dict(counts),
        abnormal_fraction=round(counts['abnormal']/len(rows),5),
        source_documents=len(by_source),contract_templates=len({r['contract_id'] for r in rows}),
        template_families=len({r['template_family'] for r in rows}),leakage_groups=len(groups),
        abnormal_source_documents=sum(v.get('abnormal',0)>0 for v in by_source.values()),
        abnormal_leakage_groups=positive_groups,risk_category_counts=dict(risk_counts),
        missing_abnormal_categories=sorted(set(all_codes)-set(risk_counts)),
        clause_type_counts=dict(Counter(r['clause_type'] for r in rows)),
        by_source=by_source,by_leakage_group=groups,
        candidate_count=len(ledger),candidate_decisions=dict(Counter(r['action'] for r in ledger)),
        exact_duplicates_not_counted=len(duplicates),near_duplicate_pair_count=len(near),
        near_pairs_with_different_labels=sum(not p['same_label'] for p in near),
        split_preflight=dict(no_split_committed=True,no_fitting=True,
            positive_groups_available=positive_groups,
            three_way_positive_group_minimum_met=positive_groups>=3,
            warning='Minimum group count is not evidence of adequate support; no performance claim. Source concentration and missing risk categories remain material.'))

def legacy_audit():
    legacy=read_rows(ROOT/'data/clauses.csv')
    auxiliary=[]
    decisions=[]
    for row in legacy:
        cid=row['clause_id']
        reuse=cid in LEGACY_AUX
        decisions.append(dict(clause_id=cid,document_id=row['document_id'],
            primary_rental_eligible=False,disposition='auxiliary_only' if reuse else 'retain_legacy_out_of_domain',
            reason='Original provenance is a service/transport/bank/vehicle template, not residential rental; no domain relabelling.'))
        if reuse:
            a=dict(row)
            a.update(dataset_role='auxiliary_only',domain='legacy_non_residential',
                label='normal',annotation_status='draft',review_status='pending',reviewer='',
                annotation_reason='Đã đọc: thương lượng rồi cơ quan có thẩm quyền/Tòa án; không tước quyền phản đối. Câu hoàn toàn chung nhưng nguồn ngoài miền nên chỉ phụ trợ, không vào train/test thuê nhà chính.',
                clause_type='dispute_resolution',risk_category='',tenant_role='not_applicable',
                included_in_primary_rental='false',proposed_action='auxiliary_only')
            auxiliary.append(a)
    assert len(legacy)==752 and len(auxiliary)==7
    write_rows(BASE/'legacy_auxiliary.csv',auxiliary,list(auxiliary[0]))
    write_json(BASE/'legacy_selection_audit.json',dict(legacy_rows=len(legacy),
        primary_rental_reused=0,auxiliary_only_reused=len(auxiliary),
        other_rows_retained_in_legacy=len(legacy)-len(auxiliary),decisions=decisions))

def acquisition_audit():
    catalog=read_json(BASE/'collection_manifest.json')
    downloaded={s['document_id']:s for s in catalog}
    attempts={}
    for path in sorted((ROOT/'configs').glob('rental_collection_v*.json')):
        for spec in read_json(path):attempts[spec['document_id']]=spec
    result=[]
    selected={s['document_id'] for s in read_json(BASE/'sources.json')}
    reasons={
        'acc_room':'Title says room rental, operative Article 1 explicitly says commercial premises for a clothing shop; excluded from residential primary.',
        'sadeco_worker_individual_pdf':'Operator public worker-residential template; six-page scan recovered by visually checked selected transcription with image/raw/page hashes, not discarded for absent text layer.',
        'acc_room_actual':'Different URL from acc_room; this template explicitly leases a residential room. Selected draft rows, not copied commercial wording.',
        'acc_room_bilingual':'Purpose/office-business electricity wording is ambiguous; no automatic conversion into a residential lease.',
        'cochinh_compilation_pdf':'Anthology mixes house/foreigner/apartment with office, headquarters and social rent-to-own. Only scoped candidates; no anthology-wide label.',
        'enha_room':'Only public three-article preview; renewal duration blank and full exceptions unavailable in visible contract. Guidance is not a substitute contract.',
        'danang_house_simple_docx':'Operative clauses explicitly discuss tenant business activity; not selected as a residential source.',
        'danang_house_docx':'Near copy of Minh Khue ten-article residential template; retained for lineage/reserve, not extra independent support.',
        'danang_house2_docx':'Copy of simple-house legacy template, including same 30-day vacancy risk; not an additional independent abnormal family.',
        'danang_room_docx':'Copy of the notary house/room template; retained as source lineage, not extra independent support.',
        'benri_house':'Filled illustrative identities/example contract; not selected as an authentic anonymous rental clause source.',
        'quanlynhatro_room':'Fetched page redirects to app guidance, not the contract suggested by the search snippet.',
        'akihome_room':'Advice about what a contract should contain; not converted into operative contractual obligations.',
        'roomi_room':'Advice, not the full operative template selected from the separate registration page.',
        'omnistay_room':'Advice/checklist, not an executed contract or complete operative template.',
        'locloc_index':'Risk explanations and cautions are not taken as authentic quoted contract clauses.',
        'nhatrobieu_rules':'Republished first-person rental rules; provenance/attachment to a contract not established. Not primary.',
        'huit_rental_index':'Index points to legacy .doc; no extraction of this binary format was claimed.',
        'congchung6_index':'Download index for legacy .doc files; no extraction of those binaries was claimed.',
    }
    for key,spec in sorted(attempts.items()):
        result.append(dict(document_id=key,url=spec['url'],
            downloaded=key in downloaded,selected_in_primary=key in selected,
            status='included_draft' if key in selected else ('discovery_or_reserve' if key in downloaded else 'unavailable_network_or_http'),
            raw_sha256=downloaded.get(key,{}).get('source_sha256',''),
            reason=reasons.get(key,'Selected clauses were checked by scope and context; other bytes remain discovery/reserve, not automatically labelled. No access restrictions bypassed.')))
    write_json(BASE/'acquisition_ledger.json',dict(attempted_sources=len(attempts),downloaded_sources=len(catalog),
        unavailable_sources=len(set(attempts)-set(downloaded)),sources=result))

if __name__=='__main__':package()
