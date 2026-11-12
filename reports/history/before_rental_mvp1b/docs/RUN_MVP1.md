# Chạy kiểm tra và đọc dataset thuê nhà MVP 1A

Thư mục dự án: `D:\NLP\ContractGuard`. Dataset hiện cần xem là `data/clauses_rental_v1.csv`; không dùng các lệnh train hoặc readiness legacy để chứng nhận corpus thuê nhà.

## Đọc toàn bộ nhãn và nguồn cục bộ

```powershell
Set-Location D:\NLP\ContractGuard
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --label abnormal --count 30
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --clause-id roomi_registration_0052
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --start 0 --count 20
.venv\Scripts\python.exe -X utf8 tools/review_rental_dataset.py --start 20 --count 20
```

CSV mở trực tiếp được bằng Excel; lọc label, risk_category, clause_type, nguồn. Cả CSV và CLI đều cho đọc toàn bộ dữ liệu, không chỉ ví dụ. Không cần người dùng gán hoặc nhập nhãn thay agent. Có thể xác nhận “Dataset thuê nhà Đạt” hoặc “Chưa đạt” sau khi xem báo cáo `reports/MVP1A_REVIEW.md`. Tiêu chí đã được duyệt, không cần duyệt lại.

## Kiểm tra và tái đóng gói đúng snapshot

```powershell
.venv\Scripts\python.exe -X utf8 -m pip check
.venv\Scripts\python.exe -X utf8 -m pytest -q --junitxml=reports/rental-test-results.xml
.venv\Scripts\python.exe -X utf8 tools/package_rental_dataset.py
.venv\Scripts\python.exe -X utf8 tools/write_rental_handoff.py
```

Đóng gói chỉ đọc raw/candidates và quyết định nhãn ID tường minh, kiểm tra hash rồi viết lại CSV/audit. Không fetch, không huấn luyện, không đổi approval. Snapshot ứng viên thay đổi thì tool dừng để agent kiểm tra nhãn thay vì gán vào nhầm ID. Không chạy lại các script snapshot/migration một lần nếu chưa hiểu version history. `build_rental_candidates.py` phục vụ tạo phiên bản ứng viên mới; không được coi ID mới là đã có nhãn đúng.

## Môi trường thu thập tùy chọn

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -X utf8 -m pip install -r requirements-rental-collection-lock.txt
.venv\Scripts\python.exe -X utf8 -m pip install --no-build-isolation --no-deps -e .
```

`rental_corpus.py fetch --config configs/rental_collection_v9.json` tải URL công khai trong manifest nếu chưa có raw, cần quyền mạng thông thường của host. Không vô hiệu TLS hoặc bypass 403. `prepare-html`, `prepare-pdf` tạo text có phiên bản, không ghi đè raw. Công cụ dùng requests/BeautifulSoup, OOXML ZIP, pypdf/pdfplumber; không gọi API AI.

## Trước huấn luyện thật

`configs/rental_approval.json` vẫn dataset_approved=false/source_use_confirmed=false. `approved_by`/`approved_at`/hash bản được duyệt vẫn trống. CLI training cũ dùng profile tổng quát/legacy và chưa được phép dùng cho corpus mới. Sau quyết định duyệt thật, agent còn phải tích hợp gate đúng tiêu chí thuê nhà, chốt nhóm chia và support rủi ro, rồi mới sang MVP 1B. Chưa có model thật để chạy inference sản phẩm; kiểm thử save/load/toy không thay kết quả thực nghiệm.
