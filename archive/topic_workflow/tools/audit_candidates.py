"""Inspect preliminary corpus. Does not approve rows or fit classifiers."""
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import FIELDS, audit, read_json, read_rows, write_json, write_rows
from contractguard.annotation import ANNOTATION_FIELDS
from contractguard.text import normalize


def main():
    rows = read_rows(ROOT/'data/review/clauses.csv')
    duplicates = defaultdict(list)
    issues = defaultdict(list)
    priority = []
    sources = {s['document_id']:s for s in read_json(ROOT/'data/sources.json')}
    pages = {k:read_json(ROOT/s['pages_path']) for k,s in sources.items()}
    for row in rows:
        key = row['clause_id']
        duplicates[normalize(row['text'])].append(key)
        if not row['suggested_label']:
            issues['ambiguous_or_no_keyword'].append(key)
        if len(row['text']) > 2000:
            issues['long_clause_check_boundary'].append(key)
        if len(row['text']) < 100:
            issues['short_clause_check_context'].append(key)
        if any(w in normalize(row['text']) for w in ['cmnd', 'cccd', 'số tài khoản', 'số điện thoại', 'đại diện bên']):
            issues['possible_identity_or_form'].append(key)
        text = normalize(' '.join(pages[row['document_id']][int(row['page_start'])-1:int(row['page_end'])]))
        if normalize(row['text']) not in text:
            issues['not_contiguous_in_extracted_pages'].append(key)
    dup_groups = [ids for ids in duplicates.values() if len(ids)>1]
    dup_ids = {key for ids in dup_groups for key in ids}
    for key in sorted(dup_ids):
        issues['duplicate_normalized_text'].append(key)
    # Small review queue: sample each suggestion plus each issue and each source.
    selected = set()
    for values in issues.values():
        selected.update(values[:5])
    for label in ['payment','termination','liability','confidentiality','dispute','force_majeure','duration','']:
        selected.update(r['clause_id'] for r in [r for r in rows if r['suggested_label']==label][:4])
    for source_id in sources:
        selected.update(r['clause_id'] for r in [r for r in rows if r['document_id']==source_id][:3])
    for row in rows:
        if row['clause_id'] in selected:
            flags = [name for name, keys in issues.items() if row['clause_id'] in keys]
            priority.append({**row, 'review_flags':','.join(flags)})
    write_rows(ROOT/'data/review/review_priority.csv', priority, FIELDS+ANNOTATION_FIELDS+['review_flags'])
    quality = audit(rows, read_json(ROOT/'configs/labels.json')['labels'])
    write_json(ROOT/'reports/data_quality.json', quality)
    report = {'purpose':'preliminary_data_audit_not_model_evaluation',
              'rows':len(rows), 'sources':len(sources),
              'template_families':len({r['group_id'] for r in rows}),
              'per_source':dict(Counter(r['document_id'] for r in rows)),
              'suggested_counts_not_ground_truth':dict(Counter(r['suggested_label'] or 'unresolved' for r in rows)),
              'duplicate_groups':dup_groups, 'issue_counts':{k:len(v) for k,v in issues.items()},
              'issue_clause_ids':dict(issues), 'priority_rows':len(priority),
              'reviewed_accepted':sum(r['review_status']=='accepted' for r in rows),
              'note':'Rows and suggestions are unreviewed. No official metric or trained model.'}
    write_json(ROOT/'reports/candidate_quality.json', report)
    print({k:v for k,v in report.items() if k not in {'issue_clause_ids', 'duplicate_groups'}})


if __name__ == '__main__':
    main()
