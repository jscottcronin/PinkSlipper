import pymongo
import pandas as pd
import matplotlib.pyplot as plt


def read_from_pr_clean():
	cli = pymongo.MongoClient()
	db = cli.pr
	coll2 = db.pr_clean
	cursor = coll2.find()
	df =  pd.DataFrame(list(cursor))
	cli.close()
	return df


def extract_loc(row):
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
    try:
        body = row['body'].split('/ -- ', 1)[1]
    except:
        body = None
    return body


def get_company(row):
    try:
        corp = row['authors'][0]
    except:
        corp = None
    return corp


def clean_data(df):
	df2 = df[(df.lang == 'en') & (df.source == 'personnel-announcements-list')]
	df3 = df2[['_id', 'authors', 'brief', 'date', 'time', 'lang', 'meta_keywords', 'meta_desc', 'body']].dropna()
	df3['geo'] = df3.apply(extract_loc, axis=1)
	df3['article'] = df3.apply(extract_body, axis=1)
	df3['org'] = df3.apply(get_company, axis=1)
	df3.dropna(inplace=True)
	df3.drop(['body','authors'], axis=1, inplace=True)
	return df3


def main():
	df = read_from_pr_clean()
	df = clean_data(df)
	return df[['_id', 'brief', 'org', 'geo', 'date', 'article']].sample(500, random_state=200)


if __name__ == '__main__':
	main()
	
