# Tiêu chí thuê nhà — bản đề xuất cần người dùng xác nhận

Ngày 08/11/2026, người dùng chọn: **“Thuê nhà, bảo vệ người thuê theo prompt gốc”**. Đây là xác nhận phạm vi, chưa phải duyệt bản tiêu chí này, dataset hay cho phép huấn luyện.

Bản tiêu chí tổng quát đã được duyệt trước đây vẫn được giữ nguyên tại [ANNOTATION_GUIDELINES.md](ANNOTATION_GUIDELINES.md), cùng SHA256/hồ sơ cũ. Không tự diễn giải quyết định cũ thành phê duyệt các tiêu chí thuê nhà bổ sung dưới đây. Trước huấn luyện phải tích hợp đúng phiên bản tiêu chí thuê nhà được duyệt vào gate và metadata; hiện CLI vẫn trỏ vào bản tổng quát cũ.

## 1. Bài toán, góc nhìn và đơn vị

- Đầu vào: điều khoản thuê nhà ở/phòng trọ/căn hộ để ở bằng tiếng Việt, kèm phần ngữ cảnh cần thiết từ cùng hợp đồng.
- Bên được bảo vệ: người thuê nhà. Không mặc định Bên A hay Bên B luôn là người thuê; agent xác định từ phần định nghĩa các bên và ghi lại vai trò.
- Không tự trộn hợp đồng thuê xe, văn phòng, mặt bằng kinh doanh, thuê mua nhà, ngân hàng hoặc viễn thông vào corpus chính.
- Đơn vị gán nhãn: khoản hoặc nhóm khoản đủ nghĩa, giữ câu dẫn, điều kiện, ngoại lệ, số tiền/thời hạn liên quan. Không tách mỗi câu thành mẫu độc lập để tăng số lượng.
- Mục tiêu nhị phân: dấu hiệu bất lợi theo tiêu chí này, không phải phát hiện một câu hiếm gặp về thống kê hoặc kết luận vi phạm pháp luật.

## 2. Nhãn và trạng thái thiếu thông tin

| Giá trị | Điều kiện |
|---|---|
| normal | Đủ nội dung/ngữ cảnh để chưa thấy dấu hiệu cụ thể thuộc các nhóm ở mục 3; có lý do, không chỉ do không trúng từ khóa. Không bảo đảm toàn hợp đồng an toàn. |
| abnormal | Chỉ ra được cơ chế làm người thuê có nguy cơ chịu bất lợi và bằng chứng trong nguồn; đọc cả ngoại lệ/quyền phản đối/bảo vệ người thuê trước khi quyết định. |
| label trống, annotation_status=needs_context | Chưa biết vai trò các bên, số liệu bị bỏ trống quyết định nhãn, hoặc cần dẫn chiếu chưa lấy được. Agent đọc nguồn/sửa đơn vị; không ép thành normal. Đây không phải lớp thứ ba. |

Không phân ba mức độ rủi ro ở bản đề xuất này: số mẫu và độ nhất quán nhãn chưa hỗ trợ việc đó. Nhãn normal/abnormal kế thừa hướng nhị phân đã dùng trong dự án; người dùng duyệt việc áp dụng cụ thể cho thuê nhà cùng bản này.

## 3. Nhóm dấu hiệu cần kiểm tra

