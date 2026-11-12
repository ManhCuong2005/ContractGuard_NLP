# MVP 1A — bản dữ liệu thuê nhà v1 để kiểm duyệt

**Hồ sơ lịch sử trước duyệt. Cập nhật 09/11/2026:** Người dùng đã xác nhận “Dataset thuê nhà Đạt”. Bản được duyệt riêng tại `data/rental_approved_v1/clauses.csv`; xem [trạng thái hiện hành](MVP1_STATUS.md) và [thực nghiệm MVP 1B](MVP1B_EXPERIMENT_REPORT.md). Các câu “chưa duyệt/chưa có metrics” phía dưới mô tả thời điểm trình bản gốc.

**Đã chuẩn bị một bản dữ liệu có nguồn và nhãn sơ bộ để kiểm duyệt; chưa đạt mong muốn abnormal nhiều và chưa hoàn thành toàn bộ MVP 1.** Không gọi bản này là bộ dữ liệu lớn, cân bằng hoặc bằng chứng mô hình nhận dạng tốt. Mục tiêu 1.500–3.000 trong master prompt là tham khảo khi có nguồn phù hợp; bản hiện tại có 517 đơn vị sau chọn và loại bản lặp.

## Bản cần xem

[data/clauses_rental_v1.csv](../data/clauses_rental_v1.csv) — 489 normal, **28 abnormal** (5.42%), 17 tài liệu nguồn, 19 mẫu hợp đồng, 19 họ mẫu, 17 nhóm theo nguồn/họ/gần trùng. Đây là nhãn **draft/pending**, chưa phải ground truth được người dùng duyệt. Không phải 19 hợp đồng đã được các bên ký thực tế: phần lớn là mẫu công khai chưa điền, một nguồn là hợp đồng lưu xá theo kỳ năm học.

Mỗi dòng có text đủ ngữ cảnh được chọn, nhãn nhị phân, chủ đề phụ, cơ chế rủi ro, lý do, bằng chứng, mức chắc chắn định tính, vai trò người thuê, nguồn/trang/spans và SHA256. Toàn bộ text trong CSV có thể đối chiếu về nguồn; giải thích/nhãn không được đưa vào đầu vào mô hình. CSV dùng UTF-8 BOM để mở trên Excel đúng tiếng Việt. Các dòng abnormal mức chắc chắn medium nằm trước, sau đó abnormal còn lại, các đối chứng dễ nhầm và phần còn lại. Người dùng không phải tự nhập nhãn.

Tiêu chí thuê nhà đã được người dùng duyệt: **“Tiêu chí thuê nhà Đạt”**; giữ nguyên bytes và SHA256 của `docs/LABELING_GUIDELINES.md`. Hồ sơ xác nhận ở [rental_criteria_approval.json](rental_criteria_approval.json). Đã phục hồi dấu tiếng Việt trong các câu trích chat bị lỗi encoding từ lượt trước, giữ bản trước sửa ở `reports/approval_encoding_history`; quyết định duyệt dataset vẫn false.

## Thu thập và chọn lọc

- Đã thử 72 địa chỉ mới, tải/lưu raw được 65, 7 không lấy được vì TLS/HTTP/DNS; không tắt kiểm tra chứng chỉ hoặc vượt hạn chế truy cập. Nguồn Chính phủ từ staging trước được tái sử dụng riêng, không tính thành lượt tải mới.
- 65 tài liệu tải được **không phải** 65 hợp đồng hợp lệ/độc lập: có trang tư vấn, chỉ mục tải, mẫu thương mại, bản chép và mẫu thiếu ngữ cảnh. Chỉ 17 nguồn đóng góp vào CSV này. [Nhật ký tải/chọn](../data/rental_mvp1a_v1/acquisition_ledger.json) ghi riêng từng mục.
- Pool kỹ thuật có 1411 ứng viên chưa phải dataset được duyệt. Có 523 quyết định nhãn tường minh, loại 6 bản lặp chính xác khỏi số mẫu chính; 18 đơn vị thật sự mơ hồ ở nguyên bản giữ nội bộ; 870 ứng viên dự trữ không được tự gán normal. Không tuyên bố đã đọc và gán nhãn toàn bộ pool.
- Các lỗi trích được sửa trước khi đưa vào CSV: tách chữ do inline HTML, đoạn lồng trong danh sách, dòng xuống trang PDF, tham chiếu “Điều 9.7” bị nhầm thành tiêu đề, “01 bản” bị tách thành khoản, và lẫn phần đầu mẫu kế bên trong tuyển tập. Bản trích trước sửa vẫn ở `extraction_history`. Những điều khoản hợp lệ chưa chọn vẫn còn nguyên, không bị xóa vì lỗi bộ trích.
- Đã đối chiếu ảnh PDF Sunshine trang 34, 45 và lưu xá trang 2 tại `reports/rental_source_quality`; nguồn 9.6 có dẫn chiếu 9.7 khác thường được giữ đúng, không tự sửa ý văn bản. Audit nguồn xác nhận tính truy vết, không chứng minh nhãn chính xác tuyệt đối.
- Sau yêu cầu “tiếp tục”, bổ sung nguồn thuê phòng lưu trú công nhân SADECO và hai mẫu phòng trọ thực sự khác. PDF SADECO không có lớp text; agent đã đọc ảnh cả sáu trang và chép/đối chiếu hai lượt các phần nguyên văn được chọn. Có 34 dòng từ bản trích scan này. `visual_transcription_v1.json` ghi phạm vi phần đã chép, phần hành chính/công thức tháng đầu không dùng và hash ảnh. **Spans của scan khớp bản chép đã kiểm tra bằng ảnh, không phải kiểm chứng độc lập bằng lớp text PDF.** Bản trước mở rộng 466 dòng/23 abnormal được giữ tại `data/rental_mvp1a_v1/dataset_history/before_worker_extension_466`.

