# Trạng thái hiện hành ContractGuard

**MVP 1A đã được người dùng duyệt; thực nghiệm truyền thống MVP 1B đã chạy nhưng chưa đạt chất lượng phát hiện rủi ro. Toàn bộ MVP 1 chưa hoàn thành. Không sang MVP 2.**

Vòng mở rộng ngày 09/11/2026 tạo [v2 draft](../data/clauses_rental_v2.csv): **820 mẫu, 788 normal/32 abnormal**, gồm 517 mẫu v1 nguyên text/label và 303 mẫu mới; chỉ thêm 4 abnormal. **Chưa đạt yêu cầu 1.000–2.000 mẫu và 500 abnormal.** Nhãn mới vẫn draft/pending, chưa được duyệt và chưa huấn luyện. [Báo cáo nguồn và thiếu hụt](RENTAL_EXPANSION_V2_REVIEW.md), [data card](../docs/RENTAL_V2_DATA_CARD.md), [kiểm chứng kỹ thuật](rental_expansion_v2_verification.json). Không suy quyết định “Dataset thuê nhà Đạt” của v1 thành duyệt v2.

Ngày 09/11/2026 ghi nhận câu xác nhận “Dataset thuê nhà Đạt” trong [hồ sơ duyệt](rental_dataset_approval.json), đóng băng [dataset được duyệt](../data/rental_approved_v1/clauses.csv): 517 dòng, 489 normal/28 abnormal, 17 nguồn. Text/label giữ nguyên bản đã trình; không đổi tiêu chí, bản draft, dữ liệu 752 dòng hoặc approval legacy.

Đã tích hợp profile rental và gate đầy đủ: kiểm tra quyết định người dùng, hash tiêu chí/nhãn/dataset/nguồn, spans/proof scan, trạng thái review và miền người thuê. Chốt trước fit nhóm nguồn/họ/gần trùng: train 315 (16 abnormal), validation 108 (6), test 94 (6). Chọn 23 ứng viên bằng validation, ghi quyết định trước test; refit ứng viên thắng trên train+validation, đánh giá test một lần với Dummy.

Kết quả BoW unigram + Logistic Regression: Accuracy 93,62%, macro F1 0,4835; Precision/Recall/F1 abnormal đều 0, bỏ sót 6/6 abnormal. Ma trận normal/abnormal `[[88,0],[6,0]]`, bằng Dummy. Validation của ứng viên thắng Recall abnormal 50%, không chuyển được sang nguồn test. Đã lưu/nạp và chạy inference offline, xuất dự đoán/phân tích sáu lỗi/biểu đồ. [Báo cáo chi tiết](MVP1B_EXPERIMENT_REPORT.md).

Việc còn lại trong MVP 1:

1. Tăng abnormal có nguồn thật, khác họ; thêm các cơ chế chưa có (deemed_consent, automatic_renewal, overbroad_data_use), điều khoản tương phản/ngoại lệ và hợp đồng đại diện hơn. Agent trích/nhãn/giải thích; người dùng duyệt bản mới, không tự nhập nhãn.
2. Chốt protocol mới theo train/validation; capture warning từng ứng viên, xác minh hội tụ. Giữ test v1 là phân tích hồi cứu, thu nguồn test mới chưa dùng chọn mô hình khi công bố kết quả cải tiến.
3. CNN/BiLSTM từ đầu theo prompt chưa triển khai/huấn luyện. Baseline truyền thống hiện chưa đạt; không có căn cứ khẳng định deep learning cải thiện, không có số đo DL.
4. Hoàn thiện báo cáo cuối và tiêu chí chất lượng trên tập hợp lệ; chỉ chốt MVP 1 khi người dùng đánh giá đạt. Chưa làm backend/UI/truy hồi/quản lý hợp đồng.

Các báo cáo MVP 1A/audit/verification trước phê duyệt giữ như lịch sử, không phải trạng thái approval hiện hành hoặc metrics model. Test kỹ thuật không được dùng làm chất lượng NLP. Biên bản kiểm chứng hiện hành: `reports/rental_mvp1b_verification.json` và JUnit `rental-mvp1b-test-results.xml`.
