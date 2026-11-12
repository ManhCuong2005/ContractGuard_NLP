"""Versioned source collection for rental MVP 1A. No external AI or official fitting."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import sys
import zipfile
from xml.etree import ElementTree as ET
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from contractguard.dataset import read_json, sha256, write_json

BASE = ROOT / 'data/rental_mvp1a_v1'


def html_pages(raw):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw, 'html.parser')
    links = [{'text': a.get_text(' ', strip=True), 'href': a.get('href', '')}
             for a in soup.find_all('a', href=True)]
    for el in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
        el.decompose()
    selectors = ['.detail-content', '.entry-content', '.post-content', '.article-content',
                 '.content-detail', '.content-detail-post', '.article__body', 'article', 'main']
    choices = [(selector, el) for selector in selectors for el in soup.select(selector)
               if len(el.get_text()) > 700]
    selector, body = choices[0] if choices else ('body', soup.body or soup)
    # get_text with separators preserves paragraph/inline order as evidence.
    text = body.get_text('\n', strip=True)
    text = '\n'.join(re.sub(r'\s+', ' ', p).strip() for p in text.splitlines() if p.strip())
    return [text], links, selector


def semantic_html(raw):
    """Recover paragraph boundaries from DOM; never join inline spans with spaces."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw, 'html.parser')
    for el in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
        el.decompose()
    selectors = ['.detail-content', '.entry-content', '.post-content', '.article-content',
                 '.content-detail', '.content-detail-post', '.article__body', 'article', 'main']
    choices = [(selector, el) for selector in selectors for el in soup.select(selector)
               if len(el.get_text()) > 700]
    selector, body = choices[0] if choices else ('body', soup.body or soup)
    from bs4 import NavigableString, Tag
    tags = {'p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr', 'div', 'section', 'br'}
    paragraphs, buffer = [], []

    def flush():
        value = re.sub(r'\s+', ' ', ''.join(buffer)).strip()
        if value:
            paragraphs.append(value)
        buffer.clear()

    def walk(node):
        if isinstance(node, NavigableString):
            buffer.append(str(node))
        elif isinstance(node, Tag):
            block = node.name in tags
            if block:
                flush()
            for child in node.children:
                walk(child)
            if block:
                flush()

    walk(body)
    flush()
    if len(' '.join(paragraphs)) < 700:
        raise ValueError('Insufficient DOM paragraphs; inspect source')
    return ['\n'.join(paragraphs)], selector


def prepare_html():
    for source in read_json(BASE / 'collection_manifest.json'):
        if source['format'] != 'html':
            continue
        folder = BASE / 'raw' / source['document_id']
        target = folder / 'pages_semantic_v2.json'
        if target.exists():
            continue
        pages, selector = semantic_html((ROOT / source['raw_path']).read_bytes())
        write_json(target, pages)
        write_json(folder / 'semantic_extraction_v2.json', {
            'raw_sha256': source['source_sha256'], 'pages_sha256': sha256(target),
            'selector': selector, 'method': 'DOM recursive block boundaries, inline text concatenation, whitespace normalization only; v1 retained',
        })
        print(source['document_id'], len(pages[0].splitlines()), 'paragraphs')


def fetch_source(spec):
    import requests
    document = spec['document_id']
    if not re.fullmatch(r'[a-z0-9_]+', document):
        raise ValueError('Invalid source identifier')
    folder = BASE / 'raw' / document
    manifest = folder / 'source.json'
    if manifest.exists():
        source = read_json(manifest)
        if source['source_url'] != spec['url']:
            raise ValueError('Existing source URL differs')
        if sha256(ROOT / source['raw_path']) != source['source_sha256']:
            raise ValueError('Existing source hash differs')
        return {**source, 'reused_existing_bytes': True}
    if urlparse(spec['url']).scheme != 'https':
        raise ValueError('Only public HTTPS sources are permitted')
    response = requests.get(spec['url'], timeout=(12, 40),
                            headers={'User-Agent': 'ContractGuard-AcademicDataset/0.1'})
    response.raise_for_status()
    if len(response.content) > 40_000_000:
        raise ValueError('Source exceeds 40MB; inspect before downloading')
    raw = response.content
    extension = spec['format']
    links, selector = [], None
    if extension == 'pdf':
        from pypdf import PdfReader
        if not raw.startswith(b'%PDF'):
            raise ValueError('Server did not return a PDF')
        pages = [(page.extract_text() or '') for page in PdfReader(io.BytesIO(raw)).pages]
        extractor = 'pypdf'
    elif extension == 'html':
        pages, links, selector = html_pages(raw)
        extractor = 'bs4'
    elif extension == 'docx':
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            xml = ET.fromstring(archive.read('word/document.xml'))
            ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            pages = ['\n'.join(''.join(t.text or '' for t in p.iter(ns + 't'))
                              for p in xml.iter(ns + 'p'))]
        extractor = 'ooxml_paragraphs'
    else:
        raise ValueError('Unsupported source format')
    scanned = not any(p.strip() for p in pages)
    if scanned and not spec.get('allow_scanned'):
        raise ValueError('No text; needs OCR or source repair')
    folder.mkdir(parents=True, exist_ok=True)
    original = folder / ('original.' + extension)
    if original.exists():
        raise ValueError('Partial collection exists; preserve and inspect it')
    original.write_bytes(raw)
    write_json(folder / 'pages.json', pages)
    write_json(folder / 'links.json', [{**link, 'url': urljoin(response.url, link['href'])} for link in links])
    source = {
        'document_id': document, 'title': spec['title'], 'source_url': spec['url'],
        'resolved_url': response.url, 'format': extension,
        'data_kind': 'public_template_candidate', 'source_use_status': 'pending_dataset_and_source_review',
        'raw_path': original.relative_to(ROOT).as_posix(), 'source_sha256': sha256(original),
        'pages_path': (folder / 'pages.json').relative_to(ROOT).as_posix(),
        'pages_sha256': sha256(folder / 'pages.json'), 'page_count': len(pages),
        'extractor': extractor, 'html_selector': selector,
        'requires_visual_transcription': scanned,
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'discovery_only': spec.get('discovery_only', False),
        'notes': 'Source content must be inspected for residential scope, template boundaries, duplication, personal data and use conditions before inclusion. No label, source approval, legal conclusion or training permission inferred.',
    }
    write_json(manifest, source)
    return source


