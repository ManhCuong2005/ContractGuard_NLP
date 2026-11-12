"""Recover source-derived pending text after a lossy ANSI/TSV spreadsheet save.

Keep byte-exact backups. Refuse to replace any row with user review work.
"""
from pathlib import Path
import csv
import hashlib
import io
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import FIELDS, read_json, sha256, write_rows
from collect_sources import extract_clauses, suggest


def main():
    path = ROOT/'data/review/clauses.csv'
    raw = path.read_bytes()
    if raw.startswith(b'\xef\xbb\xbf') and b'clause_id,document_id' in raw[:100]:
        raise SystemExit('Already UTF-8 CSV; no recovery needed')
    old = list(csv.DictReader(io.StringIO(raw.decode('cp1252')), delimiter='\t'))
    if len(old) != 967 or any(r['label'] or r['reviewer'] or r['review_notes'] or r['review_status']!='pending' for r in old):
        raise SystemExit('Unexpected content or human review work: manual reconciliation required')
    sources = read_json(ROOT/'data/sources.json')
    rows = []
    for source in sources:
        if sha256(ROOT/source['raw_path']) != source['source_sha256'] or sha256(ROOT/source['pages_path']) != source['pages_sha256']:
            raise SystemExit('Source checksum changed; do not regenerate')
        clauses = extract_clauses(read_json(ROOT/source['pages_path']), source.get('numbered_headings', False))
        for i, clause in enumerate(clauses, 1):
            label, reason = suggest(clause['text'])
            rows.append({**clause, 'clause_id':f'{source["document_id"]}_{i:04d}',
                         'document_id':source['document_id'], 'group_id':source['group_id'],
                         'source_url':source['source_url'], 'source_sha256':source['source_sha256'],
                         'suggested_label':label, 'suggestion_reason':reason,
                         'label':'', 'review_status':'pending', 'reviewer':'', 'review_notes':''})
    if {r['clause_id'] for r in rows} != {r['clause_id'] for r in old}:
        raise SystemExit('Regenerated IDs differ; do not replace')
    backup = ROOT/'data/review/backups'/('before_annotation_'+hashlib.sha256(raw).hexdigest()[:12])
    backup.mkdir(parents=True, exist_ok=True)
    for name in ['clauses.csv', 'review_priority.csv']:
        original = ROOT/'data/review'/name
        (backup/name).write_bytes(original.read_bytes())
    write_rows(path, rows)
    print(f'Restored {len(rows)} source-derived rows to UTF-8 CSV. Original bytes: {backup}')


if __name__ == '__main__':
    main()
