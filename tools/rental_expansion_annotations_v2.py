"""Explicit ID-level source-reading decisions. Unassigned candidates remain unlabelled.

The requested 500 positives is a collection target, never a labelling rule.
No training, prediction-based relabelling, fabricated clauses or inferred approval.
"""
from rental_annotation_decisions import PROFILES, ids

CANDIDATE_SHA256='8581c0d30d14f48db4421845b7120469b92097b4ff2824fccfb33faef28a678a'
DECISIONS={}
HOLDS={}
SOURCE_REVIEWS={}


def source(sid,subtype,evidence,role='Bên B (bên thuê), Bên A (bên cho thuê)'):
    SOURCE_REVIEWS[sid]=dict(domain='residential_rental',protected_party='tenant',
        rental_subtype=subtype,tenant_role=role,scope_evidence=evidence,
        review_method='explicit_agent_source_reading',source_use_status='pending_dataset_and_source_review')


def normal(contract,numbers,profile,context=(),reason=None):
    kind,default=PROFILES[profile]
    for cid in ids(contract,numbers):
        if cid in DECISIONS:raise ValueError('Duplicate decision '+cid)
        DECISIONS[cid]=dict(label='normal',clause_type=kind,risk_category='',
            annotation_reason=reason or default,label_confidence='high',
            context_clause_ids=list(context),decision_profile=profile)


def abnormal(cid,risk,kind,reason,evidence,context=(),confidence='high'):
    if cid in DECISIONS:raise ValueError('Duplicate decision '+cid)
    DECISIONS[cid]=dict(label='abnormal',clause_type=kind,risk_category=risk,
        annotation_reason=reason,risk_evidence=evidence,label_confidence=confidence,
        context_clause_ids=list(context),decision_profile='individual_source_reading')


def hold(contract,numbers,reason):
    for cid in ids(contract,numbers):HOLDS[cid]=reason


source('bdsdaily_house_pdf','house','1.1: để sử dụng làm nơi để ở; phần các bên xác định Bên B là bên thuê.')
normal('bdsdaily_house_pdf','4 19 24','handover')
normal('bdsdaily_house_pdf','5 22','owner_liability')
normal('bdsdaily_house_pdf','7 21 25','stable_use')
normal('bdsdaily_house_pdf','9','renewal')
normal('bdsdaily_house_pdf','12','deposit')
normal('bdsdaily_house_pdf','13','deposit',context=['bdsdaily_house_pdf_0012'])
normal('bdsdaily_house_pdf','15 16 17 29','payment')
normal('bdsdaily_house_pdf','18 28','fault')
normal('bdsdaily_house_pdf','26','owner_repair')
normal('bdsdaily_house_pdf','27 30','return')
normal('bdsdaily_house_pdf','31 36','consent')
normal('bdsdaily_house_pdf','32','conduct')
normal('bdsdaily_house_pdf','20 34 35 37','effect')
hold('bdsdaily_house_pdf','11 33','Cần rà quan hệ giữa quyền chấm dứt hai phía chỉ báo trước và trách nhiệm bồi thường/ngoại lệ; chưa ép nhãn để tăng abnormal.')

source('danang_house2_docx','house','Tiêu đề HỢP ĐỒNG CHO THUÊ NHÀ Ở; Điều 4-8 quy định sinh sống, hộ khẩu và tài sản nhà ở.')
normal('danang_house2_docx','17','payment')
normal('danang_house2_docx','18 19','conduct')
normal('danang_house2_docx','20','consent')
normal('danang_house2_docx','21','return')
normal('danang_house2_docx','22','fault')
normal('danang_house2_docx','24','owner_repair')
normal('danang_house2_docx','25','stable_use')
normal('danang_house2_docx','26','dispute')
normal('danang_house2_docx','27','effect')
hold('danang_house2_docx','23','Điều 6 ghi mọi hư hỏng/mất mát trong thời gian bỏ trống, nhưng Điều 5 giới hạn lỗi và Điều 7 giao chủ nhà sửa; cần rà phạm vi ngoại lệ, chưa ép abnormal.')

source('danang_house_docx','house','1.1 xác định mục đích làm nơi để ở; các bên A/B được định nghĩa ở đầu hợp đồng.')
normal('danang_house_docx','15 35 40','handover')
normal('danang_house_docx','18 38','owner_liability')
normal('danang_house_docx','20 37 41','stable_use')
normal('danang_house_docx','22','renewal')
normal('danang_house_docx','26','deposit')
normal('danang_house_docx','27','deposit',context=['danang_house_docx_0026'])
normal('danang_house_docx','29 30 31 32 33 45','payment')
normal('danang_house_docx','34 44','fault')
normal('danang_house_docx','42','owner_repair')
normal('danang_house_docx','43 46','return')
normal('danang_house_docx','47 52','consent')
normal('danang_house_docx','48','conduct')
normal('danang_house_docx','36 39 50 51 53','effect')
hold('danang_house_docx','24 25 49','Cùng họ nội dung BDSDaily; quan hệ điều khoản chấm dứt/cọc cần rà riêng, không đếm bản chép thành dữ liệu mới.')

