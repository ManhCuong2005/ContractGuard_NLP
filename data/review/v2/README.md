# Lịch sử xử lý nguồn và gán chủ đề — v2

Bản này không có nhãn normal/abnormal. File chính cho bài toán rủi ro là data/clauses.csv ở gốc dự án; các chủ đề của bản này đã chuyển sang clause_type. Nội dung bên dưới chỉ giữ để đối chiếu lịch sử, không là hướng dẫn duyệt hiện hành. Excel đã chuyển vào archive/topic_workflow/outputs; báo cáo SOURCE_REPAIR_V2.md đã chuyển vào archive/topic_workflow/reports.

Mở `outputs/annotation_20261108_v2/ContractGuard_DuyetNhan.xlsx` ở gốc dự án để xác nhận nhãn. Chỉ có một sheet Duyet nhan: người dùng chọn Đạt/Chưa đạt ở cột A, không phải gán nhãn hay duyệt danh sách lỗi.

`clauses.csv` gồm 802 đơn vị điều khoản có nhãn sơ bộ. Đã ghép câu dẫn/mục con, tách câu khác cơ chế, gỡ phần biểu mẫu/chân trang dính nội dung. Mỗi văn bản có source_spans đối chiếu đúng trang/vị trí nguồn và legacy_clause_id truy về ứng viên cũ.

Tệp nguồn gốc và toàn bộ 967 ứng viên v1 vẫn được giữ. Bản lặp được liên kết với bản chính; tiêu đề/biểu mẫu vẫn ở hồ sơ nguồn. Nhật ký xử lý nằm ở reports/repair_ledger.json. Danh sách agent cần xử lý tiếp hiện rỗng; điều này chỉ xác nhận đã xử lý các mục lỗi được ghi nhận, không bảo đảm mọi nhãn sơ bộ đều đúng.

Mọi review_status vẫn pending. Chưa phê duyệt dataset và chưa huấn luyện chính thức. Nếu nhãn Chưa đạt, agent sửa rồi gửi xác nhận lại.
