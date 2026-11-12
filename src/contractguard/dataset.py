"""CSV review, provenance checks, and the explicit human approval gate."""
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from .text import normalize, require_text, shingles

FIELDS = ['clause_id', 'document_id', 'group_id', 'source_url', 'source_sha256',
          'page_start', 'page_end', 'heading', 'text', 'suggested_label',
          'suggestion_reason', 'label', 'review_status', 'reviewer', 'review_notes']
REQUIRED_FIELDS = [field for field in FIELDS if field not in {'suggested_label','suggestion_reason'}]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        missing = set(REQUIRED_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'Missing CSV columns: {sorted(missing)}')
        return [{k: (v or '').strip() for k, v in row.items() if k} for row in reader]


def write_rows(path, rows, fields=FIELDS):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def audit(rows, labels):
    errors = []
    ids = set()
    texts = {}
    for i, row in enumerate(rows, 2):
        key = row.get('clause_id', '')
        if not key or key in ids:
            errors.append(f'line {i}: empty or duplicate clause_id {key}')
        ids.add(key)
        status = row.get('review_status')
        if status not in {'pending', 'accepted', 'rejected'}:
            errors.append(f'{key}: invalid review_status')
        if status in {'accepted', 'rejected'} and not row.get('reviewer'):
            errors.append(f'{key}: missing reviewer')
        if status == 'rejected' and not row.get('review_notes'):
            errors.append(f'{key}: rejected row needs a reason')
        if row.get('label') and row['label'] not in labels and status != 'accepted':
            errors.append(f'{key}: unknown draft label')
        if status != 'accepted':
            continue
        try:
            text = require_text(row['text'])
        except ValueError as e:
            errors.append(f'{key}: {e}')
            continue
        if row.get('label') not in labels:
            errors.append(f'{key}: unknown/empty human label')
        for field in ['document_id', 'group_id', 'source_sha256']:
            if not row.get(field):
                errors.append(f'{key}: missing {field}')
        if urlparse(row.get('source_url', '')).scheme != 'https':
            errors.append(f'{key}: source_url must be HTTPS')
        if text in texts:
            errors.append(f'{key}: duplicate normalized text with {texts[text]} (resolve before training)')
        texts[text] = key
    accepted = [r for r in rows if r.get('review_status') == 'accepted']
    return {'rows': len(rows), 'status_counts': dict(Counter(r.get('review_status') for r in rows)),
            'unlabeled_rows':sum(not r.get('label') for r in rows),
            'suggested_counts': dict(Counter(r.get('suggested_label') for r in rows if 'suggested_label' in r)),
            'label_counts': dict(Counter(r.get('label') for r in accepted)),
            'draft_label_counts': dict(Counter(r.get('label') for r in rows
                if r.get('annotation_status') == 'draft' and r.get('proposed_action') != 'exclude' and r.get('label'))),
            'proposed_action_counts': dict(Counter(r.get('proposed_action') for r in rows if r.get('proposed_action'))),
            'accepted_documents': len({r.get('document_id') for r in accepted}),
            'accepted_groups': len({r.get('group_id') for r in accepted}), 'errors': errors}


def _safe_source(root, relative):
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f'Invalid provenance file: {relative}')
    return target


def audit_provenance(rows, sources_path, root):
    """Validate pending clauses too; source integrity is independent of approval."""
    root = Path(root)
    sources = read_json(sources_path)
    errors, pages_by_id = [], {}
    by_id = {}
    for source in sources:
        doc = source['document_id']
        if doc in by_id:
            errors.append(f'{doc}: duplicate source document_id')
        by_id[doc] = source
        try:
            raw = _safe_source(root, source['raw_path'])
            pages_path = _safe_source(root, source['pages_path'])
            if sha256(raw) != source['source_sha256'] or sha256(pages_path) != source['pages_sha256']:
                raise ValueError('Source file changed since collection')
            pages = read_json(pages_path)
            if not isinstance(pages, list) or not pages or any(not isinstance(p, str) for p in pages):
                raise ValueError('Source pages must be a nonempty array of strings')
            if source.get('page_count', len(pages)) != len(pages):
                raise ValueError('Source page_count mismatch')
            pages_by_id[doc] = pages
        except (ValueError, OSError, KeyError) as exc:
            errors.append(f'{doc}: {exc}')
    checked = 0
    for row in rows:
        key, doc = row.get('clause_id', ''), row.get('document_id', '')
        try:
            require_text(row['text'])
            if doc not in by_id:
                raise ValueError(f'Unknown source: {doc}')
            source = by_id[doc]
            if any(row.get(k) != source.get(k) for k in ['source_url', 'source_sha256', 'group_id']):
                raise ValueError('Row provenance differs from source manifest')
            if urlparse(row.get('source_url', '')).scheme != 'https':
                raise ValueError('source_url must be HTTPS')
            if doc not in pages_by_id:
                continue  # The source-level error is already recorded.
            pages = pages_by_id[doc]
            start, end = int(row['page_start']), int(row['page_end'])
            if not 1 <= start <= end <= len(pages):
                raise ValueError('Invalid source page range')
            if row.get('source_spans'):
                from .provenance import verify_clause_spans
                spans = verify_clause_spans(row, pages)
                if row.get('text_repair_reference'):
                    ref = json.loads(row['text_repair_reference'])
                    reference_path = _safe_source(root, ref['path'])
                    if sha256(reference_path) != ref['sha256']:
                        raise ValueError('Text repair reference hash changed')
                    reference = read_json(reference_path)
                    if reference.get('source_sha256') != row['source_sha256']:
                        raise ValueError('Text repair reference is from another source')
                if min(s['page'] for s in spans) != start or max(s['page'] for s in spans) != end:
                    raise ValueError('Declared page range differs from source span pages')
            elif normalize(row['text']) not in normalize(' '.join(pages[start-1:end])):
                raise ValueError('Clause not found verbatim in source pages')
            checked += 1
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            errors.append(f'{key}: {exc}')
    return {'sources': len(sources), 'clauses_verified': checked, 'errors': errors}


