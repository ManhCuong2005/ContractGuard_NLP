# Duyệt dataset rủi ro — bản gán nhãn sơ bộ 1

**Bản này được giữ để truy vết draft 752 dòng ngoài miền thuê nhà.** Sau đối chiếu master prompt, người dùng giữ phạm vi thuê nhà/bảo vệ người thuê; chưa dùng xác nhận bản cũ này làm kiểm duyệt dataset thuê nhà. Trạng thái và quy trình hiện hành ở [MVP1_PROGRESS_REVIEW.md](MVP1_PROGRESS_REVIEW.md). Tiêu chí thuê nhà đã được duyệt riêng, dataset thuê nhà còn ở staging, chưa sẵn sàng xin duyệt để train.

**File cần xem: [data/clauses.csv](../data/clauses.csv).** Đây là nhãn do agent chuẩn bị, chưa phải ground truth được duyệt.

Bản hiện tại có **752 điều khoản: 722 normal và 30 abnormal**. Tất cả review_status=pending, annotation_status=draft; reviewer để trống.

## Cách xác nhận

Đọc text, label và annotation_reason trong CSV chính. Với abnormal, xem thêm risk_category và risk_evidence; source_url, trang và source_spans dùng đối chiếu nguồn, context_clause_ids/context_source_pages chỉ rõ ngữ cảnh đã đọc.

- Nếu đồng ý bộ nhãn của bản này, trả lời trong chat: **Dataset Đạt**.
- Nếu còn mục chưa phù hợp, trả lời **Chưa đạt**, nêu clause_id và điểm chưa phù hợp; agent sửa và gửi lại. Bạn không cần tự nhập nhãn mới hoặc sửa cấu hình.
- Không dùng Excel nhãn chủ đề trong archive. Không cần duyệt hay sửa danh sách lỗi kỹ thuật/đề xuất loại.

Xác nhận áp dụng cho đúng bản CSV và các nguồn mẫu hợp đồng công khai được liệt kê tại data/sources.json. Chưa có quyền dùng nội dung này để khẳng định độ an toàn pháp lý của hợp đồng.

SHA256 CSV: `4a259465d17d3c4d9c4b5a836c9a5c05083b5a5c592014fb4fc11ca9e94fd3c6`. Tiêu chí bạn đã duyệt giữ nguyên SHA256 `ef0596c0ead897ff3a5d178b6b7801abd24a772e4b8270f8936ca3a64e7330f8`.

## Vì sao từ 802 ứng viên còn 752 điều khoản duyệt?

802 ứng viên ban đầu được giữ nguyên byte trong snapshot. Sửa cấu trúc tạo 809 đơn vị để theo dõi: giữ 752 đơn vị có nhãn, liên kết 29 bản trùng sau sửa Unicode/khoảng trắng, giữ riêng 10 bảng/metadata hoặc bản lặp gộp, và tạm giữ 18 trường hợp chưa đủ dữ kiện nguồn (ví dụ giá trị chưa điền hoặc điều khoản dẫn chiếu chưa có đúng phiên bản). Không dùng lỗi bộ trích làm lý do loại điều khoản hợp lệ.

Không xóa nguồn và không ép các trường hợp chưa đủ căn cứ thành normal. Tất cả 802 ứng viên và các đơn vị được tách thêm đều có nhật ký nội bộ; người dùng chỉ duyệt tập đã chuẩn bị xong trong CSV chính.

## Những điều khoản được cảnh báo

Bảng dưới hỗ trợ đọc nhanh; nội dung đầy đủ và các dòng normal nằm trong CSV chính. Một điều khoản có thể có nhiều nhóm dấu hiệu.

