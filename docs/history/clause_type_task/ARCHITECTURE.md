# Kiến trúc ContractGuard và ranh giới MVP

## Phạm vi được triển khai

Chỉ MVP 1. Mọi mô-đun thực thi hiện có là công cụ offline phục vụ dataset, kiểm duyệt, preprocessing, training, evaluation và inference. Không có HTTP server, giao diện, vector search hoặc SQLite.

## Luồng NLP đã xây dựng

`nguồn công khai → raw PDF + SHA256 → pages.json → CSV ứng viên → người duyệt → approval + SHA256 → audit → gom nhóm chống leakage → train/validation/test → so sánh model → lưu model → inference CLI`

| Vị trí | Trách nhiệm MVP 1 |
|---|---|
| `tools/read_materials.py` | Đọc tài liệu/Lab cục bộ, lập danh mục, không chạy notebook |
| `tools/collect_sources.py` | Tải nguồn allowlist, lưu nguyên bản, provenance, trích đoạn và gợi ý từ khóa |
| `data/raw/` | PDF/HTML gốc và text từng trang (HTML = một trang logic), không gửi sang AI API |
| `data/review/clauses.csv` | Các đoạn pending/accepted/rejected, nhãn người duyệt riêng gợi ý |
| `configs/` và `docs/ANNOTATION_GUIDELINES.md` | Nhãn, tiêu chí và xác nhận bằng mã băm |
| `src/contractguard/text.py` | NFC, khoảng trắng, chữ thường; giữ phủ định/số/dấu |
| `src/contractguard/dataset.py` | Schema CSV, kiểm duyệt, đối chiếu nguyên văn, chống trùng/leakage |
| `src/contractguard/model.py` | TF-IDF và classifier, lưu/nạp, inference batch |
| `src/contractguard/training.py` | Split nhóm, so sánh validation, test, xuất metrics/report |
| `src/contractguard/cli.py` | Các lệnh audit, approval-digests, train, predict |

Hợp đồng trao đổi của NLP core là `list[str] → list[dict]`, mỗi phần tử có `text`, `label`, `needs_review`, `reason`, `model_id`, `model_purpose`, `confidence`. Confidence hiện là null vì chưa hiệu chỉnh xác suất; không đổi khoảng cách SVM thành “độ tin cậy”. Văn bản không có đặc trưng đã biết trả nhãn null để người dùng xem lại. Với văn bản ngoài miền nhưng có từ vựng trùng, model vẫn có thể đoán sai và chưa tự phát hiện được.

## Quyết định mô hình

TF-IDF âm tiết unigram/bigram + MultinomialNB / LogisticRegression / LinearSVC, thêm phương án SVM với character 3–5 gram. DummyClassifier là mốc so sánh. Tất cả học tại máy, không tải trọng số model sẵn có và không sử dụng API AI. Char n-gram giảm phụ thuộc tách từ; đây chưa phải bộ tách từ tiếng Việt theo Underthesea.

Giữ nguyên từ phủ định, phần trăm, tiền và ngày. Bộ TF-IDF âm tiết không mã hóa đầy đủ quan hệ pháp lý hay giá trị số; nhánh character giữ thêm các dấu cục bộ. Không loại stopword theo thói quen và không khẳng định đã hiểu ngữ nghĩa.

Fit riêng vectorizer trong mỗi pipeline trên train. Chọn ứng viên theo validation Macro F1, refit cấu hình được chọn trên train+validation, đánh giá test đúng một lần trong một run. Ghi nhãn thứ tự confusion matrix, support từng lớp, dự đoán sai, nhóm split, phiên bản thư viện, seed, thời gian và hash dữ liệu. Người dùng phải giữ test đóng băng qua các lần so sánh; công cụ chưa ngăn được việc cố tình chạy nhiều seed trên cùng test.

Lưu toàn pipeline trong joblib và metadata JSON cùng checksum; nạp lại và so dự đoán. Chỉ nạp artifact do dự án tạo ở máy đáng tin cậy vì joblib dùng pickle. Checksum phát hiện thay đổi ngẫu nhiên, không phải chữ ký chống giả mạo.

## Mở rộng đến MVP 4 — chỉ thiết kế

| Giai đoạn | Thiết kế tích hợp tương lai | Điều kiện bắt đầu |
|---|---|---|
| MVP 2 — Web Demo | Adapter upload → trích văn bản/tách khoản → gọi Predictor → hiển thị nhãn/ngữ cảnh/trạng thái cần duyệt; NLP core không phụ thuộc framework web | Người dùng xác nhận MVP 1 đạt và cho phép MVP 2 |
| MVP 3 — Advanced | Module biểu diễn và index tìm điều khoản tương tự, đo retrieval riêng; cải tiến model có phiên bản dataset và benchmark | Chỉ khi được cho phép riêng |
| MVP 4 — Data Management | Repository lưu contracts, clauses, analysis_runs, predictions; SQLite và migration nằm ngoài NLP core; liên kết model_id và dataset version | Chỉ khi được cho phép riêng |

Không tạo sẵn backend, router, màn hình upload, index truy hồi, bảng SQLite, migration, ORM hay repository cho các giai đoạn này. Lịch sử run JSON/CSV trong MVP 1 chỉ là bằng chứng thực nghiệm của NLP, không phải chức năng quản lý hợp đồng MVP 4.

## Điều kiện hoàn thành MVP 1

Tiêu chí + nguồn + dataset được người dùng duyệt; đủ dữ liệu độc lập; train thật; test đủ; model save/load; inference trên điều khoản mới; Accuracy/Precision/Recall/F1 và confusion matrix có nguồn gốc thực nghiệm; báo cáo hạn chế và lệnh chạy máy. Thiếu bất kỳ bước nào thì ghi trạng thái chưa hoàn thành. Dừng ở MVP 1.
