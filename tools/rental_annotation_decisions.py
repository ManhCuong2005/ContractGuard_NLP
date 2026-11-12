"""Explicit agent decisions after source reading, never keyword-generated target labels.

Numbers refer to the pinned candidate snapshot below (including versioned
source extensions). Every retained label has an explicit ID assignment below.
Unassigned candidates remain an unlabelled reserve.
Human dataset review is separate and remains pending.
"""
CANDIDATE_SNAPSHOT_SHA256 = '1613ab24936e84da16edd0192108555e968a1512c08af8acf3d40d84d67a75cd'

PROFILES = {
 'handover': ('handover','Giao nhận theo thỏa thuận/hiện trạng được ghi nhận; khoản này xác định trách nhiệm bàn giao hoặc quyền nhận nhà của người thuê.'),
 'stable_use': ('tenant_rights','Bảo đảm quyền sử dụng ổn định/riêng rẽ hoặc tiếp tục thuê khi thay đổi chủ; quyền này được quy định cho người thuê, không trao quyền thu hồi tùy ý.'),
 'payment': ('payment','Nghĩa vụ thanh toán gắn với tiền thuê, kỳ hạn hoặc dịch vụ đã sử dụng/thỏa thuận; không có cơ chế tự bổ sung khoản nợ không xác định trong đơn vị này.'),
 'owner_repair': ('repair','Chủ nhà thực hiện bảo dưỡng/sửa chữa hoặc người thuê có quyền yêu cầu khắc phục; không chuyển mọi hư hỏng không do người thuê sang người thuê.'),
 'fault': ('liability','Trách nhiệm bồi thường/sửa chữa gắn với lỗi hoặc hư hỏng do chính người thuê/người liên quan gây ra; có căn cứ giới hạn phạm vi trách nhiệm.'),
 'owner_liability': ('liability','Quy định trách nhiệm/cam kết của bên cho thuê hoặc bồi thường cho người thuê khi bên cho thuê gây thiệt hại; không phải nghĩa vụ bồi thường mở của người thuê.'),
 'consent': ('modification','Cải tạo, thay đổi hoặc sửa đổi hợp đồng cần thỏa thuận/chấp thuận; điều khoản có cơ chế đồng ý, không cho chủ nhà tự đặt nghĩa vụ mới.'),
 'renewal': ('renewal','Tiếp tục thuê/gia hạn theo thỏa thuận hoặc quyền ưu tiên; không mặc nhiên tái ràng buộc người thuê vào một kỳ tài chính mới.'),
 'return': ('handover','Quy định trả lại nhà/tài sản hoặc lập biên bản quyết toán khi kết thúc; nội dung này không tự cho phép tịch thu toàn bộ tài sản của người thuê.'),
 'conduct': ('use_rules','Quy định sử dụng đúng mục đích, bảo quản, vệ sinh/an ninh/PCCC hoặc hạn chế chuyển nhượng; nghĩa vụ cụ thể phục vụ sử dụng nhà, không phải miễn trách nhiệm chủ nhà.'),
 'dispute': ('dispute_resolution','Cho các bên thương lượng và yêu cầu cơ quan có thẩm quyền/Tòa án giải quyết; người thuê không bị tước quyền phản đối trong nội dung này.'),
 'deposit': ('deposit','Đặt cọc/hoàn cọc gắn với nghĩa vụ bảo đảm và quyết toán nợ, thiệt hại được xác định; đọc kèm phân định lỗi và ngoại lệ đã đưa vào text.'),
 'termination': ('termination','Chấm dứt có căn cứ xác định như hết hạn, hai bên thỏa thuận hoặc vi phạm đã mô tả và thủ tục liên quan; không suy nhãn từ riêng chữ chấm dứt.'),
 'notice': ('notice','Quy định cách gửi/nhận thông báo và thông tin liên hệ; xác nhận nhận thông báo không phải mặc nhiên đồng ý giá hay nghĩa vụ mới.'),
 'force_majeure': ('force_majeure','Nghĩa vụ thông báo, chứng minh hoặc tạm dừng được áp dụng khi có sự kiện khách quan; đơn vị này không tự chuyển mọi thiệt hại sang người thuê.'),
 'privacy': ('personal_data','Mục đích thông tin giới hạn ở thực hiện thuê nhà/cư trú, hoặc có nghĩa vụ bảo mật/đồng ý; không có quyền sử dụng/chia sẻ mở cho mục đích khác.'),
 'effect': ('general','Xác định hiệu lực, cam kết tự nguyện hoặc giá trị văn bản/phụ lục cho các bên; không phải từ bỏ quyền khiếu nại hay miễn trách nhiệm vô điều kiện.'),
 'access': ('access','Việc kiểm tra/vào nhà có giới hạn thông báo, lịch/mục đích hoặc ngoại lệ khẩn cấp được nêu trong text; không đồng nhất mọi việc kiểm tra với rủi ro.'),
 'fixed_price': ('price_change','Giá được giữ ổn định hoặc thay đổi bằng cơ chế đã thống nhất có quyền tham gia của người thuê; không phải quyền tự tăng vô hạn của chủ nhà.'),
}
DECISIONS = {}

