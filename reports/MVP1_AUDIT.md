# Kiểm tra mức đáp ứng MVP 1 — 08/11/2026

Cập nhật sau audit: người dùng đã xác nhận “Tiêu chí Đạt”, ghi nhận tại criteria_approval.json. Bảng dưới giữ trạng thái tại thời điểm audit; trạng thái hiện hành ở MVP1_STATUS.md. Dataset vẫn chưa được duyệt và chưa training chính thức.

Cập nhật sau gán nhãn: CSV chính đã có 752 nhãn sơ bộ và hướng dẫn tại DATASET_REVIEW.md. Dữ liệu 802 ứng viên trước đó được giữ nguyên trong snapshot; các con số 802 nhãn trống trong phần khảo sát dưới là trạng thái lịch sử, không phải bản hiện hành.

**Kết luận: chưa đạt MVP 1.** Project có bộ khung kỹ thuật chạy được; phần dữ liệu rủi ro được duyệt, model tự huấn luyện trên dữ liệu đó và đánh giá thực nghiệm chính thức còn thiếu.

## Đối chiếu yêu cầu

| Hạng mục | Bằng chứng hiện tại | Kết luận |
|---|---|---|
| Đúng bài toán | Nhãn normal/abnormal; chủ đề chỉ ở clause_type | Đúng cấu hình mục tiêu |
| Nguồn thật và provenance | 802 điều khoản, 11 tài liệu, 9 họ mẫu; SHA256 và source_spans đều khớp | Đạt kiểm tra truy vết kỹ thuật |
| Dataset rủi ro | 802 nhãn rủi ro còn trống, 802 hàng pending | Chưa đạt |
| Tiêu chí và kiểm duyệt | criteria_approved=false, dataset_approved=false | Chưa đạt; không được tự xác nhận |
| Preprocessing | NFC, whitespace, lowercase; giữ phủ định và số | Có, đã kiểm thử |
| Mô hình tự huấn luyện | TF-IDF + NB/LR/SVM và Dummy; word+char alternative | Có engine, chưa có model chính thức |
| Chống leakage | Gom hợp đồng/họ mẫu/gần trùng; hiện còn 8 nhóm độc lập | Có; chưa kiểm tra đủ nhóm cho từng nhãn vì chưa gán nhãn |
| Evaluation | Validation chọn cấu hình; test tách nhóm; xuất đủ metrics và confusion matrix | Có code, chưa có kết quả chính thức |
| Save/load và dự đoán mới | Các model và engine được kiểm tra bằng technical_test | Đạt kiểm tra phần mềm; chưa kiểm tra model chính thức |
| Hướng dẫn và kiến trúc | docs/RUN_MVP1.md, docs/ARCHITECTURE.md | Có |
| Giới hạn phạm vi | Core/CLI offline; chưa có web/backend, retrieval hay SQLite | Đúng MVP 1 |

## Công việc kỹ thuật trong lần kiểm tra này

- Chạy lại kiểm thử, kiểm tra dependency, CLI và script dự đoán. Kết quả cuối có ở `verification.json`, `tests.log`, `test-results.xml`; đó không phải điểm chất lượng NLP.
- Bổ sung kiểm tra nguồn/hashes/spans cho cả hàng pending. Audit cũ bỏ qua phần này trước accepted.
- Thêm `readiness` để hiện số nhãn thiếu, điều kiện duyệt và số nhóm ứng viên; chỉ kiểm tra khả năng split sau khi có dữ liệu được duyệt. Không fit model hoặc ghi approval.
- Kiểm tra đúng scope và bằng chứng gán nhãn trước train; chặn training/loading artifact chủ đề như model rủi ro. Test khóa train dùng approval giả lập riêng, không sửa approval thật.
- Sửa công cụ đọc nhãn để dùng CSV chính và xem trang nguồn; bỏ gọi quy tắc chủ đề trong workflow hiện hành.
- Tách dữ liệu mới thu thập vào `data/candidates.csv`, tránh collector ghi đè CSV review lịch sử. Ứng viên mới vẫn phải sửa và gán nhãn trước khi đưa vào CSV chính.
- Chuyển 20 mục tooling, Excel review và bản xuất trùng của workflow chủ đề vào `archive/topic_workflow`. Giữ nguồn, CSV lịch sử và repair ledger tại chỗ. Danh sách ở `cleanup_manifest.json`.
- Lập lại inventory tài liệu/Lab: 121 mục, 116 bản riêng và 5 bản trùng byte, không lỗi trích xuất. Bản text không bao gồm OCR mọi hình; không chạy lại Lab hoặc lấy điểm Lab làm điểm dự án.

