# Kiến trúc ContractGuard — nhận diện dấu hiệu rủi ro/bất lợi

## Bài toán và ranh giới

Đầu vào NLP là điều khoản tiếng Việt kèm ngữ cảnh hợp đồng nguồn khi cần. Nhãn đích đề xuất: normal / abnormal. Thanh toán/bảo mật/chấm dứt... chỉ là clause_type, không trả lời điều khoản có dấu hiệu rủi ro hay không.

Chỉ triển khai MVP 1: thu thập, sửa dữ liệu, gán nhãn sơ bộ, preprocessing, training, evaluation và inference cục bộ. Hiện chưa có dataset/mô hình rủi ro được duyệt, chưa có kết quả phát hiện bất thường chính thức.

## Dữ liệu và luồng xử lý

`data/raw → sửa bản trích có provenance → data/clauses.csv → gán label rủi ro + lý do → người dùng xác nhận → khóa dataset/split theo hợp đồng → train/validation/test → lưu model → dự đoán điều khoản mới`

| Thành phần | Trách nhiệm |
|---|---|
| data/raw và data/sources.json | Giữ nguồn thật, trang và SHA256 |
| data/clauses.csv | Dataset CSV chính; text, label, lý do, trạng thái xác nhận và nguồn |
| clause_type trong CSV | Metadata chủ đề cũ; không dùng thay nhãn normal/abnormal |
| docs/ANNOTATION_GUIDELINES.md | Tiêu chí rủi ro cụ thể cần xác nhận |
| configs/labels.json, approval.json | Nhãn đích và cổng duyệt đúng phiên bản bài toán/dữ liệu |
| text.py, provenance.py, dataset.py | Chuẩn hóa, đối chiếu nguyên văn, audit và chống rò rỉ dữ liệu |
| model.py, training.py, cli.py | Khung ML cục bộ có thể tái sử dụng cho nhãn rủi ro sau khi dataset được duyệt |

Các CSV dưới data/review và Excel/tooling dưới archive/topic_workflow thuộc lịch sử phân loại chủ đề/sửa dữ liệu. Không coi các bản đó là dataset đã gán nhãn bất thường. Không chuyển nhãn chủ đề thành normal/abnormal hoặc suy ra normal từ việc không thấy từ khóa. Thu thập thêm dùng data/candidates.csv làm staging, không ghi đè CSV chính hoặc bản review lịch sử.

## Mô hình và thực nghiệm

Khung baseline dự kiến TF-IDF + NB/LR/SVM, so với Dummy. Phải tự fit trên dữ liệu thật đã duyệt; không gọi API AI hoặc dùng model Lab tin tức/intent thay model ContractGuard. Chưa quyết định cấu hình tốt nhất khi chưa có thực nghiệm.

Gom hợp đồng/họ mẫu/đoạn gần trùng, chia train/validation/test không chồng nhóm. Fit vectorizer chỉ train, chọn cấu hình bằng validation, đánh giá test độc lập. Báo Accuracy, Precision/Recall/F1 macro và riêng lớp abnormal, support từng lớp, confusion matrix và lỗi mẫu. Không kết luận tốt chỉ từ Accuracy khi lớp bất thường ít.

Lưu toàn pipeline và metadata task=contract_anomaly_detection, bộ nhãn, phiên bản tiêu chí/dataset, hashes, seed/split và thư viện. Kiểm tra dự đoán không đổi sau save/load. Dự đoán mới trả normal/abnormal; hiện chỉ abstain khi đầu vào không có feature đã học. Chưa có bộ phát hiện tổng quát thiếu ngữ cảnh/ngoài miền hoặc confidence đã hiệu chỉnh. Không gọi nhãn đó là kết luận pháp lý hay điểm rủi ro hợp đồng đã được hiệu chỉnh.

Khung hiện có kiểm thử phần mềm bằng fixture. Những kiểm thử đó chưa chứng minh chất lượng nhận diện rủi ro. Muốn hoàn thành MVP 1 phải có nhãn thật được duyệt, train thật, đánh giá thật và script chạy thử.

## Mở rộng đến MVP 4 — chỉ thiết kế

| Giai đoạn | Tích hợp tương lai | Điều kiện |
|---|---|---|
| MVP 2 | Upload hợp đồng, trích/tách, gọi NLP và hiển thị điều khoản bị cảnh báo cùng nguồn/ngữ cảnh | Người dùng xác nhận MVP 1 đạt và cho phép |
| MVP 3 | Truy hồi điều khoản tương tự, cải tiến biểu diễn/model và đánh giá riêng | Cho phép riêng |
| MVP 4 | SQLite, lưu hợp đồng/lịch sử phân tích/model version | Cho phép riêng |

Không viết code cho các giai đoạn này trong MVP 1. Dừng khi hoàn thành MVP 1 và chờ xác nhận.

## Hợp đồng tích hợp cho các giai đoạn sau — chỉ thiết kế

MVP 2 sẽ gọi lớp Predictor hiện có qua một adapter riêng; đầu vào từng điều khoản có clause_id, text và vị trí nguồn. Kết quả giữ label, needs_review, reason, model_id, model_purpose và confidence. Việc trích file upload, quản lý phiên, lỗi HTTP và hiển thị thuộc lớp web tương lai, không đưa vào core training. Model đã fit dùng như artifact chỉ đọc; không train theo mỗi upload.

MVP 3 sẽ có adapter truy hồi riêng, đọc corpus và phiên bản biểu diễn; kết quả tương tự không tự thay thế nhãn rủi ro. Phải đánh giá retrieval và cải tiến classifier riêng, giữ test độc lập để tránh chọn mô hình theo test cũ.

MVP 4 sẽ bổ sung repository SQLite lưu tài liệu, lần phân tích, kết quả điều khoản và phiên bản model/dataset. Hợp đồng dịch vụ ở MVP 2 gọi repository qua interface tương lai; NLP core tiếp tục chạy từ CSV/artifact và không phụ thuộc DB. Chưa tạo interface, bảng hay migration trong code.

Lệnh readiness hiện chỉ chẩn đoán khả năng train; không phải tiêu chí tuyên bố hoàn thành MVP 1. Hoàn thành còn đòi hỏi model/metrics chính thức, thử điều khoản mới và người dùng nghiệm thu.
