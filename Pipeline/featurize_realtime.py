import pandas as pd
import numpy as np
import pymongo
import requests
import newspaper
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tag import StanfordNERTagger, StanfordPOSTagger


def connect_to_mongodb():
    '''
    INPUT:  None
    OUTPUT: db - pymongo object connection to mongodb
            cli - pymongo client to close conn from main
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    return db, cli


def featurize_page_soup(soup, link):
    '''
    INPUT:  page_soup - as HTML string
            link - string url for article of interest
    OUTPUT: page_data - dict of additional features from page_soup
    '''
    soup = BeautifulSoup(soup, 'html.parser')
    s = soup.find(class_='news-release', href=link) \
            .find_parent() \
            .find_parent() \
            .find_parent() \
            .find_previous_sibling()
    try:
        date = s.find(class_='date').text.strip()
    except:
        date = ''
    try:
        time = s.find(class_='time').text.strip()
    except:
        time = ''
    try:
        img = soup.find(href=link).img['src']
    except:
        img = ''
    try:
        summary = soup.find(class_='news-release', href=link) \
                  .find_parent().find_next_sibling().text.strip()
    except:
        summary = ''
    page_data = {'date': date,
                 'time': time,
                 'summary': summary,
                 'img': img}
    return page_data


def feature_engineering(data):
    '''
    INPUT:  data - dict of features for a given document
    OUTPUT: d - dict of additional features for given document
    '''
    try:
        text = data['body'].split('/ -- ', 1)[1].strip()
    except:
        text = None
    try:
        month = data['date'][:3]
        if data['meta_desc'].find(month) > -1:
            location = data['meta_desc'].split(month, 1)[0].strip()
        else:
            location = None
    except:
        location = None
    try:
        org = data['authors'][0]
    except:
        org = None
    if text and org and location:
        d = {'text': text,
             'location': location,
             'org': org}
    else:
        d = {}
    return d


def featurize(doc):
    '''
    INPUT: doc - dict of scraped data for each document
    OUTPUT: data - dict of relevant features for each doc
    '''
    title = doc['_id']
    link = doc['link']
    source = doc['source']
    soup = doc['body_soup']
    page_soup = doc['page_soup']

    article = newspaper.Article(link)
    article.download(html=soup)
    article.parse()

    data = {'_id': title,
            'link': link,
            'source': source,
            'authors': article.authors,
            'body': article.text,
            'keywords': article.meta_keywords,
            'lang': article.meta_lang,
            'meta_desc': article.meta_description,
            'source_url': article.source_url}

    additional_data = featurize_page_soup(page_soup, link)
    data.update(additional_data)

    additional_data2 = feature_engineering(data)
    data.update(additional_data2)

    del data['authors']
    del data['meta_desc']
    del data['body']
    return data


def get_POS(title, label, st_pos):
    '''
    INPUT:  title - string of headline for doc
            label - dict of features for doc
            st_pos - Stanford POS tagger object used for tagging
    OUTPUT: label - dict of features for doc with updated POS
    '''
    pos_tpls = st_pos.tag(title.split())
    for i, (word, pos) in enumerate(pos_tpls):
        label[str(i)]['POS'] = pos
    return label


def get_ner(title, label, st_ner):
    '''
    INPUT:  title - string of headline for doc
            label - dict of features for doc
            st_ner - Stanford NER tagger object used for tagging
    OUTPUT: label - dict of features for doc with updated NER
    '''
    ner_tpls = st_ner.tag(title.split())
    for i, (word, ner) in enumerate(ner_tpls):
        label[str(i)]['ner'] = ner
    return label


def get_labels(title, st_pos, st_ner):
    '''
    INPUT:  title - string of headline for doc
            st_pos - Stanford POS tagger object used for tagging
            st_ner - Stanford NER tagger object used for tagging
    OUTPUT: label - dict of features to be used for vectorizing docs
    '''
    num_words = len(title.split())
    label = {}
    for i, word in enumerate(title.split()):
        label[str(i)] = {'word': word,
                         'all_lower': word.islower(),
                         'all_upper': word.isupper(),
                         'word_pct': i / float(num_words)}
    label = get_POS(title, label, st_pos)
    label = get_ner(title, label, st_ner)
    return label


if __name__ == '__main__':
    '''
    PURPOSE:    Loop through every document scrapped from prnewswire stored
                in mongodb. Featurize each document and store results in
                new mongodb collection. Mark each scrapped document in
                original db so that it does not need to be looked at again.
    '''
    # using Stanford's POS tagger for featurization of data
    pos = '/Users/scottcronin/nltk_data/taggers' + \
          '/stanford-postagger-full-2015-04-20/models' + \
          '/english-caseless-left3words-distsim.tagger'
    pos_jar = '/Users/scottcronin/nltk_data/taggers' + \
              '/stanford-postagger-full-2015-04-20' + \
              '/stanford-postagger-3.5.2.jar'
    # using Stanford's NER tagger for comparison metric
    ner = '/Users/scottcronin/nltk_data/stanford-ner/' + \
          'classifiers/english.all.3class.distsim.crf.ser.gz'
    ner_jar = '/Users/scottcronin/nltk_data/stanford-ner/' + \
              'stanford-ner-3.5.2.jar'
    st_pos = StanfordPOSTagger(pos, pos_jar)
    st_ner = StanfordNERTagger(ner, ner_jar)

    db, cli = connect_to_mongodb()
    cursor = db.prnewswire.find({'$query':
                                {'source': 'personnel-announcements-list',
                                 'pulled': {'$exists': False}},
                                 '$snapshot': True})
    count = 1
    tot = db.prnewswire.find({'source': 'personnel-announcements-list',
                              'pulled': {'$exists': False}}).count()
    for doc in cursor:
        doc_features = featurize(doc)
        if 'text' in doc_features:
            print doc_features['_id']
            label = get_labels(doc_features['_id'], st_pos, st_ner)
            doc_features['label'] = label
            db.pr_realtime.insert(doc_features)
        print 'Saving %i of %i' % (count, tot)
        db.prnewswire.update_one({'_id': doc['_id']},
                                 {'$set': {'pulled': 'yes'}})
        count += 1
    cli.close()