def fetch_all(config):
    BASE.mkdir(parents=True, exist_ok=True)
    specs = read_json(config)
    results, failures = [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks = {pool.submit(fetch_source, spec): spec for spec in specs}
        for future in as_completed(tasks):
            spec = tasks[future]
            try:
                result = future.result()
                results.append(result)
                print(f'{spec["document_id"]}: {result["page_count"]} pages', flush=True)
            except Exception as exc:
                failures.append({'document_id': spec['document_id'], 'url': spec['url'], 'error': str(exc)})
                print(f'{spec["document_id"]}: FAILED {type(exc).__name__}', flush=True)
    manifest_path = BASE / 'collection_manifest.json'
    existing = read_json(manifest_path) if manifest_path.exists() else []
    merged = {s['document_id']: s for s in existing}
    merged.update({s['document_id']: s for s in results})
    write_json(manifest_path, sorted(merged.values(), key=lambda s: s['document_id']))
    write_json(BASE / 'collection_failures.json', failures)
    receipt=BASE/'collection_runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    write_json(receipt, {'config':str(config),'successful_source_ids':[s['document_id'] for s in results],
                        'failures':failures,'recorded_at':datetime.now(timezone.utc).isoformat()})
    print(f'Successful this batch: {len(results)}; failures: {len(failures)}; known sources: {len(merged)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    fetch = commands.add_parser('fetch')
    fetch.add_argument('--config', type=Path, default=ROOT / 'configs/rental_collection_v1.json')
    commands.add_parser('prepare-html')
    commands.add_parser('prepare-pdf')
    show = commands.add_parser('show')
    show.add_argument('document')
    show.add_argument('--page', type=int)
    show.add_argument('--links', action='store_true')
    show.add_argument('--start', type=int, default=0)
    show.add_argument('--count', type=int, default=150)
    show.add_argument('--semantic', action='store_true')
    headings = commands.add_parser('headings')
    headings.add_argument('document')
    args = parser.parse_args()
    if args.command == 'fetch':
        fetch_all(args.config)
    elif args.command == 'prepare-html':
        prepare_html()
    elif args.command == 'prepare-pdf':
        import pdfplumber
        for source in read_json(BASE / 'collection_manifest.json'):
            if source['format'] != 'pdf':
                continue
            folder = BASE / 'raw' / source['document_id']
            target = folder / 'pages_geometry.json'
            if target.exists():
                continue
            with pdfplumber.open(ROOT / source['raw_path']) as pdf:
                pages = [(page.extract_text(x_tolerance=2, y_tolerance=3) or '') for page in pdf.pages]
            write_json(target, pages)
            write_json(folder / 'geometry_extraction.json', {
                'raw_sha256': source['source_sha256'], 'pages_sha256': sha256(target),
                'method': 'pdfplumber 0.11.9, x_tolerance=2, y_tolerance=3',
            })
            print(source['document_id'], len(pages), 'geometry pages', flush=True)
    else:
        folder = BASE / 'raw' / args.document
        if args.command == 'headings':
            path = next((folder / n for n in ['pages_visual_selected_v1.json', 'pages_semantic_v2.json', 'pages_geometry.json', 'pages.json']
                         if (folder / n).exists()))
            for page, value in enumerate(read_json(path), 1):
                lines = value.splitlines()
                print('PAGE', page, 'LINES', len(lines))
                for i, line in enumerate(lines):
                    if re.search(r'^(?:Điều\s*\d|ĐIỀU\s*\d|HỢP ĐỒNG|BÊN THUÊ|BÊN CHO|ĐẠI DIỆN|[IVX]+\.\s)', line):
                        print(i, line[:180])
            return
        if args.links:
            for i, link in enumerate(read_json(folder / 'links.json')):
                if re.search(r'\.pdf|\.docx?|thue|thuê|download|tải|tải về', link['url'] + ' ' + link['text'], re.I):
                    print(i, json.dumps(link, ensure_ascii=False))
        else:
            alternate = next(folder/n for n in ['pages_visual_selected_v1.json','pages_semantic_v2.json','pages_geometry.json','pages.json'] if (folder/n).exists())
            if args.semantic and alternate.name.startswith('pages_visual_'):
                print('VISUALLY TRANSCRIBED SELECTED EXCERPTS; not full-page OCR')
            pages = read_json(alternate if args.semantic else folder / 'pages.json')
            for number, page in enumerate(pages, 1):
                if args.page is not None and number != args.page:
                    continue
                print(f'PAGE {number}')
                lines = page.splitlines()
                for i in range(args.start, min(len(lines), args.start + args.count)):
                    print(f'{i:04d} {lines[i]}')


if __name__ == '__main__':
    main()
