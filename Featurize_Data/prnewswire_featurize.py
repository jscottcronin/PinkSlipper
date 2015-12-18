from collections import defaultdict
import pymongo
import requests
from bs4 import BeautifulSoup
import numpy as np
import newspaper


def in_clean_db(title, database):
    '''
    PURPOSE:    check if article is in given database
    INPUT:      title (str) - article headline
                database (pymongo obj) - connection to mongodb
    OUTPUT:     boolean -  True if article is in database
    '''
    if database.find({'_id': title}).count() > 0:
        return True
    else:
        return False


def page_data_added(title, database):
    '''
    PURPOSE:    check if page_data was added to article in mongodb
    INPUT:      title (str) - article headline
                database (pymongo obj) - connection to mongodb
    OUTPUT:     boolean -  True if article page_data is in database
    '''
    if database.find({'_id': title, 'date': {'$exists': True}}).count() > 0:
        return True
    else:
        return False


def add_to_clean_db(title, link, soup, source, database):
    '''
    PURPOSE:    use newspaper to extract article features and save
                into database
    INPUT:      title (str) - article headline
                link (str) - url for article
                soup (str) - article body soup
                source (str) - article source
                database (pymongo obj) - mongodb connection obj
    OUTPUT:     None
    '''
    article = newspaper.Article(link)
    article.download(html=soup)
    article.parse()

    data = {'_id': title,
            'link': link,
            'source': source,
            'source_url': article.source_url,
            'url': article.url,
            'title': article.title,
            'top_img': article.top_img,
            'meta_img': article.meta_img,
            'body': article.text,
            'keywords': article.keywords,
            'meta_keywords': article.meta_keywords,
            # 'tags': article.tags,
            'authors': article.authors,
            'publish_date': article.publish_date,
            'summary': article.summary,
            'meta_desc': article.meta_description,
            'lang': article.meta_lang}
    database.insert_one(data)


def add_features_from_page_soup(title, link, soup, db):
    '''
    PURPOSE:    update article features in mongodb with info from
                page_soup
    INPUT:      title (str) - article headline
                link (str) - url for article
                soup (str) - page_soup for given article
                db (pymongo obj) - connection to mongodb
    OUTPUT:     None
    '''
    print title
    if in_clean_db(title, db) and not page_data_added(title, db):
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
        uid = {'_id': title}
        additional_data = {'date': date,
                           'time': time,
                           'brief': summary,
                           'img': img
                           }

        db.update_one(uid, {'$set': additional_data})


def main2():
    '''
    PURPOSE:    update articles in new mongodb with features extracted
                from page_soup
    INPUT:      None
    OUTPUT:     None
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    coll = db.prnewswire
    coll2 = db.pr_clean
    cursor = coll.find()
    tot = coll.find().count()
    count = 1
    for doc in cursor:
        title = doc['_id']
        link = doc['link']
        psoup = doc['page_soup']
        source = doc['source']
        if not in_clean_db(title, coll2):
            print 'error - not in pr_clean db'
        else:
            print 'updating features'
            add_features_from_page_soup(title, link, psoup, coll2)
        print 'Importing article %i of %i' % (count, tot)
        count += 1
    cli.close()


def main():
    '''
    PURPOSE:    cleanse articles from original mongodb and store
                in new mongodb with updated features from body soup
    INPUT:      None
    OUTPUT:     None
    '''
    cli = pymongo.MongoClient()
    db = cli.pr
    coll = db.prnewswire
    coll2 = db.pr_clean
    cursor = coll.find()
    tot = coll.find().count()
    count = 1
    for doc in cursor:
        title = doc['_id']
        link = doc['link']
        soup = doc['body_soup']
        source = doc['source']
        if not in_clean_db(title, coll2):
            print 'adding to clean db'
            add_to_clean_db(title, link, soup, source, coll2)
        else:
            print 'already in clean db'
        print 'Importing article %i of %i' % (count, tot)

        count += 1

    cli.close()


if __name__ == '__main__':
    main()
    # main2()
