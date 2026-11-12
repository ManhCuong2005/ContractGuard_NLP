# MVP 1A đang thực hiện theo yêu cầu tiếp tục tự động

## Checkpoint hiện hành — 09/11/2026

Đã tiếp tục theo tin nhắn “tiếp tục”, không coi đó là duyệt dataset hay cho phép train.

- CSV hiện để duyệt: `data/clauses_rental_v1.csv`, **517 dòng: 489 normal, 28 abnormal sơ bộ**, 17 nguồn/19 mẫu; tất cả draft/pending. Abnormal có ở 10 nguồn và 6 mã cơ chế. Chưa đạt mong muốn abnormal nhiều; thiếu ba mã deemed_consent, automatic_renewal, overbroad_data_use. Không tuyên bố chất lượng mô hình hoặc hoàn thành toàn MVP 1.
- 72 URL đã thử, 65 raw tải được; không phải 65 hợp đồng hợp lệ. Có 1.411 ứng viên kỹ thuật, 523 quyết định draft (6 bản lặp không tính thêm), 18 hold, 870 reserve không nhãn. Không mặc định normal cho reserve. `reports/rental_dataset_audit.json` là số liệu hiện hành.
- Đã chọn 7 câu tranh chấp chung từ 752 dòng legacy vào `legacy_auxiliary.csv`, **0 primary thuê nhà** vì provenance ngoài miền. Bộ cũ, approval cũ và hai bản tiêu chí giữ nguyên hashes.
- Nguồn mới SADECO là PDF scan 6 trang (trang 6 trắng). Đã render/đọc cả sáu trang và đối chiếu hai lượt phần nguyên văn được chọn; 34 dòng chính dùng bản chép chọn lọc `pages_visual_selected_v1.json`. Manifest/proof ghi rõ đây không phải full OCR, kèm raw/page/ảnh SHA256. Spans kiểm tra bản chép đã đối chiếu ảnh, không giả là lớp text PDF tự trích. Không dùng OCR pretrained hay API AI.
- Đã bổ sung CoChinh room1 và ACC đúng URL chứa phòng trọ; ACC cũ có mục đích cửa hàng vẫn ngoài miền. Không gán rủi ro cho giá SADECO chỉ từ câu tối thiểu 4% vì Điều 5 đòi hai bên ký phụ lục; giữ chờ nội bộ. Cơ chế ngừng điện/nước và kiểm tra đột xuất có nhãn theo tiêu chí đã duyệt.
- Code thu thập/trích/đóng gói/read-only review trong tools; explicit decisions tại `rental_annotation_decisions.py`, bị ràng buộc hash candidate. Thay candidate phải rà lại nhãn, không dùng nhầm ID. Các script migration/snapshot chỉ chạy một lần; không chạy lại mù.
- Snapshot bản 466/23 trước mở rộng ở `data/rental_mvp1a_v1/dataset_history/before_worker_extension_466`. Source/raw và extraction history không xóa.
- Đã sửa mất dấu của các câu xác nhận chat, giữ bản trước sửa ở `reports/approval_encoding_history`; không thay quyết định duyệt dataset. `configs/rental_approval.json` vẫn dataset/source false, reviewer trống.
- **94 tests passed**, pip check sạch, compileall thành công. Chỉ test kỹ thuật/toy fixture; không train/evaluate corpus thật. Kết quả `reports/rental-test-results.xml`.
- Tài liệu hiện hành: `reports/MVP1A_REVIEW.md`, `reports/MVP1_STATUS.md`, `docs/RENTAL_DATASET_SCHEMA.md`, `docs/RUN_MVP1.md`; README/data README đã cập nhật. Handoff nói thẳng mục tiêu abnormal nhiều chưa đạt. Người dùng chỉ Đạt/Chưa đạt khi duyệt, không nhập nhãn thay agent. Chưa được nhảy MVP 1B/MVP 2.

Các mục bên dưới là checkpoint lịch sử trước khi hoàn tất đóng gói; không dùng các số 47 nguồn/zero labels hay việc còn thiếu alias từ chúng thay trạng thái hiện hành.

Người dùng yêu cầu trực tiếp hoàn tất MVP 1A: tạo dataset mới, tận dụng phần phù hợp từ 752 dòng, tìm thêm nguồn thật, abnormal nhiều và đa dạng, agent tự sửa và gán nhãn; chỉ xin kiểm duyệt dataset cuối, không train trước duyệt.

