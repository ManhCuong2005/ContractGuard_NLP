"""One-time documentation transition after the actual accepted v1 experiment."""
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    approval = json.loads((ROOT/'reports/rental_dataset_approval.json').read_text('utf-8'))
    metrics = json.loads((ROOT/'outputs/rental_mvp1b_v1/metrics.json').read_text('utf-8'))
    assert 'Dataset thuê nhà Đạt' in json.dumps(approval, ensure_ascii=False)
    assert metrics['selected_model'] == 'bow_unigram__logistic_regression'
    docs = {
        'README.md': r'''# ContractGuard — phát hiện dấu hiệu bất lợi trong điều khoản thuê nhà

Phạm vi: hợp đồng thuê nhà/phòng/căn hộ tiếng Việt, bảo vệ người thuê. Chỉ triển khai MVP 1 offline; không gọi API AI bên ngoài.

**MVP 1A đã được người dùng duyệt bằng câu “Dataset thuê nhà Đạt”. MVP 1B đã chạy thực nghiệm truyền thống nhưng chất lượng phát hiện abnormal chưa đạt; toàn bộ MVP 1 chưa hoàn thành.**

[Dataset được duyệt](data/rental_approved_v1/clauses.csv): 517 điều khoản, 489 normal và 28 abnormal, 17 tài liệu nguồn; nhãn/lý do/ngữ cảnh/provenance giữ nguyên bản đã trình. [Hồ sơ xác nhận](reports/rental_dataset_approval.json) ghi quyết định thật, không tự phê duyệt. [Bản draft](data/clauses_rental_v1.csv) và [752 mẫu legacy](data/clauses.csv) được bảo toàn.

Đã so sánh 23 cấu hình gồm Dummy, BoW/TF-IDF/ngram và NB/LR/SVM trên validation. Mô hình được chọn là BoW unigram + Logistic Regression. **Test: Accuracy 93,62%, nhưng Recall abnormal 0% — bỏ sót 6/6 điều khoản bất lợi, bằng Dummy trên tập test.** Không dùng Accuracy này để kết luận mô hình tốt. Save/load và inference offline đã chạy; model chỉ dùng nghiên cứu ở trạng thái hiện tại.

Đọc [báo cáo thực nghiệm và sáu lỗi](reports/MVP1B_EXPERIMENT_REPORT.md), [trạng thái/phần còn lại](reports/MVP1_STATUS.md), [hướng dẫn chạy](docs/RUN_MVP1.md), [schema](docs/RENTAL_DATASET_SCHEMA.md), [ánh xạ Lab](docs/LAB_MAPPING.md). Thư mục `outputs/rental_mvp1b_v1` giữ model, metrics, split/precommit, dự đoán, phân tích và biểu đồ PNG/SVG.

Bước tiếp theo vẫn thuộc MVP 1: tăng dữ liệu bất lợi thật và đa dạng nguồn, kiểm duyệt phiên bản mới, thực nghiệm theo validation và giữ test mới chưa dùng để chọn mô hình. CNN/BiLSTM chưa triển khai; không có kết quả deep learning. Không bắt đầu MVP 2 cho đến khi người dùng xác nhận MVP 1 đạt và cho phép.
''',
        'data/README.md': r'''# Dữ liệu ContractGuard

**Dataset thuê nhà v1 đã được người dùng duyệt:** [rental_approved_v1/clauses.csv](rental_approved_v1/clauses.csv), 517 dòng = 489 normal + 28 abnormal. [Hồ sơ duyệt](../reports/rental_dataset_approval.json) ghi đúng câu “Dataset thuê nhà Đạt”. Chỉ bản snapshot này được gate rental cho phép huấn luyện chính thức.

- `rental_approved_v1/clauses.csv`: text/label không đổi so với bản trình; annotation_status=reviewed, review_status=accepted, reviewer=user_in_chat theo quyết định thật. Không suy ra tên thật hoặc có chuyên gia độc lập đã rà từng nhãn.
- `rental_approved_v1/sources.json`, `approval.json`: manifest và phê duyệt đóng băng; giữ hash raw/pages và proof nguồn scan.
- `rental_approved_v1/reviewed_draft.csv`, `reviewed_draft_sources.json`, `review_snapshot.json`, `approval_before_acceptance.json`: bytes trước quyết định để truy vết.
- `clauses_rental_v1.csv`: bản draft 517 dòng đã trình, giữ nguyên draft/pending vì là hồ sơ lịch sử, không phải snapshot train hiện hành.
- `rental_mvp1a_v1/sources.json`, `raw`, `candidates.json`: 17 nguồn đóng góp, archive và 1.411 ứng viên kỹ thuật; phần dự trữ không tự có nhãn normal.
- `rental_mvp1a_v1/annotation_decisions.json`, `annotation_ledger.json`: quyết định sơ bộ của agent và phần dự trữ/hold, không phải công việc gán nhãn giao cho người dùng.
- `rental_mvp1a_v1/legacy_auxiliary.csv`: 7 câu tranh chấp chung từ bộ cũ, ngoài train/test chính.
- `clauses.csv`, `sources.json`, `raw`, `review`, `snapshots`: bộ legacy 752 dòng ngoài miền, bảo toàn; không dùng làm kết quả thuê nhà.

Tiêu chí đích `docs/LABELING_GUIDELINES.md` đã được duyệt và giữ nguyên hash. label/risk_label là normal/abnormal; clause_type/category chỉ là chủ đề phụ. annotation_reason/risk_category/ID/nguồn không đi vào features. label_confidence là nhận định gán nhãn, không phải xác suất model. normal không chứng nhận điều khoản hoặc toàn hợp đồng an toàn.

28 abnormal còn ít, thiếu ba nhóm dấu hiệu; thực nghiệm v1 bỏ sót toàn bộ 6 abnormal test. Xem [báo cáo thực nghiệm](../reports/MVP1B_EXPERIMENT_REPORT.md). Không thay nhãn hoặc nhân bản theo dự đoán; dữ liệu mới cần snapshot và quyết định duyệt riêng. Không chạy lại tool đóng gói/handoff lịch sử lên bản đã chốt.
''',
        'reports/MVP1_STATUS.md': r'''# Trạng thái hiện hành ContractGuard

**MVP 1A đã được người dùng duyệt; thực nghiệm truyền thống MVP 1B đã chạy nhưng chưa đạt chất lượng phát hiện rủi ro. Toàn bộ MVP 1 chưa hoàn thành. Không sang MVP 2.**

Ngày 09/11/2026 ghi nhận câu xác nhận “Dataset thuê nhà Đạt” trong [hồ sơ duyệt](rental_dataset_approval.json), đóng băng [dataset được duyệt](../data/rental_approved_v1/clauses.csv): 517 dòng, 489 normal/28 abnormal, 17 nguồn. Text/label giữ nguyên bản đã trình; không đổi tiêu chí, bản draft, dữ liệu 752 dòng hoặc approval legacy.

Đã tích hợp profile rental và gate đầy đủ: kiểm tra quyết định người dùng, hash tiêu chí/nhãn/dataset/nguồn, spans/proof scan, trạng thái review và miền người thuê. Chốt trước fit nhóm nguồn/họ/gần trùng: train 315 (16 abnormal), validation 108 (6), test 94 (6). Chọn 23 ứng viên bằng validation, ghi quyết định trước test; refit ứng viên thắng trên train+validation, đánh giá test một lần với Dummy.

Kết quả BoW unigram + Logistic Regression: Accuracy 93,62%, macro F1 0,4835; Precision/Recall/F1 abnormal đều 0, bỏ sót 6/6 abnormal. Ma trận normal/abnormal `[[88,0],[6,0]]`, bằng Dummy. Validation của ứng viên thắng Recall abnormal 50%, không chuyển được sang nguồn test. Đã lưu/nạp và chạy inference offline, xuất dự đoán/phân tích sáu lỗi/biểu đồ. [Báo cáo chi tiết](MVP1B_EXPERIMENT_REPORT.md).

Việc còn lại trong MVP 1:

1. Tăng abnormal có nguồn thật, khác họ; thêm các cơ chế chưa có (deemed_consent, automatic_renewal, overbroad_data_use), điều khoản tương phản/ngoại lệ và hợp đồng đại diện hơn. Agent trích/nhãn/giải thích; người dùng duyệt bản mới, không tự nhập nhãn.
2. Chốt protocol mới theo train/validation; capture warning từng ứng viên, xác minh hội tụ. Giữ test v1 là phân tích hồi cứu, thu nguồn test mới chưa dùng chọn mô hình khi công bố kết quả cải tiến.
3. CNN/BiLSTM từ đầu theo prompt chưa triển khai/huấn luyện. Baseline truyền thống hiện chưa đạt; không có căn cứ khẳng định deep learning cải thiện, không có số đo DL.
4. Hoàn thiện báo cáo cuối và tiêu chí chất lượng trên tập hợp lệ; chỉ chốt MVP 1 khi người dùng đánh giá đạt. Chưa làm backend/UI/truy hồi/quản lý hợp đồng.

Các báo cáo MVP 1A/audit/verification trước phê duyệt giữ như lịch sử, không phải trạng thái approval hiện hành hoặc metrics model. Test kỹ thuật không được dùng làm chất lượng NLP. Biên bản kiểm chứng hiện hành: `reports/rental_mvp1b_verification.json` và JUnit `rental-mvp1b-test-results.xml`.
''',
        'docs/RUN_MVP1.md': r'''# Chạy MVP 1 offline — profile thuê nhà

Thư mục `D:\NLP\ContractGuard`. Dataset hiện hành đã được duyệt: `data/rental_approved_v1/clauses.csv`. Bản draft và 752 dòng legacy chỉ để truy vết. Model v1 có Recall abnormal test bằng 0, chưa dùng làm công cụ cảnh báo đáng tin cậy.

## Môi trường và kiểm tra

```powershell
Set-Location D:\NLP\ContractGuard
.venv\Scripts\python.exe -X utf8 -m pip check
.venv\Scripts\python.exe -X utf8 -m pytest -q --junitxml=reports/rental-mvp1b-test-results.xml
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

```powershell
.venv\Scripts\python.exe -X utf8 tools/report_rental_experiment.py
```

Lệnh này chỉ nạp output v1, vẽ biểu đồ, phân tích và kiểm tra inference; không fit hoặc chọn lại mô hình. Cache matplotlib nằm trong workspace. Không chạy lại `accept_rental_dataset_v1.py` (migration một lần), `package_rental_dataset.py` hoặc `write_rental_handoff.py` (hồ sơ trước duyệt đã đóng băng). Không tự thay approval/hash để vượt gate. Dữ liệu mới cần bản mới và xác nhận thật của người dùng.
'''
    }
    for rel, content in docs.items():
        destination = ROOT / rel
        backup = ROOT / 'reports/history/before_rental_mvp1b' / rel
        if destination.exists() and not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(destination, backup)
        destination.write_text(content, encoding='utf-8')
    schema = ROOT / 'docs/RENTAL_DATASET_SCHEMA.md'
    content = schema.read_text('utf-8')
    notice = '**Cập nhật 09/11/2026:** Người dùng đã duyệt “Dataset thuê nhà Đạt”. Snapshot hiện hành `data/rental_approved_v1/clauses.csv` giữ nguyên text/label; annotation_status=reviewed, review_status=accepted, reviewer=user_in_chat theo quyết định thật. Mô tả draft/pending bên dưới ghi trạng thái của bản trình gốc được bảo toàn, không phải trạng thái snapshot train. Xem `reports/rental_dataset_approval.json`.\n\n'
    if notice not in content:
        schema.write_text(content.replace('\n\n', '\n\n'+notice, 1), encoding='utf-8')
    review = ROOT/'reports/MVP1A_REVIEW.md'
    content = review.read_text('utf-8')
    notice = '**Hồ sơ lịch sử trước duyệt. Cập nhật 09/11/2026:** Người dùng đã xác nhận “Dataset thuê nhà Đạt”. Bản được duyệt riêng tại `data/rental_approved_v1/clauses.csv`; xem [trạng thái hiện hành](MVP1_STATUS.md) và [thực nghiệm MVP 1B](MVP1B_EXPERIMENT_REPORT.md). Các câu “chưa duyệt/chưa có metrics” phía dưới mô tả thời điểm trình bản gốc.\n\n'
    if notice not in content:
        review.write_text(content.replace('\n\n', '\n\n'+notice, 1), encoding='utf-8')
    worklog = ROOT/'reports/MVP1A_WORKLOG.md'
    content = worklog.read_text('utf-8') if worklog.exists() else ''
    entry = '\n\n## 09/11/2026 — duyệt dataset và thực nghiệm MVP 1B\n\nĐã nhận xác nhận thật “Dataset thuê nhà Đạt”, đóng băng snapshot riêng, tích hợp rental profile và gate, chia theo nhóm trước fit; chạy 23 ứng viên trên validation, refit winner BoW+LR và test một lần. Recall abnormal test 0/6; không đạt mục tiêu cảnh báo, không chuyển MVP 2. Đã lưu/nạp/inference, phân tích lỗi, biểu đồ và báo cáo. Bản draft/legacy giữ nguyên. Xem `MVP1B_EXPERIMENT_REPORT.md`.\n'
    if entry not in content:
        worklog.write_text(content+entry, encoding='utf-8')
    print('Current MVP 1B documentation updated; preapproval documentation archived.')


if __name__ == '__main__':
    main()