source('v2_nhatrang_tdtu_edu_vn_04ae8be4','student_dormitory','HỢP ĐỒNG THUÊ CHỖ Ở NỘI TRÚ; Bên A là TDTU Phân hiệu Nha Trang, Bên B thuê chỗ ở. Lưu thành cohort riêng, không giả thành phòng trọ tư nhân.')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','2 21 23','handover')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','4','deposit',context=['v2_nhatrang_tdtu_edu_vn_04ae8be4_0017'],reason='Tiền thế chân hoàn khi kết thúc và người thuê không gây mất mát/hư hỏng; kèm Điều 4 giới hạn bồi thường tài sản công do chính người thuê gây ra. Không suy rủi ro từ mức cọc.')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','5','payment',context=['v2_nhatrang_tdtu_edu_vn_04ae8be4_0004'])
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','6 7 8','termination')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','11 12 13 15 16 20','conduct')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','14 24','privacy')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','17','fault')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','18 19 25','payment')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','22','stable_use')
normal('v2_nhatrang_tdtu_edu_vn_04ae8be4','27 28 29','effect')
hold('v2_nhatrang_tdtu_edu_vn_04ae8be4','9 10 26','Cần đọc quy chế/khung kỷ luật được dẫn chiếu và phân định quyền chấm dứt; không suy abnormal chỉ vì có kỷ luật hoặc điều kiện sức khỏe.')

source('v2_attachment_25e68c195f4c','room','Tiêu đề HỢP ĐỒNG THUÊ PHÒNG TRỌ; Bên A cho Bên B thuê 01 phòng ở.')
normal('v2_attachment_25e68c195f4c','3','stable_use')
normal('v2_attachment_25e68c195f4c','4','payment')
normal('v2_attachment_25e68c195f4c','5','fault',reason='Bảo quản trang thiết bị đã giao, làm hỏng phải sửa, mất phải đền; cơ chế diễn đạt gắn hành vi làm hỏng/mất của bên thuê, không miễn mọi trách nhiệm chủ nhà.')
normal('v2_attachment_25e68c195f4c','6','consent')
normal('v2_attachment_25e68c195f4c','7 8','conduct')
normal('v2_attachment_25e68c195f4c','11','termination',reason='Chấm dứt trước hạn đòi hỏi báo trước ít nhất 30 ngày và hai bên thống nhất; không cho chủ nhà tự thu hồi chỉ bằng ý muốn.')
normal('v2_attachment_25e68c195f4c','12','deposit',context=['v2_attachment_25e68c195f4c_0011'])
normal('v2_attachment_25e68c195f4c','13 14','effect')
hold('v2_attachment_25e68c195f4c','9 10','Cần rà phạm vi trách nhiệm hành vi khách và việc chấm dứt vì mọi vi phạm; không tự coi điều kiện báo ở qua đêm là bất lợi.')

source('v2_attachment_6e5afb9b6dda','room','HỢP ĐỒNG CHO THUÊ PHÒNG TRỌ; Bên A chủ trọ, Bên B người thuê trọ; Điều 1 cho thuê một phòng trọ.')
normal('v2_attachment_6e5afb9b6dda','17 28','handover')
normal('v2_attachment_6e5afb9b6dda','24 30','payment')
normal('v2_attachment_6e5afb9b6dda','25','deposit')
normal('v2_attachment_6e5afb9b6dda','27','owner_liability')
normal('v2_attachment_6e5afb9b6dda','29','privacy')
normal('v2_attachment_6e5afb9b6dda','31','consent')
normal('v2_attachment_6e5afb9b6dda','32','conduct')
normal('v2_attachment_6e5afb9b6dda','33 35','effect')
normal('v2_attachment_6e5afb9b6dda','34','dispute')
abnormal('v2_attachment_6e5afb9b6dda_0026','deposit_forfeiture','deposit',
    'Người thuê ngưng trước thời hạn được ghi mất cọc mà không phân biệt lý do, gồm chưa có ngoại lệ khi chủ nhà vi phạm. Đã đọc nhánh chủ nhà phải bồi thường gấp đôi và quyền tranh chấp; đối ứng đó chưa giải quyết ngoại lệ này. Cùng cơ chế với mẫu ACC v1, không khẳng định chấm dứt trước hạn luôn trái luật.',
    'Bên B ngưng hợp đồng trước thời hạn thì phải chịu mất tiền cọc.',
    context=['v2_attachment_6e5afb9b6dda_0027','v2_attachment_6e5afb9b6dda_0034'],confidence='medium')