## 752 dòng cũ được xử lý thế nào

Đã kiểm tra miền nguồn của cả **752** dòng. Không dòng nào có provenance hợp đồng thuê nhà ở. Vì vậy **0 dòng được trộn vào corpus thuê nhà chính**. Đã chọn lại **7** câu giải quyết tranh chấp hoàn toàn chung làm [legacy_auxiliary.csv](../data/rental_mvp1a_v1/legacy_auxiliary.csv), có nhãn sơ bộ và lý do, luôn `auxiliary_only` và nằm ngoài train/test thuê nhà chính. 745 dòng còn lại được giữ trong bộ cũ, không đổi tên miền hay thay từ “xe/dịch vụ” thành “nhà”. [Hồ sơ chọn toàn bộ 752 dòng](../data/rental_mvp1a_v1/legacy_selection_audit.json).

Bộ `data/clauses.csv`, approval tổng quát cũ và tiêu chí cũ không bị sửa. Quyền tạo tên CSV mới được người dùng cho phép trong yêu cầu lần này; chưa tự promote bản v1 thành corpus chính thức đã duyệt.

## Phân bố theo nguồn

| Nguồn | normal sơ bộ | abnormal sơ bộ |
|---|---:|---:|
| acc_room_actual | 11 | 1 |
| bandon_room | 22 | 6 |
| cenhomes_sunshine_longterm | 102 | 8 |
| chinhphu_residential_2024 | 32 | 0 |
| cochinh_room1_pdf | 4 | 1 |
| danang_bilingual_docx | 20 | 1 |
| homedy_room | 46 | 0 |
| iuoss_dorm_pdf | 19 | 2 |
| mauhopdong_house_public | 16 | 0 |
| minhkhue_house | 37 | 1 |
| replus_house | 9 | 0 |
| resident_apartment | 23 | 1 |
| resident_room_pdf | 43 | 0 |
| roomi_registration_template | 32 | 4 |
| sadeco_worker_individual_pdf | 31 | 3 |
| thuecanho123_apartment | 28 | 0 |
| troxanh_room_docx | 14 | 0 |

Abnormal hiện có ở 10 nguồn/10 nhóm độc lập theo quy tắc kiểm tra đang dùng. Các nguồn chép một mẫu như DOCX Đà Nẵng/Resident/Minh Khuê được giữ làm dự trữ và provenance, không coi là hàng chục nguồn rủi ro độc lập. Phát hiện gần trùng bằng word-trigram Jaccard >= 0,86 là kiểm tra phụ, không bảo đảm bắt mọi bản diễn đạt lại. Họ mẫu và cùng tài liệu luôn giữ chung nhóm.

## Độ đa dạng của abnormal

| Mã giải thích | Cơ chế | Số dòng có dấu hiệu |
|---|---|---:|
| access_interference | Tự vào phòng, niêm phong hoặc cản trở sử dụng | 6 |
| broad_liability | Trách nhiệm/bồi thường hoặc miễn trách nhiệm quá rộng | 14 |
| deposit_forfeiture | Mất cọc/tiền trả trước theo cơ chế bất lợi | 7 |
| repair_burden | Đẩy sửa chữa không phân định lỗi sang người thuê | 4 |
| termination_discretion | Thu hồi/chấm dứt tùy nghi hoặc thiếu căn cứ/thủ tục | 5 |
| unilateral_change | Chủ nhà tự bổ sung nghĩa vụ/điều chỉnh phí | 2 |

