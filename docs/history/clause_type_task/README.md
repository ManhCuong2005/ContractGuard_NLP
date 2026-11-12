# ContractGuard — MVP 1: NLP Core

**Trạng thái: đã xây dựng pipeline và bộ ứng viên; người dùng đã xác nhận tiêu chí 8 nhãn ngày 05/11/2026, đang chờ kiểm duyệt dữ liệu. MVP 1 chưa hoàn thành; chưa huấn luyện chính thức.** Không có mã MVP 2–4.

Mục tiêu đề xuất: phân loại loại điều khoản tiếng Việt bằng mô hình tự huấn luyện tại máy. Không dùng API AI ngoài; không công bố điểm thực nghiệm khi chưa chạy trên dữ liệu thật đã duyệt.

Đọc [kiến trúc](docs/ARCHITECTURE.md), [tiêu chí gán nhãn đã chốt](docs/ANNOTATION_GUIDELINES.md) và [trạng thái bàn giao](reports/MVP1_STATUS.md).

**Bản dữ liệu hiện tại là v2:** [Excel duyệt 802 điều khoản đã xử lý nguồn](outputs/annotation_20261108_v2/ContractGuard_DuyetNhan.xlsx), CSV `data/review/v2/clauses.csv`. Bản v1 được giữ để đối chiếu, không còn dùng làm bản gửi duyệt chính. Không còn yêu cầu người dùng duyệt một danh sách đề xuất loại.

## Chạy trên Windows PowerShell

Môi trường `.venv` đã được tạo trong dự án. Không cần activate nên không cần đổi ExecutionPolicy.

```powershell
Set-Location D:\NLP\ContractGuard
$env:PYTHONIOENCODING = 'utf-8'
& .\.venv\Scripts\python.exe -m pytest -q
& .\.venv\Scripts\python.exe -m contractguard audit --data data\review\v2\clauses.csv --output reports\data_quality.json
```

Nếu cần tạo lại môi trường (Python 3.11 hoặc 3.12):

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
& .\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps -e .
```

Không chạy lại collector lên bộ dữ liệu đã kiểm duyệt. Nó có cổng chống ghi đè. Bản trích tài liệu học tập nằm ở `reports/materials/`, danh mục kèm SHA256 là `inventory.json`.

## Những việc cần người dùng chốt

1. Tiêu chí và 8 nhãn tại `docs/ANNOTATION_GUIDELINES.md` đã được người dùng xác nhận; áp dụng phiên bản này khi kiểm duyệt.
2. Mở [file Excel duyệt nhãn v2](outputs/annotation_20261108_v2/ContractGuard_DuyetNhan.xlsx). Agent đã xử lý bản trích, ghép/tách và điền nhãn sơ bộ; người dùng chỉ chọn Đạt/Chưa đạt ở cột A. Xem `data/review/README.md`.
3. Agent sửa các mục Chưa đạt và đề xuất lại. Sau khi người dùng xác nhận bản cuối, agent ghi hồ sơ duyệt. Nhãn sơ bộ **chưa phải tập chuẩn được duyệt**; không tự gán accepted để lách gate.
4. Sau khi xác nhận tập cuối, lấy hash bằng lệnh sau rồi ghi xác nhận vào `configs/approval.json`. Lệnh chỉ in hash, không phê duyệt.

```powershell
& .\.venv\Scripts\python.exe -m contractguard approval-digests --data data\review\v2\clauses.csv
```

Các cờ `criteria_approved`, `dataset_approved`, `source_use_confirmed` chỉ được đặt true sau xác nhận thật. Điền `approved_by`, `approved_at` ISO có múi giờ, bốn hash, và `reviewed_source_ids`. Nếu CSV/tiêu chí/nhãn/manifest đổi, hash hết khớp và cần duyệt lại. Đây là hồ sơ xác nhận cục bộ, không phải cơ chế xác thực danh tính.

## Huấn luyện và thử điều khoản mới — chỉ sau khi duyệt

```powershell
& .\.venv\Scripts\python.exe -m contractguard train --data data\review\v2\clauses.csv --output artifacts\run_001
& .\.venv\Scripts\python.exe -m contractguard predict --model artifacts\run_001\model.joblib --text 'Bên mua có trách nhiệm thanh toán trong vòng 15 ngày kể từ ngày nhận hóa đơn.'
& .\.venv\Scripts\python.exe -m contractguard predict --model artifacts\run_001\model.joblib --input data\inference_examples.json --output artifacts\run_001\new_predictions.json
```

`data/inference_examples.json` chứa câu tự viết để thử thao tác, được đánh dấu riêng và không đưa vào training/test hoặc tính chỉ số chính thức. Chưa có kết quả của các câu này khi chưa có model chính thức.

Kết quả một run: `model.joblib`, `model.json`, `metrics.json`, `report.md`, `splits.csv`, `split_counts.json`, `test_predictions.csv`, `errors.csv`, `confusion_matrix.csv`. Confusion matrix: hàng là nhãn thật, cột là dự đoán; thứ tự nhãn ghi trong file. Dùng `metrics.json` lấy Accuracy, Precision/Recall/F1 macro, F1 weighted và chỉ số từng lớp.

Không chọn seed/model dựa trên điểm test rồi báo lại như test độc lập. `run_001` không ghi đè; lần chạy mới phải dùng thư mục khác và giữ quy trình đánh giá đã chốt. Không nạp joblib không rõ nguồn gốc.

Sau khi hoàn thành và báo cáo MVP 1, dừng lại; chỉ bắt đầu giao diện/backend khi người dùng xác nhận MVP 1 đạt yêu cầu và cho phép MVP 2.
