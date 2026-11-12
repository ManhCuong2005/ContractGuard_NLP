"""Explicit source-boundary repairs found while reading the 802 candidates.

This module changes no labels. Each reconstructed statement must be found as
ordered exact source excerpts. Indexes refer to the immutable pre-annotation
snapshot, and added child IDs retain their parent clause ID.
"""
import json
import re
import unicodedata
from copy import deepcopy

from contractguard.provenance import locate_spans
from contractguard.text import normalize


def repair_structure(rows, pages):
    rows = [{**r, 'text': unicodedata.normalize('NFC', r['text'])} for r in rows]
    result = deepcopy(rows)
    changes = []
    extras = []

    def change(index, text, reason, child=None):
        original = rows[index]
        doc = original['document_id']
        start = max(1, int(original['page_start'])-1)
        end = min(len(pages[doc]), int(original['page_end'])+1)
        spans = locate_spans(text, pages[doc], start, end)
        row = {**original, 'text': text, 'source_spans': json.dumps(spans, ensure_ascii=False),
               'page_start': str(min(s['page'] for s in spans)),
               'page_end': str(max(s['page'] for s in spans)),
               'repair_kind': 'risk_annotation_source_boundary_repair',
               'structure_repair_reason': reason, 'snapshot_index': str(index)}
        key = str(index)
        if child:
            key += child
            row['clause_id'] += '_'+child
            row['parent_clause_id'] = original['clause_id']
            extras.append((key, row))
        else:
            result[index] = row
        changes.append({'key': key, 'original_clause_id': original['clause_id'],
                        'result_clause_id': row['clause_id'], 'reason': reason,
                        'before': original['text'], 'after': text, 'source_spans': spans})

    def source_prefix(doc, page, pattern):
        text = normalize(pages[doc][page-1])
        positions = [i for i,c in enumerate(text) if not c.isspace()]
        dense = ''.join(text[i] for i in positions)
        matches = list(re.finditer(pattern.replace(' ', ''), dense))
        if len(matches) != 1:
            raise ValueError(f'Context anchor not unique: {doc} page {page}: {pattern}')
        match = matches[0]
        found = text[positions[match.start()]:positions[match.end()-1]+1]
        return found[0].upper()+found[1:]

    phone = rows[484]['document_id']
    prefix = source_prefix(phone, 5, r'thời hạn chấm dứt hợp đồng đƣợc xác định:')
    for i in [484, 485, 486]:
        body = rows[i]['text'].split(':', 1)[1].strip()
        change(i, prefix+' '+body, 'Replace incorrect termination-ground intro with actual date-setting intro in article 7.2.')

    for i, marker in [(186, 'ĐIỀU 2'), (619, 'PHẦN II.'), (293, 'ĐẠI DIỆN BÊN B')]:
        assert marker in rows[i]['text']
        change(i, rows[i]['text'].split(marker, 1)[0].strip(), 'Remove trailing section heading or signature block, retained in original source.')

    # The business form embedded three operative payment clauses in a checkbox table.
    t = rows[264]['text']
    a, b, c = (t.index(s) for s in ['Phí hòa mạng/Cước lắp đặt', 'Cước thuê bao hàng tháng', 'Lãi suất trong trường hợp'])
    change(264, t[a:b].strip(' -'), 'Extract operative installation-payment sentence from the registration table.')
    change(264, t[b:c].strip(' -'), 'Keep the separate variable due-date clause out of checkbox metadata.', 'b')
    change(264, t[c:].strip(' -'), 'Extract the separate late-interest clause without discarding it.', 'c')

    # Five list items accidentally repeated maintenance and the entire suspension procedure.
    suspend_intro = re.search(r'Bên B có quyền tạm dừng.*?trường hợp sau:', rows[345]['text']).group()
    original = rows[347]['text']
    marker = re.search(r'5\.2\.3\.\s*(Bên B có quyền.*?trường hợp sau:)', original)
    assert marker
    terminate_intro = marker.group(1)
    for i in [347, 348, 349, 352, 353]:
        m = re.search(r'5\.2\.3\.\s*(Bên B có quyền.*?trường hợp sau:)', rows[i]['text'])
        change(i, rows[i]['text'][m.start(1):], 'Retain the correct termination intro and its own list item; stop repeating unrelated maintenance/suspension clauses.')
    a = original.index('5.2.2.')
    change(347, suspend_intro+' '+original[:a].strip(), 'Preserve maintenance ground once, with correct suspension intro.', 'a')
    change(347, original[a+len('5.2.2.'):marker.start()].strip(), 'Preserve the shared notice/no-fee suspension procedure as its own clause once.', 'b')
    change(346, suspend_intro+' '+rows[346]['text'], 'Restore suspension subject for authority/force-majeure list item.')
    change(351, terminate_intro+' '+rows[351]['text'], 'Restore termination subject for authority/force-majeure list item.')
    t = rows[354]['text']
    a = t.index('5.2.4.')
    change(354, terminate_intro+' '+t[:a].strip(), 'Separate the objective technical-impossibility termination ground from settlement obligations.')
    change(354, t[a+len('5.2.4.'):].strip(), 'Keep settlement obligations, including return of unused prepaid money, separately.', 'b')

    # Printed footnotes interrupted a sentence describing default package conversion.
    t = rows[365]['text']
    a, b, c = (t.index(s) for s in ['2 Đối với các nội dung để trống', '3 Tên gói Dịch Vụ', '(là gói dịch vụ bao gồm'])
    change(365, t[:a].strip()+' '+t[c:].strip(), 'Reconnect the conversion sentence over two printed footnotes without paraphrasing.')
    change(365, t[a+2:b].strip(), 'Retain the bilateral agreement requirement for blank form fields separately.', 'b')
    change(365, t[b+2:c].strip(), 'Retain the package-name publication note separately.', 'c')

    doc = rows[65]['document_id']
    prefix = source_prefix(doc, 9, r'dữ liệu cá nhân được xử lý gồm.*?như sau:')
    for i in [65, 66]:
        change(i, prefix+' '+rows[i]['text'], 'Restore data-processing scope intro for a dependent list item.')
    prefix = source_prefix(doc, 12, r'viettel thực hiện ngừng xử lý dữ liệu cá nhân.*?trường hợp sau đây:')
    for i in [102, 103]:
        change(i, prefix+' '+rows[i]['text'], 'Restore cessation-of-processing intro: withdrawing consent is a stop condition, not permission to continue.')
    # Wrong marketing heading had been prepended to the next independent purpose.
    t = rows[97]['text']
    change(97, t.split(':', 1)[1].strip(), 'Remove preceding marketing-list intro incorrectly attached to the separate market-research purpose.')
    prefix = source_prefix(doc, 14, r'khi quý khách chấm dứt.*?một số trường hợp không thể thực hiện được như sau:')
    for i in range(117, 125):
        change(i, prefix+' '+rows[i]['text'], 'Restore the deletion-exception predicate so retention exceptions cannot be learned as harmless isolated noun phrases.')
    prefix = source_prefix(doc, 15, r'trong trường hợp khách hàng không đồng ý.*?khách hàng có thể sẽ:')
    for i in range(135, 141):
        change(i, prefix+' '+rows[i]['text'], 'Restore conditional context for listed consequences of declining processing.')
    return [(str(i), row) for i, row in enumerate(result)] + extras, changes
