# Gán nhãn sơ bộ — cập nhật 08/11/2026

Agent gán nhãn sơ bộ. Người dùng chỉ xác nhận Đạt/Chưa đạt, không tự nhập nhãn. File duyệt: `outputs/annotation_20261108/ContractGuard_DuyetNhan.xlsx`.

- Đã xử lý 967 hàng: 673 đề xuất giữ có nhãn/lý do, 294 đề xuất loại có lý do.
- Trong nhóm loại, 88 bản trùng vẫn có nhãn của bản chính nhưng không tính là mẫu bổ sung; 206 đoạn chưa đủ nghĩa/lỗi trích/đa chủ đề không bị ép vào nhãn other.
- Phương pháp: quy tắc cục bộ có xét cơ chế chính và ngữ cảnh, kết hợp 146 hiệu chỉnh theo mã điều khoản sau rà soát. Đây là nhãn sơ bộ, chưa phải 967 nhãn được con người kiểm định và chưa đo được độ chính xác nhãn.

| Nhãn đề xuất giữ | Số lượng |
|---|---:|
| other | 308 |
| payment | 77 |
| confidentiality | 121 |
| termination | 63 |
| dispute | 22 |
| liability | 30 |
| force_majeure | 33 |
| duration | 19 |
| Tổng | 673 |

Quy tắc có thể bỏ sót ngoại lệ, ranh giới PDF còn cần tối ưu, nhãn còn lệch phân bố. Người dùng đánh Chưa đạt thì agent sửa rồi gửi duyệt lại, không yêu cầu người dùng gán nhãn mới.

CSV hiện tại ban đầu được phát hiện đã thành TSV/ANSI và mất dấu tiếng Việt. Không có label/reviewer/review_notes do người dùng nhập. Đã giữ byte gốc tại `data/review/backups/before_annotation_b09b560cf536/`, rồi khôi phục 967 ID từ nguồn có SHA256 khớp. Giữ original_text để đối chiếu những đoạn bỏ chữ ký/chân trang dính cuối.

Sheet Duyet nhan: Đạt = xác nhận nhãn. Sheet De xuat loai: Đạt = xác nhận loại đoạn. Chưa đạt ở bất kỳ sheet nào = agent cần xem lại. Ghi chú tùy chọn.

Mọi review_status vẫn pending, reviewer trống, dataset_approved=false. Chưa huấn luyện và chưa có chỉ số thực nghiệm chính thức. Tiêu chí 8 nhãn giữ nguyên; chỉ phân công được làm rõ theo yêu cầu mới.
