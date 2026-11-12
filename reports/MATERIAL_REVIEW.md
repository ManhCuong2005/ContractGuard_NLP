# Khảo sát tài liệu D:\NLP và quyết định cho MVP 1

## Phạm vi khảo sát

Danh mục máy đọc được tại `materials/inventory.json`, có đường dẫn gốc, SHA256, kích thước, tệp trích xuất, trạng thái và liên kết bản trùng. Đã xử lý 121 mục tài liệu/mã Lab: 116 bản riêng và 5 bản trùng byte, không lỗi trích xuất. Bao gồm Word, PDF, notebook (source và output văn bản đã lưu), README, HTML báo cáo/chụp cell và script hỗ trợ Lab; mở cả notebook trong ZIP.

Không chạy lại mã nguồn Lab, không sửa tệp gốc, không dùng model hoặc điểm số Lab làm kết quả ContractGuard. Bỏ qua môi trường ảo, mã thư viện bên thứ ba, cache và lockfile Word `~$`. Hình nhúng/screenshot không được OCR toàn bộ; bản trích là nội dung văn bản, không thay thế kiểm tra thị giác từng hình. Không tuyên bố đã xác minh thực nghiệm độc lập các kết quả trong báo cáo cũ.

## Đối chiếu nội dung và áp dụng

| Tài liệu/Lab | Nội dung được đối chiếu | Quyết định MVP 1 |
|---|---|---|
| Lab 01, báo cáo Word/PDF và notebook gốc/bài làm | Sentence/word segmentation, POS, NER, regex, lỗi do email/ngày/số thập phân | Đơn vị là điều khoản; không tách tùy tiện theo dấu chấm; giữ raw text và nguồn |
| Lab 02, bản mẫu và bài làm, báo cáo Word | Thu thập nguồn thật, selector đúng thân bài, URL trùng, validation và log lỗi | Allowlist nguồn, tải nguyên bản, hash, log lỗi tải; bộ tin tức của Lab không dùng train hợp đồng |
| Lab 03, bài làm và hai bản mẫu, báo cáo Word | NFC/NFD, whitespace, tách từ, tác động lowercase/stopwords/numbers/punctuation | Normalize NFC; giữ phủ định, số, dấu; không bỏ stopword mặc định |
| Lab 04, bản mẫu/bài làm và báo cáo Word; bài giảng Text Representation | BoW, TF-IDF, unigram/bigram, sparsity, cosine lexical khác semantic, save/load vectorizer | TF-IDF nằm trong Pipeline. Tìm điều khoản tương tự chỉ thiết kế cho MVP 3, không triển khai feature đó |
| Lab 05, Word2Vec và báo cáo/thư mục baocaolab05 | Window/min_count/vector_size, OOV, average document vector, coverage và lưu model | Chưa chọn embedding từ corpus nhỏ thiếu duyệt; ưu tiên baseline cục bộ tái lập, có kiểm tra input không có feature |
| Lab 06, bản trước/sau code, Ham/Spam demo, Word/PDF, bài giảng Text Classification I | Train/test, stratify, fit TF-IDF chỉ train, NB/LR/SVM, Dummy baseline, metrics/error analysis | So sánh đúng 3 họ classifier trên cùng split; thêm validation độc lập và group split theo nguồn hợp đồng |
| Lab 07, bản chính/bản copy/bản ZIP, báo cáo và short_report | Accuracy trap, macro/weighted, minority recall, controlled experiments, phân tích nhãn nhiễu | Macro F1 chọn trên validation. Báo cáo Lab có chọn cải tiến theo test; ContractGuard tách validation để tránh dùng test chọn cấu hình |
| Lab 08, notebook và 2 báo cáo Word | Tokenizer fit train, padding/truncation, Embedding, CNN/LSTM, EarlyStopping, learning curves | Không cắt ngắn điều khoản âm thầm. Deep learning chưa cần để chứng minh baseline; không mang mô hình tin tức sang bài toán normal/abnormal hợp đồng |
| Lab 09, notebook/HTML/Word, README và code RideBot | Intent char n-gram, confidence thấp, regex entity, slot/dialog, controlled CV | Bổ sung phương án word+char trong classifier. Không triển khai chatbot/slot/API; confidence để null khi chưa hiệu chỉnh |
| Check_MidTerm/A_23IT033.ipynb | Kiểm tra môi trường và regex bỏ số | Môi trường `.venv` riêng, dependency lock và pip check; không kế thừa bước bỏ số |
| NLP_7_LAB..., Test/Tong_hop..., Test/NLP_Giai_thich..., Test/Giải thích trên đầu, tonghop/test | Bản tổng hợp và diễn giải lại cùng các API; có ví dụ tự viết/offline | Dùng để đối chiếu cách gọi; phân biệt dữ liệu minh họa với dữ liệu thật. Không công bố điểm minh họa là thực nghiệm dự án |
| Script build report/execute/update/capture và HTML cell | Quy trình xuất báo cáo, dữ liệu/metric từng Lab đã lưu và các bản trình bày | Ghi bằng chứng máy đọc được cho ContractGuard; không chạy script cũ vì có thể ghi đè ngoài dự án |

## Những khác biệt có chủ đích

1. ContractGuard chưa dùng Underthesea: baseline âm tiết unigram/bigram + char n-gram chạy cục bộ, không tải model tách từ. Không gọi baseline này là tách từ tiếng Việt hoàn chỉnh. Có thể nghiên cứu ablation tách từ sau khi có dataset được duyệt.
2. Chia theo hợp đồng/họ mẫu và nhóm gần trùng, thay cho random split từng hàng thường dùng trong bài tập. Lọc gần trùng chỉ phục vụ chất lượng dataset MVP 1, không cung cấp tìm kiếm điều khoản cho người dùng.
3. Vectorizer chỉ học trên train trong so sánh; chọn model trên validation, sau đó refit train+validation và đánh giá test một lần mỗi run. Không diễn giải việc thử nhiều cấu hình trên cùng test là một đánh giá độc lập.
4. Ưu tiên xây dựng dữ liệu có provenance và gate người duyệt. Những corpus bài báo và intent có sẵn không giải quyết được nhãn hợp đồng dù giúp kiểm tra kỹ thuật.
5. Phần mở rộng MVP 2–4 chỉ có kiến trúc trong `docs/ARCHITECTURE.md`, không có mã chạy.
