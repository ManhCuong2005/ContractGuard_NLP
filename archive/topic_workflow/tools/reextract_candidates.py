"""Re-extract pending candidates from existing raw files; no downloads or approval."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import read_json, read_rows, write_json, write_rows
from collect_sources import extract_clauses, suggest


def main():
    destination = ROOT/'data/review/clauses.csv'
    old = read_rows(destination)
    if any(r['review_status'] != 'pending' or r['label'] or r['reviewer'] for r in old):
        raise SystemExit('Review work found. Do not replace human review; create a separately reconciled version.')
    sources = read_json(ROOT/'data/sources.json')
    rows = []
    for source in sources:
        if source['document_id'] == 'greenfuture_vehicle_service':
            source['numbered_headings'] = True
        if source['document_id'] == 'moj_business_template':
            source['title'] = 'Bộ Tư pháp — mẫu hợp đồng li-xăng nhãn hiệu'
        clauses = extract_clauses(read_json(ROOT/source['pages_path']), source.get('numbered_headings', False))
        for i, clause in enumerate(clauses, 1):
            label, reason = suggest(clause['text'])
            rows.append({**clause, 'clause_id':f'{source["document_id"]}_{i:04d}',
                         'document_id':source['document_id'], 'group_id':source['group_id'],
                         'source_url':source['source_url'], 'source_sha256':source['source_sha256'],
                         'suggested_label':label, 'suggestion_reason':reason,
                         'label':'', 'review_status':'pending', 'reviewer':'', 'review_notes':''})
        print(f'{source["document_id"]}: {len(clauses)} pending candidates')
    write_rows(destination, rows)
    write_json(ROOT/'data/sources.json', sources)


if __name__ == '__main__':
    main()
