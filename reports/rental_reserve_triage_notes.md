# Rà tiếp phần dự trữ sau khi mở rộng nguồn công nhân

Agent đã đọc thân khoản của **82** ứng viên chưa có quyết định, được lọc để ưu tiên đọc bằng các dấu hiệu như mọi/toàn bộ/không hoàn/điều chỉnh/kiểm tra. Đây chỉ là hàng đợi đọc, không phải bộ gán nhãn; lượt rà này không tự tạo thêm label và không khẳng định đã rà toàn bộ 870 ứng viên dự trữ.

Các kết quả cần giữ cho lần mở rộng tiếp theo:

- CoChinh house 0006 và Homedy simple 0014 lặp cùng cơ chế mọi hư hỏng khi bỏ trống của Minh Khuê simple 0013 đang có trong chính; không cộng chúng thành họ abnormal độc lập. Có thể dùng làm lineage/biến thể cùng nhóm khi thật sự cần.
- Nhiều khoản bảo trì, tăng giá do cải tạo, vi phạm mục đích hoặc chậm trả trong các bản notary/Chính phủ tương tự nhau. Không gán bất lợi từ từ khóa; phải giữ cả quyền đồng ý, bồi thường và báo trước. Việc chưa chọn vào CSV không phải kết luận bỏ điều khoản hợp lệ.
- Sunshine 15.3 là quy tắc nhận thông báo; đã là context cho 15.3(a-d), không phải cơ chế mặc nhiên đồng ý nghĩa vụ mới. Phần 10.3 là chuyển sở hữu, không đổi thành ví dụ thuê nhà thông thường.
- Homedy room full 0024 có câu bồi thường rộng nhưng khoản 0015 giới hạn lỗi; giữ hold, không tăng abnormal bằng cách bỏ ngoại lệ. Tương tự SADECO 0004 phải đọc Điều 5 hai bên ký phụ lục; 0028 phải đối chiếu giới hạn lỗi khi sửa/hoàn trả.
- Bandon 0037 có ba lần nhắc nhở; Roomi 0026 gắn hành vi chất cấm; những khoản nghiêm khắc này không tự thành bất lợi theo tiêu chí. Phần chủ nhà niêm phong với bất kỳ vi phạm nào được giữ riêng theo bằng chứng rõ ở khoản khác.
- Danang 0052 về bên thua chịu án phí và chi phí khác cần làm rõ phạm vi chi phí, không chỉ lấy chữ toàn bộ để gán broad_liability. Khoản 0018 về hoàn cọc phụ thuộc nghĩa vụ khác trong hợp đồng, không tự normal từ riêng chữ hoàn lại.

Không dùng các ghi chú này như ground truth, không chốt nhãn test và không fit mô hình. Kết quả CSV hiện hành vẫn là 517 dòng/28 abnormal sơ bộ, cần kiểm duyệt thật. Công cụ đọc lại: `tools/read_rental_candidates.py --priority --unassigned --body-only`, đọc theo batch; muốn ra quyết định mới phải mở đầy đủ câu dẫn/ngoại lệ và nguồn.