| clause_id | Nhóm dấu hiệu | Lý do sơ bộ |
|---|---|---|
| viettel_stracking_2026_0013 | broad_liability | Sau nghĩa vụ giữ tài khoản, câu Bên B không có trách nhiệm khi dữ liệu khách bị rò rỉ không chừa lỗi hệ thống/bảo mật của Bên B; có thể chuyển hậu quả rò rỉ rộng hơn lỗi khách. Nghĩa vụ bảo mật của Bên B vẫn được ghi ở khoản khác. |
| viettel_stracking_2026_0028 | broad_liability | Bên B miễn bồi thường và không hoàn bất kỳ khoản đã thu khi chấm dứt theo cả căn cứ cơ quan nhà nước, không chừa tiền dịch vụ chưa dùng hoặc trường hợp khách không có lỗi. |
| viettel_stracking_2026_0131 | overbroad_data_use | Thu thập tự động mô tả bất kỳ thông tin/công nghệ theo dõi nào, cả dữ liệu khác do thiết bị/phần mềm/hệ thống đọc, không định rõ loại cần cho dịch vụ. Có giới hạn mục đích và lựa chọn đồng ý trong phụ lục; cảnh báo phần phạm vi loại dữ liệu vẫn mở. |
| viettel_stracking_2026_0142 | overbroad_data_use | Sau yêu cầu xóa hợp lệ vẫn ngoại lệ toàn bộ dữ liệu từng dùng cho AI, không phân biệt dữ liệu gốc/đã khử nhận dạng hoặc nêu điểm kết thúc lưu; vượt cơ chế rút lại lựa chọn tham gia AI. |
| viettel_stracking_2026_0143 | overbroad_data_use | Ngoại lệ không xóa gồm dữ liệu dùng báo cáo theo quy định nội bộ Viettel mà không nêu hạn lưu/cơ sở hết nhu cầu; có thể tiếp tục giữ dữ liệu sau yêu cầu xóa vì mục đích quản trị riêng. |
| viettel_stracking_2026_0164 | broad_liability,termination_discretion | Viettel được hoãn/chấm dứt khi rút/xóa dữ liệu gây các hậu quả rất rộng ở khoản 6 (gồm mất thông báo/khuyến mại), đồng thời miễn mọi trách nhiệm pháp lý/bồi thường tổn thất; có căn cứ an toàn/pháp lý khác nhưng nhánh hậu quả và miễn trừ không phân biệt lỗi. |
| viettel_stracking_2026_0179 | broad_liability | Quyền xóa/hủy kèm điều kiện khách chấp nhận rủi ro/thiệt hại theo thông báo Viettel từng thời điểm; đọc cùng 141 có miễn mọi tổn thất, tạo phân bổ thiệt hại mở cho người thực hiện quyền. |
| viettel_stracking_2026_0201 | deemed_consent | Tiếp tục đăng ký/sử dụng được coi đồng ý bản sửa đổi xử lý dữ liệu; có thông báo trước và ngoại lệ trường hợp luật cần xin đồng ý, nhưng vẫn là mặc nhiên nhận thay đổi đối với phần còn lại. |
| viettel_tv_personal_0070 | termination_discretion | Điểm vi cho phép nhà cung cấp tự đổi chính sách rồi chấm dứt nếu khách không chuyển gói trong 7 ngày. Các điểm khác có căn cứ vi phạm/cơ quan và có báo trước; vẫn còn căn cứ chấm dứt do ý chí riêng bên cung cấp. |
| fpt_internet_0002 | automatic_renewal | Tự tái tục thêm 2 năm và không giới hạn số lần khi tiếp tục thực hiện, tạo ràng buộc thời hạn lặp cho Bên A. Điều 5.1.2 vẫn cho phép chấm dứt; không suy diễn mỗi kỳ tự tái lập cam kết/phí 24 tháng. |
| fpt_internet_0052 | deemed_consent | Bên A không phản hồi trong 5 ngày hoặc tiếp tục dùng bị coi là đồng ý toàn bộ thay đổi. Có thông báo, quyền phản đối/chấm dứt và căn cứ thay đổi giới hạn; các biện pháp đó không xóa cơ chế mặc nhiên chấp thuận. |
| fpt_internet_0065 | termination_discretion | Nhà cung cấp tự đổi chính sách rồi được chấm dứt khi khách không chuyển gói trong 7 ngày; căn cứ xuất phát từ ý chí bên cung cấp, không phải lỗi khách hoặc trở ngại khách quan. |
| fpt_internet_0078 | deemed_consent | Không gia hạn và không báo chấm dứt bị coi là đồng ý chuyển gói thanh toán tháng. Đã đọc mô tả gói tương đương; vẫn là thay đổi mặc nhiên khi khách im lặng. Đã tách chú thích chen giữa để giữ nguyên cơ chế. |
| fpt_domain_legacy_0027 | broad_liability | Nhà đăng ký tuyên bố không chịu bất kỳ trách nhiệm nào liên quan tranh chấp tên miền, không phân biệt lỗi xử lý đăng ký của mình; bên đăng ký có thể mất cơ chế bồi thường. |
| techcombank_direct_banking_0066 | broad_liability | Nghĩa vụ bảo đảm chứng từ kèm câu miễn Techcombank mọi trách nhiệm liên quan, không nêu ngoại lệ lỗi kiểm soát của ngân hàng. Điều 600 vẫn đặt trách nhiệm vi phạm trực tiếp chung; cảnh báo phạm vi miễn rộng riêng tại khoản chứng từ. |
| techcombank_direct_banking_0067 | broad_liability | Bên đăng ký chịu hoàn toàn rủi ro cả sửa chữa/giả mạo trước gửi và mọi giao dịch ngân hàng xử lý theo chứng từ; không phân biệt lỗi xác thực, tạo phân bổ rủi ro rộng cho bên đăng ký. |
| techcombank_direct_banking_0068 | broad_liability | Bên đăng ký phải nhận mọi giao dịch dùng chữ ký số và không phủ nhận vì bất cứ lý do nào; thiếu ngoại lệ giả mạo/lỗi ngoài kiểm soát, có thể mất cơ chế phản đối thiệt hại. |
| techcombank_direct_banking_0123 | termination_discretion | Khi tái tổ chức, bên còn lại được chấm dứt nếu tự xét thấy ảnh hưởng lợi ích mong muốn, không có chuẩn khách quan và không chịu trách nhiệm ngoài quyết toán. Có báo trước về tổ chức lại và giữ nghĩa vụ cũ; vẫn tồn tại căn cứ xét đoán mở. |
| greenfuture_vehicle_service_0056 | deemed_consent | Bảng phí do Green Future lập bị coi là khách đồng ý nếu không phản hồi trong 3 giờ, từ đó xuất hóa đơn/yêu cầu thanh toán; mặc nhiên chấp nhận số liệu nghĩa vụ tài chính thay vì xác nhận chủ động. |
| greenfuture_vehicle_service_0059 | deemed_consent | Không phản hồi bảng phí trong 2 ngày bị coi đồng ý/nghiệm thu; ngay cả có tranh luận khách phải trả toàn bộ số liệu bên cho thuê lập rồi điều chỉnh kỳ sau. Có cơ chế đối trừ nhưng vẫn mặc nhiên chấp nhận nghĩa vụ tài chính. |
| greenfuture_vehicle_service_0069 | broad_liability | Khoản này nói theo lỗi khách nhưng Điều 8.8.1 định nghĩa cả lỗi bên thứ ba cũng là lỗi khách trong ĐKC, nên phạm vi bồi thường toàn bộ có thể vượt lỗi thực của khách. Có bảo hiểm, không tự kết luận bị thu hai lần. |
| greenfuture_vehicle_service_0077 | broad_liability | Dù xe hỏng do lỗi Green Future/nhà sản xuất, ngoài đổi xe hoặc giảm phí lại miễn mọi trách nhiệm khác kể cả thiệt hại khách; miễn trừ có thể bao gồm thiệt hại trực tiếp do lỗi mình. |
| greenfuture_vehicle_service_0083 | unilateral_change | Quy trình và quy định sửa chữa/bồi thường khách phải theo có thể do Green Future bổ sung bằng thông báo riêng, không cần thỏa thuận lại; mở quyền thay nghĩa vụ xử lý thiệt hại. |
| greenfuture_vehicle_service_0085 | broad_liability | Tai nạn do lỗi bên thứ ba vẫn mặc nhiên bị coi lỗi khách và khách chịu toàn bộ hỏng hóc/thiệt hại; chuyển trách nhiệm không theo lỗi thực tế. |
| greenfuture_vehicle_service_0090 | broad_liability | Miễn trách nhiệm Green Future và tài xế đối với mất/tổn thất tài sản người dùng mà không chừa ngoại lệ do lỗi tài xế/nhà cung cấp. |
| greenfuture_vehicle_service_0099 | unilateral_change | Khách phải tuân thủ các điều kiện cho thuê lại khác do Green Future đặt tại từng thời điểm, không có cơ chế đồng ý/từ chối riêng; mở quyền bổ sung nghĩa vụ. |
| greenfuture_vehicle_service_0107 | unilateral_change | Green Future được tự sửa/bổ sung ĐKC và áp dụng sau thông báo qua email hoặc kênh do mình chọn; không nêu chấp thuận lại, thời hạn báo trước hoặc quyền từ chối trong cơ chế này. |
| moj_transport_template_0033 | broad_liability | Cùng khoản vừa buộc Bên B/tài xế tự chịu mọi vấn đề vừa tuyên bố Bên B không chịu bất cứ trách nhiệm và chuyển bồi thường cho Bên A; miễn trừ và phân bổ lỗi mâu thuẫn làm Bên A có thể gánh thiệt hại do bên vận chuyển. |
| moj_transport_template_0039 | termination_discretion | Nguy cơ ảnh hưởng danh tiếng/uy tín được coi là vi phạm nghiêm trọng nhưng không có chuẩn xác định, lại ghi bên gây và bên chịu ảnh hưởng đều là Bên B; kết hợp quyền chấm dứt tạo căn cứ rất mở cho Bên A. |
| moj_transport_template_0042 | broad_liability | Bên B phải bồi thường cả thiệt hại khách hàng/đối tác, lợi nhuận Bên A có thể hưởng và chi phí mở không giới hạn; vượt thiệt hại trực tiếp giữa hai bên. |