def ids(contract, numbers):
    values=[]
    for token in numbers.replace(',',' ').split():
        if '-' in token:
            a,b=map(int,token.split('-'))
            values.extend(range(a,b+1))
        else:
            values.append(int(token))
    return [f'{contract}_{n:04d}' for n in values]

def normal(contract,numbers,profile,context=(),reason=None):
    kind,default=PROFILES[profile]
    for cid in ids(contract,numbers):
        if cid in DECISIONS:
            raise ValueError(f'Duplicate decision: {cid}')
        DECISIONS[cid]=dict(label='normal',clause_type=kind,risk_category='',
            annotation_reason=reason or default,label_confidence='high',
            context_clause_ids=list(context),decision_profile=profile)

def abnormal(cid,category,kind,reason,evidence,context=(),confidence='high'):
    if cid in DECISIONS:
        raise ValueError(f'Duplicate decision: {cid}')
    DECISIONS[cid]=dict(label='abnormal',risk_category=category,clause_type=kind,
        annotation_reason=reason,risk_evidence=evidence,label_confidence=confidence,
        context_clause_ids=list(context),decision_profile='individual_source_reading')

# Chính phủ: empty form fields and statutory cross-references without the
# operative conditions are not automatically normal.
normal('gov_residential','39 40 42 54 66 78','payment')
normal('gov_residential','53 61 68','handover')
normal('gov_residential','55 77 81','conduct')
normal('gov_residential','56 79 82','fault')
normal('gov_residential','57 70 71 99','consent')
normal('gov_residential','59 80','return')
normal('gov_residential','62 64 72','stable_use')
normal('gov_residential','63 73','owner_repair')
normal('gov_residential','65 74','owner_liability')
normal('gov_residential','69','handover')
normal('gov_residential','84','force_majeure')
normal('gov_residential','88','termination')
normal('gov_residential','94','dispute')
normal('gov_residential','98','effect')

# Sunshine: long-term residential lease, a separate cohort; purchase conversion
# 10.3 is deliberately not included. Cross references used for a decision are
# included in model input, rather than hidden in the annotation rationale.
normal('sunshine_longterm','1-4 11 22-25 27 39 43 51 52 81 83','handover')
normal('sunshine_longterm','9 29 34 54 58 59','payment')
normal('sunshine_longterm','13','consent')
normal('sunshine_longterm','15 16 30 35 45 46','conduct')
normal('sunshine_longterm','26 50 86-89','owner_repair')
normal('sunshine_longterm','28','handover')
normal('sunshine_longterm','32','owner_liability')
normal('sunshine_longterm','33','privacy')
normal('sunshine_longterm','36 37 41 42','stable_use')
normal('sunshine_longterm','44','handover')
normal('sunshine_longterm','55 57 61-64 68 69 72','conduct')
normal('sunshine_longterm','70','fault')
normal('sunshine_longterm','82','notice')
normal('sunshine_longterm','84','handover',context=['sunshine_longterm_0044','sunshine_longterm_0081','sunshine_longterm_0082'],reason='Cơ chế coi đã nhận bàn giao chỉ khi không có lý do chính đáng, loại trừ 6.1(f); đã kèm quyền từ chối do chất lượng và thông báo trước. Không lấy riêng chữ được xem như để gán bất lợi.')
abnormal('sunshine_longterm_0056','broad_liability','liability','Người thuê gánh mọi rủi ro/mất mát từ bàn giao và không được hoàn tiền thuê; ngoại lệ chỉ gồm bảo đảm pháp lý, bảo hành và vi phạm chủ nhà đã quy định. Phần rủi ro khách quan còn lại vẫn chuyển sang người thuê, không phụ thuộc lỗi.','mọi rủi ro, mất mát, hay thiệt hại',confidence='high')
abnormal('sunshine_longterm_0067','broad_liability','liability','Bồi thường đầy đủ tất cả chi phí/tổn thất cả trực tiếp lẫn gián tiếp liên quan bất kỳ vi phạm nào. Nghĩa vụ mở vượt thiệt hại trực tiếp có phạm vi xác định.','trực tiếp hoặc gián tiếp')
abnormal('sunshine_longterm_0071','unilateral_change','modification','Phạm vi công việc người thuê phải làm do bên cho thuê tự thấy cần thiết quyết định. Dù mục đích là giúp thực hiện hợp đồng/pháp luật, không có giới hạn đầu việc hay quyền từ chối tương ứng.','mọi việc mà Bên Cho Thuê nhận thấy cần thiết',confidence='medium')

