"""Ordered, exact source spans for clauses assembled across pages/list items.

Offsets refer to normalize(original_page), never to modified source files.
Every excerpt and the concatenated clause must match; a span is not an excuse
to paraphrase or replace missing text.
"""
from difflib import SequenceMatcher
import json
import re
import unicodedata

from .text import normalize


def apply_verified_text_repairs(source_text, repairs, document_id=''):
    """Reproduce logged spacing/font repairs without permitting paraphrases.

    Offsets apply to NFC(source_text). The only non-spacing change allowed is
    the checked legacy-font OI -> Vietnamese U-HORN mapping in the FPT phone PDF.
    Exact excerpts remain verifiable against the immutable original extraction.
    """
    if isinstance(repairs, str):
        repairs = json.loads(repairs)
    if not isinstance(repairs, list):
        raise ValueError('Text repairs must be a list')
    original = unicodedata.normalize('NFC', source_text)
    previous = 0
    for repair in repairs:
        if not isinstance(repair, dict) or any(type(repair.get(k)) is not int for k in ['start','end']):
            raise ValueError('Text repair coordinates must be integers')
        start, end = repair['start'], repair['end']
        replacement = repair.get('replacement')
        if not isinstance(replacement, str) or not previous <= start <= end <= len(original):
            raise ValueError('Text repairs must be ordered, nonoverlapping and in bounds')
        before = re.sub(r'\s+', '', original[start:end])
        after = re.sub(r'\s+', '', replacement)
        kind = repair.get('kind', 'whitespace')
        if kind == 'verified_legacy_font_glyph' and document_id == 'fpt_phone_business':
            before = before.translate(str.maketrans({'ƣ':'ư','Ƣ':'Ư'}))
        elif kind != 'whitespace':
            raise ValueError('Unapproved glyph repair or document')
        if before != after:
            raise ValueError('Text repair changes clause content beyond verified spacing/font correction')
        previous = end
    for repair in reversed(repairs):
        original = original[:repair['start']]+repair['replacement']+original[repair['end']:]
    return original


def verify_clause_spans(row, pages):
    """Verify the source excerpt first, then replay the complete repair ledger."""
    source_text = row.get('source_text') or row['text']
    spans = verify_spans(source_text, pages, row['source_spans'])
    repaired = apply_verified_text_repairs(source_text, row.get('text_repairs') or [], row['document_id'])
    if repaired != unicodedata.normalize('NFC', row['text']):
        raise ValueError('Clause text does not match its replayed source repairs')
    return spans


def verify_spans(text, pages, spans):
    if isinstance(spans, str):
        spans = json.loads(spans)
    if not isinstance(spans, list) or not spans:
        raise ValueError('Source spans must be a nonempty list')
    pieces, previous = [], (0, 0)
    for span in spans:
        if not isinstance(span, dict):
            raise ValueError('Each source span must be an object')
        if any(type(span.get(k)) is not int for k in ['page','start','end']):
            raise ValueError('Source span coordinates must be integers')
        page, start, end = (span[k] for k in ['page','start','end'])
        if not 1 <= page <= len(pages):
            raise ValueError('Source span page outside source')
        source = normalize(pages[page-1])
        if not 0 <= start < end <= len(source) or (page, start) < previous:
            raise ValueError('Source spans must be ordered, nonoverlapping and in bounds')
        pieces.append(source[start:end])
        previous = (page, end)
    if normalize(' '.join(pieces)) != normalize(text):
        raise ValueError('Assembled clause differs from exact source span content')
    return spans


def locate_spans(text, pages, page_start=1, page_end=None):
    """Locate all clause characters, allowing only source-side gaps (footers).

    No clause-side content may disappear. Final reconstruction is always checked.
    """
    page_end = page_end or len(pages)
    normalized = [normalize(p) for p in pages]
    subset = normalized[page_start-1:page_end]
    source = ' '.join(subset)
    target = normalize(text)
    if not target:
        raise ValueError('Empty clause')
    bases, cursor = [], 0
    for page in subset:
        bases.append(cursor)
        cursor += len(page)+1
    found = source.find(target)
    if found >= 0:
        blocks = [(0, found, len(target))]
    else:
        blocks = [(b.a,b.b,b.size) for b in SequenceMatcher(None,target,source,autojunk=False).get_matching_blocks() if b.size]
        last = 0
        for a,b,size in blocks:
            if target[last:a].strip():
                raise ValueError('Clause contains content not found verbatim in source')
            last = a+size
        if target[last:].strip():
            raise ValueError('Clause suffix not found verbatim in source')
    spans = []
    for _, start, size in blocks:
        end = start+size
        for i, (base, page_text) in enumerate(zip(bases,subset)):
            lo, hi = max(start,base), min(end,base+len(page_text))
            if lo < hi and page_text[lo-base:hi-base].strip():
                spans.append({'page':page_start+i,'start':lo-base,'end':hi-base})
    # Joining arbitrary character fragments could introduce spaces inside words.
    # Reconstruction equality rejects such alignments instead of guessing.
    verify_spans(text,pages,spans)
    return spans
