import pymongo
import pandas as pd
import json
import ipdb


def extract_loc(row):
    '''
    PURPOSE:    get location of article. function is designed
                for use with pandas dataframe apply function.
    INPUT:      row (pandas df row) - from df.apply lambda func
    OUTPUT:     location (str) - geographic location
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
    PURPOSE:    get text body from article
    INPUT:      row (pandas df row) - from df.apply lambda func
    OUTPUT:     body (str) - article body text
    '''
    try:
        body = row['body'].split('/ -- ', 1)[1].strip()
    except:
        body = None
    return body


def get_org(row):
    '''
    PURPOSE:    get orginazation name from article
    INPUT:      row (pandas df row) - from df.apply lambda func
    OUTPUT:     body (str) - orginazation name
    '''
    try:
        org = row['authors'][0]
    except:
        org = None
    return org


def clean_data(df):
    '''
    PURPOSE:    filter data to only use articles thare are: english
                and from personnel-announcements-list page on PR Newswire.
                Furthermore, extract only relevant features for each article
                and drop any remaining NaNs.
    INPUT:      df (pandas dataframe) - all articles from mongodb
    OUTPUT:     df (pandas dataframe) - df of articles after filtering
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
    PURPOSE:    open all docs in a mongo db, clean and filter
                the docs for model training, and save docs in new db
    INPUT:      None
    OUTPUT:     None
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    cursor = db.pr_clean.find()
    df = pd.DataFrame(list(cursor))
    df2 = clean_data(df)
    records = json.loads(df2.T.to_json()).values()
    db.pr_train.insert_many(records)
    cli.close()