## Một số trường hợp có từ ngữ dễ nhầm nhưng vẫn normal

| clause_id | Căn cứ |
|---|---|
| viettel_stracking_2026_0003 | Đổi cước có thông báo trước một tháng và khách được không đồng ý rồi chấm dứt; có quyền từ chối, không đánh bất thường chỉ từ quyền chỉnh giá. Khoản thông báo website mâu thuẫn được tạm giữ riêng. |
| viettel_stracking_2026_0110 | Dùng dữ liệu huấn luyện AI phải thông báo, giải thích ảnh hưởng và cho lựa chọn không tham gia; nằm trong mục đích khách tích chọn, không tự cho phép mặc nhiên. |
| viettel_stracking_2026_0152 | Cảnh báo không có bảo mật tuyệt đối và mô tả nguy cơ; không phải câu miễn toàn bộ trách nhiệm, nghĩa vụ bảo vệ và báo sự cố vẫn có. |
| viettel_tv_personal_0020 | Bảo mật và tiếp thị theo nội dung khách đồng ý; có quyền từ chối miễn phí bất cứ lúc nào, không coi im lặng là quyền khai thác mở. |
| fpt_internet_0015 | Quyền nhận dịch vụ đúng giá/chất lượng, chấm dứt, khiếu nại và bồi thường thiệt hại trực tiếp do lỗi nhà cung cấp được ghi rõ. |
| fpt_server_legacy_0030 | Gia hạn cần Bên A ký xác nhận thông báo và nộp phí, không coi im lặng hay hết hạn là tự gia hạn. |
| fpt_phone_business_0031 | Chấm dứt sau 60 ngày vẫn chưa khắc phục nguyên nhân tạm ngừng đã liệt kê; có căn cứ vi phạm và thời gian khắc phục. |
| techcombank_direct_banking_0094 | Nghĩa vụ trước bất khả kháng vẫn phải thanh toán và nghĩa vụ tiếp tục khi hết sự kiện; giới hạn miễn trừ rõ. |
| techcombank_direct_banking_0125 | Bồi thường tài chính thực tế, trực tiếp do vi phạm và phải có chứng từ hợp lệ; không gồm lợi nhuận dự kiến/thiệt hại gián tiếp. |
| greenfuture_vehicle_service_0101 | Miễn do bất khả kháng phải ngoài kiểm soát/không do lỗi và đã đề phòng/giảm thiệt hại; không miễn mọi sự kiện tự gọi khách quan. |
| moj_business_template_0011 | Gia hạn cần thỏa thuận trước bằng văn bản của hai bên và đăng ký; không tự động tái ràng buộc. |

