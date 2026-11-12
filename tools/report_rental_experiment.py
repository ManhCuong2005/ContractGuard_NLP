"""Read the frozen v1 experiment and produce figures/error analysis; never fit models."""
import csv
import json
import os
from collections import Counter
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', str(Path(__file__).resolve().parents[1] / '.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from contractguard.dataset import sha256, write_json
from contractguard.model import Predictor

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'outputs/rental_mvp1b_v1'


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    metrics = json.loads((RUN / 'metrics.json').read_text('utf-8'))
    dataset = ROOT / 'data/rental_approved_v1/clauses.csv'
    records = {r['clause_id']: r for r in read_rows(dataset)}
    splits = read_rows(RUN / 'splits.csv')
    errors = read_rows(RUN / 'errors.csv')
    figures = RUN / 'figures'
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'savefig.dpi': 160})

    fig, ax = plt.subplots(figsize=(5.8, 4.8), layout='constrained')
    matrix = np.asarray(metrics['test']['confusion_matrix'])
    ax.imshow(matrix, cmap='Blues', vmin=0)
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=['normal', 'abnormal'],
           yticklabels=['normal', 'abnormal'], xlabel='Predicted label', ylabel='Reviewed label',
           title='Held-out test: 94 clauses, 6 abnormal')
    for (i, j), count in np.ndenumerate(matrix):
        ax.text(j, i, str(count), ha='center', va='center', fontsize=18,
                color='white' if count > matrix.max()/2 else 'black')
    for ext in ['png', 'svg']:
        fig.savefig(figures / f'confusion_matrix.{ext}')
    plt.close(fig)

    validation = sorted(metrics['validation_experiments'], key=lambda x: -x['validation']['f1_macro'])
    fig, ax = plt.subplots(figsize=(12, 9), layout='constrained')
    values = [r['validation']['f1_macro'] for r in validation]
    ax.barh(range(len(validation)), values, color=['#007f73' if r['model'] == metrics['selected_model'] else '#7e9db4' for r in validation])
    ax.set(yticks=range(len(validation)), yticklabels=[r['model'] for r in validation],
           xlabel='Validation macro F1 (108 clauses, 6 abnormal)', xlim=(0, 1),
           title='Model selection used validation only; no test ranking')
    ax.invert_yaxis()
    ax.tick_params(axis='y', labelsize=8)
    for i, value in enumerate(values):
        ax.text(value+.01, i, f'{value:.3f}', va='center', fontsize=8)
    for ext in ['png', 'svg']:
        fig.savefig(figures / f'validation_comparison.{ext}')
    plt.close(fig)

    counts = {name: Counter(r['label'] for r in splits if r['split'] == name)
              for name in ['train', 'validation', 'test']}
    fig, ax = plt.subplots(figsize=(7, 4.5), layout='constrained')
    normal = [v['normal'] for v in counts.values()]
    abnormal = [v['abnormal'] for v in counts.values()]
    ax.bar(list(counts), normal, label='normal', color='#7e9db4')
    ax.bar(list(counts), abnormal, bottom=normal, label='abnormal', color='#bb4a43')
    for i, (n, a) in enumerate(zip(normal, abnormal)):
        ax.text(i, n/2, str(n), ha='center')
        ax.text(i, n+a+3, f'{a} abnormal', ha='center')
    ax.set(ylabel='Clauses', title='Frozen splits: document / template / near-duplicate groups')
    ax.set_ylim(0, 360)
    ax.legend()
    for ext in ['png', 'svg']:
        fig.savefig(figures / f'split_distribution.{ext}')
    plt.close(fig)

    table = []
    for row in validation:
        score = row['validation']
        minority = score['classification_report']['abnormal']
        table.append({'model': row['model'], 'validation_accuracy': score['accuracy'],
                      'validation_macro_f1': score['f1_macro'],
                      'validation_abnormal_precision': minority['precision'],
                      'validation_abnormal_recall': minority['recall'],
                      'validation_abnormal_f1': minority['f1-score']})
    write_csv(RUN / 'validation_comparison.csv', table)

    # Review annotations are explanatory metadata, never input features.
    detailed = [{**e, **{k: records[e['clause_id']][k] for k in
                ['document_id', 'risk_category', 'annotation_reason', 'risk_evidence', 'source_url']}}
                for e in errors]
    write_csv(RUN / 'error_analysis.csv', detailed)
    model = Predictor(RUN / 'model.joblib')
    classifier = model.pipeline.named_steps['classifier']
    vocabulary = model.pipeline.named_steps['features'].get_feature_names_out()
    coefficients = classifier.coef_[0]
    assert list(classifier.classes_) == ['abnormal', 'normal']
    order = np.argsort(coefficients)
    write_csv(RUN / 'linear_feature_associations.csv', [
        {'token': str(vocabulary[i]), 'coefficient_for_normal': float(coefficients[i]),
         'association': direction}
        for indices, direction in [(order[:20], 'abnormal'), (order[-20:][::-1], 'normal')]
        for i in indices])

    # Reuse known held-out cases for an inference smoke check; not new evaluation data.
    ids = [e['clause_id'] for e in errors[:2]]
    ids.append(next(r['clause_id'] for r in splits if r['split'] == 'test' and r['label'] == 'normal'))
    inputs = [records[i]['text'] for i in ids]
    write_json(RUN / 'offline_inference_inputs.json', inputs)
    write_json(RUN / 'offline_inference_input_manifest.json', {
        'purpose': 'smoke_check_reusing_existing_test_cases_not_new_quality_estimate',
        'clause_ids': ids, 'dataset_sha256': sha256(dataset)})
    predictions = model.predict(inputs)
    saved_predictions = {r['clause_id']: r['predicted_label'] for r in read_rows(RUN / 'test_predictions.csv')}
    assert [p['label'] for p in predictions] == [saved_predictions[i] for i in ids]
    write_json(RUN / 'offline_inference.json', predictions)

    comparisons = '\n'.join(f"| {r['model']} | {r['validation_macro_f1']:.4f} | {r['validation_abnormal_recall']:.4f} |" for r in table)
    error_sections = '\n\n'.join(
        f"### {r['clause_id']}\n\nNguồn: [{r['document_id']}]({r['source_url']}). Mã dấu hiệu: `{r['risk_category']}`. "
        f"Nhãn đã duyệt abnormal, dự đoán normal.\n\nBằng chứng nguyên văn: {r['risk_evidence']}\n\nLý do đã có trước huấn luyện: {r['annotation_reason']}"
        for r in detailed)
    report = f'''# MVP 1B — thực nghiệm thuê nhà v1

Ngày chạy: 09/11/2026. **MVP 1A được người dùng duyệt; thực nghiệm học máy truyền thống đã chạy, nhưng khả năng phát hiện abnormal chưa đạt. Chưa hoàn thành toàn bộ MVP 1, chưa sang MVP 2.**

## Dữ liệu và quyền thực nghiệm

Người dùng xác nhận đúng câu “Dataset thuê nhà Đạt”. [Hồ sơ duyệt](rental_dataset_approval.json) ghi actor `user_in_chat`; không suy ra tên thật hoặc đánh giá nhãn độc lập của chuyên gia. [Bản được duyệt](../data/rental_approved_v1/clauses.csv) có 517 mẫu, 489 normal/28 abnormal (5,42%), 17 tài liệu nguồn. Giữ nguyên nội dung/nhãn của bản đã trình, chỉ cập nhật trạng thái kiểm duyệt trong snapshot riêng; bản draft và 752 mẫu legacy được bảo toàn.

SHA256 dataset: `{sha256(dataset)}`. Tiêu chí thuê nhà, nhãn, raw/pages và proof scan SADECO được kiểm tra trước train. Duyệt cho thực nghiệm cục bộ không đồng nghĩa được phép phân phối lại tài liệu nguồn.

## Thiết kế đã chốt trước fit

Train 315 (299 normal,16 abnormal); validation 108 (102,6); test 94 (88,6). Chia theo nhóm tài liệu/họ mẫu/gần trùng, tổng 17 nhóm; không có nhóm đi qua hai tập. Seed mô hình 42, seed chia chọn được 128. Thuật toán cân bằng duyệt 128 seed × các cặp fold bằng số lượng/nhãn/nhóm, không dùng dự đoán hoặc điểm mô hình. Mỗi held-out có tối thiểu 5 abnormal từ ít nhất 2 nhóm. Đây không phải chia ngẫu nhiên độc lập từng điều khoản.

[Precommit](../outputs/rental_mvp1b_v1/precommit.json) và [splits](../outputs/rental_mvp1b_v1/splits.csv) được ghi trước fit: hash dữ liệu/split/code, tham số và cấu hình. 23 ứng viên gồm Dummy và 22 cấu hình BoW/TF-IDF, unigram/bigram, NB/LR/SVM, tham số C/alpha, giữ hoa, stopword hạn chế, ghép từ bằng từ điển hạn chế và word+char. Vectorizer chỉ học trên train ở vòng chọn. Không dùng pretrained hoặc API AI, không đưa lý do/nhãn phụ/nguồn/ID vào features.

Chuẩn hóa Unicode/whitespace, lowercase theo cấu hình; bảo toàn phủ định, con số. Unigram/bigram thông thường là n-gram âm tiết; biến thể từ điển chỉ nối một số cụm định trước, không phải bộ tách từ tiếng Việt tổng quát. Không tuyên bố đã so sánh underthesea/PyVi. Không có oversampling hoặc dữ liệu sinh giả.

Chọn bằng macro F1 validation, ghi [validation_selection](../outputs/rental_mvp1b_v1/validation_selection.json) trước test. Sau đó refit duy nhất ứng viên thắng trên train+validation; đánh giá test một lần cùng Dummy đối chứng. Không thử các mô hình còn lại trên test, không sửa nhãn/chia lại theo kết quả.

## Kết quả thực đo

Ứng viên thắng: **{metrics['selected_model']}**, class_weight balanced, C=1; macro F1 validation 0,7605, Recall abnormal 0,50 (3/6). Kết quả test:

| Chỉ số | Giá trị |
|---|---:|
| Accuracy | {metrics['test']['accuracy']:.6f} |
| Precision macro | {metrics['test']['precision_macro']:.6f} |
| Recall macro | {metrics['test']['recall_macro']:.6f} |
| F1 macro | {metrics['test']['f1_macro']:.6f} |
| Precision abnormal | 0 |
| Recall abnormal | 0/6 = 0 |
| F1 abnormal | 0 |

Confusion matrix, thứ tự normal/abnormal: `[[88, 0], [6, 0]]`. Dự đoán toàn bộ test là normal, cùng kết quả với Dummy. **Accuracy 93,62% không chứng minh cảnh báo hữu ích.** Không mẫu test nào có vector toàn 0; các lỗi không phải do inference từ chối hết từ lạ. Lưu/nạp model cho dự đoán giống hệt, nhưng đúng kỹ thuật không có nghĩa đúng nghiệp vụ.

![Confusion matrix](../outputs/rental_mvp1b_v1/figures/confusion_matrix.png)

## So sánh validation, không phải test

| Ứng viên | Macro F1 validation | Recall abnormal validation |
|---|---:|---:|
{comparisons}

![Validation](../outputs/rental_mvp1b_v1/figures/validation_comparison.png)

Có một `ConvergenceWarning` của Liblinear trong vòng fit ứng viên SVM. Lần chạy v1 không ghi riêng warning theo tên ứng viên, vì vậy chưa xác định ứng viên phát cảnh báo; không tuyên bố tất cả SVM hội tụ. Mô hình được chọn là Logistic Regression. Giữ nguyên kết quả v1, không tăng số vòng lặp rồi chọn lại theo test đã xem. Thời gian trong metrics là thời gian trên máy hiện tại, không phải benchmark phần cứng chuẩn.

## Phân tích sáu false negative

Sáu lỗi đến từ 3 nguồn: Cô Chinh (1), mẫu song ngữ Đà Nẵng (1), Roomi (4). Chứa sửa chữa/trách nhiệm không phân định, thu hồi kèm mất cọc, miễn trách nhiệm, mở khóa/di dời tài sản, và chấm dứt khi bị phản ánh ồn. Giữ nguyên toàn bộ nhãn đã duyệt. Mô hình tuyến tính với token không bảo đảm hiểu chủ thể, ngoại lệ và quan hệ giữa căn cứ/hậu quả; ở bộ này điểm validation không chuyển được sang các nguồn test. Đây là nhận định từ quan sát lỗi, chưa là thí nghiệm xác định nguyên nhân.

{error_sections}

`error_analysis.csv` giữ text đầy đủ, nguồn, lý do cũ và dự đoán. `linear_feature_associations.csv` chỉ là trọng số liên hệ từ của mô hình, không là lời giải thích pháp lý hoặc bằng chứng nhân quả. Abnormal chỉ có 28 mẫu tổng, 16 trong train và 6 trong từng held-out: một mẫu thay đổi Recall held-out 16,67 điểm phần trăm. Thiếu cả ba nhóm deemed_consent, automatic_renewal, overbroad_data_use; không có số đo cho các nhóm vắng mặt. Nhiều nguồn là mẫu công khai, chưa đại diện cho hợp đồng thực tế hay mọi phân khúc.

## Model và inference offline

[Model](../outputs/rental_mvp1b_v1/model.joblib), metadata cùng tên, SHA256 kiểm tra khi nạp; `purpose=official` chỉ là thực nghiệm trên dataset được duyệt, **không phải chứng nhận chất lượng**. Không nạp joblib không tin cậy. CLI và `predict.py` nhận text đầy đủ ngữ cảnh hoặc JSON mảng chuỗi, không tự đọc PDF/tách khoản. Trả normal/abnormal; vector không có feature quen thuộc thì trả needs_review. Confidence null vì chưa hiệu chỉnh xác suất. Nhãn normal không chứng minh điều khoản an toàn.

`offline_inference_inputs.json`, manifest và output minh họa lại ba mẫu test có thật để kiểm tra đường nạp/inference; không gọi đây là tập mới hoặc đánh giá chất lượng độc lập. Không đưa nội dung nguồn lên dịch vụ AI. Biểu đồ có PNG và SVG trong thư mục figures.

## Phần tiếp theo trong MVP 1

Giữ bản v1 làm baseline thất bại có thể kiểm chứng. Ưu tiên tìm thêm điều khoản bất lợi thật, khác nguồn/họ, bổ sung nhóm còn thiếu và cặp dễ nhầm có đủ ngoại lệ; không nhân bản để tăng số lượng. Agent phụ trách trích/nhãn/giải thích, người dùng chỉ duyệt phiên bản mới. Không tự coi phê duyệt v1 là phê duyệt dữ liệu chưa có.

Thực nghiệm tiếp theo phải khai báo trước cách chọn theo train/validation, capture warning từng ứng viên và kiểm tra hội tụ. Test v1 đã xem chỉ dùng phân tích hồi cứu, không còn làm test cuối cho chuỗi tối ưu tiếp theo; cần nguồn test mới chưa dùng lựa chọn khi báo chất lượng phiên bản mới. Chưa chọn ngưỡng/cấu hình theo sáu lỗi này rồi báo test độc lập.

CNN/BiLSTM từ đầu theo master prompt chưa triển khai/huấn luyện. Mốc prompt đặt sau baseline truyền thống ổn định; hiện baseline chưa đạt mục tiêu, dữ liệu train chỉ có 16 abnormal, không có căn cứ hứa deep learning sẽ sửa được. Chưa có metrics DL, chưa hoàn tất yêu cầu này. Chủ đề clause_type tiếp tục là metadata phân tích, không thay nhãn đích rủi ro. Không làm backend, giao diện, truy hồi hay quản lý hợp đồng; chỉ chuyển MVP 2 sau khi người dùng xác nhận MVP 1 đạt và cho phép.
'''
    (ROOT / 'reports/MVP1B_EXPERIMENT_REPORT.md').write_text(report, encoding='utf-8')
    write_json(RUN / 'analysis_manifest.json', {
        'analysis_only_no_fit': True, 'dataset_sha256': sha256(dataset),
        'metrics_sha256': sha256(RUN / 'metrics.json'),
        'model_sha256': sha256(RUN / 'model.joblib'),
        'error_source_counts': dict(Counter(r['document_id'] for r in detailed)),
        'smoke_predictions_match_existing_test': True,
        'quality_gate_passed': False, 'mvp1_completed': False, 'mvp2_authorized': False})
    print('Read-only model analysis, figures and report completed; no fitting performed.')


if __name__ == '__main__':
    main()