| risk_category đề xuất | Cơ chế cảnh báo | Trường hợp dễ nhầm và ngữ cảnh phải đọc |
|---|---|---|
| deposit_forfeiture | Chủ nhà được giữ/khấu trừ toàn bộ cọc theo quyết định riêng, không gắn với nghĩa vụ/thiệt hại được xác định, hoặc người thuê mất cọc kể cả khi chấm dứt do lỗi chủ nhà. | Có đặt cọc, điều kiện bảo đảm, khấu trừ nợ thực tế/hỏng do lỗi người thuê không tự thành abnormal. Đọc điều kiện hoàn cọc, đối soát, lỗi, chấm dứt và chứng từ. Không tự đặt mốc số tháng cọc “quá cao”. |
| unilateral_change | Chủ nhà được tự tăng tiền thuê/phí hoặc bổ sung nghĩa vụ trong thời hạn thuê mà thiếu cơ chế giới hạn, thỏa thuận hoặc lựa chọn từ chối có ý nghĩa. | Điều chỉnh theo lịch/công thức đã thỏa thuận không tự là bất lợi. Đọc phụ lục giá, phí, kỳ áp dụng, báo trước và hậu quả nếu người thuê từ chối. |
| termination_discretion | Chủ nhà có thể thu hồi nhà/chấm dứt/tước quyền sử dụng theo ý riêng, trong khi người thuê đang thực hiện nghĩa vụ, thiếu căn cứ khách quan hoặc cơ chế giải quyết quyền lợi. | Chấm dứt vì vi phạm rõ ràng, có thủ tục khắc phục theo hợp đồng, không tự bị gán abnormal. Đọc tiền trả trước/cọc, báo trước, cơ hội khắc phục và nghĩa vụ bàn giao. |
| broad_liability | Người thuê phải chịu thiệt hại không theo lỗi/phạm vi sử dụng của mình, hao mòn tự nhiên hoặc lỗi chủ nhà; chủ nhà miễn cả trách nhiệm do lỗi mình; hoặc bồi thường mở không xác định được phạm vi. | Người thuê sửa hỏng do chính mình gây ra chưa phải dấu hiệu. Đọc biên bản bàn giao, hiện trạng, hao mòn, điều kiện lỗi, bảo hiểm và ngoại lệ. Không chỉ nhìn số tiền hay từ “bồi thường”. |
| repair_burden | Chuyển toàn bộ sửa kết cấu, hư hỏng có sẵn hoặc hỏng không do người thuê sang người thuê, thiếu phân định trách nhiệm; đồng thời có thể vẫn thu đủ tiền khi không sử dụng được nhà. | Phân chia sửa chữa có mô tả cụ thể chưa tự là bất lợi. Đọc nguyên nhân hỏng, nghĩa vụ báo hỏng, quyền sửa/khấu trừ, gián đoạn sử dụng và thỏa thuận tài sản. |
| access_interference | Chủ nhà tự vào/kiểm tra nhà hoặc hạn chế sử dụng thiết yếu để ép thực hiện nghĩa vụ, không giới hạn lý do/thông báo hay ngoại lệ khẩn cấp phù hợp với cơ chế đã thỏa thuận. | Kiểm tra có lịch, có thông báo và sự đồng ý hoặc xử lý khẩn cấp không tự thành abnormal. Đọc mục đích, thời gian, quyền sử dụng riêng và các ngoại lệ. |
| deemed_consent | Im lặng/tiếp tục ở bị coi là chấp nhận giá, phí, thiệt hại hoặc nghĩa vụ mới do chủ nhà xác định mà thiếu cơ chế phản đối khả thi. | Thông báo đã nhận hoặc xác nhận thủ tục không đồng nghĩa chấp nhận nghĩa vụ mới. Đọc kênh/thời hạn phản hồi, quyền phản đối và hậu quả. |
| automatic_renewal | Tự tái ràng buộc thời hạn/nghĩa vụ tài chính khi người thuê không chủ động đồng ý, cơ chế từ chối không rõ hoặc gắn mất cọc/phạt không được xác định rõ trước. | Gia hạn cần hai bên thỏa thuận, hoặc cơ chế gia hạn có điều kiện và quyền từ chối rõ ràng, không tự bị gán abnormal. Đọc thời hạn báo, quyền rời đi và quyết toán cọc. |
| overbroad_data_use | Cho chủ nhà dùng/chia sẻ thông tin hoặc hình ảnh của người thuê vượt mục đích thuê/quản lý đã xác định, theo phạm vi mở thiếu lựa chọn. | Cung cấp thông tin phục vụ cư trú/liên hệ đúng mục đích không tự thành abnormal. Phải có điều khoản nguồn; không đưa mẫu viễn thông vào thay cho dữ liệu thuê nhà. |

Đây là các mã giải thích, **không phải chín lớp cần huấn luyện riêng**. Một điều khoản có thể có nhiều dấu hiệu nhưng chỉ một label normal/abnormal. Không khẳng định cứ thiếu một mục trong hợp đồng là toàn bộ các khoản còn lại abnormal; đánh giá cơ chế cụ thể và phần ngữ cảnh có thể kiểm tra.

## 4. Ví dụ thật và giới hạn hiện tại

