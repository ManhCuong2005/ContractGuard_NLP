# Tiêu chí gán nhãn ContractGuard — phiên bản 1, đã xác nhận

Người dùng đã xác nhận phạm vi và bộ 8 nhãn ngày 05/11/2026 qua câu trả lời “Đồng ý tiêu chí đề xuất”. Xác nhận này chỉ chốt tiêu chí; **dataset chưa được kiểm duyệt/phê duyệt**.

## Bài toán đã xác nhận

Phân loại **loại điều khoản tiếng Việt**, một nhãn cho một đơn vị ý nghĩa. MVP 1 chưa chấm điểm rủi ro pháp lý, chưa kết luận điều khoản có hợp pháp/có lợi hay không. Tên ContractGuard không đồng nghĩa đã có chức năng phát hiện điều khoản bất lợi. Nếu mục tiêu là phân loại rủi ro, phải thống nhất tiêu chí khác và thu thập nhãn chuyên môn trước khi train.

## Đơn vị gán nhãn và ngữ cảnh

- Một hàng là một khoản/tiểu khoản có ý nghĩa tương đối hoàn chỉnh, thường 1–5 câu; giữ phủ định, số tiền, tỷ lệ, ngày/thời hạn và ngoại lệ.
- Không đưa riêng tiêu đề Điều vào `text`; `heading` chỉ để người kiểm duyệt hiểu ngữ cảnh, không phải đặc trưng của classifier.
- Không chia máy móc theo dấu chấm: `1.2`, ngày tháng, số thập phân và viết tắt không phải ranh giới câu chắc chắn.
- PDF được trích tự động, có thể dính chân trang, biểu mẫu, phụ lục hoặc thiếu phần tiếp nối. Phải đối chiếu `data/raw/<document_id>/original.pdf` và `pages.json` theo `page_start/page_end`.
- Không sửa/paraphrase câu để làm đẹp dữ liệu. Được sửa ranh giới bằng cách lấy lại nguyên văn từ nguồn. Khi chia hàng: tạo `clause_id` mới, giữ `document_id`, `group_id`, URL, SHA256 và trang nguồn.
- Nếu OCR sai/ngữ cảnh không đủ/không tách được nội dung nhiều nhãn: `rejected` và ghi lý do. Không đoán nhãn để đủ số lượng.

## Bộ 8 nhãn đã xác nhận

| Nhãn | Phạm vi | Điểm phân biệt |
|---|---|---|
| `payment` | Giá, phí, hóa đơn, thời điểm và phương thức trả tiền | Khoản phạt/bồi thường vì vi phạm thuộc liability; khoản chỉ tất toán khi chấm dứt cần đọc ý chính |
| `termination` | Tạm dừng, hủy, đơn phương chấm dứt, thủ tục và hậu quả trực tiếp | Ngày bắt đầu/hết hạn thông thường thuộc duration |
| `liability` | Trách nhiệm bồi thường, phạt, giới hạn hoặc miễn trách nhiệm | Nghĩa vụ vận hành thông thường không mặc nhiên là liability |
| `confidentiality` | Bảo mật, sử dụng/chia sẻ thông tin, bảo vệ dữ liệu cá nhân | Thông báo thay đổi địa chỉ liên lạc thông thường không đủ điều kiện |
| `dispute` | Khiếu nại, thương lượng, cơ quan giải quyết tranh chấp, tòa án/trọng tài | Chỉ nêu luật áp dụng mà không giải quyết tranh chấp: other |
| `force_majeure` | Định nghĩa, thông báo, xử lý sự kiện bất khả kháng | Chỉ nhắc “trừ bất khả kháng” trong khoản thanh toán chưa đủ để đổi nhãn |
| `duration` | Bắt đầu hiệu lực, thời hạn, gia hạn, hết hạn tự nhiên | Thời hạn thanh toán, báo trước hay khắc phục vi phạm không tự động là duration |
| `other` | Nội dung hợp đồng rõ nghĩa ngoài 7 nhóm trên: đối tượng, giao nhận, nghĩa vụ vận hành... | Không dùng làm thùng chứa lỗi PDF, đoạn mơ hồ hoặc đoạn đa chủ đề |

## Xử lý nhiều chủ đề

1. Đọc toàn khoản và ngữ cảnh, xác định cơ chế chính mà khoản thiết lập.
2. Nếu có hai nghĩa vụ tách được: chia nguyên văn thành hai hàng đầy đủ ý nghĩa, giữ nhóm nguồn.
3. Nếu một ý chính và một dẫn chiếu/ngoại lệ phụ: chọn ý chính và ghi lý do trong `review_notes`.
4. Nếu hai chủ đề ngang nhau và không tách được: loại hàng (`rejected: ambiguous_multitopic`). Không có thứ tự ưu tiên từ khóa mặc định.

