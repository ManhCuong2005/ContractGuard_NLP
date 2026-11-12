# Cập nhật xử lý nguồn v2 — 08/11/2026

Đã chuẩn bị lại 802 điều khoản có nhãn sơ bộ và kiểm tra nguyên văn theo nguồn. Không còn yêu cầu người dùng duyệt danh sách đề xuất loại. Xem SOURCE_REPAIR_V2.md và Excel outputs/annotation_20261108_v2/ContractGuard_DuyetNhan.xlsx. Dataset chưa được phê duyệt, chưa huấn luyện chính thức. Thông tin v1 phía dưới giữ để đối chiếu lịch sử.

# Báo cáo tiến độ MVP 1 — cập nhật 08/11/2026

**Cập nhật gán nhãn:** agent đã chuẩn bị 673 điều khoản đề xuất giữ có nhãn/lý do và 294 hàng đề xuất loại. Người dùng chỉ chọn Đạt/Chưa đạt trong `outputs/annotation_20261108/ContractGuard_DuyetNhan.xlsx`, không tự gán nhãn. Xem `ANNOTATION_STATUS.md`. Mọi hàng vẫn pending; dataset chưa được phê duyệt.

**MVP 1 CHƯA HOÀN THÀNH. Người dùng đã xác nhận tiêu chí 8 nhãn ngày 05/11/2026. Đang chờ kiểm duyệt dataset và bổ sung dữ liệu độc lập. Chưa có model hay kết quả thực nghiệm chính thức.**

## Đã hoàn thành trong phạm vi được phép

- Khảo sát/trích xuất tài liệu và Lab trong D:\NLP: 121 mục, 116 bản riêng, 5 bản trùng; không lỗi trích xuất. Xem `materials/inventory.json` và `MATERIAL_REVIEW.md` về phạm vi, giới hạn đọc hình và đối chiếu Lab 01–09.
- Thiết kế kiến trúc mở rộng đến MVP 4; code chỉ cho MVP 1. Đã lưu quy định phạm vi vào AGENTS.md để các lượt sau không tự chuyển giai đoạn.
- Tạo `.venv`, package Python cục bộ, CLI, dependency lock và hướng dẫn chạy Windows.
- Tải 11 tài liệu mẫu/điều kiện hợp đồng công khai từ Viettel, FPT, Techcombank, Green Future và Bộ Tư pháp; bao phủ viễn thông, ngân hàng, thuê xe, vận chuyển và li-xăng nhãn hiệu. Giữ byte gốc, trang nguồn, URL, thời điểm, SHA256 và họ mẫu. Nguồn VNPT thử tải trả 503, không đưa vào corpus; lỗi nằm ở `collection_errors.json`.
- Chuẩn bị 967 hàng ứng viên; 967 pending, 0 accepted. Hiện đã điền nhãn sơ bộ vào label và lý do/đề xuất giữ hoặc loại ở cột riêng; annotation_status=draft. Không tự nhận là corpus đã kiểm duyệt.
- Soạn tiêu chí 8 lớp, đã được người dùng xác nhận “Đồng ý tiêu chí đề xuất”. Hiện có Excel duyệt nhãn với 673 điều khoản đã gán sơ bộ và 294 đề xuất loại; bản xem vấn đề chất lượng có 82 hàng ưu tiên. Người dùng chỉ xác nhận Đạt/Chưa đạt.
- Xây dựng normalization bảo toàn phủ định/số; pipeline TF-IDF + NB/LR/SVM; biến thể word+char; Dummy baseline; chống leakage theo họ mẫu/đoạn gần trùng; split train/validation/test; validation selection; refit train+validation; xuất metrics, confusion matrix, lỗi và báo cáo.
- Cổng huấn luyện chính thức kiểm tra xác nhận, các hash tiêu chí/nhãn/dataset/manifest, người duyệt từng hàng, nguồn và nguyên văn trích dẫn. Thay đổi dữ liệu sau duyệt làm hash không khớp.
- Lưu/nạp toàn pipeline có checksum, chặn model test ở inference thông thường, xử lý input rỗng/quá dài và nhãn null khi không có feature đã biết.

## Kiểm thử đã thực hiện

58 kiểm thử kỹ thuật đã qua, 0 lỗi, gồm kiểm tra nhãn sơ bộ không trở thành dữ liệu được duyệt. Chi tiết máy đọc được: `test-results.xml`, `verification.json`; log: `tests.log`. `pip check`, CLI, script dự đoán, audit dataset và compile mã đều được chạy bằng `tools/verify_mvp1.py`.

Đã thử fit/predict và save/reload cho cả 5 pipeline trên toy fixture; kiểm thử toàn bộ engine thử nghiệm (chia nhóm → train → chọn model → báo cáo → nạp lại) với artifact `technical_test`. Dự đoán trước/sau nạp được so sánh thực tế. Các câu đầu vào mới trong test cũng là fixture kiểm thử và **không chứng minh chất lượng trên hợp đồng**.

Có hai cảnh báo DeprecationWarning từ scikit-learn 1.6.1 với tùy chọn optimizer của SciPy 1.17.1; không làm kiểm thử thất bại. Phiên bản đang chạy được khóa trong requirements-lock.txt. Không sửa thư viện bên thứ ba để giấu cảnh báo.