# The eNha page only previews articles 1-3; the rest is behind its download flow.
# Do not infer an automatic-renewal positive without the missing exit conditions.
hold('v2_enha_vn_3ec5e91c','46','Chỉ có xem trước Điều 1-3, thời gian gia hạn trống và chưa có điều kiện từ chối/chấm dứt ở Điều 4-9; cần nguyên bản đủ ngữ cảnh.')

source('danang_room_docx','room','HỢP ĐỒNG THUÊ NHÀ TRỌ; Điều 1 mô tả căn nhà/căn hộ ở, Điều 4-6 bảo đảm chỗ ở và cư trú, không có mục đích kinh doanh.')
normal('danang_room_docx','18 19 26 52','handover')
normal('danang_room_docx','21 22 33 45','payment')
normal('danang_room_docx','27 32 48 49 50','conduct')
normal('danang_room_docx','28 30 58 62 63 64','stable_use')
normal('danang_room_docx','29 56','owner_repair')
normal('danang_room_docx','31','owner_liability')
normal('danang_room_docx','34','fixed_price',reason='Cải tạo cần người thuê đồng ý, giá mới do hai bên thỏa thuận; khi không thống nhất có nhánh chấm dứt và bồi thường theo pháp luật. Không gán bất lợi chỉ vì có từ điều chỉnh giá.')
normal('danang_room_docx','35 44 75','fault')
normal('danang_room_docx','36 53 54 55 66 76','consent')
normal('danang_room_docx','47 51','return')
normal('danang_room_docx','57','renewal')
normal('danang_room_docx','65','dispute')
normal('danang_room_docx','67 68 69 71 72','termination')
normal('danang_room_docx','70','notice',context=['danang_room_docx_0069'])
normal('danang_room_docx','74 77 78','effect')
hold('danang_room_docx','37 38 39 40 41 42 43 59 60 61 73','Cần gộp các câu dẫn và căn cứ chấm dứt thành đơn vị hoàn chỉnh, bao gồm điều kiện còn trống; chưa dùng các gạch đầu dòng rời làm ground truth.')

source('cochinh_apartment','apartment','Mẫu HỢP ĐỒNG THUÊ CĂN HỘ NHÀ CHUNG CƯ trong tuyển tập; chỉ chọn hợp đồng căn hộ, không chọn thuê mua/kinh doanh của tuyển tập.')
normal('cochinh_apartment','9 10 15 45','payment')
normal('cochinh_apartment','16 46','fault')
normal('cochinh_apartment','17 50','return',context=['cochinh_apartment_0057','cochinh_apartment_0058','cochinh_apartment_0060','cochinh_apartment_0062'])
normal('cochinh_apartment','19 20 21 22 23','termination',context=['cochinh_apartment_0033','cochinh_apartment_0034'])
normal('cochinh_apartment','26','handover',context=['cochinh_apartment_0027'])
normal('cochinh_apartment','28 32 47 49','conduct')
normal('cochinh_apartment','29 40 54 55 56','stable_use')
normal('cochinh_apartment','30 38','owner_liability')
normal('cochinh_apartment','31 37','owner_repair')
normal('cochinh_apartment','33','notice',context=['cochinh_apartment_0019','cochinh_apartment_0020','cochinh_apartment_0021','cochinh_apartment_0022','cochinh_apartment_0023'])
normal('cochinh_apartment','34','owner_liability')
normal('cochinh_apartment','36','handover')
normal('cochinh_apartment','39 48 65','consent')
normal('cochinh_apartment','41 42 43','termination')
normal('cochinh_apartment','51','notice',context=['cochinh_apartment_0041','cochinh_apartment_0042','cochinh_apartment_0043'])
normal('cochinh_apartment','52','fault')
normal('cochinh_apartment','57 58 59 60 61 62','termination')
normal('cochinh_apartment','63','owner_liability')
normal('cochinh_apartment','64 66 69 70','effect')

source('dkrs_full_docx','house','Mẫu HỢP ĐỒNG THUÊ NHÀ Ở, các mục giá/thiết kế/sử dụng nhà ở; không tự coi văn bản pháp lý tham chiếu là nhãn.',role='Bên thuê (định danh theo nguồn); Bên cho thuê (không mặc định A/B)')
normal('dkrs_full_docx','39 40 42 54 78','payment')
normal('dkrs_full_docx','53 61 68','handover')
normal('dkrs_full_docx','55 77','conduct')
normal('dkrs_full_docx','56 79 82','fault')
normal('dkrs_full_docx','57 70 71 81','consent')
normal('dkrs_full_docx','59 80','return')
normal('dkrs_full_docx','62 64 69 72','stable_use')
normal('dkrs_full_docx','63 73','owner_repair')
normal('dkrs_full_docx','65 66 74','owner_liability')
normal('dkrs_full_docx','84','force_majeure')
normal('dkrs_full_docx','88','termination')
hold('dkrs_full_docx','58 75 89 90 91 92','Điều kiện chấm dứt dẫn chiếu luật hoặc thời hạn/biện pháp hậu quả còn trống; cần đủ nội dung trước nhãn, không mặc định normal vì là mẫu pháp lý.')
normal('dkrs_full_docx','94','dispute')
normal('dkrs_full_docx','95 96','effect')
normal('dkrs_full_docx','98 99','consent')

