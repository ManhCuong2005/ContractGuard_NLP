# ContractGuard — phát hiện dấu hiệu bất lợi trong điều khoản thuê nhà

Phạm vi: hợp đồng thuê nhà/phòng/căn hộ tiếng Việt, bảo vệ người thuê. Chỉ triển khai MVP 1 offline; không gọi API AI bên ngoài.

**Mở rộng dữ liệu ngày 09/11/2026:** [v2 draft](data/clauses_rental_v2.csv) có **820 mẫu = 788 normal + 32 abnormal**, kế thừa nguyên 517 mẫu v1 và thêm 303 mẫu sau khử trùng. **Chưa đạt yêu cầu 1.000–2.000 mẫu/500 abnormal**; chỉ thêm được 4 abnormal. Xem [báo cáo nguồn, thiếu hụt và cách review](reports/RENTAL_EXPANSION_V2_REVIEW.md), [data card](docs/RENTAL_V2_DATA_CARD.md). V2 chưa được duyệt/chưa train; quyết định v1 không áp dụng cho v2.

**MVP 1A đã được người dùng duyệt bằng câu “Dataset thuê nhà Đạt”. MVP 1B đã chạy thực nghiệm truyền thống nhưng chất lượng phát hiện abnormal chưa đạt; toàn bộ MVP 1 chưa hoàn thành.**

[Dataset được duyệt](data/rental_approved_v1/clauses.csv): 517 điều khoản, 489 normal và 28 abnormal, 17 tài liệu nguồn; nhãn/lý do/ngữ cảnh/provenance giữ nguyên bản đã trình. [Hồ sơ xác nhận](reports/rental_dataset_approval.json) ghi quyết định thật, không tự phê duyệt. [Bản draft](data/clauses_rental_v1.csv) và [752 mẫu legacy](data/clauses.csv) được bảo toàn.

Đã so sánh 23 cấu hình gồm Dummy, BoW/TF-IDF/ngram và NB/LR/SVM trên validation. Mô hình được chọn là BoW unigram + Logistic Regression. **Test: Accuracy 93,62%, nhưng Recall abnormal 0% — bỏ sót 6/6 điều khoản bất lợi, bằng Dummy trên tập test.** Không dùng Accuracy này để kết luận mô hình tốt. Save/load và inference offline đã chạy; model chỉ dùng nghiên cứu ở trạng thái hiện tại.

Đọc [báo cáo thực nghiệm và sáu lỗi](reports/MVP1B_EXPERIMENT_REPORT.md), [trạng thái/phần còn lại](reports/MVP1_STATUS.md), [hướng dẫn chạy](docs/RUN_MVP1.md), [schema](docs/RENTAL_DATASET_SCHEMA.md), [ánh xạ Lab](docs/LAB_MAPPING.md). Thư mục `outputs/rental_mvp1b_v1` giữ model, metrics, split/precommit, dự đoán, phân tích và biểu đồ PNG/SVG.

Bước tiếp theo vẫn thuộc MVP 1: tăng dữ liệu bất lợi thật và đa dạng nguồn, kiểm duyệt phiên bản mới, thực nghiệm theo validation và giữ test mới chưa dùng để chọn mô hình. CNN/BiLSTM chưa triển khai; không có kết quả deep learning. Không bắt đầu MVP 2 cho đến khi người dùng xác nhận MVP 1 đạt và cho phép.
