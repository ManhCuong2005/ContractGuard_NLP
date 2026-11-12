"""Populate actual draft labels and exclusion reasons, keeping approval pending."""
from collections import Counter
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.annotation import ANNOTATION_FIELDS, LABEL_NAMES, classify, prepare_text
from contractguard.dataset import FIELDS, read_json, read_rows, sha256, write_json, write_rows
from contractguard.text import normalize


def annotate(rows, sources, overrides):
    pages = {s['document_id']:read_json(ROOT/s['pages_path']) for s in sources}
    seen = {}
    result = []
    for row in rows:
        if row['review_status'] != 'pending' or row['reviewer'] or row['review_notes']:
            raise ValueError('Human review work found; do not overwrite it')
        if row['label'] and row.get('annotation_status') != 'draft':
            raise ValueError('Existing label has no agent draft marker; do not overwrite')
        original = row.get('original_text') or row['text']
        text, preparation = prepare_text(original)
        label, reason = classify(text, row['heading'])
        correction = overrides.get(row['clause_id'])
        method = 'local_context_rules_v1'
        if correction:
            label, reason = correction['label'], correction['reason']
            method = 'codex_context_correction_v1'
        flags = []
        source = normalize(' '.join(pages[row['document_id']][int(row['page_start'])-1:int(row['page_end'])]))
        if normalize(text) not in source:
            label, reason = '', 'Trích đoạn không liền mạch trong trang nguồn; cần ghép lại nguyên văn trước khi dùng huấn luyện.'
            flags.append('source_span_mismatch')
        if len(text) > 2000:
            label, reason = '', 'Đoạn dài trên 2.000 ký tự có nhiều nội dung/biểu mẫu; cần tách lại trước khi sử dụng.'
            flags.append('long_or_mixed_span')
        if 'Người tải:' in text:
            label, reason = '', 'Chân trang/thông tin người tải xen giữa nội dung; cần trích lại đoạn liên tục sạch từ nguồn.'
            flags.append('embedded_page_metadata')
        if len(text) > 1200:
            flags.append('long_clause')
        if preparation:
            flags.append('trimmed_trailing_material')
        if any('\ue000' <= c <= '\uf8ff' for c in text):
            flags.append('pdf_symbol')
        # An item may have a proposed class even when it duplicates a retained item.
        action, duplicate = ('keep' if label else 'exclude'), ''
        key = normalize(text)
        if key in seen:
            canonical = seen[key]
            duplicate = canonical['clause_id']
            label = canonical['label']
            action = 'exclude'
            reason = f'Trùng nguyên văn sau chuẩn hóa với {duplicate}; giữ bản đầu, đề xuất loại bản lặp.'
            flags.append('duplicate')
        else:
            seen[key] = {'clause_id':row['clause_id'], 'label':label}
        if not label:
            flags.append('not_a_standalone_labelled_clause')
        result.append({**row, 'text':text, 'label':label, 'review_status':'pending',
                       'reviewer':'', 'review_notes':'', 'annotation_status':'draft',
                       'annotation_by':'Codex — nhãn sơ bộ, chưa được người dùng duyệt',
                       'annotation_method':method, 'annotation_reason':reason,
                       'proposed_action':action, 'annotation_flags':','.join(flags),
                       'duplicate_of':duplicate, 'original_text':original,
                       'text_preparation':preparation})
    return result


def main():
    path = ROOT/'data/review/clauses.csv'
    rows = read_rows(path)
    approval_path = ROOT/'configs/approval.json'
    approval_before = approval_path.read_bytes()
    backup = path.parent/'backups'/'before_draft_labels_utf8.csv'
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copyfile(path, backup)
    corrections_path = ROOT/'configs/annotation_corrections.json'
    corrections = read_json(corrections_path) if corrections_path.exists() else {}
    annotated = annotate(rows, read_json(ROOT/'data/sources.json'), corrections)
    write_rows(path, annotated, FIELDS+ANNOTATION_FIELDS)
    kept = [r for r in annotated if r['proposed_action']=='keep']
    excluded = [r for r in annotated if r['proposed_action']=='exclude']
    export = {'rows':annotated, 'label_names':LABEL_NAMES,
              'summary':{'total':len(annotated), 'proposed_keep':len(kept), 'proposed_exclude':len(excluded),
                         'labelled_rows':sum(bool(r['label']) for r in annotated),
                         'unlabelable_excluded':sum(not r['label'] for r in excluded),
                         'kept_labels':dict(Counter(r['label'] for r in kept)),
                         'methods':dict(Counter(r['annotation_method'] for r in annotated)),
                         'human_accepted':0, 'official_training_performed':False,
                         'dataset_sha256':sha256(path)}}
    write_json(ROOT/'reports/annotation_review.json', export)
    # This workflow must never write or grant dataset approval.
    assert approval_path.read_bytes() == approval_before
    write_rows(ROOT/'data/review/labels_to_confirm.csv',
               [{'clause_id':r['clause_id'], 'text':r['text'],
                 'label':r['label'], 'nhan_tieng_viet':LABEL_NAMES[r['label']],
                 'ly_do':r['annotation_reason'], 'xac_nhan':'Chờ xác nhận',
                 'ghi_chu':'', 'source_url':r['source_url'],
                 'page_start':r['page_start'], 'page_end':r['page_end']} for r in kept],
               ['clause_id','text','label','nhan_tieng_viet','ly_do','xac_nhan','ghi_chu','source_url','page_start','page_end'])
    print(export['summary'])


if __name__ == '__main__':
    main()
