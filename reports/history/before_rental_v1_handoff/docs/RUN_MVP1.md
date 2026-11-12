# Chạy ContractGuard MVP 1 trên Windows

**Cập nhật:** phạm vi hiện hành là thuê nhà/bảo vệ người thuê. Tiêu chí thuê nhà đã được duyệt riêng tại reports/rental_criteria_approval.json; corpus cũ 752 dòng chưa có nguồn thuê nhà. Các lệnh audit/readiness dưới đây vẫn kiểm tra bản cũ, không chứng minh dataset đúng miền. Staging mới và cách đọc ở data/rental_staging/README.md. Chưa tích hợp profile thuê nhà vào training CLI; không chạy train theo cổng duyệt lịch sử. Phải hoàn thiện/duyệt dataset thuê nhà và được phép MVP 1B trước. Xem reports/MVP1_PROGRESS_REVIEW.md.

## Trạng thái hiện tại

Có thể chạy kiểm thử, kiểm tra nguồn và xem điều kiện còn thiếu. Chưa có model phát hiện rủi ro chính thức để dự đoán. Tiêu chí đã được người dùng xác nhận “Tiêu chí Đạt” ngày 08/11/2026, ghi tại reports/criteria_approval.json. CSV đã có 752 nhãn sơ bộ (722 normal, 30 abnormal), đang chờ người dùng duyệt theo reports/DATASET_REVIEW.md; lệnh train vẫn dừng trước khi tạo artifact.

## Chuẩn bị môi trường

Môi trường `.venv` hiện có đã được kiểm tra bằng `pip check`. Nếu cần tạo lại, dùng Python 3.11 hoặc 3.12:

```powershell
Set-Location D:\NLP\ContractGuard
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
& .\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps -e .
```

Không cần kích hoạt môi trường. Các lệnh dưới đây dùng trực tiếp Python của project:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& .\.venv\Scripts\python.exe tools\verify_mvp1.py
& .\.venv\Scripts\python.exe -m contractguard audit --data data\clauses.csv
& .\.venv\Scripts\python.exe -m contractguard readiness --output reports\readiness.json
& .\.venv\Scripts\python.exe tools\inspect_annotation.py --document fpt_internet --count 3 --context
& .\.venv\Scripts\python.exe tools\inspect_annotation.py --label abnormal --count 30
& .\.venv\Scripts\python.exe tools\inspect_annotation.py --clause-id viettel_stracking_2026_0142 --count 1 --context
```

`audit` kiểm tra cấu trúc, nguồn, hash, vị trí trích và bản trùng, kể cả hàng pending. Mã thoát 0 chỉ có nghĩa kiểm tra đó không phát hiện lỗi kỹ thuật. `readiness` là lệnh chẩn đoán, mã thoát 0 nghĩa đã tạo được báo cáo; phải đọc `official_training_ready` và `blockers`. Không lệnh nào xác nhận nhãn đúng hay tự cấp quyền train.

## Sau hai lần kiểm duyệt thật

1. Người dùng xác nhận tiêu chí cụ thể trong `ANNOTATION_GUIDELINES.md` Đạt/Chưa đạt. Agent ghi nhận đúng quyết định và phiên bản.
2. Agent hoàn tất sửa bản trích, đọc ngữ cảnh, gán nhãn sơ bộ và lý do trong CSV chính, bổ sung nguồn thật khi thiếu. Người dùng xác nhận dữ liệu Đạt/Chưa đạt; không phải tự gán nhãn.
3. Sau khi được duyệt, agent mới cập nhật các hàng accepted/rejected, reviewer và dấu thời gian thật; hàng được nhận có annotation_status=reviewed. Agent ghi đúng hashes của tiêu chí, nhãn, CSV và nguồn vào approval. Không tự điền tên người duyệt hoặc thay cờ để thử train.
4. Chạy readiness; nếu thiếu ít nhất 5 nhóm độc lập cho một nhãn hoặc không chia được ba tập có đủ hai nhãn, agent bổ sung dữ liệu. Không nới split để lấy điểm đẹp.

Các lệnh bên dưới chỉ dùng khi cổng duyệt đã hợp lệ. Chọn thư mục run mới, không ghi đè lần chạy trước:

```powershell
& .\.venv\Scripts\python.exe -m contractguard train --data data\clauses.csv --output artifacts\mvp1_run_001 --seed 42
& .\.venv\Scripts\python.exe tools\predict.py --model artifacts\mvp1_run_001\model.joblib --text "Bên cung cấp có trách nhiệm bàn giao thiết bị trong vòng hai ngày."
& .\.venv\Scripts\python.exe tools\predict.py --model artifacts\mvp1_run_001\model.joblib --input data\inference_examples.json --output outputs\predictions.json
& .\.venv\Scripts\python.exe tools\verify_mvp1.py
```

Ví dụ câu ở trên và `inference_examples.json` chỉ minh họa thao tác, không có nhãn chuẩn và không dùng để báo chất lượng. Agent còn phải chọn điều khoản mới có nguồn thật, ngoài dataset, để kiểm tra model chính thức.

Mỗi run tạo `model.joblib`, `model.json`, metrics, split assignments, test predictions, errors, confusion matrix và báo cáo. Chọn model theo validation Macro F1, refit train+validation rồi đánh giá test; không dùng test chọn cấu hình. Metrics gồm Accuracy, Precision/Recall/F1 macro, F1 weighted và từng lớp, support, confusion matrix. Save/load phải giữ nguyên dự đoán.

Inference trả nhãn normal/abnormal; chỉ tự yêu cầu xem lại khi đầu vào không có feature đã học. Cơ chế này chưa nhận diện mọi trường hợp ngoài miền hay thiếu ngữ cảnh. `confidence=null` vì chưa hiệu chỉnh xác suất. Chỉ nạp model tin cậy do project tạo tại máy.

## Tái lập bước chuẩn bị nhãn — dành cho agent

Không cần chạy các công cụ này để duyệt hoặc sử dụng dataset. Nếu cần trích tham chiếu PDF lại, dùng dependency tùy chọn `pdfplumber==0.11.9` (extra `annotation` trong pyproject.toml) hoặc Python runtime đã có thư viện đó. Các bản trích tham chiếu, phiên bản extractor và SHA256 đã lưu ở reports/source_quality; chạy core/tests/train không cần pdfplumber.

`prepare_annotation.py` dùng snapshot bất biến, sửa cấu trúc theo annotation_structure.py và đối chiếu khoảng trắng với bản trích hình học. `risk_annotation_notes.tsv` chứa quyết định đã rà soát cho từng ứng viên; `apply_risk_annotations.py` chỉ áp dụng các quyết định này, không tự suy nhãn khi thiếu quyết định. Script từ chối ghi đè khi tìm thấy review của người dùng hoặc CSV đã đổi ngoài phiên chuẩn bị. `check_risk_annotations.py` kiểm tra và tạo hướng dẫn duyệt; không chạy sau khi CSV đã được người dùng duyệt mà chưa cập nhật hồ sơ phiên bản.

Dừng sau MVP 1. Các bước web/backend, retrieval và SQLite vẫn cần cho phép riêng.
