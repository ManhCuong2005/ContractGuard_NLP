# Tiêu chí phát hiện dấu hiệu rủi ro/bất lợi — bản đề xuất, chưa phê duyệt

Người dùng đã chốt hướng phát hiện rủi ro/bất lợi trong nội dung điều khoản. Các quy tắc gán nhãn cụ thể dưới đây vẫn cần xác nhận trước huấn luyện chính thức. Lịch sử tiêu chí chủ đề cũ được giữ tại docs/history/clause_type_task; không áp dụng làm nhãn đích.

## Nhãn đích

| label | Ý nghĩa trong phạm vi tiêu chí được duyệt |
|---|---|
| normal | Có đủ nội dung/ngữ cảnh để chưa ghi nhận dấu hiệu rủi ro thuộc tiêu chí. Không đồng nghĩa bảo đảm hợp pháp hoặc an toàn tuyệt đối. |
| abnormal | Có dấu hiệu rủi ro/bất lợi cụ thể, chỉ rõ bên có thể chịu ảnh hưởng và căn cứ trong điều khoản/ngữ cảnh nguồn. Không tự kết luận điều khoản vô hiệu hoặc vi phạm luật. |

Chưa đủ căn cứ: label để trống và annotation_status=needs_context hoặc awaiting_criteria. Đây là trạng thái công việc của agent, không phải lớp normal hay other. Agent chịu trách nhiệm đọc thêm nguồn/sửa nhãn, không yêu cầu người dùng tự gán.

## Nhóm dấu hiệu đề xuất cho lần gán sơ bộ

1. **unilateral_change:** cho một bên tự thay đổi nội dung/giá/nghĩa vụ mà không cần thông báo hoặc không cần sự đồng ý theo cơ chế đã nêu. Cần xem quyền từ chối/chấm dứt và điều khoản thông báo liên quan; có quyền thay đổi không tự động là rủi ro.
2. **broad_liability:** chuyển trách nhiệm/bồi thường quá rộng, gồm thiệt hại gián tiếp hoặc khoản lợi nhuận dự kiến, hoặc miễn trừ toàn bộ trách nhiệm không phân biệt lỗi. Phải phân biệt với bồi thường thiệt hại trực tiếp do lỗi đã xác định.
3. **deemed_consent:** coi im lặng/tiếp tục sử dụng là chấp thuận thay đổi hoặc quyền sử dụng dữ liệu theo phạm vi rộng. Ghi rõ cơ chế và quyền phản đối trong ngữ cảnh nếu có.
4. **automatic_renewal:** tự gia hạn thời gian ràng buộc dài/không giới hạn số lần, cần làm rõ quyền từ chối và thủ tục thông báo. Không đánh abnormal chỉ vì có chữ gia hạn.
5. **termination_discretion:** cho một bên chấm dứt/tạm khóa theo quyết định tùy ý, không nêu căn cứ khách quan hoặc cơ chế xử lý quyền lợi. Phân biệt với chấm dứt vì vi phạm rõ ràng/có thủ tục khắc phục.
6. **overbroad_data_use:** cho phép dùng/chia sẻ/lưu giữ dữ liệu vượt mục đích cung cấp dịch vụ với phạm vi mở hoặc không rõ giới hạn. Cần đọc đồng ý, ngoại lệ và quyền rút lại trong nguồn.

Không dùng các quy tắc này để khẳng định trái luật. Không tự đặt ngưỡng “phạt cao”, lãi suất hay tỷ lệ phần trăm bằng suy đoán. Các tình huống cần số tiền/giá trị thực tế, vai trò bảo vệ hoặc đánh giá chuyên môn mà nguồn chưa có phải giữ needs_context.

## Phân biệt nhãn chủ đề

payment, confidentiality, termination, liability, dispute, force_majeure, duration, other chỉ là clause_type. Một điều khoản thanh toán có thể normal hoặc abnormal. Không chuyển payment thành normal, liability thành abnormal, hay other thành normal. Các file Excel/CSV cũ chỉ có nhãn chủ đề không chứng minh được dataset rủi ro đã hoàn thành.

## Dữ liệu và bằng chứng

- File chính: data/clauses.csv, UTF-8 có BOM. label là nhãn rủi ro. clause_type là thông tin phụ. annotation_reason/risk_category ghi căn cứ; source_url, trang, source_spans giữ truy vết.
- Mọi nhãn agent chuẩn bị là sơ bộ, review_status=pending. Chỉ sau quyết định thật của người dùng mới cập nhật accepted/rejected và reviewer. Người dùng không cần nhập nhãn mới.
- Đọc điều khoản kèm hợp đồng nguồn khi có dẫn chiếu, ngoại lệ, phạm vi thông tin/tiền/ngày chưa đủ. Không gán normal chỉ vì không trúng từ khóa.
- Không tạo câu bất thường giả để cân bằng dữ liệu chính thức. Không lấy tin tức/intent từ Lab làm nhãn hợp đồng. Mẫu hợp đồng công khai khác hợp đồng đã ký; phạm vi kết luận phải ghi đúng loại nguồn.
- Giữ cùng hợp đồng/họ mẫu/đoạn gần trùng trong cùng nhóm train/validation/test. Chọn mô hình theo validation, không tune trên test. Đánh giá riêng precision/recall/F1 của abnormal và confusion matrix, bên cạnh Accuracy và macro metrics.

## Điều kiện trước huấn luyện

Người dùng xác nhận bản tiêu chí cụ thể và dataset cuối; đủ nhãn normal/abnormal có căn cứ, không còn hàng chưa gán trong tập chính thức, các nguồn đủ độc lập để split. Ghi mã băm đúng phiên bản vào approval. Hiện criteria_approved=false và dataset_approved=false; không huấn luyện chính thức.
