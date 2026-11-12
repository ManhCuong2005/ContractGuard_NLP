"""Conservative Vietnamese normalization shared by training and inference."""
import re
import unicodedata


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError('Clause text must be a string')
    text = unicodedata.normalize('NFC', text)
    text = text.replace('\u200b', '').replace('\ufeff', '').replace('\u00ad', '')
    return re.sub(r'\s+', ' ', text).strip().lower()


def require_text(text: str) -> str:
    cleaned = normalize(text)
    if len(re.findall(r'\w+', cleaned)) < 3 or not any(c.isalpha() for c in cleaned):
        raise ValueError('Clause needs at least three tokens and some letters')
    if len(cleaned) > 20000:
        raise ValueError('Clause exceeds 20000 characters; split at a meaningful boundary')
    return cleaned


def shingles(text: str) -> set[tuple[str, ...]]:
    # Internal dataset leakage check only; not a similar-clause search feature.
    tokens = re.findall(r'\w+', normalize(text))
    return {tuple(tokens[i:i+3]) for i in range(max(1, len(tokens)-2))}
