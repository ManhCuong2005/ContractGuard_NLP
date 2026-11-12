# Đối chiếu MVP 1A với master prompt

| Yêu cầu | Kết quả hiện tại |
|---|---|
| Khảo sát tài liệu, không sửa Lab gốc | `docs/LAB_MAPPING.md`, báo cáo khảo sát đã có; 9 notebook được đối chiếu trước đợt thu thập này |
| Đúng miền/góc nhìn | Thuê nhà ở, bảo vệ người thuê; nguồn thương mại, xe, ngân hàng/viễn thông không trộn vào chính |
| Chủ động tìm nguồn | 72 URL thử mới, 65 raw tải được; 17 nguồn vào CSV, có archive/hash |
| Mục tiêu số lượng có điều kiện | 517 đơn vị giữ lại; chưa đạt 1.500–3.000. Báo số thật, không tạo câu giả |
| Tăng abnormal | 28 sơ bộ, 6 cơ chế/10 nguồn; **chưa đạt mong muốn nhiều**, thiếu 3 cơ chế |
| Lấy phần phù hợp trong 752 | 0 primary thuê nhà vì provenance ngoài miền; 7 câu chung vào auxiliary riêng |
| Sửa trích trước trình duyệt | DOM inline/block/nested list, PDF wraps/tham chiếu/số bản, phạm vi tuyển tập đã sửa cho mẫu giữ lại; lịch sử và spans còn nguyên |
| Schema tối thiểu | Có contract_id, clause_id, text, category, risk_label, source, label_reason, label_confidence, review_status; các alias phải khớp |
| Tiêu chí duyệt trước gán hàng loạt | Người dùng đã xác nhận “Tiêu chí thuê nhà Đạt”, hash giữ nguyên; không cần hỏi lại |
| Gán sơ bộ, lý do và thiếu dữ kiện | Quyết định ID tường minh, evidence/context, draft/pending; không có quyết định thì không gán normal |
| Review toàn bộ ở local | CSV UTF-8 BOM + CLI lọc/đọc toàn bộ; ưu tiên abnormal/medium/đối chứng; người dùng chỉ Đạt/Chưa đạt |
| Không tự duyệt/AI API/MVP 2 | Gate dataset đóng; không API AI, không model thật/metrics, không frontend/backend |
| Kiểm tra kỹ thuật | `reports/rental_dataset_audit.json` và `rental-test-results.xml`; không phải accuracy/F1 corpus |
| Điểm dừng mục 8 | Trình bản v1 và giới hạn; chờ kiểm duyệt thật trước MVP 1B; phần tăng độ phủ dữ liệu vẫn cần tiếp tục |
