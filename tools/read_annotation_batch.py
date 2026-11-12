"""Display complete prepared text in small batches for manual agent decisions."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--start',type=int,default=0)
parser.add_argument('--end',type=int,required=True)
args=parser.parse_args()
data=json.loads((ROOT/'configs/annotation_preparation.json').read_text(encoding='utf-8'))
for row in data['rows'][args.start:args.end]:
    print(f"{row['index']}|{row['clause_id']}|{row['text']}")
