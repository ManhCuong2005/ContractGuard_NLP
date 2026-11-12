"""Inventory and extract local course material without executing notebooks."""
from pathlib import Path
import hashlib
import json
import os
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.venv', '.git', 'node_modules', '__pycache__', 'python_packages',
            'deps', 'site-packages', '.ipynb_checkpoints', 'ContractGuard'}


def extract(name, raw):
    suffix = Path(name).suffix.lower()
    if suffix == '.ipynb':
        nb = json.loads(raw)
        blocks = []
        for i, cell in enumerate(nb.get('cells', [])):
            blocks.append(f"[{i}: {cell.get('cell_type')}]\n{''.join(cell.get('source', []))}")
            for output in cell.get('outputs', []):
                value = output.get('text', output.get('data', {}).get('text/plain', ''))
                blocks.append('[saved output, not independently verified]\n' + (''.join(value) if isinstance(value, list) else str(value)))
        return '\n\n'.join(blocks)
    if suffix == '.html':
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw, 'html.parser')
        for element in soup(['script', 'style']):
            element.decompose()
        return soup.get_text('\n', strip=True)
    if suffix == '.docx':
        import io
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            return '\n'.join(''.join(t.text or '' for t in p.iter(ns + 't')) for p in
                             ET.fromstring(z.read('word/document.xml')).iter(ns + 'p'))
    if suffix == '.pdf':
        import io
        from pypdf import PdfReader
        return '\n\n'.join(f'[Page {i+1}]\n{p.extract_text()}'
                           for i, p in enumerate(PdfReader(io.BytesIO(raw)).pages))
    return raw.decode('utf-8-sig', errors='replace')


def main():
    dest = ROOT / 'reports' / 'materials'
    dest.mkdir(parents=True, exist_ok=True)
    entries = []
    candidates = []
    for base, dirs, files in os.walk(ROOT.parent):
        dirs[:] = [d for d in dirs if d not in EXCLUDED and not d.startswith('.')]
        for name in sorted(files):
            p = Path(base) / name
            if name.startswith('~$'):
                continue
            if p.suffix.lower() in {'.ipynb', '.docx', '.pdf', '.md', '.txt', '.html', '.py', '.ps1', '.mjs', '.cjs'}:
                candidates.append((str(p), p.read_bytes()))
            elif p.suffix.lower() == '.zip':
                with zipfile.ZipFile(p) as z:
                    for item in z.namelist():
                        if Path(item).suffix.lower() in {'.ipynb', '.md', '.txt', '.pdf', '.docx', '.py'}:
                            candidates.append((f'{p}!{item}', z.read(item)))
    seen = {}
    for i, (name, raw) in enumerate(candidates):
        digest = hashlib.sha256(raw).hexdigest()
        entry = {'source': name, 'sha256': digest, 'bytes': len(raw)}
        if digest in seen:
            entry.update(duplicate_of=seen[digest], status='duplicate')
        else:
            try:
                content = extract(name, raw)
                target = dest / f'{i:03d}_{Path(name).stem}.txt'
                target.write_text(content, encoding='utf-8')
                entry.update(status='extracted', characters=len(content), extracted=str(target.relative_to(ROOT)))
                seen[digest] = name
            except Exception as e:
                entry.update(status='error', error=str(e))
        entries.append(entry)
    (dest / 'inventory.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'total': len(entries), 'extracted': sum(e['status']=='extracted' for e in entries),
                      'errors': [e for e in entries if e['status']=='error']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