source('homedy_apartment','apartment','Mẫu thuê căn hộ nhà chung cư trong bài Homedy; Điều 2 giá thuê nhà ở, Điều 4-7 ổn định chỗ ở; không lấy phần tư vấn ngoài mẫu.')
normal('homedy_apartment','13 14 19 52','payment')
normal('homedy_apartment','20 53 59','fault')
normal('homedy_apartment','21 57','return',context=['homedy_apartment_0065','homedy_apartment_0066','homedy_apartment_0068','homedy_apartment_0070'])
normal('homedy_apartment','32 43','handover')
normal('homedy_apartment','33 37 54 56','conduct')
normal('homedy_apartment','34 47 61 62 63 64','stable_use')
normal('homedy_apartment','35 39 45 71','owner_liability')
normal('homedy_apartment','36 44','owner_repair')
normal('homedy_apartment','46 55 73','consent')
normal('homedy_apartment','65 66 67 68 69 70','termination')
normal('homedy_apartment','72 74 77 78','effect')
normal('homedy_apartment','76','dispute')
hold('homedy_apartment','23 24 25 26 27 38 48 49 50 58','Cần gộp câu dẫn về căn cứ chấm dứt bị bộ trích giữ như cấu trúc; không lấy các gạch rời để đo chất lượng.')

source('latendoc_house','house','Mẫu hợp đồng nhà ở; Điều 4-5 nói về sinh hoạt/chỗ ở và quyền tiếp tục thuê, Bên B là người thuê.')
normal('latendoc_house','8 21 31','payment')
normal('latendoc_house','9','deposit')
normal('latendoc_house','10 49 51 53 54 55','effect')
normal('latendoc_house','13 37','handover')
normal('latendoc_house','14 17 38 40','stable_use')
normal('latendoc_house','15','notice')
normal('latendoc_house','16','owner_repair')
normal('latendoc_house','18','owner_liability')
normal('latendoc_house','27','fixed_price',reason='Cải tạo phải được người thuê đồng ý; khi không thống nhất giá mới, chủ nhà phải bồi thường theo pháp luật. Không là quyền tăng giá tùy ý trong thời hạn thuê.')
normal('latendoc_house','28 44 47','consent')
normal('latendoc_house','29 35','return')
normal('latendoc_house','30 33','conduct')
normal('latendoc_house','32 36 50','fault')
normal('latendoc_house','39','renewal')
normal('latendoc_house','45','dispute')
hold('latendoc_house','19 20 22 23 24 25 26 41 42 43','Phải đưa câu dẫn và căn cứ/thủ tục chấm dứt vào cùng text trước khi dùng; giữ ngoài bản chính trong vòng này.')

source('v2_rentapartment_lease','apartment','Điều 2.1: mục đích thuê cho nhân viên công ty ở, không sử dụng làm văn phòng. Đơn vị cho thuê đăng mẫu công khai; người thuê có thể là công ty nhưng mục đích cư trú.',role='Bên Thuê/Lessee và Bên Cho Thuê/Lessor theo định nghĩa; không gán A/B')
normal('v2_rentapartment_lease','2 29 30','conduct')
normal('v2_rentapartment_lease','3 18','handover')
normal('v2_rentapartment_lease','5 6 12 14 15 25','payment')
normal('v2_rentapartment_lease','7','fixed_price')
normal('v2_rentapartment_lease','8','deposit',context=['v2_rentapartment_lease_0011','v2_rentapartment_lease_0031','v2_rentapartment_lease_0032','v2_rentapartment_lease_0033','v2_rentapartment_lease_0037'])
normal('v2_rentapartment_lease','10','renewal')
normal('v2_rentapartment_lease','11','termination')
normal('v2_rentapartment_lease','19','stable_use')
normal('v2_rentapartment_lease','20 21','owner_repair')
normal('v2_rentapartment_lease','22','access')
normal('v2_rentapartment_lease','23','privacy')
normal('v2_rentapartment_lease','26','consent')
normal('v2_rentapartment_lease','27','return')
normal('v2_rentapartment_lease','31 32','termination')
normal('v2_rentapartment_lease','33','force_majeure')
normal('v2_rentapartment_lease','36','owner_liability',reason='Khi chủ nhà muốn chấm dứt, phải hoàn cọc, tiền thuê chưa sử dụng và bồi thường hai tháng thuê. Nguồn lặp Bên Cho Thuê ở người nhận thông báo; giữ nguyên lỗi nguyên bản, không tự sửa thành bên khác.')
normal('v2_rentapartment_lease','37','deposit',context=['v2_rentapartment_lease_0011','v2_rentapartment_lease_0031','v2_rentapartment_lease_0032','v2_rentapartment_lease_0033'])
normal('v2_rentapartment_lease','38','dispute')
normal('v2_rentapartment_lease','39','effect')
abnormal('v2_rentapartment_lease_0016','deposit_forfeiture','termination',
    'Chậm thanh toán quá 15 ngày dẫn đến chấm dứt và mất toàn bộ quyền đòi cọc, không gắn phần cọc giữ lại với nợ/thiệt hại quyết toán. Đã đọc khoản phạt chậm trả riêng 5.2.2 và quy định kết thúc 7.1.4; cảnh báo cơ chế tước cọc, không suy bất lợi chỉ vì có chậm thanh toán.',
    'Bên Thuê không có quyền yêu cầu trả lại tiền đã đặt cọc.',
    context=['v2_rentapartment_lease_0015','v2_rentapartment_lease_0034'],confidence='medium')
