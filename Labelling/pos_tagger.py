import pymongo
import pandas as pd
import numpy as np
from nltk.tag import StanfordNERTagger, StanfordPOSTagger


def get_data_from_mongodb():
	'''
	INPUT: None
	OUTPUT: pandas df and mongodb db as pymongo object
	'''
	cli = pymongo.MongoClient()
	db = cli.pr
	cursor = db.pr_train.find({'labels': {'$exists': True}})
	df =  pd.DataFrame(list(cursor))
	return df, db


def save_pos_to_db(title, pos_tuples, db):
	'''
	INPUT:	title as unicode string
			pos_tuples as list [(word1, POS), (word2, POS), ... ]
			db as pymongo object connection to mongodb
	OUTPUT:	None
	'''
    labels = defaultdict(list)
    for position, word in enumerate(title.split()):
        word = word.replace('.', '[dot]')
        word = word.replace('$', '[dol]')
        labels[word].append({'position': position,
                             'label': 'other',
                             'POS': ''})
    for item in form:
        if form[item] != '' and item != 'horf':
            for word in form[item].split():
                word = word.replace('.', '[dot]')
                word = word.replace('$', '[dol]')
                for label in labels[word.strip()]:
                    label['label'] = item
    _id = {'_id': title}
    update = {'$set': {'POS': pos}}
    DB.pr_train.update_one(_id, update)


if __name__ == '__main__':
	pos = '/Users/scottcronin/nltk_data/taggers' + \
		  '/stanford-postagger-full-2015-04-20/models' + \
		  '/english-caseless-left3words-distsim.tagger'
	pos_jar = '/Users/scottcronin/nltk_data/taggers' + \
			  '/stanford-postagger-full-2015-04-20' + \
			  '/stanford-postagger-3.5.2.jar'
	st_pos = StanfordPOSTagger(pos, pos_jar)
	df, db = get_data_from_mongodb()
	for row in df[['_id', 'labels']].values:
		headline = row[0]
		pos_tuples = st_pos.tag(headline.split())
		save_pos_to_db(headline, pos_tuples, db)