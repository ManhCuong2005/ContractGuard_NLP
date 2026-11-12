# Chạy MVP 1 offline — profile thuê nhà

Thư mục `D:\NLP\ContractGuard`. Dataset hiện hành đã được duyệt: `data/rental_approved_v1/clauses.csv`. Bản draft và 752 dòng legacy chỉ để truy vết. Model v1 có Recall abnormal test bằng 0, chưa dùng làm công cụ cảnh báo đáng tin cậy.

## Môi trường và kiểm tra

```powershell
Set-Location D:\NLP\ContractGuard
.venv\Scripts\python.exe -X utf8 -m pip check
.venv\Scripts\python.exe -X utf8 -m pytest -q --junitxml=reports/rental-v2-test-results.xml
.venv\Scripts\python.exe -X utf8 -m contractguard readiness --profile rental
```

Tạo môi trường mới nếu cần: Python 3.11, cài `requirements-experiments-lock.txt` (gồm core/thu thập/plot), sau đó `pip install --no-build-isolation --no-deps -e .`. Không cần PyTorch, TensorFlow hoặc API AI cho thực nghiệm truyền thống hiện tại. `tools/review_rental_dataset.py` đọc bản draft đã trình và hỗ trợ lọc label/clause-id; snapshot được duyệt cùng text/label, khác trạng thái kiểm duyệt.

## Xem kết quả đã chạy

`outputs/rental_mvp1b_v1` có `model.joblib`, `model.json`, `metrics.json`, `precommit.json`, `validation_selection.json`, `splits.csv`, `test_predictions.csv`, `errors.csv`, `error_analysis.csv`, `validation_comparison.csv`, `figures` PNG/SVG. Đọc `reports/MVP1B_EXPERIMENT_REPORT.md` để hiểu thất bại trên abnormal; không diễn giải Accuracy cao là mô hình tốt.

```powershell
.venv\Scripts\python.exe -X utf8 predict.py --model outputs/rental_mvp1b_v1/model.joblib --input outputs/rental_mvp1b_v1/offline_inference_inputs.json --output outputs/rental_mvp1b_v1/cli_inference.json
```

Hoặc `python -m contractguard predict` với cùng tham số; `--text` thay `--input` để dự đoán một chuỗi. JSON đầu vào là mảng chuỗi, mỗi chuỗi là khoản đủ ngữ cảnh như dataset; không phải file PDF. Confidence null vì chưa hiệu chỉnh; needs_review khi không có features quen thuộc. Các input minh họa là mẫu test cũ được dùng lại kiểm tra đường inference, không là đánh giá dữ liệu mới. Chỉ nạp joblib tin cậy do dự án tạo.

## Tái lập thực nghiệm

Lệnh đã dùng cho v1, không ghi đè output đã có:

```powershell
.venv\Scripts\python.exe -X utf8 -m contractguard train --profile rental --data data/rental_approved_v1/clauses.csv --output outputs/rental_mvp1b_v1 --seed 42
```

Engine từ chối thư mục đã tồn tại. Tái lập cần output mới và giữ nguyên dataset/hash/code/dependency, seed/protocol; không coi tái lập trên cùng test là bằng chứng chất lượng mới. Thay cấu hình hoặc lựa chọn sau khi xem test v1 cần test mới cho đánh giá cuối.

## Xem bản dữ liệu mở rộng v2, chưa huấn luyện

`data/clauses_rental_v2.csv` có 820 mẫu, 32 abnormal, chưa đạt mục tiêu 1.000–2.000/500 abnormal. Đọc `reports/RENTAL_EXPANSION_V2_REVIEW.md` và `docs/RENTAL_V2_DATA_CARD.md`; v2 chưa được duyệt. Bộ v1, approval v1 và kết quả đã chạy được giữ nguyên.

```powershell
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --data data/clauses_rental_v2.csv --label abnormal --origin new --count 10
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --data data/clauses_rental_v2.csv --start 0 --count 25
.venv\Scripts\python.exe -X utf8 tools/verify_rental_expansion_v2.py
```

Tăng `--start` để duyệt cả file; không phải nhập nhãn. Lệnh review/verify không phê duyệt hoặc huấn luyện. Khi cập nhật quyết định hoặc nguồn, `tools/package_rental_expansion_v2.py` đóng gói draft theo ID rõ ràng; `tools/report_rental_expansion_v2.py` tái tạo báo cáo theo số liệu hiện tại. Không đổi cờ approval để chạy train. JUnit v1 99 test là bằng chứng lịch sử, không ghi đè; kết quả kiểm thử hiện tại nằm ở JUnit v2.

```powershell
.venv\Scripts\python.exe -X utf8 tools/report_rental_experiment.py
```

Lệnh này chỉ nạp output v1, vẽ biểu đồ, phân tích và kiểm tra inference; không fit hoặc chọn lại mô hình. Cache matplotlib nằm trong workspace. Không chạy lại `accept_rental_dataset_v1.py` (migration một lần), `package_rental_dataset.py` hoặc `write_rental_handoff.py` (hồ sơ trước duyệt đã đóng băng). Không tự thay approval/hash để vượt gate. Dữ liệu mới cần bản mới và xác nhận thật của người dùng.
