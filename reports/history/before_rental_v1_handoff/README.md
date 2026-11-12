# ContractGuard — MVP 1

**Cập nhật phạm vi sau đối chiếu master prompt:** người dùng giữ **thuê nhà, bảo vệ người thuê** và đã duyệt tiêu chí thuê nhà riêng. Xem [báo cáo tiến độ và việc cần làm](reports/MVP1_PROGRESS_REVIEW.md), [ánh xạ Lab](docs/LAB_MAPPING.md) và [hồ sơ duyệt tiêu chí thuê nhà](reports/rental_criteria_approval.json). Bộ 752 dòng dưới đây được giữ nguyên nhưng nằm ngoài miền thuê nhà; chưa dùng nó làm dataset chính thức cho phạm vi vừa xác nhận. [Staging thuê nhà](data/rental_staging/README.md) mới có một nguồn, 12 ứng viên nguyên Điều và 10 ví dụ normal sơ bộ; chưa đủ dữ liệu/abnormal, chưa được duyệt hoặc train.

Mục tiêu: nhận diện **dấu hiệu rủi ro/bất lợi trong điều khoản hợp đồng tiếng Việt**, tự huấn luyện mô hình tại máy. Chỉ triển khai MVP 1. Không dùng API AI bên ngoài.

**Trạng thái: chưa đạt MVP 1.** Có engine NLP offline, chưa có mô hình, chỉ số hay dataset rủi ro được người dùng phê duyệt. Xem [kết quả audit](reports/MVP1_AUDIT.md), [trạng thái](reports/MVP1_STATUS.md) và [hướng dẫn chạy](docs/RUN_MVP1.md).

Người dùng đã xác nhận **“Tiêu chí Đạt”** ngày 08/11/2026; ghi nhận tại [hồ sơ duyệt tiêu chí](reports/criteria_approval.json). Agent đã chuẩn bị **752 điều khoản: 722 normal, 30 abnormal**, có lý do và nguồn; đang chờ người dùng duyệt dataset riêng theo [hướng dẫn duyệt](reports/DATASET_REVIEW.md). Chưa cho phép training hoặc MVP 2. Văn bản tiêu chí được giữ nguyên để bảo toàn hash của phiên bản đã duyệt.

## Dữ liệu chính

[data/clauses.csv](data/clauses.csv) là CSV chính trong thư mục data, gồm 752 điều khoản đã sửa bản trích và gán nhãn sơ bộ. 802 ứng viên trước đó được giữ nguyên trong snapshot và có nhật ký cho mọi quyết định tách/ghép, liên kết bản lặp hoặc tạm giữ vì thiếu dữ kiện nguồn. Cột quan trọng:

| Cột | Chức năng |
|---|---|
| text | Điều khoản đã sửa lỗi trích/ghép; mọi sửa đổi được đối chiếu nguồn |
| label | normal / abnormal sau khi có căn cứ gán nhãn rủi ro |
| annotation_reason | Lý do/căn cứ gán nhãn |
| review_status | Quyết định xác nhận của người dùng; hiện pending |
| clause_type | Chủ đề phụ như thanh toán/bảo mật, không phải nhãn bất thường |
| source_url, trang, source_spans | Truy vết nguồn |
| source_text, text_repairs | Bản trích nguồn và nhật ký sửa khoảng trắng/font có thể replay |
| risk_evidence, context_clause_ids, context_source_pages | Trích dẫn cảnh báo và ngữ cảnh đã đọc |

CSV duyệt không còn nhãn trống. Những ứng viên chưa đủ căn cứ được giữ trong hồ sơ nội bộ để agent xử lý tiếp, không ép thành normal. Không tự biến nhãn chủ đề cũ thành nhãn rủi ro hoặc dùng từ khóa làm nhãn chuẩn.

Nguồn gốc ở data/raw. Các CSV data/review giữ để đối chiếu lịch sử; tooling và Excel chủ đề cũ đã chuyển vào archive/topic_workflow. Không dùng chúng làm dataset rủi ro chính thức. Không tạo thêm Excel thay CSV.

## Quy trình đúng

Đọc [yêu cầu đã đối chiếu](docs/PROJECT_REQUIREMENTS.md), [nội dung tiêu chí đã duyệt](docs/ANNOTATION_GUIDELINES.md) và [kiến trúc](docs/ARCHITECTURE.md). Tiêu đề bản tiêu chí được giữ như lúc xác nhận để không đổi hash; hồ sơ criteria_approval.json ghi quyết định hiện hành.

Agent thu thập/sửa dữ liệu/gán nhãn sơ bộ/giải thích. Người dùng xác nhận tiêu chí và nhãn đạt/chưa đạt. Chỉ sau khi được duyệt mới train thật, lưu/nạp, dự đoán và tổng hợp metrics. Việc xác nhận bộ nhãn chủ đề cũ không áp dụng cho nhãn rủi ro.

## Chạy kiểm tra kỹ thuật

```powershell
Set-Location D:\NLP\ContractGuard
$env:PYTHONIOENCODING = 'utf-8'
& .\.venv\Scripts\python.exe tools\verify_mvp1.py
& .\.venv\Scripts\python.exe -m contractguard audit --data data\clauses.csv
& .\.venv\Scripts\python.exe -m contractguard readiness --output reports\readiness.json
& .\.venv\Scripts\python.exe tools\inspect_annotation.py --label abnormal --count 30
```

Audit kiểm tra cả nguồn/hash/source_spans của hàng pending, không xác nhận nhãn đúng hoặc đủ điều kiện train. Readiness báo điều kiện còn thiếu; hiện official_training_ready=false. Lệnh train vẫn bị khóa. Các kiểm thử toy fixture chỉ kiểm tra phần mềm, không chứng minh chất lượng phát hiện rủi ro.

Engine TF-IDF + NB/LR/SVM học hai nhãn rủi ro. Sau khi được phép train: so sánh validation, đánh giá test theo hợp đồng/họ mẫu, kiểm tra save/load, thử điều khoản mới, báo Accuracy/Precision/Recall/F1/confusion matrix thật và hạn chế. Lệnh train/predict và các điều kiện sử dụng nằm trong docs/RUN_MVP1.md.

Tập hiện tại lệch lớp và số mẫu abnormal ít. Preflight chỉ kiểm tra có thể chia tập theo nhóm, không chứng minh chất lượng nhãn hay model; chưa có Accuracy/F1 chính thức.

Dừng sau MVP 1. Không viết giao diện/backend MVP 2, tìm tương tự MVP 3 hoặc SQLite/quản lý hợp đồng MVP 4 khi chưa được phép.
