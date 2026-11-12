# Rà soát tiến độ theo master prompt — 08/11/2026

**MVP 1 chưa hoàn thành. Đang ở MVP 1A; cần xây dataset đúng miền thuê nhà trước khi duyệt dữ liệu và sang MVP 1B.**

Người dùng đã xác nhận trong lần rà soát này:

- Phạm vi: “Thuê nhà, bảo vệ người thuê theo prompt gốc”.
- Tiêu chí mới: “Tiêu chí thuê nhà Đạt”. Hồ sơ và SHA256 ở [rental_criteria_approval.json](rental_criteria_approval.json).

Xác nhận trên chưa duyệt dataset, chưa xác nhận điều kiện sử dụng nguồn và chưa cho phép train/MVP 1B. Không yêu cầu duyệt lại tiêu chí vừa được chấp thuận. Văn bản [tiêu chí thuê nhà](../docs/LABELING_GUIDELINES.md) được giữ nguyên như lúc duyệt, kể cả tiêu đề trạng thái trước duyệt, để bảo toàn hash.

## 1. Đã kiểm tra những gì

Đã đọc toàn bộ [prompt gốc](../docs/MASTER_PROMPT_ORIGINAL.md), AGENTS.md, hồ sơ duyệt, dataset/schema, code core, công cụ chuẩn bị nhãn, báo cáo hiện có; kiểm tra các notebook liên quan và đọc lại source cell của chín Lab. Workspace tiếp tục là D:\NLP\ContractGuard theo vị trí người dùng đang làm; đường dẫn D:\ContractGuard trong prompt gốc không tạo thêm bản dự án khác.

Đã chạy tools/verify_mvp1.py: **86/86 tests qua**, pip check, CLI, audit, readiness, annotation inspector và compile qua. Đây là kiểm tra phần mềm; các test model dùng fixture technical_test, không chứng minh chất lượng nhận diện điều khoản bất lợi. Chi tiết ở [verification.json](verification.json).

Đã chạy [audit_progress.py](../tools/audit_progress.py) để tính lại số liệu từ CSV; kết quả [progress_audit.json](progress_audit.json). Không fit model. SHA256 CSV chính, approval cũ, nguồn, nhãn và tiêu chí tổng quát được giữ nguyên.

## 2. Hiện trạng bộ 752 dòng

| Hạng mục | Kết quả thực đo |
|---|---:|
| Điều khoản | 752 |
| normal sơ bộ | 722 (96,01%) |
| abnormal sơ bộ | 30 (3,99%) |
| Tỷ lệ normal : abnormal | khoảng 24,1 : 1 |
| Hàng người dùng đã duyệt | 0 |
| Tài liệu nguồn / họ mẫu / nhóm chống leakage | 11 / 9 / 8 |
| Nhóm có abnormal | 6 |
| Điều khoản có tham chiếu ngữ cảnh khi gán nhãn | 180, trong đó 22 abnormal |
| Nguồn thuê nhà trong bộ này | 0, theo rà soát nội dung và loại 11 nguồn |

Toàn bộ 752 hàng vẫn draft/pending; đây không phải ground truth chính thức. 11 nguồn là viễn thông/dịch vụ, ngân hàng, thuê xe, vận chuyển, li-xăng; thuê xe không phải thuê nhà. Vì người dùng giữ phạm vi thuê nhà, **không chỉ bổ sung một ít abnormal vào corpus này rồi coi là đã đúng phạm vi**. Giữ corpus cũ để truy vết/tham khảo, không báo kết quả trên nó như kết quả cho người thuê nhà.

### Độ bao phủ dấu hiệu của bản cũ

| Dấu hiệu | Số khoản abnormal | Số nhóm chống leakage |
|---|---:|---:|
| broad_liability | 14 | 5 |
| deemed_consent | 5 | 3 |
| termination_discretion | 5 | 4 |
| overbroad_data_use | 3 | 1 |
| unilateral_change | 3 | 1 |
| automatic_renewal | 1 | 1 |

Có một khoản thuộc hai nhóm dấu hiệu nên tổng cột số khoản là 31, trong khi số abnormal duy nhất là 30. Các mã dấu hiệu là metadata giải thích, không phải sáu lớp classifier.

### Chia draft hiện tại có vấn đề gì?

Đây là kiểm tra khả năng chia, **không phải huấn luyện hoặc đánh giá model**. Seed yêu cầu 42; thuật toán tìm được split đủ hai nhãn ở seed hiệu lực 45:

| Tập | normal | abnormal | Nguồn |
|---|---:|---:|---|
| train | 564 | 23 | 9 tài liệu, 6 nhóm |
| validation | 56 | 3 | chỉ mẫu vận chuyển Bộ Tư pháp |
| test | 102 | 4 | chỉ mẫu ngân hàng Techcombank |

