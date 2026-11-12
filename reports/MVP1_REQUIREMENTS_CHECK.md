# Đối chiếu yêu cầu MVP 1 sau chuẩn bị dataset

**MVP 1 chưa hoàn thành.** Đã chuẩn bị dataset để người dùng duyệt; không tự phê duyệt và không huấn luyện chính thức trước quyết định đó.

| Yêu cầu | Bằng chứng / trạng thái |
|---|---|
| Chỉ triển khai MVP 1 | Core, CLI offline và công cụ dataset; kiến trúc MVP 2–4 chỉ ở tài liệu |
| Phát hiện rủi ro, không phân loại chủ đề | label normal/abnormal; clause_type chỉ là metadata, không phải đầu vào nhãn |
| Đọc tài liệu/Lab trong D:\NLP | reports/MATERIAL_REVIEW.md và materials/inventory.json; không chạy mã Lab, không mang model/điểm Lab sang dự án |
| Tiêu chí do người dùng xác nhận | reports/criteria_approval.json ghi nguyên quyết định “Tiêu chí Đạt”; hash tiêu chí không đổi |
| Agent sửa bản trích và gán sơ bộ | 42 sửa ranh giới/câu dẫn; nhật ký text repairs, source spans và quyết định từng ứng viên |
| Không loại điều khoản hợp lệ vì lỗi bộ trích | Phần tách/ghép được sửa và kiểm chứng từ nguồn; bản lặp liên kết, trường hợp nguồn thiếu dữ kiện tạm giữ riêng |
| CSV chính, không tạo Excel thay dataset | data/clauses.csv có 752 dòng nhãn/lý do; hướng dẫn reports/DATASET_REVIEW.md |
| Nguồn thật, SHA256 và provenance | 11 PDF/HTML gốc giữ nguyên, snapshot trước gán nhãn, audit 752/752 dòng khớp nguồn và replay sửa text |
| Nhãn sơ bộ khác ground truth | Toàn bộ dòng draft/pending, reviewer trống; dataset_approved=false, không giả danh người duyệt |
| Kiểm tra chống leakage | 8 nhóm hợp đồng/họ mẫu/gần trùng; abnormal ở 6 nhóm. Preflight chỉ kiểm tra chia tập, không fit model |
| Không API AI bên ngoài | Quyết định agent được ghi tường minh và áp dụng cục bộ; tải/đọc nguồn công khai không phải gọi API AI |
| Không dữ liệu/số liệu thực nghiệm giả | Fixture chỉ dùng technical_test; official_metrics=null |
| Mô hình tự huấn luyện | Có engine TF-IDF + NB/LR/SVM/Dummy; huấn luyện chính thức còn chờ dataset được duyệt |
| Accuracy/Precision/Recall/F1/Confusion Matrix | Có code xuất metrics; chưa có kết quả chính thức vì chưa được phép train |
| Lưu/nạp và dự đoán điều khoản mới | Đã kiểm thử kỹ thuật trên fixture; còn phải kiểm tra model chính thức và điều khoản mới có nguồn thật sau huấn luyện |
| Chạy toàn bộ kiểm thử | Kết quả chạy cuối tại verification.json, tests.log, test-results.xml; không xem số test qua là chất lượng NLP |
| Báo cáo hạn chế và hướng dẫn chạy | reports/DATASET_REVIEW.md, reports/MVP1_STATUS.md, docs/RUN_MVP1.md |
| Dừng sau MVP 1 | Chưa viết web/backend, truy hồi điều khoản hoặc SQLite; chưa có xác nhận nghiệm thu MVP 1/cho phép MVP 2 |

Dataset hiện lệch 722 normal / 30 abnormal; phần kiểm tra chia draft chỉ có 3 abnormal ở validation và 4 ở test. Các giới hạn này phải được báo cùng kết quả thực nghiệm về sau; không tự tuyên bố đạt chất lượng hoặc đạt MVP 1 chỉ từ việc code chạy được.

Bước tiếp theo bắt buộc: người dùng xem bản có nhãn/lý do và xác nhận dataset Đạt/Chưa đạt. Agent xử lý các mục Chưa đạt; sau khi được duyệt mới chốt đúng phiên bản/hashes, train/evaluate, kiểm tra model chính thức, bàn giao và dừng.