Phạm vi đã xác nhận: thuê nhà ở/bảo vệ người thuê. Tiêu chí thuê nhà đã được duyệt trong chat. Không được coi số trang tải được hoặc số ứng viên là dataset đã hoàn thành.

## Trạng thái làm việc

- Bộ cũ data/clauses.csv và approval cũ chưa đổi.
- Đã tải 47 đầu mối/tài liệu vào data/rental_mvp1a_v1/raw; collection_manifest.json giữ mọi raw/hash, nhiều mục là chỉ mục/hướng dẫn hoặc bản trùng, chưa phải 47 nguồn hợp lệ.
- configs/rental_collection_v1..v5.json là danh sách tải. Một số nguồn TLS/403 không lấy được, không vượt kiểm soát truy cập.
- Đã cài pdfplumber==0.11.9 (Pillow, pypdfium2, pdfminer, cryptography...). Chưa cập nhật lock tùy chọn; cần ghi versions chính xác trước bàn giao.
- Đã dùng PDF skill; render và xem Sunshine trang 15 tại reports/rental_source_quality/sunshine_page15.png. Cần xem thêm các trang có nhãn abnormal để đối chiếu.
- tools/rental_corpus.py: fetch, prepare-html, prepare-pdf, headings, show. pages_semantic_v2.json là bản HTML sửa từ DOM, giữ v1; pages_geometry.json là PDF theo vị trí. Không coi pypdf một dòng là đúng đơn vị.
- configs/rental_contracts_v1.json chọn các đoạn thuê nhà trong anthology; cần tiếp tục sửa vì **cochinh_social thực ra là thuê mua nhà ở xã hội**, phải bỏ khỏi dataset chính theo tiêu chí. Một số anthology có phần văn phòng/nhà xưởng, không trộn vào nhà ở.
- tools/build_rental_candidates.py đã tạo 1.280 ứng viên ở lần v2, KHÔNG gán nhãn; còn nhiều chỗ trống/metadata và vài lỗi ranh giới đã phát hiện. V1 bị tách theo dòng PDF được giữ trong extraction_history/v1_line_boundaries. Mã builder vừa sửa thêm Điều tham chiếu (không phải heading), Điều có câu nghĩa vụ trên cùng dòng, numbered cross-reference, nested roman i. Cần snapshot bản 1.280 và rebuild trước annotation.
- tools/read_rental_candidates.py dùng đọc batch/priority; --priority CHỈ lọc để rà, không tự gán nhãn.
- reports/rental_source_quality/sunshine_vi_reading.txt là bản đọc chỉ tiếng Việt; source_spans cuối vẫn đối chiếu pages_geometry.json song ngữ, không đối chiếu bản đọc này.

## Những điểm đã học để không gán sai

- 752 dòng cũ thuộc 11 nguồn ngoài miền thuê nhà; chưa tìm thấy điều khoản có provenance thuê nhà. Có thể dùng một số câu giải quyết tranh chấp hoàn toàn chung làm auxiliary_only ở CSV riêng, KHÔNG trộn vào primary thuê nhà hoặc đổi danh xưng nguồn. Các ID phù hợp đã đọc: viettel_stracking_2026_0202, viettel_tv_personal_0075, fpt_internet_0072, fpt_domain_legacy_0031, fpt_server_legacy_0033, fpt_phone_business_0045, moj_transport_template_0054. Phải rà/có lý do trước ghi, giữ provenance và nhãn draft/pending.
- Nguồn Cenhomes Sunshine 54 trang là lease căn hộ dài hạn cho người nước ngoài, có phần chuyển sở hữu; giữ subtype riêng, không trộn phần mua/chuyển sở hữu 10.3 vào primary thuê nhà. Có rủi ro rõ: nghĩa vụ bồi thường thiệt hại gián tiếp (6.2 n); làm mọi việc theo đánh giá chủ nhà (6.2 r); toàn bộ rủi ro nhà thuộc tenant trừ vi phạm chủ nhà đã quy định (6.2 c); sửa nhà sau warranty (9.6, đọc 9.5 và ngoại lệ); phí điều chỉnh bằng thông báo (11.6 a); hoàn tiền sau thanh lý chỉ khi bán/cho thuê lại, chủ nhà quyết giá và hoàn mức thấp hơn (13.1 d/g); không hoàn tiền trả trước khi nhà không dùng được do bất khả kháng (13.1 e B). Đây là ứng viên cần lý do/căn cứ, không phải nhãn đã khóa.
- Đừng gán 8.4 Sunshine là abnormal chỉ vì mặc nhiên nhận bàn giao: có báo trước, quyền từ chối có lý do 6.1f, cần cân nhắc đầy đủ.
- Đừng gán phạt 16% là abnormal chỉ vì thấy cao; hai bên có cơ chế đối ứng và tiêu chí không có ngưỡng tự đặt.
- Thuecanho123: 8.3 mất cọc tenant chấm dứt phải đọc 8.6 được chấm dứt không bồi thường khi bên kia vi phạm; không bỏ ngoại lệ. 6.1 wording chấm dứt trước 5 ngày đầu kỳ có thể mơ hồ, không tự chắc chắn.
- Homedy simple/CoChinh house/MinhKhue simple có khoản tenant chịu mọi mất mát khi bỏ trống, không phân biệt nguyên nhân; cần giữ toàn câu dẫn và số ngày/ngoại lệ, có thể broad_liability, không chỉ chủ đề.
- Resident apartment có phí mọi vấn đề bên thứ ba do tenant chịu; cần đọc nguồn xung quanh.
- Nhiều nguồn là bài tư vấn/không có nguyên hợp đồng: Akihome/Roomi/Omnistay không được biến lời “nên ghi” thành điều khoản thật. locloc chỉ là hướng dẫn; quanlynhatro_room URL thực tế redirect ra hướng dẫn dùng app khác search snippet, không lấy snippet làm nguồn.
- Benri có dữ liệu điền sẵn kiểu ví dụ; chưa chọn primary. Không thu thập các link user-generated resident CDN có thể lộ thông tin nhạy cảm/không rõ công khai.