abnormal('v2_rentapartment_lease_0028','broad_liability','liability',
    'Ngoài lỗi của người thuê, nghĩa vụ trả chi phí còn bao gồm hư hỏng/mất mát do Bên Thứ Ba gây ra khi sử dụng, không giới hạn bên thứ ba là khách do người thuê mời hoặc có lỗi của người thuê. Đã đọc ngoại lệ hỏng tự nhiên và nghĩa vụ sửa phần xây dựng của chủ nhà; chỉ cảnh báo phạm vi trách nhiệm phần tài sản bên trong.',
    'hay do Bên Thứ Ba gây ra',context=['v2_rentapartment_lease_0020'],confidence='medium')
abnormal('v2_rentapartment_lease_0035','deposit_forfeiture','deposit',
    'Người thuê báo trước 30 ngày nhưng vẫn mất cả cọc và toàn bộ tiền thuê trả trước cho thời gian chưa dùng, không gắn số giữ với tổn thất thực tế. Đã đưa ngoại lệ chuyển công tác 4.3 và hoàn cọc/tiền trả trước ở 7.2.3 vào text; các ngoại lệ này không giải quyết trường hợp rời đi do chủ nhà vi phạm.',
    'tiền cọc và phần tiền thuê nhà đã trả trước cho thời gian chưa sử dụng đến (nếu có) sẽ không được hoàn trả lại.',
    context=['v2_rentapartment_lease_0011','v2_rentapartment_lease_0031','v2_rentapartment_lease_0032','v2_rentapartment_lease_0033','v2_rentapartment_lease_0037'],confidence='medium')

source('v2_attachment_abe5864a10af','room','Mẫu HỢP ĐỒNG THUÊ PHÒNG TRỌ của quanlynhatro.vip; 1.2: phòng dùng để ở; các bên A/B được định nghĩa rõ.')
normal('v2_attachment_abe5864a10af','27 29 53 54 56','handover')
normal('v2_attachment_abe5864a10af','28 63','consent')
normal('v2_attachment_abe5864a10af','31','renewal')
normal('v2_attachment_abe5864a10af','34','fixed_price',reason='Đơn giá/cách tính có thể thay đổi nhưng phải thông báo và thống nhất theo thỏa thuận hai bên; không cho chủ nhà tự tăng giá chỉ bằng thông báo.')
normal('v2_attachment_abe5864a10af','51','deposit',reason='Hai bên cùng đối chiếu tiền thuê, chỉ số, hiện trạng và tài sản để xử lý cọc. Không có cơ chế tự định khoản khấu trừ trong đơn vị này; khoản điều kiện khấu trừ trống giữ ngoài nhãn.')
normal('v2_attachment_abe5864a10af','55','fault')
normal('v2_attachment_abe5864a10af','57','access')
normal('v2_attachment_abe5864a10af','58 60','payment')
normal('v2_attachment_abe5864a10af','61 62','conduct')
normal('v2_attachment_abe5864a10af','65 66','owner_repair',reason='Báo sự cố để chủ nhà phản hồi xử lý; chi phí phân định theo nguyên nhân hư hỏng và thỏa thuận được lưu lại, không chuyển tất cả sửa chữa sang người thuê.')
normal('v2_attachment_abe5864a10af','69','return')
normal('v2_attachment_abe5864a10af','71 72','dispute')
normal('v2_attachment_abe5864a10af','73 74 75','effect')
hold('v2_attachment_abe5864a10af','52 68 70','Điều kiện khấu trừ, thời hạn và cách hoàn/trừ cọc còn để trống; không suy bình thường hoặc bất lợi từ phần chưa được điền.')

