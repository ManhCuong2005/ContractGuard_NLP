"""Generate the MVP 1A handoff from measured corpus counts, not model scores."""
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]

def read(path):return json.loads((ROOT/path).read_text('utf-8'))
def write(path,text):
    p=ROOT/path
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text.strip()+'\n',encoding='utf-8')

def main():
    if read('configs/rental_approval.json').get('dataset_approved'):
        raise SystemExit('Historical MVP 1A handoff is frozen after acceptance; do not overwrite current experiment documentation.')
    audit=read('reports/rental_dataset_audit.json')
    acquisition=read('data/rental_mvp1a_v1/acquisition_ledger.json')
    sources=read('data/rental_mvp1a_v1/sources.json')
    snapshot=read('data/rental_mvp1a_v1/review_snapshot.json')
    for relative in ['README.md','data/README.md','reports/MVP1_STATUS.md','docs/RUN_MVP1.md']:
        original=ROOT/relative
        saved=ROOT/'reports/history/before_rental_v1_handoff'/relative
        if original.exists() and not saved.exists():
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(original,saved)
    normal= audit['draft_label_counts']['normal']
    abnormal=audit['draft_label_counts']['abnormal']
    rows=audit['rows']
    table='\n'.join(f'| {name} | {counts.get("normal",0)} | {counts.get("abnormal",0)} |'
        for name,counts in sorted(audit['by_source'].items()))
    source_links='\n'.join(f'- [{s["document_id"]}]({s["source_url"]}) — raw SHA256 `{s["source_sha256"]}`; text nguồn `{s["pages_path"]}`.' for s in sources)
    risk_names={
        'broad_liability':'Trách nhiệm/bồi thường hoặc miễn trách nhiệm quá rộng',
        'repair_burden':'Đẩy sửa chữa không phân định lỗi sang người thuê',
        'deposit_forfeiture':'Mất cọc/tiền trả trước theo cơ chế bất lợi',
        'termination_discretion':'Thu hồi/chấm dứt tùy nghi hoặc thiếu căn cứ/thủ tục',
        'access_interference':'Tự vào phòng, niêm phong hoặc cản trở sử dụng',
        'unilateral_change':'Chủ nhà tự bổ sung nghĩa vụ/điều chỉnh phí',
    }
    risk_table='\n'.join(f'| {code} | {risk_names[code]} | {count} |' for code,count in sorted(audit['risk_category_counts'].items()))
    report=f'''
# MVP 1A — bản dữ liệu thuê nhà v1 để kiểm duyệt

**Đã chuẩn bị một bản dữ liệu có nguồn và nhãn sơ bộ để kiểm duyệt; chưa đạt mong muốn abnormal nhiều và chưa hoàn thành toàn bộ MVP 1.** Không gọi bản này là bộ dữ liệu lớn, cân bằng hoặc bằng chứng mô hình nhận dạng tốt. Mục tiêu 1.500–3.000 trong master prompt là tham khảo khi có nguồn phù hợp; bản hiện tại có {rows} đơn vị sau chọn và loại bản lặp.

## Bản cần xem

[data/clauses_rental_v1.csv](../data/clauses_rental_v1.csv) — {normal} normal, **{abnormal} abnormal** ({100*abnormal/rows:.2f}%), {audit['source_documents']} tài liệu nguồn, {audit['contract_templates']} mẫu hợp đồng, {audit['template_families']} họ mẫu, {audit['leakage_groups']} nhóm theo nguồn/họ/gần trùng. Đây là nhãn **draft/pending**, chưa phải ground truth được người dùng duyệt. Không phải {audit['contract_templates']} hợp đồng đã được các bên ký thực tế: phần lớn là mẫu công khai chưa điền, một nguồn là hợp đồng lưu xá theo kỳ năm học.

Mỗi dòng có text đủ ngữ cảnh được chọn, nhãn nhị phân, chủ đề phụ, cơ chế rủi ro, lý do, bằng chứng, mức chắc chắn định tính, vai trò người thuê, nguồn/trang/spans và SHA256. Toàn bộ text trong CSV có thể đối chiếu về nguồn; giải thích/nhãn không được đưa vào đầu vào mô hình. CSV dùng UTF-8 BOM để mở trên Excel đúng tiếng Việt. Các dòng abnormal mức chắc chắn medium nằm trước, sau đó abnormal còn lại, các đối chứng dễ nhầm và phần còn lại. Người dùng không phải tự nhập nhãn.

Tiêu chí thuê nhà đã được người dùng duyệt: **“Tiêu chí thuê nhà Đạt”**; giữ nguyên bytes và SHA256 của `docs/LABELING_GUIDELINES.md`. Hồ sơ xác nhận ở [rental_criteria_approval.json](rental_criteria_approval.json). Đã phục hồi dấu tiếng Việt trong các câu trích chat bị lỗi encoding từ lượt trước, giữ bản trước sửa ở `reports/approval_encoding_history`; quyết định duyệt dataset vẫn false.

## Thu thập và chọn lọc

- Đã thử {acquisition['attempted_sources']} địa chỉ mới, tải/lưu raw được {acquisition['downloaded_sources']}, {acquisition['unavailable_sources']} không lấy được vì TLS/HTTP/DNS; không tắt kiểm tra chứng chỉ hoặc vượt hạn chế truy cập. Nguồn Chính phủ từ staging trước được tái sử dụng riêng, không tính thành lượt tải mới.
- {acquisition['downloaded_sources']} tài liệu tải được **không phải** {acquisition['downloaded_sources']} hợp đồng hợp lệ/độc lập: có trang tư vấn, chỉ mục tải, mẫu thương mại, bản chép và mẫu thiếu ngữ cảnh. Chỉ {audit['source_documents']} nguồn đóng góp vào CSV này. [Nhật ký tải/chọn](../data/rental_mvp1a_v1/acquisition_ledger.json) ghi riêng từng mục.
- Pool kỹ thuật có {audit['candidate_count']} ứng viên chưa phải dataset được duyệt. Có {audit['candidate_decisions']['annotated_draft']} quyết định nhãn tường minh, loại {audit['exact_duplicates_not_counted']} bản lặp chính xác khỏi số mẫu chính; {audit['candidate_decisions']['hold']} đơn vị thật sự mơ hồ ở nguyên bản giữ nội bộ; {audit['candidate_decisions']['reserve_unlabelled']} ứng viên dự trữ không được tự gán normal. Không tuyên bố đã đọc và gán nhãn toàn bộ pool.
- Các lỗi trích được sửa trước khi đưa vào CSV: tách chữ do inline HTML, đoạn lồng trong danh sách, dòng xuống trang PDF, tham chiếu “Điều 9.7” bị nhầm thành tiêu đề, “01 bản” bị tách thành khoản, và lẫn phần đầu mẫu kế bên trong tuyển tập. Bản trích trước sửa vẫn ở `extraction_history`. Những điều khoản hợp lệ chưa chọn vẫn còn nguyên, không bị xóa vì lỗi bộ trích.
- Đã đối chiếu ảnh PDF Sunshine trang 34, 45 và lưu xá trang 2 tại `reports/rental_source_quality`; nguồn 9.6 có dẫn chiếu 9.7 khác thường được giữ đúng, không tự sửa ý văn bản. Audit nguồn xác nhận tính truy vết, không chứng minh nhãn chính xác tuyệt đối.
- Sau yêu cầu “tiếp tục”, bổ sung nguồn thuê phòng lưu trú công nhân SADECO và hai mẫu phòng trọ thực sự khác. PDF SADECO không có lớp text; agent đã đọc ảnh cả sáu trang và chép/đối chiếu hai lượt các phần nguyên văn được chọn. Có {audit.get('visually_transcribed_rows',0)} dòng từ bản trích scan này. `visual_transcription_v1.json` ghi phạm vi phần đã chép, phần hành chính/công thức tháng đầu không dùng và hash ảnh. **Spans của scan khớp bản chép đã kiểm tra bằng ảnh, không phải kiểm chứng độc lập bằng lớp text PDF.** Bản trước mở rộng 466 dòng/23 abnormal được giữ tại `data/rental_mvp1a_v1/dataset_history/before_worker_extension_466`.

## 752 dòng cũ được xử lý thế nào

Đã kiểm tra miền nguồn của cả **752** dòng. Không dòng nào có provenance hợp đồng thuê nhà ở. Vì vậy **0 dòng được trộn vào corpus thuê nhà chính**. Đã chọn lại **7** câu giải quyết tranh chấp hoàn toàn chung làm [legacy_auxiliary.csv](../data/rental_mvp1a_v1/legacy_auxiliary.csv), có nhãn sơ bộ và lý do, luôn `auxiliary_only` và nằm ngoài train/test thuê nhà chính. 745 dòng còn lại được giữ trong bộ cũ, không đổi tên miền hay thay từ “xe/dịch vụ” thành “nhà”. [Hồ sơ chọn toàn bộ 752 dòng](../data/rental_mvp1a_v1/legacy_selection_audit.json).

Bộ `data/clauses.csv`, approval tổng quát cũ và tiêu chí cũ không bị sửa. Quyền tạo tên CSV mới được người dùng cho phép trong yêu cầu lần này; chưa tự promote bản v1 thành corpus chính thức đã duyệt.

## Phân bố theo nguồn

| Nguồn | normal sơ bộ | abnormal sơ bộ |
|---|---:|---:|
{table}

Abnormal hiện có ở {audit['abnormal_source_documents']} nguồn/{audit['abnormal_leakage_groups']} nhóm độc lập theo quy tắc kiểm tra đang dùng. Các nguồn chép một mẫu như DOCX Đà Nẵng/Resident/Minh Khuê được giữ làm dự trữ và provenance, không coi là hàng chục nguồn rủi ro độc lập. Phát hiện gần trùng bằng word-trigram Jaccard >= 0,86 là kiểm tra phụ, không bảo đảm bắt mọi bản diễn đạt lại. Họ mẫu và cùng tài liệu luôn giữ chung nhóm.

## Độ đa dạng của abnormal

| Mã giải thích | Cơ chế | Số dòng có dấu hiệu |
|---|---|---:|
{risk_table}

Một dòng có thể có nhiều mã; tổng bảng này không bằng số abnormal. Đây là mã giải thích, **không phải các lớp chủ đề dùng thay nhãn rủi ro**.

**Còn thiếu nguồn abnormal đủ căn cứ cho `deemed_consent`, `automatic_renewal`, `overbroad_data_use`.** Ví dụ eNha chỉ có preview, thời hạn gia hạn trống và chưa có đủ toàn hợp đồng nên không ép thành abnormal. Câu thu thông tin để khai báo cư trú không bị coi là sử dụng dữ liệu quá rộng. Cơ chế bàn giao mặc nhiên Sunshine được đọc cùng quyền từ chối vì chất lượng; không gán chỉ theo từ khóa.

## Một số đối chứng đã rà

- `bandon_room_0043` abnormal: mọi hư hỏng sau 15 ngày do người thuê chịu. `roomi_registration_0052` normal: 100% chi phí chỉ khi sử dụng **sai cách**, kèm loại trừ hao mòn và chủ nhà sửa hỏng không do lỗi người thuê. Không gán theo từ “100%”.
- `iuoss_dorm_0016` abnormal: kiểm tra đột xuất không có giới hạn báo trước/khẩn cấp. `roomi_registration_0037` normal: định kỳ một lần/tháng, báo trước 24 giờ và có mục đích sửa chữa/an toàn.
- `sunshine_longterm_0117` abnormal mức chắc chắn medium: phí có thể điều chỉnh/bổ sung bằng thông báo, dù phải hợp lý/theo luật; thiếu cơ chế giới hạn cụ thể và từ chối. `homedy_student_0011` normal: căn cứ thay đổi khung giá Nhà nước, báo trước một tháng.
- `sunshine_longterm_0129` abnormal: căn hộ không sử dụng được do bất khả kháng thì không hoàn tiền đã trả, kèm cả nhánh ngoại lệ còn dùng được nhà và bảo hiểm để tránh cắt mất ngữ cảnh.
- `sadeco_worker_0014` abnormal: ngừng điện/nước để xử lý chậm thanh toán. `sadeco_worker_0004` về tăng giá được giữ nội bộ để làm rõ tương quan với Điều 5 yêu cầu hai bên ký phụ lục; không tự gán abnormal chỉ vì thấy “tối thiểu 4%”.
- `minhkhue_house_0012` normal: khấu trừ cọc theo thiệt hại và mức chi phí thống nhất bằng văn bản; khác với mất cọc/tiền còn lại với bất kỳ lý do nào ở Bandon.

Sunshine là thuê căn hộ dài hạn hình thành trong tương lai cho người nước ngoài, có phần chuyển sở hữu. Phần 10.3 không được dùng làm mẫu chính; các khoản thuê được giữ với subtype riêng. Đây không phải phòng trọ thông thường và đang chiếm 8/{abnormal} abnormal: cần xem xét cohort riêng ở thực nghiệm sau duyệt, không mặc định đại diện mọi loại thuê nhà.

## Chất lượng, giới hạn và bước kế tiếp

**Yêu cầu tăng mạnh số lượng abnormal chưa đạt.** {abnormal} mẫu sơ bộ và sáu nhóm dấu hiệu là một tập khởi đầu có truy vết, chưa đủ để hứa hẹn mô hình tổng quát tốt. Bản hiện tại vẫn lệch lớp nặng, nhiều mẫu công khai có cùng cách viết, và thiếu ba cơ chế. Agent không tạo thêm câu giả, diễn đạt lại một câu thành nhiều mẫu hoặc ép nhãn để làm đẹp tỷ lệ.

Preflight kiểm tra được {audit['abnormal_leakage_groups']} nhóm có abnormal, nhưng chưa chốt train/validation/test và chưa fit BoW/TF-IDF hoặc predictor trên corpus này. Chỉ đủ số nhóm tối thiểu không có nghĩa validation/test đủ mẫu rủi ro. Chưa có Accuracy/Precision/Recall/F1/confusion matrix chính thức.

Việc tiếp theo để tăng chất lượng dữ liệu là thu thêm mẫu vận hành thuê nhà khác họ, có toàn bộ điều kiện cọc/hoàn tiền, phí, thông báo, quyền từ chối, nội quy đính kèm và mục đích dữ liệu. Ưu tiên abnormal mới và đối chứng cùng cơ chế; không ưu tiên thêm hàng trăm normal hoặc bản sao. Mục tiêu thu thập còn mở, không coi dữ liệu trong pool chưa đọc là đã giải quyết.

Nếu chấp nhận bản hiện tại cho một baseline thăm dò có giới hạn, người dùng chỉ cần xác nhận **“Dataset thuê nhà Đạt”**; nếu chưa chấp nhận, trả lời **“Chưa đạt”** và agent tiếp tục sửa/bổ sung, không yêu cầu người dùng nhập nhãn. Đây là bước kiểm duyệt thật bắt buộc ở mục 8 master prompt, không phải yêu cầu duyệt lại tiêu chí đã duyệt. Sau quyết định thật còn cần chốt nguồn sử dụng và profile gate thuê nhà trước MVP 1B. Không có huấn luyện chính thức trước quyết định này.

## Truy vết và tái lập

- Dataset SHA256: `{audit['dataset_sha256']}`.
- Source manifest SHA256: `{audit['sources_sha256']}`.
- Tiêu chí: `{audit['criteria_sha256']}`.
- [Audit kiểm tra kỹ thuật](rental_dataset_audit.json): {audit['verified_source_spans']} dòng khớp spans, raw/pages khớp hash, CSV round-trip UTF-8 BOM, input lịch sử giữ nguyên, gate vẫn đóng.
- [Snapshot duyệt](../data/rental_mvp1a_v1/review_snapshot.json), [quyết định nhãn](../data/rental_mvp1a_v1/annotation_decisions.json), [lineage bản lặp](../data/rental_mvp1a_v1/exact_duplicate_lineage.json), [schema](../docs/RENTAL_DATASET_SCHEMA.md).
- `tools/package_rental_dataset.py` chỉ đóng gói từ quyết định ID đã đọc, kiểm tra hash candidate cố định và tạo audit; không gán normal cho dòng không có quyết định. Các trường needs_context/reserve không vào CSV chính.
- Công cụ đọc toàn bộ CSV: `tools/review_rental_dataset.py`, có lọc nguồn, nhãn, mã rủi ro và clause_id. Hướng dẫn ở [RUN_MVP1.md](../docs/RUN_MVP1.md).
- Nguồn công khai không đồng nghĩa giấy phép tái phân phối mở. Raw được lưu để kiểm tra cục bộ; manifest không tự khẳng định quyền công bố lại toàn bộ văn bản. Chưa xuất bản corpus ra ngoài.

## Danh sách nguồn đóng góp

{source_links}
'''
    write('reports/MVP1A_REVIEW.md',report)
    write('README.md',f'''
# ContractGuard — phát hiện dấu hiệu bất lợi trong điều khoản thuê nhà

Phạm vi hiện hành: hợp đồng thuê nhà ở/phòng trọ/căn hộ tiếng Việt, bảo vệ người thuê. Chỉ MVP 1, chạy NLP và học máy offline; không gọi API AI bên ngoài.

**Đã có bản MVP 1A để kiểm duyệt:** [data/clauses_rental_v1.csv](data/clauses_rental_v1.csv), gồm {rows} điều khoản có nguồn, {normal} normal và {abnormal} abnormal sơ bộ. Có lý do, ngữ cảnh, bằng chứng và SHA256. **Abnormal vẫn ít và thiếu ba nhóm dấu hiệu; chưa hứa hẹn chất lượng mô hình.** Toàn bộ nhãn draft/pending; chưa có dataset/model/metrics chính thức được duyệt.

Đọc [báo cáo dữ liệu và giới hạn](reports/MVP1A_REVIEW.md), [trạng thái MVP 1](reports/MVP1_STATUS.md), [hướng dẫn chạy](docs/RUN_MVP1.md), [schema và chủ đề phụ](docs/RENTAL_DATASET_SCHEMA.md), [ánh xạ Lab](docs/LAB_MAPPING.md).

Người dùng đã duyệt tiêu chí thuê nhà tại [hồ sơ xác nhận](reports/rental_criteria_approval.json). Duyệt tiêu chí chưa phải duyệt dataset. Chỉ người dùng xác nhận Dataset Đạt/Chưa đạt; agent chịu trách nhiệm nhãn, sửa nguồn và bổ sung.

[data/clauses.csv](data/clauses.csv) là bộ 752 dòng ngoài miền được bảo toàn. Có 7 câu chung tái sử dụng ở CSV phụ trợ riêng, 0 dòng được đổi thành nguồn thuê nhà. Không dùng bộ cũ làm kết quả thuê nhà.

Khung offline đã có preprocessing, TF-IDF/char n-gram, Naive Bayes/Logistic Regression/SVM và save/load/inference để kiểm thử kỹ thuật. Chỉ bắt đầu thực nghiệm corpus thuê nhà sau kiểm duyệt và tích hợp gate đúng profile. Không làm backend/giao diện/MVP 2–4 trong giai đoạn này.
''')
    write('data/README.md',f'''
# Dữ liệu ContractGuard

**Bản thuê nhà hiện cần kiểm duyệt:** [clauses_rental_v1.csv](clauses_rental_v1.csv), {rows} dòng, {normal} normal/{abnormal} abnormal sơ bộ, UTF-8 BOM. Chưa được duyệt, chưa dùng làm ground truth hay train chính thức. Xem [báo cáo và giới hạn](../reports/MVP1A_REVIEW.md).

- `rental_mvp1a_v1/sources.json`: {audit['source_documents']} nguồn đóng góp, URL/raw/pages/SHA256, họ mẫu và trạng thái nguồn.
- `rental_mvp1a_v1/raw`: archive tải được, gồm cả chỉ mục/tư vấn/bản sao; không phải mọi mục là hợp đồng hợp lệ.
- `rental_mvp1a_v1/candidates.json`: {audit['candidate_count']} ứng viên kỹ thuật; phần chưa có quyết định vẫn trống nhãn, không mặc định normal.
- `rental_mvp1a_v1/annotation_decisions.json`: quyết định sơ bộ tường minh; `annotation_ledger.json` ghi chọn/dự trữ/hold, phục vụ agent, không phải danh sách người dùng phải sửa.
- `rental_mvp1a_v1/legacy_auxiliary.csv`: 7 câu giải quyết tranh chấp chung từ bộ cũ, ngoài train/test thuê nhà chính.
- `rental_mvp1a_v1/review_snapshot.json`: hashes của đúng bản để duyệt; `extraction_history` giữ các lần sửa trích.
- `clauses.csv`, `sources.json`, `raw`, `review`, `snapshots`: hồ sơ legacy 752 dòng không có provenance thuê nhà; giữ nguyên để truy vết. Không suy miền thuê nhà từ câu chữ chung.
- `rental_staging`: pilot Chính phủ từ lượt trước; không cộng lặp 10 mẫu pilot vào số hiện tại.

Tiêu chí đích ở `docs/LABELING_GUIDELINES.md` đã được duyệt. `label`/`risk_label` là normal/abnormal; `clause_type`/`category` chỉ là chủ đề phụ. `risk_category` là mã giải thích, không phải các lớp chủ đề thay mục tiêu. `label_confidence` là nhận định sơ bộ, không phải xác suất hay accuracy. Mọi reviewer/verified label hiện trống. Không sửa approval để thử train.
''')
    write('reports/MVP1_STATUS.md',f'''
# Trạng thái hiện hành ContractGuard

**Đang ở điểm kiểm duyệt MVP 1A, chưa hoàn thành MVP 1.** Tiêu chí thuê nhà đã được người dùng duyệt; dataset thuê nhà chưa được duyệt. Chưa có model/metrics chính thức. Chưa sang MVP 1B hoặc MVP 2.

Bản để duyệt: [clauses_rental_v1.csv](../data/clauses_rental_v1.csv), {rows} dòng = {normal} normal + {abnormal} abnormal, nhãn draft/pending, {audit['source_documents']} nguồn đóng góp/{audit['contract_templates']} mẫu. Xem [MVP1A_REVIEW.md](MVP1A_REVIEW.md) để biết nguồn, quyết định nhãn, kiểm tra và giới hạn.

Đã thực hiện: khảo sát/ánh xạ Lab; giữ master prompt; ghi xác nhận tiêu chí thật; mở rộng thu thập; sửa extraction; nhãn có lý do/bằng chứng/ngữ cảnh; nguồn/hash/spans; kiểm tra trùng/họ mẫu; review CSV/CLI; giữ nguyên bộ 752 dòng lịch sử và tách 7 câu phụ trợ ngoài miền.

**Chưa đạt mong muốn abnormal nhiều:** {abnormal} mẫu, có ở {audit['abnormal_source_documents']} nguồn và 6 nhóm dấu hiệu; thiếu abnormal cho deemed_consent, automatic_renewal và overbroad_data_use. Không làm giả hoặc nhân bản mẫu để tăng tỷ lệ. Cần thêm nguồn vận hành khác họ trước khi kỳ vọng đánh giá vững. Quy mô hiện tại dưới mục tiêu tham khảo 1.500–3.000 trong prompt.

Còn phải làm để qua MVP 1B: người dùng kiểm duyệt dataset/nguồn; agent sửa khi Chưa đạt, chốt bản/hashes theo quyết định thật; tích hợp đúng profile tiêu chí/nguồn thuê nhà vào training gate; chốt chia nhóm và kiểm tra support của abnormal. Sau đó mới thực nghiệm BoW/TF-IDF, NB/LR/SVM, đánh giá, save/load và inference offline. Không tự chốt nhãn test dựa vào dự đoán.

Các số trong `rental_dataset_audit.json` là kiểm tra dữ liệu, không phải chất lượng mô hình. Test kỹ thuật dùng fixture technical_test; kết quả không phải Accuracy/F1 trên corpus thật. Báo cáo lịch sử trước bản thuê nhà được giữ tại `reports/history/before_rental_v1_handoff`.
''')
    write('docs/RUN_MVP1.md',r'''
# Chạy kiểm tra và đọc dataset thuê nhà MVP 1A

Thư mục dự án: `D:\NLP\ContractGuard`. Dataset hiện cần xem là `data/clauses_rental_v1.csv`; không dùng các lệnh train hoặc readiness legacy để chứng nhận corpus thuê nhà.

## Đọc toàn bộ nhãn và nguồn cục bộ

```powershell
Set-Location D:\NLP\ContractGuard
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --label abnormal --count 30
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --clause-id roomi_registration_0052
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --start 0 --count 20
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --start 20 --count 20
```

CSV mở trực tiếp được bằng Excel; lọc label, risk_category, clause_type, nguồn. Cả CSV và CLI đều cho đọc toàn bộ dữ liệu, không chỉ ví dụ. Không cần người dùng gán hoặc nhập nhãn thay agent. Có thể xác nhận “Dataset thuê nhà Đạt” hoặc “Chưa đạt” sau khi xem báo cáo `reports/MVP1A_REVIEW.md`. Tiêu chí đã được duyệt, không cần duyệt lại.

## Kiểm tra và tái đóng gói đúng snapshot

```powershell
.venv\Scripts\python.exe -X utf8 -m pip check
.venv\Scripts\python.exe -X utf8 -m pytest -q --junitxml=reports/rental-test-results.xml
.venv\Scripts\python.exe -X utf8 tools/package_rental_dataset.py
.venv\Scripts\python.exe -X utf8 tools/write_rental_handoff.py
```

Đóng gói chỉ đọc raw/candidates và quyết định nhãn ID tường minh, kiểm tra hash rồi viết lại CSV/audit. Không fetch, không huấn luyện, không đổi approval. Snapshot ứng viên thay đổi thì tool dừng để agent kiểm tra nhãn thay vì gán vào nhầm ID. Không chạy lại các script snapshot/migration một lần nếu chưa hiểu version history. `build_rental_candidates.py` phục vụ tạo phiên bản ứng viên mới; không được coi ID mới là đã có nhãn đúng.

## Môi trường thu thập tùy chọn

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -X utf8 -m pip install -r requirements-rental-collection-lock.txt
.venv\Scripts\python.exe -X utf8 -m pip install --no-build-isolation --no-deps -e .
```

`rental_corpus.py fetch --config configs/rental_collection_v9.json` tải URL công khai trong manifest nếu chưa có raw, cần quyền mạng thông thường của host. Không vô hiệu TLS hoặc bypass 403. `prepare-html`, `prepare-pdf` tạo text có phiên bản, không ghi đè raw. Công cụ dùng requests/BeautifulSoup, OOXML ZIP, pypdf/pdfplumber; không gọi API AI.

## Trước huấn luyện thật

`configs/rental_approval.json` vẫn dataset_approved=false/source_use_confirmed=false. `approved_by`/`approved_at`/hash bản được duyệt vẫn trống. CLI training cũ dùng profile tổng quát/legacy và chưa được phép dùng cho corpus mới. Sau quyết định duyệt thật, agent còn phải tích hợp gate đúng tiêu chí thuê nhà, chốt nhóm chia và support rủi ro, rồi mới sang MVP 1B. Chưa có model thật để chạy inference sản phẩm; kiểm thử save/load/toy không thay kết quả thực nghiệm.
''')
    write('reports/MVP1A_REQUIREMENTS_CHECKLIST.md',f'''
# Đối chiếu MVP 1A với master prompt

| Yêu cầu | Kết quả hiện tại |
|---|---|
| Khảo sát tài liệu, không sửa Lab gốc | `docs/LAB_MAPPING.md`, báo cáo khảo sát đã có; 9 notebook được đối chiếu trước đợt thu thập này |
| Đúng miền/góc nhìn | Thuê nhà ở, bảo vệ người thuê; nguồn thương mại, xe, ngân hàng/viễn thông không trộn vào chính |
| Chủ động tìm nguồn | {acquisition['attempted_sources']} URL thử mới, {acquisition['downloaded_sources']} raw tải được; {audit['source_documents']} nguồn vào CSV, có archive/hash |
| Mục tiêu số lượng có điều kiện | {rows} đơn vị giữ lại; chưa đạt 1.500–3.000. Báo số thật, không tạo câu giả |
| Tăng abnormal | {abnormal} sơ bộ, 6 cơ chế/{audit['abnormal_source_documents']} nguồn; **chưa đạt mong muốn nhiều**, thiếu 3 cơ chế |
| Lấy phần phù hợp trong 752 | 0 primary thuê nhà vì provenance ngoài miền; 7 câu chung vào auxiliary riêng |
| Sửa trích trước trình duyệt | DOM inline/block/nested list, PDF wraps/tham chiếu/số bản, phạm vi tuyển tập đã sửa cho mẫu giữ lại; lịch sử và spans còn nguyên |
| Schema tối thiểu | Có contract_id, clause_id, text, category, risk_label, source, label_reason, label_confidence, review_status; các alias phải khớp |
| Tiêu chí duyệt trước gán hàng loạt | Người dùng đã xác nhận “Tiêu chí thuê nhà Đạt”, hash giữ nguyên; không cần hỏi lại |
| Gán sơ bộ, lý do và thiếu dữ kiện | Quyết định ID tường minh, evidence/context, draft/pending; không có quyết định thì không gán normal |
| Review toàn bộ ở local | CSV UTF-8 BOM + CLI lọc/đọc toàn bộ; ưu tiên abnormal/medium/đối chứng; người dùng chỉ Đạt/Chưa đạt |
| Không tự duyệt/AI API/MVP 2 | Gate dataset đóng; không API AI, không model thật/metrics, không frontend/backend |
| Kiểm tra kỹ thuật | `reports/rental_dataset_audit.json` và `rental-test-results.xml`; không phải accuracy/F1 corpus |
| Điểm dừng mục 8 | Trình bản v1 và giới hạn; chờ kiểm duyệt thật trước MVP 1B; phần tăng độ phủ dữ liệu vẫn cần tiếp tục |
''')
    print('Wrote current handoff, schema references and archived older scope docs; approvals unchanged.')

if __name__=='__main__':main()
