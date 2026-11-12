# Explicit v2 fork: preserve role introductions in every format and skip invisible-only lines.
"""Assemble source-faithful rental clauses for explicit agent annotation, without labels."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from contractguard.dataset import read_json, sha256, write_json, write_rows
from contractguard.provenance import locate_spans, verify_clause_spans
from contractguard.text import normalize

BASE = ROOT/'data/rental_mvp1a_v1'
ARTICLE = re.compile(r'^Điều\s*\d+(?:\s*[.:](?!\d)\s*|\s*$)', re.I)
NUMBER = re.compile(r'^(?!0\d\s+bản)\d+(?:\.\d+)*[.):]?\s+(?!(?:của|nói|và|hoặc)\b)')
ITEM = re.compile(r'^(?:[-–+•●]|\(?[a-zđ]\)|[a-zđ][./]|\([ivx]+\))\s*', re.I)
VI = re.compile(r'[À-ỹĐđ]')


def is_role_intro(value):
    return bool(re.fullmatch(r'(?:\d+(?:\.\d+)*[.)]?\s*)?(?:Trách nhiệm|Quyền và nghĩa vụ).{0,70}Bên\s*[AB]:?',value,re.I))


def choose_source(spec, catalog):
    if spec.get('seed'):
        source = read_json(ROOT/'data/rental_staging/sources.json')[0]
        return source, ROOT/source['pages_path']
    source = catalog[spec['source']]
    folder = BASE/'raw'/spec['source']
    path = next(folder/n for n in ['pages_visual_selected_v1.json','pages_semantic_v2.json','pages_geometry.json','pages.json'] if (folder/n).exists())
    if path.name=='pages_visual_selected_v1.json':
        proof_path=folder/'visual_transcription_v1.json'
        proof=read_json(proof_path)
        if proof['source_sha256']!=source['source_sha256'] or proof['pages_sha256']!=sha256(path):
            raise ValueError('Selected scan transcription is not bound to source')
        source=dict(source,extractor='agent_visual_selected_transcription',
            transcription_proof_path=proof_path.relative_to(ROOT).as_posix(),
            transcription_proof_sha256=sha256(proof_path),full_page_transcription=False)
    return source, path


def assemble(spec, source, pages):
    selected = []
    lo, hi = spec.get('pages', [1, len(pages)])
    for page_number, page in enumerate(pages, 1):
        if not lo <= page_number <= hi:
            continue
        lines = page.splitlines()
        a, b = spec.get('lines', [0, len(lines)])
        for line_index in range(a, min(b, len(lines))):
            value = unicodedata.normalize('NFC', lines[line_index]).strip()
            if not normalize(value) or re.fullmatch(r'\d+', value) or re.fullmatch(r'Trang\s*\|\s*\d+', value):
                continue
            if spec.get('vietnamese_only') and not VI.search(value):
                continue
            selected.append({'page':page_number,'line':line_index,'text':value})
    article, section, lead = [], [], []
    pending = []
    rows, structural = [], []
    pdf_lines = source['format'] == 'pdf'
    last_alpha = ''

    def flush():
        nonlocal section, lead
        if not pending:
            return
        pending_text = ' '.join(p['text'] for p in pending)
        role_intro = is_role_intro(pending_text)
        if ((pending_text.endswith(':') and len(pending_text)<220) or role_intro):
            section = list(pending)
            lead = []
            structural.extend(pending)
            pending.clear()
            return
        prefix = article + section + lead
        seen, parts = set(), []
        for part in prefix + pending:
            key = (part['page'], part['line'])
            if key not in seen:
                parts.append(part)
                seen.add(key)
        parts.sort(key=lambda p:(p['page'],p['line']))
        spans = []
        for part in parts:
            # Locate by actual line offset, not the first matching substring:
            # repeated boilerplate and blank-form dots can occur many times.
            page_lines = pages[part['page']-1].splitlines()
            before = normalize('\n'.join(page_lines[:part['line']]))
            start = len(before) + bool(before)
            end = start + len(normalize(part['text']))
            if normalize(pages[part['page']-1])[start:end] != normalize(part['text']):
                raise ValueError(f'Line offset mismatch: {spec["contract"]}, {part}')
            spans.append({'page':part['page'],'start':start,'end':end})
        text = '\n'.join(p['text'] for p in parts)
        body = '\n'.join(p['text'] for p in pending)
        row = {
            'clause_id':f'{spec["contract"]}_{len(rows)+1:04d}',
            'contract_id':spec['contract'],'document_id':source['document_id'],
            'group_id':spec['family'],'domain':'residential_rental','rental_subtype':spec['subtype'],
            'protected_party':'tenant','tenant_role':'Bên thuê; xác định từ phần các bên của nguồn',
            'text':text,'clause_body':body,'label':'','annotation_reason':'','risk_category':'',
            'clause_type':'','label_confidence':'','review_status':'pending','reviewer':'','review_notes':'',
            'annotation_status':'awaiting_annotation','task':'contract_anomaly_detection',
            'source_url':source['source_url'],'source_sha256':source['source_sha256'],
            'page_start':min(s['page'] for s in spans),'page_end':max(s['page'] for s in spans),
            'heading':' | '.join(p['text'] for p in article+section),
            'source_text':text,'source_spans':json.dumps(spans,ensure_ascii=False),
            'text_repairs':'[]','source_line_refs':json.dumps([(p['page'],p['line']) for p in parts]),
            'body_line_refs':json.dumps([(p['page'],p['line']) for p in pending]),
            'annotation_criteria_sha256':sha256(ROOT/'docs/LABELING_GUIDELINES.md'),
            'proposed_action':'','context_clause_ids':'[]','risk_evidence':'',
        }
        verify_clause_spans(row,pages)
        rows.append(row)
        pending.clear()

    for i, part in enumerate(selected):
        text = part['text']
        if pdf_lines and re.match(r'^\d+\s+(?:Điền theo|Quy định phần này)',text):
            structural.append(part)
            continue
        article_match = ARTICLE.match(text)
        if article_match:
            flush()
            inline_obligation = bool(re.match(r'(?:Bên |Các |Trong |Nếu |Khi |Được |Hai |Hợp đồng)',text[article_match.end():]))
            article, section, lead = ([] if inline_obligation else [part]), [], []
            last_alpha = ''
            if inline_obligation:
                pending.append(part)
            else:
                structural.append(part)
            continue
        if pdf_lines:
            # PDF line wrapping is not a clause boundary. Keep roman sublists
            # inside their parent, and reject numbered cross-reference wraps.
            numeric = NUMBER.match(text)
            alpha = re.match(r'^\(([a-zđ])\)\s+',text)
            plain_alpha = re.match(r'^[a-zđ][.)]\s+',text)
            nested = re.match(r'^\((?:ii|iii|iv|vi|vii|viii|ix|x|A|B)\)',text)
            if alpha and alpha.group(1) in {'i','v','x'} and (
                    last_alpha not in {'h','u','w'} or
                    (pending and pending[-1]['text'].endswith(':'))):
                nested = True
            dash_start = bool(re.match(r'^[-–•●]\s+',text)) and (
                not pending or bool(re.search(r'[.;:]\s*$', pending[-1]['text'])) or
                is_role_intro(' '.join(p['text'] for p in pending)))
            start = bool(numeric or (alpha and not nested) or plain_alpha or dash_start)
            if numeric:
                flush()
                section, lead = [], []
                last_alpha = ''
            elif start:
                flush()
                if alpha:
                    last_alpha=alpha.group(1)
            elif not pending and text.isupper() and len(text)<180 and article:
                article.append(part)
                structural.append(part)
                continue
            pending.append(part)
            continue
        # Section/list introductions carry actor, conditions and exceptions.
        is_intro = (text.endswith(':') and len(text)<550) or bool(re.fullmatch(
            r'(?:\d+(?:\.\d+)*[.)]?\s*)?(?:QUYỀN|NGHĨA VỤ|Quyền|Nghĩa vụ|Trách nhiệm|TRÁCH NHIỆM).{0,90}', text))
        if is_intro:
            flush()
            if NUMBER.match(text):
                section, lead = [part], []
            else:
                lead = [part]
            structural.append(part)
            continue
        start = NUMBER.match(text) or ITEM.match(text)
        # DOM paragraphs already mark meaningful boundaries. A plain lead
        # that ends in a colon is retained above, not turned into a sample.
        flush()
        if NUMBER.match(text):
            section = []
        pending.append(part)
    flush()
    return rows, structural


def main():
    destination=BASE/'candidates.json'
    if destination.exists():
        raise ValueError('Preserve candidate version before rebuilding')
    catalog={s['document_id']:s for s in read_json(BASE/'collection_manifest.json')}
    rows, sources, coverage = [], {}, []
    for spec in read_json(ROOT/'configs/rental_contracts_v1.json'):
        source,path=choose_source(spec,catalog)
        pages=read_json(path)
        source={**source,'pages_path':path.relative_to(ROOT).as_posix(),
                'pages_sha256':sha256(path),'data_kind':'public_contract_template',
                'group_id':spec['family'],'domain':'residential_rental'}
        new,structural=assemble(spec,source,pages)
        rows.extend(new)
        # A physical compilation can contain several contract families; family
        # resides on each row. All share document_id, hence remain group-disjoint.
        sources[source['document_id']]=source
        coverage.append({'contract_id':spec['contract'],'source':source['document_id'],
                         'candidate_count':len(new),'structural_lines':structural,
                         'selection':spec})
        print(spec['contract'],len(new))
    write_json(destination,rows)
    write_json(BASE/'candidate_sources.json',list(sources.values()))
    write_json(BASE/'candidate_coverage.json',coverage)
    write_rows(BASE/'candidates.csv',rows,list(rows[0]))
    print('Total',len(rows),'candidates; zero risk labels assigned')


if __name__=='__main__':
    main()
