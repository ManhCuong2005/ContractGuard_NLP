"""Version extraction repairs without touching raw sources or chat decisions."""
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/rental_mvp1a_v1'

def main():
    history=BASE/'extraction_history/v4_before_scope_repair'
    history.mkdir(parents=True,exist_ok=True)
    for name in ['candidates.json','candidates.csv','candidate_sources.json','candidate_coverage.json']:
        p=BASE/name
        if (history/name).exists():
            raise ValueError('Already snapshotted')
        shutil.move(str(p),str(history/name))
    config=ROOT/'configs/rental_contracts_v1.json'
    shutil.copyfile(config,history/config.name)
    specs=json.loads(config.read_text('utf-8'))
    for s in specs:
        if s['contract']=='homedy_simple':
            s['lines']=[58,77]
        if s['contract']=='cochinh_house':
            s['pages']=[4,5]
        if s['contract']=='cochinh_foreigner':
            s['pages']=[19,22]
    config.write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Scope boundaries and extraction history saved.')

if __name__=='__main__':
    main()
