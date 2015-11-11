import pymongo
import pandas as pd
import numpy as np


def get_data_from_mongodb():
    '''
    INPUT: None
    OUTPUT: 3 dataframes from mongodb database for backing up
    df_train_labels: db of training data with labels completed
    df_train_bckup: db of all training data (with / without labels)
    df_clean_bckup: db of featurized data prior to input in train db
    '''

    cli = pymongo.MongoClient()
    db = cli.pr
    # backup training db with rows that have labelled
    cursor = db.pr_train.find({'labels': {'$exists': True}})
    df_train_labels = pd.DataFrame(list(cursor))
    # backup all training db
    cursor = db.pr_train.find({})
    df_train_bckup = pd.DataFrame(list(cursor))
    # backup clean db
    cursor = db.pr_train.find({'labels': {'$exists': True}})
    df_clean_bckup = pd.DataFrame(list(cursor))
    cli.close()
    return df_train_labels, df_train_bckup, df_clean_bckup


if __name__ == '__main__':
    '''
    INPUT: None
    OUTPUT: Saves Mongodb databases into pickles for backup
    '''
    df1, df2, df3 = get_data_from_mongodb()
    df1.to_pickle('pr_train_labelled_475_v1.pkl')
    df2.to_pickle('pr_train_all_v1.pkl')
    df3.to_pickle('pr_clean_all_v1.pkl')
