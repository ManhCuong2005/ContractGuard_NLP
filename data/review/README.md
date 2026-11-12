# Lịch sử nhãn chủ đề — không phải dataset rủi ro

File chính hiện tại là data/clauses.csv ở gốc dự án. Các bản dưới đây thuộc hướng phân loại chủ đề trước khi sửa mục tiêu. Không dùng các nhãn này làm normal/abnormal; không tiếp tục duyệt Excel cũ như dataset phát hiện bất thường. Excel, các bản xuất labels_to_confirm/review_priority và tooling cũ đã chuyển vào archive/topic_workflow theo đường dẫn tương ứng. Toàn bộ hướng dẫn bên dưới là lịch sử, không còn là thao tác hiện hành.

## Thông tin lịch sử

Mở outputs/annotation_20261108_v2/ContractGuard_DuyetNhan.xlsx ở gốc dự án. Chỉ chọn Đạt/Chưa đạt cho các nhãn đã chuẩn bị. Xem v2/README.md. Bản v1 và danh sách đề xuất loại dưới đây chỉ giữ làm lịch sử đối chiếu.

# Bạn chỉ xác nhận nhãn, không phải tự gán nhãn

Agent đã điền label sơ bộ cho các điều khoản đề xuất giữ, kèm annotation_reason. Các đoạn thiếu nghĩa/lỗi trích/biểu mẫu/trùng có đề xuất loại và lý do. Mọi review_status vẫn pending, chưa được dùng làm nhãn chuẩn chính thức.

Mở `D:\NLP\ContractGuard\outputs\annotation_20261108\ContractGuard_DuyetNhan.xlsx`.

- Sheet **Duyet nhan**: đã có nội dung, nhãn và lý do. Chỉ chọn **Đạt** hoặc **Chưa đạt** ở cột A. Không cần tự nhập nhãn. Cột F ghi chú tùy chọn.
- Sheet **De xuat loai**: Đạt nghĩa là đồng ý loại đoạn. Chưa đạt nghĩa là agent cần xem lại quyết định loại hoặc trích/gán nhãn lại.
- Có bộ lọc theo nhãn/mã nguồn. Cột nguồn và trang dùng để đối chiếu khi cần.
- Lưu Excel rồi báo lại trong chat. Agent xử lý các mục Chưa đạt, không huấn luyện trước xác nhận dữ liệu cuối cùng.

`clauses.csv` chứa toàn bộ 967 hàng, nhãn sơ bộ và đề xuất giữ/loại, nguyên văn trước xử lý và nguồn. `labels_to_confirm.csv` là bản gọn những hàng đề xuất giữ đã có nhãn. `review_priority.csv` chỉ là bản xem vấn đề chất lượng, không phải chỗ yêu cầu bạn tự gán nhãn.

Nên dùng XLSX để duyệt. CSV là UTF-8 có BOM; không lưu đè bằng ANSI hoặc Text/Tab của Excel vì có thể mất dấu tiếng Việt. Bản mất dấu trước đó đã được sao lưu ở backups, nội dung hiện tại khôi phục từ nguồn gốc có SHA256 khớp.

Agent chịu trách nhiệm gán/giải thích/sửa nhãn. Người dùng xác nhận Đạt/Chưa đạt. Không ghi tên người dùng làm reviewer và không ghi accepted khi chưa có quyết định thật.

Tiêu chí 8 nhãn đã được người dùng chốt ngày 05/11/2026. Ngày 08/11/2026 người dùng làm rõ phân công. Chưa phê duyệt dataset, chưa huấn luyện chính thức.
