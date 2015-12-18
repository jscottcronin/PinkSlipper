import pymongo
import pandas as pd
import numpy as np
import pickle
from sklearn.cross_validation import train_test_split
from sklearn.svm import LinearSVC
from pystruct.models import ChainCRF
from pystruct.learners import FrankWolfeSSVM
from sklearn.naive_bayes import MultinomialNB


def inv_label_dict(row):
    '''
    PURPOSE:    update word feature formatting to simplify modeling
                by inverting label dict
    INPUT:      row (pd.dataframe) - row from pd.apply function
    OUTPUT:     d (dict) - updated label dict in proper formatting
    '''
    d = {}
    title = row['_id']
    label = row['labels']
    for k, vs in label.iteritems():
        k = k.replace('[dot]', '.')
        k = k.replace('[dol]', '$')
        for v in vs:
            d[v['position']] = {'word': k,
                                'POS': v['POS'],
                                'label': v['label']}
    return d


def update_POS(row):
    '''
    PURPOSE:    update POS tags for words in label dict
    INPUT:      row (pd.dataframe) - row from pd.apply function
    OUTPUT:     label (dict) - updated label dict with POS tags
    '''
    title = row['_id']
    pos_tpls = st_pos.tag(title.split())
#     print datetime.now().time()
    label = row['labels']
    for i, (word, pos) in enumerate(pos_tpls):
        label[i]['POS'] = pos
    return label


def update_ner(row):
    '''
    PURPOSE:    update NER tags for words in label dict
    INPUT:      row (pd.dataframe) - row from pd.apply function
    OUTPUT:     label (dict) - updated label dict with NER tags
    '''
    title = row['_id']
    ner_tpls = st_ner.tag(title.split())
    label = row['labels']
    print datetime.now().time()
    for i, (word, ner) in enumerate(ner_tpls):
        label[i]['ner'] = ner
    return label


def word_pct(label):
    '''
    PURPOSE:    update normalized word location feature in label dict
    INPUT:      label (pd.Series) - label dict for given article
    OUTPUT:     label (pd.Series) - label dict updated with word_pct feature
    '''
    word_count = len(label)
    for num in xrange(word_count):
        word_pct = num / float(word_count)
        label[num]['word_pct'] = word_pct
    return label


def all_lower(label):
    '''
    PURPOSE:    update all_lower feature in label dict
    INPUT:      label (pd.Series) - label dict for given article
    OUTPUT:     label (pd.Series) - label dict updated with all_lower feature
    '''
    for k, v in label.iteritems():
        label[k]['all_lower'] = v['word'].islower()
    return label


def all_upper(label):
    '''
    PURPOSE:    update all_upper feature in label dict
    INPUT:      label (pd.Series) - label dict for given article
    OUTPUT:     label (pd.Series) - label dict updated with all_upper feature
    '''
    for k, v in label.iteritems():
        label[k]['all_upper'] = v['word'].isupper()
    return label


def vectorize(label):
    '''
    PURPOSE:    return X, y, needed to build a model and also return y_stanford
                (predicted labels from Stanfords model) to evaluate model
    INPUT:      label (dict) - word features for a given document
    OUTPUT:     X (np.array) - 2d nd.array of features for each word in article
                y (np.array) - 1d array of labels for each word in article
                y_stanford (np.array) - 1d array of pred labels for each word
    '''
    tags = ['$', '``', "''", '(', ')', ',', '--', '.', ':', 'CC', 'CD',
            'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN',
            'NNP', 'NNPS', 'NNS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB',
            'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG',
            'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', 'BOS', 'EOS']
    mapping = {'other': 3,
               'org': 0,
               'name': 1,
               'name2': 1,
               'position': 2,
               'O': 3,
               'ORGANIZATION': 0,
               'PERSON': 1,
               'LOCATION': 3}

    df = pd.DataFrame(label).T
    df_calcs = df[['word_pct', 'all_lower', 'all_upper']].astype(float)
    df['POS'] = df['POS'].astype('category', categories=tags)

    y = df['label'].map(mapping).values
    y_stanford = df['ner'].map(mapping).values

    # include POS of num number of words before and after word of interest
    num = 2
    for i in xrange(1, num+1):
        col_pos = 'POS' + '+'*i
        col_neg = 'POS' + '-'*i
        df[col_pos] = df['POS'].shift(-i).fillna('EOS')
        df[col_neg] = df['POS'].shift(i).fillna('BOS')

    df_pos = pd.get_dummies(df.filter(regex='POS'))
    df = pd.concat([df_calcs, df_pos], axis=1)
    X = df.values
    return X, y, y_stanford


