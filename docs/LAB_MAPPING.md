# Ánh xạ Lab vào ContractGuard MVP 1

Đối chiếu ngày 08/11/2026. Phạm vi hiện hành do người dùng xác nhận: **hợp đồng thuê nhà tiếng Việt, phát hiện dấu hiệu bất lợi cho người thuê**. Dữ liệu dịch vụ hiện có chưa chứng minh được khả năng trong phạm vi này.

Đã đọc lại source cell của chín notebook dưới đây, nội dung text trích tương ứng và kiểm tra SHA256 notebook gốc khớp inventory. Không chạy notebook, sửa Lab gốc hoặc sử dụng model/điểm Lab làm kết quả dự án. Danh mục khảo sát trước đó có 121 mục (116 bản trích, 5 bản trùng byte) tại [inventory](../reports/materials/inventory.json); không tuyên bố lần này đọc lại toàn bộ 121 mục hoặc OCR mọi hình.

| Notebook đã đọc trong D:\NLP | Kiến thức | Vị trí áp dụng và trạng thái |
|---|---|---|
| New folder/Lab01_Student_First_NLP_Pipeline.ipynb | Pipeline, tokenization, tách câu và xử lý cấu trúc | tools/collect_sources.py, công cụ sửa cấu trúc và src/contractguard/text.py. Đơn vị là điều khoản đủ nghĩa; chưa có dataset thuê nhà để kiểm tra chất lượng tách riêng miền này. |
| Lab02_Student_Data_Acquisition.ipynb | Thu thập, làm sạch nguồn, kiểm tra dữ liệu | tools/collect_sources.py, data/raw, source manifest và provenance. Giữ URL/hash/trang, staging riêng; chưa thu thập corpus thuê nhà chính thức. |
| Lab03_Student_Vietnamese_Preprocessing.ipynb | NFC, whitespace, underthesea, stopwords, số/phủ định | text.py giữ số và phủ định, dùng chung khi train/inference. Chưa có thí nghiệm tách từ tiếng Việt; không gọi tách âm tiết bằng khoảng trắng là word segmentation hoàn chỉnh. |
| Lab04_Student_Guided_Classical_Text_Representation.ipynb | BoW, TF-IDF, n-grams, sparse vectors, cosine | model.py dùng TF-IDF âm tiết (1,2), phương án thêm char n-grams. Chưa có BoW candidate/ablation; tìm kiếm điều khoản tương tự thuộc MVP 3, chưa triển khai. |
| Lab05_Student_Guided_Word_Embeddings.ipynb | Word2Vec, window, min_count, OOV, average vectors | Chưa dùng: corpus nhỏ, chưa được duyệt. Không lấy word2vec.model của corpus tin tức làm model hợp đồng; không dùng pretrained khi chưa được phép. |
| Lab06/Lab06_Student_Guided_Text_Classification.ipynb | MultinomialNB, LogisticRegression, LinearSVC, vectorizer, save/load | model.py và training.py có ba họ classifier và Dummy comparator. Chỉ kiểm thử bằng technical_test; chưa huấn luyện chính thức. |
| Lab07/Lab07_Student_Evaluation_Improvement.ipynb | Accuracy trap, macro F1, minority recall, class_weight, ablation | training.py chọn cấu hình bằng validation macro F1; LR/SVM có balanced weights; ghi support/confusion matrix/lỗi. Thí nghiệm dự án và learning curves còn chờ dữ liệu được duyệt. |
| Lab08_Student_Package/Lab08_Student_Deep_Learning_Text_Classification.ipynb | Embedding, CNN, LSTM, EarlyStopping | Chưa triển khai ContractGuard DL; xét sau baseline khi dữ liệu/tài nguyên cho phép. Ghi rõ lý do hoãn thay vì xem DL đã hoàn thành hoặc mặc định sẽ tốt hơn. |
| Lab09/Lab09_Student_Conversational_NLP_I.ipynb | char_wb, TF-IDF, confidence, intent | model.py tái sử dụng ý tưởng char_wb (3,5) để so sánh biểu diễn. Không dùng model intent/chatbot; confidence hiện null, chưa hiệu chỉnh xác suất. |

## Cải tiến so với bài tập

- Gom cùng hợp đồng/họ mẫu/đoạn gần trùng trước chia tập; không random từng điều khoản rồi để mẫu cùng hợp đồng xuất hiện cả train và test.
- Vectorizer nằm trong Pipeline, chỉ fit trên phần train khi so sánh; dùng validation chọn cấu hình rồi refit train+validation, test cuối được giữ riêng.
- Gate người dùng kiểm duyệt tiêu chí, dataset và nguồn theo đúng hashes; kiểm tra provenance cho cả draft. Gợi ý từ khóa và nhãn chủ đề không trở thành ground truth rủi ro.
- Kiểm tra artifact hash, save/load và dự đoán offline; artifact technical_test không được sử dụng như model chính thức.
- Không kế thừa bước bỏ số/phủ định hoặc chọn cấu hình theo test từ ví dụ Lab.

## Phần còn thiếu theo prompt

Dataset thuê nhà có nhãn được duyệt; biểu diễn BoW và so sánh preprocessing/tách từ khi sang MVP 1B; thí nghiệm NB/LR/SVM thực tế; phân tích lỗi và mẫu thuê nhà mới; quyết định DL có căn cứ. Các mục này chưa hoàn thành. Phân loại chủ đề chỉ là metadata phụ theo chỉ dẫn dự án hiện hành; chưa xây classifier chủ đề riêng.

Xem [báo cáo tiến độ](../reports/MVP1_PROGRESS_REVIEW.md) và [tiêu chí thuê nhà đang đề xuất](LABELING_GUIDELINES.md).