Một dòng có thể có nhiều mã; tổng bảng này không bằng số abnormal. Đây là mã giải thích, **không phải các lớp chủ đề dùng thay nhãn rủi ro**.

**Còn thiếu nguồn abnormal đủ căn cứ cho `deemed_consent`, `automatic_renewal`, `overbroad_data_use`.** Ví dụ eNha chỉ có preview, thời hạn gia hạn trống và chưa có đủ toàn hợp đồng nên không ép thành abnormal. Câu thu thông tin để khai báo cư trú không bị coi là sử dụng dữ liệu quá rộng. Cơ chế bàn giao mặc nhiên Sunshine được đọc cùng quyền từ chối vì chất lượng; không gán chỉ theo từ khóa.

## Một số đối chứng đã rà

- `bandon_room_0043` abnormal: mọi hư hỏng sau 15 ngày do người thuê chịu. `roomi_registration_0052` normal: 100% chi phí chỉ khi sử dụng **sai cách**, kèm loại trừ hao mòn và chủ nhà sửa hỏng không do lỗi người thuê. Không gán theo từ “100%”.
- `iuoss_dorm_0016` abnormal: kiểm tra đột xuất không có giới hạn báo trước/khẩn cấp. `roomi_registration_0037` normal: định kỳ một lần/tháng, báo trước 24 giờ và có mục đích sửa chữa/an toàn.
- `sunshine_longterm_0117` abnormal mức chắc chắn medium: phí có thể điều chỉnh/bổ sung bằng thông báo, dù phải hợp lý/theo luật; thiếu cơ chế giới hạn cụ thể và từ chối. `homedy_student_0011` normal: căn cứ thay đổi khung giá Nhà nước, báo trước một tháng.
- `sunshine_longterm_0129` abnormal: căn hộ không sử dụng được do bất khả kháng thì không hoàn tiền đã trả, kèm cả nhánh ngoại lệ còn dùng được nhà và bảo hiểm để tránh cắt mất ngữ cảnh.
- `sadeco_worker_0014` abnormal: ngừng điện/nước để xử lý chậm thanh toán. `sadeco_worker_0004` về tăng giá được giữ nội bộ để làm rõ tương quan với Điều 5 yêu cầu hai bên ký phụ lục; không tự gán abnormal chỉ vì thấy “tối thiểu 4%”.
- `minhkhue_house_0012` normal: khấu trừ cọc theo thiệt hại và mức chi phí thống nhất bằng văn bản; khác với mất cọc/tiền còn lại với bất kỳ lý do nào ở Bandon.

Sunshine là thuê căn hộ dài hạn hình thành trong tương lai cho người nước ngoài, có phần chuyển sở hữu. Phần 10.3 không được dùng làm mẫu chính; các khoản thuê được giữ với subtype riêng. Đây không phải phòng trọ thông thường và đang chiếm 8/28 abnormal: cần xem xét cohort riêng ở thực nghiệm sau duyệt, không mặc định đại diện mọi loại thuê nhà.

## Chất lượng, giới hạn và bước kế tiếp

**Yêu cầu tăng mạnh số lượng abnormal chưa đạt.** 28 mẫu sơ bộ và sáu nhóm dấu hiệu là một tập khởi đầu có truy vết, chưa đủ để hứa hẹn mô hình tổng quát tốt. Bản hiện tại vẫn lệch lớp nặng, nhiều mẫu công khai có cùng cách viết, và thiếu ba cơ chế. Agent không tạo thêm câu giả, diễn đạt lại một câu thành nhiều mẫu hoặc ép nhãn để làm đẹp tỷ lệ.

Preflight kiểm tra được 10 nhóm có abnormal, nhưng chưa chốt train/validation/test và chưa fit BoW/TF-IDF hoặc predictor trên corpus này. Chỉ đủ số nhóm tối thiểu không có nghĩa validation/test đủ mẫu rủi ro. Chưa có Accuracy/Precision/Recall/F1/confusion matrix chính thức.

Việc tiếp theo để tăng chất lượng dữ liệu là thu thêm mẫu vận hành thuê nhà khác họ, có toàn bộ điều kiện cọc/hoàn tiền, phí, thông báo, quyền từ chối, nội quy đính kèm và mục đích dữ liệu. Ưu tiên abnormal mới và đối chứng cùng cơ chế; không ưu tiên thêm hàng trăm normal hoặc bản sao. Mục tiêu thu thập còn mở, không coi dữ liệu trong pool chưa đọc là đã giải quyết.