# Resident apartment: taxes/third-party costs retained as contextual holds if
# they cannot be isolated without ambiguous financial scope.
normal('resident_apartment','6','renewal')
normal('resident_apartment','9 18','payment')
normal('resident_apartment','10','handover')
normal('resident_apartment','11-14 16','stable_use')
normal('resident_apartment','17 20 24','conduct')
normal('resident_apartment','19','fault')
normal('resident_apartment','25','consent')
normal('resident_apartment','27','dispute')
normal('resident_apartment','29-34 36-39','effect')
abnormal('resident_apartment_0015','broad_liability','liability','Phối hợp xử lý vấn đề bên thứ ba nhưng chuyển mọi chi phí phát sinh sang bên thuê, không phân định vấn đề do lỗi/quyền sở hữu chủ nhà hay do người thuê. Cụm pháp luật có quy định bắt buộc không thu hẹp người gây chi phí.','Mọi chi phí nếu có thuộc bên B',confidence='medium')

normal('resident_room','1 7 8 33','handover')
normal('resident_room','2 3 12 14 26','payment')
normal('resident_room','9 11 43-45','stable_use')
normal('resident_room','10 37','owner_repair')
normal('resident_room','13','privacy')
normal('resident_room','15 17 34-36 47','consent')
normal('resident_room','16 25','fault')
normal('resident_room','28 32','return')
normal('resident_room','29-31','conduct')
normal('resident_room','38','renewal')
normal('resident_room','40-42','termination')
normal('resident_room','46','dispute')
normal('resident_room','48-52','termination')
normal('resident_room','54-56','effect')

normal('minhkhue_house_simple','6','payment')
normal('minhkhue_house_simple','8-10','conduct',context=['minhkhue_house_simple_0007'])
normal('minhkhue_house_simple','12','fault',context=['minhkhue_house_simple_0011'])
normal('minhkhue_house_simple','14','owner_repair')
normal('minhkhue_house_simple','15','stable_use')
normal('minhkhue_house_simple','16','dispute')
abnormal('minhkhue_house_simple_0013','broad_liability','liability','Sau khi bỏ trống không lý do chính đáng 30 ngày từ thông báo, người thuê phải chịu mọi hư hỏng/mất mát trong thời gian bỏ trống. Cơ chế gánh mọi nguyên nhân rộng hơn điều khoản lỗi/hao mòn ở Điều 5 đã kèm.','Mọi hư hỏng, mất mát trong thời gian bỏ trống',context=['minhkhue_house_simple_0011','minhkhue_house_simple_0012'],confidence='medium')

normal('thuecanho123_apartment','7 39','renewal')
normal('thuecanho123_apartment','9','fixed_price')
normal('thuecanho123_apartment','10 13 14 30 38','payment')
normal('thuecanho123_apartment','12','deposit')
normal('thuecanho123_apartment','17 31','fault')
normal('thuecanho123_apartment','18','access')
normal('thuecanho123_apartment','19','handover')
normal('thuecanho123_apartment','20 21 23','stable_use')
normal('thuecanho123_apartment','25 27 29','conduct')
normal('thuecanho123_apartment','24','deposit',context=['thuecanho123_apartment_0040'])
normal('thuecanho123_apartment','32-36','termination')
normal('thuecanho123_apartment','42','dispute')
normal('thuecanho123_apartment','43 44','effect')

