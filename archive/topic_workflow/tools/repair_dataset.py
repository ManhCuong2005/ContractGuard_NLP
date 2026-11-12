"""Repair source extraction before review, preserving all legacy candidates.

Writes version 2 separately. Duplicates/nonclauses go into a provenance ledger;
unresolved source reconstruction stays on the agent's worklist, not the user's
label confirmation sheet. Does not grant approval or train.
"""
from collections import Counter
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.annotation import ANNOTATION_FIELDS, LABEL_NAMES, REASONS, classify, prepare_text
from contractguard.dataset import FIELDS, read_json, read_rows, sha256, write_json, write_rows
from contractguard.provenance import locate_spans, verify_spans
from contractguard.text import normalize

EXTRA = ['parent_clause_id','source_spans','repair_kind','legacy_clause_id']


def clean_source_noise(text):
    """Remove known extraction boilerplate; evidence verification follows."""
    t = re.sub(r'Người tải:.*?Trang số:\s*\d+/\d+\s*',' ',text)
    t = re.sub(r'\b\d+(?:[./]\d+){2,4}[-–]BM/[A-Z0-9/.-]+\s+\d+/\d+\s+\d+/\d+',' ',t)
    t, note = prepare_text(t)
    return re.sub(r'\s+',' ',t).strip(),note


def split_sentences(text):
    # Period/semicolon followed by a new operative subject or conditional clause.
    return [s.strip() for s in re.split(
        r'(?<=[.;])\s+(?=(?:Bên [AB]|Các [Bb]ên|Hai [Bb]ên|Trong trường hợp|Trường hợp|Nếu |Mỗi [Bb]ên|Một [Bb]ên|Hợp [Đđ]ồng))',text) if s.strip()]


def intro_label(intro,heading):
    t = normalize(intro)
    if 'chấm dứt' in t or 'tạm ngừng' in t or 'tạm dừng' in t:
        return 'termination'
    if any(k in t for k in ['dữ liệu','thông tin mật','bảo mật','bí mật']):
        return 'confidentiality'
    if 'bất khả kháng' in t:
        return 'force_majeure'
    if 'thanh toán' in t or 'các khoản phí' in t:
        return 'payment'
    if 'định nghĩa' in normalize(heading) or 'giải thích từ ngữ' in normalize(heading):
        return 'other'
    return ''


def non_clause(text):
    t = normalize(text)
    if len(re.findall(r'\w+',t)) < 4:
        return True
    return bool(re.search(r'^(?:bên sử dụng dịch vụ:|bên cung cấp dịch vụ:|thông tin tàu cá|thông tin về chủ tàu|thông tin về thuyền trưởng|đặc điểm .*tàu cá|thiết bị giám sát và thông tin liên lạc|thông tin trung tâm|hỗ trợ kỹ thuật:|thông tin về người quản lý tên miền|địa chỉ lắp đặt|người tải:|: )',t)) or (
        not re.search(r'(phải|được|có quyền|nghĩa vụ|thỏa thuận|thoả thuận|cam kết)',t) and
        bool(re.search(r'(stt khoản mục|stt loại thiết bị|họ và tên: chức vụ:|số điện thoại.*số fax)',t)))