[Mẫu thuê nhà trên Cổng Chính phủ, đăng 27/08/2024](https://xaydungchinhsach.chinhphu.vn/mau-hop-dong-thue-nha-o-119240827172441217.htm) có các trường hợp để đối chiếu: sửa hỏng gắn với lỗi người thuê; nghĩa vụ chủ nhà bảo đảm sử dụng ổn định; sửa đổi hợp đồng cần văn bản hai bên ký. Theo bản tiêu chí đề xuất, các cơ chế có giới hạn này là ứng viên normal sau khi kiểm tra đủ nội dung. Không gán normal chỉ vì mẫu do cơ quan chính thức đăng.

Khoản sửa chữa cần đọc cùng hiện trạng nhà và phân định lỗi; khoản tăng giá cần phụ lục giá; khoản chấm dứt cần đọc hoàn cọc và tiền trả trước. Nếu chỉ lấy tiêu đề hoặc phần bỏ trống thì chưa đủ gán nhãn.

Hiện chưa có corpus thuê nhà đã thu thập, sửa trích và gán nhãn; chưa đưa ra ví dụ abnormal thuê nhà có nguồn được kiểm chứng đầy đủ. Agent phải bổ sung ví dụ nguồn thật và các cặp dễ nhầm trong vòng pilot sau khi tiêu chí được chấp thuận, trình lại nếu phát hiện điểm cần sửa. Không tự sáng tác điều khoản abnormal để minh họa như dữ liệu thật. Không coi các mô tả cơ chế ở mục 3 là mẫu dataset.

## 5. Hồ sơ gán nhãn và xử lý bất đồng

Mỗi mẫu cần có text, label sơ bộ, lý do, trích dẫn bằng chứng, vai trò bên thuê, chủ đề phụ, risk_category, ngữ cảnh thực sự cần, nguồn/trang/spans/hash và trạng thái draft/pending. Thêm label_confidence định tính high/medium/low do agent đánh giá; đó là độ chắc chắn gán nhãn sơ bộ, không phải xác suất model hay độ chính xác đã đo.

Nếu cần ngữ cảnh ngoài text, phải đưa phần cần thiết vào đầu vào được xây từ cấu trúc nguồn và dùng cùng cách ở inference, hoặc giữ mẫu ngoài tập chính đến khi giải quyết. Không đưa annotation_reason, risk_category hay nhãn đúng vào đầu vào model. Không tự chọn ngữ cảnh bằng nhãn test. Việc đã đọc ngữ cảnh khi gán nhãn không làm classifier nhận text đơn lẻ tự có ngữ cảnh đó.

Agent sửa lỗi trích/tách trước khi trình duyệt. Khi người dùng chọn Chưa đạt, agent đối chiếu nguồn, kiểm tra lại điều kiện/ngoại lệ, sửa hoặc giữ chờ ngữ cảnh và trình lại; người dùng không phải nhập nhãn thay agent. Không tự thay nhãn đã được duyệt. Khi sửa tiêu chí, đánh dấu phiên bản mới cần duyệt và rà lại các mẫu liên quan.

## 6. Kiểm duyệt và điều kiện trước MVP 1B

1. Người dùng xác nhận **Tiêu chí thuê nhà Đạt/Chưa đạt** cho đúng bản này. Phạm vi đã xác nhận không thay quyết định tiêu chí.
2. Agent thu thập nguồn thuê nhà thật, kiểm tra điều kiện sử dụng, gộp họ mẫu, sửa trích, tạo pilot có lý do và ví dụ đối chiếu; sau đó mở rộng nhãn khi tiêu chí ổn định. Chưa được tự phê duyệt nguồn có điều kiện chưa rõ.
3. Trình dataset thuê nhà cuối để người dùng chọn **Dataset thuê nhà Đạt/Chưa đạt**. Chỉ lúc đó mới chuyển bản đã duyệt thành CSV chính có snapshot/hash đầy đủ, cập nhật gate theo quyết định thật và phiên bản tiêu chí tương ứng.
4. Chốt chia theo hợp đồng/họ mẫu/gần trùng; kiểm tra số abnormal và độ bao phủ dấu hiệu ở từng tập, không chỉ đủ hai lớp. Mẫu test cần được kiểm tra nhãn độc lập với dự đoán, trước khi xem kết quả.
5. Chỉ sau duyệt tiêu chí và dataset, và được phép chuyển sang MVP 1B, mới làm thí nghiệm preprocessing/BoW/TF-IDF/NB/LR/SVM, save/load và inference. Không tự bắt đầu MVP 2.
