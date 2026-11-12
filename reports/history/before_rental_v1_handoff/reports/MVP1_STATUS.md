# Trạng thái MVP 1 — đã sửa lại mục tiêu ngày 08/11/2026

**Trạng thái mới nhất sau đối chiếu master prompt:** người dùng chọn **thuê nhà, bảo vệ người thuê** và duyệt tiêu chí thuê nhà mới; hồ sơ tại rental_criteria_approval.json. Bộ 752 dòng mô tả dưới đây được bảo toàn nhưng không có nguồn thuê nhà, chưa đáp ứng miền mục tiêu. Đang quay lại hoàn thiện dataset đúng miền trong MVP 1A. Staging mới có một nguồn, 12 ứng viên nguyên Điều và 10 normal sơ bộ, 0 abnormal. Chưa có dataset được duyệt, chưa train/MVP 1B. Xem [báo cáo mới](MVP1_PROGRESS_REVIEW.md) để biết thiếu sót, số liệu và thứ tự tiếp theo; các chỉ dẫn duyệt bản 752 dòng trước đây không phải yêu cầu duyệt dataset thuê nhà hiện hành.

**MVP 1 chưa hoàn thành. Dataset đã có nhãn sơ bộ, đang chờ người dùng duyệt; chưa có model hoặc metrics chính thức.** Xem [bản để duyệt](DATASET_REVIEW.md), [kiểm tra dataset](draft_dataset_audit.json) và [hướng dẫn chạy](../docs/RUN_MVP1.md). MVP1_AUDIT.md giữ kết quả khảo sát trước khi gán nhãn.

Người dùng đã xác nhận mục tiêu là dấu hiệu rủi ro/bất lợi trong nội dung điều khoản. Hướng phân loại 8 chủ đề trước đây không đáp ứng mục tiêu này. Không dùng xác nhận chủ đề cũ để cho phép train mô hình rủi ro.

## Dữ liệu hiện tại

- CSV chính: data/clauses.csv, nằm trong thư mục data.
- CSV chính có 752 điều khoản từ 11 nguồn, 9 họ mẫu và 8 nhóm độc lập: 722 normal, 30 abnormal. Mỗi dòng có lý do, nguồn và trạng thái draft/pending.
- 802 ứng viên ban đầu giữ nguyên trong snapshot. Sau sửa cấu trúc có 809 đơn vị theo dõi; 29 bản lặp liên kết, 10 bảng/metadata/bản lặp gộp giữ trong nguồn và 18 trường hợp chưa đủ dữ kiện tạm giữ nội bộ. Mọi ứng viên có nhật ký, không loại điều khoản hợp lệ do lỗi trích.
- Đã sửa 42 ranh giới/câu dẫn/đoạn ghép; 189 dòng giữ lại có sửa khoảng trắng/font với 6 ký tự font được kiểm tra trên ảnh PDF. Toàn bộ 752 dòng qua audit hash/spans và replay text repairs. Kiểm tra này không chứng minh nhãn chắc chắn đúng.
- Nhãn chủ đề cũ chuyển sang clause_type và clause_type_reason. Chúng không phải nhãn bất thường.
- Nhãn normal/abnormal được agent rà soát nội dung và ngữ cảnh theo sáu nhóm tiêu chí đã duyệt; không dùng quy tắc phân loại chủ đề cũ hoặc gán normal từ việc thiếu từ khóa.
- Người dùng đã xác nhận “Tiêu chí Đạt” ngày 08/11/2026. criteria_approved=true; hồ sơ và SHA256 của đúng bản tiêu chí ở criteria_approval.json. Giữ nguyên văn bản tiêu chí đã duyệt để bảo toàn hash, kể cả tiêu đề trạng thái trước duyệt của bản đó.
- review_status vẫn pending, dataset_approved=false. Quyết định này chưa duyệt dataset và chưa cho phép huấn luyện chính thức.

## Có thể tái sử dụng

Nguồn/hash, sửa đoạn, chuẩn hóa, kiểm tra nguyên văn, chống leakage, CLI và khung thực nghiệm cục bộ. Bộ khung được kiểm thử bằng fixture, chưa chứng minh được chất lượng phát hiện rủi ro.

Không tạo thêm Excel thay dataset CSV. Các Excel và tooling cũ đã chuyển vào archive/topic_workflow; CSV review cũ giữ để đối chiếu provenance. Không tiếp tục giới thiệu chúng như kết quả phát hiện bất thường. Xem docs/history/clause_type_task, reports/history/MVP1_STATUS_clause_type.md và cleanup_manifest.json.

## Còn phải làm để hoàn thành đúng MVP 1

1. Tiêu chí cụ thể trong docs/ANNOTATION_GUIDELINES.md đã được người dùng xác nhận; dùng đúng phiên bản có SHA256 trong criteria_approval.json.
2. Người dùng kiểm duyệt bản CSV có nhãn và lý do; xác nhận Đạt/Chưa đạt. Agent sửa những mục Chưa đạt, không yêu cầu người dùng gán nhãn mới.
3. Bản draft có normal ở 8 nhóm và abnormal ở 6 nhóm độc lập; preflight chia được ba tập có đủ hai nhãn nhưng validation chỉ có 3, test chỉ có 4 abnormal. Đây không phải thực nghiệm model. Cần ghi rõ độ bất định, lệch lớp và bổ sung nguồn thật khi kết quả/độ bao phủ chưa đạt yêu cầu.
4. Sau khi tiêu chí và dataset được duyệt mới train thật, kiểm tra save/load, dự đoán điều khoản mới, báo Accuracy/Precision/Recall/F1/confusion matrix thật và phân tích lỗi.
5. Hướng dẫn chạy lại rồi dừng ở MVP 1; không chuyển sang MVP 2.

Kiểm thử kỹ thuật và audit hiện tại được ghi tại reports/verification.json và test-results.xml. Điểm Accuracy/F1 của phát hiện bất thường hiện **chưa có**, không dùng các con số kiểm thử toy hoặc nhãn chủ đề làm kết quả thay thế.
