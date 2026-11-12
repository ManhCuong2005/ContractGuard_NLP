# Xử lý lỗi trích và chuẩn bị lại dữ liệu — 08/11/2026

Trách nhiệm xử lý dữ liệu do agent thu thập thuộc agent. Bản v1 đã đưa ứng viên còn lỗi ra duyệt quá sớm. Bản v2 thay danh sách đề xuất loại bằng một tập điều khoản đã chuẩn bị lại, có nhãn sơ bộ để người dùng xác nhận.

## Đã thực hiện

- Giữ nguyên byte gốc các PDF/HTML, pages.json và mã SHA256; giữ toàn bộ 967 ứng viên v1 và Excel cũ.
- Chuẩn bị 802 đơn vị điều khoản sau phân đoạn lại. Số đơn vị mới không so trực tiếp với số ứng viên cũ vì có ghép, tách và liên kết bản lặp.
- 45 đơn vị được ghép câu dẫn với mục con để khôi phục ngữ cảnh; 28 đơn vị được gỡ chân trang/vật liệu đọc dính; 13 hiệu chỉnh trực tiếp từ nguồn; 6 đơn vị được tách có chọn lọc từ các khối chứa bảng/phí trả xe; 25 đơn vị được tách theo câu/cơ chế. Các nhóm này là cách tạo đơn vị v2, không phải số lỗi chính tả hay độ chính xác nhãn.
- Đã sửa bộ trích không tự bỏ câu ngắn theo ngưỡng 45 ký tự/6 từ. Một câu dẫn về thời điểm chấm dứt từng bị mất vì ngưỡng này đã được khôi phục từ nguồn.
- Từng đơn vị được kiểm tra bằng source_spans có thứ tự; nội dung ghép phải khớp toàn bộ các phần nguồn, không chấp nhận diễn đạt lại. Cổng huấn luyện vẫn kiểm tra nguồn/hashes và yêu cầu xác nhận thật.
- Nhật ký có liên kết cho mọi ID ứng viên cũ, gồm bản chính, bản lặp, câu dẫn ngữ cảnh, tiêu đề/biểu mẫu. Không xóa điều khoản hợp lệ vì lỗi của bộ trích.
- Danh sách công việc sửa lỗi đã ghi nhận của agent hiện có 0 mục. Mọi nhãn vẫn là sơ bộ, chưa được người dùng xác nhận; không coi danh sách rỗng là bằng chứng độ chính xác của nhãn.

## Bản để người dùng duyệt

`outputs/annotation_20261108_v2/ContractGuard_DuyetNhan.xlsx`, chỉ một sheet Duyet nhan. Chọn Đạt/Chưa đạt ở cột A; agent xử lý các mục Chưa đạt. Không yêu cầu người dùng tự gán nhãn hoặc xác nhận loại các lỗi kỹ thuật.

CSV hiện tại: data/review/v2/clauses.csv. Mọi dòng pending, reviewer trống, dataset_approved=false. Không huấn luyện hoặc tạo điểm thực nghiệm chính thức.

Giới hạn còn lại: nhãn đề xuất vẫn có thể sai, độ đa dạng lĩnh vực và số lượng từng lớp còn lệch. Cần xác nhận dataset trước khi đánh giá khả năng split và huấn luyện chính thức. Chỉ triển khai MVP 1.