source('v2_attachment_1ea902e44843','house','HỢP ĐỒNG THUÊ NHÀ TRỌ NGUYÊN CĂN; Điều 2: Bên B thuê nhà để ở. Nhà/phòng dùng ở, không phải thuê mặt bằng kinh doanh.')
normal('v2_attachment_1ea902e44843','29 41 42','consent')
normal('v2_attachment_1ea902e44843','31','handover')
normal('v2_attachment_1ea902e44843','34','fixed_price')
normal('v2_attachment_1ea902e44843','36','deposit')
normal('v2_attachment_1ea902e44843','37','payment')
normal('v2_attachment_1ea902e44843','39','owner_repair')
normal('v2_attachment_1ea902e44843','40','fault',context=['v2_attachment_1ea902e44843_0039'],reason='Người thuê bảo dưỡng/sửa chữa nhỏ và bồi thường khi làm mất/hư hỏng; kèm nghĩa vụ chủ nhà sửa hư hỏng/khuyết tật khác. Đây là phân định cụ thể, không chuyển toàn bộ kết cấu sang người thuê.')
normal('v2_attachment_1ea902e44843','43','stable_use')
normal('v2_attachment_1ea902e44843','44','return')
normal('v2_attachment_1ea902e44843','45','termination')
normal('v2_attachment_1ea902e44843','46','notice')
normal('v2_attachment_1ea902e44843','48','dispute')
normal('v2_attachment_1ea902e44843','49','effect')
hold('v2_attachment_1ea902e44843','47','Phương án xử lý cọc khi người thuê chấm dứt không hợp lệ chưa được điền; không ép label.')

source('nguyenhue_room','room','Mẫu hợp đồng phòng trọ trong tuyển tập Nguyễn Huệ; chỉ chọn các khoản rõ cơ chế và không tăng số từ các bản chép.')
normal('nguyenhue_room','17','fixed_price',reason='Cải tạo phải được bên thuê đồng ý; giá mới do hai bên thỏa thuận, không thống nhất thì có cơ chế bồi thường khi chủ nhà chấm dứt. Không suy abnormal từ tăng giá.')
normal('nguyenhue_room','35','handover')
normal('nguyenhue_room','54','termination')
normal('nguyenhue_room','59','consent')
normal('nguyenhue_room','61','effect')

source('v2_caselaw_tenancy','apartment','Điều 2.3: Mục đích thuê: Để ở. Chỉ phần công khai của mẫu Tenancy Contract, không tải phần yêu cầu tài khoản.')
normal('v2_caselaw_tenancy','66','handover')
normal('v2_caselaw_tenancy','68 82','conduct')
normal('v2_caselaw_tenancy','72 78 80','payment')
normal('v2_caselaw_tenancy','73','fixed_price')
normal('v2_caselaw_tenancy','75','deposit')
normal('v2_caselaw_tenancy','84 89','return')
normal('v2_caselaw_tenancy','86','handover')
normal('v2_caselaw_tenancy','87','stable_use')
normal('v2_caselaw_tenancy','88','privacy',reason='Chủ nhà phối hợp đăng ký chỗ ở với cơ quan địa phương và thủ tục khi người thuê yêu cầu; mục đích thông tin xác định, không là quyền chia sẻ dữ liệu mở.')
normal('v2_caselaw_tenancy','92','consent')
normal('v2_caselaw_tenancy','97 114 117','effect')
normal('v2_caselaw_tenancy','105 106','force_majeure')
normal('v2_caselaw_tenancy','108 109 110 112','termination')
normal('v2_caselaw_tenancy','116','dispute')
hold('v2_caselaw_tenancy','76','Mất cọc có ngoại lệ Điều 12 nhưng phần rút gọn chưa đủ cơ chế không nhận bàn giao do lỗi chủ nhà/điều 11; cần đủ bản, không ép nhãn từ cụm bất kỳ lý do gì.')
hold('v2_caselaw_tenancy','83 90 95 96 99 100 101 102 103 111','Phần rút gọn làm thiếu câu dẫn/ngoại lệ về vi phạm và nghĩa vụ; giữ ngoài corpus được chọn thay vì tự điền nội dung.')

source('v2_replus_room','room','Chỉ phần mẫu hợp đồng thực sự từ Điều 1-8, Điều 1 ghi mục đích để ở; loại toàn bộ phần tư vấn/CTA/FAQ xung quanh.')
normal('v2_replus_room','94','handover')
normal('v2_replus_room','95','renewal')
normal('v2_replus_room','98','owner_repair',reason='Chủ nhà bàn giao, bảo đảm sử dụng, sửa kết cấu/hệ thống chung, tôn trọng phần riêng và hỗ trợ cư trú; không đẩy trách nhiệm không theo lỗi sang người thuê.')
normal('v2_replus_room','99','conduct')
normal('v2_replus_room','101','effect')
hold('v2_replus_room','96 97 100','Mẫu xem trước chưa điền điều kiện hoàn cọc, phí và hậu quả chấm dứt, không suy nhãn từ các chỗ trống.')

