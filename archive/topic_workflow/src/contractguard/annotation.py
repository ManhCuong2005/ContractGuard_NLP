"""Historical topic annotation, now auxiliary clause_type only, NOT risk labels.

Rules read the operative clause and its section, with explicit agent corrections.
Do not use these eight topics as the target for anomaly/risk detection.
Ambiguity is exposed as an exclusion proposal, never hidden in the `other` class.
"""
import re
from .text import normalize

ANNOTATION_FIELDS = ['annotation_status', 'annotation_by', 'annotation_method',
                     'annotation_reason', 'proposed_action', 'annotation_flags',
                     'duplicate_of', 'original_text', 'text_preparation']

LABEL_NAMES = {'payment':'Thanh toán', 'termination':'Chấm dứt / tạm dừng',
               'liability':'Trách nhiệm / phạt / bồi thường', 'confidentiality':'Bảo mật',
               'dispute':'Tranh chấp', 'force_majeure':'Bất khả kháng',
               'duration':'Hiệu lực / thời hạn', 'other':'Khác'}

REASONS = {
    'payment':'Quy định khoản tiền, giá/phí hoặc cách thức/thời điểm thanh toán.',
    'termination':'Quy định điều kiện, quyền, thủ tục hoặc hậu quả của tạm dừng/chấm dứt.',
    'liability':'Quy định phạt, bồi thường hoặc giới hạn/miễn trách nhiệm khi xảy ra thiệt hại.',
    'confidentiality':'Quy định bảo vệ, thu thập, sử dụng, chia sẻ thông tin hoặc dữ liệu cá nhân.',
    'dispute':'Quy định khiếu nại, thương lượng hoặc cơ quan/thủ tục giải quyết tranh chấp.',
    'force_majeure':'Quy định sự kiện bất khả kháng, thông báo hoặc xử lý hậu quả của sự kiện.',
    'duration':'Quy định hiệu lực, thời hạn hoặc gia hạn của hợp đồng/văn bản.',
    'other':'Quy định đối tượng, định nghĩa, cung cấp dịch vụ hoặc nghĩa vụ vận hành ngoài 7 nhóm chuyên biệt.',
}


def has(text, pattern):
    return re.search(pattern, text) is not None


def prepare_text(text):
    """Remove only a trailing extracted header/signature, retaining verbatim prefix."""
    cuts = []
    metadata = re.search(r'Người tải:.*?Trang số:\s*\d+/\d+', text)
    if metadata and not text[metadata.end():].strip():
        text = text[:metadata.start()].rstrip()
    for pattern in [r'ĐẠI DIỆN BÊN', r'ĐẠI DIỆN ĐẠI LÝ', r'PHỤ LỤC\s+0?\d',
                    r'ĐIỂU \d+:', r'ĐIỀU \d+[:.]', r'CỘNG HO[ÀA] XÃ HỘI',
                    r'Các tin khác', r'Tin liên quan', r'File đính kèm',
                    r'\d+[./]\d+[./]\d+[./]?[-–]BM/']:
        match = re.search(pattern, text)
        if match and match.start() > 20:
            cuts.append(match.start())
    if cuts:
        return text[:min(cuts)].rstrip(), 'Cắt phần tiêu đề/chữ ký/phụ lục dính ở cuối; giữ nguyên văn phần trước.'
    return text, ('Bỏ khối thông tin người tải/mã hiệu dính ở cuối trang, giữ nguyên văn nội dung trước đó.' if metadata and not text[metadata.end():].strip() else '')


