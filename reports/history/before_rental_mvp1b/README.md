# ContractGuard — phát hiện dấu hiệu bất lợi trong điều khoản thuê nhà

Phạm vi hiện hành: hợp đồng thuê nhà ở/phòng trọ/căn hộ tiếng Việt, bảo vệ người thuê. Chỉ MVP 1, chạy NLP và học máy offline; không gọi API AI bên ngoài.

**Đã có bản MVP 1A để kiểm duyệt:** [data/clauses_rental_v1.csv](data/clauses_rental_v1.csv), gồm 517 điều khoản có nguồn, 489 normal và 28 abnormal sơ bộ. Có lý do, ngữ cảnh, bằng chứng và SHA256. **Abnormal vẫn ít và thiếu ba nhóm dấu hiệu; chưa hứa hẹn chất lượng mô hình.** Toàn bộ nhãn draft/pending; chưa có dataset/model/metrics chính thức được duyệt.

Đọc [báo cáo dữ liệu và giới hạn](reports/MVP1A_REVIEW.md), [trạng thái MVP 1](reports/MVP1_STATUS.md), [hướng dẫn chạy](docs/RUN_MVP1.md), [schema và chủ đề phụ](docs/RENTAL_DATASET_SCHEMA.md), [ánh xạ Lab](docs/LAB_MAPPING.md).

Người dùng đã duyệt tiêu chí thuê nhà tại [hồ sơ xác nhận](reports/rental_criteria_approval.json). Duyệt tiêu chí chưa phải duyệt dataset. Chỉ người dùng xác nhận Dataset Đạt/Chưa đạt; agent chịu trách nhiệm nhãn, sửa nguồn và bổ sung.

[data/clauses.csv](data/clauses.csv) là bộ 752 dòng ngoài miền được bảo toàn. Có 7 câu chung tái sử dụng ở CSV phụ trợ riêng, 0 dòng được đổi thành nguồn thuê nhà. Không dùng bộ cũ làm kết quả thuê nhà.

Khung offline đã có preprocessing, TF-IDF/char n-gram, Naive Bayes/Logistic Regression/SVM và save/load/inference để kiểm thử kỹ thuật. Chỉ bắt đầu thực nghiệm corpus thuê nhà sau kiểm duyệt và tích hợp gate đúng profile. Không làm backend/giao diện/MVP 2–4 trong giai đoạn này.