def main():
    rows = read_rows(ROOT/'data/review/clauses.csv')
    if any(r['review_status']!='pending' or r['reviewer'] or r['review_notes'] for r in rows):
        raise SystemExit('Human review found: preserve it and reconcile before creating a replacement version')
    sources = read_json(ROOT/'data/sources.json')
    manual = read_json(ROOT/'configs/repair_overrides.json')
    by_id = {r['clause_id']:r for r in rows}
    pages = {}
    for s in sources:
        if sha256(ROOT/s['raw_path'])!=s['source_sha256'] or sha256(ROOT/s['pages_path'])!=s['pages_sha256']:
            raise SystemExit('Source checksum changed')
        pages[s['document_id']] = read_json(ROOT/s['pages_path'])
    approval = (ROOT/'configs/approval.json').read_bytes()
    fixed, ledger, worklist, seen = [], [], [], {}
    parent = None

    def register(row,text,label,reason,kind,parent_row=None,suffix=''):
        doc = row['document_id']
        if not label:
            label,reason = classify(text,row['heading'])
        if not label:
            return False
        start = min(int(row['page_start']),int(parent_row['page_start']) if parent_row else int(row['page_start']))
        end = max(int(row['page_end']),int(parent_row['page_end']) if parent_row else int(row['page_end']))
        try:
            spans = locate_spans(text,pages[doc],start,end)
        except ValueError:
            return False
        key = normalize(text)
        if key in seen:
            ledger.append({'legacy_clause_id':row['clause_id'],'status':'duplicate_link',
                           'linked_clause_id':seen[key], 'reason':'Bản lặp được liên kết tới điều khoản chính; giữ nguyên nguồn và bản ứng viên.'})
            return True
        cid = row['clause_id']+suffix
        seen[key] = cid
        fixed.append({**row,'clause_id':cid,'text':text,'label':label,'review_status':'pending',
                      'reviewer':'','review_notes':'','annotation_status':'draft','proposed_action':'keep',
                      'annotation_by':'Codex — đã xử lý bản trích, chờ xác nhận nhãn',
                      'annotation_method':'source_repair_and_context_v2','annotation_reason':reason,
                      'annotation_flags':'','duplicate_of':'','original_text':row.get('original_text') or row['text'],
                      'text_preparation':kind,'parent_clause_id':parent_row['clause_id'] if parent_row else '',
                      'source_spans':json.dumps(spans,ensure_ascii=False),
                      'page_start':min(s['page'] for s in spans),'page_end':max(s['page'] for s in spans),
                      'repair_kind':kind,'legacy_clause_id':row['clause_id']})
        ledger.append({'legacy_clause_id':row['clause_id'],'status':'prepared',
                       'linked_clause_id':cid,'reason':kind})
        return True

    for row in rows:
        original = row.get('original_text') or row['text']
        text,note = clean_source_noise(original)
        context = (row['document_id'],row['heading'])
        if parent and (parent['document_id'],parent['heading'])!=context:
            parent=None
        correction=manual.get(row['clause_id'])
        if correction:
            if correction.get('technical_only'):
                ledger.append({'legacy_clause_id':row['clause_id'],'status':'source_nonclause',
                               'linked_clause_id':'','reason':correction['reason']})
                continue
            patched=text
            if correction.get('remove_regex'):
                if not re.search(correction['remove_regex'],patched):
                    raise ValueError('Expected source noise not found: '+row['clause_id'])
                patched=re.sub(correction['remove_regex'],' ',patched)
                patched=re.sub(r'\s+',' ',patched).strip()
            if correction.get('parts'):
                for i,part in enumerate(correction['parts'],1):
                    match=re.search(part['extract_regex'],patched)
                    if not match:
                        raise ValueError('Expected operative sentence not found: '+row['clause_id'])
                    excerpt=(part.get('prefix','')+' '+match.group(1)).strip()
                    if not register(row,excerpt,part['label'],part['reason'],'agent_split_from_source',suffix=f'_r{i:02d}'):
                        raise ValueError('Repaired sentence not verified against source: '+row['clause_id'])
                continue
            if correction.get('extract_regex'):
                match=re.search(correction['extract_regex'],patched)
                if not match:
                    raise ValueError('Manual excerpt no longer matches: '+row['clause_id'])
                patched=match.group(1)
            parent_rows=[by_id[k] for k in correction.get('parent_ids',[])]
            prefix=' '.join(clean_source_noise(r.get('original_text') or r['text'])[0] for r in parent_rows)
            if correction.get('source_prefix_regex'):
                for page_number,page_text in enumerate(pages[row['document_id']],1):
                    match=re.search(correction['source_prefix_regex'],page_text)
                    if match:
                        prefix=match.group(1)
                        parent_rows=[{**row,'clause_id':row['document_id']+'_source_context',
                                      'page_start':str(page_number),'page_end':str(page_number)}]
                        break
                else:
                    raise ValueError('Manual source context not found')
            if prefix:
                patched=prefix+' '+patched
            if register(row,patched,correction['label'],correction['reason'],'agent_source_correction',
                        parent_rows[0] if parent_rows else None):
                continue
            raise ValueError('Manual source repair failed verification: '+row['clause_id'])
        if non_clause(text):
            ledger.append({'legacy_clause_id':row['clause_id'],'status':'source_nonclause',
                           'linked_clause_id':'','reason':'Biểu mẫu/định danh/tiêu đề được giữ trong nguồn, không phải đơn vị điều khoản.'})
            continue
        if text.endswith(':'):
            parent={**row,'text':text}
            ledger.append({'legacy_clause_id':row['clause_id'],'status':'context_intro',
                           'linked_clause_id':'','reason':'Câu dẫn được dùng làm ngữ cảnh ghép với các mục con, không bỏ khỏi nguồn.'})
            continue
        reason_old=row.get('annotation_reason','')
        needs_context=(not row.get('label') and any(k in reason_old for k in ['liệt kê','câu dẫn','cần ghép','phụ thuộc','thiếu đoạn dẫn','thiếu cơ chế','thiếu phần quy định','chủ thể','ngữ cảnh']))
        if needs_context and parent:
            combined=parent['text']+' '+text
            label=intro_label(parent['text'],row['heading'])
            if register(row,combined,label,'Ghép câu dẫn gốc với mục con để khôi phục chủ thể/cơ chế. '+REASONS.get(label,''),
                        'restore_list_context',parent):
                continue
        split_requested=any(k in reason_old for k in ['cần tách','Cần tách','Gộp','gộp']) or len(text)>2000
        if split_requested:
            parts=split_sentences(text)
            if len(parts)>1:
                success=True
                for i,part in enumerate(parts,1):
                    label,why=classify(part,row['heading'])
                    if not register(row,part,label,'Tách nguyên văn theo câu/cơ chế: '+why,'split_operative_sentences',suffix=f'_s{i:02d}'):
                        success=False
                        worklist.append({'legacy_clause_id':row['clause_id'],'text':part,'reason':'Cần đọc lại nguồn để hoàn thiện phần còn lại sau tách.'})
                if success or any(r['legacy_clause_id']==row['clause_id'] for r in fixed):
                    continue
        # Retain previously reasoned labels unless the row was rejected solely for extraction.
        label=row.get('label','')
        why=row.get('annotation_reason','')
        if row.get('duplicate_of') or not label:
            label,why=classify(text,row['heading'])
        if register(row,text,label,why,'clean_page_material' if note or text!=original else 'retain_source_clause'):
            continue
        # Small complete cross-reference clauses are valid `other`, not broken lists.
        if re.search(r'^(Các (quyền|nghĩa vụ)|Các (quyền|nghĩa vụ)|Chi trả tiền lương|Hoàn toàn chịu trách nhiệm)',text):
            if register(row,text,'other','Nghĩa vụ/quyền vận hành hoặc dẫn chiếu chung ngoài 7 nhãn chuyên biệt.','restore_general_obligation'):
                continue
        worklist.append({'legacy_clause_id':row['clause_id'],'text':text,
                         'reason':'Agent cần xử lý tiếp từ nguồn; không yêu cầu người dùng duyệt loại.'})
        ledger.append({'legacy_clause_id':row['clause_id'],'status':'agent_repair_pending','linked_clause_id':'',
                       'reason':'Đang xử lý, chưa đưa vào bản xác nhận nhãn và chưa xóa dữ liệu.'})
    path=ROOT/'data/review/v2/clauses.csv'
    write_rows(path,fixed,FIELDS+ANNOTATION_FIELDS+EXTRA)
    write_json(ROOT/'reports/repair_ledger.json',ledger)
    write_json(ROOT/'reports/agent_repair_worklist.json',worklist)
    summary={'version':'v2','total_legacy_candidates':len(rows),'prepared_clauses':len(fixed),
             'legacy_handling':dict(Counter(r['status'] for r in ledger)),
             'repair_kinds':dict(Counter(r['repair_kind'] for r in fixed)),
             'kept_labels':dict(Counter(r['label'] for r in fixed)),
             'agent_worklist':len(worklist),'dataset_sha256':sha256(path),
             'human_accepted':0,'official_training_performed':False}
    write_json(ROOT/'reports/annotation_review_v2.json',{'rows':fixed,'label_names':LABEL_NAMES,'summary':summary})
    assert (ROOT/'configs/approval.json').read_bytes()==approval
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
