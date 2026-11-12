"""Source repair must preserve exact content and cannot grant approval."""
import json
from pathlib import Path

import pytest

from contractguard.dataset import read_json, read_rows
from contractguard.provenance import locate_spans, verify_spans


def test_ordered_spans_restore_clause_over_page_footer():
    pages=['Bên mua phải thanh toán khoản phí. CHÂN TRANG', 'Theo đúng thời hạn được thỏa thuận.']
    text='Bên mua phải thanh toán khoản phí. Theo đúng thời hạn được thỏa thuận.'
    spans=locate_spans(text,pages)
    assert verify_spans(text,pages,spans)==spans
    assert {s['page'] for s in spans}=={1,2}


def test_original_intro_can_be_joined_to_later_list_item():
    pages=['Hợp đồng chấm dứt khi: a) Hai bên đồng ý. b) Một bên bị giải thể.']
    text='Hợp đồng chấm dứt khi: Một bên bị giải thể.'
    assert len(locate_spans(text,pages))==2


def test_paraphrase_is_rejected():
    with pytest.raises(ValueError):
        locate_spans('Bên mua phải trả thêm năm triệu đồng.',['Bên mua phải thanh toán khoản phí.'])


def test_reordered_source_content_is_rejected():
    pages=['Bên mua trả phí. Bên bán giao hàng.']
    spans=[{'page':1,'start':16,'end':32},{'page':1,'start':0,'end':15}]
    with pytest.raises(ValueError,match='ordered'):
        verify_spans('Bên bán giao hàng. Bên mua trả phí.',pages,spans)


def test_modified_excerpt_is_rejected():
    with pytest.raises(ValueError,match='differs'):
        verify_spans('Không thanh toán phí.',['Phải thanh toán phí.'],[{'page':1,'start':0,'end':20}])


def test_prepared_v2_exact_sources_no_pending_agent_work():
    root=Path(__file__).resolve().parents[1]
    rows=read_rows(root/'data/review/v2/clauses.csv')
    sources={s['document_id']:s for s in read_json(root/'data/sources.json')}
    pages={doc:read_json(root/source['pages_path']) for doc,source in sources.items()}
    assert rows and len(rows)==len({r['clause_id'] for r in rows})
    assert not read_json(root/'reports/agent_repair_worklist.json')
    for row in rows:
        spans=verify_spans(row['text'],pages[row['document_id']],row['source_spans'])
        assert min(s['page'] for s in spans)==int(row['page_start'])
        assert max(s['page'] for s in spans)==int(row['page_end'])
        assert row['label'] and row['review_status']=='pending' and not row['reviewer']
    originals={r['clause_id'] for r in read_rows(root/'data/review/clauses.csv')}
    ledger=read_json(root/'reports/repair_ledger.json')
    assert {r['legacy_clause_id'] for r in ledger}==originals


def test_short_complete_clause_is_not_discarded_by_extractor():
    import importlib.util
    root=Path(__file__).resolve().parents[1]
    spec=importlib.util.spec_from_file_location('collection_v2',root/'tools/collect_sources.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result=module.extract_clauses(['ĐIỀU 1: BẢO MẬT\n1.1. Không được tiết lộ thông tin.'])
    assert len(result)==1 and result[0]['text']=='Không được tiết lộ thông tin.'