`suggested_label` là gợi ý từ khóa ban đầu, không phải nhãn chuẩn. Agent điền nhãn sơ bộ vào `label`, giải thích ở `annotation_reason`, đề xuất giữ/loại ở `proposed_action`. Khi `annotation_status=draft` và `review_status=pending`, `label` vẫn là nhãn sơ bộ, chưa được dùng làm ground truth chính thức. Không sao chép cả cột gợi ý ban đầu sang nhãn chuẩn hàng loạt.

Theo làm rõ của người dùng ngày 08/11/2026: **agent gán nhãn, người dùng chỉ xác nhận Đạt/Chưa đạt**, không tự nghĩ hay nhập nhãn. Nếu Chưa đạt, agent sửa nhãn/trích đoạn và gửi duyệt lại. Bộ 8 nhãn và định nghĩa giữ nguyên.

## Quy trình kiểm duyệt

1. Người dùng đã xác nhận bài toán và bộ tiêu chí này ngày 05/11/2026. Nếu thay đổi phạm vi/nhãn sau đây, cần xác nhận phiên bản mới trước khi áp dụng.
2. Kiểm tra phạm vi sử dụng từng nguồn; tài liệu công khai không mặc nhiên có giấy phép tái phân phối/huấn luyện. Chỉ dùng cục bộ sau khi người dùng xác nhận nguồn phù hợp; không phát hành corpus ra ngoài.
3. Agent chuẩn bị nhãn, lý do và Excel. Người dùng chỉ chọn Đạt/Chưa đạt ở cột A, ghi chú tùy chọn. Agent ghi quyết định thật vào review_status/reviewer/review_notes sau khi nhận xác nhận, không tự ghi accepted/rejected thay người dùng. Trước đó mọi hàng giữ pending.
4. Agent xử lý ranh giới và gán nhãn trước khi gửi duyệt. Bản trùng liên kết với bản chính; biểu mẫu/tiêu đề giữ trong hồ sơ nguồn, không giao người dùng duyệt một danh sách đề xuất loại. Đoạn bị cắt/đa chủ đề phải được agent khôi phục/ghép/tách từ nguồn. Đoạn gần trùng/họ mẫu vẫn phải cùng nhóm khi split.

Mỗi khoản ghép qua chân trang hoặc ghép câu dẫn với mục con có `source_spans` lưu trang và vị trí trong văn bản nguồn đã chuẩn hóa. Từng phần và toàn nội dung sau ghép phải kiểm tra khớp nguyên văn; không sửa lời điều khoản để làm dữ liệu đẹp hơn. Tệp nguồn gốc và SHA256 không đổi. Quy trình được cập nhật ngày 08/11/2026 theo phản hồi người dùng về trách nhiệm của agent đối với chất lượng dữ liệu.
5. Nên có hai người gán độc lập tối thiểu 10–20% (khuyến nghị, chưa thực hiện), đối chiếu bất đồng rồi chốt. Không báo agreement khi chưa đo.
6. Sau khi duyệt hết phiên bản CSV, người dùng xác nhận tập cuối. Ghi xác nhận, thời điểm có múi giờ và SHA256 vào `configs/approval.json`; agent không tự nhận mình là người duyệt.

## Điều kiện dữ liệu trước thực nghiệm chính thức

- Có đủ cả 8 lớp, không trùng văn bản chuẩn hóa, không hàng pending hoặc lỗi kiểm duyệt.
- Tối thiểu 5 nhóm nguồn độc lập **cho từng nhãn**, sau khi gom họ mẫu và đoạn gần trùng; nếu thiếu, phải bổ sung dữ liệu, không chia ngẫu nhiên từng hàng để lách điều kiện.
- Mục tiêu thu thập ban đầu: 400–800 điều khoản được duyệt, khoảng 40–100 mỗi lớp, từ ít nhất 15 họ hợp đồng ở nhiều lĩnh vực. Đây là mục tiêu, không phải số liệu đã đạt hay bảo đảm chất lượng.
- Không bổ sung câu do AI tự viết vào tập chính thức. Không lấy dataset tin tức/intent trong Lab làm dữ liệu hợp đồng.
- Test theo hợp đồng/họ mẫu; mỗi lớp xuất hiện ở train, validation và test. Tỷ lệ dự kiến 60/20/20, thực tế lệch theo kích thước nhóm và được ghi rõ.
- Dùng validation Macro F1 chọn model. Chỉ đánh giá test sau khi chọn; không sửa nhãn hoặc tune dựa vào lỗi test rồi dùng lại điểm đó làm kết quả độc lập.

## Ví dụ dùng để giải thích tiêu chí

Các ví dụ diễn giải này **không phải mẫu huấn luyện**: khoản quy định trả phí hàng tháng → payment; khoản ấn định cơ quan giải quyết tranh chấp → dispute; khoản yêu cầu giao thiết bị đúng quy cách → other. Cần đọc nguyên văn khi xử lý điều khoản thực.
