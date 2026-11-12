# ContractGuard — project instructions

- Mục tiêu cốt lõi: phát hiện dấu hiệu rủi ro/bất lợi trong nội dung điều khoản hợp đồng. Không thay bằng bài toán phân loại chủ đề.
- Nhãn đích đề xuất normal/abnormal. payment/confidentiality/other... chỉ là clause_type phụ; không suy ra bất thường từ chủ đề và không tự gán bình thường khi chưa đủ căn cứ.
- CSV chính là data/clauses.csv. Không tạo thêm Excel thay dataset; các Excel/CSV review cũ là lịch sử của hướng gán chủ đề sai.

- Chỉ triển khai MVP 1: dataset, gán nhãn, preprocessing, training, evaluation, inference offline.
- Có thể thiết kế tổng thể đến MVP 4 trong tài liệu. Không viết giao diện/backend MVP 2, truy hồi điều khoản MVP 3 hoặc SQLite/quản lý hợp đồng MVP 4 khi chưa được người dùng cho phép.
- Không gọi API AI bên ngoài. Tải nguồn công khai và thư viện phục vụ NLP được phép trong phạm vi công việc thông thường.
- Người dùng phải xác nhận tiêu chí gán nhãn và kiểm duyệt dataset trước huấn luyện chính thức. Không tự phê duyệt thay người dùng; không đổi cờ approval hoặc tên reviewer để vượt gate.
- Agent gán nhãn sơ bộ, giải thích và đề xuất giữ/loại. Người dùng chỉ xác nhận Đạt/Chưa đạt, không tự gán hoặc nhập nhãn thay agent.
- Agent phải sửa lỗi trích/ghép/tách từ nguồn trước khi gửi duyệt. Không coi lỗi do bộ trích là lý do bỏ điều khoản hợp lệ; không đẩy danh sách lỗi/đề xuất loại sang người dùng. Dữ liệu hiện tại: data/clauses.csv, xem data/README.md.
- label có thể chứa nhãn sơ bộ khi annotation_status=draft và review_status=pending; không coi đó là ground truth đã duyệt.
- Giữ provenance và SHA256; gợi ý từ khóa không phải nhãn chuẩn. Không tạo dữ liệu giả hoặc số liệu thực nghiệm giả để làm kết quả chính thức.
- Dữ liệu giả chỉ dùng cho unit/integration test có đánh dấu `technical_test`; không dùng để báo chất lượng MVP 1.
- Không dùng model của các Lab tin tức/intent làm model ContractGuard. Không sao chép điểm trong báo cáo Lab sang báo cáo dự án.
- Kiểm thử toàn bộ, kiểm tra save/load và inference, báo Accuracy/Precision/Recall/F1/confusion matrix chỉ khi đã thực nghiệm trên dataset được duyệt.
- MVP 1 hiện chưa hoàn thành. Xem `reports/MVP1_STATUS.md` và hồ sơ kiểm duyệt trước khi tiếp tục.
- Sau khi hoàn thành MVP 1 phải dừng. Chỉ bắt đầu MVP 2 khi người dùng xác nhận MVP 1 đạt yêu cầu và cho phép thực hiện.
