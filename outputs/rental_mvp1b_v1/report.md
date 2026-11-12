# ContractGuard MVP 1 — rental_mvp1b_v1

Purpose: official.
Model: bow_unigram__logistic_regression.
Selected using validation Macro F1; refit train + validation; evaluate test once.
Save/reload identical predictions: True. Dataset SHA256: 19d7554f2b27a754c570ffbb9b8a58dc75a5a053dfa3b5d593717c9541c4c442.

| Metric | Test | Dummy |
|---|---:|---:|
| accuracy | 0.936170 | 0.936170 |
| precision_macro | 0.468085 | 0.468085 |
| recall_macro | 0.500000 | 0.500000 |
| f1_macro | 0.483516 | 0.483516 |
| f1_weighted | 0.905307 | 0.905307 |

Confusion matrix: rows = true, columns = predicted; see confusion_matrix.csv.
Review errors.csv manually. Metrics describe this dataset/split only.
Limitations: public templates, domain imbalance, single-label ambiguity, no calibrated confidence.
No legal risk assessment or legal advice. Stop after MVP 1.