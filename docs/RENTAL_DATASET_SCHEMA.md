# Schema bản thuê nhà v1

**Cập nhật 09/11/2026:** Người dùng đã duyệt “Dataset thuê nhà Đạt”. Snapshot hiện hành `data/rental_approved_v1/clauses.csv` giữ nguyên text/label; annotation_status=reviewed, review_status=accepted, reviewer=user_in_chat theo quyết định thật. Mô tả draft/pending bên dưới ghi trạng thái của bản trình gốc được bảo toàn, không phải trạng thái snapshot train. Xem `reports/rental_dataset_approval.json`.

CSV để kiểm duyệt: `data/clauses_rental_v1.csv`. Đơn vị là khoản/nhóm khoản đủ nghĩa, giữ câu dẫn và phần ngữ cảnh thực sự dùng khi quyết định. Đây là một phiên bản gán nhãn sơ bộ; không tự thay thế bộ được người dùng duyệt trong tương lai.

## Nhãn, nội dung và trạng thái

| Trường | Ý nghĩa |
|---|---|
| contract_id, clause_id | Mã mẫu hợp đồng và đơn vị; không phải định danh hợp đồng đã ký thực tế |
| text | Đầu vào dự kiến: các đoạn thật của cùng hợp đồng, theo thứ tự nguồn, gồm ngữ cảnh cần thiết |
| clause_body | Khoản trung tâm; khác text khi cần thêm câu dẫn/ngoại lệ |
| label / risk_label | Alias cùng giá trị normal hoặc abnormal, theo tiêu chí thuê nhà đã duyệt |
| clause_type / category | Alias chủ đề phụ theo bảng dưới, không quyết định nhãn rủi ro |
| annotation_reason / label_reason | Alias lý do gán nhãn do agent viết, **không là feature đầu vào** |
| annotation_evidence | Nguyên văn khoản trung tâm làm bằng chứng, không phải diễn đạt lại |
| risk_evidence | Cụm nguyên văn chỉ dấu bất lợi; có trong text đối với mọi abnormal |
| risk_category | Một hoặc nhiều mã giải thích ngăn bằng dấu `\|`; không phải nhãn đích nhiều lớp |
| label_confidence | high/medium do agent nhận định; không phải xác suất model hoặc kết quả kiểm định |
| context_clause_ids | Danh sách JSON các khoản nguồn được đưa thêm vào text; không chỉ đọc ngầm khi gán nhãn |
| tenant_role, protected_party | Vai trò xác định từ nguồn; không mặc định bên A/B theo mọi hợp đồng |
| annotation_status, review_status | Hiện draft và pending; không coi là nhãn đã duyệt |
| reviewer, verified_risk_label, verified_category | Trống trước quyết định thật của người dùng |
| review_priority | 1: abnormal medium; 2: abnormal còn lại; 3: một số đối chứng dễ nhầm; 4: phần còn lại |
| dataset_role | primary_residential_rental; CSV legacy phụ trợ không vào corpus chính |

`normal` chỉ áp dụng cho đơn vị đã đọc và đủ căn cứ để chưa thấy cơ chế bất lợi theo tiêu chí. Nó không chứng nhận toàn hợp đồng an toàn. Những đơn vị chưa đủ dữ kiện hoặc chưa chọn trong pool không được mặc định normal và không có mặt trong CSV này. Người dùng chỉ xác nhận Đạt/Chưa đạt; agent chịu trách nhiệm nhãn và sửa/bổ sung.

## Chủ đề phụ

Mục đích là hỗ trợ lọc, kiểm tra và phân tích lỗi. Trường này được agent chọn cùng lúc đọc khoản; không dùng từ chủ đề suy thành bất thường. Mỗi đơn vị chọn một chủ đề chính dù có nhiều nội dung. Không huấn luyện một model phân loại các chủ đề dưới đây để thay bài toán phát hiện rủi ro.