## Kết quả kiểm tra và giới hạn

- 752/752 điều khoản khớp nguồn và có thể replay mọi sửa Unicode/khoảng trắng. Có 42 sửa ranh giới/câu dẫn và 189 dòng giữ lại có sửa text, gồm 6 ký tự lỗi font đã đối chiếu ảnh PDF.
- Có 8 nhóm hợp đồng/họ mẫu/gần trùng; normal xuất hiện trong 8 nhóm và abnormal trong 6 nhóm.
- Tập dữ liệu lệch lớp rõ rệt và ít nguồn độc lập; normal chỉ có nghĩa chưa ghi nhận dấu hiệu theo sáu nhóm đã duyệt, không bảo đảm toàn hợp đồng an toàn.
- Nhãn do một agent rà soát, chưa được đo độ đúng nhãn hoặc mức đồng thuận giữa nhiều người gán. Kiểm tra provenance không chứng minh nhãn chắc chắn đúng.
- Classifier hiện nhận text điều khoản; một số nhãn cần ngữ cảnh được ghép lại hoặc ghi nguồn tham chiếu. Khả năng khái quát ngoài các mẫu này chưa được thực nghiệm.
- Preflight chia được ba tập đủ hai nhãn, nhưng trên bản draft hiện tại validation chỉ có 3 và test chỉ có 4 mẫu abnormal. Đây là kiểm tra khả năng chia, không phải kết quả thực nghiệm; metrics sau train sẽ có độ bất định lớn và cần ghi rõ support.
- Chưa huấn luyện chính thức; chưa có Accuracy/Precision/Recall/F1 hoặc Confusion Matrix chính thức. Khi dataset được duyệt mới tiến hành các bước đó.

Ngừng ở bước chờ duyệt dataset theo AGENTS.md. Chưa làm MVP 2–4.
