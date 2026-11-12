"""Controlled classical baselines, with all learned features fitted on train only."""
import re
import unicodedata
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.dummy import DummyClassifier
from .text import normalize

# Declared from approved domain terminology, not mined from test labels.
# This is limited dictionary tokenization, not a general pretrained segmenter.
DOMAIN_TERMS=('bất khả kháng','hợp đồng','đặt cọc','tiền thuê','người thuê','bồi thường',
    'thiệt hại','bảo trì','sửa chữa','đơn phương','chấm dứt','trách nhiệm','toàn bộ','bất kỳ')

def domain_tokenize(text):
    text=normalize(text)
    for term in DOMAIN_TERMS:
        text=re.sub(r'(?<!\w)'+re.escape(term)+r'(?!\w)',term.replace(' ','_'),text)
    return re.findall(r'(?u)\b\w+\b',text)

def case_preserving(text):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFC',text).replace('\u200b','').replace('\ufeff','').replace('\u00ad','')).strip()

def vector(kind='tfidf',order=2,preprocessing='conservative'):
    cls=CountVectorizer if kind=='bow' else TfidfVectorizer
    kwargs=dict(preprocessor=case_preserving if preprocessing=='case_preserving' else normalize,
        lowercase=False,ngram_range=(1,order),max_features=40000,token_pattern=r'(?u)\b\w+\b')
    if kind=='tfidf':kwargs['sublinear_tf']=True
    if preprocessing=='limited_stopwords':kwargs['stop_words']=['và','là','của','các','những']
    if preprocessing=='domain_dictionary':
        kwargs.update(tokenizer=domain_tokenize,token_pattern=None)
    return cls(**kwargs)

def rental_candidates(seed=42):
    models={}
    config={}
    def add(name,features,classifier,**details):
        models[name]=Pipeline([('features',features),('classifier',classifier)])
        config[name]=details
    add('dummy',vector(),DummyClassifier(strategy='most_frequent'),algorithm='dummy',representation='tfidf_bigram')
    for kind in ['bow','tfidf']:
        for order in [1,2]:
            representation=f'{kind}_{"unigram" if order==1 else "bigram"}'
            classifiers={
                'naive_bayes':MultinomialNB(alpha=1.0),
                'logistic_regression':LogisticRegression(C=1.0,class_weight='balanced',max_iter=3000,random_state=seed),
                'linear_svm':LinearSVC(C=1.0,class_weight='balanced',random_state=seed,dual='auto'),
            }
            for algorithm,clf in classifiers.items():
                add(f'{representation}__{algorithm}',vector(kind,order),clf,
                    algorithm=algorithm,representation=representation,preprocessing='conservative',
                    class_weight=None if algorithm=='naive_bayes' else 'balanced',C=1.0 if algorithm!='naive_bayes' else None,alpha=1.0 if algorithm=='naive_bayes' else None)
    for c in [.5,2.0]:
        for algorithm,cls in [('logistic_regression',LogisticRegression),('linear_svm',LinearSVC)]:
            kwargs=dict(C=c,class_weight='balanced',random_state=seed)
            if algorithm=='logistic_regression':kwargs['max_iter']=3000
            else:kwargs['dual']='auto'
            add(f'tfidf_bigram__{algorithm}_C{c}',vector(),cls(**kwargs),
                algorithm=algorithm,representation='tfidf_bigram',preprocessing='conservative',C=c,class_weight='balanced')
    for alpha in [.25,4.0]:
        add(f'tfidf_bigram__naive_bayes_a{alpha}',vector(),MultinomialNB(alpha=alpha),
            algorithm='naive_bayes',representation='tfidf_bigram',preprocessing='conservative',alpha=alpha)
    for preprocessing in ['case_preserving','limited_stopwords','domain_dictionary']:
        add(f'tfidf_bigram__linear_svm_{preprocessing}',vector(preprocessing=preprocessing),
            LinearSVC(C=1.0,class_weight='balanced',random_state=seed,dual='auto'),
            algorithm='linear_svm',representation='tfidf_bigram',preprocessing=preprocessing,C=1.0,class_weight='balanced')
    char=TfidfVectorizer(preprocessor=normalize,lowercase=False,analyzer='char_wb',
        ngram_range=(3,5),sublinear_tf=True,max_features=60000)
    add('tfidf_word_char__linear_svm',FeatureUnion([('word',vector()),('char',char)]),
        LinearSVC(C=1.0,class_weight='balanced',random_state=seed,dual='auto'),
        algorithm='linear_svm',representation='tfidf_word_bigram_char3to5',preprocessing='conservative',C=1.0,class_weight='balanced')
    return models,config
