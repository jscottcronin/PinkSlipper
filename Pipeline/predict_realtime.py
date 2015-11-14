import pymongo
import pandas as pd
import numpy as np
import pickle

def load_data():
    '''
    INPUT:  None
    OUTPUT: cli - Mongoclient object w connection to db
            db - pymongo object connection to db
            df - pandas dataframe with data from mongodb
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    cursor = db.pr_realtime.find()
    df = pd.DataFrame(list(cursor))
    return cli, db, df

def vectorize(label):
    '''
    INPUT:  label - dict of features for a given document
    OUTPUT: X - np.array list of 2d ndarray formatted for chainCRF model
    '''
    tags = ['$', '``', "''", '(', ')', ',', '--', '.', ':', 'CC', 'CD', 'DT', 'EX',
            'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN', 'NNP', 'NNPS',
            'NNS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP', 'SYM',
            'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP',
            'WP$', 'WRB', 'BOS', 'EOS']

    mapping = {'other': 3,
               'org': 0,
               'name': 1,
               'name2': 1,
               'position': 2,
               'O': 3,
               'ORGANIZATION': 0,
               'PERSON': 1,
               'LOCATION': 3}

    label = {int(k): v for k, v in label.iteritems()}
    df = pd.DataFrame(label).T
    df_calcs = df[['word_pct', 'all_lower', 'all_upper']].astype(float)
    df['POS'] = df['POS'].astype('category', categories=tags)

    # include POS for num number of words before and after word of interest
    num = 2
    for i in xrange(1,num+1):
        col_pos = 'POS' + '+'*i
        col_neg = 'POS' + '-'*i
        df[col_pos] = df['POS'].shift(-i).fillna('EOS')
        df[col_neg] = df['POS'].shift(i).fillna('BOS')
    
    df_pos = pd.get_dummies(df.filter(regex='POS'))
    df = pd.concat([df_calcs, df_pos], axis=1)
    X = df.values
    return np.array([X])


def convert_y_to_tag(y):
    '''
    INPUT:  y - np.array list of 1d ndarray model label predictions
    OUTPUT: list of predicted labels for each word in headline
    '''
    map_inverse = {0: 'ORGANIZATION',
                   1: 'PERSON',
                   2: 'POSITION',
                   3: 'O'}
    tag = [map_inverse[k] for k in y[0]]
    return tag


if __name__ == '__main__':
    '''
    PURPOSE:    Loops through docs in pr_realtime and predicts labels
                for each word based on pickled model. Saves labels
                under doc['label]['word_position']['model'] = label
    '''
    with open('../Modeling/chainCRF.pkl') as f:
        model = pickle.load(f)
    cli, db, df = load_data()
    cursor = db.pr_realtime.find({'$query': {}, '$snapshot': True})
    for doc in cursor:
        X = vectorize(doc['label'])
        y = model.predict(X)
        tag = convert_y_to_tag(y)
        for i, label in enumerate(tag):
            doc['label'][str(i)]['model'] = label
        db.pr_realtime.update_one({'_id': doc['_id']},
                                  {'$set': {'label': doc['label']}})
    cli.close()