normal('homedy_room_full','5 21 23 25','conduct')
normal('homedy_room_full','10','renewal')
normal('homedy_room_full','14 22','payment')
normal('homedy_room_full','15','fault')
normal('homedy_room_full','17','consent')
normal('homedy_room_full','19','access')
normal('homedy_room_full','20','handover')
normal('homedy_room_full','26 27 28','termination')
normal('homedy_room_full','29 30','effect')

normal('minhkhue_house','1 24','handover')
normal('minhkhue_house','4 20 22','owner_liability')
normal('minhkhue_house','6 21 25','stable_use')
normal('minhkhue_house','8','renewal')
normal('minhkhue_house','9 12','deposit')
normal('minhkhue_house','13','deposit',context=['minhkhue_house_0012'])
normal('minhkhue_house','15-17 29','payment')
normal('minhkhue_house','18 28','fault')
normal('minhkhue_house','19','handover')
normal('minhkhue_house','26','owner_repair')
normal('minhkhue_house','27 30','return')
normal('minhkhue_house','31','consent')
normal('minhkhue_house','32','conduct')
normal('minhkhue_house','33','termination')
normal('minhkhue_house','34-37','effect')

normal('mauhopdong_public','7','renewal')
normal('mauhopdong_public','20','handover')
normal('mauhopdong_public','21 23','stable_use')
normal('mauhopdong_public','24','payment')
normal('mauhopdong_public','25-27','conduct')
normal('mauhopdong_public','28','owner_repair')
normal('mauhopdong_public','29','fault')
normal('mauhopdong_public','30-33','termination')
normal('mauhopdong_public','35','dispute',context=['mauhopdong_public_0034'])
normal('mauhopdong_public','36','effect')

normal('replus_house','3','renewal')
normal('replus_house','5','deposit')
normal('replus_house','7','stable_use')
normal('replus_house','8','conduct')
normal('replus_house','9','owner_repair')
normal('replus_house','10','termination')
normal('replus_house','11','return')
normal('replus_house','13','dispute')
normal('replus_house','14','effect')
normal('troxanh_room','3','renewal')
normal('troxanh_room','8 9','deposit',context=['troxanh_room_0019'])
normal('troxanh_room','11 12','stable_use')
normal('troxanh_room','13 18','privacy')
normal('troxanh_room','14','access')
normal('troxanh_room','15','payment')
normal('troxanh_room','16 17','conduct')
normal('troxanh_room','19','fault')
normal('troxanh_room','21','termination')
normal('troxanh_room','22','dispute')
normal('troxanh_room','23','effect')