Validation và test chỉ có broad_liability và termination_discretion; bốn nhóm còn lại không được đánh giá bằng mẫu dương ở hai tập đó. Một lỗi thêm ở 4 abnormal làm recall thay đổi **25 điểm phần trăm**; với 3 mẫu validation là 33,33 điểm. Tập test chỉ một nguồn cũng không đo được tính ổn định giữa nhiều hợp đồng/miền. Không bỏ group split hoặc tìm seed theo điểm model để làm đẹp số liệu.

## 3. NLP có làm được tốt không?

**Có thể xây mô hình cảnh báo phạm vi hẹp và kiểm chứng bằng thực nghiệm; hiện chưa có căn cứ nói mô hình sẽ tốt.** Đây là supervised classification theo tiêu chí nhãn, không tự động hiểu đúng mọi rủi ro hợp đồng.

Bài toán khó hơn phân loại chủ đề vì nghĩa thay đổi theo bên có nghĩa vụ, lỗi của ai, ngoại lệ, quyền từ chối, tiền cọc, phụ lục và điều kiện chấm dứt. Hai khoản cùng có từ “bồi thường” có thể mang hai nhãn khác nhau. Không thể khắc phục thiếu thông tin bằng việc chọn model phức tạp hơn.

Với bản draft cũ, **chỉ luôn đoán normal cũng trùng 722/752 = 96,01% nhãn sơ bộ**, nhưng sẽ không tìm được abnormal nào. Đây là phép tính minh họa bẫy Accuracy từ phân bố draft, không phải kết quả model hay chỉ số chính thức.

TF-IDF + NB/LR/SVM là hướng baseline hợp lý để thực nghiệm theo Lab. Code LR và SVM **đã có class_weight='balanced'**. Trọng số chỉ thay đổi mức phạt sai khi học, không tạo thêm ví dụ rủi ro hoặc giải quyết thiếu ngữ cảnh. Nhân bản 30 mẫu cũng không tạo thêm 30 cơ chế độc lập. Không tự tạo dữ liệu bất lợi giả hoặc sửa nhãn để ép cân bằng 50/50.

