"""Collect one public rental template into isolated staging; no labels or approval."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from contractguard.dataset import sha256, write_json, write_rows
from contractguard.provenance import locate_spans

URL = 'https://xaydungchinhsach.chinhphu.vn/mau-hop-dong-thue-nha-o-119240827172441217.htm'
DOCUMENT = 'chinhphu_residential_2024'


def main() -> None:
    import requests
    from bs4 import BeautifulSoup

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/rental_staging')
    args = parser.parse_args()
    destination = args.output.resolve()
    if not destination.is_relative_to(ROOT.resolve()) or destination.exists():
        raise ValueError('Use a new staging directory inside the project; preserve existing data')
    response = requests.get(URL, timeout=(15, 40),
                            headers={'User-Agent': 'ContractGuard-AcademicDataset/0.1'})
    response.raise_for_status()
    if not response.url.startswith('https://xaydungchinhsach.chinhphu.vn/'):
        raise ValueError('Unexpected source redirect')
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
    body = soup.select_one('.detail-content')
    if body is None:
        raise ValueError('Article selector changed; inspect before collecting')
    # Join inline HTML text without injecting spaces into split digits/words.
    paragraphs = [re.sub(r'\s+', ' ', p.get_text()).strip() for p in body.find_all('p')]
    page = '\n'.join(p for p in paragraphs if p)
    headings = list(re.finditer(r'^Điều\s+(\d+)\.\s+[^\n]+', page, re.MULTILINE))
    if [int(m.group(1)) for m in headings] != list(range(1, 13)):
        raise ValueError('Expected twelve complete articles; inspect source structure')
    signature = page.find('\nBÊN', headings[-1].end())
    if signature < 0:
        raise ValueError('Cannot separate signatures and footnotes from the contract body')
    raw_dir = destination / 'raw' / DOCUMENT
    raw_dir.mkdir(parents=True)
    raw_file = raw_dir / 'original.html'
    raw_file.write_bytes(response.content)
    pages_file = raw_dir / 'pages.json'
    write_json(pages_file, [page])
    digest = sha256(raw_file)
    source = {
        'document_id': DOCUMENT, 'group_id': 'residential_template_decree96_2024',
        'title': 'Cổng Chính phủ — Mẫu Hợp đồng thuê nhà ở, đăng 27/08/2024',
        'source_url': URL, 'resolved_url': response.url, 'format': 'html',
        'domain': 'residential_rental', 'protected_party': 'tenant',
        'data_kind': 'public_contract_template', 'source_use_status': 'pending_human_review',
        'source_sha256': digest, 'pages_sha256': sha256(pages_file),
        'raw_path': raw_file.relative_to(ROOT).as_posix(),
        'pages_path': pages_file.relative_to(ROOT).as_posix(),
        'page_count': 1, 'extraction': 'bs4 .detail-content p; inline text retained; whitespace collapsed',
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'notes': 'Source discovery/annotation staging only. No training or redistribution permission inferred. Blank fields and source wording are retained, including buyer/seller wording in Article 12.',
    }
    rows = []
    for i, heading in enumerate(headings):
        start = heading.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else signature
        while page[end - 1].isspace():
            end -= 1
        rows.append({
            'clause_id': f'{DOCUMENT}_article_{i+1:02d}', 'document_id': DOCUMENT,
            'group_id': source['group_id'], 'source_url': URL, 'source_sha256': digest,
            'page_start': 1, 'page_end': 1, 'heading': heading.group(),
            'text': page[start:end], 'source_text': page[start:end],
            'source_spans': json.dumps(locate_spans(page[start:end], [page])),
            'label': '', 'annotation_reason': '', 'annotation_status': 'awaiting_annotation',
            'review_status': 'pending', 'reviewer': '', 'review_notes': '',
            'task': 'contract_anomaly_detection', 'domain': 'residential_rental',
            'protected_party': 'tenant',
        })
    write_json(destination / 'sources.json', [source])
    write_rows(destination / 'candidates.csv', rows, list(rows[0]))
    print(f'{DOCUMENT}: {len(rows)} whole-article candidates; unannotated; {destination}')


if __name__ == '__main__':
    main()
