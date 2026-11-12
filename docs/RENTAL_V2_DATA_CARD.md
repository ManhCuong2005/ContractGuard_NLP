# Data card — ContractGuard rental v2 draft

Ngày 09/11/2026. **820 mẫu, 788 normal / 32 abnormal; chưa đạt mục tiêu 1.000–2.000 và 500 abnormal.**

## Mục đích và phạm vi

Phát hiện dấu hiệu bất lợi cho người thuê nhà ở bằng tiếng Việt, offline; normal/abnormal là nhãn đích. Chủ đề phụ không quyết định nhãn rủi ro. Cảnh báo không kết luận vi phạm pháp luật. Không gọi API AI bên ngoài; không sinh câu giả cho tập chính. Tiêu chí cố định: `docs/LABELING_GUIDELINES.md`, SHA256 `68a1d9c068637c942e4c4c44648f299431960d64c01d1654652fc23f13c1a9fa`; ghi nhận duyệt tiêu chí tại `reports/rental_criteria_approval.json`.

## Đơn vị, nguồn và nhãn

Khoản/nhóm khoản đủ nghĩa, kèm câu dẫn và ngữ cảnh cùng hợp đồng. 517 mẫu v1 giữ nguyên text/label; 303 mẫu mới có quyết định ID/lý do. 40 tài liệu đóng góp, 27 nhóm nguồn/họ mẫu. Mẫu công khai không được gọi là giao dịch đã ký. Bản chép bị loại khỏi số đếm nhưng giữ lineage. Không tự normal hóa ứng viên chưa đọc/thiếu thông tin. `label_confidence` high/medium là nhận định gán nhãn, không là xác suất mô hình.

## Schema và cách dùng

CSV UTF-8 BOM, giữ 49 cột gốc và thêm metadata:

| Trường | Ý nghĩa |
|---|---|
| `contract_id`, `clause_id`, `document_id` | Hợp đồng, đơn vị và tài liệu nguồn |
| `text`, `clause_body`, `heading` | Đầu vào đủ ngữ cảnh, phần thân và cấu trúc nguồn |
| `label`, `risk_label` | Nhãn sơ bộ normal/abnormal, hai alias phải khớp |
| `clause_type`, `category` | Chủ đề phụ, hai alias phải khớp |
| `annotation_reason`, `label_reason`, `risk_evidence`, `risk_category` | Giải thích và bằng chứng; không đưa vào features |
| `source_url`, `source`, `source_sha256`, `source_spans`, `source_line_refs` | URL, hash và vị trí giúp đối chiếu nguồn |
| `context_clause_ids`, `body_line_refs`, `selection_repairs` | Ngữ cảnh cùng hợp đồng, dòng thân và log chọn lại dòng nguồn |
| `tenant_role`, `rental_subtype`, `protected_party` | Vai trò đã đọc từ nguồn và cohort thuê ở |
| `annotation_status`, `review_status`, `reviewer`, `verified_risk_label` | draft/pending, reviewer và verified để trống; không phải ground truth đã duyệt |
| `dataset_version`, `row_origin`, `inherited_approval_record` | rental_v2_draft, dòng kế thừa hay mới, hồ sơ v1 |
| `group_id`, `template_family`, `inherited_group_id` | Nhóm chống leakage, không là features |
| `prior_v1_split`, `shares_group_with_v1` | Tiếp xúc thí nghiệm v1; không là features |

Mô tả các cột nền: [RENTAL_DATASET_SCHEMA.md](RENTAL_DATASET_SCHEMA.md). Nếu huấn luyện sau duyệt, đầu vào chỉ là `text`; không đưa lý do, risk_category, nguồn, ID, metadata hoặc nhãn chủ đề chuẩn vào classifier rủi ro. Phải bảo đảm inference xây ngữ cảnh theo cấu trúc nguồn, không dựa vào nhãn đúng.

PDF dùng số trang gốc. Với HTML/DOCX, page là khối trích xuất logic (thường một khối toàn văn), không phải phân trang Word thực tế; đối chiếu bằng source_spans/source_line_refs trong pages.json.

## Chất lượng, rò rỉ và quyền dùng

Audit hash/spans không đánh giá độ đúng nhãn và không thay duyệt. Chưa đo agreement độc lập hay chất lượng model v2. Nguồn công khai thiên về mẫu chuẩn/sao chép; positive ít và chỉ 1 nhóm mới ngoài v1. Thiếu ba cơ chế deemed_consent, automatic_renewal, overbroad_data_use. Ký túc xá và thuê dài hạn là cohort riêng. Không kết luận lỗi mô hình chỉ do số lượng positive; ngữ cảnh, độ nhất quán nhãn và khác biệt nguồn cũng cần kiểm chứng.

Giữ nguyên test v1 như dữ liệu đã tiếp xúc, không gọi là test độc lập mới. Chỉ chia theo nhóm khi đã duyệt; chưa chốt split v2 hay fit mô hình. `approval.json` v2 giữ dataset_approved=false/source_use_confirmed=false. Công khai truy cập không tự đồng nghĩa có giấy phép tái phân phối; corpus đang lưu nội bộ phục vụ rà soát học thuật, không phát hành công khai thay tác giả nguồn. Nguồn từng file và trạng thái dùng được giữ tại `data/rental_expansion_v2/sources.json`.

## Tái lập và hồ sơ

`tools/package_rental_expansion_v2.py` chỉ đóng gói các quyết định ID đã ghi; không huấn luyện hay phê duyệt. `tools/report_rental_expansion_v2.py` tổng hợp số liệu, không gán nhãn. Đối chiếu đầy đủ tại [báo cáo review](../reports/RENTAL_EXPANSION_V2_REVIEW.md). Dataset SHA256 `adcecd1ceb5462a640b0f268ce3f93a292d36b1a3c096e4b5334365499c2452a`; manifest SHA256 `bc46e3f9719f0093c62c22233fb7e7665cf92e036883d8bd26d5ea0a6666ed10`. Các bước/tệp v1 và 752 mẫu legacy được giữ nguyên.
