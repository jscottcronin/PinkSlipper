import pymongo
import pandas as pd
import json
import ipdb


def extract_loc(row):
    '''
    INPUT: dataframe row from df.apply lambda func
    OUTPUT: string describing geographic location
    '''
    try:
        month = row['date'][:3]
        if row['meta_desc'].find(month) > -1:
            location = row['meta_desc'].split(month, 1)[0].strip()
        else:
            location = None
    except:
        location = None
    return location


def extract_body(row):
    '''
    INPUT: dataframe row from df.apply lambda func
    OUTPUT: string of news article body
    '''
    try:
        body = row['body'].split('/ -- ', 1)[1].strip()
    except:
        body = None
    return body


def get_org(row):
    '''
    INPUT: dataframe row from df.apply lambda func
    OUTPUT: string describing org name
    '''
    try:
        org = row['authors'][0]
    except:
        org = None
    return org


def clean_data(df):
    '''
    INPUT: dataframe
    OUTPUT: dataframe after some cleaning / filtering
    '''
    df2 = df[(df.lang == 'en') &
             (df.source == 'personnel-announcements-list')]
    df3 = df2[['_id', 'authors', 'body', 'meta_desc',
               'date', 'time', 'lang']].dropna()
    df3['geo'] = df3.apply(extract_loc, axis=1)
    df3['org'] = df3.apply(get_org, axis=1)
    df3['article'] = df3.apply(extract_body, axis=1)
    df3.drop(['body', 'authors', 'meta_desc'], axis=1, inplace=True)
    df3.dropna(inplace=True)
    return df3


if __name__ == '__main__':
    '''
    PURPOSE: open all docs in a mongo db, clean and filter
    the docs for model training, and save docs in new db
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    cursor = db.pr_clean.find()
    df = pd.DataFrame(list(cursor))
    df2 = clean_data(df)
    records = json.loads(df2.T.to_json()).values()
    db.pr_train.insert_many(records)
    cli.close()
