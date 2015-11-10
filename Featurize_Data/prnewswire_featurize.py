from collections import defaultdict
import pymongo
import requests
from bs4 import BeautifulSoup
import numpy as np
import newspaper


def in_clean_db(title, database):
    if database.find({'_id': title}).count() > 0:
        return True
    else:
        return False


def page_data_added(title, database):
    if database.find({'_id': title, 'date': {'$exists': True}}).count() > 0:
        return True
    else:
        return False

def add_to_clean_db(title, link, soup, source, database):
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


def get_article():
    title == "Hello Kitty Men; Unveiling 12 Items in Collaboration with 6 Tokyo Men's Brands"
    soup = BeautifulSoup(soup, 'html.parser')


def add_features_from_page_soup(title, link, soup, db):
    
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
        print 'Importing article %i of %i' %(count, tot)
        count += 1
    cli.close()


def main():
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
        print 'Importing article %i of %i' %(count, tot)

        count += 1

    cli.close()


if __name__ == '__main__':
    main()