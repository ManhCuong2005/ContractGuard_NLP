"""Local parser tests only; never download from the test suite."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('collection', Path(__file__).resolve().parents[1]/'tools/collect_sources.py')
collection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collection)


def test_suggestion_never_resolves_ambiguous_multitopic():
    label, reason = collection.suggest('Khi chấm dứt hợp đồng phải thanh toán cước phí.')
    assert label == ''
    assert 'payment' in reason and 'termination' in reason


def test_single_keyword_is_only_suggestion():
    assert collection.suggest('Các bên có nghĩa vụ bảo mật dữ liệu.')[0] == 'confidentiality'
    assert collection.suggest('Thiết bị được giao tại kho của bên mua.')[0] == ''


def test_clause_boundaries_page_range_and_heading_excluded():
    pages = ['Tên cá nhân cần loại\nĐIỀU 1: TEST\n1.1. fixture orange fruit\ncontinued basket',
             'continuation test fixture\n1.2. unrelated fixture second paragraph with enough words.']
    clauses = collection.extract_clauses(pages)
    assert len(clauses) == 2
    assert clauses[0]['page_start'] == 1 and clauses[0]['page_end'] == 2
    assert 'ĐIỀU' not in clauses[0]['text']
    assert 'cá nhân' not in clauses[0]['text']
    assert clauses[1]['page_start'] == 2


def test_numbered_headings_and_inline_cross_reference():
    pages = ['1. PHẠM VI\n1.1. fixture orange fruit basket with enough words here.\n'
             'Điều 4.4, đây chỉ là dẫn chiếu trong cùng khoản của hợp đồng.\n'
             '2.\nBẢO MẬT\n2.1. fixture private fruit basket with enough words here.']
    clauses = collection.extract_clauses(pages, numbered_headings=True)
    assert len(clauses) == 2
    assert 'Điều 4.4' in clauses[0]['text']
    assert clauses[1]['heading'] == '2. BẢO MẬT'
    assert 'BẢO MẬT' not in clauses[1]['text']


def test_append_uses_staging_and_preserves_canonical_and_history(tmp_path, monkeypatch):
    from contractguard.dataset import write_json
    (tmp_path/'data/review').mkdir(parents=True)
    (tmp_path/'configs').mkdir()
    canonical = tmp_path/'data/clauses.csv'
    historical = tmp_path/'data/review/clauses.csv'
    canonical.write_bytes(b'canonical risk annotation must be preserved')
    historical.write_bytes(b'historical repair evidence must be preserved')
    write_json(tmp_path/'data/sources.json', [{'document_id':'already_downloaded'}])
    write_json(tmp_path/'configs/collection_sources.json', [{'document_id':'already_downloaded'}])
    def forbidden(*args, **kwargs):
        raise AssertionError('Already collected source must not be downloaded again')
    monkeypatch.setattr(collection, 'ROOT', tmp_path)
    monkeypatch.setattr('sys.argv', ['collect_sources.py', '--append'])
    monkeypatch.setattr('requests.get', forbidden)
    assert collection.main() == 0
    assert canonical.read_bytes() == b'canonical risk annotation must be preserved'
    assert historical.read_bytes() == b'historical repair evidence must be preserved'
    assert (tmp_path/'data/candidates.csv').is_file()
