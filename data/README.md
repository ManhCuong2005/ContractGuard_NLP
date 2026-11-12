# Dữ liệu ContractGuard

**Bản mở rộng mới, chưa duyệt:** [clauses_rental_v2.csv](clauses_rental_v2.csv), 820 dòng = 788 normal + 32 abnormal. Có 517 mẫu kế thừa v1, 303 mẫu mới giữ lại, trong đó chỉ 4 abnormal mới. Chưa đạt mục tiêu 1.000–2.000/500 abnormal; không huấn luyện bằng approval v1.

- `rental_expansion_v2/sources.json`, `raw`, `collection_runs`, `acquisition_inventory.json`: nguồn đóng góp, archive mới và kết quả từng URL; số file tải được không phải số hợp đồng hợp lệ.
- `rental_expansion_v2/candidates.json`, `candidates_extension_*.json`: ứng viên chưa có nhãn, tách khỏi CSV đã chọn; không tự gọi toàn bộ là điều khoản hợp lệ.
- `rental_expansion_v2/annotation_decisions.json`, `annotation_ledger.json`, `exact_duplicate_lineage.json`: quyết định từng ID, lý do, reserve và các bản lặp không tính lại.
- `rental_expansion_v2/approval.json`, `review_snapshot.json`: dataset_approved=false, reviewer trống và snapshot hash của phiên bản mới.
- [Hồ sơ review](../reports/RENTAL_EXPANSION_V2_REVIEW.md), [data card/schema bổ sung](../docs/RENTAL_V2_DATA_CARD.md), [kiểm chứng](../reports/rental_expansion_v2_verification.json). Agent xử lý reserve/ngữ cảnh; người dùng không phải nhập nhãn thay agent.

**Dataset thuê nhà v1 đã được người dùng duyệt:** [rental_approved_v1/clauses.csv](rental_approved_v1/clauses.csv), 517 dòng = 489 normal + 28 abnormal. [Hồ sơ duyệt](../reports/rental_dataset_approval.json) ghi đúng câu “Dataset thuê nhà Đạt”. Chỉ bản snapshot này được gate rental cho phép huấn luyện chính thức.

- `rental_approved_v1/clauses.csv`: text/label không đổi so với bản trình; annotation_status=reviewed, review_status=accepted, reviewer=user_in_chat theo quyết định thật. Không suy ra tên thật hoặc có chuyên gia độc lập đã rà từng nhãn.
- `rental_approved_v1/sources.json`, `approval.json`: manifest và phê duyệt đóng băng; giữ hash raw/pages và proof nguồn scan.
- `rental_approved_v1/reviewed_draft.csv`, `reviewed_draft_sources.json`, `review_snapshot.json`, `approval_before_acceptance.json`: bytes trước quyết định để truy vết.
- `clauses_rental_v1.csv`: bản draft 517 dòng đã trình, giữ nguyên draft/pending vì là hồ sơ lịch sử, không phải snapshot train hiện hành.
- `rental_mvp1a_v1/sources.json`, `raw`, `candidates.json`: 17 nguồn đóng góp, archive và 1.411 ứng viên kỹ thuật; phần dự trữ không tự có nhãn normal.
- `rental_mvp1a_v1/annotation_decisions.json`, `annotation_ledger.json`: quyết định sơ bộ của agent và phần dự trữ/hold, không phải công việc gán nhãn giao cho người dùng.
- `rental_mvp1a_v1/legacy_auxiliary.csv`: 7 câu tranh chấp chung từ bộ cũ, ngoài train/test chính.
- `clauses.csv`, `sources.json`, `raw`, `review`, `snapshots`: bộ legacy 752 dòng ngoài miền, bảo toàn; không dùng làm kết quả thuê nhà.

Tiêu chí đích `docs/LABELING_GUIDELINES.md` đã được duyệt và giữ nguyên hash. label/risk_label là normal/abnormal; clause_type/category chỉ là chủ đề phụ. annotation_reason/risk_category/ID/nguồn không đi vào features. label_confidence là nhận định gán nhãn, không phải xác suất model. normal không chứng nhận điều khoản hoặc toàn hợp đồng an toàn.

28 abnormal còn ít, thiếu ba nhóm dấu hiệu; thực nghiệm v1 bỏ sót toàn bộ 6 abnormal test. Xem [báo cáo thực nghiệm](../reports/MVP1B_EXPERIMENT_REPORT.md). Không thay nhãn hoặc nhân bản theo dự đoán; dữ liệu mới cần snapshot và quyết định duyệt riêng. Không chạy lại tool đóng gói/handoff lịch sử lên bản đã chốt.
