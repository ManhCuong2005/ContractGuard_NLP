"""Summarize draft data and split coverage without fitting or approving anything."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from contractguard.dataset import leakage_groups, read_json, read_rows, sha256, write_json
from contractguard.training import split_rows


def summarize(dataset: Path) -> dict:
    rows = read_rows(dataset)
    if not rows:
        raise ValueError('Dataset is empty')
    labels = read_json(ROOT / 'configs/labels.json')['labels']
    sources = read_json(ROOT / 'data/sources.json')
    groups = leakage_groups(rows)
    categories = sorted({c for r in rows for c in r.get('risk_category', '').split(',') if c})
    risk_support = {}
    for category in categories:
        indices = [i for i, row in enumerate(rows)
                   if row['label'] == 'abnormal' and category in row['risk_category'].split(',')]
        risk_support[category] = {
            'clauses': len(indices),
            'leakage_groups': len({groups[i] for i in indices}),
            'documents': sorted({rows[i]['document_id'] for i in indices}),
        }
    preflight = {'purpose': 'draft_split_coverage_only_not_model_evaluation'}
    try:
        partitions, _, seed = split_rows(rows, labels, seed=42)
        preflight.update(feasible=True, requested_seed=42, effective_seed=seed, partitions={})
        for name, indices in partitions.items():
            counts = Counter(rows[i]['label'] for i in indices)
            covered = sorted({c for i in indices if rows[i]['label'] == 'abnormal'
                              for c in rows[i]['risk_category'].split(',') if c})
            support = counts.get('abnormal', 0)
            preflight['partitions'][name] = {
                'rows': len(indices), 'label_counts': dict(counts),
                'documents': sorted({rows[i]['document_id'] for i in indices}),
                'leakage_groups': len({groups[i] for i in indices}),
                'risk_categories_present': covered,
                'risk_categories_absent': sorted(set(categories) - set(covered)),
                'abnormal_recall_resolution_percentage_points': 100 / support if support else None,
            }
    except ValueError as exc:
        preflight.update(feasible=False, reason=str(exc))
    approval = read_json(ROOT / 'configs/approval.json')
    return {
        'purpose': 'draft_progress_audit_not_label_validation_or_model_quality',
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'dataset_sha256': sha256(dataset),
        'approval_sha256': sha256(ROOT / 'configs/approval.json'),
        'criteria_sha256': sha256(ROOT / 'docs/ANNOTATION_GUIDELINES.md'),
        'rows': len(rows), 'draft_label_counts': dict(Counter(r['label'] for r in rows)),
        'review_status_counts': dict(Counter(r['review_status'] for r in rows)),
        'annotation_status_counts': dict(Counter(r.get('annotation_status') for r in rows)),
        'abnormal_fraction': sum(r['label'] == 'abnormal' for r in rows) / len(rows),
        'draft_majority_label_share': max(Counter(r['label'] for r in rows).values()) / len(rows),
        'documents': len({r['document_id'] for r in rows}),
        'template_families': len({r['group_id'] for r in rows}),
        'leakage_groups': len(set(groups)),
        'per_source': [{
            'document_id': s['document_id'], 'title': s['title'],
            'label_counts': dict(Counter(r['label'] for r in rows if r['document_id'] == s['document_id'])),
            'source_use_status': s.get('source_use_status'),
        } for s in sources],
        'risk_category_support': risk_support,
        'rows_with_context_references': sum(bool(json.loads(r.get('context_clause_ids', '[]'))) for r in rows),
        'abnormal_rows_with_context_references': sum(
            r['label'] == 'abnormal' and bool(json.loads(r.get('context_clause_ids', '[]'))) for r in rows),
        'context_note': 'A reference records annotation context; it does not prove that context is essential for every label. The classifier currently receives text only.',
        'draft_partition_preflight': preflight,
        'approval_flags': {k: approval.get(k) for k in
                           ['criteria_approved', 'dataset_approved', 'source_use_confirmed']},
        'official_training_performed': False, 'official_metrics': None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'data/clauses.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/progress_audit.json')
    args = parser.parse_args()
    protected = [args.data, ROOT / 'configs/approval.json', ROOT / 'data/sources.json',
                 ROOT / 'docs/ANNOTATION_GUIDELINES.md', ROOT / 'configs/labels.json']
    if args.output.resolve() in {p.resolve() for p in protected} or args.output.exists():
        raise ValueError('Choose a new report path; existing files and protected inputs are preserved')
    before = {p: sha256(p) for p in protected}
    result = summarize(args.data)
    if before != {p: sha256(p) for p in protected}:
        raise RuntimeError('Protected inputs changed during audit; rerun on a stable dataset')
    result['protected_inputs_unchanged'] = True
    write_json(args.output, result)
    print(f'Draft progress audit: {len(result["per_source"])} sources, {result["rows"]} rows; {args.output}')


if __name__ == '__main__':
    main()