normal('bandon_room','1 26 27 29 33-36 44','conduct')
normal('bandon_room','15','payment')
normal('bandon_room','17','deposit',context=['bandon_room_0030','bandon_room_0031','bandon_room_0051'])
normal('bandon_room','20','owner_liability')
normal('bandon_room','24 46','privacy')
normal('bandon_room','30 31','fault')
normal('bandon_room','47 48','consent')
normal('bandon_room','49','payment',context=['bandon_room_0047','bandon_room_0048'])
normal('bandon_room','51','fault')
normal('bandon_room','57 58','effect')
abnormal('bandon_room_0016','access_interference|deposit_forfeiture|broad_liability','termination','Chậm trả dẫn đến niêm phong phòng, mất cọc và miễn trách nhiệm đối với tài sản người thuê. Cảnh báo dựa trên cơ chế tự hạn chế quyền sử dụng/miễn trách nhiệm, không dựa vào việc tự đặt ngưỡng phụ thu cao.','niêm phong phòng')
abnormal('bandon_room_0021','deposit_forfeiture|termination_discretion','termination','Bất kỳ vi phạm nào hoặc người thuê chấm dứt với bất kỳ lý do gì đều có thể bị ngừng hợp đồng ngay và mất cọc lẫn tiền phòng còn lại; không loại trừ việc chấm dứt vì lỗi chủ nhà. Điều sang nhượng có thủ tục riêng không giải quyết ngoại lệ lỗi chủ nhà.','Với bất kỳ lý do gì',context=['bandon_room_0047','bandon_room_0048','bandon_room_0049'])
abnormal('bandon_room_0022','termination_discretion|deposit_forfeiture','termination','Chủ nhà tự phát hiện hành vi sai trái là căn cứ lấy lại chỗ ở và không hoàn cọc; phạm vi sai trái không được định nghĩa, không yêu cầu xác minh hay cơ hội khắc phục.','có hành vi sai trái')
abnormal('bandon_room_0025','broad_liability','liability','Miễn hoàn toàn trách nhiệm chủ nhà khi tài sản cá nhân mất, không phân biệt lỗi hoặc việc giữ tài sản của chủ nhà; nghĩa vụ tự bảo quản không giải quyết ngoại lệ đó.','bên A hoàn toàn không chịu trách nhiệm',confidence='medium')
abnormal('bandon_room_0043','repair_burden','repair','Sau 15 ngày chuyển mọi hư hỏng tài sản/thiết bị sang người thuê tự sửa, thay thế hoặc bồi thường, không xét lỗi, hao mòn hay hư hỏng có sẵn phát lộ muộn. Không chỉ là sửa chữa nhỏ do sử dụng sai.','Nếu sau 15 ngày, mọi hư hỏng')
abnormal('bandon_room_0052','access_interference|deposit_forfeiture|termination_discretion|broad_liability','termination','Bất kỳ vi phạm nào cho phép chấm dứt vô điều kiện ngay, niêm phong phòng, mất cọc và miễn trách nhiệm tài sản. Đã kèm quy định nhắc nhở ba lần: Điều 7 vẫn dùng bất kỳ vi phạm/ngay thời điểm nên có cơ chế rộng và mâu thuẫn bảo vệ.','vô điều kiện ngay tại thời điểm vi phạm',context=['bandon_room_0037'])

normal('roomi_registration','1 42','handover')
normal('roomi_registration','3','renewal')
normal('roomi_registration','9 35 47','payment')
normal('roomi_registration','13 14','handover')
normal('roomi_registration','24 27 41','privacy')
normal('roomi_registration','29-31 48-51','conduct')
normal('roomi_registration','32 36','fault')
normal('roomi_registration','37','access')
normal('roomi_registration','39 43','stable_use')
normal('roomi_registration','40 44','owner_repair')
normal('roomi_registration','45','return')
normal('roomi_registration','46','fault',reason='Người thuê được loại trừ hao mòn theo thời gian; các ví dụ như bóng đèn tự cháy/rỉ sét không buộc người thuê bồi thường. Đây là đối chứng cho việc chuyển mọi sửa chữa sau một mốc ngày.')
normal('roomi_registration','52','fault',context=['roomi_registration_0036','roomi_registration_0040','roomi_registration_0046'],reason='Chịu 100% chi phí chỉ đối với sử dụng SAI CÁCH; text đã kèm chủ nhà sửa hỏng không do lỗi và miễn bồi thường hao mòn. Không gán abnormal chỉ vì chữ 100%.')
normal('roomi_registration','53 55 56 61','effect')
normal('roomi_registration','54','conduct')
abnormal('roomi_registration_0010','deposit_forfeiture|termination_discretion','termination','Sau ba ngày chậm trả, chủ nhà có thể chấm dứt, thu hồi và giữ toàn bộ cọc; không có thông báo/khắc phục hoặc đối soát nợ trước chế tài mất cọc. Cảnh báo sự gộp thu hồi và tịch cọc không dựa trên ngưỡng số ngày tự đặt.','không cần hoàn trả lại tiền cọc',confidence='medium')
abnormal('roomi_registration_0025','broad_liability','liability','Miễn bất cứ trách nhiệm nào của chủ nhà đối với hư hỏng/mất tài sản cá nhân, không loại trừ lỗi chủ nhà; phạm vi miễn trách nhiệm rộng hơn yêu cầu tự bảo quản.','Bên A không chịu bất cứ trách nhiệm nào',confidence='medium')
abnormal('roomi_registration_0033','termination_discretion','termination','Chỉ cần phòng khác/hàng xóm phản ánh ồn ào là hợp đồng bị hủy; không có bước xác minh vi phạm, nhắc nhở hay khắc phục trước khi mất chỗ ở.','phòng khác/hàng xóm phản ánh',confidence='high')
abnormal('roomi_registration_0058','access_interference','access','Dù có điều kiện vi phạm nghiêm trọng và thông báo, chủ nhà được tự mở khóa, niêm phong/di dời tài sản để thu hồi; cơ quan chức năng chỉ được mời chứng kiến, không phải cơ chế giải quyết tranh chấp/thi hành quyết định được nêu.','mời cơ quan chức năng chứng kiến',confidence='medium')