def audit_dataset(dataset, labels_path, sources_path, root):
    rows = read_rows(dataset)
    config = read_json(labels_path)
    result = audit(rows, config['labels'])
    provenance = audit_provenance(rows, sources_path, root)
    result['provenance'] = provenance
    result['errors'].extend(provenance['errors'])
    seen = {}
    for row in rows:
        if config.get('task') == 'contract_anomaly_detection':
            key = row['clause_id']
            if row.get('task') != config['task']:
                result['errors'].append(f'{key}: row task differs from configured risk task')
            if row.get('label'):
                if not row.get('annotation_reason'):
                    result['errors'].append(f'{key}: risk label needs annotation_reason')
                if row.get('annotation_status') not in {'draft', 'reviewed'}:
                    result['errors'].append(f'{key}: populated label must be draft or reviewed')
                if row['label'] == 'abnormal' and not row.get('risk_category'):
                    result['errors'].append(f'{key}: abnormal needs a risk_category')
        text = normalize(row['text'])
        if text in seen:
            result['errors'].append(f"{row['clause_id']}: duplicate normalized text with {seen[text]}")
        seen[text] = row['clause_id']
    result['dataset_sha256'] = sha256(dataset)
    result['note'] = 'Integrity audit only; a pass does not approve labels or authorize training.'
    return result


def training_readiness(root, dataset, profile='legacy'):
    """Read-only preflight; never changes approval or fits a model."""
    root, dataset = Path(root), Path(dataset)
    from .profiles import profile_paths
    paths=profile_paths(root,profile)
    result = audit_dataset(dataset, paths['labels'], paths['sources'], root)
    approval = read_json(paths['approval'])
    blockers = list(result['errors'])
    for flag in ['criteria_approved', 'dataset_approved', 'source_use_confirmed']:
        if approval.get(flag) is not True:
            blockers.append(f'Human approval required: {flag}')
    if result['unlabeled_rows']:
        blockers.append(f"Unlabeled clauses: {result['unlabeled_rows']}")
    if result['status_counts'].get('pending'):
        blockers.append(f"Pending human review: {result['status_counts']['pending']}")
    # Include the actual provenance/hash gate and split feasibility, without fitting.
    independent = {}
    rows = read_rows(dataset)
    groups = leakage_groups(rows)
    result['candidate_documents'] = len({r['document_id'] for r in rows})
    result['candidate_template_families'] = len({r['group_id'] for r in rows})
    result['candidate_leakage_groups'] = len(set(groups))
    if not blockers:
        try:
            rows, labels, _ = require_approval(dataset, paths['approval'],paths['rubric'],paths['labels'],paths['sources'],root)
            if profile=='rental':
                from .rental_split import balanced_split_rows as splitter
            else:
                from .training import split_rows as splitter
            split, groups, _ = splitter(rows, labels)
            result['split_counts']={name:dict(Counter(rows[i]['label'] for i in idx)) for name,idx in split.items()}
            independent = {label: len({groups[i] for i, r in enumerate(rows) if r['label'] == label})
                           for label in labels}
        except ValueError as exc:
            blockers.append(str(exc))
    return {**result, 'official_training_ready': not blockers, 'blockers': blockers,
            'independent_groups_by_label': independent, 'official_metrics': None}


