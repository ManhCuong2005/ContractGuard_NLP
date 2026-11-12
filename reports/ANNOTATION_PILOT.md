# Ví dụ áp dụng tiêu chí đề xuất — chưa phê duyệt

Đây là các ví dụ từng dùng để làm rõ tiêu chí. Tiêu chí đã được người dùng duyệt; CSV chính hiện có 752 nhãn sơ bộ và hướng dẫn duyệt hiện hành ở DATASET_REVIEW.md. Các ví dụ dưới đã cập nhật theo ngữ cảnh đầy đủ; chưa phải ground truth hoặc kết quả thực nghiệm.

| Điều khoản thật | Đề xuất sơ bộ | Căn cứ và ngữ cảnh |
|---|---|---|
| viettel_stracking_2026_0005, trang 2 | normal | Bên B phải cung cấp trong 02 ngày sau ký và thanh toán; nêu việc bàn giao, lắp đặt và tài khoản. Nội dung là nghĩa vụ cung cấp dịch vụ cụ thể, chưa có cơ chế thuộc sáu nhóm rủi ro đề xuất. Đây là nhận xét trong phạm vi tiêu chí, không bảo đảm toàn hợp đồng an toàn. |
| fpt_internet_0052, trang 6 | abnormal / deemed_consent | Sau thông báo, không phản hồi trong 05 ngày làm việc hoặc tiếp tục sử dụng được xem là đồng ý toàn bộ thay đổi, ảnh hưởng Bên A. Ngữ cảnh 0051 giới hạn một số căn cứ thay đổi; 0053 cho phép phản đối và chấm dứt; Điều 5.1.2–5.1.3 nêu nghĩa vụ khi chấm dứt. Có quyền phản đối nhưng cơ chế mặc nhiên chấp thuận vẫn là dấu hiệu cần cảnh báo theo tiêu chí đề xuất, không khẳng định trái luật. |
| fpt_internet_0002, trang 2 | abnormal / automatic_renewal, nhãn sơ bộ | Tái tục 02 năm không hạn chế số lần khi tiếp tục thực hiện; cảnh báo thời hạn ràng buộc lặp. Đã đọc Điều 5.1.2: khách vẫn có quyền chấm dứt. Không suy diễn mỗi kỳ tái lập phí/cam kết 24 tháng; cảnh báo dựa trên cơ chế tái tục dài không giới hạn, không chỉ từ chữ gia hạn. |

Các ví dụ không đại diện toàn bộ dataset. Agent đã sửa nguồn, gán nhãn và ghi lý do/ngữ cảnh trong CSV; người dùng chỉ xác nhận Đạt/Chưa đạt, không cần nhập nhãn thay agent.

Xem nội dung đầy đủ bằng `tools/inspect_annotation.py --document fpt_internet --start 0 --count 3 --context`, hoặc tra clause_id trong `data/clauses.csv`. Nguồn và vị trí trích đã có trong từng hàng.