normal('iuoss_dorm','3','conduct')
normal('iuoss_dorm','4 5','effect')
normal('iuoss_dorm','6','fixed_price')
normal('iuoss_dorm','7-9 15 19 20','payment')
normal('iuoss_dorm','10','deposit',context=['iuoss_dorm_0021'])
normal('iuoss_dorm','17','stable_use')
normal('iuoss_dorm','18','owner_liability')
normal('iuoss_dorm','21','fault')
normal('iuoss_dorm','22 24','conduct')
normal('iuoss_dorm','25','termination')
normal('iuoss_dorm','26','renewal')
normal('iuoss_dorm','27','dispute')
abnormal('iuoss_dorm_0016','access_interference','access','Cho chủ nhà kiểm tra đột xuất trong thời hạn hợp đồng, không giới hạn khẩn cấp, báo trước hay đồng ý; mục đích tìm hỏng để bồi thường không tự bảo vệ quyền sử dụng riêng.','quyền kiểm tra đột xuất')
abnormal('iuoss_dorm_0023','deposit_forfeiture|broad_liability','termination','Sau ba lần nhắc bằng văn bản có thể chấm dứt và không hoàn cả cọc HOẶC tiền lưu trú đã đóng. Dù có cơ hội sửa vi phạm, giữ tiền trả trước không gắn thời gian đã ở/nợ/thiệt hại nên vẫn có dấu hiệu bất lợi.','không hoàn trả lại tiền cọc hoặc tiền lưu trú đã đóng',confidence='medium')

normal('sunshine_longterm','96','owner_repair')
normal('sunshine_longterm','99-103','consent',context=['sunshine_longterm_0098'])
normal('sunshine_longterm','107','stable_use')
normal('sunshine_longterm','118 119','fixed_price')
normal('sunshine_longterm','125 126','termination')
normal('sunshine_longterm','127','stable_use')
normal('sunshine_longterm','132','owner_liability')
normal('sunshine_longterm','133','return')
normal('sunshine_longterm','134-140 143','force_majeure')
normal('sunshine_longterm','141 142','force_majeure',context=['sunshine_longterm_0129'])
normal('sunshine_longterm','144 145 151','notice')
normal('sunshine_longterm','147-150','notice',context=['sunshine_longterm_0146'])
normal('sunshine_longterm','152','dispute')
normal('sunshine_longterm','153 154','owner_liability')
normal('sunshine_longterm','155 156 159-169','effect')
normal('sunshine_longterm','158','privacy')
abnormal('sunshine_longterm_0095','repair_burden','repair','Sau thời hạn bảo hành mọi sửa hư hỏng căn hộ trong suốt thời hạn thuê thuộc người thuê, không phân định nguyên nhân/lỗi. Đã kèm phạm vi sửa kết cấu và 60 tháng bảo hành; nguyên bản dẫn Điều 9.7 được giữ đúng, không tự sửa thành 9.5.','việc sửa chữa các hư hỏng',context=['sunshine_longterm_0086','sunshine_longterm_0089','sunshine_longterm_0096'])
abnormal('sunshine_longterm_0117','unilateral_change','price_change','Trước khi có ban quản trị, chủ nhà có thể điều chỉnh/bổ sung mức phí chỉ bằng thông báo. Dù phải tính hợp lý và phù hợp pháp luật/thực tế, không có công thức/trần hoặc quyền từ chối tương ứng; cảnh báo phần tùy nghi còn lại, không khẳng định toàn bộ điều chỉnh trái luật.','điều chỉnh, bổ sung bằng thông báo',confidence='medium')
abnormal('sunshine_longterm_0128','broad_liability','termination','Trong trường hợp chấm dứt do phá sản/giải thể, chỉ hoàn tiền khi bán/cho thuê lại và thu được giá thanh lý do chủ nhà toàn quyền quyết; lấy số thấp hơn và khấu trừ thêm. Người thuê chịu rủi ro giá và thời gian hoàn không xác định.','tùy thuộc vào khoản nào thấp hơn')
abnormal('sunshine_longterm_0129','broad_liability','force_majeure','Căn hộ không thể sử dụng do bất khả kháng thì không hoàn bất kỳ phần tiền thuê đã thanh toán; người thuê chỉ có bảo hiểm nếu đã mua. Đã giữ cả nhánh A hoàn tiền khi nhà còn dùng được để không bỏ ngoại lệ.','không có trách nhiệm hoàn trả lại bất kỳ phần nào')
abnormal('sunshine_longterm_0131','broad_liability','termination','Sau chấm dứt do vi phạm, việc hoàn tiền vẫn chờ chủ nhà bán/cho thuê lại theo giá tự quyết, lấy mức thấp hơn và khấu trừ. Không gán rủi ro chỉ vì mức phạt 16% vì Điều 13.1(h) có đối ứng; rủi ro là phụ thuộc thanh lý và giá không kiểm soát.','theo toàn quyền quyết định',context=['sunshine_longterm_0130','sunshine_longterm_0132'])