## Phải làm tiếp theo

1. Người dùng xác nhận tiêu chí rủi ro cụ thể Đạt/Chưa đạt. Có ví dụ nguồn thật và nhãn đề xuất ở `ANNOTATION_PILOT.md` để làm rõ cách hiểu; chưa phải dataset được duyệt.
2. Agent hoàn tất gán nhãn sơ bộ 802 điều khoản với căn cứ và ngữ cảnh, sửa lỗi trích/tách còn phát hiện, kiểm tra độ đa dạng và bổ sung nguồn thật. Không ánh xạ chủ đề hoặc dùng thiếu từ khóa để gán normal. Người dùng duyệt nhãn; agent xử lý Chưa đạt.
3. Khi được duyệt, kiểm tra đủ nhóm độc lập ở cả normal và abnormal; train, chọn trên validation, đánh giá test, kiểm tra model lưu/nạp và điều khoản mới thật; báo đầy đủ số liệu và lỗi. Chạy lại toàn bộ kiểm thử, bàn giao cách chạy và dừng.

## Hạn chế hiện tại

- Khớp source_spans chỉ xác nhận trung thành với text đã trích, không chứng minh đã sửa hết lỗi khoảng trắng trong PDF, đúng ranh giới nghĩa hoặc đúng nhãn. Các nguồn có chỗ tách chữ như `ch ấm dứt`; agent cần xử lý trong bước chuẩn bị dataset, không giao lỗi đó cho người dùng duyệt loại.
- 11 mẫu công khai tập trung viễn thông/dịch vụ, không đại diện toàn bộ hợp đồng và không phải hợp đồng đã ký. Số nhóm thực tế ít hơn số tài liệu; không thể coi 802 hàng là 802 mẫu độc lập.
- Việc gán nhãn có thể cần ngữ cảnh hợp đồng, trong khi classifier hiện chỉ nhận text điều khoản. Cần ưu tiên đơn vị đủ nghĩa và ghi rõ giới hạn; OOV check không thay thế phát hiện mọi trường hợp ngoài miền.
- Không có ngưỡng chất lượng nghiệm thu do người dùng xác nhận. Sau thực nghiệm phải trình cả minority recall/F1, lỗi mẫu và phạm vi áp dụng để đánh giá; không tự đặt mốc điểm hoặc tự tuyên bố hoàn thành.
- Accuracy/Precision/Recall/F1/Confusion Matrix chính thức: **chưa có**. Không dùng kết quả fixture hoặc Lab thay thế.

Yêu cầu duyệt trước train đến từ `AGENTS.md` và prompt MVP của người dùng. Việc tự chạy train để hoàn thành báo cáo lúc này sẽ vi phạm yêu cầu đó. Cờ duyệt và CSV chính không được thay đổi trong lần audit này.

Cơ chế duyệt tự động từ chối xóa workflow và hồ sơ review cũ do rủi ro mất provenance/lịch sử trước kiểm duyệt. Đã dùng phương án chuyển vào archive để giữ đầy đủ nội dung; không xóa dữ liệu lịch sử hay thay đổi thư viện ở đích junction ngoài project.
