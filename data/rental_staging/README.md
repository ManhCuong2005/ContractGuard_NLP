# Staging thuê nhà — chưa phải dataset chính được duyệt

Người dùng đã xác nhận phạm vi thuê nhà/bảo vệ người thuê và **“Tiêu chí thuê nhà Đạt”** ngày 08/11/2026. Hồ sơ ở reports/rental_criteria_approval.json, tiêu chí đúng hash ở docs/LABELING_GUIDELINES.md. Không phải xác nhận dataset hay quyền dùng nguồn/train.

- raw/chinhphu_residential_2024/original.html: byte nguồn tải trực tiếp từ bài mẫu thuê nhà Cổng Chính phủ.
- raw/.../pages.json: text được trích từ các đoạn trong .detail-content, giữ nguyên từ ngữ/chỗ trống; một trang HTML được đánh số page=1, không giả làm số trang PDF.
- sources.json: URL, selector, ngày thu thập, hashes và họ mẫu. source_use_status=pending_human_review.
- candidates.csv: 12 nguyên Điều, chưa gán nhãn; giữ đầy đủ nội dung để tiếp tục sửa/tách theo nghĩa. Không tự loại Điều vì chưa đủ số liệu.
- pilot.csv: 10 khoản/câu dẫn đủ nghĩa, chọn làm ví dụ normal sơ bộ; có lý do, confidence định tính, nguồn và source_spans. Tất cả draft/pending, reviewer trống. Không dùng làm model training/evaluation.
- pilot_audit.json: kiểm tra spans/hash và giới hạn pilot; không đánh giá độ đúng nhãn hoặc chất lượng NLP.

Chưa có ví dụ abnormal thuê nhà được kiểm chứng trong pilot này; không gán nhãn bất lợi để cân bằng. Một nguồn/một họ mẫu không đủ split train/validation/test. Các khoản nguồn bỏ trống giá, phạt, hoàn cọc/thời hạn hoặc dẫn chiếu chưa giải quyết cần agent đọc thêm và xử lý tiếp. Không sửa nội dung nguồn, kể cả tên Bên mua/Bên bán xuất hiện trong mẫu thuê nhà tại Điều 12; không coi đó là lỗi bộ trích cần “sửa đúng hợp đồng”.

Toàn bộ text có thể kiểm tra bằng contractguard.provenance.verify_clause_spans. tools/collect_rental_seed.py và tools/prepare_rental_pilot.py từ chối ghi đè kết quả; quyết định pilot được ghi tường minh ở configs/rental_pilot_notes.json, không suy nhãn từ chủ đề/từ khóa.

CSV chính data/clauses.csv và approval tổng quát cũ được giữ nguyên, hiện là draft ngoài miền thuê nhà. Chỉ chuyển dataset thuê nhà thành CSV chính sau kiểm duyệt thực tế và snapshot đầy đủ. Core CLI hiện chưa tích hợp profile configs/rental_approval.json; đây là việc phải làm trước train, không phải một đường train thay thế.
