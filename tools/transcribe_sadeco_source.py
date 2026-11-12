"""Visually checked selected excerpts from the public scanned SADECO template.

No OCR/LLM API. These are source transcriptions, not newly authored clauses.
Pages 2--5 contain operative clauses; administrative blanks and the first-month
formula are outside this selected transcription. Page 6 was visually blank.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from contractguard.dataset import read_json,write_json,sha256

PAGES=[
'''HỢP ĐỒNG THUÊ PHÒNG LƯU TRÚ
TẠI TÒA NHÀ ... - KHU LƯU TRÚ CÔNG NHÂN KCX TÂN THUẬN
1. BÊN CHO THUÊ (BÊN A):
CÔNG TY CỔ PHẦN PHÁT TRIỂN NAM SÀI GÒN (SADECO)
2. BÊN THUÊ (BÊN B):''',
'''ĐIỀU 1. NỘI DUNG HỢP ĐỒNG
Bên A đồng ý cho Bên B thuê và Bên B đồng ý thuê phòng ... tại Tòa nhà ... – Khu lưu trú Công nhân KCX Tân Thuận (Lô X.01 – Lô X.06 KCX Tân Thuận, Bùi Văn Ba, phường Tân Thuận Đông, Quận 7) với các nội dung sau:
- Mục đích thuê: để Bên B ở.
- Số lượng người lưu trú: tối đa 04 người/phòng. Người lưu trú cùng Bên B phải đáp ứng điều kiện là công nhân đang làm việc và có ký Hợp đồng lao động với Công ty tại Khu Chế Xuất Tân Thuận hoặc có quan hệ gia đình với Bên B.
- Giá cho thuê chưa bao gồm tiền điện, nước và các chi phí phát sinh khác theo quy định Nhà nước.
- Đơn giá cho thuê phòng sẽ được điều chỉnh tăng theo tỷ lệ tối thiểu 4%/năm tính từ kể từ ngày 01/01/2024 đến hết ngày 30/12/2034 hoặc khi có Thông báo điều chỉnh giá của Bên A.
- Thời hạn thuê là 12 tháng từ ngày .../.../..... đến hết ngày .../.../......... Trước khi kết thúc thời hạn thuê ít nhất 30 ngày, nếu Bên B vẫn có nhu cầu thuê thì Bên B phải thông báo đề nghị gia hạn Hợp đồng cho Bên A. Hai bên sẽ thỏa thuận cụ thể về nội dung việc ký phụ lục gia hạn Hợp đồng hoặc Hợp đồng mới.
- Tiền điện - nước được tính theo đơn giá của Công ty Điện lực Tân Thuận và Công ty Cấp nước Nhà Bè căn cứ vào chỉ số tiêu thụ của từng phòng, định mức cá nhân cộng vào phụ thu (nếu có).
ĐIỀU 2. ĐẶT CỌC VÀ THANH TOÁN
2.1. Đặt cọc và thanh toán
a. Đặt cọc: Ngay sau khi ký hợp đồng này, Bên B thanh toán cho bên A số tiền đặt cọc: ...đồng (Bằng chữ:........), tương đương 02 tháng tiền thuê phòng. Sau khi hai bên hoàn tất thủ tục thanh lý Hợp đồng, trong vòng ....ngày làm việc, Bên A sẽ hoàn trả tiền đặt cọc cho bên B sau khi khấu trừ các khoản chi phí mà bên B phải thanh toán theo quy định tại Hợp đồng.''',
'''- Những tháng tiếp theo, Bên B có nghĩa vụ thanh toán tiền thuê phòng, tiền điện và tiền nước cho Bên A trước ngày 18 hàng tháng căn cứ theo phiếu báo và hóa đơn của Bên A.
2.2. Phương thức thanh toán.
Bên B thanh toán cho bên A bằng phương thức chuyển khoản theo thông tin tài khoản của Bên A ở phần đầu Hợp đồng này hoặc thông tin tài khoản khác khi bên A có yêu cầu bằng văn bản.
ĐIỀU 3. QUYỀN VÀ NGHĨA VỤ CỦA MỖI BÊN
3.1. Quyền và nghĩa vụ của Bên A
- Nhận đủ tiền thuê phòng theo đúng thời hạn đã thỏa thuận tại Hợp đồng.
- Kiểm tra phòng định kỳ 01 lần/tháng và trường hợp đột xuất (nếu có).
- Yêu cầu Bên B sửa chữa và bồi thường thiệt hại các hư hỏng tại phòng thuê (bao gồm cả việc sơn sửa phòng lưu trú), hư hỏng các vật dụng trang thiết bị do lỗi của Bên B/người lưu trú cùng bên B gây ra.
- Được quyền tạm ngưng cung cấp điện, nước tại Phòng thuê nếu Bên B chậm thanh toán tiền thuê, tiền điện, nước quá 03 ngày kể từ ngày đến hạn thanh toán theo thỏa thuận.
- Thông báo và phối hợp với Bên B xử lý các trường hợp người sử dụng phòng của Bên B có các hành vi vi phạm Nội quy, Quy chế của Khu lưu trú.
- Giao phòng cho Bên B theo đúng thỏa thuận tại Điều 1.
- Gửi hoá đơn tiền thuê phòng, tiền điện, tiền nước cho Bên B trước ngày 12 dương lịch mỗi tháng.
- Đăng ký tạm trú cho người lưu trú với cơ quan có thẩm quyền.
- Bảo đảm Bên B được sử dụng ổn định phòng thuê trong thời hạn cho thuê.
- Sửa chữa những hư hỏng trong phòng lưu trú liên quan đến chất lượng xây dựng phòng lưu trú mà không do lỗi của Bên B hoặc người lưu trú cùng bên B.
3.2. Quyền và nghĩa vụ của Bên B:
- Thay đổi người lưu trú nhưng phải thông báo bằng văn bản cho Bên A trước 02 ngày làm việc.
- Được ưu tiên ký tiếp hợp đồng thuê khi hết hạn hợp đồng.
- Đơn phương chấm dứt hợp đồng thuê phòng trước hạn theo quy định tại Điều 4 Hợp đồng này.
- Sử dụng phòng thuê đúng theo mục đích, đối tượng đã thỏa thuận tại Hợp đồng này.
- Thanh toán đúng thời hạn các khoản tiền phải trả theo Hợp đồng.''',
'''- Cung cấp cho Bên A danh sách và các giấy tờ cần thiết liên quan đến người lưu trú.
- Bảo quản các trang thiết bị tại phòng thuê theo đúng hiện trạng bàn giao ban đầu. Trường hợp bị hư hỏng thì phải sửa chữa nếu các hư hỏng trong phòng thuê do lỗi của Bên B/người lưu trú cùng Bên B gây ra trên cơ sở giấy báo của Bên A gồm: các trang thiết bị điện, nước (cấp nước, thoát nước) bị hư hỏng. Quá thời gian trên, Bên A có quyền thuê một bên thứ ba thực hiện các công việc này và toàn bộ chi phí cho việc sửa chữa (có bao gồm công thợ) để chi trả cho bên thứ ba sẽ do Bên B chịu, Bên A sẽ thông báo cho Bên B giá trị trên, Bên B buộc phải chấp thuận giá trị trên và tiến hành thanh toán cho Bên A trong thời hạn 03 ngày kể từ ngày nhận được thông báo của Bên A.
- Khi Bên B không còn nhu cầu thuê phòng thì phải báo trước 30 ngày cho Bên A, trường hợp Bên B không báo trước hoặc thời gian báo trước không đủ theo quy định thì Bên B phải chịu tiền thuê phòng cho thời gian không báo trước. Trong thời hạn 02 (hai) ngày làm việc kể từ ngày nhận được thông báo của Bên B, Bên A sẽ đi kiểm tra phòng xác định hiện trạng và thông báo cho Bên B các công việc cần thực hiện để hoàn trả nguyên trạng phòng như thời điểm Bên A bàn giao cho Bên B (loại trừ công tác sơn lại phòng nếu Bên B tái ký hợp đồng liên tục tối thiểu 3 năm). Bên B có trách nhiệm hoàn tất công tác sửa chữa trong vòng 07 (bảy) ngày kể từ ngày đăng ký trả phòng để đủ điều kiện tiến hành thanh lý. Quá thời gian trên, Bên A có quyền thuê một bên thứ ba thực hiện các công việc này và toàn bộ chi phí cho việc sửa chữa sẽ do Bên B chịu và chi phí này được khấu trừ vào tiền đặt cọc của Bên B. Sau khi khấu trừ tiền đặt cọc mà vẫn không đủ chi trả chi phí sửa chữa cho bên thứ ba thì Bên B có trách nhiệm thanh toán khoản tiền còn lại cho Bên A trước khi thực hiện thanh lý Hợp đồng. Trong thời gian chưa hoàn tất thủ tục thanh lý do lỗi của Bên B thì Bên B vẫn phải thực hiện nghĩa vụ đóng tiền thuê phòng cho Bên A theo đúng thỏa thuận Hợp đồng.
- Thanh toán các khoản chi phí bồi thường do người lưu trú cùng Bên B vi phạm Nội quy, Quy chế phòng ở trên cơ sở giấy báo của Bên A.
- Người lưu trú cùng Bên B phải chấp hành nội quy sinh hoạt của Khu lưu trú.
- Giữ gìn vệ sinh trong và ngoài khuôn viên của phòng lưu trú.
- Bên B/người lưu trú cùng Bên B phải chấp hành mọi quy định của pháp luật, quy định của địa phương và Nội quy Khu lưu trú do bên A quy định.
- Nếu Bên B/người lưu trú cùng Bên B cho khách ở qua đêm thì phải thông báo và được sự đồng ý của Ban quản lý Khu lưu trú. Đồng thời phải chịu trách nhiệm về dân sự về các hành vi vi phạm pháp luật, Nội quy Khu lưu trú của khách (nếu có) trong thời gian ở lại.
- Giao trả phòng thuê theo đúng thời hạn thỏa thuận và hiện trạng bàn giao.
ĐIỀU 4. ĐƠN PHƯƠNG CHẤM DỨT HỢP ĐỒNG
4.1. Quyền đơn phương chấm dứt Hợp đồng của Bên A
Bên A được quyền đơn phương chấm dứt Hợp đồng trong các trường hợp sau:
- Bên B không thanh toán tiền thuê theo đúng thời hạn thỏa thuận từ 01 tháng trở lên mà''',
'''không có lý do chính đáng được Bên A chấp thuận.
- Bên B sử dụng phòng thuê không đúng mục đích, không đúng đối tượng theo thỏa thuận Hợp đồng.
- Bên B tự ý đục phá, cơi nới, cải tạo, phá dỡ phòng thuê.
- Bên B chuyển đổi, cho mượn, cho thuê lại phòng thuê mà không được sự đồng ý của Bên A.
- Bên B/Người lưu trú cùng Bên B thường xuyên làm mất trật tự, vệ sinh môi trường, ảnh hưởng nghiêm trọng đến sinh hoạt của những người lưu trú xung quanh đã được bên Ban Quản lý Khu lưu trú lập biên bản đến lần thứ ba mà vẫn không khắc phục.
- Phòng thuê bị xuống cấp phải thu hồi để sửa chữa.
Bên A có trách nhiệm thông báo cho Bên B biết về việc đơn phương chấm dứt Hợp đồng trước 30 ngày.
4.2. Quyền đơn phương chấm dứt Hợp đồng của Bên B
Bên B được quyền đơn phương chấm dứt Hợp đồng trong các trường hợp sau:
- Bên A không sửa chữa phòng thuê khi có hư hỏng, xuống cấp nặng mặc dù đã được Bên B kiến nghị bằng văn bản.
- Tăng giá cho thuê bất hợp lý, không đúng với thỏa thuận tại Hợp đồng.
Bên B có trách nhiệm thông báo cho Bên A biết về việc đơn phương chấm dứt Hợp đồng trước 30 ngày.
ĐIỀU 5. ĐIỀU KHOẢN THI HÀNH
- Hai bên cam kết thực hiện đúng và đầy đủ các điều khoản đã ghi trong hợp đồng. Mọi sự thay đổi đều phải được sự đồng ý bằng văn bản của hai Bên.
- Trong trường hợp có sự điều chỉnh lại giá cho thuê thì Bên A phải báo cho Bên B trước một tháng bằng văn bản và hai Bên phải ký phụ lục điều chỉnh hoặc ký Hợp đồng mới.
- Trong quá trình thực hiện hợp đồng, nếu có vướng mắc hai Bên cùng nhau bàn bạc giải quyết trên tinh thần tôn trọng lợi ích lẫn nhau, nếu không tự giải quyết được thì có quyền yêu cầu Toà án nhân dân có thẩm quyền giải quyết theo quy định của pháp luật.
- Hợp đồng có hiệu lực kể từ ngày ký, được lập thành 04 (bốn) bản có giá trị như nhau, mỗi Bên giữ 02 (hai) bản để thực hiện.''',
''
]

def main():
    folder=ROOT/'data/rental_mvp1a_v1/raw/sadeco_worker_individual_pdf'
    source=read_json(folder/'source.json')
    target=folder/'pages_visual_selected_v1.json'
    if target.exists():raise ValueError('Preserve existing transcription version before editing')
    write_json(target,PAGES)
    images=ROOT/'reports/rental_source_quality/sadeco'
    write_json(folder/'visual_transcription_v1.json',dict(
        source_sha256=source['source_sha256'],pages_path=target.relative_to(ROOT).as_posix(),
        pages_sha256=sha256(target),method='agent_visual_selected_transcription',
        full_page_transcription=False,automated_ocr_used=False,external_ai_api_used=False,
        omitted_content='Page 1 administrative contact/identity blanks; page 2 room/price blanks and first-month formula; page 3 formula continuation; signatures/page numbers. No omitted exception treated as absent.',
        page6='visually_blank',
        inspection_passes=2,
        rendered_pages=[dict(page=i,image_path=(images/f'page{i}.png').relative_to(ROOT).as_posix(),sha256=sha256(images/f'page{i}.png')) for i in range(1,7)],
        note='Selected operative excerpts were read against rendered scan. Span audit verifies against this transcription, not a text layer in the scanned PDF. This is source acquisition, not synthetic training data.'))
    print('Saved selected visual transcription for scan, six-page alignment retained.')

if __name__=='__main__':main()
