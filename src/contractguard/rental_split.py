"""Balance approved labels across indivisible groups, before any model scores."""
from collections import Counter
from itertools import permutations
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold
from .dataset import leakage_groups

def balanced_split_rows(rows,labels,seed=42):
    y=np.array([r['label'] for r in rows])
    groups=np.array(leakage_groups(rows))
    for label in labels:
        if len(set(groups[y==label]))<5:
            raise ValueError(f'{label}: needs at least five independent groups')
    targets=np.array([.6,.2,.2])
    best=None
    # Fixed, outcome-independent search. Never inspect features or predictions.
    for attempt in range(128):
        folds=list(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=seed+attempt)
            .split(np.zeros(len(y)),y,groups))
        for test_fold,val_fold in permutations(range(5),2):
            test,val=folds[test_fold][1],folds[val_fold][1]
            train=np.array(sorted(set(range(len(rows)))-set(test)-set(val)))
            partitions=[train,val,test]
            if any(set(y[idx])!=set(labels) for idx in partitions):continue
            # At least five actual abnormal in each held-out split; do not relax
            # this floor because a particular model performs poorly.
            if any(sum(y[idx]=='abnormal')<5 for idx in [val,test]):continue
            if any(len(set(groups[idx][y[idx]=='abnormal']))<2 for idx in [val,test]):continue
            sizes=np.array([len(idx)/len(y) for idx in partitions])
            if sizes[0]<.5 or any(v<.12 or v>.30 for v in sizes[1:]):continue
            error=float(np.abs(sizes-targets).sum())
            for label in labels:
                fractions=np.array([sum(y[idx]==label)/sum(y==label) for idx in partitions])
                error+=float(np.abs(fractions-targets).sum())
            key=(round(error,12),attempt,test_fold,val_fold)
            if best is None or key<best[0]:best=(key,partitions,seed+attempt)
    if best is None:
        raise ValueError('Cannot form balanced group-disjoint splits with >=5 abnormal and >=2 positive groups per held-out set; collect more sources.')
    key,(train,val,test),split_seed=best
    return {'train':train,'validation':val,'test':test},groups,split_seed
