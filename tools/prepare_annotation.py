"""Prepare evidence for manual annotation; no class is inferred by this script.

Run with pdfplumber installed (the bundled runtime includes it). Raw source files
and the approved rubric are immutable. Only whitespace is reconciled against a
second geometry-based extraction; every original and change remains recorded.
"""
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import read_json, read_rows, sha256, write_json
from contractguard.text import normalize


def compact(text):
    return re.sub(r'\s+', '', normalize(text))


def prepare():
    import pdfplumber
    source = ROOT/'data/clauses.csv'
    previous_path=ROOT/'configs/annotation_preparation.json'
    previous=read_json(previous_path) if previous_path.exists() else {}
    if previous:
        snapshot=ROOT/previous['snapshot']
        manifest_path=ROOT/'reports/risk_annotation_manifest.json'
        manifest=read_json(manifest_path) if manifest_path.exists() else {}
        if sha256(source) not in {previous['snapshot_sha256'],manifest.get('dataset_sha256')}:
            raise ValueError('Canonical dataset changed after preparation; do not reset annotation or review work')
        if sha256(snapshot)!=previous['snapshot_sha256']:
            raise ValueError('Immutable snapshot changed')
    else:
        snapshot = ROOT/'data/snapshots'/f"before_risk_annotation_{sha256(source)[:12]}.csv"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if not snapshot.exists():
        snapshot.write_bytes(source.read_bytes())
    rows = read_rows(snapshot)
    originals = {s['document_id']: read_json(ROOT/s['pages_path']) for s in read_json(ROOT/'data/sources.json')}
    from annotation_structure import repair_structure
    indexed_rows, structure_changes = repair_structure(rows, originals)
    write_json(ROOT/'reports/source_quality/structure_repairs.json', structure_changes)
    references = {}
    for spec in read_json(ROOT/'data/sources.json'):
        if sha256(ROOT/spec['raw_path']) != spec['source_sha256']:
            raise ValueError('Source hash changed')
        if spec['format'] == 'pdf':
            path = ROOT/'reports/source_quality'/f"{spec['document_id']}_pdfplumber.json"
            cached = read_json(path) if path.exists() else {}
            if cached.get('source_sha256') == spec['source_sha256'] and cached.get('version') == pdfplumber.__version__:
                pages = cached['pages']
            else:
                with pdfplumber.open(ROOT/spec['raw_path']) as pdf:
                    pages = [p.extract_text(x_tolerance=3) or '' for p in pdf.pages]
                write_json(path, {'extractor': 'pdfplumber', 'version': pdfplumber.__version__,
                                 'source_sha256': spec['source_sha256'], 'pages': pages})
            references[spec['document_id']] = {'path': path.relative_to(ROOT).as_posix(),
                'sha256': sha256(path), 'pages': pages}
    prepared = []
    for i, row in indexed_rows:
        text = unicodedata.normalize('NFC', row['text'])
        ref = references.get(row['document_id'])
        pieces = []
        matched = True
        for span in json.loads(row['source_spans']):
            raw_piece = normalize(originals[row['document_id']][span['page']-1])[span['start']:span['end']]
            if not ref:
                pieces.append(raw_piece)
                continue
            page = normalize(ref['pages'][span['page']-1])
            positions = [j for j,c in enumerate(page) if not c.isspace()]
            dense = ''.join(page[j] for j in positions)
            needle = compact(raw_piece)
            start = dense.find(needle)
            if start < 0:
                matched = False
                break
            # Identical repeated phrases have known ordinal positions in the original
            # page; use that occurrence in the independent extraction when possible.
            dense_original = compact(originals[row['document_id']][span['page']-1])
            before = compact(normalize(originals[row['document_id']][span['page']-1])[:span['start']])
            original_hits = [m.start() for m in re.finditer(re.escape(needle), dense_original)]
            alternate_hits = [m.start() for m in re.finditer(re.escape(needle), dense)]
            if len(original_hits) == len(alternate_hits) and len(before) in original_hits:
                start = alternate_hits[original_hits.index(len(before))]
            pieces.append(page[positions[start]:positions[start+len(needle)-1]+1])
        repaired = text
        if matched and pieces:
            layout = ' '.join(pieces)
            if compact(layout) != compact(text):
                raise ValueError('Whitespace reconciliation changed content')
            letters = iter(c for c in text if not c.isspace())
            repaired = ''.join(' ' if c.isspace() else next(letters) for c in layout)
            repaired = re.sub(r'\s+', ' ', repaired).strip()
        # Verified visually on page 5: the legacy font's ToUnicode map emits
        # LATIN OI (ƣ) where the PDF renders Vietnamese ư. Keep this correction
        # narrow to the checked document, not as a general spelling rule.
        if row['document_id'] == 'fpt_phone_business':
            repaired = repaired.translate(str.maketrans({'ƣ':'ư', 'Ƣ':'Ư'}))
        edits = []
        for tag, a,b,c,d in SequenceMatcher(None, text, repaired, autojunk=False).get_opcodes():
            if tag != 'equal':
                before, after = text[a:b], repaired[c:d]
                kind = 'whitespace'
                if before.strip() or after.strip():
                    mapped = re.sub(r'\s+', '', before).translate(str.maketrans({'ƣ':'ư','Ƣ':'Ư'}))
                    if row['document_id'] != 'fpt_phone_business' or mapped != re.sub(r'\s+', '', after):
                        raise ValueError('Unverified non-whitespace edit rejected')
                    kind = 'verified_legacy_font_glyph'
                edits.append({'start':a, 'end':b, 'replacement':after, 'kind':kind})
        prepared.append({'index':i, 'clause_id':row['clause_id'], 'source_text':text,
            'source_text_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'text':repaired, 'text_repairs':edits,
            'reference': {k:v for k,v in ref.items() if k!='pages'} if ref and edits else None,
            'source_row':row})
    write_json(ROOT/'configs/annotation_preparation.json', {
        'snapshot':snapshot.relative_to(ROOT).as_posix(), 'snapshot_sha256':sha256(snapshot),
        'rubric_sha256':sha256(ROOT/'docs/ANNOTATION_GUIDELINES.md'), 'rows':prepared})
    print(json.dumps({'rows':len(prepared), 'whitespace_repaired':sum(bool(r['text_repairs']) for r in prepared),
                      'edits':sum(len(r['text_repairs']) for r in prepared)}))


if __name__=='__main__':
    prepare()