# Explicit family links from comparing complete sources; URL/file extensions do
# not make independent templates. These affect leakage groups, not target labels.
FAMILY_OVERRIDES={
    'v2_attachment_6e5afb9b6dda':'room_short_deposit_legacy',
    'bdsdaily_house_pdf':'house_bdsdaily_danang_deposit_notice',
    'danang_house_docx':'house_bdsdaily_danang_deposit_notice',
    'v2_attachment_34cf963d6447':'house_bdsdaily_danang_deposit_notice',
    'danang_house2_docx':'house_old_notary_family',
    'v2_attachment_da8baa7ffa37':'house_old_notary_family',
}
SOURCE_REVIEWS['v2_rentapartment_lease']['publisher_note']='PDF carries a REVER footer and is hosted by RentApartment; public mirrored template, not an authenticated signed transaction.'

source('v2_naue_dorm_contract','student_dormitory','HỢP ĐỒNG Ở TRONG KHU KÝ TÚC XÁ; trường Đại học Nghệ An, sinh viên thuê chỗ ở nội trú. Cohort riêng.',role='Sinh viên nội trú; phía Phòng CTCT HSSV/nhà trường theo nguyên bản, không gán A/B')
normal('v2_naue_dorm_contract','25','handover',context=['v2_naue_dorm_contract_0026'])
normal('v2_naue_dorm_contract','28','return')
normal('v2_naue_dorm_contract','29','conduct',reason='Điều chuyển nơi ở đòi hỏi lý do cần thiết và xác đáng; không ghi quyền chuyển tùy ý không lý do.')
normal('v2_naue_dorm_contract','31 32 33 36 37','termination')
normal('v2_naue_dorm_contract','38','effect')
hold('v2_naue_dorm_contract','27 30 34 35','Cần quy chế nội trú/khung sức khỏe, kỷ luật được dẫn chiếu; không tự gán nhãn cho nội dung chưa đủ phạm vi.')

# Operative lines only; source signatures remain in the immutable original.
BODY_LINE_LIMITS={'v2_nhatrang_tdtu_edu_vn_04ae8be4_0029':2,
    'bdsdaily_house_pdf_0037':2,'v2_attachment_25e68c195f4c_0014':1}

# Reading full assembled text confirms these leads are present (the compact
# reader's heading omitted its lead field). Resolve the extraction concern here;
# never ask the user to fix it or keep valid clauses out for an agent display bug.
for contract,numbers in [('homedy_apartment','23 24 25 26 27 38 48 49 50 58'),
                         ('latendoc_house','22 23 24 25 26 41 42 43'),
                         ('danang_room_docx','59 60 61')]:
    for cid in ids(contract,numbers):HOLDS.pop(cid,None)
normal('homedy_apartment','23 24 25 26 27','termination',context=['homedy_apartment_0038','homedy_apartment_0039'])
normal('homedy_apartment','38','notice',context=['homedy_apartment_0023','homedy_apartment_0024','homedy_apartment_0025','homedy_apartment_0026','homedy_apartment_0027'])
normal('homedy_apartment','48 49 50','termination')
normal('homedy_apartment','58','notice',context=['homedy_apartment_0048','homedy_apartment_0049','homedy_apartment_0050'])
normal('latendoc_house','22 23 24 25 26 41 42 43','termination')
normal('danang_room_docx','59 60 61','termination')

source('v2_attachment_5b18a72e8d9c','room','Mẫu HỢP ĐỒNG THUÊ PHÒNG TRỌ, Điều 1 ghi phòng để ở; tải từ trang mẫu vanban.org qua vb.docstc.com.')
normal('v2_attachment_5b18a72e8d9c','13 29','handover')
normal('v2_attachment_5b18a72e8d9c','28','renewal')
normal('v2_attachment_5b18a72e8d9c','34','deposit')
normal('v2_attachment_5b18a72e8d9c','35 40','payment')
normal('v2_attachment_5b18a72e8d9c','38','owner_repair')
normal('v2_attachment_5b18a72e8d9c','39','privacy')
normal('v2_attachment_5b18a72e8d9c','41','fault',context=['v2_attachment_5b18a72e8d9c_0038'],reason='Bên thuê bảo dưỡng/sửa chữa nhỏ và chịu hậu quả khi làm mất/hỏng; đã đưa nghĩa vụ chủ nhà sửa phần khác vào text, không chuyển toàn bộ sửa chữa sang người thuê.')
normal('v2_attachment_5b18a72e8d9c','42','consent')
normal('v2_attachment_5b18a72e8d9c','43','conduct')
normal('v2_attachment_5b18a72e8d9c','44','return')
normal('v2_attachment_5b18a72e8d9c','48','dispute')
hold('v2_attachment_5b18a72e8d9c','47','Phương án xử lý cọc chưa điền, không suy nhãn.')