normal('homedy_student','8 10 15 31','payment')
normal('homedy_student','11','fixed_price',reason='Giá thay đổi khi Nhà nước thay khung giá/giá thuê và phải báo trước một tháng; căn cứ điều chỉnh được nêu, không phải chủ nhà tùy nghi tăng bất kỳ lúc nào.')
normal('homedy_student','14 21 24 29 33-35','conduct')
normal('homedy_student','16 32','fault')
normal('homedy_student','20 26','handover')
normal('homedy_student','22 27','owner_repair')
normal('homedy_student','23','fixed_price',context=['homedy_student_0011'])
normal('homedy_student','36','return')
normal('homedy_student','38-42 44 45','termination')
normal('homedy_student','46 48','effect')
normal('homedy_student','47','dispute')

# Danang source has spaced article headings in the DOCX. Retain those exact
# heading rows as context, rather than silently inventing an actor or title.
normal('danang_bilingual','3','conduct',context=['danang_bilingual_0001'])
normal('danang_bilingual','6','renewal',context=['danang_bilingual_0001'])
normal('danang_bilingual','11','payment',context=['danang_bilingual_0007'])
normal('danang_bilingual','12','fixed_price',context=['danang_bilingual_0007'])
normal('danang_bilingual','26','owner_liability',context=['danang_bilingual_0025'])
normal('danang_bilingual','27','handover',context=['danang_bilingual_0025'])
normal('danang_bilingual','28','stable_use',context=['danang_bilingual_0025'])
normal('danang_bilingual','29','privacy',context=['danang_bilingual_0025'])
normal('danang_bilingual','31 37','payment',context=['danang_bilingual_0030'])
normal('danang_bilingual','32 34-36','conduct',context=['danang_bilingual_0030'])
normal('danang_bilingual','33','consent',context=['danang_bilingual_0030'])
normal('danang_bilingual','41','access',context=['danang_bilingual_0040'])
normal('danang_bilingual','43 44','termination',context=['danang_bilingual_0042','danang_bilingual_0046'])
normal('danang_bilingual','48','owner_liability',context=['danang_bilingual_0042'])
normal('danang_bilingual','50','consent')
abnormal('danang_bilingual_0038','broad_liability|repair_burden','repair','Người thuê chịu bất kỳ/toàn bộ bảo dưỡng và mất mát thiết bị, nội thất, không phân biệt lỗi/hao mòn. Đã kèm Điều 6: chủ nhà báo trước khi bảo dưỡng và người thuê chịu chi phí do cản trở vô lý; điều đó không thu hẹp nghĩa vụ toàn bộ ở 5.9.','bất kỳ/toàn bộ sự bảo dưỡng',context=['danang_bilingual_0030','danang_bilingual_0040','danang_bilingual_0041'],confidence='medium')

