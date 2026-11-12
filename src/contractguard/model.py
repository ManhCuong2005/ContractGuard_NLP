"""Locally trained scikit-learn pipelines and offline prediction."""
import hashlib
from pathlib import Path

import joblib
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from .dataset import read_json, sha256, write_json
from .text import normalize, require_text

ARTIFACT_VERSION = 1


def word_features():
    # Deliberately syllable n-grams, not claimed to be Vietnamese word segmentation.
    return TfidfVectorizer(preprocessor=normalize, lowercase=False,
                           ngram_range=(1, 2), sublinear_tf=True,
                           max_features=40000, token_pattern=r'(?u)\b\w+\b')


def candidates(seed=42):
    classifiers = {
        'dummy': DummyClassifier(strategy='most_frequent'),
        'naive_bayes': MultinomialNB(alpha=1.0),
        'logistic_regression': LogisticRegression(C=1.0, class_weight='balanced',
                                                  max_iter=3000, random_state=seed),
        'linear_svm': LinearSVC(C=1.0, class_weight='balanced', random_state=seed, dual='auto'),
    }
    result = {name: Pipeline([('features', word_features()), ('classifier', clf)])
              for name, clf in classifiers.items()}
    # A controlled representation alternative; no externally pretrained model.
    result['linear_svm_word_char'] = Pipeline([
        ('features', FeatureUnion([
            ('word', word_features()),
            ('char', TfidfVectorizer(preprocessor=normalize, lowercase=False,
                                     analyzer='char_wb', ngram_range=(3, 5),
                                     sublinear_tf=True, max_features=60000))])),
        ('classifier', LinearSVC(C=1.0, class_weight='balanced', random_state=seed, dual='auto'))])
    return result


def save_model(path, pipeline, metadata):
    path = Path(path)
    if path.exists() or path.with_suffix('.json').exists():
        raise ValueError('Model destination exists; use a new run directory')
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    write_json(path.with_suffix('.json'), {**metadata, 'artifact_version': ARTIFACT_VERSION,
                                         'model_sha256': sha256(path)})


class Predictor:
    def __init__(self, path, allow_test_artifact=False):
        path = Path(path)
        self.metadata = read_json(path.with_suffix('.json'))
        if self.metadata.get('artifact_version') != ARTIFACT_VERSION:
            raise ValueError('Unsupported model artifact version')
        if sha256(path) != self.metadata.get('model_sha256'):
            raise ValueError('Model checksum mismatch')
        if self.metadata.get('purpose') != 'official' and not allow_test_artifact:
            raise ValueError('Technical test artifact cannot be used as an official model')
        if self.metadata.get('purpose') == 'official' and (
                self.metadata.get('task') != 'contract_anomaly_detection' or
                set(self.metadata.get('labels', [])) != {'normal', 'abnormal'}):
            raise ValueError('Official model must target normal/abnormal contract risk labels')
        # joblib uses pickle: load only artifacts created locally by this project.
        self.pipeline = joblib.load(path)

    def predict(self, texts):
        if not texts:
            raise ValueError('At least one clause required')
        clean = [require_text(t) for t in texts]
        features = self.pipeline.named_steps['features'].transform(clean)
        labels = self.pipeline.predict(clean)
        result = []
        for i, (text, label) in enumerate(zip(clean, labels)):
            oov = features[i].nnz == 0
            result.append({'text': texts[i], 'label': None if oov else str(label),
                           'needs_review': oov, 'reason': 'no_known_features' if oov else None,
                           'model_id': self.metadata.get('run_id'),
                           'model_purpose': self.metadata.get('purpose'),
                           'confidence': None})
        return result
