# Yêu cầu ContractGuard được đối chiếu lại từ cuộc trò chuyện

## Phạm vi được xác nhận lại khi đối chiếu master prompt — 08/11/2026

Người dùng chọn **“Thuê nhà, bảo vệ người thuê theo prompt gốc”**, sau đó xác nhận **“Tiêu chí thuê nhà Đạt”** cho [LABELING_GUIDELINES.md](LABELING_GUIDELINES.md). Hồ sơ đúng phiên bản ở reports/rental_criteria_approval.json. Đây là phạm vi hiện hành: thuê nhà ở/phòng trọ/căn hộ tiếng Việt; người thuê là bên được bảo vệ. Không tự mở rộng sang viễn thông/ngân hàng/thuê xe hoặc coi phê duyệt tiêu chí là duyệt dữ liệu.

[Prompt nguyên bản](MASTER_PROMPT_ORIGINAL.md) được giữ nguyên. Tiếp tục dùng workspace D:\NLP\ContractGuard hiện tại, không tạo bản dự án khác ở D:\ContractGuard. Bộ 752 dòng cũ được bảo toàn để truy vết, chưa là dataset đúng miền thuê nhà; dữ liệu mới ở data/rental_staging. [Rà soát và thứ tự tiếp theo](../reports/MVP1_PROGRESS_REVIEW.md).

Tiêu chí tổng quát và hồ sơ duyệt lịch sử giữ nguyên hash; bản tiêu chí thuê nhà mới có hồ sơ riêng và chưa tích hợp vào core training CLI. Chưa dataset nào được duyệt, chưa cho phép MVP 1B/huấn luyện chính thức. Trước train phải chốt corpus thuê nhà và profile/hash tương ứng, không dùng gate lịch sử để train nhầm miền.

## Mục tiêu sản phẩm

Phát hiện **dấu hiệu rủi ro/bất lợi trong nội dung điều khoản hợp đồng tiếng Việt**. Người dùng đã xác nhận cách hiểu này ngày 08/11/2026. Không dùng phân loại chủ đề thanh toán/bảo mật/tranh chấp làm kết quả phát hiện bất thường.

Đơn vị NLP trước mắt là điều khoản, có ngữ cảnh từ hợp đồng nguồn khi cần. Việc kết luận/hiển thị hợp đồng có những điều khoản nào bị cảnh báo là bước sử dụng kết quả NLP; chưa xây giao diện/backend ở MVP 1.

## Phạm vi và trách nhiệm

1. Chỉ triển khai MVP 1: dataset, gán nhãn sơ bộ, preprocessing, training, evaluation, inference. Kiến trúc mở rộng đến MVP 4 chỉ viết trong tài liệu.
2. Agent đọc tài liệu/Lab, thu thập nguồn thật, sửa lỗi trích, ghép/tách, gán nhãn sơ bộ và giải thích. Người dùng chỉ xác nhận đạt/chưa đạt, không tự gán nhãn thay agent.
3. Tiêu chí gán nhãn rủi ro và phiên bản dữ liệu cuối phải được người dùng xác nhận trước khi huấn luyện chính thức. Xác nhận 8 nhãn chủ đề trước đây không phải xác nhận nhãn rủi ro.
4. Không gọi API AI ngoài. Mô hình phải tự huấn luyện tại máy. Không tạo số liệu thực nghiệm hoặc dùng dữ liệu giả làm kết quả chính thức.
5. CSV trong thư mục data là dữ liệu chính. File chính hiện tại: data/clauses.csv. Không tạo thêm Excel làm sản phẩm chính hoặc giao người dùng xử lý các lỗi kỹ thuật.
6. Giữ nguồn, SHA256 và bằng chứng từng đoạn. Không tự đổi một chủ đề thành rủi ro, không tự gán bình thường khi chưa đủ căn cứ.
7. Sau huấn luyện: chạy kiểm thử đầy đủ, kiểm tra save/load, dự đoán điều khoản mới, báo Accuracy/Precision/Recall/F1/confusion matrix thật, hạn chế và cách chạy máy.
8. Dừng sau MVP 1. Chỉ làm MVP 2 sau khi người dùng xác nhận MVP 1 đạt và cho phép bắt đầu.

## Sai lệch đã xác định

Bộ 8 nhãn cũ mô tả loại điều khoản, không có nhãn nào là bất thường. Việc trình bày 802 điều khoản được gán chủ đề như dataset hoàn chỉnh cho ContractGuard là sai hướng. Mã chuẩn hóa, lưu nguồn, chống leakage và bộ khung thực nghiệm có thể tái sử dụng, nhưng nhãn đích/dataset/báo cáo phải được chuẩn bị lại cho đúng bài toán. Chưa có mô hình hoặc kết quả phát hiện bất thường chính thức.
