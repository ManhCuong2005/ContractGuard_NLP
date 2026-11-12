# Dữ liệu ContractGuard

**Bản thuê nhà hiện cần kiểm duyệt:** [clauses_rental_v1.csv](clauses_rental_v1.csv), 517 dòng, 489 normal/28 abnormal sơ bộ, UTF-8 BOM. Chưa được duyệt, chưa dùng làm ground truth hay train chính thức. Xem [báo cáo và giới hạn](../reports/MVP1A_REVIEW.md).

- `rental_mvp1a_v1/sources.json`: 17 nguồn đóng góp, URL/raw/pages/SHA256, họ mẫu và trạng thái nguồn.
- `rental_mvp1a_v1/raw`: archive tải được, gồm cả chỉ mục/tư vấn/bản sao; không phải mọi mục là hợp đồng hợp lệ.
- `rental_mvp1a_v1/candidates.json`: 1411 ứng viên kỹ thuật; phần chưa có quyết định vẫn trống nhãn, không mặc định normal.
- `rental_mvp1a_v1/annotation_decisions.json`: quyết định sơ bộ tường minh; `annotation_ledger.json` ghi chọn/dự trữ/hold, phục vụ agent, không phải danh sách người dùng phải sửa.
- `rental_mvp1a_v1/legacy_auxiliary.csv`: 7 câu giải quyết tranh chấp chung từ bộ cũ, ngoài train/test thuê nhà chính.
- `rental_mvp1a_v1/review_snapshot.json`: hashes của đúng bản để duyệt; `extraction_history` giữ các lần sửa trích.
- `clauses.csv`, `sources.json`, `raw`, `review`, `snapshots`: hồ sơ legacy 752 dòng không có provenance thuê nhà; giữ nguyên để truy vết. Không suy miền thuê nhà từ câu chữ chung.
- `rental_staging`: pilot Chính phủ từ lượt trước; không cộng lặp 10 mẫu pilot vào số hiện tại.

Tiêu chí đích ở `docs/LABELING_GUIDELINES.md` đã được duyệt. `label`/`risk_label` là normal/abnormal; `clause_type`/`category` chỉ là chủ đề phụ. `risk_category` là mã giải thích, không phải các lớp chủ đề thay mục tiêu. `label_confidence` là nhận định sơ bộ, không phải xác suất hay accuracy. Mọi reviewer/verified label hiện trống. Không sửa approval để thử train.
