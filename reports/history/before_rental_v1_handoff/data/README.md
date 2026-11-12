# Dữ liệu ContractGuard

**Cập nhật phạm vi:** người dùng đã chọn thuê nhà/bảo vệ người thuê. Bộ clauses.csv gồm 752 dòng bên dưới vẫn giữ nguyên để truy vết nhưng chưa có nguồn thuê nhà, không phải corpus đã đáp ứng phạm vi mới xác nhận. [rental_staging](rental_staging/README.md) có nguồn/pilot thuê nhà ban đầu; chưa thay CSV chính hoặc được phép train. Xem reports/MVP1_PROGRESS_REVIEW.md. Không dùng lời mời duyệt bản cũ để coi dữ liệu thuê nhà đã được kiểm duyệt.

**File CSV chính là clauses.csv trong thư mục này.** Không lấy Excel ở outputs làm dataset chính.

`label` dành cho normal/abnormal — nhãn phát hiện dấu hiệu rủi ro/bất lợi. `clause_type` chỉ là thông tin chủ đề cũ. Không có phép ánh xạ một chủ đề thành bình thường/bất thường.

CSV chính hiện có 752 điều khoản có nguồn: 722 normal và 30 abnormal, đều là nhãn sơ bộ có lý do. Mọi annotation_status=draft, review_status=pending và reviewer trống. Người dùng chưa phê duyệt dataset rủi ro; chỉ cần xác nhận Đạt/Chưa đạt, không phải gán nhãn thay agent. Xem reports/DATASET_REVIEW.md để duyệt đúng bản.

- raw/: PDF/HTML và text nguồn, giữ nguyên/hash.
- candidates.csv (khi thu thập thêm): staging ứng viên mới, chưa gán nhãn; không tự thay CSV chính.
- clauses.csv: bản dữ liệu chính cho bài toán đã làm rõ.
- sources.json: nguồn, họ hợp đồng và mã băm.
- review/: lịch sử các bản gán chủ đề và sửa bản trích, không phải dataset rủi ro hoàn chỉnh.
- snapshots/: giữ nguyên byte 802 ứng viên trước gán nhãn; SHA256 có trong reports/risk_annotation_manifest.json.
- inference_examples.json: ví dụ thử thao tác từ trước, không dùng huấn luyện/đánh giá chính thức.

Quy trình/tiêu chí mới ở docs/ANNOTATION_GUIDELINES.md. Sau khi người dùng chốt tiêu chí và dữ liệu, agent mới tiến hành huấn luyện chính thức. Không yêu cầu người dùng sửa nhãn, nguồn, hash hoặc cấu hình kỹ thuật bằng tay.

Tiêu chí đã được duyệt, dataset vẫn chưa. Sau sửa cấu trúc có 809 đơn vị được theo dõi: 752 dòng duyệt, 29 liên kết trùng, 10 bảng/metadata hoặc bản lặp gộp, 18 trường hợp thiếu dữ kiện nguồn tạm giữ. Nhật ký nội bộ ở reports/risk_annotation_ledger.json, không phải danh sách yêu cầu người dùng sửa lỗi. Không xóa dữ liệu nguồn hoặc loại điều khoản hợp lệ chỉ vì lỗi của bộ trích.

text là bản đã sửa và kiểm tra, source_text là bằng chứng trước sửa text; source_spans trỏ vào text nguồn đã trích. text_repairs chỉ cho phép sửa khoảng trắng và một ánh xạ font đã kiểm tra trên PDF FPT, không cho phép diễn đạt lại/đổi nghĩa. Những sửa ghép/tách có nhật ký và được kiểm tra lại từng đoạn nguồn.

Tooling và Excel chủ đề cũ đã chuyển vào archive/topic_workflow; data/review chỉ giữ để truy vết. Audit provenance khớp không thay thế việc agent kiểm tra lỗi tách chữ PDF, ranh giới nghĩa và ngữ cảnh trước khi gửi nhãn duyệt.
