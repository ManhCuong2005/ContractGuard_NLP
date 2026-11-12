# Trạng thái hiện hành ContractGuard

**Đang ở điểm kiểm duyệt MVP 1A, chưa hoàn thành MVP 1.** Tiêu chí thuê nhà đã được người dùng duyệt; dataset thuê nhà chưa được duyệt. Chưa có model/metrics chính thức. Chưa sang MVP 1B hoặc MVP 2.

Bản để duyệt: [clauses_rental_v1.csv](../data/clauses_rental_v1.csv), 517 dòng = 489 normal + 28 abnormal, nhãn draft/pending, 17 nguồn đóng góp/19 mẫu. Xem [MVP1A_REVIEW.md](MVP1A_REVIEW.md) để biết nguồn, quyết định nhãn, kiểm tra và giới hạn.

Đã thực hiện: khảo sát/ánh xạ Lab; giữ master prompt; ghi xác nhận tiêu chí thật; mở rộng thu thập; sửa extraction; nhãn có lý do/bằng chứng/ngữ cảnh; nguồn/hash/spans; kiểm tra trùng/họ mẫu; review CSV/CLI; giữ nguyên bộ 752 dòng lịch sử và tách 7 câu phụ trợ ngoài miền.

**Chưa đạt mong muốn abnormal nhiều:** 28 mẫu, có ở 10 nguồn và 6 nhóm dấu hiệu; thiếu abnormal cho deemed_consent, automatic_renewal và overbroad_data_use. Không làm giả hoặc nhân bản mẫu để tăng tỷ lệ. Cần thêm nguồn vận hành khác họ trước khi kỳ vọng đánh giá vững. Quy mô hiện tại dưới mục tiêu tham khảo 1.500–3.000 trong prompt.

Còn phải làm để qua MVP 1B: người dùng kiểm duyệt dataset/nguồn; agent sửa khi Chưa đạt, chốt bản/hashes theo quyết định thật; tích hợp đúng profile tiêu chí/nguồn thuê nhà vào training gate; chốt chia nhóm và kiểm tra support của abnormal. Sau đó mới thực nghiệm BoW/TF-IDF, NB/LR/SVM, đánh giá, save/load và inference offline. Không tự chốt nhãn test dựa vào dự đoán.

Các số trong `rental_dataset_audit.json` là kiểm tra dữ liệu, không phải chất lượng mô hình. Test kỹ thuật dùng fixture technical_test; kết quả không phải Accuracy/F1 trên corpus thật. Báo cáo lịch sử trước bản thuê nhà được giữ tại `reports/history/before_rental_v1_handoff`.