def require_approval(dataset, approval, rubric, labels_path, sources_path, root):
    """No official fit or output creation before this succeeds."""
    a = read_json(approval)
    for field in ['criteria_approved', 'dataset_approved', 'source_use_confirmed']:
        if a.get(field) is not True:
            raise ValueError(f'Human approval required: {field}; official training is locked')
    if not a.get('approved_by', '').strip() or not a.get('approved_at'):
        raise ValueError('Approval must name the human reviewer and timestamp')
    try:
        timestamp = datetime.fromisoformat(a['approved_at'])
        if timestamp.tzinfo is None:
            raise ValueError('Approval timestamp requires a timezone')
    except (TypeError, ValueError) as e:
        raise ValueError('Invalid approved_at ISO timestamp') from e
    for field, path in [('dataset_sha256', dataset), ('criteria_sha256', rubric),
                        ('labels_sha256', labels_path), ('sources_sha256', sources_path)]:
        if a.get(field) != sha256(path):
            raise ValueError(f'Approval digest mismatch: {field}; review changed files again')
    config = read_json(labels_path)
    labels = config['labels']
    if config.get('task') and a.get('scope') != config['task']:
        raise ValueError('Approval scope differs from configured task')
    if config.get('domain') and a.get('domain')!=config['domain']:
        raise ValueError('Approval domain differs from configured domain')
    if a.get('dataset_confirmation_record'):
        record_path=_safe_source(Path(root),a['dataset_confirmation_record'])
        if sha256(record_path)!=a.get('approval_record_sha256'):
            raise ValueError('Human confirmation record changed')
    rows = read_rows(dataset)
    quality = audit(rows, labels)
    if quality['errors'] or quality['status_counts'].get('pending', 0):
        raise ValueError(f'Dataset not fully reviewed: {quality}')
    accepted = [r for r in rows if r['review_status'] == 'accepted']
    if config.get('task') == 'contract_anomaly_detection':
        for row in accepted:
            if config.get('domain') and (row.get('domain')!=config['domain'] or
                    row.get('protected_party')!=config.get('protected_party') or
                    row.get('dataset_role')!='primary_residential_rental'):
                raise ValueError('Accepted row is outside the rental domain/role')
            if config.get('domain') and row.get('annotation_criteria_sha256')!=a['criteria_sha256']:
                raise ValueError('Row annotation criteria version differs from approval')
            if row.get('task') != config['task'] or not row.get('annotation_reason'):
                raise ValueError(f"{row['clause_id']}: risk task and annotation_reason required")
            if row.get('annotation_status') != 'reviewed':
                raise ValueError(f"{row['clause_id']}: annotation_status must be reviewed after human acceptance")
            if row['label'] == 'abnormal' and not row.get('risk_category'):
                raise ValueError(f"{row['clause_id']}: abnormal needs a risk_category")
    if set(r['label'] for r in accepted) != set(labels):
        raise ValueError('Every configured label needs accepted real examples')
    sources = {s['document_id']: s for s in read_json(sources_path)}
    for row in accepted:
        source = sources.get(row['document_id'])
        if not source or source['document_id'] not in a.get('reviewed_source_ids', []):
            raise ValueError(f'Unreviewed source: {row["document_id"]}')
        if source.get('data_kind') != 'public_contract_template':
            raise ValueError('Only reviewed public contract templates allowed in this dataset version')
        if source.get('transcription_proof_path'):
            proof_path=_safe_source(Path(root),source['transcription_proof_path'])
            if sha256(proof_path)!=source.get('transcription_proof_sha256'):
                raise ValueError('Scanned-source transcription proof changed')
            proof=read_json(proof_path)
            if proof['source_sha256']!=source['source_sha256'] or proof['pages_sha256']!=source['pages_sha256']:
                raise ValueError('Scanned-source proof belongs to different raw/pages')
            for render in proof['rendered_pages']:
                if sha256(_safe_source(Path(root),render['image_path']))!=render['sha256']:
                    raise ValueError('Scanned-source render changed')
        if any(row[k] != source[k] for k in ['source_url', 'source_sha256', 'group_id']):
            raise ValueError('Row provenance differs from source manifest')
        raw = _safe_source(Path(root), source['raw_path'])
        pages_file = _safe_source(Path(root), source['pages_path'])
        if sha256(raw) != source['source_sha256'] or sha256(pages_file) != source['pages_sha256']:
            raise ValueError('Source file changed since collection')
        pages = read_json(pages_file)
        start, end = int(row['page_start']), int(row['page_end'])
        if not 1 <= start <= end <= len(pages):
            raise ValueError('Invalid source page range')
        if row.get('source_spans'):
            from .provenance import verify_clause_spans
            spans = verify_clause_spans(row, pages)
            if min(s['page'] for s in spans) != start or max(s['page'] for s in spans) != end:
                raise ValueError('Declared page range differs from source span pages')
        elif normalize(row['text']) not in normalize(' '.join(pages[start-1:end])):
            raise ValueError(f'Clause not found verbatim in source pages: {row["clause_id"]}')
    source_quality = audit_provenance(accepted, sources_path, root)
    if source_quality['errors']:
        raise ValueError(f'Source integrity failed: {source_quality["errors"][:10]}')
    return accepted, labels, a


def leakage_groups(rows, threshold=0.85):
    """Join template families and near duplicate clauses into indivisible groups."""
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(j)] = find(i)

    families = {}
    documents = {}
    for i, r in enumerate(rows):
        for mapping, key in [(families, r['group_id']), (documents, r['document_id'])]:
            if key in mapping:
                union(i, mapping[key])
            mapping[key] = i
    grams = [shingles(r['text']) for r in rows]
    for i in range(len(rows)):
        for j in range(i):
            if find(i) == find(j):
                continue
            a, b = grams[i], grams[j]
            if a and b and len(a & b) / len(a | b) >= threshold:
                union(i, j)
    return [str(find(i)) for i in range(len(rows))]
