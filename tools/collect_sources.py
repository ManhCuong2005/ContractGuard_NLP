"""Download public contract templates, retain byte-exact originals and provenance.

No external AI; extraction and weak annotation use local code only.
Re-running never overwrites an existing review sheet or source manifest.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))

from contractguard.dataset import read_json, sha256, write_json, write_rows
from contractguard.text import normalize

KEYWORDS = {
    'payment': ['thanh toán', 'giá cước', 'cước phí', 'hóa đơn', 'hoá đơn'],
    'termination': ['chấm dứt', 'thanh lý', 'tạm ngừng', 'tạm dừng'],
    'liability': ['bồi thường', 'phạt vi phạm', 'chịu trách nhiệm', 'miễn trách nhiệm'],
    'confidentiality': ['bảo mật', 'thông tin cá nhân', 'dữ liệu cá nhân', 'thông tin mật'],
    'dispute': ['tranh chấp', 'trọng tài', 'tòa án', 'toà án', 'khiếu nại'],
    'force_majeure': ['bất khả kháng'],
    'duration': ['thời hạn hợp đồng', 'thời hạn của hợp đồng', 'có hiệu lực', 'gia hạn'],
}


def suggest(text):
    normalized = normalize(text)
    hits = [label for label, words in KEYWORDS.items() if any(w in normalized for w in words)]
    return (hits[0] if len(hits) == 1 else ''), (
        'keyword_only:' + ','.join(hits) if hits else 'no_keyword:review_other_or_resegment')


def extract_clauses(pages, numbered_headings=False):
    # Keep PDF line order and page ranges; never silently truncate long paragraphs.
    pieces = []
    current, heading, start, end = [], '', 1, 1
    collecting_heading = False

    def flush():
        if current:
            text = re.sub(r'\s+', ' ', ' '.join(current)).strip()
            if text:
                pieces.append({'text': text, 'heading': heading, 'page_start': start, 'page_end': end})
        current.clear()

    for page_number, page in enumerate(pages, 1):
        for line in page.splitlines():
            line = line.strip()
            if not line:
                continue
            article = re.match(r'^(?:ĐIỀU|Điều)\s+\d+(?:\s*$|\s*[:.]\s*(?:$|[A-ZÀ-Ỵ]))', line)
            numbered = numbered_headings and re.fullmatch(r'\d+\.\s*(?:[A-ZÀ-Ỵ][A-ZÀ-Ỵ0-9\s:(),/–-]*)?', line)
            if article or numbered:
                flush()
                heading = line
                collecting_heading = True
                continue
            if re.fullmatch(r'\d+(?:\s*/\s*\d+)?', line) or re.match(r'^\d+[./]\d+[./]\d+[-–]BM', line):
                continue
            # Only numbered contract body; exclude identities/signatures before first article.
            if not heading:
                continue
            if collecting_heading and line.isupper() and len(line) < 150:
                heading += ' ' + line
                continue
            collecting_heading = False
            boundary = re.match(r'^(?:\d+\.\d+(?:\.\d+)*[.)]?|\d+[.)]|[a-zđ][.)])\s+', line)
            if boundary:
                flush()
                line = line[boundary.end():]
            if not current:
                start = page_number
            end = page_number
            current.append(line)
    flush()
    return pieces


def main():
    import argparse
    import requests
    from bs4 import BeautifulSoup
    from pypdf import PdfReader
    import io
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--append', action='store_true', help='Collect only new source IDs, preserving existing sources/rows')
    args = parser.parse_args()
    # New extraction is a staging area, separate from canonical and historical review data.
    destinations = [ROOT/'data/sources.json', ROOT/'data/candidates.csv']
    if any(p.exists() for p in destinations) and not args.append:
        raise SystemExit('Collection already exists. Preserve review work; use a new dataset version instead.')
    from contractguard.dataset import read_rows
    rows = read_rows(destinations[1]) if args.append and destinations[1].exists() else []
    if any(r.get('label') or r.get('review_status') != 'pending' or r.get('reviewer') for r in rows):
        raise SystemExit('Staging contains annotation/review work; preserve it before collecting more sources.')
    sources = read_json(destinations[0]) if args.append and destinations[0].exists() else []
    existing = {s['document_id'] for s in sources}
    errors = []
    for spec in read_json(ROOT/'configs/collection_sources.json'):
        if spec['document_id'] in existing:
            continue
        try:
            if urlparse(spec['source_url']).scheme != 'https':
                raise ValueError('Only HTTPS source URLs allowed')
            response = requests.get(spec['source_url'], timeout=(15, 60),
                                    headers={'User-Agent':'ContractGuard-AcademicDataset/0.1'})
            response.raise_for_status()
            raw = response.content
            if spec['format'] == 'pdf':
                if not raw.startswith(b'%PDF'):
                    raise ValueError('Source did not return a PDF')
                pages = [page.extract_text() or '' for page in PdfReader(io.BytesIO(raw)).pages]
            else:
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'html.parser')
                for el in soup(['script', 'style', 'nav', 'footer', 'header']):
                    el.decompose()
                # Narrow the extraction to the actual contract article where possible.
                article = soup.find('article') or soup.find('main') or soup.body or soup
                pages = [article.get_text('\n', strip=True)]
            if not any(normalize(p) for p in pages):
                raise ValueError('No extractable text; OCR/manual transcription required')
            folder = ROOT/'data/raw'/spec['document_id']
            folder.mkdir(parents=True, exist_ok=True)
            raw_path = folder/('original.' + spec['format'])
            raw_path.write_bytes(raw)
            pages_path = folder/'pages.json'
            write_json(pages_path, pages)
            source = {**spec, 'data_kind':'public_contract_template',
                      'source_sha256':sha256(raw_path), 'pages_sha256':sha256(pages_path),
                      'raw_path':raw_path.relative_to(ROOT).as_posix(),
                      'pages_path':pages_path.relative_to(ROOT).as_posix(),
                      'retrieved_at':datetime.now(timezone.utc).isoformat(),
                      'resolved_url':response.url, 'page_count':len(pages),
                      'source_use_status':'pending_human_review',
                      'notes':'Public availability does not establish a redistribution/training license; historical templates, not signed contracts.'}
            clauses = extract_clauses(pages, spec.get('numbered_headings', False))
            if not clauses:
                raise ValueError('No clause boundaries recognized; manual extraction required')
            sources.append(source)
            for i, clause in enumerate(clauses, 1):
                label, reason = suggest(clause['text'])
                rows.append({**clause, 'clause_id':f'{spec["document_id"]}_{i:04d}',
                             'document_id':spec['document_id'], 'group_id':spec['group_id'],
                             'source_url':spec['source_url'], 'source_sha256':source['source_sha256'],
                             'suggested_label':label, 'suggestion_reason':reason,
                             'label':'', 'review_status':'pending', 'reviewer':'', 'review_notes':''})
            print(f'{spec["document_id"]}: {len(pages)} pages, {len(clauses)} candidates')
        except Exception as e:
            errors.append({'document_id':spec['document_id'], 'error':str(e)})
            print(f'{spec["document_id"]}: ERROR {e}', file=sys.stderr)
    write_json(ROOT/'data/sources.json', sources)
    write_rows(destinations[1], rows)
    write_json(ROOT/'reports/collection_errors.json', errors)
    print(json.dumps({'sources':len(sources), 'candidates':len(rows), 'errors':len(errors)}))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
