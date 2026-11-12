"""Publish measured expansion inventory and review documentation; no fitting or approval."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import os
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from contractguard.dataset import read_json, read_rows, sha256, write_json
from rental_expansion_annotations_v2 import SOURCE_REVIEWS, EXCLUDED_SOURCE_NOTES

BASE = ROOT / 'data/rental_expansion_v2'


def relative(path):
    return Path(path).relative_to(ROOT).as_posix()


def acquisition_inventory():
    catalog = read_json(BASE / 'collection_manifest.json')
    sources = {s['document_id']: s for s in catalog}
    attempted = defaultdict(lambda: dict(source_ids=set(), errors=set(), receipts=set()))
    for path in sorted((BASE / 'collection_runs').glob('*.json')):
        receipt = read_json(path)
        for sid in receipt['successes']:
            source = sources[sid]
            item = attempted[source['source_url']]
            item['source_ids'].add(sid)
            item['receipts'].add(relative(path))
        for failure in receipt['failures']:
            item = attempted[failure['url']]
            item['source_ids'].add(failure['document_id'])
            item['errors'].add(failure['error'])
            item['receipts'].add(relative(path))
    successes = {s['source_url'] for s in catalog}
    ledger = [dict(url=url, source_ids=sorted(v['source_ids']),
                   status='archived_and_parsed' if url in successes else 'not_in_parsed_archive',
                   errors=sorted(v['errors']), receipts=sorted(v['receipts']))
              for url, v in sorted(attempted.items())]
    for source in catalog:
        assert sha256(ROOT / source['raw_path']) == source['source_sha256']
        assert sha256(ROOT / source['pages_path']) == source['pages_sha256']
    unparsed = read_json(BASE / 'unparsed_responses/inspection_manifest.json')
    for source in unparsed:
        assert sha256(ROOT / source['raw_path']) == source['sha256']
    discovery = [p for p in (BASE / 'discovery').glob('search_*.json') if p.stem[7:].isdigit()]
    stats = dict(distinct_attempted_urls=len(attempted), parsed_source_records=len(catalog),
                 distinct_parsed_urls=len(successes), not_in_parsed_archive=sum(x['status'] != 'archived_and_parsed' for x in ledger),
                 search_batches_archived=len(discovery), inspected_unparsed_responses=len(unparsed),
                 format_counts=dict(Counter(s['format'] for s in catalog)),
                 note='URL count is not a count of valid contracts. Repeated attempts are deduplicated by exact URL; alternate domains/URLs may still mirror the same file.')
    write_json(BASE / 'acquisition_inventory.json', dict(summary=stats, urls=ledger, unparsed_inspections=unparsed))
    return stats, catalog


def main():
    stats, catalog = acquisition_inventory()
    audit = read_json(ROOT / 'reports/rental_expansion_v2_audit.json')
    snapshot = read_json(BASE / 'review_snapshot.json')
    rows = read_rows(ROOT / snapshot['dataset_path'])
    assert sha256(ROOT / snapshot['dataset_path']) == snapshot['dataset_sha256']
    types = Counter(r['clause_type'] for r in rows)
    cohorts = Counter(r['rental_subtype'] for r in rows)
    groups = {r['group_id'] for r in rows if r['label'] == 'abnormal'}
    selected_docs = {r['document_id'] for r in rows}
    contributing = read_json(BASE / 'sources.json')
    per_source = []
    for s in catalog:
        sid = s['document_id']
        chosen = [r for r in rows if r['document_id'] == sid]
        selected_review = SOURCE_REVIEWS.get(sid)
        if chosen:
            assessment = 'selected_draft_scope_and_clause_review'
        elif selected_review:
            assessment = 'explicit_scope_review_no_unique_selected_rows'
        elif sid in EXCLUDED_SOURCE_NOTES:
            assessment = 'not_selected_with_explicit_source_note'
        else:
            assessment = 'archived_candidate_not_selected_not_a_validated_contract'
        per_source.append(dict(document_id=sid, title=s['title'], source_url=s['source_url'],
            raw_sha256=s['source_sha256'], assessment=assessment,
            retained_rows=len(chosen), retained_labels=dict(Counter(r['label'] for r in chosen)),
            note=EXCLUDED_SOURCE_NOTES.get(sid, ''), source_use_status='pending_dataset_and_source_review'))
    write_json(BASE / 'source_assessment.json', per_source)
    distribution = dict(clause_types=dict(types), rental_subtypes=dict(cohorts),
        ledger_actions=dict(Counter(r['action'] for r in read_json(BASE / 'annotation_ledger.json'))),
        missing_abnormal_categories=sorted({'deemed_consent','automatic_renewal','overbroad_data_use'} - set(audit['risk_category_counts'])))
    write_json(BASE / 'distributions.json', distribution)
    label_counts = audit['label_counts']
    new_positive = [r for r in rows if r['label'] == 'abnormal' and r['row_origin'].startswith('new')]
    junit=ROOT/'reports/rental-v2-test-results.xml'
    if junit.exists():
        suites=list(ET.parse(junit).getroot().iter('testsuite'))
        checks={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','errors','failures','skipped']}
        test_note=f'JUnit hiện tại: {checks["tests"]} kiểm thử kỹ thuật, {checks["failures"]} thất bại, {checks["errors"]} lỗi, {checks["skipped"]} bỏ qua. Đây là kiểm tra code/provenance/gate, không phải độ chính xác gán nhãn hay chất lượng NLP. Hai cảnh báo deprecation SciPy/sklearn xuất hiện ở fixture kỹ thuật của bộ test, không phải kết quả huấn luyện v2.'
    else:
        test_note='Chưa có JUnit hiện tại; chưa tuyên bố kiểm thử đã qua.'
    report = [
        '# ContractGuard — hồ sơ mở rộng dữ liệu thuê nhà v2',
        '', 'Ngày cập nhật: **09/11/2026**. Bản nháp có nguồn truy vết; chưa được duyệt và chưa huấn luyện.',
        '', f'**Chưa đạt mục tiêu 1.000–2.000 mẫu và 500 abnormal. Hiện có {len(rows):,} mẫu: {label_counts["normal"]:,} normal / {label_counts["abnormal"]:,} abnormal.**'.replace(',', '.'),
        f'Còn thiếu tối thiểu {max(0,1000-len(rows))} mẫu tổng và {max(0,500-label_counts["abnormal"])} abnormal. Đây là kết quả thu thập thực tế, không phải tuyên bố hoàn tất yêu cầu số lượng hoặc hoàn tất MVP 1.',
        '', '## 1. Kết quả có thể kiểm chứng', '',
        '| Hạng mục | Số lượng |', '|---|---:|',
        f'| URL khác nhau đã thử tải trong vòng v2 | {stats["distinct_attempted_urls"]} |',
        f'| Tài liệu nguồn tải và trích được trong archive mới | {stats["parsed_source_records"]} |',
        f'| URL chưa đưa được vào archive đã trích | {stats["not_in_parsed_archive"]} |',
        f'| Bản ghi ứng viên kỹ thuật, chưa tự có nhãn | {audit["candidate_pool"]} |',
        f'| Điều khoản kế thừa v1, nguyên text/label | {audit["inherited_v1_rows"]} |',
        f'| Quyết định gán nhãn mới có ID và lý do | {audit["explicit_new_decisions"]} |',
        f'| Bản lặp được giữ dấu vết, không tính lại | {audit["exact_repetitions_not_counted"]} |',
        f'| Mẫu mới giữ lại sau khử trùng | {audit["newly_selected_rows"]} |',
        f'| Abnormal mới giữ lại | {len(new_positive)} |',
        f'| Tài liệu thực sự đóng góp vào CSV v2 | {audit["source_documents"]} |',
        f'| Mẫu hợp đồng/phụ lục đóng góp (theo contract_id) | {len({r["contract_id"] for r in rows})} |',
        f'| Nhóm nguồn/họ mẫu dùng ngăn rò rỉ dữ liệu | {audit["leakage_groups"]} |',
        f'| Nhóm có abnormal / nhóm abnormal mới ngoài v1 | {len(groups)} / {audit["fresh_positive_groups_outside_v1"]} |',
        '', 'Số tệp tải được không đồng nghĩa số hợp đồng phù hợp. Bản ứng viên gồm cả tiêu đề, tư vấn, metadata và bản chép; chỉ những ID được agent chọn và giải thích mới vào CSV. Nguồn dự trữ chưa được đọc/duyệt đầy đủ không được tính là hợp đồng hợp lệ.',
        '', '## 2. Nguồn và phương pháp', '',
        'Kế thừa v1 từ Cổng Chính phủ, đơn vị vận hành nhà ở/ký túc xá, mẫu thuê nhà công khai và mẫu song ngữ. Vòng mới bổ sung nguồn từ cơ sở giáo dục TDTU/NAUE, tệp DOCX/PDF trực tiếp từ các trang mẫu, Wipi, BDSDaily/Đà Nẵng, các phần hợp đồng công khai trên Caselaw, Homedy và bản PDF mang chân trang REVER do RentApartment lưu trữ. Nguồn đăng lại được ghi đúng vai trò, không gọi là hợp đồng thực tế đã ký.',
        'Chi tiết từng tài liệu đóng góp: [sources.json](../data/rental_expansion_v2/sources.json). Từng URL đã thử: [acquisition_inventory.json](../data/rental_expansion_v2/acquisition_inventory.json). Đánh giá trạng thái các nguồn mới: [source_assessment.json](../data/rental_expansion_v2/source_assessment.json).',
        '', 'Quy trình: tìm nguồn → kiểm tra truy cập công khai → lưu bytes và SHA256 → trích DOM/OOXML/PDF → sửa tách/ghép từ nguồn → đọc vai trò, mục đích ở, điều kiện và ngoại lệ → quyết định từng ID → khử trùng và gộp họ → audit spans/hash → xuất draft. Tìm từ khóa chỉ sắp xếp hàng đọc, không sinh ground truth.',
        'Đã sửa bố cục PDF BDSDaily từ nguồn gốc và đối chiếu trực quan bốn trang; sửa giữ câu dẫn vai trò ở HTML/DOCX; bỏ dòng vô hình; loại chữ ký/tiêu đề điều kế tiếp khỏi đơn vị được chọn. Đã xem các trang chứa abnormal mới của RentApartment và cả hai trang CoChinh bổ sung. Bản CoChinh lặp abnormal v1 nên không tính là abnormal mới. Ảnh kiểm tra nằm tại `reports/rental_source_quality_v2`. Không tuyên bố đã kiểm tra trực quan mọi trang của tất cả tệp tải.',
        'Các giới hạn truy cập được giữ nguyên: không vượt robots/login, không đoán nội dung sau preview, không bỏ xác minh TLS. Hai file eLib tải được qua tên miền chính thức không có www sau lỗi chứng thư ở www; hiện nằm trong ứng viên, chưa chọn thêm vào CSV. File Office Mogi bị mã hóa đã giữ bytes và nhận diện EncryptionInfo/EncryptedPackage, không phá mật khẩu; có bản PDF thay thế nhưng không thêm mẫu nếu chỉ là trường trống. Phản hồi Scribd chỉ có metadata/mô tả không đủ nội dung hợp đồng không dùng để gán nhãn.',
        '', '## 3. Abnormal mới và lý do', '',
        'Các nhãn sau là đề xuất của agent, chưa có xác nhận chuyên gia độc lập; “abnormal” cảnh báo cơ chế bất lợi theo tiêu chí đã duyệt, không kết luận trái pháp luật.',
    ]
    for r in new_positive:
        fmt=next(s['format'] for s in contributing if s['document_id']==r['document_id'])
        location=f'trang PDF {r["page_start"]}–{r["page_end"]}' if fmt=='pdf' else 'đoạn trích OOXML/DOM, vị trí chi tiết trong source_spans'
        report.extend(['', f'### `{r["clause_id"]}`', '', f'- Nguồn: [{r["document_id"]}]({r["source_url"]}), {location}.',
            f'- Nhóm: `{r["risk_category"]}`; độ chắc chắn sơ bộ: `{r["label_confidence"]}`.',
            f'- Lý do: {r["annotation_reason"]}', f'- Ngữ cảnh trong text: `{r["context_clause_ids"]}`.'])
    report.extend(['', '## 4. Phân bố và hạn chế', '', '![Tiến độ thu thập so với mục tiêu](rental_expansion_v2_figures/collection_progress.png)', '', '| Chủ đề phụ | Số mẫu |', '|---|---:|'])
    report.extend(f'| {k} | {v} |' for k,v in sorted(types.items()))
    report.extend(['', '| Cơ chế bất lợi | Số mẫu mang dấu hiệu |', '|---|---:|'])
    report.extend(f'| {k} | {v} |' for k,v in sorted(audit['risk_category_counts'].items()))
    report.extend(['', 'Một abnormal có thể có nhiều mã nên tổng cột cơ chế không bằng số abnormal. Chưa có mẫu được chọn cho `deemed_consent`, `automatic_renewal`, `overbroad_data_use`; không ép nhãn cho đủ chín nhóm.',
        f'Tỷ lệ abnormal hiện là {100*label_counts["abnormal"]/len(rows):.2f}%. Các mẫu công khai thiên về hợp đồng chuẩn và sao chép. Chỉ {audit["fresh_positive_groups_outside_v1"]} nhóm abnormal mới ngoài v1: tăng số dòng normal chưa giải quyết được thiếu độ đa dạng positive. Mốc 500 là mục tiêu thu thập, không bảo đảm mô hình sẽ tốt.',
        'Giữ riêng cohort ký túc xá/chỗ ở nội trú và thuê dài hạn; không coi chúng đại diện hoàn toàn phòng trọ dân dụng. Các hợp đồng thuê văn phòng/mặt bằng, thuê mua và ví dụ danh tính giả không được dùng để bù chỉ tiêu. Không sinh dữ liệu giả, dịch hợp đồng nước ngoài hay nhân bản positive để báo đủ mẫu.',
        'Không có Accuracy/Precision/Recall/F1 hoặc confusion matrix mới cho v2. Kết quả v1 là lịch sử thí nghiệm trên snapshot cũ; không dùng test v1 để chỉnh nhãn hoặc lựa chọn mô hình mới.',
        '', '## 5. Kiểm tra và cách mở', '',
        test_note,
        '',
        'CSV UTF-8 BOM: [clauses_rental_v2.csv](../data/clauses_rental_v2.csv), mở bằng Excel qua Data → From Text/CSV, encoding UTF-8 và delimiter dấu phẩy để giữ tiếng Việt và các ô nhiều dòng. Bộ dữ liệu v1 được duyệt và `data/clauses.csv` legacy không bị ghi đè.',
        '49 cột gốc được giữ theo thứ tự; thêm metadata phiên bản, nguồn gốc kế thừa, nhóm và mức tiếp xúc split v1. Nhãn/nguồn/lý do có các cột alias đúng schema ban đầu. Xem [data card](../docs/RENTAL_V2_DATA_CARD.md).',
        '', '```powershell', '.venv\\Scripts\\python.exe -X utf8 tools/review_rental_dataset.py --data data/clauses_rental_v2.csv --label abnormal --origin new --count 10',
        '.venv\\Scripts\\python.exe -X utf8 tools/review_rental_dataset.py --data data/clauses_rental_v2.csv --start 0 --count 25',
        '.venv\\Scripts\\python.exe -X utf8 tools/verify_rental_expansion_v2.py', '```',
        '', 'Tăng `--start` theo từng đợt để xem toàn bộ; có thể lọc `--source`, `--clause-id`, `--risk`. Công cụ chỉ đọc, không chấp thuận dataset. Danh sách reserve/needs_context là hồ sơ công việc của agent, không yêu cầu người dùng tự sửa trích hoặc nhập nhãn.',
        '', '## 6. Điều kiện để đi tiếp', '',
        'Vòng thu thập này chưa đáp ứng mục tiêu số lượng. Cần thêm hợp đồng thuê ở khác họ có đủ nội dung điều khoản, nhất là các cơ chế còn thiếu; các đường tìm tiếp hữu ích là bộ mẫu/điều kiện thuê do đơn vị vận hành công khai hoặc hợp đồng đã được phép dùng và ẩn danh. Không thể suy rằng các hợp đồng khác đều an toàn chỉ vì chưa thu được nhiều abnormal từ nguồn công khai.',
        'Sau khi nguồn và nhãn của bản mở rộng đủ chất lượng, agent trình đúng snapshot để người dùng chỉ xác nhận Đạt/Chưa đạt. Quyết định v1 không phê duyệt v2. Không thay cờ approval hoặc tên reviewer để qua gate.',
        'Đề xuất chia tương lai theo document/họ mẫu/gần trùng, không ngẫu nhiên từng dòng; cố định seed và kiểm tra số positive cùng số nhóm ở từng tập trước fit. Không hứa tỷ lệ 70/15/15 khi chỉ có một nhóm positive mới. `prior_v1_split` và `shares_group_with_v1` chỉ phục vụ quản trị: test v1 đã xem phải coi là hồi cứu, cần nhiều nhóm positive hoàn toàn mới cho test độc lập. Chỉ fit vocabulary trên train và chọn theo validation sau duyệt.',
        f'Lab tham khảo và cách áp dụng giữ tại [LAB_MAPPING.md](../docs/LAB_MAPPING.md). Thống kê kiểm duyệt: {audit["inherited_v1_rows"]} mẫu v1 có quyết định người dùng thật; toàn bộ {len(rows)} dòng trong phiên bản v2 còn pending, chưa có duyệt v2. Chưa sang MVP 2.',
        '', f'Dataset SHA256: `{snapshot["dataset_sha256"]}`. Hồ sơ máy đọc: [audit](rental_expansion_v2_audit.json), [snapshot](../data/rental_expansion_v2/review_snapshot.json), [verification](rental_expansion_v2_verification.json).',
    ])
    (ROOT / 'reports/RENTAL_EXPANSION_V2_REVIEW.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    card = f'''# Data card — ContractGuard rental v2 draft

Ngày 09/11/2026. **{len(rows)} mẫu, {label_counts['normal']} normal / {label_counts['abnormal']} abnormal; chưa đạt mục tiêu 1.000–2.000 và 500 abnormal.**

## Mục đích và phạm vi

Phát hiện dấu hiệu bất lợi cho người thuê nhà ở bằng tiếng Việt, offline; normal/abnormal là nhãn đích. Chủ đề phụ không quyết định nhãn rủi ro. Cảnh báo không kết luận vi phạm pháp luật. Không gọi API AI bên ngoài; không sinh câu giả cho tập chính. Tiêu chí cố định: `docs/LABELING_GUIDELINES.md`, SHA256 `{snapshot['criteria_sha256']}`; ghi nhận duyệt tiêu chí tại `reports/rental_criteria_approval.json`.

## Đơn vị, nguồn và nhãn

Khoản/nhóm khoản đủ nghĩa, kèm câu dẫn và ngữ cảnh cùng hợp đồng. {audit['inherited_v1_rows']} mẫu v1 giữ nguyên text/label; {audit['newly_selected_rows']} mẫu mới có quyết định ID/lý do. {audit['source_documents']} tài liệu đóng góp, {audit['leakage_groups']} nhóm nguồn/họ mẫu. Mẫu công khai không được gọi là giao dịch đã ký. Bản chép bị loại khỏi số đếm nhưng giữ lineage. Không tự normal hóa ứng viên chưa đọc/thiếu thông tin. `label_confidence` high/medium là nhận định gán nhãn, không là xác suất mô hình.

## Schema và cách dùng

CSV UTF-8 BOM, giữ 49 cột gốc và thêm metadata:

| Trường | Ý nghĩa |
|---|---|
| `contract_id`, `clause_id`, `document_id` | Hợp đồng, đơn vị và tài liệu nguồn |
| `text`, `clause_body`, `heading` | Đầu vào đủ ngữ cảnh, phần thân và cấu trúc nguồn |
| `label`, `risk_label` | Nhãn sơ bộ normal/abnormal, hai alias phải khớp |
| `clause_type`, `category` | Chủ đề phụ, hai alias phải khớp |
| `annotation_reason`, `label_reason`, `risk_evidence`, `risk_category` | Giải thích và bằng chứng; không đưa vào features |
| `source_url`, `source`, `source_sha256`, `source_spans`, `source_line_refs` | URL, hash và vị trí giúp đối chiếu nguồn |
| `context_clause_ids`, `body_line_refs`, `selection_repairs` | Ngữ cảnh cùng hợp đồng, dòng thân và log chọn lại dòng nguồn |
| `tenant_role`, `rental_subtype`, `protected_party` | Vai trò đã đọc từ nguồn và cohort thuê ở |
| `annotation_status`, `review_status`, `reviewer`, `verified_risk_label` | draft/pending, reviewer và verified để trống; không phải ground truth đã duyệt |
| `dataset_version`, `row_origin`, `inherited_approval_record` | rental_v2_draft, dòng kế thừa hay mới, hồ sơ v1 |
| `group_id`, `template_family`, `inherited_group_id` | Nhóm chống leakage, không là features |
| `prior_v1_split`, `shares_group_with_v1` | Tiếp xúc thí nghiệm v1; không là features |

Mô tả các cột nền: [RENTAL_DATASET_SCHEMA.md](RENTAL_DATASET_SCHEMA.md). Nếu huấn luyện sau duyệt, đầu vào chỉ là `text`; không đưa lý do, risk_category, nguồn, ID, metadata hoặc nhãn chủ đề chuẩn vào classifier rủi ro. Phải bảo đảm inference xây ngữ cảnh theo cấu trúc nguồn, không dựa vào nhãn đúng.

PDF dùng số trang gốc. Với HTML/DOCX, page là khối trích xuất logic (thường một khối toàn văn), không phải phân trang Word thực tế; đối chiếu bằng source_spans/source_line_refs trong pages.json.

## Chất lượng, rò rỉ và quyền dùng

Audit hash/spans không đánh giá độ đúng nhãn và không thay duyệt. Chưa đo agreement độc lập hay chất lượng model v2. Nguồn công khai thiên về mẫu chuẩn/sao chép; positive ít và chỉ {audit['fresh_positive_groups_outside_v1']} nhóm mới ngoài v1. Thiếu ba cơ chế deemed_consent, automatic_renewal, overbroad_data_use. Ký túc xá và thuê dài hạn là cohort riêng. Không kết luận lỗi mô hình chỉ do số lượng positive; ngữ cảnh, độ nhất quán nhãn và khác biệt nguồn cũng cần kiểm chứng.

Giữ nguyên test v1 như dữ liệu đã tiếp xúc, không gọi là test độc lập mới. Chỉ chia theo nhóm khi đã duyệt; chưa chốt split v2 hay fit mô hình. `approval.json` v2 giữ dataset_approved=false/source_use_confirmed=false. Công khai truy cập không tự đồng nghĩa có giấy phép tái phân phối; corpus đang lưu nội bộ phục vụ rà soát học thuật, không phát hành công khai thay tác giả nguồn. Nguồn từng file và trạng thái dùng được giữ tại `data/rental_expansion_v2/sources.json`.

## Tái lập và hồ sơ

`tools/package_rental_expansion_v2.py` chỉ đóng gói các quyết định ID đã ghi; không huấn luyện hay phê duyệt. `tools/report_rental_expansion_v2.py` tổng hợp số liệu, không gán nhãn. Đối chiếu đầy đủ tại [báo cáo review](../reports/RENTAL_EXPANSION_V2_REVIEW.md). Dataset SHA256 `{snapshot['dataset_sha256']}`; manifest SHA256 `{snapshot['sources_sha256']}`. Các bước/tệp v1 và 752 mẫu legacy được giữ nguyên.
'''
    (ROOT / 'docs/RENTAL_V2_DATA_CARD.md').write_text(card, encoding='utf-8')
    os.environ['MPLCONFIGDIR'] = str(ROOT / '.cache/matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder = ROOT / 'reports/rental_expansion_v2_figures'
    folder.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    for ax, value, target, title, color in [(axes[0],len(rows),1000,'Total clauses (minimum target)','#2861a5'),
                                           (axes[1],label_counts['abnormal'],500,'Abnormal clauses','#b44b35')]:
        ax.barh(['Collected'],[value],color=color,height=.45)
        ax.axvline(target,color='#555',linestyle='--',label=f'Target {target:,}')
        ax.set_xlim(0,target*1.15)
        ax.text(value+target*.02,0,str(value),va='center',fontweight='bold')
        ax.set_title(title); ax.set_xlabel('Unique retained clauses'); ax.legend(loc='lower right')
        ax.spines[['top','right','left']].set_visible(False)
    fig.suptitle('ContractGuard rental v2 — draft; collection targets not met',fontsize=13)
    for ext in ['png','svg']:fig.savefig(folder/f'collection_progress.{ext}',dpi=160)
    plt.close(fig)
    write_json(BASE / 'report_snapshot.json',dict(dataset_sha256=sha256(ROOT / snapshot['dataset_path']),
        report_sha256=sha256(ROOT / 'reports/RENTAL_EXPANSION_V2_REVIEW.md'),
        data_card_sha256=sha256(ROOT / 'docs/RENTAL_V2_DATA_CARD.md'),acquisition=stats))
    print(json.dumps(dict(rows=len(rows),labels=label_counts,acquisition=stats),ensure_ascii=False))


if __name__ == '__main__':
    main()
