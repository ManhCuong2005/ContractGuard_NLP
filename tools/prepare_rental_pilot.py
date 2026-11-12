"""Apply explicit agent pilot decisions to exact source excerpts, never to official data."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from contractguard.dataset import read_json, read_rows, sha256, write_json, write_rows
from contractguard.provenance import locate_spans, verify_clause_spans


def main() -> None:
    folder = ROOT / 'data/rental_staging'
    destination = folder / 'pilot.csv'
    if destination.exists():
        raise ValueError('Pilot exists; preserve prior annotation work')
    approval = read_json(ROOT / 'configs/rental_approval.json')
    rubric = ROOT / 'docs/LABELING_GUIDELINES.md'
    if approval.get('criteria_approved') is not True or approval.get('criteria_sha256') != sha256(rubric):
        raise ValueError('Approved rental criteria version required')
    source = read_json(folder / 'sources.json')[0]
    if sha256(ROOT / source['raw_path']) != source['source_sha256']:
        raise ValueError('Source hash changed')
    if sha256(ROOT / source['pages_path']) != source['pages_sha256']:
        raise ValueError('Extracted source hash changed')
    pages = read_json(ROOT / source['pages_path'])
    candidates = read_rows(folder / 'candidates.csv')
    articles = {int(r['clause_id'].rsplit('_', 1)[1]): r for r in candidates}
    rows = []
    for note in read_json(ROOT / 'configs/rental_pilot_notes.json'):
        article = articles[note['article']]
        lines = article['text'].splitlines()
        section = None
        parent = None
        matches = []
        for line in lines[1:]:
            match = re.match(r'^(\d+)\.\s', line)
            if match:
                section, parent = int(match.group(1)), line
            if line.startswith(note['prefix']) and (note['section'] is None or section == note['section']):
                matches.append((parent, line))
        if len(matches) != 1:
            raise ValueError(f'Ambiguous/missing source subclause: {note["id"]}')
        parent, excerpt = matches[0]
        pieces = [lines[0]] + ([parent] if note['section'] is not None else []) + [excerpt]
        text = '\n'.join(pieces)
        row = {**article, 'clause_id': f'{source["document_id"]}_pilot_{note["id"]}',
               'parent_clause_id': article['clause_id'], 'text': text, 'source_text': text,
               'source_spans': json.dumps(locate_spans(text, pages)),
               'label': note['label'], 'annotation_reason': note['reason'],
               'annotation_status': 'draft', 'annotation_method': 'explicit_agent_pilot_decision',
               'annotation_by': 'Codex — nhãn sơ bộ, chưa được người dùng duyệt',
               'label_confidence': 'high', 'clause_type': note['clause_type'], 'risk_category': '',
               'annotation_criteria_sha256': sha256(rubric), 'risk_evidence': '',
               'context_clause_ids': '[]', 'text_repairs': '[]'}
        verify_clause_spans(row, pages)
        rows.append(row)
    write_rows(destination, rows, list(rows[0]))
    write_json(folder / 'pilot_audit.json', {
        'purpose': 'rental_seed_pilot_not_training_dataset_or_model_evaluation',
        'criteria_sha256': sha256(rubric), 'pilot_sha256': sha256(destination),
        'sources': 1, 'template_families': 1, 'whole_article_candidates': len(candidates),
        'pilot_rows': len(rows), 'draft_label_counts': {'normal': len(rows), 'abnormal': 0},
        'clauses_source_verified': len(rows), 'dataset_approved': False,
        'official_training_performed': False, 'official_metrics': None,
        'limitations': ['Deliberately selected self-contained normal examples; not a representative sample.',
                        'No verified rental abnormal examples yet; do not train or claim risk detection quality.',
                        'All twelve original articles remain in candidates.csv; unselected content is not discarded.',
                        'Source use remains pending; no permission inferred from criteria confirmation.'],
    })
    print(f'Rental pilot: {len(rows)} draft normal examples, zero abnormal; source spans verified; not approved')


if __name__ == '__main__':
    main()