| Mã | Định nghĩa và ranh giới chính |
|---|---|
| payment | Giá trị/kỳ hạn/cách trả tiền thuê và chi phí sử dụng, phân bổ thanh toán; cơ chế thay giá dùng price_change |
| deposit | Mục đích đặt cọc, hoàn/khấu trừ/đối soát cọc; chế tài mất chỗ ở kèm cọc có thể đặt termination |
| price_change | Ổn định/điều chỉnh giá hoặc phí theo thời gian/căn cứ/thông báo |
| renewal | Tiếp tục thuê, ưu tiên thuê, thủ tục gia hạn; hiệu lực bản ký lần đầu dùng general |
| termination | Căn cứ và hậu quả chấm dứt, thu hồi, trả trước; thời gian thủ tục thông báo nằm cùng nếu cần |
| tenant_rights | Quyền sử dụng ổn định, riêng rẽ, tiếp tục sử dụng khi thay đổi chủ |
| handover | Giao/nhận/trả nhà, biên bản và hiện trạng; gồm quyền yêu cầu giao đúng chất lượng |
| repair | Bảo hành, bảo dưỡng, sửa chữa và phân chia chi phí sửa |
| liability | Lỗi, thiệt hại, bồi thường, bảo hiểm hoặc miễn trách nhiệm; khoản sửa chữa có cơ chế bảo trì chính dùng repair |
| modification | Sửa đổi hợp đồng, chấp thuận cải tạo, chuyển giao hoặc bổ sung nghĩa vụ |
| access | Quyền vào/kiểm tra nhà và hạn chế tiếp cận; chế tài niêm phong kèm chấm dứt có thể đặt termination |
| personal_data | Thông tin cư trú, giấy tờ, liên hệ, bảo mật, sử dụng/chia sẻ thông tin |
| notice | Kênh gửi/nhận, địa chỉ và thời điểm được coi nhận thông báo; không đồng nghĩa chấp thuận nội dung |
| force_majeure | Định nghĩa, thông báo và xử lý sự kiện khách quan ngoài kiểm soát |
| dispute_resolution | Thương lượng, hòa giải, Tòa án/cơ quan có thẩm quyền |
| use_rules | Mục đích ở, bảo quản, nội quy sinh hoạt/PCCC/an ninh, hạn chế cho thuê lại |
| general | Cam kết tự nguyện, hiệu lực, văn bản/phụ lục, thay đổi tổ chức, điều khoản chung còn lại |

## Nguồn và chống lẫn nhóm

| Trường | Ý nghĩa |
|---|---|
| source / source_url | Alias URL nguồn tải trực tiếp hoặc trang công khai chứa mẫu |
| source_sha256 | Hash bytes raw bất biến, không phải hash text đã sửa |
| document_id | Tài liệu vật lý; tuyển tập có thể chứa nhiều contract_id |
| template_family | Họ mẫu đã xác định khi so sánh cấu trúc/cách viết; bản sao không trở thành mẫu độc lập |
| group_id | Nhóm chống leakage: cùng tài liệu, họ mẫu hoặc gần trùng thì nối chung; chỉ preflight ở MVP 1A |
| rental_subtype | Nhà/phòng/căn hộ/lưu xá/thuê căn hộ dài hạn; không gộp kinh tế dài hạn thành phòng trọ phổ thông |
| source_text, source_spans | Nguyên văn và các đoạn có thứ tự trong `normalize(page)` của đúng pages_path trong manifest |
| text_repairs | Nhật ký sửa text được phép replay; không cho phép sửa ý/diễn đạt lại |
| page_start, page_end | Trang PDF; HTML/DOCX được trích thành một đơn vị text “page 1”, không phải số trang in Word |
| source_line_refs, body_line_refs | Tọa độ dòng đọc tại bản trích đã ghi hash; không phải số dòng CSV |
| annotation_criteria_sha256 | Hash đúng bản tiêu chí được người dùng duyệt |

Các khóa raw_path/pages_path/pages_sha256 nằm trong `data/rental_mvp1a_v1/sources.json`. Với PDF, `pages_geometry.json` theo bố cục được dùng thay việc lấy từng dòng wrap làm một khoản. Với HTML, `pages_semantic_v2.json` khôi phục ranh giới block và nối nguyên inline text; OOXML DOCX giữ thứ tự paragraph. `source_spans` xác minh chính xác phần trích được ghép, không phải phép kiểm chứng đúng/sai pháp lý của nhãn.

Ngoại lệ PDF scan SADECO: `pages_visual_selected_v1.json` là phần văn bản nguồn do agent chép từ ảnh và đối chiếu lại, giữ alignment sáu trang; không phải toàn bộ trang hay lớp text PDF tự trích. `visual_transcription_v1.json` và `transcription_proof_sha256` ghi nguyên bản, hash trang chép, ảnh render, phần không chép và phương pháp. Không có OCR/API AI bên ngoài. Spans ở nguồn này chỉ kiểm tra lại sự nhất quán với bản chép đã đối chiếu ảnh; không tự biến bản chép thành xác minh độc lập từ raw PDF. Trước công bố hoặc huấn luyện chính thức cần giữ phần phương pháp này trong hồ sơ dữ liệu.

Không đưa clause_id, nguồn, label, risk_category, annotation_reason, confidence, verified labels hoặc reviewer vào ma trận đặc trưng phân loại. Chỉ `text` sau preprocessing phù hợp và cùng quy tắc ghép ngữ cảnh tại inference. Không dùng oracle label để chọn context cho test.

## Kiểm duyệt và phiên bản

Manifest nguồn hiện chưa có xác nhận giấy phép tái phân phối mở; việc tải công khai và dùng kiểm tra cục bộ không tự cấp quyền công bố lại toàn bộ corpus. Bộ source_use/dataset approval vẫn pending/false. Không đánh dấu reviewer hay accepted khi chưa có quyết định thật.

Snapshot candidate được đóng hash trước áp quyết định ID; thay bản trích phải rà lại quyết định, không tái sử dụng ID mù. Nếu sửa sau khi người dùng duyệt, tạo phiên bản/snapshot và kiểm duyệt phần thay đổi theo quy định, không âm thầm sửa ground truth.