Nếu chấp nhận bản hiện tại cho một baseline thăm dò có giới hạn, người dùng chỉ cần xác nhận **“Dataset thuê nhà Đạt”**; nếu chưa chấp nhận, trả lời **“Chưa đạt”** và agent tiếp tục sửa/bổ sung, không yêu cầu người dùng nhập nhãn. Đây là bước kiểm duyệt thật bắt buộc ở mục 8 master prompt, không phải yêu cầu duyệt lại tiêu chí đã duyệt. Sau quyết định thật còn cần chốt nguồn sử dụng và profile gate thuê nhà trước MVP 1B. Không có huấn luyện chính thức trước quyết định này.

## Truy vết và tái lập

- Dataset SHA256: `8d37176383bda31d13dfd8e79ab1a0bc48006fe919810fffb3c7d97847080b28`.
- Source manifest SHA256: `9fa743f388a2f110e8d2f9c606ea0f8b3affea3e22353c633d96e2b6ffc85c76`.
- Tiêu chí: `68a1d9c068637c942e4c4c44648f299431960d64c01d1654652fc23f13c1a9fa`.
- [Audit kiểm tra kỹ thuật](rental_dataset_audit.json): 517 dòng khớp spans, raw/pages khớp hash, CSV round-trip UTF-8 BOM, input lịch sử giữ nguyên, gate vẫn đóng.
- [Snapshot duyệt](../data/rental_mvp1a_v1/review_snapshot.json), [quyết định nhãn](../data/rental_mvp1a_v1/annotation_decisions.json), [lineage bản lặp](../data/rental_mvp1a_v1/exact_duplicate_lineage.json), [schema](../docs/RENTAL_DATASET_SCHEMA.md).
- `tools/package_rental_dataset.py` chỉ đóng gói từ quyết định ID đã đọc, kiểm tra hash candidate cố định và tạo audit; không gán normal cho dòng không có quyết định. Các trường needs_context/reserve không vào CSV chính.
- Công cụ đọc toàn bộ CSV: `tools/review_rental_dataset.py`, có lọc nguồn, nhãn, mã rủi ro và clause_id. Hướng dẫn ở [RUN_MVP1.md](../docs/RUN_MVP1.md).
- Nguồn công khai không đồng nghĩa giấy phép tái phân phối mở. Raw được lưu để kiểm tra cục bộ; manifest không tự khẳng định quyền công bố lại toàn bộ văn bản. Chưa xuất bản corpus ra ngoài.

## Danh sách nguồn đóng góp