source('v2_attachment_1a34375e50f7','room','Mẫu thuê phòng trọ viết tay; khoản 1: thuê phòng để ở, các bên A/B định nghĩa tường minh.')
normal('v2_attachment_1a34375e50f7','6','handover')
normal('v2_attachment_1a34375e50f7','9','deposit')
normal('v2_attachment_1a34375e50f7','10','payment')
normal('v2_attachment_1a34375e50f7','11','notice')
normal('v2_attachment_1a34375e50f7','12','owner_repair',reason='Bản gọn nêu đồng thời nghĩa vụ chủ nhà sửa hỏng trừ hỏng nhỏ, bảo đảm sử dụng và nghĩa vụ bên thuê giữ gìn/không tự cải tạo; có phân định, không gán rủi ro chỉ vì người thuê phải bảo quản.')
normal('v2_attachment_1a34375e50f7','13','dispute')
normal('v2_attachment_1a34375e50f7','14','effect')

source('v2_attachment_5570fbd1079a','room_rules_annex','NỘI QUY PHÒNG TRỌ, tiêu đề ghi Kèm theo Hợp đồng thuê phòng trọ ký ngày...; là mẫu phụ lục, không coi bài hướng dẫn là hợp đồng.')
normal('v2_attachment_5570fbd1079a','4','access',reason='Dù có giờ đóng cổng, người thuê được cấp chìa khóa/mã mở cổng để ra vào; không phải khóa cổng tước quyền sử dụng.')
normal('v2_attachment_5570fbd1079a','8 10','conduct')
normal('v2_attachment_5570fbd1079a','12','conduct',reason='Người thuê tự bảo quản đồ cá nhân; không có cụm miễn mọi trách nhiệm của chủ nhà hoặc bắt gánh lỗi chủ nhà trong đơn vị này.')
normal('v2_attachment_5570fbd1079a','16','consent')
hold('v2_attachment_5570fbd1079a','6 14 18','Một số điều kiện khách/vật nuôi trống hoặc dẫn chiếu xử lý vi phạm vào hợp đồng chính; chưa đủ nhãn cho riêng các dòng này.')

source('v2_attachment_c85f17aff782','house','Mẫu thuê nhà của Luật Minh Khuê; 1.1 ghi để sử dụng làm nơi để ở. Các dòng CTA và phần liên hệ không là mẫu.')
normal('v2_attachment_c85f17aff782','14','handover')
normal('v2_attachment_c85f17aff782','17','owner_liability')

# ALODEV's filled-in example explicitly uses Ví Dụ names/addresses and an example
# data button. It is not imported as a real transaction or counted to meet quotas.
EXCLUDED_SOURCE_NOTES={
    'v2_alodev_vn_b95f3a56':'Filled demonstration with fictional Ví Dụ identity/address fields; not counted as real contract observations.',
    'v2_caselaw_house_ms02':'Purpose blank, permits advertising signage, and public text truncates key deposit/remedy conditions; not selected as residential-risk ground truth.',
    'v2_grandpark_template':'Public preview ends at occupancy fields; complete document download requires login. No guessing URLs or missing clauses.',
    'v2_vinaaccounting_room':'Page is guidance and links to files; guidance sentences are not primary contract examples.',
}

source('v2_cochinh_room_new','room','HỢP ĐỒNG THUÊ PHÒNG TRỌ; khoản 3 chỉ sử dụng phòng vào mục đích ở. Đã đối chiếu trực quan cả hai trang PDF; đây là bản chép mẫu phòng trọ đã có, không phải giao dịch độc lập.')
normal('v2_cochinh_room_new','6','stable_use')
normal('v2_cochinh_room_new','7','privacy')
normal('v2_cochinh_room_new','8','payment')
normal('v2_cochinh_room_new','10','conduct')
normal('v2_cochinh_room_new','11','consent')
abnormal('v2_cochinh_room_new_0009','repair_burden','repair',
    'Khoản 3 buộc bên thuê sửa các hư hỏng trong thời gian sử dụng và cho chủ nhà trừ cọc theo giá thị trường nếu chưa sửa, không phân định nguyên nhân/lỗi hay hao mòn. Đã đọc cả hai trang: trách nhiệm chủ nhà chỉ nêu nhà không tranh chấp và đăng ký, không có ngoại lệ sửa chữa bù lại. Đây là bản chép khoản đã có trong v1, phải khử trùng thay vì tính thành abnormal mới.',
    'Đảm bảo các thiết bị và sửa chữa các hư hỏng trong phòng trong khi sử dụng.',
    context=['v2_cochinh_room_new_0006','v2_cochinh_room_new_0007'],confidence='medium')
hold('v2_cochinh_room_new','12','Quy định báo trước một tháng ở cả hai phía nhưng chưa xác định đầy đủ căn cứ/hậu quả thu hồi nhà; không suy nhãn chỉ từ thời hạn báo.')
