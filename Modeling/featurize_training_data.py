import pymongo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def get_data_from_mongodb():
	cli = pymongo.MongoClient()
	db = cli.pr
	cursor = db.pr_train.find({'labels': {'$exists': True}})
	df =  pd.DataFrame(list(cursor))
	cli.close()
	return df


def get_X_and_y(df):
	headlines = []
	words = []
	labels = []
	for row in df.ix[:10, ['_id', 'labels']].values:
		inv_d = {}
		for k, vs in row[1].iteritems():
			for v in vs:
				inv_d[v['position']] = v['label']
		headlines.append(row[0])
		words.append(row[0].split())
		labels.append([tpl[1] for tpl in sorted(inv_d.items())])
	X = np.array(words)
	y = np.array(labels)
	headlines = np.array(headlines)
	return X, y, headlines


def main():
	df = get_data_from_mongodb()
	X, y, headlines = get_X_and_y(df)
	return X, y, headlines


if __name__ == '__main__':
	main()