## Việc còn làm để bàn giao MVP 1A

1. Hoàn thiện ranh giới/contract scope, rebuild ứng viên có provenance, rà toàn bộ nội dung thực dùng; không đẩy lỗi extraction cho user.
2. Gán nhãn bằng quyết định agent TƯỜNG MINH cho mọi ứng viên chính, kèm lý do/evidence/confidence, không mặc định normal do thiếu keyword. Hold riêng phần thực sự thiếu dữ kiện; metadata/ngoài miền/trùng có ledger nội bộ.
3. Dedup theo nội dung và họ mẫu; giữ nhóm nguồn, không lấy nhiều bản chép một mẫu thành dữ liệu độc lập. Tăng nguồn thật cho abnormal theo tiêu chí; không ép nhãn để đạt số lượng.
4. Xuất data/clauses_rental_v1.csv (người dùng cho phép file mới), source manifest riêng, annotation ledger, phụ lục legacy_auxiliary và báo cáo quy trình/coverage/counts/split preflight KHÔNG fit.
5. Kiểm tra encoding: **hồ sơ reports/rental_criteria_approval.json và configs/rental_approval.json từ lượt trước bị mất dấu ở confirmation_quote do PowerShell stdin**. Sao lưu rồi sửa chính xác hai câu quote đã có trong chat; không đổi quyết định/tiêu chí/hashes để vượt gate. Dùng apply_patch hoặc file Python UTF-8, không gửi literal tiếng Việt qua PowerShell here-string (có thể bị đổi sang ?).
6. Kiểm thử meaningful pipeline dữ liệu mới + toàn bộ 86 tests hiện có, spans/hash/save preservation, chống trùng, coverage, không API AI/không training. Lưu audit và hướng dẫn CSV người dùng chỉ Đạt/Chưa đạt.
7. Báo số thật, nêu mọi giới hạn support/nhóm dấu hiệu chưa có; chỉ tuyên bố phần chuẩn bị 1A xong nếu đã làm xong, còn human dataset review theo gate. Không sang 1B/MVP2.

Chưa tạo model/artifacts, chưa sửa cờ phê duyệt dataset. Tiếp tục công việc, không coi file worklog này là bàn giao hay lý do dừng.


## 09/11/2026 — duyệt dataset và thực nghiệm MVP 1B

Đã nhận xác nhận thật “Dataset thuê nhà Đạt”, đóng băng snapshot riêng, tích hợp rental profile và gate, chia theo nhóm trước fit; chạy 23 ứng viên trên validation, refit winner BoW+LR và test một lần. Recall abnormal test 0/6; không đạt mục tiêu cảnh báo, không chuyển MVP 2. Đã lưu/nạp/inference, phân tích lỗi, biểu đồ và báo cáo. Bản draft/legacy giữ nguyên. Xem `MVP1B_EXPERIMENT_REPORT.md`.