Ưu tiên đúng miền, đủ ngữ cảnh, nhãn nhất quán, nguồn độc lập và ví dụ dễ nhầm. Khi được phép train, đánh giá precision/recall/F1 riêng abnormal, macro F1, support và confusion matrix bên cạnh Accuracy; so Dummy, phân tích false negative/false positive và learning curves. Không có một số lượng mẫu tối thiểu duy nhất bảo đảm chất lượng. [Tài liệu đánh giá scikit-learn 1.6.1](https://scikit-learn.org/1.6/modules/model_evaluation.html) và [class weights](https://scikit-learn.org/1.6/modules/generated/sklearn.linear_model.LogisticRegression.html) giải thích cơ chế này.

### Ngữ cảnh phải khớp đầu vào model

Classifier hiện chỉ nhận text, trong khi 180 dòng đã dùng tham chiếu khi gán nhãn. Không phải mọi tham chiếu đều thiết yếu, nhưng phải rà mẫu phụ thuộc ngữ cảnh. Ví dụ greenfuture_vehicle_service_0069 có lý do abnormal dựa vào định nghĩa lỗi ở khoản khác; text riêng của nó giới hạn theo lỗi khách. Không mặc định model đọc text sẽ suy ra được định nghĩa ở nơi khác.

Dataset thuê nhà cần đủ câu dẫn/ngữ cảnh trong input hoặc giữ chờ xử lý. Cách lấy ngữ cảnh phải xuất phát từ cấu trúc văn bản và dùng được khi inference; không lấy annotation_reason, risk_category hoặc nhãn đúng của test làm đặc trưng. Cờ context_required=false ở corpus cũ thể hiện agent đã xử lý nhãn, không chứng minh text độc lập luôn đủ cho classifier.

## 4. Đối chiếu từng phần với prompt

| Phần | Trạng thái và việc còn thiếu |
|---|---|
| Khảo sát Lab/môi trường | Có inventory và bản trích; kiểm tra Python 3.11.9, sklearn 1.6.1 và dependencies. Đã bổ sung docs/LAB_MAPPING.md đúng tên prompt. |
| Mục tiêu | Đúng hướng phát hiện bất lợi; phạm vi thuê nhà đã xác nhận lại. Không dùng chủ đề thay rủi ro. |
| Tiêu chí | Bản tổng quát có duyệt lịch sử; bản thuê nhà mới đã được người dùng duyệt riêng trong lần này, có hashes riêng. |
| Dataset | Corpus cũ có provenance kỹ thuật nhưng sai miền cho yêu cầu thuê nhà. Corpus thuê nhà mới chỉ ở seed/pilot, chưa đủ nhãn và chưa được duyệt. |
| Gán nhãn/kiểm duyệt | Agent giải thích nhãn; người dùng chọn Đạt/Chưa đạt. Chưa có dataset được người dùng chấp thuận. |
| Preprocessing | Có NFC/whitespace/lowercase, giữ phủ định/số. Chưa có thí nghiệm BoW, tách từ và ablation trên dataset được duyệt; chưa coi MVP 1B hoàn thành. |
| Classical ML | Có engine NB/LR/SVM/Dummy và TF-IDF + char alternative; chưa có model chính thức. |
| Evaluation | Có code selection validation/test, metrics, errors. Chưa có thực nghiệm; hiện chưa có kiểm tra độc lập nhãn test thuê nhà. |
| Save/load, inference offline | Đã kiểm thử fixture; chưa kiểm chứng trên model chính thức và điều khoản thuê nhà mới có nguồn. |
| Deep Learning | Chưa triển khai; xét sau baseline nếu dữ liệu/tài nguyên phù hợp, ghi rõ lý do nếu hoãn. Không mặc định dữ liệu ít phải dùng BiLSTM/CNN. |
| Báo cáo/bàn giao | Có tài liệu chạy; còn thiếu kết quả thực nghiệm thật, phân tích lỗi và nghiệm thu MVP 1. |
| MVP 2–4 | Chỉ tài liệu kiến trúc, chưa triển khai; vẫn cần cho phép sau khi MVP 1 được nghiệm thu. |

Prompt gốc có task chủ đề riêng; AGENTS.md hiện hành xác định clause_type là phụ. Lần này không tự mở thêm bài toán học chủ đề hoặc lấy điểm chủ đề thay điểm phát hiện bất lợi.

## 5. Đã bắt đầu chỉnh lại dữ liệu thuê nhà

Đã tải nguyên bản [mẫu thuê nhà trên Cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/mau-hop-dong-thue-nha-o-119240827172441217.htm) vào data/rental_staging/raw, giữ SHA256 và bản text. Script tools/collect_rental_seed.py tách **12 ứng viên theo nguyên Điều**, giữ chỗ trống và cả lỗi dùng tên bên có sẵn trong nguồn. Chưa tự sửa nội dung hợp đồng mẫu hoặc suy diễn phần bỏ trống.

Đã chuẩn bị **10 mẫu normal sơ bộ**, gồm các khoản đủ nghĩa về sửa hỏng theo lỗi, bảo đảm sử dụng ổn định, giới hạn chấm dứt, thay chủ sở hữu và sửa đổi cần hai bên ký. Có tiêu đề/câu dẫn, lý do, confidence gán nhãn định tính và spans; toàn bộ khớp nguồn. Xem [pilot.csv](../data/rental_staging/pilot.csv), [pilot_audit.json](../data/rental_staging/pilot_audit.json) và [hướng dẫn staging](../data/rental_staging/README.md).

Kiểm tra cuối: audit provenance cho cả 12 Điều và 10 ví dụ pilot đạt **22/22**, hash tiêu chí/nhãn thuê nhà khớp hồ sơ duyệt, bản sao prompt giống nguyên byte và CSV/approval/tiêu chí cũ không đổi. Đã chạy audit thống kê với Pipeline.fit bị chặn để xác nhận không huấn luyện. [Bằng chứng kiểm tra staging](rental_pilot_verification.json). Sau các thay đổi, chạy lại verify_mvp1.py vẫn **86/86 tests qua**, mọi bước kiểm tra đều qua; chưa có thư mục artifacts/model chính thức.

**Pilot này chỉ kiểm chứng quy trình lấy nguồn/gán nhãn và ví dụ normal; có 1 họ mẫu, 0 abnormal, chưa phải dataset đại diện hoặc dùng để train.** Không thêm các dòng này vào CSV chính rồi coi là đã khắc phục mất cân bằng. Mọi Điều chưa được chọn vẫn giữ ở candidates.csv, chưa được coi là đã xử lý/gán nhãn toàn bộ.

Đầu mối nguồn tiếp theo đã tìm qua tìm kiếm: [danh sách biểu mẫu Phòng Công chứng số 6](https://www.congchung6.gov.vn/vi/document/bieu-mau-216.aspx) có hai mẫu thuê nhà và [bài hướng dẫn thuê nhà của Khoa Luật HUIT](https://law.huit.edu.vn/tin-tuc-hoat-dong/nhung-van-de-phap-ly-sinh-vien-can-chu-y-khi-thue-nha-tro) liệt kê file mẫu. Hai trang này chưa mở/tải được đầy đủ trong công cụ web lần này; **chỉ là đầu mối, không tính vào số nguồn đã thu thập**, chưa xác minh tính độc lập/quyền dùng. Không lấy nhiều bản chép một mẫu làm nhiều nguồn độc lập; không dùng bản án kể lại tranh chấp thay nguyên điều khoản hay lấy thông tin cá nhân làm dataset.

## 6. Thứ tự tiếp theo và điều kiện kết thúc từng bước

1. **Hoàn thiện nguồn thuê nhà thật.** Mở rộng từ pilot sang các mẫu độc lập, đặc biệt nguồn có cơ chế bất lợi thật; giữ cả điều khoản bình thường dễ nhầm. Thuê nhà ở/phòng trọ/căn hộ là miền chính. Xác minh việc sử dụng nguồn; nguồn có điều kiện chưa rõ phải trình trước khi sử dụng. Không cố đạt 1.500–3.000 dòng bằng cách chép/tách vụn hoặc tạo giả.
2. **Sửa trích và hoàn thiện nhãn.** Rà toàn bộ Điều, số liệu trống, định nghĩa bên thuê, cọc, phụ lục, ngoại lệ và đơn vị đầu vào. Hoàn thành lý do/bằng chứng và nhãn sơ bộ; cập nhật ví dụ abnormal nguồn thật và các cặp dễ nhầm. Nếu cần sửa tiêu chí đã duyệt, trình phiên bản sửa thay vì tự đổi.
3. **Kiểm tra độ bao phủ trước duyệt.** Thống kê abnormal theo dấu hiệu, nguồn/họ mẫu và split; bảo đảm không chỉ có một nguồn kiểm tra hoặc một ví dụ cho một dạng rủi ro. Mục tiêu làm việc ban đầu có thể là khoảng 100–200 abnormal thật từ nhiều họ mẫu; đây chỉ là ngân sách thu thập đề xuất, không phải chuẩn khoa học/điều kiện tự nghiệm thu. Nếu nguồn thực tế không đủ thì báo đúng giới hạn và điều chỉnh phạm vi với người dùng, không ép nhãn.
4. **Trình dataset để người dùng duyệt.** Chỉ sau quyết định Đạt thực tế mới chốt CSV thuê nhà thành data/clauses.csv, snapshot corpus cũ, đồng bộ source manifest, đúng tiêu chí/profile/hash, trạng thái reviewed và hồ sơ nguồn. Người dùng không phải tự nhập/sửa nhãn. Bản cũ không được thay thế âm thầm.
5. **Xin xác nhận chuyển MVP 1A → 1B theo prompt.** Trước đó còn phải tích hợp gate/profile thuê nhà vào core CLI và kiểm tra không thể train nhầm corpus ngoài miền. Việc code hiện tại chạy audit/readiness không có nghĩa workflow mới đã tích hợp xong.
6. **Sau khi được phép: preprocessing và baseline.** So sánh BoW/TF-IDF, n-grams, cách tách từ phù hợp; NB/LR/SVM trên cùng split. Fit chỉ train, chọn cấu hình/threshold nếu có chỉ trên validation. Nếu dùng oversampling, chỉ trong train sau chia nhóm; không nhân bản sang test.
7. **Đánh giá và hoàn tất MVP 1.** Báo số liệu thật cùng support/độ bất định, lỗi mẫu, kiểm tra save/load, inference thuê nhà mới có nguồn thật, cân nhắc DL, chạy toàn bộ kiểm thử, hoàn thiện hướng dẫn rồi trình nghiệm thu. Không làm web/MVP 2 trước cho phép.

### Lệnh đã chạy và cách tái kiểm tra

```powershell
& .\.venv\Scripts\python.exe tools/verify_mvp1.py
& .\.venv\Scripts\python.exe tools/audit_progress.py
& .\.venv\Scripts\python.exe tools/collect_rental_seed.py
& .\.venv\Scripts\python.exe tools/prepare_rental_pilot.py
```

Các script mới từ chối ghi đè báo cáo/staging/pilot đã có. Để chạy lại thống kê, chỉ định --output reports/progress_audit_v2.json. Không chạy lại collector/pilot vào cùng đích. Lần tải nguồn ban đầu bị sandbox chặn socket; đã thành công qua cơ chế nâng quyền thực thi thông thường. Đây không phải lỗi nguồn và không có thay đổi quyền sandbox toàn cục.

**Kết luận tiến độ:** khung kỹ thuật MVP 1 có thể tái sử dụng, nhưng phần quyết định chất lượng là dataset thuê nhà có nhãn và ngữ cảnh đúng vẫn ở giai đoạn đầu. Không có Accuracy/Precision/Recall/F1 chính thức; chưa chuyển MVP 1B hoặc MVP 2.
