# Hồ sơ lịch sử đã ngừng sử dụng

`topic_workflow/` giữ nguyên nội dung của các script phân loại chủ đề, bản xuất review và Excel cũ. Chúng không phải pipeline hay dataset normal/abnormal. Không chạy lại script trong archive: đường dẫn và giả định của chúng thuộc cấu trúc cũ.

Đã chuyển vào đây để thư mục đang làm việc chỉ chứa các công cụ MVP 1 hiện hành. Không xóa hồ sơ lịch sử. Danh sách đường dẫn trước/sau ở `../reports/cleanup_manifest.json`.

`topic_workflow/tools/spreadsheet_runtime/node_modules` là junction có sẵn tới thư viện ngoài project; việc chuyển thư mục chỉ chuyển liên kết, không thay đổi dữ liệu tại đích. Không cần runtime này để chạy MVP 1.

CSV lịch sử `data/review/`, nguồn `data/raw/`, manifest nguồn và nhật ký `reports/repair_ledger.json` vẫn ở vị trí cũ để kiểm tra provenance. CSV chính duy nhất: `data/clauses.csv`.