## Chất lượng dữ liệu sơ bộ và hạn chế

| Mục | Số lượng/tình trạng |
|---|---|
| Nguồn tải thành công | 11 tài liệu, 9 họ mẫu khai báo ban đầu |
| Hàng ứng viên | 967, tất cả pending |
| Nhãn gợi ý chưa rõ/đa chủ đề | 580 |
| Hàng nằm trong nhóm trùng văn bản chuẩn hóa | 221 sau chuẩn bị văn bản; không có nghĩa phải loại cả 221 hàng, cần giữ một bản mỗi nhóm |
| Có dấu hiệu định danh/biểu mẫu | 20 sau chuẩn bị văn bản |
| Không khớp đoạn liên tục trong text từng trang | 25, đã đưa vào đề xuất loại; gate không cho accepted nếu không khớp |
| Đoạn ngắn dưới 100 ký tự | 175; chỉ là cờ xem lại, không tự coi là sai |
| Đoạn dài trên 2.000 ký tự | 3, đã đưa vào đề xuất loại |

Nguồn hiện vẫn thiên về viễn thông dù đã bổ sung bốn lĩnh vực khác, có phụ lục dữ liệu cá nhân, điều khoản mẫu lịch sử và nội dung gần trùng giữa nhà cung cấp. Đây không phải các hợp đồng đã ký, không đại diện hợp đồng mọi ngành và không có xác nhận hiệu lực pháp lý hiện hành. Chưa đủ căn cứ cho phép công bố/phân phối lại corpus; cần duyệt phạm vi sử dụng nguồn trước train.

9 họ mẫu ban đầu **không đồng nghĩa** đã có đủ 5 nhóm độc lập cho mỗi nhãn sau gộp gần trùng. Nhãn gợi ý payment/termination/dispute/force_majeure/confidentiality xuất hiện ở 9 họ, duration/liability ở 8 họ; các số này chưa chứng minh số nhóm nhãn chuẩn. Cần kiểm tra lại điều kiện split sau duyệt và bổ sung nguồn nếu thiếu; không chia ngẫu nhiên hàng để vượt kiểm tra. Gán nhãn sơ bộ là quy tắc từ khóa, có thể sai; chưa có đánh giá agreement hay độ chính xác nhãn gợi ý.

TF-IDF chủ yếu học tín hiệu từ vựng, chưa hiểu quan hệ pháp lý. Chưa có hiệu chỉnh confidence hoặc phát hiện ngoài miền đáng tin cậy. Không có model phát hiện rủi ro pháp lý. Checksum/hồ sơ approval là kiểm soát quy trình cục bộ, không phải chữ ký/xác thực chống người cố ý sửa mã hoặc hồ sơ.

## Chỉ số chính thức

| Accuracy | Precision | Recall | F1-score | Confusion Matrix |
|---|---|---|---|---|
| Chưa có | Chưa có | Chưa có | Chưa có | Chưa tạo |

Chưa train chính thức vì dataset chưa được kiểm duyệt/phê duyệt. Tiêu chí đã được người dùng xác nhận riêng; xác nhận đó không thay việc duyệt dataset. Không điền 0, không sao chép điểm từ Lab, không lấy điểm fixture làm kết quả dự án.

## Việc còn lại để hoàn thành MVP 1

1. Áp dụng tiêu chí đã được người dùng xác nhận trong `docs/ANNOTATION_GUIDELINES.md`; chỉ cần xin xác nhận lại nếu thay đổi tiêu chí.
2. Người dùng xác nhận nhãn/đề xuất loại Đạt hoặc Chưa đạt; agent sửa các mục Chưa đạt, giải quyết bản trùng/đa chủ đề/biểu mẫu/lỗi PDF và bổ sung nguồn độc lập nếu cần. Không yêu cầu người dùng tự gán nhãn.
3. Ghi xác nhận thật cùng hash vào configs/approval.json; chạy audit và kiểm tra đủ nhóm cho split.
4. Huấn luyện chính thức tại máy; so sánh validation, đánh giá test; kiểm tra save/load và thử điều khoản mới không dùng tính metric test.
5. Chạy toàn bộ kiểm thử lại, tổng hợp Accuracy/Precision/Recall/F1/confusion matrix thật và phân tích lỗi/hạn chế.
6. Hướng dẫn người dùng chạy lại theo README, sau đó dừng. Không chuyển sang MVP 2 khi chưa được phép.

## Chạy thử ngay phần đã sẵn sàng

```powershell
Set-Location D:\NLP\ContractGuard
$env:PYTHONIOENCODING = 'utf-8'
& .\.venv\Scripts\python.exe tools\verify_mvp1.py
& .\.venv\Scripts\python.exe -m contractguard audit --data data\review\clauses.csv
```

Lệnh train hiện dừng với thông báo `Human approval required` đúng chủ đích. Sau khi đủ duyệt/dữ liệu, xem README để chạy train và predict. Không bắt đầu một giai đoạn mới vì đã dựng xong scaffold.
