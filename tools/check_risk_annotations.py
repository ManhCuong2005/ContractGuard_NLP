"""Read-only integrity and support checks, plus a Markdown label-review guide.

No model fitting, label inference, approval update or official metrics.
"""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import audit_dataset, leakage_groups, read_json, read_rows, sha256, write_json
from contractguard.training import split_rows
from contractguard.text import normalize


def main():
    dataset=ROOT/'data/clauses.csv'
    rows=read_rows(dataset)
    manifest=read_json(ROOT/'reports/risk_annotation_manifest.json')
    approval=read_json(ROOT/'configs/approval.json')
    if sha256(dataset)!=manifest['dataset_sha256']:
        raise ValueError('Dataset changed since draft annotation; reconcile before generating the review guide')
    if sha256(ROOT/'configs/risk_annotation_notes.tsv')!=manifest['notes_sha256']:
        raise ValueError('Manual annotation notes changed since the draft build')
    if sha256(ROOT/'configs/annotation_preparation.json')!=manifest['preparation_sha256']:
        raise ValueError('Source preparation changed since the draft build')
    quality=audit_dataset(dataset,ROOT/'configs/labels.json',ROOT/'data/sources.json',ROOT)
    if quality['errors']:
        raise ValueError(f'Source/annotation audit failed: {quality["errors"][:5]}')
    if any(not r['label'] or not r['annotation_reason'] or r['annotation_status']!='draft'
           or r['review_status']!='pending' or r['reviewer'] or r['review_notes'] for r in rows):
        raise ValueError('Review guide is only for a complete unreviewed agent draft')
    prepared={r['clause_id']:r for r in read_json(ROOT/'configs/annotation_preparation.json')['rows']}
    for row in rows:
        for context in json.loads(row['context_clause_ids']):
            if context not in prepared:
                raise ValueError('Missing preserved annotation context')
        if row['label']=='abnormal':
            evidence=json.loads(row['risk_evidence'])
            if normalize(evidence['quote']) not in normalize(prepared[evidence['clause_id']]['text']):
                raise ValueError('Risk evidence no longer matches its source clause')
    groups=leakage_groups(rows)
    independent={label:len({g for r,g in zip(rows,groups) if r['label']==label}) for label in ['normal','abnormal']}
    preflight={'purpose':'draft_partition_feasibility_only_not_a_model_experiment'}
    try:
        split,_,seed=split_rows(rows,['normal','abnormal'])
        preflight.update(feasible=True,seed=seed,counts={k:dict(Counter(rows[i]['label'] for i in v)) for k,v in split.items()})
    except ValueError as exc:
        preflight.update(feasible=False,blocker=str(exc))
    result={'purpose':'draft_dataset_integrity_not_label_accuracy_or_model_quality',
            'dataset_sha256':sha256(dataset),'criteria_sha256':manifest['criteria_sha256'],
            'rows':len(rows),'draft_label_counts':dict(Counter(r['label'] for r in rows)),
            'provenance':quality['provenance'],'source_groups':len(set(groups)),
            'independent_groups_by_label':independent,'draft_partition_preflight':preflight,
            'manual_annotation_coverage':manifest['prepared_units'],
            'source_boundary_repairs':len(read_json(ROOT/'reports/source_quality/structure_repairs.json')),
            'review_rows_with_text_repairs':sum(bool(json.loads(r['text_repairs'])) for r in rows),
            'font_glyph_repairs':sum(sum(e.get('kind')=='verified_legacy_font_glyph' for e in json.loads(r['text_repairs'])) for r in rows),
            'dataset_approved':approval['dataset_approved'],'official_training_performed':False,
            'official_metrics':None,'errors':[]}
    write_json(ROOT/'reports/draft_dataset_audit.json',result)
    lines=[
        '# Duyệt dataset rủi ro — bản gán nhãn sơ bộ 1', '',
        '**File cần xem: [data/clauses.csv](../data/clauses.csv).** Đây là nhãn do agent chuẩn bị, chưa phải ground truth được duyệt.', '',
        f"Bản hiện tại có **{len(rows)} điều khoản: {result['draft_label_counts']['normal']} normal và {result['draft_label_counts']['abnormal']} abnormal**. Tất cả review_status=pending, annotation_status=draft; reviewer để trống.", '',
        '## Cách xác nhận', '',
        'Đọc text, label và annotation_reason trong CSV chính. Với abnormal, xem thêm risk_category và risk_evidence; source_url, trang và source_spans dùng đối chiếu nguồn, context_clause_ids/context_source_pages chỉ rõ ngữ cảnh đã đọc.', '',
        '- Nếu đồng ý bộ nhãn của bản này, trả lời trong chat: **Dataset Đạt**.',
        '- Nếu còn mục chưa phù hợp, trả lời **Chưa đạt**, nêu clause_id và điểm chưa phù hợp; agent sửa và gửi lại. Bạn không cần tự nhập nhãn mới hoặc sửa cấu hình.',
        '- Không dùng Excel nhãn chủ đề trong archive. Không cần duyệt hay sửa danh sách lỗi kỹ thuật/đề xuất loại.', '',
        'Xác nhận áp dụng cho đúng bản CSV và các nguồn mẫu hợp đồng công khai được liệt kê tại data/sources.json. Chưa có quyền dùng nội dung này để khẳng định độ an toàn pháp lý của hợp đồng.', '',
        f"SHA256 CSV: `{manifest['dataset_sha256']}`. Tiêu chí bạn đã duyệt giữ nguyên SHA256 `{manifest['criteria_sha256']}`.", '',
        f"## Vì sao từ {manifest['original_candidates']} ứng viên còn {len(rows)} điều khoản duyệt?", '',
        f"{manifest['original_candidates']} ứng viên ban đầu được giữ nguyên byte trong snapshot. Sửa cấu trúc tạo {manifest['prepared_units']} đơn vị để theo dõi: giữ {len(rows)} đơn vị có nhãn, liên kết {manifest['decisions']['duplicate']} bản trùng sau sửa Unicode/khoảng trắng, giữ riêng {manifest['decisions']['exclude']} bảng/metadata hoặc bản lặp gộp, và tạm giữ {manifest['decisions']['hold']} trường hợp chưa đủ dữ kiện nguồn (ví dụ giá trị chưa điền hoặc điều khoản dẫn chiếu chưa có đúng phiên bản). Không dùng lỗi bộ trích làm lý do loại điều khoản hợp lệ.", '',
        f"Không xóa nguồn và không ép các trường hợp chưa đủ căn cứ thành normal. Tất cả {manifest['original_candidates']} ứng viên và các đơn vị được tách thêm đều có nhật ký nội bộ; người dùng chỉ duyệt tập đã chuẩn bị xong trong CSV chính.", '',
        '## Những điều khoản được cảnh báo', '',
        'Bảng dưới hỗ trợ đọc nhanh; nội dung đầy đủ và các dòng normal nằm trong CSV chính. Một điều khoản có thể có nhiều nhóm dấu hiệu.', '',
        '| clause_id | Nhóm dấu hiệu | Lý do sơ bộ |','|---|---|---|']
    for row in rows:
        if row['label']=='abnormal':
            lines.append('| '+row['clause_id']+' | '+row['risk_category']+' | '+row['annotation_reason'].replace('|','/')+' |')
    lines += ['', '## Một số trường hợp có từ ngữ dễ nhầm nhưng vẫn normal', '',
              '| clause_id | Căn cứ |','|---|---|']
    examples=['viettel_stracking_2026_0003','viettel_stracking_2026_0110','viettel_stracking_2026_0152',
              'viettel_tv_personal_0020','fpt_internet_0015','fpt_server_legacy_0030',
              'fpt_phone_business_0031','techcombank_direct_banking_0094','techcombank_direct_banking_0125',
              'greenfuture_vehicle_service_0101','moj_business_template_0011']
    by_id={r['clause_id']:r for r in rows}
    for key in examples:
        if key in by_id:
            lines.append('| '+key+' | '+by_id[key]['annotation_reason'].replace('|','/')+' |')
    lines += ['', '## Kết quả kiểm tra và giới hạn', '',
              f"- {quality['provenance']['clauses_verified']}/{len(rows)} điều khoản khớp nguồn và có thể replay mọi sửa Unicode/khoảng trắng. Có {result['source_boundary_repairs']} sửa ranh giới/câu dẫn và {result['review_rows_with_text_repairs']} dòng giữ lại có sửa text, gồm {result['font_glyph_repairs']} ký tự lỗi font đã đối chiếu ảnh PDF.",
              f"- Có {len(set(groups))} nhóm hợp đồng/họ mẫu/gần trùng; normal xuất hiện trong {independent['normal']} nhóm và abnormal trong {independent['abnormal']} nhóm.",
              '- Tập dữ liệu lệch lớp rõ rệt và ít nguồn độc lập; normal chỉ có nghĩa chưa ghi nhận dấu hiệu theo sáu nhóm đã duyệt, không bảo đảm toàn hợp đồng an toàn.',
              '- Nhãn do một agent rà soát, chưa được đo độ đúng nhãn hoặc mức đồng thuận giữa nhiều người gán. Kiểm tra provenance không chứng minh nhãn chắc chắn đúng.',
              '- Classifier hiện nhận text điều khoản; một số nhãn cần ngữ cảnh được ghép lại hoặc ghi nguồn tham chiếu. Khả năng khái quát ngoài các mẫu này chưa được thực nghiệm.',
              (f"- Preflight chia được ba tập đủ hai nhãn, nhưng trên bản draft hiện tại validation chỉ có {preflight['counts']['validation'].get('abnormal',0)} và test chỉ có {preflight['counts']['test'].get('abnormal',0)} mẫu abnormal. Đây là kiểm tra khả năng chia, không phải kết quả thực nghiệm; metrics sau train sẽ có độ bất định lớn và cần ghi rõ support."
               if preflight['feasible'] else '- Preflight chưa chia được ba tập đủ hai nhãn: '+preflight['blocker']),
              '- Chưa huấn luyện chính thức; chưa có Accuracy/Precision/Recall/F1 hoặc Confusion Matrix chính thức. Khi dataset được duyệt mới tiến hành các bước đó.', '',
              'Ngừng ở bước chờ duyệt dataset theo AGENTS.md. Chưa làm MVP 2–4.']
    (ROOT/'reports/DATASET_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['rows','draft_label_counts','provenance','source_groups','independent_groups_by_label','official_metrics']},ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