# Public operator template, originally scanned. All selected operative text was
# visually checked; proof and image hashes are part of the source manifest.
normal('sadeco_worker','1 2 15 24 30-32','conduct')
normal('sadeco_worker','3 9-11 17 25','payment')
normal('sadeco_worker','5 22','renewal')
normal('sadeco_worker','13','fault',context=['sadeco_worker_0020'])
normal('sadeco_worker','16','handover')
normal('sadeco_worker','18 26','privacy')
normal('sadeco_worker','19','stable_use')
normal('sadeco_worker','20','owner_repair')
normal('sadeco_worker','21','notice')
normal('sadeco_worker','23','termination',context=['sadeco_worker_0041','sadeco_worker_0042'])
normal('sadeco_worker','33','fault')
normal('sadeco_worker','34','return',context=['sadeco_worker_0013'])
normal('sadeco_worker','41','termination',context=['sadeco_worker_0042'])
normal('sadeco_worker','42','termination')
normal('sadeco_worker','43 44','consent')
normal('sadeco_worker','45','dispute')
normal('sadeco_worker','46','effect')
abnormal('sadeco_worker_0012','access_interference','access','Mặc dù có kiểm tra định kỳ một lần/tháng, chủ nhà còn được kiểm tra đột xuất nếu có, không nêu giới hạn khẩn cấp/thông báo hay đồng ý. Cảnh báo phần đột xuất không giới hạn, không phải bản thân lịch kiểm tra hàng tháng.','trường hợp đột xuất')
abnormal('sadeco_worker_0014','access_interference','access','Cho tạm ngưng điện, nước thiết yếu để xử lý chậm thanh toán, kể cả chậm tiền thuê. Đã kèm thời điểm gửi hóa đơn và hạn trả; rủi ro nằm ở biện pháp hạn chế sinh hoạt để ép trả nợ, không suy từ mốc ba ngày.','tạm ngưng cung cấp điện, nước',context=['sadeco_worker_0009','sadeco_worker_0017'])
abnormal('sadeco_worker_0027','broad_liability','repair','Trách nhiệm sửa chữa có giới hạn lỗi của người thuê, nhưng sau đó chủ nhà thuê bên thứ ba và người thuê buộc chấp thuận toàn bộ giá trị thông báo, trả trong ba ngày. Đã giữ quyền tranh chấp chung; cảnh báo nghĩa vụ nhận giá trước khi có cơ chế đối soát/giới hạn cụ thể, không gán vì mọi chi phí sửa chữa hoặc vì mất quyền kiện tuyệt đối.','Bên B buộc phải chấp thuận giá trị trên',context=['sadeco_worker_0013','sadeco_worker_0045'],confidence='medium')

normal('cochinh_room1','6','owner_liability')
normal('cochinh_room1','7','privacy')
normal('cochinh_room1','10','conduct')
normal('cochinh_room1','11','consent')
abnormal('cochinh_room1_0009','repair_burden','repair','Người thuê phải sửa các hư hỏng trong phòng trong khi sử dụng, nếu không thì trừ cọc theo giá thị trường, không phân định lỗi/hao mòn hay phần sửa chữa thuộc chủ nhà. Giá thị trường không tự giải quyết việc chuyển cả hỏng không do người thuê.','sửa chữa các hư hỏng trong phòng',confidence='medium')

# Different ACC URL: this operative source really is room rental, unlike the
# previously excluded page whose Article 1 specified a clothing shop.
normal('acc_room_actual','1 7','handover')
normal('acc_room_actual','5','deposit')
normal('acc_room_actual','8','privacy')
normal('acc_room_actual','9','payment')
normal('acc_room_actual','10','consent')
normal('acc_room_actual','11','conduct')
normal('acc_room_actual','12 15','effect')
normal('acc_room_actual','13','dispute')
normal('acc_room_actual','14','renewal')
abnormal('acc_room_actual_0006','deposit_forfeiture','deposit','Mọi việc người thuê ngưng trước hạn được diễn đạt là mất cọc, không nêu ngoại lệ khi chấm dứt do bên cho thuê vi phạm. Đã đọc cả nhánh chủ nhà ngưng phải bồi thường gấp đôi: tính đối ứng đó chưa xử lý trường hợp người thuê có căn cứ chấm dứt. Chỉ là dấu hiệu cần xem xét, không kết luận mất cọc trước hạn luôn trái luật.','Bên B ngưng hợp đồng trước thời hạn sẽ bị mất tiền cọc',context=['acc_room_actual_0013'],confidence='medium')
