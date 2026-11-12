"""Local CLI only. No HTTP endpoints or database."""
import argparse
import json
from pathlib import Path
import sys

from .dataset import audit_dataset, read_json, sha256, training_readiness, write_json


def parser():
    p = argparse.ArgumentParser(description='ContractGuard MVP 1 — offline NLP')
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    commands = p.add_subparsers(dest='command', required=True)
    check = commands.add_parser('audit', help='Audit review CSV without fitting a model')
    check.add_argument('--data', type=Path, required=True)
    check.add_argument('--output', type=Path)
    ready = commands.add_parser('readiness', help='Report training blockers without fitting or granting approval')
    ready.add_argument('--data', type=Path, default=Path('data/clauses.csv'))
    ready.add_argument('--output', type=Path)
    digest = commands.add_parser('approval-digests', help='Show digests only; never grant approval')
    digest.add_argument('--data', type=Path, required=True)
    fit = commands.add_parser('train', help='Official training; requires human approval')
    fit.add_argument('--data', type=Path, required=True)
    fit.add_argument('--output', type=Path, required=True)
    fit.add_argument('--seed', type=int, default=42)
    pred = commands.add_parser('predict', help='Predict new clauses with a locally trained model')
    pred.add_argument('--model', type=Path, required=True)
    group = pred.add_mutually_exclusive_group(required=True)
    group.add_argument('--text')
    group.add_argument('--input', type=Path, help='JSON array of clause strings')
    pred.add_argument('--output', type=Path)
    for subparser in [check,ready,digest,fit]:
        subparser.add_argument('--profile',choices=['legacy','rental'],default='legacy')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command!='predict':
            from .profiles import profile_paths
            paths=profile_paths(args.root,args.profile)
            if args.command=='readiness' and args.profile=='rental' and args.data==Path('data/clauses.csv'):
                args.data=paths['dataset']
        if args.command == 'audit':
            result = audit_dataset(args.data, paths['labels'], paths['sources'], args.root)
            if args.output:
                write_json(args.output, result)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1 if result['errors'] else 0
        if args.command == 'readiness':
            result = training_readiness(args.root, args.data, args.profile)
            if args.output:
                write_json(args.output, result)
        elif args.command == 'approval-digests':
            result = {k: sha256(p) for k, p in {
                'dataset_sha256': args.data, 'criteria_sha256': paths['rubric'],
                'labels_sha256': paths['labels'], 'sources_sha256': paths['sources']}.items()}
        elif args.command == 'train':
            from .training import train
            result = train(args.root, args.data, args.output, args.seed,profile=args.profile)
        elif args.command == 'predict':
            from .model import Predictor
            texts = [args.text] if args.text is not None else read_json(args.input)
            if not isinstance(texts, list) or any(not isinstance(t, str) for t in texts):
                raise ValueError('Input must be a JSON array of strings')
            result = Predictor(args.model).predict(texts)
            if args.output:
                write_json(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f'ContractGuard: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
