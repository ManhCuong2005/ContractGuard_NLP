"""Explicit data/criteria profiles; legacy approval never authorizes rental data."""
from pathlib import Path

def profile_paths(root,profile='legacy'):
    root=Path(root)
    if profile=='legacy':
        return dict(dataset=root/'data/clauses.csv',approval=root/'configs/approval.json',
            rubric=root/'docs/ANNOTATION_GUIDELINES.md',labels=root/'configs/labels.json',sources=root/'data/sources.json')
    if profile=='rental':
        return dict(dataset=root/'data/rental_approved_v1/clauses.csv',approval=root/'configs/rental_approval.json',
            rubric=root/'docs/LABELING_GUIDELINES.md',labels=root/'configs/rental_labels.json',sources=root/'data/rental_approved_v1/sources.json')
    raise ValueError(f'Unknown dataset profile: {profile}')