- [acc_room_actual](https://accgroup.vn/mau-hop-dong-thue-phong-tro) — raw SHA256 `c3058184b4e48a02ca7bdc713a9c15a554b0e33ba3e4eac0abb52e90a4775a85`; text nguồn `data/rental_mvp1a_v1/raw/acc_room_actual/pages_semantic_v2.json`.
- [bandon_room](https://www.bandon.vn/tin-tuc/mau-hop-dong-thue-phong-tro) — raw SHA256 `6d8c322be58f6cd09dffecbbf046e424cf41312a40479a500bd8970144a22648`; text nguồn `data/rental_mvp1a_v1/raw/bandon_room/pages_semantic_v2.json`.
- [cenhomes_sunshine_longterm](https://images.cenhomes.vn/2019/11/1573555056-hop-dong-cho-kh-nuoc-ngoai-thue-dai-han.pdf) — raw SHA256 `9e2f823f0516eb6c8040327ae76c5976e8d7c8b153014a1d28d495ccda780dd5`; text nguồn `data/rental_mvp1a_v1/raw/cenhomes_sunshine_longterm/pages_geometry.json`.
- [chinhphu_residential_2024](https://xaydungchinhsach.chinhphu.vn/mau-hop-dong-thue-nha-o-119240827172441217.htm) — raw SHA256 `e79d7ccd16f7befc2af659d409fbdc2c298e5db472559667a42b2f9e900a40f0`; text nguồn `data/rental_staging/raw/chinhphu_residential_2024/pages.json`.
- [cochinh_room1_pdf](https://cochinhquantritaichinh.vn/uploads/hopdong/pdf/mau1_hop_dong_thue_phong_tro_0553_H1VQkQ1n9cXrvg_103448.pdf) — raw SHA256 `d61157549ac6e1dbff8d3173ab2fbc13a217f2c57d8881364fcfa04992c66d54`; text nguồn `data/rental_mvp1a_v1/raw/cochinh_room1_pdf/pages_geometry.json`.
- [danang_bilingual_docx](https://houserentaldanang.com/wp-content/uploads/2018/12/Hop_dong_thue_nha_song_ngu.docx) — raw SHA256 `5f271b848cf01af08ea828f097a81bef2e022850494eacd082b14b9f5ad8fe07`; text nguồn `data/rental_mvp1a_v1/raw/danang_bilingual_docx/pages.json`.
- [homedy_room](https://homedy.com/news/mau-hop-dong-cho-thue-phong-tro-chuan-nhat-moi-duoc-cap-nhat-ne5129) — raw SHA256 `0c11506cd7e558a4ad76431ef7544e9483b999219be9e41df8be346c6277b265`; text nguồn `data/rental_mvp1a_v1/raw/homedy_room/pages_semantic_v2.json`.
- [iuoss_dorm_pdf](https://www.iuoss.com/wp-content/uploads/2016/08/%C4%90HQT_H%C4%90-Luu-xa-Phan-Liem.pdf) — raw SHA256 `422bcb1c928a9b12f5fc75a788744f112ed3c01715fc96cbfee870f01bf32295`; text nguồn `data/rental_mvp1a_v1/raw/iuoss_dorm_pdf/pages_geometry.json`.
- [mauhopdong_house_public](https://mauhopdong.vn/hop-dong-thue-nha-1) — raw SHA256 `af7cc8aa10f4cb2017fd42d3e5c235e6373ddeb2bd0355bde1a9ad0cfc17c708`; text nguồn `data/rental_mvp1a_v1/raw/mauhopdong_house_public/pages_semantic_v2.json`.
- [minhkhue_house](https://luatminhkhue.vn/mau-hop-dong-thue-nha.aspx) — raw SHA256 `b7a3e535bd81ef9386985652429e36c6de10e2a3a421887a4a8fe07fb35a232d`; text nguồn `data/rental_mvp1a_v1/raw/minhkhue_house/pages_semantic_v2.json`.
- [replus_house](https://replus.com.vn/mau-hop-dong-thue-nha/) — raw SHA256 `a39e2747cd51c391fb1a3a424b41dde0fed593485a8c69ae9a1a83d869234921`; text nguồn `data/rental_mvp1a_v1/raw/replus_house/pages_semantic_v2.json`.
- [resident_apartment](https://resident.vn/wp-content/uploads/2024/06/mau-hop-dong-thue-nha-chung-cu.pdf) — raw SHA256 `6cb34bd897ab0375c1f2591c0310923b4b5a7200fbab11927084fbfbca788ac5`; text nguồn `data/rental_mvp1a_v1/raw/resident_apartment/pages_geometry.json`.
- [resident_room_pdf](https://resident.vn/wp-content/uploads/2024/06/mau-hop-dong-thue-nha-tro.pdf) — raw SHA256 `a5cf36819838386b654c56e13792df4841eb7bd85bfbdd1e8378ca1a2f8203dd`; text nguồn `data/rental_mvp1a_v1/raw/resident_room_pdf/pages_geometry.json`.
- [roomi_registration_template](https://roomi.aom.vn/blog/mau-hop-dong-thue-phong-tro-dang-ky-tam-tru-2027) — raw SHA256 `c6960660d0bbf15722820ecf9f0d82f29c6903d300cf6bd70b617536af862a9f`; text nguồn `data/rental_mvp1a_v1/raw/roomi_registration_template/pages_semantic_v2.json`.
- [sadeco_worker_individual_pdf](https://www.sadeco.com.vn/Data/Sites/1/media/du-an/khu-luu-tru-cong-nhan-2023/hop-dong-thue-phong-luu-tru---mau-ca-nhan.pdf) — raw SHA256 `caa5aac843afe894974acdbf9ab6805ba41a31dcfd8880af7187d16e35ac2a11`; text nguồn `data/rental_mvp1a_v1/raw/sadeco_worker_individual_pdf/pages_visual_selected_v1.json`.
- [thuecanho123_apartment](https://thuecanho123.com/hop-dong-cho-thue-can-ho-chung-cu-day-du-don-gian-post6.html) — raw SHA256 `e3a15e3bf9b0d54afb98b89187261159bb45125aaf647e93447724f23d3b7c12`; text nguồn `data/rental_mvp1a_v1/raw/thuecanho123_apartment/pages_semantic_v2.json`.
- [troxanh_room_docx](https://www.troxanh.com/wp-content/themes/qlnt-web/assets/mau-bieu/hop-dong-thue-phong-tro.docx) — raw SHA256 `f6f36f370cca9ac1962f4eeef2af0cd81ed5e3c8750d08d7383b75aff05d4976`; text nguồn `data/rental_mvp1a_v1/raw/troxanh_room_docx/pages.json`.