def classify(text, heading):
    """Return a proposed label and reason, or no label with an exclusion reason."""
    t, h = normalize(text), normalize(heading)
    if not t or not any(c.isalpha() for c in t):
        return '', 'Không có nội dung ngôn ngữ đủ nghĩa.'
    if has(t, r'^(bên sử dụng dịch vụ:|bên cung cấp dịch vụ:|thông tin tàu cá|thông tin về chủ tàu|thông tin về thuyền trưởng|đặc điểm .*tàu cá|đặc điểm chung của tàu cá|thiết bị giám sát và thông tin liên lạc|nội dung đăng ký sử dụng:)'):
        return '', 'Đây là biểu mẫu/khối thông tin định danh hoặc bảng đăng ký, không phải điều khoản hoàn chỉnh.'
    if has(t, r'^(thông tin trung tâm|thông tin về người quản lý tên miền|hỗ trợ kỹ thuật:|địa chỉ lắp đặt|chi phí khởi tạo dịch vụ stt)') or has(t, r'(?i)(bên sử dụng dịch vụ \(bên a\): người đại diện|stt khoản mục|tổng giá dịch vụ tại thời điểm ký kết:.*[…\.]{4})'):
        return '', 'Khối biểu mẫu/bảng đăng ký hoặc thông tin liên hệ, không phải khoản văn xuôi độc lập.'
    if t.endswith(':') or (len(t.split()) < 10 and has(t, r'(;|hoặc|và)$')):
        return '', 'Đoạn là câu dẫn hoặc mục liệt kê chưa đủ ý; cần ghép nguyên văn với phần tiếp theo.'
    if has(t, r'^(họ, chữ đệm|ngày, tháng, năm sinh|nơi sinh, nơi đăng ký|số điện thoại, số định danh|quan điểm về|vị trí của cá nhân|các công ty con,|bất kỳ cá nhân, tổ chức nào là người giám hộ)'):
        return '', 'Mục liệt kê phụ thuộc đoạn dẫn/định nghĩa, chưa đủ nghĩa để phân loại riêng.'
    if len(t.split()) < 8:
        return '', 'Đoạn quá ngắn hoặc phụ thuộc phần trước, chưa đủ ngữ cảnh độc lập.'
    # Definition clauses concern what a term means, not a new payment/termination obligation.
    if 'định nghĩa' in h and has(t, r'(\blà\b|được hiểu|có nghĩa|bao gồm)'):
        return 'other', 'Khoản định nghĩa thuật ngữ/phạm vi, chưa thiết lập cơ chế nghĩa vụ của 7 nhóm chuyên biệt.'
    # A force-majeure exception inside an ordinary obligation is not the main subject.
    fm = 'bất khả kháng' in t and not has(t, r'^(trừ|ngoại trừ)')
    if fm and ('bất khả kháng' in h or has(t, r'^(sự kiện bất khả kháng|bất khả kháng|khi (sự kiện )?bất khả kháng|trong trường hợp (xảy ra )?(sự kiện )?bất khả kháng|nếu (sự kiện )?bất khả kháng)')):
        return 'force_majeure', REASONS['force_majeure']
    if 'bất khả kháng' in h and has(t, r'(bên bị ảnh hưởng|sự kiện|tiếp tục thực hiện|khắc phục|thông báo|nghĩa vụ|chứng minh)'):
        return 'force_majeure', REASONS['force_majeure']
    if has(t, r'^(mọi tranh chấp|nếu .*tranh chấp|trong .*tranh chấp|các tranh chấp|hai bên .*khiếu nại|các bên .*tranh chấp)') or has(t, r'(tòa án|toà án|trọng tài|giải quyết tranh chấp|thời hiệu khiếu nại)'):
        return 'dispute', REASONS['dispute']
    if has(t, r'(giải quyết.{0,20}khiếu nại|quyền khiếu nại|được khiếu nại|khiếu nại.{0,30}giá cước|tranh chấp tên miền)') and not has(t, r'(bồi thường|hoàn trả|từ chối)'):
        return 'dispute', REASONS['dispute']
    if has(t, r'^(bên .{0,20}(không|sẽ không) (chịu|có) trách nhiệm|không bên nào.*chịu trách nhiệm|mức phạt|tiền phạt|phạt vi phạm|bồi thường thiệt hại)'):
        return 'liability', REASONS['liability']
    # Operative suspension/termination is distinct from payment being merely its trigger.
    termination = has(t, r'(chấm dứt|tạm ngừng|tạm dừng|đình chỉ|hủy bỏ hợp đồng|huỷ bỏ hợp đồng|chặn dịch vụ|chặn chiều)')
    if termination and ('chấm dứt' in h or 'tạm ngừng' in h or has(t, r'(có quyền.*(?:chấm dứt|tạm ngừng|tạm dừng)|được.*(?:chấm dứt|chặn dịch vụ)|quyền.*hủy bỏ|bị hủy hợp đồng|bị huỷ hợp đồng)')):
        return 'termination', REASONS['termination']
    duration = has(t, r'((hợp đồng|văn bản|phụ lục).{0,60}có hiệu lực|thời hạn (của )?hợp đồng|gia hạn (hợp đồng|thời hạn)|hợp đồng.{0,35}hết hạn)')
    if duration and not has(h, r'(thanh toán|bất khả kháng|chấm dứt|bảo mật|dữ liệu)'):
        return 'duration', REASONS['duration']
    if has(t, r'(không.{0,35}(?:chịu trách nhiệm|bồi thường)|miễn trách nhiệm|phạt vi phạm|phạt chậm|phạt.{0,35}\d+\s*%|bồi thường|bồi hoàn)'):
        # A payment for compensation is a liability remedy, not an ordinary service fee.
        if not has(t, r'^(giá cước|phí dịch vụ|phí sử dụng)'):
            return 'liability', REASONS['liability']
    privacy_context = has(h, r'(dữ liệu|bảo mật|xử lý thông tin|thông tin mật)')
    privacy = has(t, r'(bảo mật|giữ bí mật|bí mật thông tin|tiết lộ|thông tin mật|dữ liệu cá nhân|mật khẩu|an toàn thông tin|bí mật nội dung|chia sẻ thông tin.{0,30}bên a)')
    if privacy or (privacy_context and has(t, r'(thu thập|xử lý|quý khách|khách hàng|lưu trữ|cung cấp|công khai|thông tin|bảo vệ)')):
        return 'confidentiality', REASONS['confidentiality']
    if has(h, r'(tiến độ|bảo hành|chất lượng|nội dung cung cấp)') and has(t, r'^(bên .{0,15}(có trách nhiệm )?cung cấp|thời gian bảo hành|bảo hành|việc cung cấp|đảm bảo chất lượng)'):
        return 'other', 'Ý chính là tiến độ, chất lượng, phạm vi dịch vụ hoặc bảo hành; mốc thanh toán/thời gian chỉ là điều kiện phụ.'
    if has(t, r'(thanh toán|giá cước|đơn giá|đặt cọc|hoá đơn|hóa đơn|cước phí|chi phí sử dụng|phí dịch vụ|giá dịch vụ|thu phí|đóng phí|nộp phí|tiền cước|tiền thuê|phí chuyển giao)'):
        return 'payment', REASONS['payment']
    if termination:
        return 'termination', REASONS['termination']
    if duration or (has(h, r'(thời hạn|hiệu lực)') and has(t, r'(hợp đồng|văn bản|gia hạn|hiệu lực)')):
        return 'duration', REASONS['duration']
    if fm:
        return 'force_majeure', REASONS['force_majeure']
    if has(t, r'(khiếu nại|khiếu kiện)'):
        return 'dispute', REASONS['dispute']
    if has(t, r'(phải|có quyền|có trách nhiệm|chịu trách nhiệm|được|cam kết|thỏa thuận|thoả thuận|đồng ý|thực hiện|cung cấp|là|bao gồm|bảo hành|tuân thủ|thông báo|yêu cầu|đảm bảo|bảo đảm|sử dụng dịch vụ)'):
        return 'other', REASONS['other']
    return '', 'Đoạn thiếu chủ thể/cơ chế rõ ràng khi đọc riêng; đề xuất loại hoặc ghép lại từ nguồn, không ép vào nhãn khác.'