def get_X_and_y(df):
    '''
    PURPOSE:    return X, y for model training / testing as well as
                returning y_stranford to compare model against
    INPUT:      df (pandas dataframe obj) - df of articles
    OUTPUT:     X (np.array) - array of 2d nd.arrays (one for each article)
                y (np.array) - array of 1d nd.arrays labels
                y_stanford (np.array) - array of 1d nd.arrays of Stanford preds
                headlines (list) - list of headlines
    '''
    X = []
    y = []
    y_stanford = []
    headlines = []
    for row in df[['_id', 'labels']].values:
        headline, label = row[0], row[1]
        headlines.append(headline)
        _X, _y, _y_stanford = vectorize(label)
        X.append(_X)
        y.append(_y)
        y_stanford.append(_y_stanford)
    X = np.array(X)
    y = np.array(y)
    y_stanford = np.array(y_stanford)
    return X, y, y_stanford, headlines


def preprocessing(df):
    '''
    PURPOSE:    update features for headline words in each article
    INPUT:      df (pandas dataframe obj) - df of articles
    OUTPUT:     df (pandas dataframe obj) - df of articles w updated features
    '''
    df = df[df['horf'] == 'Hired']
    df['labels'] = df['labels'].apply(word_pct)
    df['labels'] = df['labels'].apply(all_lower)
    df['labels'] = df['labels'].apply(all_upper)
    return df


def build_models(X_train, y_train):
    '''
    PURPOSE:    ouput model objects which have been fitted with training data
    INPUT:      X_train (np.array) - features matrix
                y_train (np.array) - label matrix
    OUTPUT:     nmb (MultinomialNB obj) - model trained on X_train, y_train
                svm (LinearSVC obj) - model trained on X_train, y_train
                ssvm (PyStruct chainCRF object) - trained Chain CRF model
    '''
    # Multinomial Naive Bayes Classifier:
    nmb = MultinomialNB()
    nmb.fit(np.vstack(X_train), np.hstack(y_train))

    # Support Vector Machine Classifier
    svm = LinearSVC(dual=False, C=.1)
    svm.fit(np.vstack(X_train), np.hstack(y_train))

    # Chain Conditional Random Field Classifier
    model = ChainCRF()
    ssvm = FrankWolfeSSVM(model=model, C=0.5, max_iter=15)
    ssvm.fit(X_train, y_train)
    return nmb, svm, ssvm


def score_models(X_test, y_test, nmb, svm, chainCRF):
    '''
    PURPOSE:    print cross-validated scores for input models
    INPUT:      X_test (np.array) - feature matrix for testing
                y_test (np.array) - label matrix on test data for scoring
                nmb - MultinomialNB object trained on X_train, y_train
                svm - LinearSVC object trained on X_train, y_train
                chainCRF - PyStruct chainCRF object trained on X_train, y_train
    OUTPUT: None - print results of accuracy score
    '''
    print 'NMB: %f' % nmb.score(np.vstack(X_test), np.hstack(y_test))
    print 'SVM: %f' % svm.score(np.vstack(X_test), np.hstack(y_test))
    print 'CRF: %f' % chainCRF.score(X_test, y_test)


if __name__ == '__main__':
    '''
    PURPOSE:    open df of articles and fit various models to cross-validated
                splits of training data. Score models and output ChainCRF as
                pickled obj.
    INPUT:      None
    OUTPUT:     None
    '''
    df = pd.read_pickle('../Data/feat_pos_ner.pkl')
    df = preprocessing(df)
    X, y, y_stanford, headlines = get_X_and_y(df)
    X_train, X_test, y_train, y_test, y_st_train, y_st_test, \
        hl_train, hl_test = train_test_split(X, y, y_stanford,
                                             headlines, test_size=0.25)
    nmb, svm, chainCRF = build_models(X_train, y_train)
    score_models(X_test, y_test, nmb, svm, chainCRF)
    with open('chainCRF.pkl', 'w') as f:
        pickle.dump(chainCRF, f)
